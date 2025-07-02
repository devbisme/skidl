# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Geometric primitives and transformations for SKiDL.

This module provides classes and functions to handle geometric operations needed for
positioning and transforming components. It includes support for
points/vectors, transformation matrices, and unit conversions between millimeters
and thousandths-of-inch (mils).
"""

from math import sqrt, sin, cos, radians
from copy import copy

from .utilities import export_to_all

__all__ = [
    "mms_per_mil",
    "mils_per_mm",
    "Vector",
    "tx_rot_0",
    "tx_rot_90",
    "tx_rot_180",
    "tx_rot_270",
    "tx_flip_x",
    "tx_flip_y",
]


# Millimeters/thousandths-of-inch conversion factor.
mils_per_mm = 39.37008
mms_per_mil = 0.0254


@export_to_all
def to_mils(mm):
    """
    Convert millimeters to thousandths-of-inch (mils).
    
    Args:
        mm (float): Value in millimeters.
        
    Returns:
        float: Equivalent value in mils.
    """
    return mm * mils_per_mm


@export_to_all
def to_mms(mils):
    """
    Convert thousandths-of-inch (mils) to millimeters.
    
    Args:
        mils (float): Value in mils.
        
    Returns:
        float: Equivalent value in millimeters.
    """
    return mils * mms_per_mil


@export_to_all
class Tx:
    """
    A 2D transformation matrix for geometric operations.
    
    This class implements a 3x3 transformation matrix for 2D operations
    like rotation, scaling, flipping, and translation. The matrix has
    the following structure:
    
    [ a  b  0 ]
    [ c  d  0 ]
    [ dx dy 1 ]
    
    Where the transformed coordinates are calculated as:
    x' = a*x + c*y + dx
    y' = b*x + d*y + dy
    
    Args:
        a (float, optional): Scaling/rotation factor for x coordinate. Defaults to 1.
        b (float, optional): Rotation factor for y contribution to x. Defaults to 0.
        c (float, optional): Rotation factor for x contribution to y. Defaults to 0.
        d (float, optional): Scaling/rotation factor for y coordinate. Defaults to 1.
        dx (float, optional): Translation in x direction. Defaults to 0.
        dy (float, optional): Translation in y direction. Defaults to 0.
    """
    
    def __init__(self, a=1, b=0, c=0, d=1, dx=0, dy=0):
        """
        Create a transformation matrix.
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

    @classmethod
    def from_symtx(cls, symtx):
        """
        Create a transformation matrix from a string of symbolic operations.
        
        Args:
            symtx (str): A string of H, V, L, R operations that are applied in sequence left-to-right.
                        H = horizontal flip, V = vertical flip, 
                        L = rotate 90° left (CCW), R = rotate 90° right (CW)
                        
        Returns:
            Tx: A transformation matrix that implements the sequence of operations.
            
        Examples:
            >>> tx = Tx.from_symtx("RH")  # Rotate right, then flip horizontally
        """
        op_dict = {
            "H": Tx(a=-1, c=0, b=0, d=1),  # Horizontal flip.
            "V": Tx(a=1, c=0, b=0, d=-1),  # Vertical flip.
            "L": Tx(a=0, c=-1, b=1, d=0),  # Rotate 90 degrees left (counter-clockwise).
            "R": Tx(a=0, c=1, b=-1, d=0),  # Rotate 90 degrees right (clockwise).
        }

        tx = Tx()
        for op in symtx.upper():
            tx *= op_dict[op]
        return tx

    def __repr__(self):
        """
        Return a string representation of the transformation matrix.
        
        Returns:
            str: String showing the class name and transformation parameters.
        """
        return f"{type(self)}({self.a}, {self.b}, {self.c}, {self.d}, {self.dx}, {self.dy})"

    def __str__(self):
        """
        Return a simplified string representation of the transformation matrix.
        
        Returns:
            str: String showing the transformation parameters in a list format.
        """
        return f"[{self.a}, {self.b}, {self.c}, {self.d}, {self.dx}, {self.dy}]"

    def __mul__(self, m):
        """
        Multiply this transformation matrix by another matrix or scalar.
        
        If m is another transformation matrix, the matrices are multiplied.
        If m is a scalar, it scales the matrix uniformly.
        
        Args:
            m: Another Tx object or a scalar.
            
        Returns:
            Tx: The resulting transformation matrix.
        """
        if isinstance(m, Tx):
            tx = m
        else:
            # Assume m is a scalar, so convert it to a scaling Tx matrix.
            tx = Tx(a=m, d=m)
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
        """
        Get the translation component of the transformation.
        
        Returns:
            Point: A Point object representing the (dx, dy) translation.
        """
        return Point(self.dx, self.dy)

    # This setter doesn't work in Python 2.7.18.
    # @origin.setter
    # def origin(self, pt):
    #     """Set the (dx, dy) translation from an (x,y) Point."""
    #     self.dx, self.dy = pt.x, pt.y

    @property
    def scale(self):
        """
        Get the scaling factor of the transformation.
        
        This calculates the length of a unit vector after transformation.
        
        Returns:
            float: The scaling factor.
        """
        return (Point(1, 0) * self - Point(0, 0) * self).magnitude

    def move(self, vec):
        """
        Return a new Tx with an additional translation applied.
        
        Args:
            vec (Point): The vector to translate by.
            
        Returns:
            Tx: A new transformation matrix with the translation applied.
        """
        return self * Tx(dx=vec.x, dy=vec.y)

    def rot_90cw(self):
        """
        Return a new Tx with a 90-degree clockwise rotation applied.
        
        Returns:
            Tx: A new transformation matrix with the rotation applied.
        """
        return self * Tx(a=0, b=1, c=-1, d=0)

    def rot(self, degs):
        """
        Return a new Tx with a rotation by the given angle in degrees.
        
        Args:
            degs (float): The rotation angle in degrees.
            
        Returns:
            Tx: A new transformation matrix with the rotation applied.
        """
        rads = radians(degs)
        return self * Tx(a=cos(rads), b=sin(rads), c=-sin(rads), d=cos(rads))

    def flip_x(self):
        """
        Return a new Tx with a horizontal flip (mirror across y-axis).
        
        Returns:
            Tx: A new transformation matrix with the flip applied.
        """
        return self * Tx(a=-1)

    def flip_y(self):
        """
        Return a new Tx with a vertical flip (mirror across x-axis).
        
        Returns:
            Tx: A new transformation matrix with the flip applied.
        """
        return self * Tx(d=-1)

    def no_translate(self):
        """
        Return a new Tx with the same rotation/scaling but no translation.
        
        Returns:
            Tx: A new transformation matrix with translation set to (0,0).
        """
        return Tx(a=self.a, b=self.b, c=self.c, d=self.d)


