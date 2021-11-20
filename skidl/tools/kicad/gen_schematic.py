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

from future import standard_library

from .geometry import Point, Vector, BBox, Segment
from ...logger import active_logger
from ...part import Part
from ...scriptinfo import *
from ...utilities import *


standard_library.install_aliases()

"""
Generate a KiCad EESCHEMA schematic from a Circuit object.
"""


class Node(dict):
    """Data structure for holding information about a node in the circuit hierarchy."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["parts"] = []
        self["wires"] = []
        self["sch_bb"] = []
        self.parent = None
        self.children = []


def round_num(num, base=50):
    return base * round(num / base)


def bbox_to_sch_bb(bbox):
    sch_bb = [0, 0, 0, 0]
    sch_bb[0] = round_num(bbox.ctr.x)
    sch_bb[1] = round_num(bbox.ctr.y)
    sch_bb[2] = round(bbox.w / 2)
    sch_bb[3] = round(bbox.h / 2)
    return sch_bb


def propagate_pin_labels(part):
    """Propagate labels from part pins to all connected pins.

    Args:
        part (Part): The Part object whose pin labels will be propagated.

    This allows the user to only define one label and then connect pins.
    """
    for src_pin in part:
        if len(src_pin.label) and src_pin.net:
            for dst_pin in src_pin.net.pins:
                dst_pin.label = src_pin.label


def rotate_power_pins(part, pin_cnt_threshold=10000):
    """Rotate a part based on the direction of its power pins.

    Args:
        part (Part): The part to be rotated.
        pin_cnt_threshold (int): Parts with more pins than this will not be rotated.

    This function is to make sure that voltage sources face up and gnd pins
    face down.
    """

    # Don't rotate parts with too many pins.
    if len(part) > pin_cnt_threshold:
        return

    # Tally what rotation would make each pwr/gnd pin point up or down.
    rotation_tally = Counter()
    for pin in part:
        net_name = getattr(pin.net, "name", "").lower()
        if "gnd" in net_name:
            if pin.orientation == "U":
                rotation_tally[0] += 1
            if pin.orientation == "D":
                rotation_tally[180] += 1
            if pin.orientation == "L":
                rotation_tally[90] += 1
            if pin.orientation == "R":
                rotation_tally[270] += 1
        elif "+" in net_name:
            if pin.orientation == "D":
                rotation_tally[0] += 1
            if pin.orientation == "U":
                rotation_tally[180] += 1
            if pin.orientation == "L":
                rotation_tally[90] += 1
            if pin.orientation == "R":
                rotation_tally[270] += 1

    # Rotate the part in the direction with the most tallies.
    try:
        rotation = rotation_tally.most_common()[0][0]
    except IndexError:
        pass
    else:
        if rotation != 0:
            for i in range(int(rotation / 90)):
                rotate_90_cw(part)


def rotate_90_cw(part):
    """Rotate a part 90-degrees clockwise."""

    # Replace the pin orientation with the 90-deg CW-rotated orientation.
    pin_rotation_tbl = {
        "D": "L",
        "U": "R",
        "R": "D",
        "L": "U",
    }
    for pin in part:
        pin.x, pin.y = pin.y, -pin.x
        pin.orientation = pin_rotation_tbl[pin.orientation]

    # Replace the part orientation with the 90-deg CW-rotated orientation.
    part_rotation_tbl = {
        (1, 0, 0, -1):  [0, 1, 1, 0],  # 0 => 90 deg.
        (0, 1, 1, 0):   [-1, 0, 0, 1],  # 90 => 180 deg.
        (-1, 0, 0, 1):  [0, -1, -1, 0],  # 180 => 270 deg.
        (0, -1, -1, 0): [1, 0, 0, -1],  # 270 => 0 deg.
    }
    part.orientation = part_rotation_tbl[tuple(part.orientation)]


def calc_part_bbox(part):
    """Calculate the bounding box for a part."""

    # Find bounding box around pins.
    part.bbox = BBox()
    for pin in part:
        part.bbox.add(Point(pin.x, pin.y))

    # Find expanded bounding box that includes any labels attached to pins.
    part.lbl_bbox = BBox()
    part.lbl_bbox.add(part.bbox)
    for pin in part:
        if len(pin.label) > 0:
            lbl_len = (len(pin.label) + 1) * 50
            pin_dir = pin.orientation
            x = pin.x
            y = pin.y
            if pin_dir == "U":
                part.lbl_bbox.add(Point(x, y + lbl_len))
            elif pin_dir == "D":
                part.lbl_bbox.add(Point(x, y - lbl_len))
            elif pin_dir == "L":
                part.lbl_bbox.add(Point(x + lbl_len, y))
            elif pin_dir == "R":
                part.lbl_bbox.add(Point(x - lbl_len, y))

    # Expand the bounding box if it's too small in either dimension.
    resize_xy = Vector(0, 0)
    if part.bbox.w < 100:
        resize_xy.x = 100 - part.bbox.w
    if part.bbox.h < 100:
        resize_xy.y = 100 - part.bbox.h
    part.bbox.resize(resize_xy)
    part.lbl_bbox.resize(resize_xy)

    # Update the equivalent bounding box.
    part.sch_bb = bbox_to_sch_bb(part.bbox)


def calc_node_bbox(node):
    """Compute the bounding box for the node in the circuit hierarchy."""

    node.bbox = BBox()
    for part in node["parts"]:
        node.bbox.add(part.lbl_bbox)

    node.bbox.resize(Vector(200, 100))
    node["sch_bb"] = bbox_to_sch_bb(node.bbox)


def calc_move_part(moving_pin, anchor_pin, other_parts):

    moving_part = moving_pin.part
    anchor_part = anchor_pin.part
    # dx = moving_pin.x + anchor_pin.x + anchor_part.sch_bb[0] + anchor_part.sch_bb[2]
    # dy = -moving_pin.y + anchor_pin.y - anchor_part.sch_bb[1]
    dx = anchor_pin.x + moving_pin.x + anchor_part.bbox.max.x
    dy = anchor_pin.y - moving_pin.y - anchor_part.bbox.ctr.y
    move_part(moving_part, Vector(dx, -dy), other_parts)


def move_part(part, vector, other_parts):
    """Move part until it doesn't collide with other parts."""

    # Setup the movement vector to use if the initial placement leads to collisions.
    avoid_vec = Vector(200, 0) if vector.x > 0 else Vector(-200, 0)

    vec = Vector(vector.x, vector.y)  # EESCHEMA Y direction is reversed.

    while True:
        part.bbox.move(vec)
        part.lbl_bbox.move(vec)
        collision = False

        for other_part in other_parts:
            if other_part is part:
                continue
            if part.lbl_bbox.intersects(other_part.lbl_bbox):
                collision = True
                break

        if not collision:
            break
        else:
            vec = avoid_vec

    part.sch_bb = bbox_to_sch_bb(part.bbox)
    part.moved = True


