# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.


from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import datetime
from itertools import chain
import re
import time
from builtins import range, str
from collections import defaultdict, OrderedDict, Counter
import os.path

from future import standard_library

from skidl.tools.kicad.kicad import DrawText

from .common import GRID, PIN_LABEL_FONT_SIZE
from .geometry import Point, Vector, BBox, Segment, Tx
from .route import route
from .place import place
from .symbol import calc_symbol_bbox
from ...logger import active_logger
from ...net import NCNet
from ...part import Part
from ...scriptinfo import *
from ...utilities import *


standard_library.install_aliases()

"""
Generate a KiCad EESCHEMA schematic from a Circuit object.
"""

# Sizes of EESCHEMA schematic pages from smallest to largest. Dimensions in mils.
A_sizes_list = [
    ("A4", BBox(Point(0, 0), Point(11693, 8268))),
    ("A3", BBox(Point(0, 0), Point(16535, 11693))),
    ("A2", BBox(Point(0, 0), Point(23386, 16535))),
    ("A1", BBox(Point(0, 0), Point(33110, 23386))),
    ("A0", BBox(Point(0, 0), Point(46811, 33110))),
]
A_sizes = OrderedDict(A_sizes_list)


def preprocess_parts_and_nets(circuit):
    """Add stuff to parts & nets for doing placement and routing of schematics."""

    def rotate_power_pins(part, dont_rotate_pin_threshold=10000):
        """Rotate a part based on the direction of its power pins.

        This function is to make sure that voltage sources face up and gnd pins
        face down.
        """

        def is_pwr(net):
            return net_name.startswith("+")

        def is_gnd(net):
            return "gnd" in net_name.lower()

        # Don't rotate parts with too many pins.
        if len(part) > dont_rotate_pin_threshold:
            return

        # Tally what rotation would make each pwr/gnd pin point up or down.
        rotation_tally = Counter()
        for pin in part:
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

        # Rotate the part in the direction with the most tallies.
        try:
            rotation = rotation_tally.most_common()[0][0]
        except IndexError:
            pass
        else:
            # Rotate part 90-degrees clockwise until the desired rotation is reached.
            tx_cw_90 = Tx(a=0, b=-1, c=1, d=0)  # 90-degree trans. matrix.
            for _ in range(round(rotation / 90)):
                part.tx = part.tx.dot(tx_cw_90)

    def calc_part_bbox(part):
        """Calculate the bare, labeled, and placement bounding boxes and store them in the part."""

        # Find part bounding box excluding any net labels on pins.
        part.bare_bbox = calc_symbol_bbox(part)[1]

        # Expand the bounding box if it's too small in either dimension.
        resize_wh = Vector(0, 0)
        if part.bare_bbox.w < 100:
            resize_wh.x = (100 - part.bare_bbox.w) / 2
        if part.bare_bbox.h < 100:
            resize_wh.y = (100 - part.bare_bbox.h) / 2
        part.bare_bbox = part.bare_bbox.resize(resize_wh)

        # Find expanded bounding box that includes any labels attached to pins.
        part.lbl_bbox = BBox()
        part.lbl_bbox.add(part.bare_bbox)
        lbl_vectors = {
            "U": Vector(0, -1),
            "D": Vector(0, 1),
            "L": Vector(1, 0),
            "R": Vector(-1, 0),
        }
        for pin in part:
            lbl_len = len(pin.label)
            if lbl_len:
                # Add 1 to the label length to account for extra graphics on label.
                lbl_len = (lbl_len + 1) * PIN_LABEL_FONT_SIZE
            lbl_vector = lbl_vectors[pin.orientation] * lbl_len
            part.lbl_bbox.add(pin.pt + lbl_vector)

        # Create a bounding box for placement by adding some space for routing signals from the part.
        # TODO: Resize based on #pins coming from each side of part to ensure adequate routing area.
        part.place_bbox = part.lbl_bbox.resize(Vector(GRID, GRID))

        # Set the active bounding box to the placement version.
        part.bbox = part.place_bbox

    # Pre-process nets.
    net_stubs = circuit.get_net_nc_stubs()
    net_stubs = [net for net in net_stubs if not isinstance(net, NCNet)]
    for net in net_stubs:
        if True or net.netclass != "Power":
            for pin in net.pins:
                pin.label = net.name

    # Pre-process parts
    for part in circuit.parts:

        # Initialize part attributes used for generating schematics.
        part.placed = False
        part.tx = Tx()

        # Initialize pin attributes used for generating schematics.
        for pin in part:
            pin.pt = Point(pin.x, pin.y)
            pin.routed = False
            # Assign empty label if not already labeled.
            pin.label = getattr(pin, "label", "")

        # Rotate parts.  Power pins should face up. GND pins should face down.
        rotate_power_pins(part)

        # Compute bounding boxes around parts
        calc_part_bbox(part)


