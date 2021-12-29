# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""
Functions for handling KiCad symbols.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from builtins import int, range, zip
from collections import namedtuple

from future import standard_library

from ...logger import active_logger
from ...utilities import *
from .common import *
from .geometry import *

standard_library.install_aliases()


def calc_symbol_bbox(part):
    """
    Return the bounding box of the part symbol.

    Args:
        part: Part object for which an SVG symbol will be created.

    Returns: List of BBoxes for all units in the part symbol. 
    """

    def make_pin_dir_tbl(abs_xoff=20):

        # abs_xoff is the absolute distance of name/num from the end of the pin.
        rel_yoff_num = -0.15  # Relative distance of number above pin line.
        rel_yoff_name = (
            0.2  # Relative distance that places name midline even with pin line.
        )

        # Tuple for storing information about pins in each of four directions:
        #     direction: The direction the pin line is drawn from start to end.
        #     side: The side of the symbol the pin is on. (Opposite of the direction.)
        #     angle: The angle of the name/number text for the pin (usually 0, -90.).
        #     num_justify: Text justification of the pin number.
        #     name_justify: Text justification of the pin name.
        #     num_offset: (x,y) offset of the pin number w.r.t. the end of the pin.
        #     name_offset: (x,y) offset of the pin name w.r.t. the end of the pin.
        PinDir = namedtuple(
            "PinDir",
            "direction side angle num_justify name_justify num_offset name_offset net_offset",
        )

        return {
            "U": PinDir(
                Point(0, 1),
                "bottom",
                -90,
                "end",
                "start",
                Point(-abs_xoff, rel_yoff_num),
                Point(abs_xoff, rel_yoff_name),
                Point(abs_xoff, rel_yoff_num),
            ),
            "D": PinDir(
                Point(0, -1),
                "top",
                -90,
                "start",
                "end",
                Point(abs_xoff, rel_yoff_num),
                Point(-abs_xoff, rel_yoff_name),
                Point(-abs_xoff, rel_yoff_num),
            ),
            "L": PinDir(
                Point(-1, 0),
                "right",
                0,
                "start",
                "end",
                Point(abs_xoff, rel_yoff_num),
                Point(-abs_xoff, rel_yoff_name),
                Point(-abs_xoff, rel_yoff_num),
            ),
            "R": PinDir(
                Point(1, 0),
                "left",
                0,
                "end",
                "start",
                Point(-abs_xoff, rel_yoff_num),
                Point(abs_xoff, rel_yoff_name),
                Point(abs_xoff, rel_yoff_num),
            ),
        }

    default_pin_name_offset = 20

    # Go through each graphic object that makes up the component symbol.
    for obj in part.draw:

        obj_bbox = BBox()  # Bounding box of all the component objects.
        thickness = 0

        if isinstance(obj, DrawDef):
            def_ = obj
            # Make pin direction table with symbol-specific name offset.
            pin_dir_tbl = make_pin_dir_tbl(def_.name_offset or default_pin_name_offset)
            # Make structures for holding info on each part unit.
            num_units = def_.num_units
            unit_bboxes = [BBox() for _ in range(num_units + 1)]

        elif isinstance(obj, DrawF0):
            pass

        elif isinstance(obj, DrawF1):
            pass

        elif isinstance(obj, DrawArc):
            arc = obj
            center = Point(arc.cx, arc.cy)
            thickness = arc.thickness
            radius = arc.radius
            start = Point(arc.startx, arc.starty)
            end = Point(arc.endx, arc.endy)
            start_angle = arc.start_angle / 10
            end_angle = arc.end_angle / 10
            clock_wise = int(end_angle < start_angle)
            large_arc = int(abs(end_angle - start_angle) > 180)
            radius_pt = Point(radius, radius)
            obj_bbox.add(center - radius_pt)
            obj_bbox.add(center + radius_pt)

        elif isinstance(obj, DrawCircle):
            circle = obj
            center = Point(circle.cx, circle.cy)
            thickness = circle.thickness
            radius = circle.radius
            radius_pt = Point(radius, radius)
            obj_bbox.add(center - radius_pt)
            obj_bbox.add(center + radius_pt)

        elif isinstance(obj, DrawPoly):
            poly = obj
            thickness = obj.thickness
            pts = [
                Point(x, y)
                for x, y in zip(poly.points[0::2], poly.points[1::2])
            ]
            path = []
            for pt in pts:
                obj_bbox.add(pt)

        elif isinstance(obj, DrawRect):
            rect = obj
            thickness = obj.thickness
            start = Point(rect.x1, rect.y1)
            end = Point(rect.x2, rect.y2)
            obj_bbox.add(start)
            obj_bbox.add(end)

        elif isinstance(obj, DrawText):
            pass

        elif isinstance(obj, DrawPin):
            pin = obj

            try:
                visible = pin.shape[0] != "N"
            except IndexError:
                visible = True  # No pin shape given, so it is visible by default.

            if visible:
                # Draw pin if it's not invisible.

                # Create line for pin lead.
                dir = pin_dir_tbl[pin.orientation].direction
                start = Point(pin.x, pin.y)
                l = dir * pin.length
                end = start + l
                obj_bbox.add(start)
                obj_bbox.add(end)

        else:
            active_logger.error(
                "Unknown graphical object {} in part symbol {}.".format(
                    type(obj), part.name
                )
            )

        # Expand bounding box to account for object line thickness.
        obj_bbox.resize(Vector(round(thickness/2), round(thickness/2)))

        # Enter the current object into the SVG for this part.
        unit = getattr(obj, "unit", 0)
        if unit == 0:
            for bbox in unit_bboxes:
                bbox.add(obj_bbox)
        else:
            unit_bboxes[unit].add(obj_bbox)

    # End of loop through all the component objects.

    return unit_bboxes
