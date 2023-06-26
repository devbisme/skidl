# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.


from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import re
from builtins import range, super
from collections import Counter, defaultdict
from itertools import chain

from future import standard_library

from ..net import NCNet
from ..part import Part
from ..pin import Pin
from ..scriptinfo import get_script_name
from ..tools.kicad.constants import GRID
from ..tools.kicad.eeschema_v5 import Eeschema_V5, pin_label_to_eeschema
from ..tools.kicad.v5 import calc_hier_label_bbox, calc_symbol_bbox
from ..utilities import export_to_all, rmv_attr
from .geometry import BBox, Point, Tx, Vector
from .place import PlacementFailure, Placer
from .route import Router, RoutingFailure

standard_library.install_aliases()

"""
Generate a KiCad EESCHEMA schematic from a Circuit object.
"""

# TODO: Handle symio attribute.


def preprocess_parts_and_nets(circuit):
    """Add stuff to parts & nets for doing placement and routing of schematics."""

    def units(part):
        if len(part.unit) == 0:
            return [part]
        else:
            return part.unit.values()

    def initialize(part):
        """Initialize part or its part units."""

        # Initialize the units of the part, or the part itself if it has no units.
        for part_unit in units(part):
            # Initialize transform matrix.
            part_unit.tx = Tx.from_symtx(getattr(part_unit, "symtx", ""))

            # Lock part orientation if symtx was specified. Also lock parts with a lot of pins
            # since they're typically drawn the way they're supposed to be oriented.
            # And also lock single-pin parts because these are usually power/ground and
            # they shouldn't be flipped around.
            num_pins = len(part_unit.pins)
            part_unit.orientation_locked = (
                getattr(part_unit, "symtx", False) or num_pins > 10 or num_pins <= 1
            )

            # Assign pins from the parent part to the part unit.
            part_unit.grab_pins()

            # Initialize pin attributes used for generating schematics.
            for pin in part_unit:
                pin.pt = Point(pin.x, pin.y)
                pin.routed = False

    def rotate_power_pins(part, dont_rotate_pin_threshold=10000):
        """Rotate a part based on the direction of its power pins.

        This function is to make sure that voltage sources face up and gnd pins
        face down.
        """

        # Don't rotate parts that are already explicitly rotated/flipped.
        if not getattr(part, "symtx", ""):
            return

        def is_pwr(net):
            return net_name.startswith("+")

        def is_gnd(net):
            return "gnd" in net_name.lower()

        for part_unit in units(part):
            # Don't rotate parts with too many pins.
            if len(part_unit) > dont_rotate_pin_threshold:
                return

            # Tally what rotation would make each pwr/gnd pin point up or down.
            rotation_tally = Counter()
            for pin in part_unit:
                net_name = getattr(pin.net, "name", "").lower()
                if is_gnd(net_name):
                    if pin.orientation == "U":
                        rotation_tally[0] += 1
                    if pin.orientation == "D":
                        rotation_tally[180] += 1
                    if pin.orientation == "L":
                        rotation_tally[90] += 1
                    if pin.orientation == "R":
                        rotation_tally[270] += 1
                elif is_pwr(net_name):
                    if pin.orientation == "D":
                        rotation_tally[0] += 1
                    if pin.orientation == "U":
                        rotation_tally[180] += 1
                    if pin.orientation == "L":
                        rotation_tally[270] += 1
                    if pin.orientation == "R":
                        rotation_tally[90] += 1

            # Rotate the part unit in the direction with the most tallies.
            try:
                rotation = rotation_tally.most_common()[0][0]
            except IndexError:
                pass
            else:
                # Rotate part unit 90-degrees clockwise until the desired rotation is reached.
                tx_cw_90 = Tx(a=0, b=-1, c=1, d=0)  # 90-degree trans. matrix.
                for _ in range(int(round(rotation / 90))):
                    part_unit.tx = part_unit.tx * tx_cw_90

    def calc_part_bbox(part):
        """Calculate the labeled bounding boxes and store it in the part."""

        # Find part/unit bounding boxes excluding any net labels on pins.
        # TODO: part.lbl_bbox could be substituted for part.bbox.
        # TODO: Part bbox should be expanded to account for reference and value labels.
        bare_bboxes = calc_symbol_bbox(part)[1:]

        for part_unit, bare_bbox in zip(units(part), bare_bboxes):
            # Expand the bounding box if it's too small in either dimension.
            resize_wh = Vector(0, 0)
            if bare_bbox.w < 100:
                resize_wh.x = (100 - bare_bbox.w) / 2
            if bare_bbox.h < 100:
                resize_wh.y = (100 - bare_bbox.h) / 2
            bare_bbox = bare_bbox.resize(resize_wh)

            # Find expanded bounding box that includes any hier labels attached to pins.
            part_unit.lbl_bbox = BBox()
            part_unit.lbl_bbox.add(bare_bbox)
            for pin in part_unit:
                if pin.stub:
                    # Find bounding box for net stub label attached to pin.
                    hlbl_bbox = calc_hier_label_bbox(pin.net.name, pin.orientation)
                    # Move the label bbox to the pin location.
                    tx = Tx()
                    tx.move_to(pin.pt)
                    hlbl_bbox *= tx
                    # Update the bbox for the labelled part with this pin label.
                    part_unit.lbl_bbox.add(hlbl_bbox)

            # Set the active bounding box to the labeled version.
            part_unit.bbox = part_unit.lbl_bbox

    def preprocess_nets(nets):
        """Get nets ready for schematic place-and-route."""

        # Set stub flag on every pin on a stub net.
        net_stubs = circuit.get_net_nc_stubs()
        net_stubs = [net for net in net_stubs if not isinstance(net, NCNet)]
        for net in net_stubs:
            if (
                True or net.netclass != "Power"
            ):  # TODO: figure out what to do with power nets.
                for pin in net.pins:
                    pin.stub = True

    # Pre-process parts
    for part in circuit.parts:
        # Initialize part attributes used for generating schematics.
        initialize(part)

        # Rotate parts.  Power pins should face up. GND pins should face down.
        rotate_power_pins(part)

        # Compute bounding boxes around parts
        calc_part_bbox(part)

        # Preprocess nets.
        preprocess_nets(circuit.nets)