def move_node(node, nodes, vector, move_dir):

    # Remember where the node was.
    old_position = node.bbox.ctr

    # Setup the movement vector to use if the initial placement leads to collisions.
    avoid_vec = Vector(200, 0) if move_dir == "R" else Vector(-200, 0)

    vec = Vector(vector.x, vector.y)  # EESCHEMA Y direction is reversed.

    # hm_parent = ".".join(hm.split(".")[0:2])
    root_parent = ".".join(node.node_key.split(".")[0:2])

    # Detect collision with other nodes.
    while True:
        node.bbox.move(vec)
        collision = False
        for other_node in nodes:

            # Don't detect collisions with itself.
            if node is other_node:
                continue

            # Only detect collision with hierarchies on the same page.
            other_root_parent = ".".join(other_node.node_key.split(".")[0:2])
            if root_parent != other_root_parent:
                continue

            if node.bbox.intersects(other_node.bbox):
                collision = True
                break

        if not collision:
            break
        else:
            vec = avoid_vec

    node["sch_bb"] = bbox_to_sch_bb(node.bbox)

    # Move the parts in the node based on the change in the node's position.
    chg_pos = node.bbox.ctr - old_position
    for part in node["parts"]:
        move_part(part, chg_pos, [])


def gen_net_wire(net, hierarchy):

    def detect_wire_part_collision(wire, parts):

        for part in parts:
            bbox = part.bbox
            sides = OrderedDict()
            sides["L"] = Segment(bbox.ul, bbox.ll)
            sides["R"] = Segment(bbox.ur, bbox.lr)
            sides["U"] = Segment(bbox.ll, bbox.lr)
            sides["D"] = Segment(bbox.ul, bbox.ur)

            for side_key, side in sides.items():
                if wire.intersects(side):
                    print("Wire/Part Collision!")
                    return part, side_key

        return None, None # No intersections detected.

    nets_output = []
    for i in range(len(net.pins) - 1):
        if net.pins[i].routed and net.pins[i + 1].routed:
            continue
        else:
            net.pins[i].routed = True
            net.pins[i + 1].routed = True

            # Calculate the coordinates of a straight line between the 2 pins that need to connect
            x1 = net.pins[i].part.sch_bb[0] + net.pins[i].x + hierarchy["sch_bb"][0]
            y1 = net.pins[i].part.sch_bb[1] - net.pins[i].y + hierarchy["sch_bb"][1]

            x2 = (
                net.pins[i + 1].part.sch_bb[0]
                + net.pins[i + 1].x
                + hierarchy["sch_bb"][0]
            )
            y2 = (
                net.pins[i + 1].part.sch_bb[1]
                - net.pins[i + 1].y
                + hierarchy["sch_bb"][1]
            )

            line = [[x1, y1], [x2, y2]]

            for i in range(len(line) - 1):
                segment = Segment(Point(line[i][0],line[i][1]), Point(line[i+1][0],line[i+1][1]))
                collided_part, collided_side = detect_wire_part_collision(segment, hierarchy["parts"])

                # if we see a collision then draw the net around the rectangle
                # since we are only going left/right with nets/rectangles the strategy to route
                # around a rectangle is basically making a 'U' shape around it
                if collided_part:

                    if collided_side == "L":
                        # check if we collided on the left or right side of the central part
                        if (
                            net.pins[i + 1].part.sch_bb[0] < 0
                            or net.pins[i].part.sch_bb[0] < 0
                        ):
                            # switch first and last coordinates if one is further left
                            if x1 > x2:
                                t = line[0]
                                line[0] = line[-1]
                                line[-1] = t

                            # draw line down
                            d_x1 = (
                                collided_part.sch_bb[0] - collided_part.sch_bb[2] - 100
                            )
                            d_y1 = t_y1
                            d_x2 = d_x1
                            d_y2 = (
                                collided_part.sch_bb[1] + collided_part.sch_bb[3] + 200
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
                                collided_part.sch_bb[0] + collided_part.sch_bb[2] + 100
                            )
                            d_y1 = t_y1
                            d_x2 = d_x1
                            d_y2 = (
                                collided_part.sch_bb[1] + collided_part.sch_bb[3] + 200
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
                        d_x1 = collided_part.sch_bb[0] - collided_part.sch_bb[2] - 100
                        d_y1 = t_y1
                        d_x2 = d_x1
                        d_y2 = collided_part.sch_bb[1] + collided_part.sch_bb[3] + 100
                        d_x3 = d_x2 - collided_part.sch_bb[2] + 100 + 100
                        d_y3 = d_y2
                        line.insert(i + 1, [d_x1, d_y1])
                        line.insert(i + 2, [d_x2, d_y2])
                        line.insert(i + 3, [x1, d_y3])
                        break

            nets_output.append(line)
    return nets_output


def gen_part_eeschema(part, offset):
    # Generate eeschema code for part from SKiDL part
    # part: SKiDL part
    # c[x,y]: coordinated to place the part
    # https://en.wikibooks.org/wiki/Kicad/file_formats#Schematic_Files_Format

    time_hex = hex(int(time.time()))[2:]

    center = round_num(part.bbox.ctr) + offset

    out = ["$Comp\n"]
    out.append("L {}:{} {}\n".format(part.lib.filename, part.name, part.ref))
    out.append("U 1 1 {}\n".format(time_hex))
    out.append("P {} {}\n".format(str(center.x), str(center.y)))
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
            str(part.draw[n_F0].x + center.x),
            str(part.draw[n_F0].y + center.y),
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
            str(part.draw[n_F2].x + center.x),
            str(part.draw[n_F2].y + center.y),
            part.draw[n_F2].size,
            "001",
            part.draw[n_F2].halign,
            part.draw[n_F2].valign,
        )
    )
    out.append("   1   {} {}\n".format(str(center.x), str(center.y)))
    out.append(
        "   {}   {}  {}  {}\n".format(
            part.orientation[0],
            part.orientation[1],
            part.orientation[2],
            part.orientation[3],
        )
    )
    out.append("$EndComp\n")
    return "\n" + "".join(out)


