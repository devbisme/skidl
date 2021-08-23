# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2018 by XESS Corp.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Handles complete circuits made of parts and nets.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import functools
from inspect import currentframe
import json
import math
import os.path
import re
import subprocess
import time
from builtins import range, str, super
from collections import defaultdict, deque, OrderedDict

import graphviz
from future import standard_library

# from .arrange import Arranger
from .bus import Bus
from .common import *
from .defines import *
from .erc import dflt_circuit_erc
from .interface import Interface
from .logger import erc_logger, logger
from .net import NCNet, Net
from .part import Part, PartUnit
from .pckg_info import __version__
from .pin import Pin
from .protonet import ProtoNet
from .schlib import SchLib
from .scriptinfo import *
from .skidlbaseobj import SkidlBaseObject
from .utilities import *
from .tools import *


standard_library.install_aliases()

rotation_matrix = [
                    [1,0,0,-1],  # 0   deg (standard orientation, ie x: -700 y: 1200 >> -700 left, -1200 down
                    [0,1,1,0],   # 90  deg x: 1200  y: -700
                    [-1,0,0,1],  # 180 deg x:  700  y: 1600
                    [0,-1,-1,0]  # 270 deg x:-1600  y:  700
]

# pin_m = pin of moving part
# pin_nm = pin of non-moving part
# parts list = hierarchical parts list
def calc_move_part(pin_m, pin_nm, parts_list):
    # For placing parts around central part we have special logic
    #   * Push parts further out 
    if pin_nm.ref in parts_list[0].ref:
        # check if the moving part is a 2 pin passive that needs to be rotated to GND or POWER
        if len(pin_m.part.pins) <= 2:
            print(pin_m.part.ref + " is a 2 pin part")
            power_conn = False
            
            for p in pin_m.part.pins:
                rotate = 0
                if 'gnd' in p.net.name.lower():
                    power_conn = True
                    # print("part: " + p.part.ref + " pin: " + str(p.num) + " is connected to ground, facing " + p.orientation)
                    if p.orientation == 'U':
                        break # pin is facing down, break
                    if p.orientation == 'D':
                        rotate = 180
                    if p.orientation == 'L':
                        rotate = 90
                    if p.orientation == 'R':
                        rotate = -90
                elif p.nets[0].name == '+5V' or p.nets[0].name == '+3V3' or p.nets[0].name == 'GND':
                    power_conn = True
                    # print("part: " + p.part.ref + " pin: " + str(p.num) + " is connected to " + p.net.name +  ", facing " + p.orientation)
                    if p.orientation == 'D':
                        break # pin is facing down, break
                    if p.orientation == 'U':
                        rotate = 180
                    if p.orientation == 'L':
                        rotate = 90
                    if p.orientation == 'R':
                        rotate = -90
                if rotate != 0:
                    _part = Part.get(pin_m.part.ref)
                    rotate_part_90_cw(_part)
                    rotate_part_90_cw(_part)
                    print("we need to rotate by " + str(rotate))
                #    # for now we'll just assume they are in the starting orientation of 100-1
                #     if rotate == 90:
                        
                #         _part.orientation = [0,1,1,0]
                #         x = _part.sch_bb[0]
                #         y = _part.sch_bb[1]
                #         width = _part.sch_bb[2]
                #         height = _part.sch_bb[3]

                #         _part.sch_bb[0] = y
                #         _part.sch_bb[1] = x
                #         _part.sch_bb[2] = height
                #         _part.sch_bb[3] = width

                #         # TODO change the pins location as well
                #     elif rotate == 180:
                #         print("rotating by 180")
                #         _part.orientation = [-1,0,0,1]
                #         x = _part.sch_bb[0]
                #         y = _part.sch_bb[1]
                #         width = _part.sch_bb[2]
                #         height = _part.sch_bb[3]

                #         _part.sch_bb[0] = -x
                #         _part.sch_bb[1] = y
                #         _part.sch_bb[2] = height
                #         _part.sch_bb[3] = width
            # if not power_conn:
            #     print("Part not connected to power net")
        # dx = pin_nm.x + pin_nm.part.sch_bb[0] # pointless, should always be 0,0 here
        dx = pin_nm.x # we move at least the x distance of central part's pin
        # if we are moving right then add on the moving part's pin's x coordinates and a buffer (400 for now)
        # if we're moving left then subtract this same value
        if pin_nm.x >= 0:
            dx += (abs(pin_m.x) + 400)
        else:
            dx -= (abs(pin_m.x) + 400)
        dy = -pin_m.y + pin_nm.y + pin_nm.part.sch_bb[1]
        p = Part.get(pin_m.part.ref)
        # print("Moving part: " + p.ref + " by  x: " + str(dx) + "  y: " + str(dy))
        p.move_part(dx, dy,parts_list)
    else:
        dx = pin_m.x + pin_nm.x + pin_nm.part.sch_bb[0]
        dy = -pin_m.y + pin_nm.y - pin_nm.part.sch_bb[1] 
        p = Part.get(pin_m.part.ref)
        # print("Moving part: " + p.ref + " by  x: " + str(dx) + "  y: " + str(dy))
        p.move_part(dx, dy,parts_list)

# Rotating the part CW 90 switches the x/y axis and makes the new height negative
# https://stackoverflow.com/questions/2285936/easiest-way-to-rotate-a-rectangle
def rotate_part_90_cw(part):
    # new_height = -part.sch_bb[2]
    # new_width = part.sch_bb[3]
    # part.sch_bb[2] = new_width
    # part.sch_bb[3] = new_height


    for p in part.pins:
        new_y = -p.x
        new_x = p.y
        p.x = new_x
        p.y = new_y
        if p.orientation == 'D':
            p.orientation = 'L'
        elif p.orientation == 'U':
            p.orientation = 'R'
        elif p.orientation == 'R':
            p.orientation = 'D'
        elif p.orientation == 'L':
            p.orientation = 'U'

        print("PIN" + str(p.num) + "  x: " + str(p.x) + " pin y: " + str(p.y))
        new_x = p.x + part.sch_bb[2]
        new_y = p.y + part.sch_bb[3]
        print("new x: " + str(new_x) + " y: " + str(new_y))

def gen_power_part_eeschema(part, stub_name, c=[0,0], orientation = [1,0,0,-1]):

    for pin in part.pins:
        try:
            if not (pin.net is None):
                if pin.net.name == stub_name:
                    # find the stub in the part
                    time_hex = hex(int(time.time()))[2:]
                    x = c[0] + part.sch_bb[0] + pin.x
                    y = c[1] + part.sch_bb[1] - pin.y
                    out=["$Comp\n"]
                    out.append("L power:{} #PWR?\n".format(stub_name))
                    out.append("U 1 1 {}\n".format(time_hex))    
                    out.append("P {} {}\n".format(str(x), str(y)))
                    # Add part symbols. For now we are only adding the designator
                    n_F0 = 1
                    for i in range(len(part.draw)):
                        if re.search("^DrawF0", str(part.draw[i])):
                            n_F0 = i
                            break
                    out.append('F 0 "{}" {} {} {} {} {} {} {}\n'.format(
                                                    stub_name,
                                                    part.draw[n_F0].orientation,
                                                    str(x + 25),
                                                    str(y + 25),
                                                    str(40),
                                                    "000",
                                                    part.draw[n_F0].halign,
                                                    part.draw[n_F0].valign
                    ))
                    out.append("   1   {} {}\n".format(str(x), str(y)))
                    out.append("   {}   {}  {}  {}\n".format(orientation[0], orientation[1], orientation[2], orientation[3]))
                    out.append("$EndComp\n") 
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
    return ("\n" + "".join(out))


