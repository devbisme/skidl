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

import math
from copy import copy, deepcopy

"""
Coordinates, mostly for working with converting symbols to SVG.
"""


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, pt):
        if not isinstance(pt, Point):
            npt = Point(pt, pt)
            return self + npt
        return Point(self.x + pt.x, self.y + pt.y)

    def __sub__(self, pt):
        if not isinstance(pt, Point):
            npt = Point(pt, pt)
            return self - npt
        return Point(self.x - pt.x, self.y - pt.y)

    def __mul__(self, m):
        return Point(m * self.x, m * self.y)

class BBox:
    def __init__(self, min_pt=None, max_pt=None):
        if min_pt is None:
            self.min = Point(math.inf, math.inf)
        else:
            self.min = deepcopy(min_pt)
        if max_pt is None:
            self.max = Point(-math.inf, -math.inf)
        else:
            self.max = deepcopy(max_pt)

    def add(self, pt):
        self.min = Point(min(self.min.x, pt.x), min(self.min.y, pt.y))
        self.max = Point(max(self.max.x, pt.x), max(self.max.y, pt.y))

    @property
    def w(self):
        return abs(self.max.x - self.min.x)

    @property
    def h(self):
        return abs(self.max.y - self.min.y)
