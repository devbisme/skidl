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
from collections import defaultdict

from future import standard_library

from .geometry import Point, BBox
from ...logger import active_logger
from ...part import Part
from ...scriptinfo import *
from ...utilities import *


standard_library.install_aliases()

"""
Generate a KiCad EESCHEMA schematic from a Circuit object.
"""
# Size options of eeschema schematic pages
eeschema_sch_sizes = {
    "A0": [46811, 33110],
    "A1": [33110, 23386],
    "A2": [23386, 16535],
    "A3": [16535, 11693],
    "A4": [11693, 8268],
}


def calc_page_size(page):
    # Calculate the schematic page size needed given xMin/Max, yMin/Max

    width = page[1] - page[0]
    height = page[3] - page[2]

    height = int(height * 1.25)
    for i in reversed(eeschema_sch_sizes):
        if width < eeschema_sch_sizes[i][0]:
            if height < eeschema_sch_sizes[i][1]:
                return i


def calc_start_point(sch_size):
    c = [0, 0]
    for n in eeschema_sch_sizes:
        if n == sch_size:
            x = int(eeschema_sch_sizes[n][0] / 2)
            # round to nearest 50 mil, DO NOT CHANGE!  otherwise parts won't play nice in eechema due to being off-grid
            x = round_num(x, 50)
            y = int(eeschema_sch_sizes[n][1] / 4)
            # round to nearest 50 mil, DO NOT CHANGE!  otherwise parts won't play nice in eechema due to being off-grid
            y = round_num(y, 50)
            c = [x, y]
            return c


def round_num(num, base):
    return base * round(num / base)


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


def gen_label(x, y, orientation, net_label, hier_label=True):
    t_orient = 0
    if orientation == "R":
        pass
    elif orientation == "D":
        t_orient = 1
    elif orientation == "L":
        t_orient = 2
    elif orientation == "U":
        t_orient = 3
    if hier_label:
        out = "\nText HLabel {} {} {}    50   UnSpc ~ 0\n{}\n".format(
            x, y, t_orient, net_label
        )
    else:
        out = "\nText GLabel {} {} {}    50   UnSpc ~ 0\n{}\n".format(
            x, y, t_orient, net_label
        )
    return out


def calc_move_part(pin_m, pin_nm, parts_list):
    # pin_m = pin of moving part
    # pin_nm = pin of non-moving part
    # parts list = hierarchical parts list

    dx = pin_m.x + pin_nm.x + pin_nm.part.sch_bb[0] + pin_nm.part.sch_bb[2]
    dy = -pin_m.y + pin_nm.y - pin_nm.part.sch_bb[1]
    p = Part.get(pin_m.part.ref)
    move_part(p, dx, dy, parts_list)


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


def gen_power_part_eeschema(part, orientation=[1, 0, 0, -1]):
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
                    x = part.sch_bb[0] + pin.x
                    y = part.sch_bb[1] - pin.y
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


def gen_hier_schematic(name, x=0, y=0, year=2021, month=8, day=15):
    time_hex = hex(int(time.time()))[2:]
    t = []
    t.append("\n$Sheet\n")
    t.append("S {} {} {} {}\n".format(x, y, 500, 1000))  # upper left x/y, width, height
    t.append("U {}\n".format(time_hex))
    t.append('F0 "{}" 50\n'.format(name))
    t.append('F1 "{}.sch" 50\n'.format(name))
    t.append("$EndSheet\n")
    out = "".join(t)
    return out


def gen_config_header(
    cur_sheet_num=1,
    total_sheet_num=1,
    title="Default",
    revMaj=0,
    revMin=1,
    year=2021,
    month=8,
    day=15,
    size="A2",
):
    # Generate a default header file

    total_sheet_num = cur_sheet_num + 1
    header = []
    header.append("EESchema Schematic File Version 4\n")
    header.append("EELAYER 30 0\n")
    header.append("EELAYER END\n")
    header.append(
        "$Descr {} {} {}\n".format(
            size, eeschema_sch_sizes[size][0], eeschema_sch_sizes[size][1]
        )
    )
    header.append("encoding utf-8\n")
    header.append("Sheet {} {}\n".format(cur_sheet_num, total_sheet_num))
    header.append('Title "{}"\n'.format(title))
    header.append('Date "{}-{}-{}"\n'.format(year, month, day))
    header.append('Rev "v{}.{}"\n'.format(revMaj, revMin))
    header.append('Comp ""\n')
    header.append('Comment1 ""\n')
    header.append('Comment2 ""\n')
    header.append('Comment3 ""\n')
    header.append('Comment4 ""\n')
    header.append("$EndDescr\n")
    return "" + "".join(header)