# Generate a default header file
def gen_config_header(cur_sheet_num=1, total_sheet_num=1, sheet_title="Default", revMaj=0, revMin=1, year=2021, month=8, day=15):
    total_sheet_num = cur_sheet_num + 1
    header = []
    header.append("EESchema Schematic File Version 4\n")
    header.append("EELAYER 30 0\n")
    header.append("EELAYER END\n")
    header.append("$Descr A1 33110 23386\n")
    header.append("encoding utf-8\n")
    header.append("Sheet {} {}\n".format(cur_sheet_num, total_sheet_num)) 
    header.append('Title "{}"\n'.format(sheet_title)) 
    header.append('Date "{}-{}-{}"\n'.format(year, month, day)) 
    header.append('Rev "v{}.{}"\n'.format(revMaj, revMin)) 
    header.append('Comp ""\n')
    header.append('Comment1 ""\n')
    header.append('Comment2 ""\n')
    header.append('Comment3 ""\n')
    header.append('Comment4 ""\n')
    header.append('$EndDescr\n')
    return (("" + "".join(header)))


# Draw a rectangle around a hierarchy and add a label
def draw_rect_hierarchies(hier, sch_center):
    # find the part with the largest x1,x1,y1,y2
    xMin = hier['parts'][0].sch_bb[0] - hier['parts'][0].sch_bb[2]
    xMax = hier['parts'][0].sch_bb[0] + hier['parts'][0].sch_bb[2]
    yMin = hier['parts'][0].sch_bb[1] + hier['parts'][0].sch_bb[3]
    yMax = hier['parts'][0].sch_bb[1] - hier['parts'][0].sch_bb[3]
    for p in hier['parts']:
        # Get min/max dimensions of the part
        t_xMin = p.sch_bb[0] - p.sch_bb[2]
        t_xMax = p.sch_bb[0] + p.sch_bb[2]
        t_yMin = p.sch_bb[1] + p.sch_bb[3]
        t_yMax = p.sch_bb[1] - p.sch_bb[3]
        # Check if we need to expand the rectangle
        if t_xMin < xMin:
            xMin = t_xMin
        if t_xMax > xMax:
            xMax = t_xMax
        if t_yMax < yMax:
            yMax = t_yMax
        if t_yMin > yMin:
            yMin = t_yMin

    # expand the box a bit so it looks nice
    xMin += sch_center[0] - 500
    xMax += sch_center[0] + 500
    yMin += sch_center[1] + 500
    yMax += sch_center[1] - 700 # Make box a bit bigger on top to make room for a label

    box = []

    # Place label starting at 1/4 x-axis distance and 200mil down
    label_x = int((xMax - xMin)/4) + xMin
    label_y = yMax + 200
    # Make the strings for the box and label
    box.append("Text Notes {} {} 0    100  ~ 20\n{}\n".format(label_x, label_y, hier['parts'][0].hierarchy[4:]))
    box.append("Wire Notes Line\n")
    box.append("	{} {} {} {}\n".format(xMin, yMax, xMin, yMin)) # left 
    box.append("Wire Notes Line\n")
    box.append("	{} {} {} {}\n".format(xMin, yMin, xMax, yMin)) # bottom 
    box.append("Wire Notes Line\n")
    box.append("	{} {} {} {}\n".format(xMax, yMin, xMax, yMax)) # right
    box.append("Wire Notes Line\n")
    box.append("	{} {} {} {}\n".format(xMax, yMax, xMin, yMax)) # top
    return (("\n" + "".join(box)))

# Generate a hierarchical schematic
def gen_hier_sheet(title, x_start, y_start, width=1000, height=2000):
    # make the file if it doesn't exist
    file_path = "stm32/"+title+".sch"
    if not os.path.isfile(file_path):
        f = open(file_path, "a")
        new_sch_file = [gen_config_header(sheet_title=title), "$EndSCHEMATC"]
        f.truncate(0) # Clear the file
        for i in new_sch_file:
            print("" + "".join(i), file=f)
        f.close()

    sheet = []
    sheet.append("$Sheet\n")
    sheet.append('S {} {} {} {}\n'.format(x_start, y_start, width, height)) 
    time_hex = hex(int(time.time()))[2:]
    sheet.append('U {}\n'.format(time_hex))
    sheet.append('F0 "{}" 100\n'.format(title))
    sheet.append('F1 "{}.sch" 100\n'.format(title))
    sheet.append('$EndSheet\n')

    return (("" + "".join(sheet)))


# # https://www.jeffreythompson.org/collision-detection/line-rect.php
# # For a particular wire see if it collides with any parts
# def det_net_wire_collision(parts, wire,c):

#     # check if we collide with a part
#     t = wire.split("\n")
#     u = t[2].split() # x1 y1 x2 y2
#     v = map(int, u)
#     w = list(v)
#     # order should be x1min, x1max, y1min, y1max
#     if w[0] > w[2]:
#         t = w[0]
#         w[0] = w[2]
#         w[2] = t
#     if w[1] > w[3]:
#         t = w[1]
#         w[1] = w[3]
#         w[3] = t
#     x1min = w[0]
#     y1min = w[1]
#     x1max = w[2]
#     y1max = w[3]
#     collided_parts = []
#     for pt in parts:
#         x2min = pt.sch_bb[0] - pt.sch_bb[2] + c[0]
#         y2min = pt.sch_bb[1] - pt.sch_bb[3] + c[1]
#         x2max = pt.sch_bb[0] + pt.sch_bb[2] + c[0]
#         y2max = pt.sch_bb[1] + pt.sch_bb[3] + c[1]
        
#         if lineLine(x1min,y1min,x1max,y1max, x2min,y2min,x2min, y2max):
#             # print(pt.ref + " collision left")
#             collided_parts.append(pt.ref)
#         elif lineLine(x1min,y1min,x1max,y1max, x2max,y2min, x2max,y2max):
#             # print(pt.ref + " collision right")
#             collided_parts.append(pt.ref)
#         elif lineLine(x1min,y1min,x1max,y1max, x2min,y2min, x2max,y2min):
#             # print(pt.ref + " collision top")
#             collided_parts.append(pt.ref)
#         elif lineLine(x1min,y1min,x1max,y1max, x2min,y2max, x2max,y2max):
#             # print(pt.ref + " collision bottom")
#             collided_parts.append(pt.ref)
#     return collided_parts



# #LINE/LINE
# # https://www.jeffreythompson.org/collision-detection/line-rect.php
# def lineLine( x1,  y1,  x2,  y2,  x3,  y3,  x4,  y4):
#   # calculate the distance to intersection point
#     uA = 0.0
#     uB = 0.0
#     try:
#         uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
#         uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
#     except:
#         return False

#     #   // if uA and uB are between 0-1, lines are colliding
#     if (uA > 0 and uA < 1 and uB > 0 and uB < 1):
#         return True
#     return False

def gen_net_wire(n, parts, c):

