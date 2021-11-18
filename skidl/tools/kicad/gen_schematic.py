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
from collections import defaultdict, OrderedDict
import os.path

from future import standard_library

from .geometry import Point, Vector, BBox
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
    return int(base * round(num / base))


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


def rotate_power_pins(part):
    """Rotate a part based on the direction of its power pins.

    Args:
        part (Part): The part to be rotated.

    This function is to make sure that voltage sources face up and gnd pins
    face down. Only rotate parts with 3 pins or less.
    """

    if len(part) <= 3:
        for pin in part:
            rotate = 0
            net_name = getattr(pin.net, "name", "").lower()
            if "gnd" in net_name:
                if pin.orientation == "U":
                    break  # pin is already facing down, break
                if pin.orientation == "D":
                    rotate = 180
                if pin.orientation == "L":
                    rotate = 90
                if pin.orientation == "R":
                    rotate = 270
            elif "+" in net_name:
                if pin.orientation == "D":
                    break  # pin is already facing up, break
                if pin.orientation == "U":
                    rotate = 180
                if pin.orientation == "L":
                    rotate = 90
                if pin.orientation == "R":
                    rotate = 270
            if rotate != 0:
                for i in range(int(rotate / 90)):
                    rotate_90_cw(part)


def rotate_90_cw(part):
    """Rotate a part 90-degrees clockwise.

    Args:
        part (Part): The part to be rotated.

    Rotating the part CW 90 switches the x/y axis and makes the new height negative.
    https://stackoverflow.com/questions/2285936/easiest-way-to-rotate-a-rectangle
    """

    rotation_matrix = [
        # Assume starting with x: -700 y: 1200
        [1, 0, 0, -1],  # 0 deg x: 1200 y:-700
        [0, 1, 1, 0],  # 90 deg x: 1200  y: -700
        [-1, 0, 0, 1],  # 180 deg x:  700  y: 1200
        [0, -1, -1, 0],  # 270 deg x:-1200  y:  700
        [1, 0, 0, -1],  # Repeat first vector to simplify loop below.
    ]

    # switch the height and width
    part.sch_bb[2], part.sch_bb[3] = part.sch_bb[3], part.sch_bb[2]

    # range through the pins and rotate them
    for pin in part:
        pin.x, pin.y = pin.y, -pin.x
        if pin.orientation == "D":
            pin.orientation = "L"
        elif pin.orientation == "U":
            pin.orientation = "R"
        elif pin.orientation == "R":
            pin.orientation = "D"
        elif pin.orientation == "L":
            pin.orientation = "U"

    # Find the part orientation and replace it with the next orientation in the array.
    # (The first orientation in the array is repeated at the end of the array to
    # remove the rollover logic.)
    for n in range(len(rotation_matrix) - 1):
        if rotation_matrix[n] == part.orientation:
            part.orientation = rotation_matrix[n + 1]
            break


def bbox_to_sch_bb(bbox, sch_bb):
    sch_bb[0] = round_num(bbox.ctr.x)
    sch_bb[1] = round_num(bbox.ctr.y)
    sch_bb[2] = bbox.w / 2
    sch_bb[3] = bbox.h / 2


def calc_bbox_part(part):
    """Calculate the bounding box for a part."""

    # Bounding box around pins.
    part.bbox = BBox()
    for pin in part:
        part.bbox.add(Point(pin.x, pin.y))

    # Bounding box around pins and any attached labels.
    part.lbl_bbox = BBox()
    part.lbl_bbox.add(part.bbox)
    for pin in part:
        if len(pin.label) > 0:
            lbl_len = (len(pin.label) + 1) * 50
            pin_dir = pin.orientation
            x = pin.x
            y = pin.y
            if pin_dir == "U":
                lbl_bbox = BBox(Point(x, y), Point(x, y - lbl_len))
            elif pin_dir == "D":
                lbl_bbox = BBox(Point(x, y), Point(x, y + lbl_len))
            elif pin_dir == "L":
                lbl_bbox = BBox(Point(x, y), Point(x + lbl_len, y))
            elif pin_dir == "R":
                lbl_bbox = BBox(Point(x, y), Point(x - lbl_len, y))
            part.lbl_bbox.add(lbl_bbox)

    resize_xy = Vector(0, 0)
    if part.bbox.w < 100:
        resize_xy.x = 100 - part.bbox.w
    if part.bbox.h < 100:
        resize_xy.y = 100 - part.bbox.h
    part.bbox.resize(resize_xy)
    part.lbl_bbox.resize(resize_xy)

    bbox_to_sch_bb(part.bbox, part.sch_bb)


