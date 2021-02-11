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

    def round(self):
        try:
            self.x = int(round(self.x))
            self.y = int(round(self.y))
        except OverflowError:
            # Point with coords set as math.inf.
            pass


class BBox:
    def __init__(self, *pts):
        inf = float("inf")
        self.min = Point(inf, inf)
        self.max = Point(-inf, -inf)
        self.add(*pts)

    def add(self, *objs):
        for obj in objs:
            if isinstance(obj, Point):
                self.min = Point(min(self.min.x, obj.x), min(self.min.y, obj.y))
                self.max = Point(max(self.max.x, obj.x), max(self.max.y, obj.y))
            elif isinstance(obj, BBox):
                self.min.x = min(self.min.x, obj.min.x)
                self.min.y = min(self.min.y, obj.min.y)
                self.max.x = max(self.max.x, obj.max.x)
                self.max.y = max(self.max.y, obj.max.y)
            else:
                raise NotImplementedError

    @property
    def area(self):
        return self.w * self.h

    def round(self):
        self.min.round()
        self.max.round()

    @property
    def w(self):
        return abs(self.max.x - self.min.x)

    @property
    def h(self):
        return abs(self.max.y - self.min.y)
