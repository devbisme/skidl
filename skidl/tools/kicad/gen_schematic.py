# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.


from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import re
import time
from builtins import range, str
from collections import defaultdict, OrderedDict, Counter
import os.path
from types import DynamicClassAttribute

from future import standard_library

from skidl.tools.kicad.kicad import DrawText

from .geometry import Point, Vector, BBox, Segment, Tx
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

GRID = 50
PIN_LABEL_FONT_SIZE = 50


class Node:
    """Data structure for holding information about a node in the circuit hierarchy."""

    def __init__(self):
        self.parts = []
        self.wires = []
        self.parent = None
        self.children = []
        self.tx = Tx()


def rotate_part_cw_90(part):
    """Rotate a part 90 degrees clockwise."""

    # Concatenate 90 clockwise rotation to part tx.
    tx_cw_90 = Tx(a=0, b=-1, c=1, d=0)
    part.tx = part.tx.dot(tx_cw_90)


def rotate_power_pins(part, pin_cnt_threshold=10000):
    """Rotate a part based on the direction of its power pins.

    Args:
        part (Part): The part to be rotated.
        pin_cnt_threshold (int): Parts with more pins than this will not be rotated.

    This function is to make sure that voltage sources face up and gnd pins
    face down.
    """

    def is_pwr(net):
        return net_name.startswith("+")

    def is_gnd(net):
        return "gnd" in net_name.lower()

    # Don't rotate parts with too many pins.
    if len(part) > pin_cnt_threshold:
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
        for _ in range(round(rotation / 90)):
            rotate_part_cw_90(part)


def calc_part_bbox(part):
    """Calculate the bounding box for a part."""

    # Find bounding box around pins.
    # part.bbox = BBox()
    # for pin in part:
    #     part.bbox.add(pin.pt)

    part.bbox = calc_symbol_bbox(part)[1]

    # Expand the bounding box if it's too small in either dimension.
    resize_xy = Vector(0, 0)
    if part.bbox.w < 100:
        resize_xy.x = (100 - part.bbox.w) / 2
    if part.bbox.h < 100:
        resize_xy.y = (100 - part.bbox.h) / 2
    part.bbox.resize(resize_xy)

    # Find expanded bounding box that includes any labels attached to pins.
    part.lbl_bbox = BBox()
    part.lbl_bbox.add(part.bbox)
    for pin in part:
        # Add 1 to the label length to account for extra graphics on label.
        lbl_len = (len(pin.label) + 1) * PIN_LABEL_FONT_SIZE
        pin_dir = pin.orientation
        if pin_dir == "U":
            lbl_vector = Vector(0, -lbl_len)
        elif pin_dir == "D":
            lbl_vector = Vector(0, lbl_len)
        elif pin_dir == "L":
            lbl_vector = Vector(lbl_len, 0)
        elif pin_dir == "R":
            lbl_vector = Vector(-lbl_len, 0)
        part.lbl_bbox.add(pin.pt + lbl_vector)


def calc_node_bbox(node):
    """Compute the bounding box for the node in the circuit hierarchy."""

    node.bbox = BBox()
    for part in node.parts:
        part_tx_bbox = part.lbl_bbox.dot(part.tx)
        node.bbox.add(part_tx_bbox)

    node.bbox.resize(Vector(100, 50))


def calc_move_part(moving_pin, anchor_pin, other_parts):
    """Move pin to anchor pin and then move it until parts no longer collide."""

    moving_part = moving_pin.part
    anchor_part = anchor_pin.part
    vector = anchor_pin.pt.dot(anchor_part.tx) - moving_pin.pt.dot(moving_part.tx)
    move_part(moving_part, vector, other_parts)