def calc_node_bbox(node):
    """Compute the bounding box for the node in the circuit hierarchy."""

    # set the initial values to the central part maximums
    xMin = node["parts"][0].sch_bb[0] - node["parts"][0].sch_bb[2]
    xMax = node["parts"][0].sch_bb[0] + node["parts"][0].sch_bb[2]
    yMin = node["parts"][0].sch_bb[1] + node["parts"][0].sch_bb[3]
    yMax = node["parts"][0].sch_bb[1] - node["parts"][0].sch_bb[3]

    # Range through the parts in the hierarchy
    for p in node["parts"]:

        # adjust the outline for any labels that pins might have
        x_label = 0
        y_label = 0

        # Look for pins with labels or power nets attached, these will increase the length of the side
        for pin in p.pins:
            if len(pin.label) > 0:
                if pin.orientation == "U" or pin.orientation == "D":
                    if (len(pin.label) + 1) * 50 > y_label:
                        y_label = (len(pin.label) + 1) * 50
                elif pin.orientation == "L" or pin.orientation == "R":
                    if (len(pin.label) + 1) * 50 > x_label:
                        x_label = (len(pin.label) + 1) * 50
            for n in pin.nets:
                if n.netclass == "Power":
                    if pin.orientation == "U" or pin.orientation == "D":
                        if 100 > y_label:
                            y_label = 100
                    elif pin.orientation == "L" or pin.orientation == "R":
                        if 100 > x_label:
                            x_label = 100

        # Get min/max dimensions of the part
        t_xMin = p.sch_bb[0] - (p.sch_bb[2] + x_label)
        t_xMax = p.sch_bb[0] + p.sch_bb[2] + x_label
        t_yMin = p.sch_bb[1] + p.sch_bb[3] + y_label
        t_yMax = p.sch_bb[1] - (p.sch_bb[3] + y_label)

        # Check if we need to expand the rectangle
        if t_xMin < xMin:
            xMin = t_xMin
        if t_xMax > xMax:
            xMax = t_xMax
        if t_yMax < yMax:
            yMax = t_yMax
        if t_yMin > yMin:
            yMin = t_yMin

    width = int(abs(xMax - xMin) / 2) + 200
    height = int(abs(yMax - yMin) / 2) + 100

    tx = int((xMin + xMax) / 2) + 100
    ty = int((yMin + yMax) / 2) + 50
    r_sch_bb = [tx, ty, width, height]

    return r_sch_bb


def calc_move_part(moving_pin, anchor_pin, other_parts):

    moving_part = moving_pin.part
    anchor_part = anchor_pin.part
    dx = moving_pin.x + anchor_pin.x + anchor_part.sch_bb[0] + anchor_part.sch_bb[2]
    dy = -moving_pin.y + anchor_pin.y - anchor_part.sch_bb[1]
    move_part(moving_part, Vector(dx, dy), other_parts)
    # vector = Vector(anchor_pin.x, anchor_pin.y) + anchor_part.bbox.ll - Vector(moving_pin.x, moving_pin.y) - moving_part.bbox.ll
    # move_part(moving_part, vector, other_parts)


def move_part(part, vector, other_parts):
    """Move part until it doesn't collide with other parts."""

    # Setup the movement vector to use if the initial placement leads to collisions.
    avoid_vec = Vector(200, 0) if vector.x > 0 else Vector(-200, 0)

    vec = Vector(vector.x, -vector.y)  # EESCHEMA Y direction is reversed.

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

    bbox_to_sch_bb(part.bbox, part.sch_bb)
    part.moved = True
    return


def move_subhierarchy(hm, hierarchy_list, dx, dy, move_dir="L"):
    # hm = hierarchy to move
    # Move hierarchy

    hierarchy_list[hm]["sch_bb"][0] += dx
    hierarchy_list[hm]["sch_bb"][1] += dy

    hm_parent = ".".join(hm.split(".")[0:2])

    # Detect collission with other hierarchies
    for h in hierarchy_list:
        # Don't detect collisions with itself
        if h == hm:
            continue

        # Only detect collision with hierarchies on the same page
        root_parent = ".".join(h.split(".")[0:2])
        if not hm_parent == root_parent:
            continue

        # Calculate the min/max for x/y in order to detect collision between rectangles
        x1min = hierarchy_list[hm]["sch_bb"][0] - hierarchy_list[hm]["sch_bb"][2]
        x1max = hierarchy_list[hm]["sch_bb"][0] + hierarchy_list[hm]["sch_bb"][2]
        y1min = hierarchy_list[hm]["sch_bb"][1] - hierarchy_list[hm]["sch_bb"][3]
        y1max = hierarchy_list[hm]["sch_bb"][1] + hierarchy_list[hm]["sch_bb"][3]

        x2min = hierarchy_list[h]["sch_bb"][0] - hierarchy_list[h]["sch_bb"][2]
        x2max = hierarchy_list[h]["sch_bb"][0] + hierarchy_list[h]["sch_bb"][2]
        y2min = hierarchy_list[h]["sch_bb"][1] - hierarchy_list[h]["sch_bb"][3]
        y2max = hierarchy_list[h]["sch_bb"][1] + hierarchy_list[h]["sch_bb"][3]

        # Logic to tell whether parts collide
        # Note that the movement direction is opposite of what's intuitive ('R' = move left, 'U' = -50)
        # https://stackoverflow.com/questions/20925818/algorithm-to-check-if-two-boxes-overlap

        if (
            (x1min <= x2max)
            and (x2min <= x1max)
            and (y1min <= y2max)
            and (y2min <= y1max)
        ):
            if move_dir == "R":
                move_subhierarchy(hm, hierarchy_list, 200, 0, move_dir=move_dir)
            else:
                move_subhierarchy(hm, hierarchy_list, -200, 0, move_dir=move_dir)


