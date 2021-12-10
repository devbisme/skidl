# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

from copy import copy

"""
Stuff for handling geometry:
    transformation matrices,
    points,
    bounding boxes,
    line segments.
"""


class Tx:
    def __init__(self, a=1, b=0, c=0, d=1, dx=0, dy=0):
        """Create a transformation matrix.
        tx = [
               a  b  0
               c  d  0
               dx dy 1
             ]
        x' = a*x + c*y + dx
        y' = b*x + d*y + dy
        """
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.dx = dx
        self.dy = dy

    def dot(self, tx):
        return Tx(
            a=self.a * tx.a + self.b * tx.c,
            b=self.a * tx.b + self.b * tx.d,
            c=self.c * tx.a + self.d * tx.c,
            d=self.c * tx.b + self.d * tx.d,
            dx=self.dx * tx.a + self.dy * tx.c + tx.dx,
            dy=self.dx * tx.b + self.dy * tx.d + tx.dy,
        )

    @property
    def origin(self):
        return Point(self.dx, self.dy)


class Point:
    def __init__(self, x, y):
        """Create a Point with coords x,y."""
        self.x = x
        self.y = y

    def __add__(self, pt):
        """Add the x,y coords of pt to self and return the resulting Point."""
        if not isinstance(pt, Point):
            pt = Point(pt, pt)
        return Point(self.x + pt.x, self.y + pt.y)

    def __sub__(self, pt):
        """Subtract the x,y coords of pt from self and return the resulting Point."""
        if not isinstance(pt, Point):
            pt = Point(pt, pt)
        return Point(self.x - pt.x, self.y - pt.y)

    def __mul__(self, m):
        """Multiply the x,y coords by m."""
        return Point(m * self.x, m * self.y)

    __rmul__ = __mul__

    def __neg__(self):
        """Negate both coords."""
        return Point(-self.x, -self.y)

    def __truediv__(self, d):
        """Divide the x,y coords by d."""
        return Point(self.x / d, self.y / d)

    def __div__(self, d):
        """Divide the x,y coords by d."""
        return Point(self.x / d, self.y / d)

    def __round__(self, n=None):
        return Point(round(self.x, n), round(self.y, n))

    def snap(self, grid_spacing):
        """Snap point x,y coords to the given grid spacing."""
        snap_func = lambda x: int(grid_spacing * round(x / grid_spacing))
        return Point(snap_func(self.x), snap_func(self.y))

    def min(self, pt):
        """Return a Point with coords that are the min x,y of both points."""
        return Point(min(self.x, pt.x), min(self.y, pt.y))

    def max(self, pt):
        """Return a Point with coords that are the max x,y of both points."""
        return Point(max(self.x, pt.x), max(self.y, pt.y))

    def dot(self, tx):
        """Apply transformation matrix to a point and return a point."""
        return Point(
            self.x * tx.a + self.y * tx.c + tx.dx, self.x * tx.b + self.y * tx.d + tx.dy
        )

    def __repr__(self):
        return "{self.__class__}({self.x}, {self.y})".format(self=self)


Vector = Point


class BBox:
    def __init__(self, *pts):
        """Create a bounding box surrounding the given points."""
        inf = float("inf")
        self.min = Point(inf, inf)
        self.max = Point(-inf, -inf)
        self.add(*pts)

    def add(self, *objs):
        """Update the bounding box size by adding Point/BBox objects."""
        for obj in objs:
            if isinstance(obj, Point):
                self.min = self.min.min(obj)
                self.max = self.max.max(obj)
            elif isinstance(obj, BBox):
                self.min = self.min.min(obj.min)
                self.max = self.max.max(obj.max)
            else:
                raise NotImplementedError

    def __mul__(self, m):
        return BBox(m * self.min, m * self.max)

    __rmul__ = __mul__

    def __round__(self, n=None):
        return BBox(round(self.min), round(self.max))

    def intersects(self, bbox):
        return (
            (self.min.x < bbox.max.x)
            and (self.max.x > bbox.min.x)
            and (self.min.y < bbox.max.y)
            and (self.max.y > bbox.min.y)
        )

    def move(self, vector):
        """Move the corner points of a bounding box."""
        self.min += vector
        self.max += vector

    def resize(self, vector):
        """Expand/contract the bounding box by applying vector to its corner points."""
        self.min -= vector
        self.max += vector

    @property
    def area(self):
        """Return area of bounding box."""
        return self.w * self.h

    @property
    def w(self):
        """Return the bounding box width."""
        return abs(self.max.x - self.min.x)

    @property
    def h(self):
        """Return the bounding box height."""
        return abs(self.max.y - self.min.y)

    @property
    def ctr(self):
        """Return center point of bounding box."""
        return (self.max + self.min) / 2

    @property
    def ll(self):
        """Return lower-left point of bounding box."""
        return Point(self.min.x, self.min.y)

    @property
    def lr(self):
        """Return lower-right point of bounding box."""
        return Point(self.max.x, self.min.y)

    @property
    def ul(self):
        """Return upper-left point of bounding box."""
        return Point(self.min.x, self.max.y)

    @property
    def ur(self):
        """Return upper-right point of bounding box."""
        return Point(self.max.x, self.max.y)

    def dot(self, tx):
        """Apply transformation to a bounding box and return a bounding box."""
        return BBox(self.min.dot(tx), self.max.dot(tx))

    def __repr__(self):
        return "{self.__class__}({self.min}, {self.max})".format(self=self)


class Segment:
    def __init__(self, p1, p2):
        "Create a line segment between two points."
        self.p1 = copy(p1)
        self.p2 = copy(p2)

    def dot(self, tx):
        """Apply transformation matrix to a segment and return a segment."""
        return Segment(self.p1.dot(tx), self.p2.dot(tx))

    def intersects(self, other):
        """Return true if the segments intersect."""

        # Given two segments:
        #   self: p1 + (p2-p1) * t1
        #   other: p3 + (p4-p3) * t2
        # Look for a solution t1, t2 that solves:
        #   p1x + (p2x-p1x)*t1 = p3x + (p4x-p3x)*t2
        #   p1y + (p2y-p1y)*t1 = p3y + (p4y-p3y)*t2
        # If t1 and t2 are both in range [0,1], then the two segments intersect.

        p1x, p1y, p2x, p2y = self.p1.x, self.p1.y, self.p2.x, self.p2.y
        p3x, p3y, p4x, p4y = other.p1.x, other.p1.y, other.p2.x, other.p2.y

        # denom = p1x*p3y - p1x*p4y - p1y*p3x + p1y*p4x - p2x*p3y + p2x*p4y + p2y*p3x - p2y*p4x
        # denom = p1x * (p3y - p4y) + p1y * (p4x - p3x) + p2x * (p4y - p3y) + p2y * (p3x - p4x)
        denom = (p1x - p2x) * (p3y - p4y) + (p1y - p2y) * (p4x - p3x)

        try:
            # t1 = (p1x*p3y - p1x*p4y - p1y*p3x + p1y*p4x + p3x*p4y - p3y*p4x) / denom
            # t2 = (-p1x*p2y + p1x*p3y + p1y*p2x - p1y*p3x - p2x*p3y + p2y*p3x) / denom
            t1 = ((p1y - p3y) * (p4x - p3x) - (p1x - p3x) * (p4y - p3y)) / denom
            t2 = ((p1y - p3y) * (p2x - p3x) - (p1x - p3x) * (p2y - p3y)) / denom
        except ZeroDivisionError:
            return False

        return (0 <= t1 <= 1) and (0 <= t2 <= 1)