def gen_wire_eeschema(wire, offset):
    """Generate EESCHEMA code for a multi-segment wire.

    Args:
        wire (list): List of (x,y) points for a wire.
        offset (Point): (x,y) offset for each point in the wire.

    Returns:
        string: Text to be placed into EESCHEMA file.
    """
    wire_code = []
    pts = [Point(pt[0], pt[1]) + offset for pt in wire]
    for pt1, pt2 in zip(pts[:-1], pts[1:]):
        wire_code.append("Wire Wire Line\n")
        wire_code.append("	{} {} {} {}\n".format(pt1.x, pt1.y, pt2.x, pt2.y))
    return "\n" + "".join(wire_code)


def gen_power_part_eeschema(part, orientation=[1, 0, 0, -1], offset=Point(0, 0)):
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
                    x = round_num(part.bbox.ctr.x) + pin.x + offset.x
                    y = round_num(part.bbox.ctr.y) - pin.y + offset.y
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


def gen_pin_label_eeschema(pin, offset):
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

    part_origin = round_num(pin.part.bbox.ctr) + offset
    x = pin.x + part_origin.x
    y = -pin.y + part_origin.y  # EESCHEMA Y direction is reversed.

    orientation = {
        "R": 0,
        "D": 1,
        "L": 2,
        "U": 3,
    }[pin.orientation]

    return "\nText {} {} {} {}    50   UnSpc ~ 0\n{}\n".format(
        label_type, x, y, orientation, pin.label
    )