# Some common rotations.
tx_rot_0 = Tx(a=1, b=0, c=0, d=1)
tx_rot_90 = Tx(a=0, b=1, c=-1, d=0)
tx_rot_180 = Tx(a=-1, b=0, c=0, d=-1)
tx_rot_270 = Tx(a=0, b=-1, c=1, d=0)

# Some common flips.
tx_flip_x = Tx(a=-1, b=0, c=0, d=1)
tx_flip_y = Tx(a=1, b=0, c=0, d=-1)


@export_to_all
class Point:
    """
    A 2D point or vector with x and y coordinates.
    
    The Point class represents both points in space and vectors for
    geometric operations. It supports various arithmetic operations
    and can be transformed using the Tx transformation matrix.
    
    Args:
        x (float): The x-coordinate.
        y (float): The y-coordinate.
    """
    
    def __init__(self, x, y):
        """Create a Point with coords x,y."""
        self.x = x
        self.y = y

    def __hash__(self):
        """
        Generate a hash value for the point.
        
        Returns:
            int: Hash value based on the x and y coordinates.
        """
        return hash((self.x, self.y))

    def __eq__(self, other):
        """
        Check if two points have the same coordinates.
        
        Args:
            other (Point): Another point to compare with.
            
        Returns:
            bool: True if both points have the same coordinates.
        """
        return (self.x, self.y) == (other.x, other.y)

    def __lt__(self, other):
        """
        Compare points lexicographically (first by x, then by y).
        
        Args:
            other (Point): Another point to compare with.
            
        Returns:
            bool: True if self is less than other.
        """
        return (self.x, self.y) < (other.x, other.y)

    def __ne__(self, other):
        """
        Check if two points have different coordinates.
        
        Args:
            other (Point): Another point to compare with.
            
        Returns:
            bool: True if points have different coordinates.
        """
        return not (self == other)

    def __add__(self, pt):
        """
        Add another point or scalar to this point.
        
        Args:
            pt (Point or number): Point or scalar to add.
            
        Returns:
            Point: A new point with the sum of coordinates.
        """
        if not isinstance(pt, Point):
            pt = Point(pt, pt)
        return Point(self.x + pt.x, self.y + pt.y)

    def __sub__(self, pt):
        """
        Subtract another point or scalar from this point.
        
        Args:
            pt (Point or number): Point or scalar to subtract.
            
        Returns:
            Point: A new point with the difference of coordinates.
        """
        if not isinstance(pt, Point):
            pt = Point(pt, pt)
        return Point(self.x - pt.x, self.y - pt.y)

    def __mul__(self, m):
        """
        Multiply this point by a transformation, another point, or a scalar.
        
        Args:
            m: A Tx transformation, another Point (for component-wise multiplication),
               or a scalar.
               
        Returns:
            Point: The transformed/scaled point.
        """
        if isinstance(m, Tx):
            return Point(
                self.x * m.a + self.y * m.c + m.dx, self.x * m.b + self.y * m.d + m.dy
            )
        elif isinstance(m, Point):
            return Point(self.x * m.x, self.y * m.y)
        else:
            return Point(m * self.x, m * self.y)

    def __rmul__(self, m):
        """
        Right multiplication with a scalar.
        
        Args:
            m: A scalar value.
            
        Returns:
            Point: Scaled point.
            
        Raises:
            ValueError: If m is a Tx transformation matrix.
        """
        if isinstance(m, Tx):
            raise ValueError
        else:
            return self * m

    def xprod(self, pt):
        """
        Calculate the cross product of this vector and another.
        
        For 2D vectors, the cross product returns a scalar representing
        the z-component of the 3D cross product.
        
        Args:
            pt (Point): Another point/vector.
            
        Returns:
            float: The cross product value.
        """
        return self.x * pt.y - self.y * pt.x

    def mask(self, msk):
        """
        Apply a binary mask to the coordinates.
        
        Args:
            msk (list or tuple): A pair of values to multiply with x and y.
            
        Returns:
            Point: New point with masked coordinates.
        """
        return Point(self.x * msk[0], self.y * msk[1])

    def __neg__(self):
        """
        Negate both coordinates.
        
        Returns:
            Point: A new point with negated coordinates.
        """
        return Point(-self.x, -self.y)

    def __truediv__(self, d):
        """
        Divide coordinates by a scalar.
        
        Args:
            d (number): Divisor.
            
        Returns:
            Point: New point with divided coordinates.
        """
        return Point(self.x / d, self.y / d)

    def __div__(self, d):
        """
        Divide coordinates by a scalar (Python 2 compatibility).
        
        Args:
            d (number): Divisor.
            
        Returns:
            Point: New point with divided coordinates.
        """
        return Point(self.x / d, self.y / d)

    def round(self):
        """
        Round coordinates to nearest integers.
        
        Returns:
            Point: New point with rounded coordinates.
        """
        return Point(int(round(self.x)), int(round(self.y)))

    def __str__(self):
        """
        Convert point to a space-separated string representation.
        
        Returns:
            str: String with x and y coordinates.
        """
        return f"{self.x} {self.y}"

    def snap(self, grid_spacing):
        """
        Snap point coordinates to a grid.
        
        Args:
            grid_spacing (float): Grid interval to snap to.
            
        Returns:
            Point: New point with coordinates snapped to the grid.
        """
        snap_func = lambda x: int(grid_spacing * round(x / grid_spacing))
        return Point(snap_func(self.x), snap_func(self.y))

    def min(self, pt):
        """
        Create a new point using the minimum x and y from two points.
        
        Args:
            pt (Point): Another point to compare with.
            
        Returns:
            Point: New point with minimum x and y values.
        """
        return Point(min(self.x, pt.x), min(self.y, pt.y))

    def max(self, pt):
        """
        Create a new point using the maximum x and y from two points.
        
        Args:
            pt (Point): Another point to compare with.
            
        Returns:
            Point: New point with maximum x and y values.
        """
        return Point(max(self.x, pt.x), max(self.y, pt.y))

    @property
    def magnitude(self):
        """
        Calculate the distance of the point from origin (vector length).
        
        Returns:
            float: The Euclidean distance from origin.
        """
        return sqrt(self.x**2 + self.y**2)

    @property
    def norm(self):
        """
        Calculate a unit vector in the same direction.
        
        Returns:
            Point: Normalized vector with length 1, or (0,0) if zero length.
        """
        try:
            return self / self.magnitude
        except ZeroDivisionError:
            return Point(0, 0)

    def flip_xy(self):
        """
        Swap the x and y coordinates in place.
        """
        self.x, self.y = self.y, self.x

    def __repr__(self):
        """
        Return a string representation for debugging.
        
        Returns:
            str: String with class name and x,y coordinates.
        """
        return f"{type(self)}({self.x}, {self.y})"