def move_part(part, vector, other_parts):
    """Move part until it doesn't collide with other parts."""

    # Make sure part moves stay on the grid.
    vector = vector.snap(GRID)

    # Setup the movement vector to use if the initial movement leads to collisions.
    avoid_vector = Vector(200, 0) if vector.x > 0 else Vector(-200, 0)
    avoid_vector = avoid_vector.snap(GRID)

    # Keep moving part until no collisions occur.
    while True:
        collision = False

        # Update the part's transformation matrix to apply movement.
        part.tx = part.tx.dot(Tx(dx=vector.x, dy=vector.y))

        # Compute the transformed bounding box for the part including the move.
        lbl_bbox = part.lbl_bbox.dot(part.tx)

        # Look for intersections with the other parts.
        for other_part in other_parts:

            # Don't detect collisions with itself.
            if other_part is part:
                continue

            # Compute the transformed bounding box for the other part.
            other_lbl_bbox = other_part.lbl_bbox.dot(other_part.tx)

            if lbl_bbox.intersects(other_lbl_bbox):
                # Collision found. No need to check any further.
                collision = True
                break

        if not collision:
            # Break out of loop once the part doesn't collide with anything.
            # The final part.tx matrix records the movements that were made.
            break
        else:
            # After the initial move, use the avoid_vector for all further moves.
            vector = avoid_vector

    part.moved = True


def move_node(node, nodes, vector, move_dir):
    """Move node until it doesn't collide with other nodes."""

    # Make sure node moves stay on the grid so the internal parts do.
    vector = vector.snap(GRID)

    # Setup the movement vector to use if the initial movement leads to collisions.
    avoid_vector = Vector(200, 0) if move_dir == "R" else Vector(-200, 0)
    avoid_vector = avoid_vector.snap(GRID)

    root_parent = ".".join(node.node_key.split(".")[0:2])

    # Keep moving node until no collisions occur.
    while True:
        collision = False

        # Update the node's transformation matrix to apply movement.
        node.tx = node.tx.dot(Tx(dx=vector.x, dy=vector.y))

        # Compute the transformed bounding box for the node including the move.
        node_bbox = node.bbox.dot(node.tx)

        # Look for intersections with the other nodes.
        for other_node in nodes:

            # Don't detect collisions with itself.
            if node is other_node:
                continue

            # Only detect collisions with nodes on the same page.
            other_root_parent = ".".join(other_node.node_key.split(".")[0:2])
            if root_parent != other_root_parent:
                continue

            # Compute the transformed bounding box for the other node.
            other_bbox = other_node.bbox.dot(other_node.tx)

            if node_bbox.intersects(other_bbox):
                # Collision found. No need to check any further.
                collision = True
                break

        if not collision:
            # Break out of loop once the node doesn't collide with anything.
            # The final node.tx matrix records the movements that were made.
            break
        else:
            # After the initial move, use the avoid_vector for all further moves.
            vector = avoid_vector


