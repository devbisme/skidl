# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

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