Vector = Point


@export_to_all
class BBox:
    """
    A bounding box defined by minimum and maximum points.
    
    BBox represents a rectangular area that can contain points or other bounding boxes.
    It provides methods for combining bounding boxes, testing if points are inside,
    and calculating intersections.
    
    Args:
        *pts: One or more Point objects defining the initial bounding box.
    """
    
    def __init__(self, *pts):
        """Create a bounding box surrounding the given points."""
        inf = float("inf")
        self.min = Point(inf, inf)
        self.max = Point(-inf, -inf)
        self.add(*pts)

    def __add__(self, obj):
        """
        Merge this bounding box with a point or another bounding box.
        
        Args:
            obj (Point or BBox): Object to merge with.
            
        Returns:
            BBox: A new bounding box that contains both this bbox and the object.
            
        Raises:
            NotImplementedError: If obj is not a Point or BBox.
        """
        sum_ = BBox()
        if isinstance(obj, Point):
            sum_.min = self.min.min(obj)
            sum_.max = self.max.max(obj)
        elif isinstance(obj, BBox):
            sum_.min = self.min.min(obj.min)
            sum_.max = self.max.max(obj.max)
        else:
            raise NotImplementedError
        return sum_

    def __iadd__(self, obj):
        """
        Expand this bounding box to include a point or another bounding box.
        
        Args:
            obj (Point or BBox): Object to include in this bbox.
            
        Returns:
            BBox: The updated bounding box (self).
        """
        sum_ = self + obj
        self.min = sum_.min
        self.max = sum_.max
        return self

    def add(self, *objs):
        """
        Update the bounding box to include multiple points and/or bounding boxes.
        
        Args:
            *objs: Points or BBoxes to include in this bounding box.
            
        Returns:
            BBox: The updated bounding box (self).
        """
        for obj in objs:
            self += obj
        return self

    def __mul__(self, m):
        """
        Apply a transformation to this bounding box.
        
        Args:
            m (Tx): Transformation matrix to apply.
            
        Returns:
            BBox: A new transformed bounding box.
        """
        return BBox(self.min * m, self.max * m)

    def round(self):
        """
        Round the bounding box limits to integers.
        
        Returns:
            BBox: A new bounding box with rounded coordinates.
        """
        return BBox(self.min.round(), self.max.round())

    def is_inside(self, pt):
        """
        Check if a point is inside or on the boundary of this bounding box.
        
        Args:
            pt (Point): The point to check.
            
        Returns:
            bool: True if the point is inside or on the boundary.
        """
        return (self.min.x <= pt.x <= self.max.x) and (self.min.y <= pt.y <= self.max.y)

    def intersects(self, bbox):
        """
        Check if this bounding box intersects with another.
        
        Args:
            bbox (BBox): Another bounding box to check for intersection.
            
        Returns:
            bool: True if the bounding boxes intersect.
        """
        return (
            (self.min.x < bbox.max.x)
            and (self.max.x > bbox.min.x)
            and (self.min.y < bbox.max.y)
            and (self.max.y > bbox.min.y)
        )

    def intersection(self, bbox):
        """
        Calculate the intersection of this bounding box with another.
        
        Args:
            bbox (BBox): Another bounding box.
            
        Returns:
            BBox or None: A new bounding box representing the intersection,
                         or None if there is no intersection.
        """
        if not self.intersects(bbox):
            return None
        corner1 = self.min.max(bbox.min)
        corner2 = self.max.min(bbox.max)
        return BBox(corner1, corner2)

    def resize(self, vector):
        """
        Expand or contract the bounding box by a given amount in all directions.
        
        Args:
            vector (Point): Amount to expand by (positive values) or contract by 
                          (negative values) in x and y directions.
                          
        Returns:
            BBox: A new resized bounding box.
        """
        return BBox(self.min - vector, self.max + vector)

    def snap_resize(self, grid_spacing):
        """
        Resize the bounding box to align min and max points to a grid.
        
        This expands the bounding box outward so that its corners align with
        the given grid spacing.
        
        Args:
            grid_spacing (float): Grid spacing to align to.
            
        Returns:
            BBox: A new bounding box with grid-aligned corners.
        """
        bbox = self.resize(Point(grid_spacing - 1, grid_spacing - 1))
        bbox.min = bbox.min.snap(grid_spacing)
        bbox.max = bbox.max.snap(grid_spacing)
        return bbox

    @property
    def area(self):
        """
        Calculate the area of the bounding box.
        
        Returns:
            float: Area (width × height).
        """
        return self.w * self.h

    @property
    def w(self):
        """Return the bounding box width."""
        return abs(self.max.x - self.min.x)

    @property
    def h(self):
        """
        Get the height of the bounding box.
        
        Returns:
            float: Height of the bounding box.
        """
        return abs(self.max.y - self.min.y)

    @property
    def ctr(self):
        """
        Get the center point of the bounding box.
        
        Returns:
            Point: Center point.
        """
        return (self.max + self.min) / 2

    @property
    def ll(self):
        """
        Get the lower-left corner of the bounding box.
        
        Returns:
            Point: Lower-left corner point.
        """
        return Point(self.min.x, self.min.y)

    @property
    def lr(self):
        """
        Get the lower-right corner of the bounding box.
        
        Returns:
            Point: Lower-right corner point.
        """
        return Point(self.max.x, self.min.y)

    @property
    def ul(self):
        """
        Get the upper-left corner of the bounding box.
        
        Returns:
            Point: Upper-left corner point.
        """
        return Point(self.min.x, self.max.y)

    @property
    def ur(self):
        """
        Get the upper-right corner of the bounding box.
        
        Returns:
            Point: Upper-right corner point.
        """
        return Point(self.max.x, self.max.y)

    def __repr__(self):
        """
        Return a string representation for debugging.
        
        Returns:
            str: String showing the class name and min/max points.
        """
        return f"{type(self)}(Point({self.min}), Point({self.max}))"

    def __str__(self):
        """
        Return a simplified string representation.
        
        Returns:
            str: String representation of the min/max points.
        """
        return f"[{self.min}, {self.max}]"