class Sheet:
    """Data structure for hierarchical sheets of a schematic."""

    def __init__(self, node, filepath, title):
        self.node = node
        self.title = title

        dir = os.path.dirname(filepath)
        self.filename = os.path.join(dir, self.node.node_key + ".sch")
        self.filename_sz = 20
        self.name = self.node.node_key.split(".")[-1]
        self.name_sz = 40

        self.bbox = BBox(Point(0, 0), Point(500, 500))
        self.bbox.add(Point(len("File: "+self.filename) * self.filename_sz, 0))
        self.bbox.add(Point(len("Sheet: "+self.name) * self.name_sz, 0))

        self.tx = Tx()
        self.placed = False

    def to_eeschema(self, tx):
        """Generate schematic files rooted in this sheet and return EESCHEMA code for a box representing this sheet."""

        def get_A_size(bbox):
            """Return the A-size page needed to fit the given bounding box."""

            width = bbox.w
            height = bbox.h * 1.25  # TODO: why 1.25?
            for A_size, page in A_sizes.items():
                if width < page.w and height < page.h:
                    return A_size
            return "A0"  # Nothing fits, so use the largest available.

        # Compute the page size and positioning for this sheet.
        node = self.node
        A_size = get_A_size(node.bbox)
        page_bbox = node.bbox.dot(Tx(d=-1))
        move_to_ctr = A_sizes[A_size].ctr - page_bbox.ctr
        move_to_ctr = move_to_ctr.snap(GRID)  # Keep things on grid.
        move_tx = Tx(d=-1).dot(Tx(dx=move_to_ctr.x, dy=move_to_ctr.y))

        # Generate schematic files for lower levels of the hierarchy.
        with open(self.filename, "w") as f:
            print(
                collect_eeschema_code(
                    node.to_eeschema(move_tx),
                    title=self.title,
                    A_size=A_size,
                ),
                file=f,
            )

        # Create the hierarchical sheet box for insertion into the calling node sheet.
        bbox = self.bbox.dot(self.tx).dot(tx)
        time_hex = hex(int(time.time()))[2:]
        return "\n".join(
            (
            "$Sheet",
            "S {} {} {} {}".format(bbox.ll.x, bbox.ll.y, bbox.w, bbox.h),
            "U {}".format(time_hex),
            'F0 "{}" {}'.format(self.name, self.name_sz),
            'F1 "{}" {}'.format(self.filename, self.filename_sz),
            "$EndSheet",
            ""
            )
        )