def finalize_parts_and_nets(circuit):
    """Restore parts and nets after place & route is done."""

    # Remove any NetTerminals that were added.
    net_terminals = (p for p in circuit.parts if isinstance(p, NetTerminal))
    circuit.rmv_parts(*net_terminals)

    # Return pins from the part units to their parent part.
    for part in circuit.parts:
        part.grab_pins()

    # Remove some stuff added to parts during schematic generation process.
    rmv_attr(circuit.parts, ("force", "bbox", "lbl_bbox", "tx"))


class NetTerminal(Part):
    def __init__(self, net):
        """Specialized Part with a single pin attached to a net.

        This is intended for attaching to nets to label them, typically when
        the net spans across levels of hierarchical nodes.
        """

        # TODO: Create net labels that point in other orientations than just to the left.

        # Create a Part.
        from ..skidl import SKIDL

        super().__init__(name="NT", ref_prefix="NT", tool=SKIDL)

        # Set a default transformation matrix for this part.
        self.tx = Tx()

        # Add a single pin to the part.
        pin = Pin(num="1", name="~")
        self.add_pins(pin)

        # Set the pin at point (0,0) and pointing leftward toward the part body
        # (consisting of just the net label for this type of part) so any attached routing
        # will go to the right.
        pin.x, pin.y = 0, 0
        pin.pt = Point(pin.x, pin.y)
        pin.orientation = "L"

        # Calculate the bounding box, but as if the pin were pointed right so
        # the associated label text would go to the left.
        self.bbox = calc_hier_label_bbox(net.name, "R")

        # Resize bbox so it's an integer number of GRIDs.
        self.bbox = self.bbox.snap_resize(GRID)

        # Extend the bounding box a bit so any attached routing will come straight in.
        self.bbox.max += Vector(GRID, 0)
        self.lbl_bbox = self.bbox

        # Flip the NetTerminal horizontally if it is an output net (label on the right).
        netio = getattr(net, "netio", "").lower()
        self.orientation_locked = bool(netio in ("i", "o"))
        if getattr(net, "netio", "").lower() == "o":
            self.tx.flip_x()

        # Connect the pin to the net.
        pin += net

    def to_eeschema(self, tx):
        """Generate the EESCHEMA code for the net terminal.

        Args:
            tx (Tx): Transformation matrix for the node containing this net terminal.

        Returns:
            str: EESCHEMA code string.
        """
        self.pins[0].stub = True
        self.pins[0].orientation = "R"
        return pin_label_to_eeschema(self.pins[0], tx)
        # return pin_label_to_eeschema(self.pins[0], tx) + bbox_to_eeschema(self.bbox, self.tx * tx)


