# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2022 Dave Vandenbout.


from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import datetime
import os.path
import re
import time
from builtins import range, str
from collections import OrderedDict

from future import standard_library

from ...schematics.geometry import BBox, Point, Tx, Vector
from .constants import GRID, BLK_INT_PAD, BOX_LABEL_FONT_SIZE, PIN_LABEL_FONT_SIZE
from ...utilities import export_to_all

standard_library.install_aliases()

__all__ = [
    "Eeschema_V5",
    "create_eeschema_file",
    "pin_label_to_eeschema",
    "bbox_to_eeschema",
]

"""
Functions for generating a KiCad EESCHEMA schematic.
"""


@export_to_all
def bbox_to_eeschema(bbox, tx, name=None):
    """Create a bounding box using EESCHEMA graphic lines."""

    # Make sure the box corners are integers.
    bbox = (bbox * tx).round()

    graphic_box = []

    if name:
        # Place name at the lower-left corner of the box.
        name_pt = bbox.ul
        graphic_box.append(
            "Text Notes {} {} 0    {}  ~ 20\n{}".format(
                name_pt.x, name_pt.y, BOX_LABEL_FONT_SIZE, name
            )
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


# Add method for generating EESCHEMA code to Part object.
# FIXME: There's got to be a better way...
from ...part import Part

setattr(Part, "to_eeschema", part_to_eeschema)


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
        eeschema.append("  {} {} {} {}".format(w.p1.x, w.p1.y, w.p2.x, w.p2.y))
    eeschema.append("")  # For blank line at end.
    return "\n".join(eeschema)


def junction_to_eeschema(net, junctions, tx):
    eeschema = []
    for junction in junctions:
        pt = (junction *tx).round()
        eeschema.append("Connection ~ {} {}".format(pt.x, pt.y))
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


# Sizes of EESCHEMA schematic pages from smallest to largest. Dimensions in mils.
A_sizes_list = [
    ("A4", BBox(Point(0, 0), Point(11693, 8268))),
    ("A3", BBox(Point(0, 0), Point(16535, 11693))),
    ("A2", BBox(Point(0, 0), Point(23386, 16535))),
    ("A1", BBox(Point(0, 0), Point(33110, 23386))),
    ("A0", BBox(Point(0, 0), Point(46811, 33110))),
]

# Create bounding box for each A size sheet.
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


@export_to_all
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

    return "Text {} {} {} {}    {}   UnSpc ~ 0\n{}\n".format(
        label_type,
        int(round(pt.x)),
        int(round(pt.y)),
        orientation,
        PIN_LABEL_FONT_SIZE,
        pin.net.name,
    )


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


@export_to_all
class Eeschema_V5:
    """Mixin to add EESCHEMA V5 file creation to the Node class."""

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
            part_code = part.to_eeschema(tx=tx)
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
            pad = Vector(BLK_INT_PAD, BLK_INT_PAD)
            bbox_code = bbox_to_eeschema(self.bbox.resize(pad), tx, block_name)

            return "\n".join((eeschema_code, bbox_code))

        # Create a hierarchical sheet file for storing this unflattened node.
        A_size = get_A_size(flattened_bbox)
        filepath = os.path.join(self.filepath, self.sheet_filename)
        create_eeschema_file(filepath, eeschema_code, title=self.title, A_size=A_size)

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