class Node:
    """Data structure for holding information about a node in the circuit hierarchy."""

    def __init__(self):
        self.parent = None
        self.children = []
        self.sheets = []
        self.non_sheets = []
        self.parts = []
        self.wires = []
        self.tx = Tx()
        self.bbox = BBox()
        self.placed = False

    def calc_bbox(self):
        """Compute the bounding box for the node in the circuit hierarchy."""

        # If a node has no parent, then its the root node so give it an
        # initial bounding box that's just a starting point for placement.
        if not self.parent:
            self.bbox = BBox(Point(0, 0), Point(0, 0))
        else:
            self.bbox = BBox()

        # Update the bounding box with anything that's been placed.
        for obj in chain(self.parts, self.sheets, self.non_sheets):
            if obj.placed:
                # Only placed parts/sheets/non_sheets contribute to the bounding box.
                tx_bbox = obj.bbox.dot(obj.tx)
                self.bbox.add(tx_bbox)

        # Pad the bounding box for extra spacing when placed.
        self.bbox = self.bbox.resize(Vector(100, 100))

        """Create hierarchical sheets for the circuitry in this node and its children."""
    def create_sheets(self, filepath, title, flatness=0.0):
        """Create hierarchical sheets for the circuitry in this node and its children.

        Args:
            filepath (string): Location where schematic files will be stored.
            title (string): Schematic title.
            flatness (float, optional): Degree of hierarchical flattening (0=completely hierarchical, 1=totally flat). Defaults to 0.0.

        Create hierarchical sheets for the node and its child nodes. Complexity (or size) of a node
        and its children is the total number of part pins they contain. The sum of all the child sizes
        multiplied by the flatness is the number of part pins that can be shown on the schematic
        page before hierarchy is used. The instances of each type of child are expanded and placed
        directly in the sheet as long as the sum of their sizes is below the slack. Otherwise, the
        children are included using hierarchical sheets. The children are handled in order of
        increasing size so small children are more likely to be expanded while large, complicated
        children are included using hierarchical sheets.
        """

        # Complexity of the parts directly instantiated at this hierarchical level.
        self.complexity = sum((len(part) for part in self.parts))

        # Sum the child complexities and use it to compute the number of pins that can be
        # shown before hierarchical sheets are used.
        child_complexity = sum((child.complexity for child in self.children))
        slack = child_complexity * flatness

        # Group the children according to what types of modules they are by removing trailing instance ids.
        child_types = defaultdict(list)
        for child in self.children:
            child_types[re.sub(r"\d+$", "", child.node_key)].append(child)

        # Compute the total size of each group of children.
        child_type_sizes = dict()
        for child_type, children in child_types.items():
            child_type_sizes[child_type] = sum((child.complexity for child in children))

        # Sort the groups from smallest total size to largest.
        sorted_child_type_sizes = sorted([(typ, sz) for typ,sz in child_type_sizes.items()], key=lambda item: item[1])

        # Expand each instance in a group until the slack is used up.
        for child_type, child_type_size in sorted_child_type_sizes:
            if child_type_size <= slack:
                # Include the circuitry of each child instance directly in the sheet.
                self.non_sheets.extend(child_types[child_type])
                # Reduce the slack by the sum of the child sizes.
                slack -= child_type_size
            else:
                # Not enough slack left. Add these children as hierarchical sheets.
                for child in child_types[child_type]:
                    self.sheets.append(Sheet(child, filepath, title))

    def move_part(self, obj, vector, dir):
        """Move part/sheet/non_sheet until it doesn't collide with other parts/sheets/non_sheets in the node."""

        # Make sure object stays on the grid.
        vector = vector.snap(GRID)

        # Keep moving part until no collisions occur.
        collision = True
        while collision:
            collision = False

            # Update the object transformation matrix to apply movement.
            obj.tx = obj.tx.dot(Tx(dx=vector.x, dy=vector.y))

            # Compute the transformed bounding box for the object including the move.
            bbox = obj.bbox.dot(obj.tx)

            # Look for intersections with the other parts/sheets/non_sheets in the node.
            for other_obj in chain(self.parts, self.sheets, self.non_sheets):

                # Don't detect collisions with itself.
                if other_obj is obj:
                    continue

                # Don't try to avoid something that hasn't been placed yet.
                if not other_obj.placed:
                    continue

                # Compute the transformed bounding box for the other object.
                other_bbox = other_obj.bbox.dot(other_obj.tx)

                if bbox.intersects(other_bbox):
                    # Collision found. No need to check any further.
                    collision = True
                    # After the initial move, use the dir vector for all further moves.
                    vector = dir
                    break

        # Exit the loop once the part doesn't collide with anything.
        # The final part.tx matrix records the movements that were made.
        obj.placed = True

    def place_children(self):
        def place_objects(objs):

            # Calculate the initial node bounding box before objects are placed.
            self.calc_bbox()

            # Set up object movement increments.
            start = Point(self.bbox.ctr.x, self.bbox.ll.y - 10 * GRID)
            dir = Vector(GRID, 0)

            for obj in objs:

                # Move any object that hasn't already been moved.
                if not obj.placed:
                    obj_tx_bbox = obj.bbox.dot(obj.tx)
                    ctr_mv = start - Point(obj_tx_bbox.ctr.x, obj_tx_bbox.ul.y)
                    self.move_part(obj, ctr_mv, dir)

                    # Switch movement direction for the next unmoved object.
                    dir = -dir

            # Calculate the node bounding box once the objects have been placed.
            self.calc_bbox()

        place_objects(self.non_sheets)
        place_objects(self.sheets)

    def place(self):
        """Place parts within a hierarchical node."""

        place(self)
        self.place_children()

    def route(self):
        """Route nets between parts of a node."""

        # Use the smaller label bounding box when doing routing.
        for part in self.parts:
            part.bbox = part.lbl_bbox

        detailed_routes = route(self)
        for segment in detailed_routes:
            self.wires.append([segment.p1, segment.p2])

    def to_eeschema(self, tx):

        # List to hold all the EESCHEMA code for this node.
        eeschema_code = []

        # Find the transformation matrix for the placement of the node.
        tx = self.tx.dot(tx)

        # Generate EESCHEMA code for each part in the node.
        for part in self.parts:
            part_code = part_to_eeschema(part, tx=tx)
            eeschema_code.append(part_code)

        # Generate EESCHEMA wiring code between the parts in the node.
        for w in self.wires:
            wire_code = wire_to_eeschema(w, tx=tx)
            eeschema_code.append(wire_code)

        # Generate power connections for the each part in the node.
        for part in self.parts:
            stub_code = power_part_to_eeschema(part, tx=tx)
            if len(stub_code) != 0:
                eeschema_code.append(stub_code)

        # Generate pin labels for stubbed nets on each part in the node.
        for part in self.parts:
            for pin in part:
                pin_label_code = pin_label_to_eeschema(pin, tx=tx)
                eeschema_code.append(pin_label_code)

        # Generate non-sheet portions of the node.
        for non_sheet in self.non_sheets:
            eeschema_code.append(non_sheet.to_eeschema(tx=tx))

        # Generate hierarchical sheet boxes.
        for sheet in self.sheets:
            eeschema_code.append(sheet.to_eeschema(tx=tx))

        # Generate the graphic box that surrounds the node.
        block_name = self.node_key.split(".")[-1]
        bbox_code = bbox_to_eeschema(self.bbox, tx, block_name)
        eeschema_code.append(bbox_code)

        return "\n".join(eeschema_code)


