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
from functools import reduce
from .coord import *

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
        self.parts = []
        self.num_pins = 0

    def add_part(self, part):
        self.parts.append(part)
        self.num_pins += len(part)
        part.region = self

    __iadd__ = add_part

    def rmv_part(self, part):
        self.parts.remove(part)
        self.num_pins -= len(part)
        part.region = None

    __isub__ = rmv_part

    def cost(self):
        return math.sqrt(self.num_pins)

class PartNet(self):
    """ Stores the parts attached to a particular net. """
    def __init__(self, net):
        self.parts = []
        self.bbox = BBox()
        for pin in net.get_pins():
            self += pin.part

    def add_part(self, part):
        if part not in self.parts:
            self.parts.append(part)
            self.bbox.add(part.region)

    __iadd__ = add_part

    def cost(self, regions):
        cst = 0
        for r in range(self.bbox.min.y, self.bbox.max.y + 1):
            for c in range(self.bbox.min.x, self.bbox.max.x + 1):
                cst += regions[r][c].cost()
        return cst

class Arranger:
    def __init__(self, circuit, height=3, width=3):
        self.width, self.height = width, height
        self.regions = [[Region(x, y) for y in range(height)] for x in range(width)]
        self.nets = [PartNet(net) for net in circuit.nets]
        for part in circuit.parts:
            x = randint(0, width-1)
            y = randint(0, height-1)
            self.regions[x][y] += part

    def cost(self):
        return sum([cost(net) for net in self.nets])

    def arrange(self):
        pass