# https://www.jeffreythompson.org/collision-detection/line-rect.php
# For a particular wire see if it collides with any parts
    def det_net_wire_collision(parts, x1,y1,x2,y2):

        # order should be x1min, x1max, y1min, y1max
        if x1 > x2:
            t = x1
            x1 = x2
            x2 = t
        if y1 > y2:
            t = y1
            y1 = y2
            y2 = t
        x1min = x1
        y1min = y1
        x1max = x2
        y1max = y2

        for pt in parts:
            x2min = pt.sch_bb[0] - pt.sch_bb[2]
            y2min = pt.sch_bb[1] - pt.sch_bb[3]
            x2max = pt.sch_bb[0] + pt.sch_bb[2]
            y2max = pt.sch_bb[1] + pt.sch_bb[3]
            
            if lineLine(x1min,y1min,x1max,y1max, x2min,y2min,x2min, y2max):
                return [pt.ref, "L"]
            elif lineLine(x1min,y1min,x1max,y1max, x2max,y2min, x2max,y2max):
                return [pt.ref, "R"]
            elif lineLine(x1min,y1min,x1max,y1max, x2min,y2min, x2max,y2min):
               return [pt.ref, "U"]
            elif lineLine(x1min,y1min,x1max,y1max, x2min,y2max, x2max,y2max):
                return [pt.ref, "D"]
        return []

    #LINE/LINE
    # https://www.jeffreythompson.org/collision-detection/line-rect.php
    def lineLine( x1,  y1,  x2,  y2,  x3,  y3,  x4,  y4):
    # calculate the distance to intersection point
        uA = 0.0
        uB = 0.0
        try:
            uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
            uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
        except:
            return False

        #   // if uA and uB are between 0-1, lines are colliding
        if (uA > 0 and uA < 1 and uB > 0 and uB < 1):
            intersectionX = x1 + (uA * (x2-x1))
            intersectionY = y1 + (uA * (y2-y1))
            print("Collision at:  X: " + str(intersectionX) + " Y: " + str(intersectionY))
            return True
        return False



    # Caluclate the coordiantes of a straight line between the 2 pins that need to connect
    x1 = n.pins[0].part.sch_bb[0] + n.pins[0].x
    y1 = n.pins[0].part.sch_bb[1] - n.pins[0].y

    x2 = n.pins[1].part.sch_bb[0] + n.pins[1].x
    y2 = n.pins[1].part.sch_bb[1] - n.pins[1].y

    line = [[x1,y1], [x2,y2]]


    # Check if the line is orthogonal by checking if we are horizontally or vertically aligned
    if not(x1 == x2) and not(y1==y2):
        # if the line is not orthogonal then insert a point to make it orthogonal
        #  y's must be equal
        x_t = x1
        y_t = y2
        line.insert(1,[x_t,y_t])

    # check each line segment for a collision
    for i in range(len(line)-1):
        t_x1 = line[i][0]
        t_y1 = line[i][1]
        t_x2 = line[i+1][0]
        t_y2 = line[i+1][1]

        collide = det_net_wire_collision(parts, t_x1,t_y1,t_x2,t_y2)
        # if we see a collision then draw the net around the rectangle
        # since we are only going left/right with nets/rectangles the strategy to route
        # around a rectangle is basically making a 'U' shape around it
        if len(collide)>0:
            collided_part = Part.get(collide[0])
            collided_side = collide[1]
            
            if collided_side == "L":
                # if we collided on the left 
                if n.pins[1].part.sch_bb[0]<0 or n.pins[0].part.sch_bb[0]<0:
                    # switch first and last coordinates if one is further left
                    if x1 > x2:
                        t = line[0]
                        line[0] = line[-1]
                        line[-1] = t

                    # draw line down
                    d_x1 = collided_part.sch_bb[0] - collided_part.sch_bb[2] - 100
                    d_y1 = t_y1
                    d_x2 = d_x1
                    d_y2 = collided_part.sch_bb[1] + collided_part.sch_bb[3] + 200
                    # d_x3 = d_x2 + collided_part.sch_bb[2] + 100 + 100
                    d_y3 = d_y2
                    line.insert(i+1, [d_x1,d_y1])
                    line.insert(i+2, [d_x2, d_y2])
                    line.insert(i+3, [x1, d_y3])

                else:
                    print("right side of U1")
                        # switch first and last coordinates if one is further left
                    if x1 < x2:
                        t = line[0]
                        line[0] = line[-1]
                        line[-1] = t
                    # draw line down
                    d_x1 = collided_part.sch_bb[0] + collided_part.sch_bb[2] + 100
                    d_y1 = t_y1
                    d_x2 = d_x1
                    d_y2 = collided_part.sch_bb[1] + collided_part.sch_bb[3] + 200
                    # d_x3 = d_x2 + collided_part.sch_bb[2] + 100 + 100
                    d_y3 = d_y2
                    line.insert(i+1, [d_x1,d_y1])
                    line.insert(i+2, [d_x2, d_y2])
                    line.insert(i+3, [x2, d_y3])
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
                line.insert(i+1, [d_x1,d_y1])
                line.insert(i+2, [d_x2, d_y2])
                line.insert(i+3, [x1, d_y3])
                break


    t_wire = []
    # TODO add the center coordinates
    for i in range(len(line)-1):
        # print(line[i])
        t_x1 = line[i][0] + c[0]
        t_y1 = line[i][1] + c[1]
        t_x2 = line[i+1][0] + c[0]
        t_y2 = line[i+1][1] + c[1]
        t_wire.append("Wire Wire Line\n")
        t_wire.append("	{} {} {} {}\n".format(t_x1,t_y1,t_x2,t_y2))
        t_out = "\n"+"".join(t_wire)    
    
    return (t_out)


