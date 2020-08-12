# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2020 by XESS Corp.
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
Arrange part units for best schematic wiring.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import re
from builtins import str, super

from future import standard_library
import math
from collections import namedtuple
from functools import reduce
from .coord import *
from .net import NCNet

standard_library.install_aliases()


# foreach net, record which part units are attached to each net.
# assign each part unit to a region.
# compute cost for placement:
#     foreach region, sum the pins for the part units assigned to that region.
#     foreach net:
#         compute the bounding box.
#         cost of the net is the square-root of the number of pins within its bounding box.
#         add net cost to the total cost.
#
# compute cost of moving a part unit to another region:
#     remove pins from source region and add to destination region.
#     compute new cost


class Region(Point):
    """ Stores an (x,y) coord and a list of the parts stored within it. """

    def __init__(self, x, y):
        super().__init__(x, y)
        self.clear()

    def clear(self):
        try:
            for part in self.parts:
                part.region = None
        except AttributeError:
            pass
        self.parts = []
        self.num_pins = 0

    def add_part(self, part):
        self.parts.append(part)
        self.num_pins += len(part)
        part.region = self
        return self

    __iadd__ = add_part

    def rmv_part(self, part):
        self.parts.remove(part)
        self.num_pins -= len(part)
        part.region = None
        return self

    __isub__ = rmv_part

    def cost(self):
        return math.sqrt(self.num_pins) + 1.0


class PartNet:
    """ Stores the parts attached to a particular net. """

    def __init__(self, net):
        self.parts = set()

        # Don't count parts attached to no-connect nets.
        if not isinstance(net, NCNet):
            for pin in net.get_pins():
                self.parts.add(pin.part)

    def calc_bbox(self):
        self.bbox = BBox()
        for part in list(self.parts):
            self.bbox.add(part.region)
        self.bbox.round()

    def cost(self, regions):
        cst = 0
        
        # Don't calculate cost of nets with no parts because they will
        # have invalid bounding boxes. Their cost should be zero.
        if self.parts:
            self.calc_bbox()
            for r in range(self.bbox.min.y, self.bbox.max.y + 1):
                for c in range(self.bbox.min.x, self.bbox.max.x + 1):
                    cst += regions[r][c].cost()
        return cst


from random import randint

class Arranger:
    def __init__(self, circuit, grid_hgt=3, grid_wid=3):
        self.w, self.h = grid_wid, grid_hgt
        self.regions = [[Region(r, c) for r in range(self.h)] for c in range(self.w)]
        self.parts = circuit.parts
        self.clear()
        self.arrange_randomly()
        # self.prearranged()
        self.nets = [PartNet(net) for net in circuit.nets if net.pins]

    def cost(self):
        return sum([net.cost(self.regions) for net in self.nets])

    def apply(self):
        for r in range(self.h):
            for c in range(self.w):
                region = self.regions[r][c]
                for part in region.parts:
                    part.region = region

    def arrange(self):
        self.arrange_randomly()
        self.arrange_kl()

    def arrange_randomly(self):
        for part in self.parts:
            c = randint(0, self.w - 1)
            r = randint(0, self.h - 1)
            self.regions[r][c] += part

    def prearranged(self):
        for part in self.parts:
            self.regions[part.xy[0]][part.xy[1]] += part

    def arrange_kl(self):
        #Move = namedtuple("Move", "part region cost")
        class Move:
            def __init__(self, part, region, cost):
                self.part = part
                self.region = region
                self.cost = cost

        def kl_phase():
            def find_best_move(parts):
                moves = []
                for part in parts:
                    saved_region = part.region
                    part.region -= part
                    for c in range(self.w):
                        for r in range(self.h):
                            self.regions[r][c] += part
                            cost = self.cost()
                            moves.append(Move(part, self.regions[r][c], cost))
                            self.regions[r][c] -= part
                    saved_region += part
                best_move = min(moves, key=lambda mv: mv.cost)
                return best_move

            beginning_cost = self.cost()
            beginning_arrangement = [Move(part, part.region, beginning_cost) for part in self.parts]
            unplaced = self.parts[:]
            moves = []
            while unplaced:
                moves.append(find_best_move(unplaced))
                unplaced.remove(moves[-1].part)
            for move in beginning_arrangement:
                move.part.region -= move.part
                move.region += move.part
            best_point = min(moves, key=lambda mv: mv.cost)
            moves = moves[:moves.index(best_point)+1]
            for move in moves:
                move.part.region -= move.part
                move.region += move.part
            cost = self.cost()
            print(f"KL phase: {cost}")
            return cost

        best_cost = self.cost()
        current_cost = best_cost + 1
        while best_cost < current_cost:
            current_cost = best_cost
            best_arrangement = [Move(part, part.region, current_cost) for part in self.parts]
            best_cost = kl_phase()
        for move in best_arrangement:
            move.part.region -= move.part
            move.region += move.part

    def clear(self):
        for x in range(self.w):
            for y in range(self.h):
                self.regions[x][y].clear()
