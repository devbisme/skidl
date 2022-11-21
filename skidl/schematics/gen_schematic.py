# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.


from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from itertools import chain
import re
from builtins import range
from collections import defaultdict, Counter

from future import standard_library

from ..tools.kicad.constants import PIN_LABEL_FONT_SIZE
from .geometry import Point, Vector, BBox, Tx
from .route import Router
from .place import Placer
from ..tools.kicad.v5 import calc_symbol_bbox
from ..net import NCNet
from ..scriptinfo import get_script_name
from ..tools.kicad.eeschema_v5 import *


standard_library.install_aliases()

"""
Generate a KiCad EESCHEMA schematic from a Circuit object.
"""


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

            # Initialize transform matrix to no translation / no rotation.
            part_unit.tx = Tx()

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

        # Find part bounding box excluding any net labels on pins.
        # FIXME: part.lbl_bbox could be substituted for part.bbox.
        bare_bboxes = calc_symbol_bbox(part)[1:]

        for part_unit, bare_bbox in zip(units(part), bare_bboxes):
            # Expand the bounding box if it's too small in either dimension.
            resize_wh = Vector(0, 0)
            if bare_bbox.w < 100:
                resize_wh.x = (100 - bare_bbox.w) / 2
            if bare_bbox.h < 100:
                resize_wh.y = (100 - bare_bbox.h) / 2
            bare_bbox = bare_bbox.resize(resize_wh)

            # Find expanded bounding box that includes any labels attached to pins.
            part_unit.lbl_bbox = BBox()
            part_unit.lbl_bbox.add(bare_bbox)
            lbl_vectors = {
                "U": Vector(0, -1),
                "D": Vector(0, 1),
                "L": Vector(1, 0),
                "R": Vector(-1, 0),
            }
            for pin in part_unit:
                if pin.stub:
                    # Pins connected to net stubs require net name labels.
                    lbl_len = len(pin.net.name)
                    if lbl_len:
                        # Add 1 to the label length to account for extra graphics on label.
                        lbl_len = (lbl_len + 1) * PIN_LABEL_FONT_SIZE
                    lbl_vector = lbl_vectors[pin.orientation] * lbl_len
                    part_unit.lbl_bbox.add(pin.pt + lbl_vector)

            # Set the active bounding box to the labeled version.
            part_unit.bbox = part_unit.lbl_bbox

    # Pre-process nets.
    net_stubs = circuit.get_net_nc_stubs()
    net_stubs = [net for net in net_stubs if not isinstance(net, NCNet)]
    for net in net_stubs:
        if True or net.netclass != "Power": # FIXME: figure out what to do with power nets.
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

def finalize_parts_and_nets(circuit):
    """Restore parts and nets after place & route is done."""

    # Return pins from the part units to their parent part.
    for part in circuit.parts:
        part.grab_pins()


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

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def add_circuit(self, circuit):
        """Add parts in circuit to node and its children.

        Args:
            circuit (Circuit): Circuit object.
        """

        # Build the circuit node hierarchy by adding the parts.
        for part in circuit.parts:
            self.add_part(part)

        # Flatten the hierarchy as specified by the flatness parameter.
        self.flatten(self.flatness)

    def add_part(self, part, level=0):
        """Add a part to the node at the appropriate level of the hierarchy."""

        from ..circuit import HIER_SEP

        level_names = part.hierarchy.split(HIER_SEP)
        self.name = level_names[level]
        base_filename = "_".join([self.top_name] + level_names[0 : level + 1]) + ".sch"
        self.sheet_filename = base_filename
        # self.sheet_filename = os.path.join(self.filepath, base_filename)

        if level == len(level_names) - 1:
            # Add part to node at this level in the hierarchy.
            if not part.unit:
                # Monolithic part so just add it to the node.
                self.parts.append(part)
            else:
                # Multi-unit part so add each unit to the node.
                for p in part.unit.values():
                    self.parts.append(p)
        else:
            # Add part to child node below the current hierarchical level.
            child_node = self.children[level_names[level + 1]]
            child_node.parent = self
            child_node.add_part(part, level + 1)

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


def gen_schematic(
    circuit, filepath=".", top_name=get_script_name(), title="SKiDL-Generated Schematic", flatness=0.0
):
    """Create a schematic file from a Circuit object."""

    preprocess_parts_and_nets(circuit)

    with Node(circuit, filepath, top_name, title, flatness) as node:
        node.place()
        node.route()
        node.to_eeschema()

    finalize_parts_and_nets(circuit)