@export_to_all
class Node(Placer, Router, Eeschema_V5):
    """Data structure for holding information about a node in the circuit hierarchy."""

    filename_sz = 20
    name_sz = 40

    def __init__(self, circuit=None, filepath=".", top_name="", title="", flatness=0.0):
        self.parent = None
        self.children = defaultdict(
            lambda: Node(None, filepath, top_name, title, flatness)
        )
        self.filepath = filepath
        self.top_name = top_name
        self.sheet_name = None
        self.sheet_filename = None
        self.title = title
        self.flatness = flatness
        self.flattened = False
        self.parts = []
        self.wires = defaultdict(list)
        self.junctions = defaultdict(list)
        self.tx = Tx()
        self.bbox = BBox()

        if circuit:
            self.add_circuit(circuit)

    def find_node_with_part(self, part):
        """Find the node that contains the part based on its hierarchy.

        Args:
            part (Part): The part being searched for in the node hierarchy.

        Returns:
            Node: The Node object containing the part.
        """

        from ..circuit import HIER_SEP

        level_names = part.hierarchy.split(HIER_SEP)
        node = self
        for lvl_nm in level_names[1:]:
            node = node.children[lvl_nm]
        assert part in node.parts
        return node

    def add_circuit(self, circuit):
        """Add parts in circuit to node and its children.

        Args:
            circuit (Circuit): Circuit object.
        """

        # Build the circuit node hierarchy by adding the parts.
        for part in circuit.parts:
            self.add_part(part)

        # Add terminals to nodes in the hierarchy for nets that span across nodes.
        for net in circuit.nets:
            # Skip nets that are stubbed since there will be no wire to attach to the NetTerminal.
            if getattr(net, "stub", False):
                continue

            # Search for pins in different nodes.
            for pin1, pin2 in zip(net.pins[:-1], net.pins[1:]):
                if pin1.part.hierarchy != pin2.part.hierarchy:
                    # Found pins in different nodes, so break and add terminals to nodes below.
                    break
            else:
                if len(net.pins) == 1:
                    # Single pin on net and not stubbed, so add a terminal to it below.
                    pass
                elif not net.is_implicit():
                    # The net has a user-assigned name, so add a terminal to it below.
                    pass
                else:
                    # No need for net terminal because there are multiple pins
                    # and they are all in the same node.
                    continue

            # Add a single terminal to each node that contains one or more pins of the net.
            visited = []
            for pin in net.pins:
                # A stubbed pin can't be used to add NetTerminal since there is no explicit wire.
                if pin.stub:
                    continue

                part = pin.part

                if part.hierarchy in visited:
                    # Already added a terminal to this node, so don't add another.
                    continue

                # Add NetTerminal to the node with this part/pin.
                self.find_node_with_part(part).add_terminal(net)

                # Record that this hierarchical node was visited.
                visited.append(part.hierarchy)

        # Flatten the hierarchy as specified by the flatness parameter.
        self.flatten(self.flatness)

    def add_part(self, part, level=0):
        """Add a part to the node at the appropriate level of the hierarchy.

        Args:
            part (Part): Part to be added to this node or one of its children.
            level (int, optional): The current level (depth) of the node in the hierarchy. Defaults to 0.
        """

        from ..circuit import HIER_SEP

        # Get list of names of hierarchical levels (in order) leading to this part.
        level_names = part.hierarchy.split(HIER_SEP)

        # Get depth in hierarchy for this part.
        part_level = len(level_names) - 1
        assert part_level >= level

        # Node name is the name assigned to this level of the hierarchy.
        self.name = level_names[level]

        # File name for storing the schematic for this node.
        base_filename = "_".join([self.top_name] + level_names[0 : level + 1]) + ".sch"
        self.sheet_filename = base_filename

        if part_level == level:
            # Add part to node at this level in the hierarchy.
            if not part.unit:
                # Monolithic part so just add it to the node.
                self.parts.append(part)
            else:
                # Multi-unit part so add each unit to the node.
                # FIXME: Some part units might be split into other nodes.
                for p in part.unit.values():
                    self.parts.append(p)
        else:
            # Part is at a level below the current node. Get the child node using
            # the name of the next level in the hierarchy for this part.
            child_node = self.children[level_names[level + 1]]

            # Attach the child node to this node. (It may have just been created.)
            child_node.parent = self

            # Add part to the child node (or one of its children).
            child_node.add_part(part, level + 1)

    def add_terminal(self, net):
        """Add a terminal for this net to the node.

        Args:
            net (Net): The net to be added to this node.
        """

        from ..circuit import HIER_SEP

        nt = NetTerminal(net)
        self.parts.append(nt)

    def external_bbox(self):
        """Return the bounding box of a hierarchical sheet as seen by its parent node."""
        bbox = BBox(Point(0, 0), Point(500, 500))
        bbox.add(Point(len("File: " + self.sheet_filename) * self.filename_sz, 0))
        bbox.add(Point(len("Sheet: " + self.name) * self.name_sz, 0))
        bbox.resize(Vector(100, 100))

        # Pad the bounding box for extra spacing when placed.
        bbox.resize(Vector(100, 100))

        return bbox

    def internal_bbox(self):
        """Return the bounding box for the circuitry contained within this node."""

        # The bounding box is determined by the arrangement of the node's parts and child nodes.
        bbox = BBox()
        for obj in chain(self.parts, self.children.values()):
            tx_bbox = obj.bbox * obj.tx
            bbox.add(tx_bbox)

        # Pad the bounding box for extra spacing when placed.
        bbox.resize(Vector(100, 100))

        return bbox

    def calc_bbox(self):
        """Compute the bounding box for the node in the circuit hierarchy."""

        if self.flattened:
            self.bbox = self.internal_bbox()
        else:
            # Use hierarchical bounding box if node has not been flattened.
            self.bbox = self.external_bbox()

        return self.bbox

    def flatten(self, flatness=0.0):
        """Flatten node hierarchy according to flatness parameter.

        Args:
            flatness (float, optional): Degree of hierarchical flattening (0=completely hierarchical, 1=totally flat). Defaults to 0.0.

        Create hierarchical sheets for the node and its child nodes. Complexity (or size) of a node
        and its children is the total number of part pins they contain. The sum of all the child sizes
        multiplied by the flatness is the number of part pins that can be shown on the schematic
        page before hierarchy is used. The instances of each type of child are flattened and placed
        directly in the sheet as long as the sum of their sizes is below the slack. Otherwise, the
        children are included using hierarchical sheets. The children are handled in order of
        increasing size so small children are more likely to be flattened while large, complicated
        children are included using hierarchical sheets.
        """

        # Create sheets and compute complexity for any circuitry in hierarchical child nodes.
        for child in self.children.values():
            child.flatten(flatness)

        # Complexity of the parts directly instantiated at this hierarchical level.
        self.complexity = sum((len(part) for part in self.parts))

        # Sum the child complexities and use it to compute the number of pins that can be
        # shown before hierarchical sheets are used.
        child_complexity = sum((child.complexity for child in self.children.values()))
        slack = child_complexity * flatness

        # Group the children according to what types of modules they are by removing trailing instance ids.
        child_types = defaultdict(list)
        for child_id, child in self.children.items():
            child_types[re.sub(r"\d+$", "", child_id)].append(child)

        # Compute the total size of each type of children.
        child_type_sizes = dict()
        for child_type, children in child_types.items():
            child_type_sizes[child_type] = sum((child.complexity for child in children))

        # Sort the groups from smallest total size to largest.
        sorted_child_type_sizes = sorted(
            child_type_sizes.items(), key=lambda item: item[1]
        )

        # Flatten each instance in a group until the slack is used up.
        for child_type, child_type_size in sorted_child_type_sizes:
            if child_type_size <= slack:
                # Include the circuitry of each child instance directly in the sheet.
                for child in child_types[child_type]:
                    child.flattened = True
                # Reduce the slack by the sum of the child sizes.
                slack -= child_type_size
            else:
                # Not enough slack left. Add these children as hierarchical sheets.
                for child in child_types[child_type]:
                    child.flattened = False

    def get_internal_nets(self):
        """Return a list of nets that have at least one pin on a part in this node."""

        processed_nets = []
        internal_nets = []
        for part in self.parts:
            for part_pin in part:
                # No explicit wire for pins connected to labeled stub nets.
                if part_pin.stub:
                    continue

                # No explicit wires if the pin is not connected to anything.
                if not part_pin.is_connected():
                    continue

                net = part_pin.net

                # Skip nets that have already been processed.
                if net in processed_nets:
                    continue

                processed_nets.append(net)

                # Skip stubbed nets.
                if getattr(net, "stub", False) is True:
                    continue

                # Add net to collection if at least one pin is on one of the parts of the node.
                for net_pin in net.pins:
                    if net_pin.part in self.parts:
                        internal_nets.append(net)
                        break

        return internal_nets

    def get_internal_pins(self, net):
        """Return the pins on the net that are on parts in the node.

        Args:
            net (Net): The net whose pins are being examined.

        Returns:
            list: List of pins on the net that are on parts in this node.
        """

        # Skip pins on stubbed nets.
        if getattr(net, "stub", False) is True:
            return []

        return [pin for pin in net.pins if pin.stub is False and pin.part in self.parts]

    def collect_stats(self, **options):
        """Return comma-separated string with place & route statistics of a schematic."""

        def get_wire_length(node):
            """Return the sum of the wire segment lengths between parts in a routed node."""

            wire_length = 0

            # Sum wire lengths for child nodes.
            for child in node.children.values():
                wire_length += get_wire_length(child)

            # Add the wire lengths between parts in the top node.
            for wire_segs in node.wires.values():
                for seg in wire_segs:
                    len_x = abs(seg.p1.x - seg.p2.x)
                    len_y = abs(seg.p1.y - seg.p2.y)
                    wire_length += len_x + len_y

            return wire_length

        return "{}\n".format(get_wire_length(self))