class Circuit(SkidlBaseObject):
    """
    Class object that holds the entire netlist of parts and nets.

    Attributes:
        parts: List of all the schematic parts as Part objects.
        nets: List of all the schematic nets as Net objects.
        buses: List of all the buses as Bus objects.
        hierarchy: A '.'-separated concatenation of the names of nested
            SubCircuits at the current time it is read.
        level: The current level in the schematic hierarchy.
        context: Stack of contexts for each level in the hierarchy.
    """

    # Set the default ERC functions for all Circuit instances.
    erc_list = [dflt_circuit_erc]

    def __init__(self, **kwargs):
        super().__init__()

        """Initialize the Circuit object."""
        self.reset(init=True)

        # Set passed-in attributes for the circuit.
        for k, v in list(kwargs.items()):
            setattr(self, k, v)

    def reset(self, init=False):
        """Clear any circuitry and cached part libraries and start over."""

        # Clear circuitry.
        self.mini_reset(init)

        # Also clear any cached libraries.
        SchLib.reset()
        global backup_lib
        backup_lib = None

    def mini_reset(self, init=False):
        """Clear any circuitry but don't erase any loaded part libraries."""

        self.name = ""
        self.parts = []
        self.nets = []
        self.netclasses = {}
        self.buses = []
        self.interfaces = []
        self.packages = deque()
        self.hierarchy = "top"
        self.level = 0
        self.context = [("top",)]
        self.erc_assertion_list = []
        self.circuit_stack = (
            []
        )  # Stack of previous default_circuits for context manager.
        self.no_files = False  # Allow creation of files for netlists, ERC, libs, etc.

        # Internal set used to check for duplicate hierarchical names.
        self._hierarchical_names = {self.hierarchy}

        # Clear the name heap for nets and parts.
        reset_get_unique_name()

        # Clear out the no-connect net and set the global no-connect if it's
        # tied to this circuit.
        self.NC = NCNet(
            name="__NOCONNECT", circuit=self
        )  # Net for storing no-connects for parts in this circuit.
        if not init and self is default_circuit:
            builtins.NC = self.NC

    def __enter__(self):
        """Create a context for making this circuit the default_circuit."""
        self.circuit_stack.append(builtins.default_circuit)
        builtins.default_circuit = self
        return self

    def __exit__(self, type, value, traceback):
        builtins.default_circuit = self.circuit_stack.pop()

    def add_hierarchical_name(self, name):
        """Record a new hierarchical name.  Throw an error if it is a duplicate."""
        if name in self._hierarchical_names:
            log_and_raise(
                logger,
                ValueError,
                "Can't add duplicate hierarchical name {} to this circuit.".format(
                    name
                ),
            )
        self._hierarchical_names.add(name)

    def rmv_hierarchical_name(self, name):
        """Remove an existing hierarchical name.  Throw an error if non-existent."""
        try:
            self._hierarchical_names.remove(name)
        except KeyError:
            log_and_raise(
                logger,
                ValueError,
                "Can't remove non-existent hierarchical name {} from circuit.".format(
                    name
                ),
            )

    def add_parts(self, *parts):
        """Add some Part objects to the circuit."""
        for part in parts:
            # Add the part to this circuit if the part is movable and
            # it's not already in this circuit.
            if part.circuit != self:
                if part.is_movable():

                    # Remove the part from the circuit it's already in.
                    if isinstance(part.circuit, Circuit):
                        part.circuit -= part

                    # Add the part to this circuit.
                    part.circuit = self  # Record the Circuit object for this part.
                    part.ref = part.ref  # This adjusts the part reference if necessary.

                    part.hierarchy = self.hierarchy  # Store hierarchy of part.

                    # Check the part does not have a conflicting hierarchical name
                    self.add_hierarchical_name(part.hierarchical_name)

                    part.skidl_trace = (
                        get_skidl_trace()
                    )  # Store part instantiation trace.

                    self.parts.append(part)
                else:
                    log_and_raise(
                        logger,
                        ValueError,
                        "Can't add unmovable part {} to this circuit.".format(part.ref),
                    )

    def rmv_parts(self, *parts):
        """Remove some Part objects from the circuit."""
        for part in parts:
            if part.is_movable():
                if part.circuit == self and part in self.parts:
                    self.rmv_hierarchical_name(part.hierarchical_name)
                    part.circuit = None
                    part.hierarchy = None
                    self.parts.remove(part)
                else:
                    logger.warning(
                        "Removing non-existent part {} from this circuit.".format(
                            part.ref
                        )
                    )
            else:
                log_and_raise(
                    logger,
                    ValueError,
                    "Can't remove part {} from this circuit.".format(part.ref),
                )

    def add_nets(self, *nets):
        """Add some Net objects to the circuit. Assign a net name if necessary."""
        for net in nets:
            # Add the net to this circuit if the net is movable and
            # it's not already in this circuit.
            if net.circuit != self:
                if net.is_movable():

                    # Remove the net from the circuit it's already in.
                    if isinstance(net.circuit, Circuit):
                        net.circuit -= net

                    # Add the net to this circuit.
                    net.circuit = self  # Record the Circuit object the net belongs to.
                    net.name = net.name
                    net.hierarchy = self.hierarchy  # Store hierarchy of net.

                    self.nets.append(net)

                else:
                    log_and_raise(
                        logger,
                        ValueError,
                        "Can't add unmovable net {} to this circuit.".format(net.name),
                    )

    def rmv_nets(self, *nets):
        """Remove some Net objects from the circuit."""
        for net in nets:
            if net.is_movable():
                if net.circuit == self and net in self.nets:
                    net.circuit = None
                    net.hierarchy = None
                    self.nets.remove(net)
                else:
                    logger.warning(
                        "Removing non-existent net {} from this circuit.".format(
                            net.name
                        )
                    )
            else:
                log_and_raise(
                    logger,
                    ValueError,
                    "Can't remove unmovable net {} from this circuit.".format(net.name),
                )

    def add_buses(self, *buses):
        """Add some Bus objects to the circuit. Assign a bus name if necessary."""
        for bus in buses:
            # Add the bus to this circuit if the bus is movable and
            # it's not already in this circuit.
            if bus.circuit != self:
                if bus.is_movable():

                    # Remove the bus from the circuit it's already in, but skip
                    # this if the bus isn't already in a Circuit.
                    if isinstance(bus.circuit, Circuit):
                        bus.circuit -= bus

                    # Add the bus to this circuit.
                    bus.circuit = self
                    bus.name = bus.name
                    bus.hierarchy = self.hierarchy  # Store hierarchy of the bus.

                    self.buses.append(bus)
                    for net in bus.nets:
                        self += net

    def rmv_buses(self, *buses):
        """Remove some buses from the circuit."""
        for bus in buses:
            if bus.is_movable():
                if bus.circuit == self and bus in self.buses:
                    bus.circuit = None
                    bus.hierarchy = None
                    self.buses.remove(bus)
                    for net in bus.nets:
                        self -= net
                else:
                    logger.warning(
                        "Removing non-existent bus {} from this circuit.".format(
                            bus.name
                        )
                    )
            else:
                log_and_raise(
                    logger,
                    ValueError,
                    "Can't remove unmovable bus {} from this circuit.".format(bus.name),
                )

    def add_packages(self, *packages):
        for package in packages:
            if package.circuit is None:
                if package.is_movable():

                    # Add the package to this circuit.
                    self.packages.appendleft(package)
                    package.circuit = self
                    for obj in package.values():
                        try:
                            if obj.is_movable():
                                obj.circuit = self
                        except AttributeError:
                            pass
            else:
                log_and_raise(
                    logger,
                    ValueError,
                    "Can't add the same package to more than one circuit.",
                )

    def rmv_packages(self, *packages):
        for package in packages:
            if package.is_movable():
                if package.circuit == self and package in self.packages:
                    self.packages.remove(package)
                    package.circuit = None
                    for obj in package.values():
                        try:
                            if obj.is_movable():
                                obj.circuit = None
                        except AttributeError:
                            pass
                else:
                    logger.warning(
                        "Removing non-existent package {} from this circuit.".format(
                            package.name
                        )
                    )
            else:
                log_and_raise(
                    logger,
                    ValueError,
                    "Can't remove unmovable package {} from this circuit.".format(
                        package.name
                    ),
                )

    def add_stuff(self, *stuff):
        """Add Parts, Nets, Buses, and Interfaces to the circuit."""

        from .package import Package

        for thing in flatten(stuff):
            if isinstance(thing, Part):
                self.add_parts(thing)
            elif isinstance(thing, Net):
                self.add_nets(thing)
            elif isinstance(thing, Bus):
                self.add_buses(thing)
            elif isinstance(thing, Package):
                self.add_packages(thing)
            else:
                log_and_raise(
                    logger,
                    ValueError,
                    "Can't add a {} to a Circuit object.".format(type(thing)),
                )
        return self

    def rmv_stuff(self, *stuff):
        """Remove Parts, Nets, Buses, and Interfaces from the circuit."""

        from .package import Package

        for thing in flatten(stuff):
            if isinstance(thing, Part):
                self.rmv_parts(thing)
            elif isinstance(thing, Net):
                self.rmv_nets(thing)
            elif isinstance(thing, Bus):
                self.rmv_buses(thing)
            elif isinstance(thing, Package):
                self.rmv_packages(thing)
            else:
                log_and_raise(
                    logger,
                    ValueError,
                    "Can't remove a {} from a Circuit object.".format(type(pnb)),
                )
        return self

    __iadd__ = add_stuff
    __isub__ = rmv_stuff

    def get_nets(self):
        """Get all the distinct nets for the circuit."""

        distinct_nets = []
        for net in self.nets:
            if net is self.NC:
                # Exclude no-connect net.
                continue
            if not net.get_pins():
                # Exclude empty nets with no attached pins.
                continue
            for n in distinct_nets:
                # Exclude net if its already attached to a previously selected net.
                if net.is_attached(n):
                    break
            else:
                # This net is not attached to any of the other distinct nets,
                # so it is also distinct.
                distinct_nets.append(net)
        return distinct_nets

    def instantiate_packages(self):
        """Run the package executables to instantiate their circuitry."""

        # Set default_circuit to this circuit and instantiate the packages.
        with self:
            while self.packages:
                package = self.packages.pop()

                # If there are still ProtoNets attached to the package at this point,
                # just replace them with Nets. This will allow any internal connections
                # inside the package to be reflected on the package I/O pins.
                # **THIS WILL PROBABLY FAIL IF THE INTERNAL CONNECTIONS ARE BUSES.**
                # DISABLE THIS FOR NOW...
                # for k, v in package.items():
                #     if isinstance(v, ProtoNet):
                #         package[k] = Net()

                # Call the function to instantiate the package with its arguments.
                package.subcircuit(**package)

    def _cull_unconnected_parts(self):
        """Remove parts that aren't connected to anything."""

        for part in self.parts:
            if not part.is_connected():
                self -= part

    def _merge_net_names(self):
        """Select a single name for each multi-segment net."""

        for net in self.nets:
            net.merge_names()

    def _preprocess(self):
        self.instantiate_packages()
        # self._cull_unconnected_parts()
        self._merge_net_names()

    def ERC(self, *args, **kwargs):
        """Run class-wide and local ERC functions on this circuit."""

        # Reset the counters to clear any warnings/errors from previous ERC run.
        erc_logger.error.reset()
        erc_logger.warning.reset()

        self._preprocess()

        if self.no_files:
            erc_logger.stop_file_output()

        super().ERC(*args, **kwargs)

        if (erc_logger.error.count, erc_logger.warning.count) == (0, 0):
            sys.stderr.write("\nNo ERC errors or warnings found.\n\n")
        else:
            sys.stderr.write(
                "\n{} warnings found during ERC.\n".format(erc_logger.warning.count)
            )
            sys.stderr.write(
                "{} errors found during ERC.\n\n".format(erc_logger.error.count)
            )

    def generate_netlist(self, **kwargs):
        """
        Return a netlist and also write it to a file/stream.

        Args:
            file_: Either a file object that can be written to, or a string
                containing a file name, or None.
            tool: The EDA tool the netlist will be generated for.
            do_backup: If true, create a library with all the parts in the circuit.

        Returns:
            A netlist.
        """

        from . import skidl

        # Reset the counters to clear any warnings/errors from previous run.
        logger.error.reset()
        logger.warning.reset()

        self._preprocess()

        # Extract arguments:
        #     Get EDA tool the netlist will be generated for.
        #     Get file the netlist will be stored in (if any).
        #     Get flag controlling the generation of a backup library.
        tool = kwargs.pop("tool", skidl.get_default_tool())
        file_ = kwargs.pop("file_", None)
        do_backup = kwargs.pop("do_backup", True)

        try:
            gen_func = getattr(self, "_gen_netlist_{}".format(tool))
            netlist = gen_func(**kwargs)  # Pass any remaining arguments.
        except KeyError:
            log_and_raise(
                logger,
                ValueError,
                "Can't generate netlist in an unknown ECAD tool format ({}).".format(
                    tool
                ),
            )

        if (logger.error.count, logger.warning.count) == (0, 0):
            sys.stderr.write(
                "\nNo errors or warnings found during netlist generation.\n\n"
            )
        else:
            sys.stderr.write(
                "\n{} warnings found during netlist generation.\n".format(
                    logger.warning.count
                )
            )
            sys.stderr.write(
                "{} errors found during netlist generation.\n\n".format(
                    logger.error.count
                )
            )

        if not self.no_files:
            with opened(file_ or (get_script_name() + ".net"), "w") as f:
                f.write(str(netlist))

        if do_backup:
            self.backup_parts()  # Create a new backup lib for the circuit parts.
            global backup_lib  # Clear out any old backup lib so the new one
            backup_lib = None  #   will get reloaded when it's needed.

        return netlist

    def generate_pcb(self, **kwargs):
        """
        Create a PCB file from the circuit.

        Args:
            file_: Either a file object that can be written to, or a string
                containing a file name, or None.
            tool: The EDA tool the netlist will be generated for.
            do_backup: If true, create a library with all the parts in the circuit.

        Returns:
            None.
        """

        from . import skidl

        # Reset the counters to clear any warnings/errors from previous run.
        logger.error.reset()
        logger.warning.reset()

        self._preprocess()

        # Extract arguments:
        #     Get EDA tool the netlist will be generated for.
        #     Get file the netlist will be stored in (if any).
        #     Get flag controlling the generation of a backup library.
        tool = kwargs.pop("tool", skidl.get_default_tool())
        file_ = kwargs.pop("file_", None)
        do_backup = kwargs.pop("do_backup", True)

        if not self.no_files:
            try:
                gen_func = getattr(self, "_gen_pcb_{}".format(tool))
            except KeyError:
                log_and_raise(
                    logger,
                    ValueError,
                    "Can't generate PCB in an unknown ECAD tool format ({}).".format(
                        tool
                    ),
                )
            else:
                if do_backup:
                    self.backup_parts()  # Create a new backup lib for the circuit parts.
                    global backup_lib  # Clear out any old backup lib so the new one
                    backup_lib = None  #   will get reloaded when it's needed.
                gen_func(file_)  # Generate the PCB file from the netlist.

        if (logger.error.count, logger.warning.count) == (0, 0):
            sys.stderr.write("\nNo errors or warnings found while creating PCB.\n\n")
        else:
            sys.stderr.write(
                "\n{} warnings found while creating PCB.\n".format(logger.warning.count)
            )
            sys.stderr.write(
                "{} errors found while creating PCB.\n\n".format(logger.error.count)
            )

    def generate_xml(self, file_=None, tool=None):
        """
        Return netlist as an XML string and also write it to a file/stream.

        Args:
            file_: Either a file object that can be written to, or a string
                containing a file name, or None.

        Returns:
            A string containing the netlist.
        """

        from . import skidl

        # Reset the counters to clear any warnings/errors from previous run.
        logger.error.reset()
        logger.warning.reset()

        self._preprocess()

        if tool is None:
            tool = skidl.get_default_tool()

        try:
            gen_func = getattr(self, "_gen_xml_{}".format(tool))
            netlist = gen_func()
        except KeyError:
            log_and_raise(
                logger,
                ValueError,
                "Can't generate XML in an unknown ECAD tool format ({}).".format(tool),
            )

        if (logger.error.count, logger.warning.count) == (0, 0):
            sys.stderr.write("\nNo errors or warnings found during XML generation.\n\n")
        else:
            sys.stderr.write(
                "\n{} warnings found during XML generation.\n".format(
                    logger.warning.count
                )
            )
            sys.stderr.write(
                "{} errors found during XML generation.\n\n".format(logger.error.count)
            )

        if not self.no_files:
            with opened(file_ or (get_script_name() + ".xml"), "w") as f:
                f.write(netlist)

        return netlist

    def generate_netlistsvg_skin(self, net_stubs):
        """Generate the skin file of symbols for use by netlistsvg."""

        # Generate the SVG for each part in the required transformations.
        part_svg = {}
        for part in self.parts:

            # If this part is attached to any net stubs, give it a symbol
            # name specifically for this part + stubs.
            if part.attached_to(net_stubs):
                # This part is attached to net stubs, so give it
                # a symbol name specifically for this part + stubs.
                symbol_name = part.name + "_" + part.ref
            else:
                # This part is not attached to any stubs, so give it
                # a symbol name for this generic part symbol.
                symbol_name = part.name

            # Get the global transformation for the part symbol.
            global_symtx = getattr(part, "symtx", "")
            # Get the transformation for each part unit.
            unit_symtx = set([""])
            for unit in part.unit.values():
                unit_symtx.add(getattr(unit, "symtx", ""))
            # Each combination of global + unit transformation is one of
            # the total transformations needed for the part.
            total_symtx = [global_symtx + u_symtx for u_symtx in unit_symtx]

            # Generate SVG of the part for each total transformation.
            for symtx in total_symtx:
                name = symbol_name + "_" + symtx
                # Skip any repeats of the part.
                if name not in part_svg.keys():
                    part_svg[name] = part.generate_svg_component(
                        symtx=symtx, net_stubs=net_stubs
                    )

        part_svg = list(part_svg.values())  # Just keep the SVG for the part symbols.

        head_svg = [
            '<svg xmlns="http://www.w3.org/2000/svg"'
            '     xmlns:xlink="http://www.w3.org/1999/xlink"'
            '     xmlns:s="https://github.com/nturley/netlistsvg">'
            "  <s:properties"
            '    constants="false"'
            '    splitsAndJoins="false"'
            '    genericsLaterals="true">'
            "    <s:layoutEngine"
            '        org.eclipse.elk.layered.spacing.nodeNodeBetweenLayers="5"'
            '        org.eclipse.elk.layered.compaction.postCompaction.strategy="4"'
            '        org.eclipse.elk.spacing.nodeNode= "50"'
            '        org.eclipse.elk.direction="DOWN"/>'
            "  </s:properties>"
            "<style>"
            "svg {"
            "  stroke: #000;"
            "  fill: none;"
            "  stroke-linejoin: round;"
            "  stroke-linecap: round;"
            "}"
            "text {"
            "  fill: #000;"
            "  stroke: none;"
            "  font-size: 10px;"
            "  font-weight: bold;"
            '  font-family: "Courier New", monospace;'
            "}"
            ".skidl_text {"
            "  fill: #999;"
            "  stroke: none;"
            "  font-weight: bold;"
            '  font-family: consolas, "Courier New", monospace;'
            "}"
            ".pin_num_text {"
            "    fill: #840000;"
            "}"
            ".pin_name_text {"
            "    fill: #008484;"
            "}"
            ".net_name_text {"
            "    font-style: italic;"
            "    fill: #840084;"
            "}"
            ".part_text {"
            "    fill: #840000;"
            "}"
            ".part_ref_text {"
            "    fill: #008484;"
            "}"
            ".part_name_text {"
            "    fill: #008484;"
            "}"
            ".pen_fill {"
            "    fill: #840000;"
            "}"
            ".background_fill {"
            "    fill: #FFFFC2"
            "}"
            ".nodelabel {"
            "  text-anchor: middle;"
            "}"
            ".inputPortLabel {"
            "  text-anchor: end;"
            "}"
            ".splitjoinBody {"
            "  fill: #000;"
            "}"
            ".symbol {"
            "  stroke-linejoin: round;"
            "  stroke-linecap: round;"
            "  stroke: #840000;"
            "}"
            ".detail {"
            "  stroke-linejoin: round;"
            "  stroke-linecap: round;"
            "  fill: #000;"
            "}"
            "</style>"
            ""
            "<!-- signal -->"
            '<g s:type="inputExt" s:width="30" s:height="20" transform="translate(0,0)">'
            '  <text x="-2" y="12" text-anchor=\'end\' class="$cell_id pin_name_text" s:attribute="ref">input</text>'
            '  <s:alias val="$_inputExt_"/>'
            '  <path d="M0,0 V20 H15 L30,10 15,0 Z" class="$cell_id symbol"/>'
            '  <g s:x="30" s:y="10" s:pid="Y" s:position="right"/>'
            "</g>"
            ""
            '<g s:type="outputExt" s:width="30" s:height="20" transform="translate(0,0)">'
            '  <text x="32" y="12" class="$cell_id pin_name_text" s:attribute="ref">output</text>'
            '  <s:alias val="$_outputExt_"/>'
            '  <path d="M30,0 V20 H15 L0,10 15,0 Z" class="$cell_id symbol"/>'
            '  <g s:x="0" s:y="10" s:pid="A" s:position="left"/>'
            "</g>"
            "<!-- signal -->"
            ""
            "<!-- builtin -->"
            '<g s:type="generic" s:width="30" s:height="40" transform="translate(0,0)">'
            '  <text x="15" y="-4" class="nodelabel $cell_id" s:attribute="ref">generic</text>'
            '  <rect width="30" height="40" x="0" y="0" s:generic="body" class="$cell_id"/>'
            '  <g transform="translate(30,10)"'
            '     s:x="30" s:y="10" s:pid="out0" s:position="right">'
            '    <text x="5" y="-4" class="$cell_id">out0</text>'
            "  </g>"
            '  <g transform="translate(30,30)"'
            '     s:x="30" s:y="30" s:pid="out1" s:position="right">'
            '    <text x="5" y="-4" class="$cell_id">out1</text>'
            "  </g>"
            '  <g transform="translate(0,10)"'
            '     s:x="0" s:y="10" s:pid="in0" s:position="left">'
            '      <text x="-3" y="-4" class="inputPortLabel $cell_id">in0</text>'
            "  </g>"
            '  <g transform="translate(0,30)"'
            '     s:x="0" s:y="30" s:pid="in1" s:position="left">'
            '    <text x="-3" y="-4" class="inputPortLabel $cell_id">in1</text>'
            "  </g>"
            "</g>"
            "<!-- builtin -->"
        ]

        tail_svg = [
            "</svg>",
        ]

        return "\n".join(head_svg + part_svg + tail_svg)

    def generate_svg(self, file_=None, tool=None):
        """
        Create an SVG file displaying the circuit schematic and
        return the dictionary that can be displayed by netlistsvg.
        """

        from . import skidl

        # Reset the counters to clear any warnings/errors from previous run.
        logger.error.reset()
        logger.warning.reset()

        self._preprocess()

        # Get the list of nets which will be routed and not represented by stubs.
        # Search all nets for those set as stubs or that are no-connects.
        net_stubs = [
            n for n in self.nets if getattr(n, "stub", False) or isinstance(n, NCNet)
        ]
        # Also find buses that are set as stubs and add their individual nets.
        net_stubs.extend(
            expand_buses([b for b in self.buses if getattr(b, "stub", False)])
        )
        routed_nets = list(set(self.nets) - set(net_stubs))

        # Assign each routed net a unique integer. Interconnected nets
        # all get the same number.
        net_nums = {}
        for num, net in enumerate(routed_nets, 1):
            for n in net.get_nets():
                if n.name not in net_nums:
                    net_nums[n.name] = num

        io_dict = {"i": "input", "o": "output"}

        # Assign I/O ports to any named net that has a netio attribute.
        ports = {}
        for net in routed_nets:
            if not net.is_implicit():
                try:
                    # Net I/O direction set by 1st letter of netio attribute.
                    io = io_dict[net.netio.lower()[0]]
                    ports[net.name] = {
                        "direction": io,
                        "bits": [
                            net_nums[net.name],
                        ],
                    }
                except AttributeError:
                    # Net has no netio so don't assign a port.
                    pass

        pin_dir_tbl = {
            Pin.types.INPUT: "input",
            Pin.types.OUTPUT: "output",
            Pin.types.BIDIR: "output",
            Pin.types.TRISTATE: "output",
            Pin.types.PASSIVE: "input",
            Pin.types.PULLUP: "output",
            Pin.types.PULLDN: "output",
            Pin.types.UNSPEC: "input",
            Pin.types.PWRIN: "input",
            Pin.types.PWROUT: "output",
            Pin.types.OPENCOLL: "output",
            Pin.types.OPENEMIT: "output",
            Pin.types.NOCONNECT: "nc",
        }

        cells = {}
        for part in self.parts:

            if part.attached_to(net_stubs):
                part_name = part.name + "_" + part.ref
            else:
                part_name = part.name

            part_symtx = getattr(part, "symtx", "")
            units = part.unit.values()
            if not units:
                units = [
                    part,
                ]
            for unit in units:

                if not unit.is_connected():
                    continue  # Skip unconnected parts.

                pins = unit.get_pins()

                # Associate each connected pin of a part with the assigned net number.
                connections = {
                    pin.num: [
                        net_nums[pin.net.name],
                    ]
                    for pin in pins
                    if pin.net in routed_nets
                }

                # Assign I/O to each part pin by either using the pin's symio
                # attribute or by using its pin function.
                part_pin_dirs = {
                    pin.num: io_dict[
                        getattr(pin, "symio", pin_dir_tbl[pin.func]).lower()[0]
                    ]
                    for pin in pins
                }
                # Remove no-connect pins.
                part_pin_dirs = {n: d for n, d in part_pin_dirs.items() if d}

                # Determine which symbol in the skin file goes with this part.
                unit_symtx = part_symtx + getattr(unit, "symtx", "")
                if not isinstance(unit, PartUnit):
                    ref = part.ref
                    name = part_name + "_1_" + part_symtx
                else:
                    ref = part.ref + num_to_chars(unit.num)
                    name = part_name + "_" + str(unit.num) + "_" + unit_symtx

                # Create the cell that netlistsvg uses to draw the part and connections.
                cells[ref] = {
                    "type": name,
                    "port_directions": part_pin_dirs,
                    "connections": connections,
                    "attributes": {
                        "value": str(part.value),
                    },
                }

        schematic_json = {
            "modules": {
                self.name: {
                    "ports": ports,
                    "cells": cells,
                }
            }
        }

        if not self.no_files:
            file_basename = file_ or get_script_name()
            json_file = file_basename + ".json"
            svg_file = file_basename + ".svg"

            with opened(json_file, "w") as f:
                f.write(
                    json.dumps(
                        schematic_json, sort_keys=True, indent=2, separators=(",", ": ")
                    )
                )

            skin_file = file_basename + "_skin.svg"
            with opened(skin_file, "w") as f:
                f.write(self.generate_netlistsvg_skin(net_stubs=net_stubs))

            subprocess.Popen(
                ["netlistsvg", json_file, "--skin", skin_file, "-o", svg_file],
                shell=False,
            )

        return schematic_json

    # Get the eeschema center point, also returning the entire header right now
    def get_schematic_center(self, _file):
        import skidl
        

        self._preprocess()
        tool = skidl.get_default_tool()
        
        try:
            gen_func = getattr(self, "_get_schematic_center_{}".format(tool))
            return gen_func(_file)
        except AttributeError:
            log_and_raise(
                logger,
                ValueError,
                "Can't get the center of the file({}).".format(tool),
            )

    # Get the eeschema center point, also returning the entire header right now
    def gen_hier_rect(self):
        import skidl
        

        self._preprocess()
        tool = skidl.get_default_tool()
        
        try:
            gen_func = getattr(self, "_gen_hier_rect_{}".format(tool))
            return gen_func()
        except AttributeError:
            log_and_raise(
                logger,
                ValueError,
                "Can't get the center of the file({}).".format(tool),
            )

    def generate_schematic(self, file_=None, tool=None):
        """
        Create a schematic file. THIS KINDA WORKS!  
        
        The target schematic file must be an already made kicad schematic.  This is where we get the header info from.
        """

        from . import skidl

        # Reset the counters to clear any warnings/errors from previous run.
        logger.error.reset()
        logger.warning.reset()

        self._preprocess()

        if tool is None:
            tool = skidl.get_default_tool()

        sch_c = self.get_schematic_center(file_) # Get the center of the schematic
        top_page = [] # List that will be populated with hierarchical schematics
        nSheets = 1 # Keep track of the number of sheets for use in eeschema header

        # Get a list of all the stubs for generation at the end
        stubs = []
        for i in self.nets:
            if hasattr(i, 'stub'):
                stubs.append(i)

        # Range through the parts and create bounding boxes
        for i in self.parts:
            i.generate_bounding_box()


        # Make dictionary of hierarchies and append parts from that hierarchy
        # Also make the hierarchicalc schematics for each subcircuit and add them to the top_page[] list
        hierarchies = {}
        x_start = 5000
        y_start = 5000
        for i in self.parts:
            # TODO: this strategy of getting the hierarchies might not work with nested hierarchies
            t = i.hierarchy
            u = t.split('.') # ignore 'top.'
            hier_name = u[1]
            if hier_name not in hierarchies:
                hierarchies[hier_name] = {'parts':[i],'nets':[]}
                hier_sheet = gen_hier_sheet(hier_name, x_start, y_start)
                top_page.append(hier_sheet)
                x_start += 3000
            else:
                hierarchies[hier_name]['parts'].append(i)



        # get the hierarchy nets
        for h in hierarchies:
            for n in self.nets:
                if hasattr(n, 'stub'):
                    if n.stub:
                        pass
                # for p in n.pins:
                #     elkjs_net = []
                #     t = "edge {}.{} -> {}.{}".format()
                #     elkjs_net.append(t)
                if h in n.hierarchy:
                    hierarchies[h]['nets'].append(n)
       
        for h in hierarchies:
            for n in hierarchies[h]['nets']:
                for p in range(len(n.pins)):
                    try:
                        part1 = n.pins[p].ref
                        pin1 = n.pins[p].num
                        part2 = n.pins[p+1].ref
                        pin2 = n.pins[p+1].num
                        t = "edge {}.p{} -> {}.p{}".format(part1, pin1, part2, pin2)
                        print(t)
                        # ("\n" + "".join(t))

                    except:
                        pass

        # Range through each hierarchy and place parts around the center part (part 0)
        for h in hierarchies:
            centerPart = hierarchies[h]['parts'][0].ref # Center part that we place everything else around
            eeschema_code = [] # List to hold all the components we'll put the in the eeschema .sch file
            hierarchies[h]['parts_placed'] = []
            hierarchies[h]['nets_to_route'] = []
            # Range through all the nets and place the parts around center pin
            for n in hierarchies[h]['nets']:
                found = False
                cp_num = 0 # central part pin # in the net
                for pin in n.pins:
                    if pin.ref in centerPart:
                        found = True
                        break
                    else:
                        cp_num += 1 # not this part, increment the counter
                if found:
                    # Place parts with pins connected to this net that we haven't placed and aren't central parts
                    # for each pin in the net check if it's a pin of the central part or 
                    #  a pin of a part we already placed.  Don't try to place those parts again.
                    for pin in n.pins:
                        if (pin.ref in centerPart) or (pin.ref in hierarchies[h]['parts_placed']):
                            continue
                        # calculate the distance and move the part
                        calc_move_part(pin, n.pins[cp_num], hierarchies[h]['parts'])
                        hierarchies[h]['parts_placed'].append(pin.ref)  
                else:
                    hierarchies[h]['nets_to_route'].append(n)
            
            # 1. range through the remaining nets, 
            # 2. find parts with one already placed components
            # 3. place those components, only nudging left and right
            # 4. Delete the net from the list of nets to route
            # Schematic components should be made to have signal pins only on left & right
            # See this article by Altium
            # https://resources.altium.com/p/guidelines-creating-useful-schematic-symbols
            # 2nd round parts to be nudged only left and right
            for n in hierarchies[h]['nets_to_route']:
                # look for parts that are connected to more central parts already
                found = False
                pplaced = "" # track which part was placed already, and we'll place relative to that
                for p in n.pins:
                    if p.ref in hierarchies[h]['parts_placed']:
                        found = True
                        pplaced = p.ref
                        break
                if not found:
                    continue

                # range through net pins and look for the part we already placed
                # We need to find the list index of the net/part already placed
                cp_num = 0 # central part pin # in the net
                for pin in n.pins:
                    if pin.ref in pplaced:
                        break
                    else:
                        cp_num += 1

                for pin in n.pins:
                    # place the part if 
                    if pin.ref in pplaced or (pin.ref in hierarchies[h]['parts_placed']):
                        continue

                    calc_move_part(pin, n.pins[cp_num], hierarchies[h]['parts'])
                    hierarchies[h]['parts_placed'].append(pin.ref)
                    hierarchies[h]['nets_to_route'].remove(n) # remove the net after we've placed this component
            # TODO: place any other parts that have not been addressed yet
            # for now we just place them down and away from the main circuit
            offset_x = 0
            offset_y = hierarchies[h]['parts'][0].sch_bb[1] + hierarchies[h]['parts'][0].sch_bb[3] + 500
            for p in hierarchies[h]['parts']:
                if p.ref == hierarchies[h]['parts'][0].ref:
                    continue
                if p.sch_bb[0] == 0 and p.sch_bb[1] ==0 :
                    p.sch_bb[0] += offset_x
                    p.sch_bb[1] += offset_y
                    offset_x += 300

            # Add the central coordinates to the part so they're in the center
            for i in hierarchies[h]['parts']:
                x = i.sch_bb[0] + sch_c[0]
                y = i.sch_bb[1] + sch_c[1]
                part_code = i.gen_part_eeschema([x, y])
                eeschema_code.append(part_code)
            
            # Create the nets and add them to the circuit parts list
            for n in hierarchies[h]['nets']:
                wire = gen_net_wire(n,hierarchies[h]['parts'], sch_c)
                eeschema_code.append(wire)

            # Append stubs
            for s in stubs:
                for p in s.pins:
                    if p.part.hierarchy[4:] == h:
                        # print("add stub " + s._name + " to " +p.part.ref)
                        stub = gen_power_part_eeschema(p.part, s._name, sch_c)
                        eeschema_code.append(stub)

            # Draw rectangle and label subcircuit
            rect = draw_rect_hierarchies(hierarchies[h], sch_c)
            eeschema_code.append(rect)
            # Create the new hierarchy file
            hier_file_name = "stm32/" + h + ".sch"
            with open(hier_file_name, "w") as f:
                new_sch_file = [gen_config_header(cur_sheet_num=nSheets), eeschema_code, "$EndSCHEMATC"]
                nSheets += 1
                f.truncate(0) # Clear the file
                for i in new_sch_file:
                    print("" + "".join(i), file=f)
            f.close()

        # Write data to main .sch file now that we know how many subcircuits we'll have
        with open(file_, "w") as f:
            new_sch_file = [gen_config_header(cur_sheet_num=nSheets), top_page, "$EndSCHEMATC"]
            nSheets += 1
            f.truncate(0) # Clear the file
            for i in new_sch_file:
                print("" + "".join(i), file=f)
        f.close()

        # Log errors if we have any
        if (logger.error.count, logger.warning.count) == (0, 0):
            sys.stderr.write(
                "\nNo errors or warnings found during schematic generation.\n\n"
            )
        else:
            sys.stderr.write(
                "\n{} warnings found during schematic generation.\n".format(
                    logger.warning.count
                )
            )
            sys.stderr.write(
                "{} errors found during schematic generation.\n\n".format(
                    logger.error.count
                )
            )

    def generate_dot(
        self,
        file_=None,
        engine="neato",
        rankdir="LR",
        part_shape="rectangle",
        net_shape="point",
        splines=None,
        show_values=True,
        show_anon=False,
        split_nets=["GND"],
        split_parts_ref=[],
    ):
        """
        Returns a graphviz graph as graphviz object and can also write it to a file/stream.
        When used in ipython the graphviz object will drawn as an SVG in the output.

        See https://graphviz.readthedocs.io/en/stable/ and http://graphviz.org/doc/info/attrs.html

        Args:
            file_: A string containing a file name, or None.
            engine: See graphviz documentation
            rankdir: See graphviz documentation
            part_shape: Shape of the part nodes
            net_shape: Shape of the net nodes
            splines: Style for the edges, try 'ortho' for a schematic like feel
            show_values: Show values as external labels on part nodes
            show_anon: Show anonymous net names
            split_nets: splits up the plot for the given list of net names
            split_parts_ref: splits up the plot for all pins for the given list of part refs

        Returns:
            graphviz.Digraph
        """

        # Reset the counters to clear any warnings/errors from previous run.
        logger.error.reset()
        logger.warning.reset()

        self._preprocess()

        dot = graphviz.Digraph(engine=engine)
        dot.attr(rankdir=rankdir, splines=splines)

        nets = self.get_nets()

        # try and keep things in the same order
        nets.sort(key=lambda n: n.name.lower())

        # Add stubbed nets to split_nets:
        split_nets = split_nets[:]  # Make a local copy.
        split_nets.extend([n.name for n in nets if getattr(n, "stub", False)])

        for i, n in enumerate(nets):
            xlabel = n.name
            if not show_anon and n.is_implicit():
                xlabel = None
            if n.name not in split_nets:
                dot.node(n.name, shape=net_shape, xlabel=xlabel)

            for j, pin in enumerate(n.get_pins()):
                net_ref = n.name
                pin_part_ref = pin.part.ref

                if n.name in split_nets:
                    net_ref += str(j)
                    dot.node(net_ref, shape=net_shape, xlabel=xlabel)
                if pin.part.ref in split_parts_ref and n.name not in split_nets:
                    label = pin.part.ref + ":" + pin.name

                    # add label to part
                    net_ref_part = "%s_%i_%i" % (net_ref, i, j)
                    dot.node(net_ref_part, shape=net_shape, xlabel=label)
                    dot.edge(pin_part_ref, net_ref_part, arrowhead="none")

                    # add label to splited net
                    pin_part_ref = "%s_%i_%i" % (pin_part_ref, i, j)
                    dot.node(pin_part_ref, shape=net_shape, xlabel=label)
                    dot.edge(pin_part_ref, net_ref, arrowhead="none")
                else:
                    dot.edge(
                        pin_part_ref, net_ref, arrowhead="none", taillabel=pin.name
                    )

        for p in sorted(self.parts, key=lambda p: p.ref.lower()):
            xlabel = None
            if show_values:
                xlabel = str(p.value)
            dot.node(p.ref, shape=part_shape, xlabel=xlabel)

        if not self.no_files:
            if file_ is not None:
                dot.save(file_)

        return dot

    generate_graph = generate_dot  # Old method name for generating graphviz dot file.

    def backup_parts(self, file_=None):
        """
        Saves parts in circuit as a SKiDL library in a file.

        Args:
            file: Either a file object that can be written to, or a string
                containing a file name, or None. If None, a standard library
                file will be used.

        Returns:
            Nothing.
        """

        from . import skidl

        if self.no_files:
            return

        self._preprocess()

        lib = SchLib(tool=SKIDL)  # Create empty library.
        for p in self.parts:
            lib += p

        if not file_:
            file_ = skidl.BACKUP_LIB_FILE_NAME

        lib.export(libname=skidl.BACKUP_LIB_NAME, file_=file_)