@export_to_all
class Segment:
    """
    A line segment between two points.
    
    Represents a straight line segment with endpoints p1 and p2.
    
    Args:
        p1 (Point): First endpoint.
        p2 (Point): Second endpoint.
    """
    
    def __init__(self, p1, p2):
        """Create a line segment between two points."""
        self.p1 = copy(p1)
        self.p2 = copy(p2)

    def __mul__(self, m):
        """
        Apply a transformation to the segment.
        
        Args:
            m (Tx): Transformation matrix to apply.
            
        Returns:
            Segment: A new transformed segment.
        """
        return Segment(self.p1 * m, self.p2 * m)

    def round(self):
        """
        Round the segment endpoints to integers.
        
        Returns:
            Segment: A new segment with rounded endpoint coordinates.
        """
        return Segment(self.p1.round(), self.p2.round())

    def __str__(self):
        """
        Return a string representation of the segment.
        
        Returns:
            str: String with the segment endpoints.
        """
        return f"{str(self.p1)} {str(self.p2)}"

    def flip_xy(self):
        """
        Swap the x and y coordinates of both endpoints.
        """
        self.p1.flip_xy()
        self.p2.flip_xy()

    def intersects(self, other):
        """
        Check if this segment intersects with another segment.
        
        Note: This method is not fully implemented and will raise an error.
        
        Args:
            other (Segment): Another segment to check for intersection.
            
        Raises:
            NotImplementedError: This method is not fully implemented.
        """

        # FIXME: This fails if the segments are parallel!
        raise NotImplementedError

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

    def shadows(self, other):
        """
        Check if two segments overlap when projected onto axes.
        
        This tests if the segments would overlap when viewed from above or the side,
        even if they don't physically intersect.
        
        Args:
            other (Segment): Another segment to check.
            
        Returns:
            bool: True if segments shadow (overlap) each other on x or y axis.
        """

        if self.p1.x == self.p2.x and other.p1.x == other.p2.x:
            # Horizontal segments. See if their vertical extents overlap.
            self_min = min(self.p1.y, self.p2.y)
            self_max = max(self.p1.y, self.p2.y)
            other_min = min(other.p1.y, other.p2.y)
            other_max = max(other.p1.y, other.p2.y)
        elif self.p1.y == self.p2.y and other.p1.y == other.p2.y:
            # Verttical segments. See if their horizontal extents overlap.
            self_min = min(self.p1.x, self.p2.x)
            self_max = max(self.p1.x, self.p2.x)
            other_min = min(other.p1.x, other.p2.x)
            other_max = max(other.p1.x, other.p2.x)
        else:
            # Segments aren't horizontal or vertical, so neither can shadow the other.
            return False

        # Overlap conditions based on segment endpoints.
        return other_min < self_max and other_max > self_min