def gen_hierarchy_bb(hier):
    # Generate hierarchy bounding box

    # find the parts with the largest xMin, xMax, yMin, yMax

    # set the initial values to the central part maximums
    xMin = hier["parts"][0].sch_bb[0] - hier["parts"][0].sch_bb[2]
    xMax = hier["parts"][0].sch_bb[0] + hier["parts"][0].sch_bb[2]
    yMin = hier["parts"][0].sch_bb[1] + hier["parts"][0].sch_bb[3]
    yMax = hier["parts"][0].sch_bb[1] - hier["parts"][0].sch_bb[3]

    # Range through the parts in the hierarchy
    for p in hier["parts"]:

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


def calc_bbox_part(self):
    for p in self.pins:
        if self.sch_bb[2] < (abs(p.x)):
            self.sch_bb[2] = abs(p.x)
        if self.sch_bb[3] < (abs(p.y)):
            self.sch_bb[3] = abs(p.y)
    if self.sch_bb[2] < 100:
        self.sch_bb[2] = 100
    if self.sch_bb[3] < 100:
        self.sch_bb[3] = 100


def move_part(self, dx, dy, _parts_list):
    # Move the part by dx/dy, then check to see if it's colliding with
    #   any other part.  If it is colliding then move the part move towards the
    #   direction of the pin it was moving towards

    # Determine if the part moved left or right
    move_dir = "L"
    if dx > 0:
        move_dir = "R"

    # Round dx/dy to nearest 50
    dx = int((50 * round(dx / 50)))
    dy = int((50 * round(dy / 50)))
    # Move the part
    self.sch_bb[0] += dx
    self.sch_bb[1] -= dy

    # Check to see if we're colliding with any other parts

    # First we need to check for a label on each pin.
    # If we find one then add that label's length to the collision detection
    x_label_p = 0
    x_label_m = 0
    y_label_p = 0
    y_label_m = 0
    for pin in self.pins:
        if len(pin.label) > 0:
            if pin.orientation == "U":
                if (len(pin.label) + 1) * 50 > y_label_m:
                    y_label_m = (len(pin.label) + 1) * 50
            elif pin.orientation == "D":
                if (len(pin.label) + 1) * 50 > y_label_p:
                    y_label_p = (len(pin.label) + 1) * 50
            elif pin.orientation == "L":
                if (len(pin.label) + 1) * 50 > x_label_p:
                    x_label_p = (len(pin.label) + 1) * 50
            elif pin.orientation == "R":
                if (len(pin.label) + 1) * 50 > x_label_m:
                    x_label_m = (len(pin.label) + 1) * 50

    # Range through parts in the subcircuit and look for overlaps
    # If we are overlapping then nudge the part 50mil left/right and rerun this function
    for pt in _parts_list:
        # Don't detect collisions with itself
        if pt.ref == self.ref:
            continue

        # Determine if there's a label on a pin and count that label length for detecting collisions
        pt_x_label_p = 0
        pt_x_label_m = 0
        pt_y_label_p = 0
        pt_y_label_m = 0
        for pin in pt.pins:
            if len(pin.label) > 0:
                if pin.orientation == "U":
                    if (len(pin.label) + 1) * 50 > pt_y_label_m:
                        pt_y_label_m = (len(pin.label) + 1) * 50
                elif pin.orientation == "D":
                    if (len(pin.label) + 1) * 50 > pt_y_label_p:
                        pt_y_label_p = (len(pin.label) + 1) * 50
                elif pin.orientation == "L":
                    if (len(pin.label) + 1) * 50 > pt_x_label_p:
                        pt_x_label_p = (len(pin.label) + 1) * 50
                elif pin.orientation == "R":
                    if (len(pin.label) + 1) * 50 > pt_x_label_m:
                        pt_x_label_m = (len(pin.label) + 1) * 50

        # Calculate the min/max for x/y in order to detect collision between rectangles

        x1min = self.sch_bb[0] - self.sch_bb[2] - x_label_m
        x1max = self.sch_bb[0] + self.sch_bb[2] + x_label_p
        y1min = self.sch_bb[1] - self.sch_bb[3] - y_label_m
        y1max = self.sch_bb[1] + self.sch_bb[3] + y_label_p
        x2min = pt.sch_bb[0] - pt.sch_bb[2] - pt_x_label_m
        x2max = pt.sch_bb[0] + pt.sch_bb[2] + pt_x_label_p
        y2min = pt.sch_bb[1] - pt.sch_bb[3] - pt_y_label_m
        y2max = pt.sch_bb[1] + pt.sch_bb[3] + pt_y_label_p

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
                move_part(self, 200, 0, _parts_list)
            else:
                move_part(self, -200, 0, _parts_list)


