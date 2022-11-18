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

from .common import GRID, PIN_LABEL_FONT_SIZE
from ...schematics.geometry import Point, Vector, BBox, Tx
from ...schematics.route import Router
from ...schematics.place import Placer
from .v5 import calc_symbol_bbox
from ...net import NCNet
from ...scriptinfo import *
from ...utilities import *


standard_library.install_aliases()

"""
Generate a KiCad EESCHEMA schematic from a Circuit object.
"""

# Sizes of EESCHEMA schematic pages from smallest to largest. Dimensions in mils.


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


class Node(Placer, Router):
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

        from ...circuit import HIER_SEP

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

    def to_eeschema(self, sheet_tx=Tx()):
        """Convert node circuitry to an EESCHEMA sheet.

        Args:
            sheet_tx (Tx, optional): Scaling/translation matrix for sheet. Defaults to Tx().

        Returns:
            str: EESCHEMA text for the node circuitry.
        """

        from ...circuit import HIER_SEP

        # List to hold all the EESCHEMA code for this node.
        eeschema_code = []

        if self.flattened:
            # Create the transformation matrix for the placement of the parts in the node.
            tx = self.tx * sheet_tx
        else:
            # Unflattened nodes are placed in their own sheet, so compute
            # their bounding box as if they *were* flattened and use that to
            # find the transformation matrix for an appropriately-sized sheet.
            flattened_bbox = self.internal_bbox()
            tx = calc_sheet_tx(flattened_bbox)

        # Generate EESCHEMA code for each child of this node.
        for child in self.children.values():
            eeschema_code.append(child.to_eeschema(tx))

        # Generate EESCHEMA code for each part in the node.
        for part in self.parts:
            part_code = part_to_eeschema(part, tx=tx)
            eeschema_code.append(part_code)

        # Generate EESCHEMA wiring code between the parts in the node.
        for net, wire in self.wires.items():
            wire_code = wire_to_eeschema(net, wire, tx=tx)
            eeschema_code.append(wire_code)
        for net, junctions in self.junctions.items():
            junction_code = junction_to_eeschema(net, junctions, tx=tx)
            eeschema_code.append(junction_code)

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

        # Join EESCHEMA code into one big string.
        eeschema_code = "\n".join(eeschema_code)

        # If this node was flattened, then return the EESCHEMA code and surrounding box
        # for inclusion in the parent node.
        if self.flattened:

            # Generate the graphic box that surrounds the flattened hierarchical block of this node.
            block_name = self.name.split(HIER_SEP)[-1]
            bbox_code = bbox_to_eeschema(self.bbox, tx, block_name)

            return "\n".join((eeschema_code, bbox_code))

        # Create a hierarchical sheet file for storing this unflattened node.
        A_size = get_A_size(flattened_bbox)
        filepath = os.path.join(self.filepath, self.sheet_filename)
        create_eeschema_file(
            filepath, eeschema_code, title=self.title, A_size=A_size
        )

        # Create the hierarchical sheet for insertion into the calling node sheet.
        bbox = (self.bbox * self.tx * sheet_tx).round()
        time_hex = hex(int(time.time()))[2:]
        return "\n".join(
            (
                "$Sheet",
                "S {} {} {} {}".format(bbox.ll.x, bbox.ll.y, bbox.w, bbox.h),
                "U {}".format(time_hex),
                'F0 "{}" {}'.format(self.name, self.name_sz),
                'F1 "{}" {}'.format(self.sheet_filename, self.filename_sz),
                "$EndSheet",
                "",
            )
        )


def bbox_to_eeschema(bbox, tx, name=None):
    """Create a bounding box using EESCHEMA graphic lines."""

    # Make sure the box corners are integers.
    bbox = (bbox * tx).round()

    graphic_box = []

    if name:
        # Place name at the upper-left corner of the box.
        name_pt = bbox.ul
        graphic_box.append(
            "Text Notes {} {} 0    100  ~ 20\n{}".format(name_pt.x, name_pt.y, name)
        )

    graphic_box.append("Wire Notes Line")
    graphic_box.append(
        "	{} {} {} {}".format(bbox.ll.x, bbox.ll.y, bbox.lr.x, bbox.lr.y)
    )
    graphic_box.append("Wire Notes Line")
    graphic_box.append(
        "	{} {} {} {}".format(bbox.lr.x, bbox.lr.y, bbox.ur.x, bbox.ur.y)
    )
    graphic_box.append("Wire Notes Line")
    graphic_box.append(
        "	{} {} {} {}".format(bbox.ur.x, bbox.ur.y, bbox.ul.x, bbox.ul.y)
    )
    graphic_box.append("Wire Notes Line")
    graphic_box.append(
        "	{} {} {} {}".format(bbox.ul.x, bbox.ul.y, bbox.ll.x, bbox.ll.y)
    )
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

    tx = part.tx * tx
    origin = tx.origin.round()
    time_hex = hex(int(time.time()))[2:]
    unit_num = getattr(part, "num", 1)

    eeschema = []
    eeschema.append("$Comp")
    lib = os.path.splitext(part.lib.filename)[0]
    eeschema.append("L {}:{} {}".format(lib, part.name, part.ref))
    eeschema.append("U {} 1 {}".format(unit_num, time_hex))
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

    return "\n".join(eeschema)