def gen_net_wire(net, hierarchy):
    def det_net_wire_collision(parts, x1, y1, x2, y2):
        # For a particular wire see if it collides with any parts

        # order should be x1min, x1max, y1min, y1max
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        x1min = x1
        y1min = y1
        x1max = x2
        y1max = y2

        for pt in parts:
            x2min = pt.sch_bb[0] - pt.sch_bb[2]
            y2min = pt.sch_bb[1] - pt.sch_bb[3]
            x2max = pt.sch_bb[0] + pt.sch_bb[2]
            y2max = pt.sch_bb[1] + pt.sch_bb[3]

            if lineLine(x1min, y1min, x1max, y1max, x2min, y2min, x2min, y2max):
                return [pt.ref, "L"]
            elif lineLine(x1min, y1min, x1max, y1max, x2max, y2min, x2max, y2max):
                return [pt.ref, "R"]
            elif lineLine(x1min, y1min, x1max, y1max, x2min, y2min, x2max, y2min):
                return [pt.ref, "U"]
            elif lineLine(x1min, y1min, x1max, y1max, x2min, y2max, x2max, y2max):
                return [pt.ref, "D"]
        return []

    def lineLine(x1, y1, x2, y2, x3, y3, x4, y4):
        # LINE/LINE
        # https://www.jeffreythompson.org/collision-detection/line-rect.php
        # calculate the distance to intersection point
        uA = 0.0
        uB = 0.0
        try:
            uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / (
                (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
            )
            uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / (
                (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
            )
        except:
            return False

        #   // if uA and uB are between 0-1, lines are colliding
        if uA > 0 and uA < 1 and uB > 0 and uB < 1:
            # intersectionX = x1 + (uA * (x2-x1))
            # intersectionY = y1 + (uA * (y2-y1))
            # print("Collision at:  X: " + str(intersectionX) + " Y: " + str(intersectionY))
            return True
        return False

    nets_output = []
    for i in range(len(net.pins) - 1):
        if net.pins[i].routed and net.pins[i + 1].routed:
            continue
        else:
            net.pins[i].routed = True
            net.pins[i + 1].routed = True

            # Calculate the coordiantes of a straight line between the 2 pins that need to connect
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
                t_x1 = line[i][0]
                t_y1 = line[i][1]
                t_x2 = line[i + 1][0]
                t_y2 = line[i + 1][1]

                collide = det_net_wire_collision(
                    hierarchy["parts"], t_x1, t_y1, t_x2, t_y2
                )
                # if we see a collision then draw the net around the rectangle
                # since we are only going left/right with nets/rectangles the strategy to route
                # around a rectangle is basically making a 'U' shape around it
                if len(collide) > 0:
                    collided_part = Part.get(collide[0])
                    collided_side = collide[1]

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


def gen_part_eeschema(self, offset):
    # Generate eeschema code for part from SKiDL part
    # self: SKiDL part
    # c[x,y]: coordinated to place the part
    # https://en.wikibooks.org/wiki/Kicad/file_formats#Schematic_Files_Format

    time_hex = hex(int(time.time()))[2:]

    center = Point(self.sch_bb[0], self.sch_bb[1]) + offset

    out = ["$Comp\n"]
    out.append("L {}:{} {}\n".format(self.lib.filename, self.name, self.ref))
    out.append("U 1 1 {}\n".format(time_hex))
    out.append("P {} {}\n".format(str(center.x), str(center.y)))
    # Add part symbols. For now we are only adding the designator
    n_F0 = 1
    for i in range(len(self.draw)):
        if re.search("^DrawF0", str(self.draw[i])):
            n_F0 = i
            break
    out.append(
        'F 0 "{}" {} {} {} {} {} {} {}\n'.format(
            self.ref,
            self.draw[n_F0].orientation,
            str(self.draw[n_F0].x + center.x),
            str(self.draw[n_F0].y + center.y),
            self.draw[n_F0].size,
            "000",
            self.draw[n_F0].halign,
            self.draw[n_F0].valign,
        )
    )
    n_F2 = 2
    for i in range(len(self.draw)):
        if re.search("^DrawF2", str(self.draw[i])):
            n_F2 = i
            break
    out.append(
        'F 2 "{}" {} {} {} {} {} {} {}\n'.format(
            self.footprint,
            self.draw[n_F2].orientation,
            str(self.draw[n_F2].x + center.x),
            str(self.draw[n_F2].y + center.y),
            self.draw[n_F2].size,
            "001",
            self.draw[n_F2].halign,
            self.draw[n_F2].valign,
        )
    )
    out.append("   1   {} {}\n".format(str(center.x), str(center.y)))
    out.append(
        "   {}   {}  {}  {}\n".format(
            self.orientation[0],
            self.orientation[1],
            self.orientation[2],
            self.orientation[3],
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
                    x = part.sch_bb[0] + pin.x + offset.x
                    y = part.sch_bb[1] - pin.y + offset.y
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

    x = pin.x + pin.part.sch_bb[0] + offset.x
    y = -pin.y + pin.part.sch_bb[1] + offset.y

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

    x1 = node["sch_bb"][0] - node["sch_bb"][2]
    y1 = node["sch_bb"][1] + node["sch_bb"][3]
    x2 = node["sch_bb"][0] + node["sch_bb"][2]
    y2 = node["sch_bb"][1] - node["sch_bb"][3]
    bbox = BBox(Point(x1, y1), Point(x2, y2))
    bbox.move(offset)

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
            )  # Assign label if not already labeled.

        # Rotate <3 pin parts that have power nets.  Pins with power pins should face up.
        # Pins with GND pins should face down.
        rotate_power_pins(part)

        # Copy labels from one pin to each connected pin.  This allows the user to only label
        # a single pin, then connect it normally, instead of having to label every pin in that net
        propagate_pin_labels(part)

        # Generate bounding boxes around parts
        calc_bbox_part(part)

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
        offset_x = 1  # Use fine movements to get close packing on X dim.
        # TODO: magic number.
        offset_y = -(node["parts"][0].sch_bb[1] + node["parts"][0].sch_bb[3] + 500)

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
        node["sch_bb"] = calc_node_bbox(node)

    # Make the (x,y) of parts relative to the (x,y) of their encapsulating node.
    for node in circuit_hier.values():
        for part in node["parts"]:
            part.sch_bb[0] -= node["sch_bb"][0]
            part.sch_bb[1] -= node["sch_bb"][1]

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

            # Get lower Y coord of parent bounding box.
            parent_ylow = node.parent["sch_bb"][1] + node.parent["sch_bb"][3]

            # Get upper Y coord of node bounding box.
            node_yup = node["sch_bb"][1] - node["sch_bb"][3]

            # Move node so its upper Y is just below parents lower Y.
            delta_y = parent_ylow - node_yup + 200  # TODO: magic number

            # Move node so its X coord lines up with parent X coord.
            delta_x = node.parent["sch_bb"][0] - node["sch_bb"][0]

            # Move node below parent and then to the side to avoid collisions with other nodes.
            move_subhierarchy(
                node.node_key, circuit_hier, delta_x, delta_y, move_dir=dir
            )

            # Alternate placement directions for the next node placement.
            # TODO: find better algorithm than switching sides, maybe based on connections
            dir, next_dir = next_dir, dir

    # Adjust placement of parts based on the movement of their encapsulating node.
    for node in circuit_hier.values():
        for part in node["parts"]:
            part.sch_bb[0] += node["sch_bb"][0]
            part.sch_bb[1] += node["sch_bb"][1]

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

        x_min = node["sch_bb"][0] - node["sch_bb"][2]
        x_max = node["sch_bb"][0] + node["sch_bb"][2]
        y_min = node["sch_bb"][1] + node["sch_bb"][3]
        y_max = node["sch_bb"][1] - node["sch_bb"][3]
        node_bbox = BBox(Point(x_min, y_min), Point(x_max, y_max))

        root_parent = ".".join(node.node_key.split(".")[0:2])
        page_sizes[root_parent].add(node_bbox)

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
        offset = sch_start - Point(node["sch_bb"][0], node["sch_bb"][1])
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
            + "\tlayout [ size: {},{} ]\n".format(pt.sch_bb[2], pt.sch_bb[3])
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