class NodeTree(defaultdict):
    """Make dict that holds part, net, and bbox info for each node in the hierarchy."""

    def __init__(self, circuit, filepath, title, flatness):

        # Set up defaultdict so that if a node with the given hierarchical key doesn't exist,
        # then a new Node object is created and added to the NodeTree.
        super().__init__(lambda: Node())

        # Save a reference to the original circuit.
        self.circuit = circuit

        # Create a node for each part in the circuit.
        for part in circuit.parts:
            # The node links to the part, and the part links to its node.
            node_key = part.hierarchy
            node = self[node_key]  # Creates the node if it doesn't already exist.
            node.parts.append(part)  # Add part to list of parts in node.
            part.node = node  # Add link from part to the node it's in.

        # Create any intermediary nodes in the hierarchy that might not exist
        # because they don't contain any parts.
        for hierarchy in list(self.keys()):
            breadcrumbs = hierarchy.split(".")
            while breadcrumbs:
                node_key = ".".join(breadcrumbs)
                node = self[node_key]  # Creates a node if it doesn't exist.
                node.node_key = node_key
                # Remove the last portion of the hierarchy string to get the
                # key for the parent node.
                breadcrumbs.pop()

        # Fill-in the parent/child relationship for all the nodes in the hierarchy.
        for node_key, node in self.items():
            parent_key = ".".join(node_key.split(".")[0:-1])
            if parent_key:
                parent = self[parent_key]
                parent.children.append(node)
                node.parent = parent
            else:
                root = node

        # Create list of nodes ordered from leaves (no children) to root (no parent).
        self.leaves2root = []
        available_nodes = list(self.values())
        while available_nodes:
            for node in available_nodes:
                add_node = True
                # Only add a node to the list if all its children are already on the list.
                for child in node.children:
                    if child not in self.leaves2root:
                        add_node = False
                        break
                if add_node:
                    # Add the node to the list and remove it from the list of available nodes.
                    self.leaves2root.append(node)
                    available_nodes.remove(node)

        # Partition circuit into sheets, starting from the leaf nodes and working to the root.
        for node in self.leaves2root:
            node.create_sheets(filepath, title, flatness)

        self[""].sheets = [Sheet(root, filepath, title)]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def place(self):
        """Place parts within nodes and then place the nodes."""

        # Place parts within each individual node, starting from the leaves and working to the root.
        for node in self.leaves2root:
            node.place()

    def route(self):
        """Route nets within each node of the tree."""
        for node in self.values():
            node.route()

    def to_eeschema(self):
        """Create EESCHEMA schematic files."""
        tx = Tx()
        sheets = [sheet for node in self.values() for sheet in node.sheets]
        for sheet in sheets:
            sheet.to_eeschema(tx)