def gen_net_wire(net, node):
    """Generate wire segments for a net."""

    def detect_wire_part_collision(wire, parts):
        """Detect collisions between a wire segment and a collection of parts."""

        for part in parts:
            # bbox = part.bbox.dot(part.tx).dot(part.node.tx)
            bbox = part.bbox.dot(part.tx)
            sides = OrderedDict()
            sides["L"] = Segment(bbox.ul, bbox.ll)
            sides["R"] = Segment(bbox.ur, bbox.lr)
            sides["U"] = Segment(bbox.ul, bbox.ur)
            sides["D"] = Segment(bbox.ll, bbox.lr)

            for side_key, side in sides.items():
                if wire.intersects(side):
                    return part, side_key

        return None, None  # No intersections detected.

    nets_output = []

    # pins = [pin for pin in net.pins if not pin.stub and pin.part.node==node]
    pins = net.pins
    try:
        pin_pairs = zip(pins[:-1], pins[1:])
    except IndexError:
        return nets_output

    for pin1, pin2 in pin_pairs:
        if pin1.routed and pin2.routed:
            continue
        else:
            pin1.routed = True
            pin2.routed = True

            # Calculate the coordinates of a straight line between the 2 pins that need to connect.
            # Apply the part transformation matrix to find the absolute wire endpoint coordinates.
            # Since all wiring is assumed to be internal to this node, don't apply the node
            # transformation matrix.
            pt1 = pin1.pt.dot(pin1.part.tx)
            pt2 = pin2.pt.dot(pin2.part.tx)

            line = [pt1, pt2]
            for i in range(len(line) - 1):
                segment = Segment(line[i], line[i + 1])
                # segment = Segment(Point(line[i][0],line[i][1]), Point(line[i+1][0],line[i+1][1]))
                collided_part, collided_side = detect_wire_part_collision(
                    segment, node.parts
                )

                # if we see a collision then draw the net around the rectangle
                # since we are only going left/right with nets/rectangles the strategy to route
                # around a rectangle is basically making a 'U' shape around it
                if False and collided_part:  # TODO: Remove False
                    print("collided part/wire")
                    if collided_side == "L":
                        # check if we collided on the left or right side of the central part
                        if pin2.part.origin.x < 0 or pin1.part.origin.x < 0:
                            # if pin2.part.sch_bb[0] < 0 or pin1.part.sch_bb[0] < 0:
                            # switch first and last coordinates if one is further left
                            if x1 > x2:
                                t = line[0]
                                line[0] = line[-1]
                                line[-1] = t

                            # draw line down
                            d_x1 = (
                                collided_part.sch_bb.ul.x
                                - 100
                                # collided_part.sch_bb[0] - collided_part.sch_bb[2] - 100
                            )
                            d_y1 = y1
                            # d_y1 = t_y1
                            d_x2 = d_x1
                            d_y2 = (
                                collided_part.sch_bb.ul.y
                                + 200
                                # collided_part.sch_bb[1] + collided_part.sch_bb[3] + 200
                            )
                            # d_x3 = d_x2 + collided_part.sch_bb[2] + 100 + 100
                            d_y3 = d_y2
                            line.insert(i + 1, [d_x1, d_y1])
                            line.insert(i + 2, [d_x2, d_y2])
                            line.insert(i + 3, [x1, d_y3])
                        else:
                            # switch first and last coordinates if one is further left
                            if x1 < x2:
                                t = line[0]
                                line[0] = line[-1]
                                line[-1] = t
                            # draw line down
                            d_x1 = (
                                collided_part.sch_bb.ur.x
                                + 100
                                # collided_part.sch_bb[0] + collided_part.sch_bb[2] + 100
                            )
                            d_y1 = y1
                            # d_y1 = t_y1
                            d_x2 = d_x1
                            d_y2 = (
                                collided_part.sch_bb.ul.y
                                + 200
                                # collided_part.sch_bb[1] + collided_part.sch_bb[3] + 200
                            )
                            # d_x3 = d_x2 + collided_part.sch_bb[2] + 100 + 100
                            d_y3 = d_y2
                            line.insert(i + 1, [d_x1, d_y1])
                            line.insert(i + 2, [d_x2, d_y2])
                            line.insert(i + 3, [x2, d_y3])
                        break
                    if collided_side == "R":
                        # switch first and last coordinates if one is further left
                        if x1 > x2:
                            t = line[0]
                            line[0] = line[-1]
                            line[-1] = t

                        # draw line down
                        d_x1 = collided_part.sch_bb.ll.x - 100
                        # d_x1 = collided_part.sch_bb[0] - collided_part.sch_bb[2] - 100
                        d_y1 = y1
                        # d_y1 = t_y1
                        d_x2 = d_x1
                        d_y2 = collided_part.sch_bb.ul.y + 100
                        # d_y2 = collided_part.sch_bb[1] + collided_part.sch_bb[3] + 100
                        d_x3 = d_x2 - collided_part.sch_bb.w / 2 + 100 + 100
                        # d_x3 = d_x2 - collided_part.sch_bb[2] + 100 + 100
                        d_y3 = d_y2
                        line.insert(i + 1, [d_x1, d_y1])
                        line.insert(i + 2, [d_x2, d_y2])
                        line.insert(i + 3, [x1, d_y3])
                        break

            nets_output.append(line)
    return nets_output