def gen_node_bbox_eeschema(node, offset):
    """Generate a graphic bounding box for a node in the circuit hierarchy."""

    hier_levels = node.node_key.split(".")
    if len(hier_levels) > 1:
        level_name = "".join(hier_levels[1:])
    else:
        level_name = node.node_key

    bbox = BBox(node.bbox.min, node.bbox.max)
    bbox.move(offset)
    bbox.round()

    label_pt = bbox.ll

    box = []

    box.append(
        "Text Notes {} {} 0    100  ~ 20\n{}\n".format(
            label_pt.x, label_pt.y, level_name
        )
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


def gen_node_block_eeschema(node_name, position):
    """Generate a hierarchical block for a node in the circuit hierarchy."""

    time_hex = hex(int(time.time()))[2:]
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
    height = int(bbox.h * 1.25)  # TODO: why 1.25?
    for A_size, page in A_sizes.items():
        if width < page.w and height < page.h:
            return A_size
    return "A0"  # Nothing fits, so use the largest available.


def get_A_size_starting_point(A_size):
    """Return the starting point for placement in the given A-size page."""

    page_bbox = A_sizes[A_size]
    x = round_num(page_bbox.w / 2)
    y = round_num(page_bbox.h / 4)
    return Point(x, y)


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


def gen_schematic(self, file_=None, _title="Default", gen_elkjs=False):
    """Create a schematic file from a Circuit object."""

    # Pre-process parts
    for part in self.parts:

        # Initialize part attributes used for generating schematics.
        part.orientation = [1, 0, 0, -1]
        part.sch_bb = [0, 0, 0, 0]  # Set schematic location to x, y, width, height.
        part.moved = False

        # Initialize pin attributes used for generating schematics.
        for pin in part:
            pin.routed = False
            pin.label = getattr(
                pin, "label", ""
            )  # Assign empty label if not already labeled.

        # Rotate <3 pin parts that have power nets.  Pins with power pins should face up.
        # Pins with GND pins should face down.
        rotate_power_pins(part)

        # Copy labels from one pin to each connected pin.  This allows the user to only label
        # a single pin, then connect it normally, instead of having to label every pin in that net
        propagate_pin_labels(part)

        # Generate bounding boxes around parts
        calc_part_bbox(part)

    # Make dict that holds part, net, and bbox info for each node in the hierarchy.
    circuit_hier = defaultdict(lambda: Node())
    for part in self.parts:
        circuit_hier[part.hierarchy]["parts"].append(part)

    # Fill-in the parent/child relationship for all the nodes in the hierarchy.
    for node_key, node in circuit_hier.items():
        node.node_key = node_key
        parent_key = ".".join(node_key.split(".")[0:-1])
        if parent_key not in circuit_hier:
            parent = Node()
        else:
            parent = circuit_hier[parent_key]
            parent.children.append(node)
        node.parent = parent

    # For each node in hierarchy: Move parts connected to central part by unlabeled nets.
    for node in circuit_hier.values():

        # Center part of hierarchy that everything else is placed around.
        anchor_part = node["parts"][0]  # TODO: Smarter selection of center part.

        # Go thru the center part's pins, moving any connected parts closer.
        for anchor_pin in anchor_part:

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

                # Skip moving the center part.
                if mv_pin.part == anchor_part:
                    continue

                # Skip parts that aren't in the same node of the hierarchy as the center part.
                if mv_pin.part.hierarchy != anchor_part.hierarchy:
                    continue

                # OK, finally move the part connected to this pin.
                calc_move_part(mv_pin, anchor_pin, node["parts"])

    # For each node in hierarchy: Move parts connected to parts moved in step previous step.
    for node in circuit_hier.values():

        # Get the center part for this node from the last phase.
        center_part = node["parts"][0]

        for mv_part in node["parts"]:

            # Skip center part.
            if mv_part is center_part:
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

                    # Don't move toward the center part.
                    if anchor_pin.part == center_part:
                        continue

                    # Skip connections from the part to itself.
                    if anchor_pin.part == mv_part:
                        continue

                    # OK, finally move the part connected to this pin.
                    calc_move_part(mv_pin, anchor_pin, node["parts"])

    # Move any remaining parts in each node down & alternating left/right.
    for node in circuit_hier.values():

        # Set up part movement increments.
        offset_x = 50  # Use fine movements to get close packing on X dim.
        # TODO: magic number.
        offset_y = node["parts"][0].bbox.max.y + 500

        # Get center part for this node.
        center_part = node["parts"][0]

        for part in node["parts"]:

            # Skip center part.
            if part is center_part:
                continue

            # Move any part that hasn't already been moved.
            if not part.moved:
                move_part(part, Point(offset_x, offset_y), node["parts"])

                # Switch movement direction for the next unmoved part.
                offset_x = -offset_x

    # Create bounding boxes for each node of the hierarchy.
    for node in circuit_hier.values():
        calc_node_bbox(node)

    # Find maximum depth of node hierarchy.
    max_node_depth = max([h.count(".") for h in circuit_hier])

    # Move each node of the hierarchy underneath its parent node and left/right, depth-wise.
    for depth in range(2, max_node_depth + 1):

        dir, next_dir = "L", "R"  # Direction of node movement.

        # Search for nodes at the current depth.
        for node in circuit_hier.values():

            # Skip nodes not at the current depth.
            if node.node_key.count(".") != depth:
                continue

            # Move node so its upper Y is just below parents lower Y.
            delta_y = (
                node.parent.bbox.max.y - node.bbox.min.y + 200
            )  # TODO: magic number.

            # Move node so its X coord lines up with parent X coord.
            delta_x = node.parent.bbox.ctr.x - node.bbox.ctr.x

            # Move node below parent and then to the side to avoid collisions with other nodes.
            # old_pos = node.bbox.ctr
            move_node(
                node, circuit_hier.values(), Vector(delta_x, delta_y), move_dir=dir
            )

            # Alternate placement directions for the next node placement.
            # TODO: find better algorithm than switching sides, maybe based on connections
            dir, next_dir = next_dir, dir

    # Collect the internal nets for each node.
    for node in circuit_hier.values():
        for part in node["parts"]:
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
                    node["wires"].extend(gen_net_wire(net, node))

    # At this point the hierarchy should be completely generated and ready for generating code.

    # Calculate the maximum page dimensions needed for each root hierarchy sheet.
    page_sizes = defaultdict(lambda: BBox())
    for node in circuit_hier.values():
        root_parent = ".".join(node.node_key.split(".")[0:2])
        page_sizes[root_parent].add(node.bbox)

    # Generate eeschema code for each node in the circuit hierarchy.
    hier_pg_eeschema_code = defaultdict(lambda: [])
    for node in circuit_hier.values():

        # List to hold all the code for the hierarchy
        eeschema_code = []

        # Find starting point for part placement
        root_parent = ".".join(node.node_key.split(".")[0:2])
        A_size = get_A_size(page_sizes[root_parent])
        sch_start = get_A_size_starting_point(A_size)

        # Generate part code
        for part in node["parts"]:
            part_code = gen_part_eeschema(part, offset=sch_start)
            eeschema_code.append(part_code)

        # Generate net wire code.
        offset = sch_start - round_num(node.bbox.ctr)
        for w in node["wires"]:
            wire_code = gen_wire_eeschema(w, offset=offset)
            eeschema_code.append(wire_code)

        # Generate power net stubs.
        for part in node["parts"]:
            stub_code = gen_power_part_eeschema(part, offset=sch_start)
            if len(stub_code) != 0:
                eeschema_code.append(stub_code)

        # Generate pin labels for stubbed nets.
        for part in node["parts"]:
            for pin in part:
                pin_label_code = gen_pin_label_eeschema(pin, offset=sch_start)
                eeschema_code.append(pin_label_code)

        # Generate node bounding box.
        bbox_code = gen_node_bbox_eeschema(node, offset=sch_start)
        eeschema_code.append(bbox_code)

        # Add generated EESCHEMA code to the root hierarchical page for this node.
        root_parent = ".".join(node.node_key.split(".")[0:2])
        # TODO: Collect the header, code, and footer into the dict.
        hier_pg_eeschema_code[root_parent].append("\n".join(eeschema_code))

    # Collect the EESCHEMA code to be saved in a file for each page.
    page_eeschema_code = {}
    hier_eeschema_code = []
    hier_start = get_A_size_starting_point("A4")
    hier_start.x = 1000  # TODO: magic number.
    for root_parent, code in hier_pg_eeschema_code.items():
        A_size = get_A_size(page_sizes[root_parent])
        page_eeschema_code[root_parent] = collect_eeschema_code(
            code, cur_sheet_num=1, size=A_size, title=_title
        )
        hier_eeschema_code.append(gen_node_block_eeschema(root_parent, hier_start))
        hier_start += Point(1000, 0)  # TODO: magic number.

    hier_eeschema_code = collect_eeschema_code(
        hier_eeschema_code, cur_sheet_num=1, size="A4", title=_title
    )

    # Generate EESCHEMA schematic files.
    if not self.no_files:

        # Generate schematic files for lower-levels in the hierarchy.
        dir = os.path.dirname(file_)
        for root_parent, code in page_eeschema_code.items():
            file_name = os.path.join(dir, root_parent + ".sch")
            with open(file_name, "w") as f:
                print(code, file=f)

        # Generate the schematic file for the top-level of the hierarchy.
        with open(file_, "w") as f:
            print(hier_eeschema_code, file=f)


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