def gen_part_eeschema(self):
    # Generate eeschema code for part from SKiDL part
    # self: SKiDL part
    # c[x,y]: coordinated to place the part
    # https://en.wikibooks.org/wiki/Kicad/file_formats#Schematic_Files_Format

    time_hex = hex(int(time.time()))[2:]

    out = ["$Comp\n"]
    out.append("L {}:{} {}\n".format(self.lib.filename, self.name, self.ref))
    out.append("U 1 1 {}\n".format(time_hex))
    out.append("P {} {}\n".format(str(self.sch_bb[0]), str(self.sch_bb[1])))
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
            str(self.draw[n_F0].x + self.sch_bb[0]),
            str(self.draw[n_F0].y + self.sch_bb[1]),
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
            str(self.draw[n_F2].x + self.sch_bb[0]),
            str(self.draw[n_F2].y + self.sch_bb[1]),
            self.draw[n_F2].size,
            "001",
            self.draw[n_F2].halign,
            self.draw[n_F2].valign,
        )
    )
    out.append("   1   {} {}\n".format(str(self.sch_bb[0]), str(self.sch_bb[1])))
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


def gen_schematic(self, file_=None, _title="Default", sch_size="A0", gen_elkjs=False):
    """
    Create a schematic file. THIS KINDA WORKS!

    1. Sort parts by hierarchy
    2. Rotate parts (<=3 pins) with power nets
    3. Copy labels to connected pins
    4. Create part bounding boxes for parts
    5. For each hierarchy: Move parts with nets drawn to central part
    6. For each hierarchy: Move parts with nets drawn to parts moved in step #5
    7. For each hierarchy: Move remaining parts
    8. Create bounding boxes for hierarchies
    8.1 Adjust the parts to be centered on the hierarchy center
    9. Sort the hierarchies by nesting length
    10. Range through each level of hierarchies and place hierarchies under parents
    12. Adjust part placement for hierachy and starting coordinates
    13. Calculate nets for each hierarchy
    14. Generate eeschema code for each hierarchy
    15. Generate elkjs code
    16. Create schematic file

    """

    # Pre-process parts
    for part in self.parts:

        # Initialize part attributes used for generating schematics.
        part.orientation = [1, 0, 0, -1]
        part.sch_bb = [0, 0, 0, 0]  # Set schematic location to x, y, width, height.

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

    # Dictionary that will hold parts and nets info for each hierarchy
    circuit_hier = defaultdict(lambda: {"parts": [], "wires": [], "sch_bb": []})
    for part in self.parts:
        circuit_hier[part.hierarchy]["parts"].append(part)

    # For each node in hierarchy: Move parts connected to central part with unlabeled nets.
    for node in circuit_hier.values():

        # Center part of hierarchy that everything else is placed around.
        anchor_part = node["parts"][0]  # TODO: Smarter selection of center part.

        # Go thru the center part's pins, moving any connected parts closer.
        for anchor_pin in anchor_part:

            # Skip unconnected pins.
            if not anchor_pin.is_connected():
                continue

            # Don't move parts connected to labeled (stub) pins.
            if len(anchor_pin.label) > 0:
                continue

            # Don't move parts connected thru power supply nets.
            if anchor_pin.net.netclass == "Power":
                continue

            # Now move any parts connected to this pin.
            for move_pin in anchor_pin.net.pins:

                # Skip moving the center part.
                if move_pin.part == anchor_part:
                    continue

                # Skip parts that aren't in the same node of the hierarchy as the center part.
                if move_pin.part.hierarchy != anchor_part.hierarchy:
                    continue

                # OK, finally move the part connected to this pin.
                calc_move_part(move_pin, anchor_pin, node["parts"])

    # For each node in hierarchy: Move parts connected to parts moved in step previous step.
    for node in circuit_hier.values():

        # Get the center part for this node from the last phase.
        center_part = node["parts"][0]

        for mv_part in node["parts"]:

            # Skip center part.
            if mv_part is center_part:
                continue

            # Skip a part that's already been moved.
            if mv_part.sch_bb[0] != 0 or mv_part.sch_bb[1] != 0:
                continue

            # Find a pin to pin connection where the part needs to be moved.
            for move_pin in mv_part:

                # Skip unconnected pins.
                if not move_pin.is_connected():
                    continue

                # Don't move parts connected to labeled (stub) pins.
                if len(move_pin.label) > 0:
                    continue

                # Don't move parts connected thru power supply nets.
                if move_pin.net.netclass == "Power":
                    continue

                # Move this part toward parts connected to its pin.
                for anchor_pin in move_pin.net.pins:

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
                    calc_move_part(move_pin, anchor_pin, node["parts"])

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
            if part.sch_bb[0] == 0 and part.sch_bb[1] == 0:
                move_part(part, offset_x, offset_y, node["parts"])

                # Switch movement direction for the next unmoved part.
                offset_x = -offset_x

    # Create bounding boxes for each node of the hierarchy.
    for node in circuit_hier.values():
        node["sch_bb"] = gen_hierarchy_bb(node)

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
        for h, node in circuit_hier.items():

            # Skip nodes not at the current depth.
            if h.count(".") != depth:
                continue

            # Find node parent by lopping off last section of hierarchy label.
            parent_label = ".".join(h.split(".")[:-1])
            parent = circuit_hier[parent_label]

            # Get lower Y coord of parent bounding box.
            parent_ylow = parent["sch_bb"][1] + parent["sch_bb"][3]

            # Get upper Y coord of node bounding box.
            node_yup = node["sch_bb"][1] - node["sch_bb"][3]
            
            # Move node so its upper Y is just below parents lower Y.
            delta_y = parent_ylow - node_yup + 200 # TODO: magic number

            # Move node so its X coord lines up with parent X coord.
            delta_x = parent["sch_bb"][0] - node["sch_bb"][0]

            # Move node below parent and then to the side to avoid collisions with other nodes.
            move_subhierarchy(h, circuit_hier, delta_x, delta_y, move_dir=dir)

            # Alternate placement directions for the next node placement.
            # TODO: find better algorithm than switching sides, maybe based on connections
            dir, next_dir = next_dir, dir

    # Adjust placement of parts based on the movement of their encapsulating node.
    for node in circuit_hier.values():
        for part in node["parts"]:
            part.sch_bb[0] += node["sch_bb"][0]
            part.sch_bb[1] += node["sch_bb"][1]

    # Collect the nets for each node.
    for h in circuit_hier:
        for pt in circuit_hier[h]["parts"]:
            for pin in pt.pins:
                if len(pin.label) > 0:
                    continue
                if pin.net is not None:
                    if pin.net.netclass == "Power":
                        continue
                    sameHier = True
                    for p in pin.net.pins:
                        if len(p.label) > 0:
                            continue
                        if p.part.hierarchy != pin.part.hierarchy:
                            sameHier = False
                    if sameHier:
                        wire_lst = gen_net_wire(pin.net, circuit_hier[h])
                        circuit_hier[h]["wires"].extend(wire_lst)

    # At this point the hierarchy should be completely generated and ready for generating code

    # Calculate the maximum page dimensions needed for each root hierarchy sheet
    hier_pg_dim = {}
    for h in circuit_hier:
        # root_parent = h.split(".")[0]
        root_parent = ".".join(h.split(".")[0:2])
        xMin = circuit_hier[h]["sch_bb"][0] - circuit_hier[h]["sch_bb"][2]
        xMax = circuit_hier[h]["sch_bb"][0] + circuit_hier[h]["sch_bb"][2]
        yMin = circuit_hier[h]["sch_bb"][1] + circuit_hier[h]["sch_bb"][3]
        yMax = circuit_hier[h]["sch_bb"][1] - circuit_hier[h]["sch_bb"][3]
        if root_parent not in hier_pg_dim:
            hier_pg_dim[root_parent] = [xMin, xMax, yMin, yMax]
        else:
            if xMin < hier_pg_dim[root_parent][0]:
                hier_pg_dim[root_parent][0] = xMin
            if xMax > hier_pg_dim[root_parent][1]:
                hier_pg_dim[root_parent][1] = xMax
            if yMin < hier_pg_dim[root_parent][2]:
                hier_pg_dim[root_parent][2] = yMin
            if yMax > hier_pg_dim[root_parent][3]:
                hier_pg_dim[root_parent][3] = yMax

    # 14. Generate eeschema code for each hierarchy
    hier_pg_eeschema_code = {}
    for h in circuit_hier:
        eeschema_code = []  # List to hold all the code for the hierarchy

        # Find starting point for part placement
        root_parent = ".".join(h.split(".")[0:2])
        pg_size = calc_page_size(hier_pg_dim[root_parent])
        sch_start = calc_start_point(pg_size)

        # a. Generate part code
        for pt in circuit_hier[h]["parts"]:
            t_pt = pt
            t_pt.sch_bb[0] += sch_start[0]
            t_pt.sch_bb[1] += sch_start[1]
            part_code = gen_part_eeschema(t_pt)
            eeschema_code.append(part_code)

        # b. net wire code
        for w in circuit_hier[h]["wires"]:
            t_wire = []
            for i in range(len(w) - 1):
                t_x1 = w[i][0] - circuit_hier[h]["sch_bb"][0] + sch_start[0]
                t_y1 = w[i][1] - circuit_hier[h]["sch_bb"][1] + sch_start[1]
                t_x2 = w[i + 1][0] - circuit_hier[h]["sch_bb"][0] + sch_start[0]
                t_y2 = w[i + 1][1] - circuit_hier[h]["sch_bb"][1] + sch_start[1]
                t_wire.append("Wire Wire Line\n")
                t_wire.append("	{} {} {} {}\n".format(t_x1, t_y1, t_x2, t_y2))
                t_out = "\n" + "".join(t_wire)
                eeschema_code.append(t_out)

        # c. power net stubs
        for pt in circuit_hier[h]["parts"]:
            stub = gen_power_part_eeschema(pt)
            if len(stub) > 0:
                eeschema_code.append(stub)

        # d. labels
        for pt in circuit_hier[h]["parts"]:
            for pin in pt.pins:
                if len(pin.label) > 0:
                    t_x = pin.x + pin.part.sch_bb[0]
                    t_y = 0
                    t_y = -pin.y + pin.part.sch_bb[1]
                    # TODO: make labels global if the label connects to a different root hierarchy
                    # eeschema_code.append(gen_label(t_x, t_y, pin.orientation, pin.label))
                    if hasattr(pin, "net"):
                        if hasattr(pin.net, "pins"):
                            for p in pin.net.pins:
                                if p.ref == pt:
                                    continue
                                # check if the pins are in the same root hierarchy
                                pt_root_parent = pt.hierarchy.split(".")[0]
                                p_root_parent = p.part.hierarchy.split(".")[0]
                                if not pt_root_parent in p_root_parent:
                                    print(
                                        "global label, pt: "
                                        + pt
                                        + "  other part: "
                                        + p.part.ref
                                    )
                                    eeschema_code.append(
                                        gen_label(
                                            t_x,
                                            t_y,
                                            pin.orientation,
                                            pin.label,
                                            hier_label=False,
                                        )
                                    )
                                else:
                                    eeschema_code.append(
                                        gen_label(
                                            t_x,
                                            t_y,
                                            pin.orientation,
                                            pin.label,
                                            hier_label=True,
                                        )
                                    )
                            continue
                    eeschema_code.append(
                        gen_label(t_x, t_y, pin.orientation, pin.label, hier_label=True)
                    )

        # e. hierarchy bounding box
        box = []
        xMin = (
            circuit_hier[h]["sch_bb"][0] - circuit_hier[h]["sch_bb"][2] + sch_start[0]
        )
        xMax = (
            circuit_hier[h]["sch_bb"][0] + circuit_hier[h]["sch_bb"][2] + sch_start[0]
        )
        yMin = (
            circuit_hier[h]["sch_bb"][1] + circuit_hier[h]["sch_bb"][3] + sch_start[1]
        )
        yMax = (
            circuit_hier[h]["sch_bb"][1] - circuit_hier[h]["sch_bb"][3] + sch_start[1]
        )

        label_x = xMin
        label_y = yMax
        subhierarchies = h.split(".")
        if len(subhierarchies) > 1:
            hierName = "".join(subhierarchies[1:])
        else:
            hierName = h

        # Make the strings for the box and label
        box.append(
            "Text Notes {} {} 0    100  ~ 20\n{}\n".format(label_x, label_y, hierName)
        )
        box.append("Wire Notes Line\n")
        box.append("	{} {} {} {}\n".format(xMin, yMax, xMin, yMin))  # left
        box.append("Wire Notes Line\n")
        box.append("	{} {} {} {}\n".format(xMin, yMin, xMax, yMin))  # bottom
        box.append("Wire Notes Line\n")
        box.append("	{} {} {} {}\n".format(xMax, yMin, xMax, yMax))  # right
        box.append("Wire Notes Line\n")
        box.append("	{} {} {} {}\n".format(xMax, yMax, xMin, yMax))  # top
        out = "\n" + "".join(box)
        eeschema_code.append(out)

        root_parent = ".".join(h.split(".")[0:2])
        # Append the eeschema code for this hierarchy to the appropriate page
        if root_parent not in hier_pg_eeschema_code:
            # make new top level hierarchy
            hier_pg_eeschema_code[root_parent] = ["\n".join(eeschema_code)]

        else:
            hier_pg_eeschema_code[root_parent].append("\n".join(eeschema_code))

    # 15. Generate elkjs code
    if gen_elkjs:
        gen_elkjs_code(self.parts, self.nets)

    # 16. Create schematic file
    if not self.no_files:

        # Generate schematic pages for lower-levels in the hierarchy.
        for hp in hier_pg_eeschema_code:
            pg_size = calc_page_size(hier_pg_dim[hp])
            u = file_.split("/")[:-1]
            dir = "/".join(u)
            file_name = dir + "/" + hp + ".sch"
            with open(file_name, "w") as f:
                f.truncate(0)  # Clear the file
                new_sch_file = [
                    gen_config_header(cur_sheet_num=1, size=pg_size, title=_title),
                    hier_pg_eeschema_code[hp],
                    "$EndSCHEMATC",
                ]
                for i in new_sch_file:
                    print("" + "".join(i), file=f)

        # Generate root schematic with hierarchical schematics
        hier_sch = []
        root_start = calc_start_point("A4")
        root_start[0] = 1000
        for hp in hier_pg_eeschema_code:
            t = gen_hier_schematic(hp, root_start[0], root_start[1])
            hier_sch.append(t)
            root_start[0] += 1000

        with open(file_, "w") as f:
            f.truncate(0)  # Clear the file
            new_sch_file = [
                gen_config_header(cur_sheet_num=1, size="A4", title=_title),
                hier_sch,
                "$EndSCHEMATC",
            ]
            for i in new_sch_file:
                print("" + "".join(i), file=f)