@export_to_all
def gen_schematic(
    circuit,
    filepath=".",
    top_name=get_script_name(),
    title="SKiDL-Generated Schematic",
    flatness=0.0,
    retries=2,
    **options
):
    """Create a schematic file from a Circuit object.

    Args:
        circuit (Circuit): The Circuit object that will have a schematic generated for it.
        filepath (str, optional): The directory where the schematic files are placed. Defaults to ".".
        top_name (str, optional): The name for the top of the circuit hierarchy. Defaults to get_script_name().
        title (str, optional): The title of the schematic. Defaults to "SKiDL-Generated Schematic".
        flatness (float, optional): Determines how much the hierarchy is flattened in the schematic. Defaults to 0.0 (completely hierarchical).
        retries (int, optional): Number of times to re-try if routing fails. Defaults to 2.
        options (dict, optional): Dict of options and values, usually for drawing/debugging.
    """

    # Start with default routing area.
    expansion_factor = 1.0

    # Try to place & route one or more times.
    for _ in range(retries):
        preprocess_parts_and_nets(circuit)

        node = Node(circuit, filepath, top_name, title, flatness)

        try:
            # Place parts.
            node.place(expansion_factor=expansion_factor, **options)

            # Route parts.
            node.route(**options)

        except PlacementFailure:
            # Placement failed, so clean up ...
            finalize_parts_and_nets(circuit)
            # ... and try again.
            continue

        except RoutingFailure:
            # Routing failed, so clean up ...
            finalize_parts_and_nets(circuit)
            # ... and expand routing area ...
            expansion_factor *= 1.25  # TODO: Ad-hoc increase of expansion factor.
            # ... and try again.
            continue

        # Generate EESCHEMA code for the schematic.
        node.to_eeschema()

        # Append place & route statistics for the schematic to a file.
        if options.get("collect_stats"):
            stats = node.collect_stats(**options)
            with open(options["stats_file"], "a") as f:
                f.write(stats)

        # Clean up.
        finalize_parts_and_nets(circuit)

        # Place & route was successful if we got here, so exit.
        return

    # Append failed place & route statistics for the schematic to a file.
    if options.get("collect_stats"):
        stats = "-1\n"
        with open(options["stats_file"], "a") as f:
            f.write(stats)

    # Clean-up after failure.
    finalize_parts_and_nets(circuit)

    # Exited the loop without successful routing.
    raise (RoutingFailure)