def bbox_to_eeschema(bbox, tx, name=None):
    """Create a bounding box using EESCHEMA graphic lines."""

    label_pt = round(bbox.ul.dot(tx))

    bbox = round(bbox.dot(tx))

    graphic_box = []

    if name:
        graphic_box.append(
            "Text Notes {} {} 0    100  ~ 20\n{}".format(label_pt.x, label_pt.y, name)
        )

    graphic_box.append("Wire Notes Line")
    graphic_box.append("	{} {} {} {}".format(bbox.ll.x, bbox.ll.y, bbox.lr.x, bbox.lr.y))
    graphic_box.append("Wire Notes Line")
    graphic_box.append("	{} {} {} {}".format(bbox.lr.x, bbox.lr.y, bbox.ur.x, bbox.ur.y))
    graphic_box.append("Wire Notes Line")
    graphic_box.append("	{} {} {} {}".format(bbox.ur.x, bbox.ur.y, bbox.ul.x, bbox.ul.y))
    graphic_box.append("Wire Notes Line")
    graphic_box.append("	{} {} {} {}".format(bbox.ul.x, bbox.ul.y, bbox.ll.x, bbox.ll.y))
    graphic_box.append("")  # For blank line at end.

    return "\n".join(graphic_box)


def part_to_eeschema(part, tx):
    """Create EESCHEMA code for a part.

    Args:
        part (Part): SKiDL part.
        tx (Tx): Transformation matrix.

    Returns:
        string: EESCHEMA code for the part.

    Notes:
        https://en.wikibooks.org/wiki/Kicad/file_formats#Schematic_Files_Format
    """

    time_hex = hex(int(time.time()))[2:]

    tx = part.tx.dot(tx)
    origin = round(tx.origin)

    eeschema = []
    eeschema.append("$Comp")
    lib = os.path.splitext(part.lib.filename)[0]
    eeschema.append("L {}:{} {}".format(lib, part.name, part.ref))
    eeschema.append("U 1 1 {}".format(time_hex))
    eeschema.append("P {} {}".format(str(origin.x), str(origin.y)))

    # Add part symbols. For now we are only adding the designator
    n_F0 = 1
    for i in range(len(part.draw)):
        if re.search("^DrawF0", str(part.draw[i])):
            n_F0 = i
            break
    eeschema.append(
        'F 0 "{}" {} {} {} {} {} {} {}'.format(
            part.ref,
            part.draw[n_F0].orientation,
            str(origin.x + part.draw[n_F0].x),
            str(origin.y + part.draw[n_F0].y),
            part.draw[n_F0].size,
            "000",
            part.draw[n_F0].halign,
            part.draw[n_F0].valign,
        )
    )

    n_F2 = 2
    for i in range(len(part.draw)):
        if re.search("^DrawF2", str(part.draw[i])):
            n_F2 = i
            break
    eeschema.append(
        'F 2 "{}" {} {} {} {} {} {} {}'.format(
            part.footprint,
            part.draw[n_F2].orientation,
            str(origin.x + part.draw[n_F2].x),
            str(origin.y + part.draw[n_F2].y),
            part.draw[n_F2].size,
            "001",
            part.draw[n_F2].halign,
            part.draw[n_F2].valign,
        )
    )
    eeschema.append("   1   {} {}".format(str(origin.x), str(origin.y)))
    eeschema.append("   {}  {}  {}  {}".format(tx.a, tx.b, tx.c, tx.d))
    eeschema.append("$EndComp")
    eeschema.append("")  # For blank line at end.

    # For debugging: draws a bounding box around a part.
    # eeschema.append(bbox_to_eeschema(part.bbox, tx))
    # eeschema.append(bbox_to_eeschema(part.bare_bbox, tx))

    return "\n".join(eeschema)