__func_name_cntr = defaultdict(int)


def SubCircuit(f):
    """
    A @SubCircuit decorator is used to create hierarchical circuits.

    Args:
        f: The function containing SKiDL statements that represents a subcircuit.
    """

    @functools.wraps(f)
    def sub_f(*args, **kwargs):
        # Upon entry, save the reference to the current default Circuit object.
        save_default_circuit = default_circuit  # pylint: disable=undefined-variable

        # If the subcircuit uses the 'circuit' argument, then set the default
        # Circuit object to that. Otherwise, use the current default Circuit object.
        circuit = kwargs.pop("circuit", default_circuit)
        builtins.default_circuit = circuit

        # Setup some globals needed in the subcircuit.
        builtins.NC = default_circuit.NC  # pylint: disable=undefined-variable

        # Invoking the subcircuit function creates circuitry at a level one
        # greater than the current level. (The top level is zero.)
        circuit.level += 1

        # Create a name for this subcircuit from the concatenated names of all
        # the nested subcircuit functions that were called on all the preceding levels
        # that led to this one. Also, add a distinct tag to the current
        # function name to disambiguate multiple uses of the same function.  This is
        # either specified as an argument, or an incrementing value is used.
        tag = kwargs.pop("tag", None)
        if tag is None:
            tag = __func_name_cntr[f.__name__]
            __func_name_cntr[f.__name__] = __func_name_cntr[f.__name__] + 1
        circuit.hierarchy = circuit.context[-1][0] + "." + f.__name__ + str(tag)
        circuit.add_hierarchical_name(circuit.hierarchy)

        # Store the context so it can be used if this subcircuit function
        # invokes another subcircuit function within itself to add more
        # levels of hierarchy.
        circuit.context.append((circuit.hierarchy,))

        # Call the function to create whatever circuitry it handles.
        # The arguments to the function are usually nets to be connected to the
        # parts instantiated in the function, but they may also be user-specific
        # and have no effect on the mechanics of adding parts or nets although
        # they may direct the function as to what parts and nets get created.
        # Store any results it returns as a list. These results are user-specific
        # and have no effect on the mechanics of adding parts or nets.
        results = f(*args, **kwargs)

        # Restore the context that existed before the subcircuitry was
        # created. This does not remove the circuitry since it has already been
        # added to the parts and nets lists.
        circuit.context.pop()

        # Restore the hierarchy label and level.
        circuit.hierarchy = circuit.context[-1][0]
        circuit.level -= 1

        # Restore the default circuit and globals.
        builtins.default_circuit = save_default_circuit
        builtins.NC = default_circuit.NC  # pylint: disable=undefined-variable

        return results

    return sub_f


# The decorator can also be called as "@subcircuit".
subcircuit = SubCircuit