def wire_to_eeschema(net, wire, tx):
    """Create EESCHEMA code for a multi-segment wire.

    Args:
        net (Net): Net associated with the wire.
        wire (list): List of Segments for a wire.
        tx (Tx): transformation matrix for each point in the wire.

    Returns:
        string: Text to be placed into EESCHEMA file.
    """

    eeschema = []
    for segment in wire:
        eeschema.append("Wire Wire Line")
        w = (segment * tx).round()
        eeschema.append("  " + str(w))
    eeschema.append("")  # For blank line at end.
    return "\n".join(eeschema)


def junction_to_eeschema(net, junctions, tx):
    eeschema = []
    for junction in junctions:
        eeschema.append("Connection ~ {}".format((junction * tx).round()))
    eeschema.append("")  # For blank line at end.
    return "\n".join(eeschema)


def power_part_to_eeschema(part, tx=Tx()):
    return ""  # REMOVE: Remove this.
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
                    pin_pt = (part.origin + offset + Point(pin.x, pin.y)).round()
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
    pin_vector = pin_vector * tx

    # Create an integer tuple from the rotated direction vector.
    pin_vector = (int(round(pin_vector.x)), int(round(pin_vector.y)))

    # Return the pin orientation based on its rotated direction vector.
    return {
        (0, 1): "U",
        (0, -1): "D",
        (-1, 0): "L",
        (1, 0): "R",
    }[pin_vector]


def pin_label_to_eeschema(pin, tx):
    """Create EESCHEMA text of net label attached to a pin."""

    if pin.stub is False or not pin.is_connected():
        # No label if pin is not connected or is connected to an explicit wire.
        return ""

    label_type = "HLabel"
    for pn in pin.net.pins:
        if pin.part.hierarchy.startswith(pn.part.hierarchy):
            continue
        if pn.part.hierarchy.startswith(pin.part.hierarchy):
            continue
        label_type = "GLabel"
        break

    part_tx = pin.part.tx * tx
    pt = pin.pt * part_tx

    pin_dir = calc_pin_dir(pin)
    orientation = {
        "R": 0,
        "D": 1,
        "L": 2,
        "U": 3,
    }[pin_dir]

    return "Text {} {} {} {}    50   UnSpc ~ 0\n{}\n".format(
        label_type, int(round(pt.x)), int(round(pt.y)), orientation, pin.net.name
    )


# Create bounding box for each A size sheet.
A_sizes_list = [
    ("A4", BBox(Point(0, 0), Point(11693, 8268))),
    ("A3", BBox(Point(0, 0), Point(16535, 11693))),
    ("A2", BBox(Point(0, 0), Point(23386, 16535))),
    ("A1", BBox(Point(0, 0), Point(33110, 23386))),
    ("A0", BBox(Point(0, 0), Point(46811, 33110))),
]
A_sizes = OrderedDict(A_sizes_list)


def get_A_size(bbox):
    """Return the A-size page needed to fit the given bounding box."""

    width = bbox.w
    height = bbox.h * 1.25  # HACK: why 1.25?
    for A_size, page in A_sizes.items():
        if width < page.w and height < page.h:
            return A_size
    return "A0"  # Nothing fits, so use the largest available.


def calc_sheet_tx(bbox):
    """Compute the page size and positioning for this sheet."""
    A_size = get_A_size(bbox)
    page_bbox = bbox * Tx(d=-1)
    move_to_ctr = A_sizes[A_size].ctr.snap(GRID) - page_bbox.ctr.snap(GRID)
    move_tx = Tx(d=-1) * Tx(dx=move_to_ctr.x, dy=move_to_ctr.y)
    return move_tx


def create_eeschema_file(
    filename,
    contents,
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
    """Write EESCHEMA header, contents, and footer to a file."""

    with open(filename, "w") as f:
        f.write(
            "\n".join(
                (
                    "EESchema Schematic File Version 4",
                    "EELAYER 30 0",
                    "EELAYER END",
                    "$Descr {} {} {}".format(
                        A_size, A_sizes[A_size].max.x, A_sizes[A_size].max.y
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
                    contents,
                    "$EndSCHEMATC",
                )
            )
        )


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