def wire_to_eeschema(wire, tx):
    """Create EESCHEMA code for a multi-segment wire.

    Args:
        wire (list): List of (x,y) points for a wire.
        tx (Point): transformation matrix for each point in the wire.

    Returns:
        string: Text to be placed into EESCHEMA file.
    """

    eeschema = []
    pts = [pt.dot(tx) for pt in wire]
    for pt1, pt2 in zip(pts[:-1], pts[1:]):
        eeschema.append("Wire Wire Line")
        eeschema.append("	{} {} {} {}".format(round(pt1.x), round(pt1.y), round(pt2.x), round(pt2.y)))
    eeschema.append("")  # For blank line at end.
    return "\n".join(eeschema)


def power_part_to_eeschema(part, tx=Tx()):
    return ""  # TODO: Remove this.
    out = []
    for pin in part.pins:
        try:
            if not (pin.net is None):
                if pin.net.netclass == "Power":
                    # strip out the '_...' section from power nets
                    t = pin.net.name
                    u = t.split("_")
                    symbol_name = u[0]
                    # find the stub in the part
                    time_hex = hex(int(time.time()))[2:]
                    pin_pt = round(part.origin + offset + Point(pin.x, pin.y))
                    x, y = pin_pt.x, pin_pt.y
                    out.append("$Comp\n")
                    out.append("L power:{} #PWR?\n".format(symbol_name))
                    out.append("U 1 1 {}\n".format(time_hex))
                    out.append("P {} {}\n".format(str(x), str(y)))
                    # Add part symbols. For now we are only adding the designator
                    n_F0 = 1
                    for i in range(len(part.draw)):
                        if re.search("^DrawF0", str(part.draw[i])):
                            n_F0 = i
                            break
                    part_orientation = part.draw[n_F0].orientation
                    part_horizontal_align = part.draw[n_F0].halign
                    part_vertical_align = part.draw[n_F0].valign

                    # check if the pin orientation will clash with the power part
                    if "+" in symbol_name:
                        # voltage sources face up, so check if the pin is facing down (opposite logic y-axis)
                        if pin.orientation == "U":
                            orientation = [-1, 0, 0, 1]
                    elif "gnd" in symbol_name.lower():
                        # gnd points down so check if the pin is facing up (opposite logic y-axis)
                        if pin.orientation == "D":
                            orientation = [-1, 0, 0, 1]
                    out.append(
                        'F 0 "{}" {} {} {} {} {} {} {}\n'.format(
                            "#PWR?",
                            part_orientation,
                            str(x + 25),
                            str(y + 25),
                            str(40),
                            "001",
                            part_horizontal_align,
                            part_vertical_align,
                        )
                    )
                    out.append(
                        'F 1 "{}" {} {} {} {} {} {} {}\n'.format(
                            symbol_name,
                            part_orientation,
                            str(x + 25),
                            str(y + 25),
                            str(40),
                            "000",
                            part_horizontal_align,
                            part_vertical_align,
                        )
                    )
                    out.append("   1   {} {}\n".format(str(x), str(y)))
                    out.append(
                        "   {}   {}  {}  {}\n".format(
                            orientation[0],
                            orientation[1],
                            orientation[2],
                            orientation[3],
                        )
                    )
                    out.append("$EndComp\n")
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
    return "\n" + "".join(out)