def gen_bbox_eeschema(bbox, tx, name=None):
    """Generate a bounding box using graphic lines."""

    label_pt = round(bbox.ul.dot(tx))

    bbox = round(bbox.dot(tx))

    box = []

    if name:
        box.append(
            "Text Notes {} {} 0    100  ~ 20\n{}\n".format(label_pt.x, label_pt.y, name)
        )

    box.append("Wire Notes Line\n")
    box.append("	{} {} {} {}\n".format(bbox.ll.x, bbox.ll.y, bbox.lr.x, bbox.lr.y))
    box.append("Wire Notes Line\n")
    box.append("	{} {} {} {}\n".format(bbox.lr.x, bbox.lr.y, bbox.ur.x, bbox.ur.y))
    box.append("Wire Notes Line\n")
    box.append("	{} {} {} {}\n".format(bbox.ur.x, bbox.ur.y, bbox.ul.x, bbox.ul.y))
    box.append("Wire Notes Line\n")
    box.append("	{} {} {} {}\n".format(bbox.ul.x, bbox.ul.y, bbox.ll.x, bbox.ll.y))

    return "\n" + "".join(box)


def gen_part_eeschema(part, tx):
    """Generate EESCHEMA code for a part.

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

    out = ["$Comp\n"]
    out.append("L {}:{} {}\n".format(part.lib.filename, part.name, part.ref))
    out.append("U 1 1 {}\n".format(time_hex))
    out.append("P {} {}\n".format(str(origin.x), str(origin.y)))
    # Add part symbols. For now we are only adding the designator
    n_F0 = 1
    for i in range(len(part.draw)):
        if re.search("^DrawF0", str(part.draw[i])):
            n_F0 = i
            break
    out.append(
        'F 0 "{}" {} {} {} {} {} {} {}\n'.format(
            part.ref,
            part.draw[n_F0].orientation,
            str(origin.x + part.draw[n_F0].x),
            str(origin.y - part.draw[n_F0].y),
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
    out.append(
        'F 2 "{}" {} {} {} {} {} {} {}\n'.format(
            part.footprint,
            part.draw[n_F2].orientation,
            str(origin.x + part.draw[n_F2].x),
            str(origin.y - part.draw[n_F2].y),
            part.draw[n_F2].size,
            "001",
            part.draw[n_F2].halign,
            part.draw[n_F2].valign,
        )
    )
    out.append("   1   {} {}\n".format(str(origin.x), str(origin.y)))
    out.append("   {}  {}  {}  {}\n".format(tx.a, tx.b, tx.c, tx.d))
    out.append("$EndComp\n")

    # For debugging: draws a bounding box around a part.
    # out.append(gen_bbox_eeschema(part.lbl_bbox, tx))

    return "\n" + "".join(out)


def gen_wire_eeschema(wire, tx):
    """Generate EESCHEMA code for a multi-segment wire.

    Args:
        wire (list): List of (x,y) points for a wire.
        tx (Point): transformation matrix for each point in the wire.

    Returns:
        string: Text to be placed into EESCHEMA file.
    """

    wire_code = []
    pts = [pt.dot(tx) for pt in wire]
    for pt1, pt2 in zip(pts[:-1], pts[1:]):
        wire_code.append("Wire Wire Line\n")
        wire_code.append("	{} {} {} {}\n".format(pt1.x, pt1.y, pt2.x, pt2.y))
    return "\n" + "".join(wire_code)


def gen_power_part_eeschema(part, tx=Tx()):
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


def gen_pin_label_eeschema(pin, tx):
    """Generate net label attached to a pin."""

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

    return "\nText {} {} {} {}    50   UnSpc ~ 0\n{}\n".format(
        label_type, pt.x, pt.y, orientation, pin.label
    )


def gen_node_bbox_eeschema(node, tx):
    """Generate a graphic bounding box for a node in the circuit hierarchy."""

    hier_levels = node.node_key.split(".")
    if len(hier_levels) > 1:
        level_name = "".join(hier_levels[1:])
    else:
        level_name = node.node_key

    return gen_bbox_eeschema(node.bbox, tx, level_name)


def gen_header_eeschema(
    cur_sheet_num, total_sheet_num, title, rev_major, rev_minor, year, month, day, size
):
    """Generate an EESCHEMA header."""

    total_sheet_num = cur_sheet_num + 1
    header = []
    header.append("EESchema Schematic File Version 4\n")
    header.append("EELAYER 30 0\n")
    header.append("EELAYER END\n")
    header.append(
        "$Descr {} {} {}\n".format(
            size,
            A_sizes[size].max.x,
            A_sizes[size].max.y
            # size, A_sizes[size][0], A_sizes[size][1]
        )
    )
    header.append("encoding utf-8\n")
    header.append("Sheet {} {}\n".format(cur_sheet_num, total_sheet_num))
    header.append('Title "{}"\n'.format(title))
    header.append('Date "{}-{}-{}"\n'.format(year, month, day))
    header.append('Rev "v{}.{}"\n'.format(rev_major, rev_minor))
    header.append('Comp ""\n')
    header.append('Comment1 ""\n')
    header.append('Comment2 ""\n')
    header.append('Comment3 ""\n')
    header.append('Comment4 ""\n')
    header.append("$EndDescr\n")
    return "".join(header)


def gen_footer_eeschema():
    """Generate an EESCHEMA footer."""

    return "$EndSCHEMATC"


def gen_node_block_eeschema(node_name, tx):
    """Generate a hierarchical block for a node in the circuit hierarchy."""

    time_hex = hex(int(time.time()))[2:]
    position = tx.origin
    t = []
    t.append("\n$Sheet\n")
    t.append(
        "S {} {} {} {}\n".format(
            position.x, position.y, 500, 1000
        )  # TODO: magic number.
    )  # upper left x/y, width, height
    t.append("U {}\n".format(time_hex))
    t.append('F0 "{}" 50\n'.format(node_name))
    t.append('F1 "{}.sch" 50\n'.format(node_name))
    t.append("$EndSheet\n")
    return "".join(t)


# Sizes of EESCHEMA schematic pages from smallest to largest. Dimensions in mils.
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
    height = bbox.h * 1.25  # TODO: why 1.25?
    for A_size, page in A_sizes.items():
        if width < page.w and height < page.h:
            return A_size
    return "A0"  # Nothing fits, so use the largest available.


def get_A_size_starting_point(A_size):
    """Return the starting point for placement in the given A-size page."""

    page_bbox = A_sizes[A_size]
    return Point(page_bbox.w / 2, page_bbox.h / 4).snap(GRID)


def collect_eeschema_code(
    code,
    cur_sheet_num=1,
    total_sheet_num=1,
    title="Default",
    rev_major=0,
    rev_minor=1,
    year=2021,
    month=8,
    day=15,
    size="A2",
):
    """Collect EESCHEMA header, code, and footer and return as a string."""
    return "".join(
        (
            gen_header_eeschema(
                cur_sheet_num=cur_sheet_num,
                total_sheet_num=total_sheet_num,
                title=title,
                rev_major=rev_major,
                rev_minor=rev_minor,
                year=year,
                month=month,
                day=day,
                size=size,
            ),
            "".join(code),
            gen_footer_eeschema(),
        )
    )


def preprocess_parts_and_nets(circuit):

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
        part.moved = False
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


def create_node_tree(circuit):

    # Make dict that holds part, net, and bbox info for each node in the hierarchy.
    node_tree = defaultdict(lambda: Node())
    for part in circuit.parts:
        node_tree[part.hierarchy].parts.append(part)
        part.node = node_tree[part.hierarchy]

    # Fill-in the parent/child relationship for all the nodes in the hierarchy.
    for node_key, node in node_tree.items():
        node.node_key = node_key
        parent_key = ".".join(node_key.split(".")[0:-1])
        if parent_key not in node_tree:
            parent = Node()
        else:
            parent = node_tree[parent_key]
            parent.children.append(node)
        node.parent = parent

    return node_tree


def place_parts(node_tree):

    # For each node in hierarchy: Move parts connected to central part by unlabeled nets.
    for node in node_tree.values():

        # Find central part in this node that everything else is placed around.
        def find_central_part(node):
            central_part = node.parts[0]
            for part in node.parts[1:]:
                if len(part) > len(central_part):
                    central_part = part
            return central_part

        node.central_part = find_central_part(node)

        # Go thru the center part's pins, moving any connected parts closer.
        for anchor_pin in node.central_part:

            # Skip unconnected pins.
            if not anchor_pin.is_connected():
                continue

            # Don't move parts connected to labeled (stub) pins.
            if len(anchor_pin.label) != 0:
                continue

            # Don't move parts connected thru power supply nets.
            if anchor_pin.net.netclass == "Power":
                continue

            # Now move any parts connected to this pin.
            for mv_pin in anchor_pin.net.pins:

                # Skip moving the central part.
                if mv_pin.part == node.central_part:
                    continue

                # Skip parts that aren't in the same node of the hierarchy as the center part.
                if mv_pin.part.hierarchy != node.central_part.hierarchy:
                    continue

                # OK, finally move the part connected to this pin.
                calc_move_part(mv_pin, anchor_pin, node.parts)

    # For each node in hierarchy: Move parts connected to parts moved in step previous step.
    for node in node_tree.values():

        for mv_part in node.parts:

            # Skip central part.
            if mv_part is node.central_part:
                continue

            # Skip a part that's already been moved.
            if mv_part.moved:
                continue

            # Find a pin to pin connection where the part needs to be moved.
            for mv_pin in mv_part:

                # Skip unconnected pins.
                if not mv_pin.is_connected():
                    continue

                # Don't move parts connected to labeled (stub) pins.
                if len(mv_pin.label) > 0:
                    continue

                # Don't move parts connected thru power supply nets.
                if mv_pin.net.netclass == "Power":
                    continue

                # Move this part toward parts connected to its pin.
                for anchor_pin in mv_pin.net.pins:

                    # Skip parts that aren't in the same node of the hierarchy as the moving part.
                    if anchor_pin.part.hierarchy != mv_part.hierarchy:
                        continue

                    # Don't move toward the central part.
                    if anchor_pin.part == node.central_part:
                        continue

                    # Skip connections from the part to itself.
                    if anchor_pin.part == mv_part:
                        continue

                    # OK, finally move the part connected to this pin.
                    calc_move_part(mv_pin, anchor_pin, node.parts)

    # Move any remaining parts in each node down & alternating left/right.
    for node in node_tree.values():

        # Get center part for this node.
        central_part = node.central_part

        # Set up part movement increments.
        offset = Vector(GRID, central_part.lbl_bbox.ll.y - 10 * GRID)

        for part in node.parts:

            # Skip central part.
            if part is central_part:
                continue

            # Move any part that hasn't already been moved.
            if not part.moved:
                move_part(part, offset, node.parts)

                # Switch movement direction for the next unmoved part.
                offset.x = -offset.x

    # Create bounding boxes for each node of the hierarchy.
    for node in node_tree.values():
        calc_node_bbox(node)

    # Find maximum depth of node hierarchy.
    max_node_depth = max([h.count(".") for h in node_tree])

    # Move each node of the hierarchy underneath its parent node and left/right, depth-wise.
    for depth in range(2, max_node_depth + 1):

        dir, next_dir = "L", "R"  # Direction of node movement.

        # Search for nodes at the current depth.
        for node in node_tree.values():

            # Skip nodes not at the current depth.
            if node.node_key.count(".") != depth:
                continue

            node_bbox = node.bbox.dot(node.tx)
            parent_bbox = node.parent.bbox.dot(node.parent.tx)

            # Move node so its upper Y is just below parents lower Y.
            # TODO: magic number.
            delta_y = parent_bbox.min.y - node_bbox.max.y - 200

            # Move node so its X coord lines up with parent X coord.
            delta_x = parent_bbox.ctr.x - node_bbox.ctr.x

            # Move node below parent and then to the side to avoid collisions with other nodes.
            # old_pos = node.bbox.ctr
            move_node(node, node_tree.values(), Vector(delta_x, delta_y), move_dir=dir)

            # Alternate placement directions for the next node placement.
            # TODO: find better algorithm than switching sides, maybe based on connections
            dir, next_dir = next_dir, dir


def route_nets(node_tree):

    # Collect the internal nets for each node.
    for node in node_tree.values():
        for part in node.parts:
            for part_pin in part:

                # A label means net is stubbed so there won't be any explicit wires.
                if len(part_pin.label) > 0:
                    continue

                # No explicit wires if the pin is not connected to anything.
                if not part_pin.is_connected():
                    continue

                net = part_pin.net

                # No explicit wires for power nets.
                if net.netclass == "Power":
                    continue

                # Determine if all the pins on this net reside in the node.
                internal_net = True
                for net_pin in net.pins:

                    # Don't consider stubs.
                    if len(net_pin.label) > 0:
                        continue

                    # If a pin is outside this node, then ignore the entire net.
                    if net_pin.part.hierarchy != part_pin.part.hierarchy:
                        internal_net = False
                        break

                # Add wires for this net if the pins are all inside the node.
                if internal_net:
                    node.wires.extend(gen_net_wire(net, node))


def generate_eeschema(circuit, node_tree, title, filepath):

    # Calculate the maximum page dimensions needed for each root hierarchy sheet.
    root_page_sizes = defaultdict(lambda: BBox())
    for node in node_tree.values():
        root_parent = ".".join(node.node_key.split(".")[0:2])
        root_page_sizes[root_parent].add(node.bbox.dot(node.tx))

    # Calculate the A page sizes that fit each root hierarchy sheet.
    root_A_sizes = {
        root_parent: get_A_size(page_size)
        for root_parent, page_size in root_page_sizes.items()
    }

    # Calculate transformation matrices for placing each root parent in the center of its A sheet.
    root_page_txs = {}
    for root_parent, A_size in root_A_sizes.items():
        page_bbox = root_page_sizes[root_parent].dot(Tx(d=-1))
        move = A_sizes[A_size].ctr - page_bbox.ctr
        move = move.snap(GRID)  # Keep things on grid.
        root_page_txs[root_parent] = Tx(d=-1).dot(Tx(dx=move.x, dy=move.y))

    # Generate eeschema code for each node in the circuit hierarchy.
    hier_pg_eeschema_code = defaultdict(lambda: [])
    for node in node_tree.values():

        # List to hold all the EESCHEMA code for this node.
        eeschema_code = []

        # Find the transformation matrix for the placement of the node.
        root_parent = ".".join(node.node_key.split(".")[0:2])
        tx = node.tx.dot(root_page_txs[root_parent])

        # Generate EESCHEMA code for each part in the node.
        for part in node.parts:
            part_code = gen_part_eeschema(part, tx=tx)
            eeschema_code.append(part_code)

        # Generate EESCHEMA wiring code between the parts in the node.
        for w in node.wires:
            wire_code = gen_wire_eeschema(w, tx=tx)
            eeschema_code.append(wire_code)

        # Generate power connections for the each part in the node.
        for part in node.parts:
            stub_code = gen_power_part_eeschema(part, tx=tx)
            if len(stub_code) != 0:
                eeschema_code.append(stub_code)

        # Generate pin labels for stubbed nets on each part in the node.
        for part in node.parts:
            for pin in part:
                pin_label_code = gen_pin_label_eeschema(pin, tx=tx)
                eeschema_code.append(pin_label_code)

        # Generate the graphic box that surrounds the node parts.
        bbox_code = gen_node_bbox_eeschema(node, tx=tx)
        eeschema_code.append(bbox_code)

        # Add generated EESCHEMA code to the root hierarchical page for this node.
        # TODO: Collect the header, code, and footer into the dict.
        hier_pg_eeschema_code[root_parent].append("\n".join(eeschema_code))

    # Collect the EESCHEMA code for each page.
    page_eeschema_code = {}
    hier_eeschema_code = []
    hier_start = get_A_size_starting_point("A4")
    hier_start.x = 1000  # TODO: magic number.
    for root_parent, code in hier_pg_eeschema_code.items():
        A_size = root_A_sizes[root_parent]
        page_eeschema_code[root_parent] = collect_eeschema_code(
            code, cur_sheet_num=1, size=A_size, title=title
        )
        hier_start_tx = Tx(dx=hier_start.x, dy=hier_start.y)
        hier_eeschema_code.append(gen_node_block_eeschema(root_parent, hier_start_tx))
        hier_start += Point(1000, 0)  # TODO: magic number.

    hier_eeschema_code = collect_eeschema_code(
        hier_eeschema_code, cur_sheet_num=1, size="A4", title=title
    )

    # Generate EESCHEMA schematic files.
    if not circuit.no_files:

        # Generate schematic files for lower-levels in the hierarchy.
        dir = os.path.dirname(filepath)
        for root_parent, code in page_eeschema_code.items():
            file_name = os.path.join(dir, root_parent + ".sch")
            with open(file_name, "w") as f:
                print(code, file=f)

        # Generate the schematic file for the top-level of the hierarchy.
        with open(filepath, "w") as f:
            print(hier_eeschema_code, file=f)


def gen_schematic(circuit, filepath=None, title="Default", gen_elkjs=False):
    """Create a schematic file from a Circuit object."""

    preprocess_parts_and_nets(circuit)

    node_tree = create_node_tree(circuit)

    place_parts(node_tree)

    route_nets(node_tree)

    generate_eeschema(circuit, node_tree, title, filepath)


##################################################################################
# INTRONS.
##################################################################################


def gen_elkjs_code(parts, nets):
    # Generate elkjs code that can create an auto diagram with this website:
    # https://rtsys.informatik.uni-kiel.de/elklive/elkgraph.html

    elkjs_code = []

    # range through parts and append code for each part
    for pt in parts:
        error = 0
        try:
            if pt.stub == True:
                continue
        except Exception as e:
            error += 1
        elkjs_part = []
        elkjs_part.append(
            "node {}".format(pt.ref)
            + " {\n"
            + "\tlayout [ size: {},{} ]\n".format(pt.bbox.w, pt.bbox.h)
            + "\tportConstraints: FIXED_SIDE\n"
            + ""
        )

        for p in pt.pins:
            pin_dir = ""
            if p.orientation == "L":
                pin_dir = "EAST"
            elif p.orientation == "R":
                pin_dir = "WEST"
            elif p.orientation == "U":
                pin_dir = "NORTH"
            elif p.orientation == "D":
                pin_dir = "SOUTH"
            elkjs_part.append(
                "\tport p{} ".format(p.num)
                + "{ \n"
                + "\t\t^port.side: {} \n".format(pin_dir)
                + '\t\tlabel "{}"\n'.format(p.name)
                + "\t}\n"
            )
        elkjs_part.append("}")
        elkjs_code.append("\n" + "".join(elkjs_part))

    # range through nets
    for n in nets:
        for p in range(len(n.pins)):
            try:
                part1 = n.pins[p].ref
                pin1 = n.pins[p].num
                part2 = n.pins[p + 1].ref
                pin2 = n.pins[p + 1].num
                t = "edge {}.p{} -> {}.p{}\n".format(part1, pin1, part2, pin2)
                elkjs_code.append(t)
            except:
                pass

    # open file to save elkjs code
    file_path = "elkjs/elkjs.txt"
    f = open(file_path, "a")
    f.truncate(0)  # Clear the file
    for i in elkjs_code:
        print("" + "".join(i), file=f)
    f.close()