def calc_pin_dir(pin):
    """Calculate pin direction accounting for part transformation matrix."""

    # Copy the part trans. matrix, but remove the translation vector, leaving only scaling/rotation stuff.
    tx = pin.part.tx
    tx = Tx(a=tx.a, b=tx.b, c=tx.c, d=tx.d)

    # Use the pin orientation to compute the pin direction vector.
    pin_vector = {
        "U": Point(0, 1),
        "D": Point(0, -1),
        "L": Point(-1, 0),
        "R": Point(1, 0),
    }[pin.orientation]

    # Rotate the direction vector using the part rotation matrix.
    pin_vector = pin_vector.dot(tx)

    # Create an integer tuple from the rotated direction vector.
    pin_vector = (round(pin_vector.x), round(pin_vector.y))

    # Return the pin orientation based on its rotated direction vector.
    return {
        (0, 1): "U",
        (0, -1): "D",
        (-1, 0): "L",
        (1, 0): "R",
    }[pin_vector]


def pin_label_to_eeschema(pin, tx):
    """Create EESCHEMA text of net label attached to a pin."""

    if len(pin.label) == 0 or not pin.is_connected():
        return ""

    label_type = "HLabel"
    for pn in pin.net.pins:
        if pin.part.hierarchy.startswith(pn.part.hierarchy):
            continue
        if pn.part.hierarchy.startswith(pin.part.hierarchy):
            continue
        label_type = "GLabel"
        break

    part_tx = pin.part.tx.dot(tx)
    pt = pin.pt.dot(part_tx)

    pin_dir = calc_pin_dir(pin)
    orientation = {
        "R": 0,
        "D": 1,
        "L": 2,
        "U": 3,
    }[pin_dir]

    return "Text {} {} {} {}    50   UnSpc ~ 0\n{}\n".format(
        label_type, round(pt.x), round(pt.y), orientation, pin.label
    )


def collect_eeschema_code(
    code,
    cur_sheet_num=1,
    total_sheet_num=1,
    title="Default",
    rev_major=0,
    rev_minor=1,
    year=datetime.date.today().year,
    month=datetime.date.today().month,
    day=datetime.date.today().day,
    A_size="A2",
):
    """Collect EESCHEMA header, code, and footer and return as a string."""

    return "\n".join(
        (
            "EESchema Schematic File Version 4",
            "EELAYER 30 0",
            "EELAYER END",
            
            "$Descr {} {} {}".format(
                A_size,
                A_sizes[A_size].max.x,
                A_sizes[A_size].max.y
            ),

            "encoding utf-8",
            "Sheet {} {}".format(cur_sheet_num, total_sheet_num),
            'Title "{}"'.format(title),
            'Date "{}-{}-{}"'.format(year, month, day),
            'Rev "v{}.{}"'.format(rev_major, rev_minor),
            'Comp ""',
            'Comment1 ""',
            'Comment2 ""',
            'Comment3 ""',
            'Comment4 ""',
            "$EndDescr",
            "",

            code,

            "$EndSCHEMATC"
        )
    )


def gen_schematic(circuit, filepath=None, title="SKiDL-Generated Schematic", flatness=0.0):
    """Create a schematic file from a Circuit object."""

    preprocess_parts_and_nets(circuit)

    with NodeTree(circuit, filepath, title, flatness) as node_tree:
        node_tree.place()
        node_tree.route()
        node_tree.to_eeschema()
