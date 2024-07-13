# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Calculate bounding boxes for part symbols and hierarchical sheets.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from builtins import range, str
import os
from builtins import int, range, zip
from collections import namedtuple

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from skidl.logger import active_logger
from skidl.schematics.geometry import (
    Tx,
    BBox,
    Point,
    Vector,
    tx_rot_0,
    tx_rot_90,
    tx_rot_180,
    tx_rot_270,
    mils_per_mm,
    mms_per_mil,
)
from skidl.utilities import export_to_all
from .constants import HIER_TERM_SIZE, PIN_LABEL_FONT_SIZE
from skidl.schematics.geometry import BBox, Point, Tx, Vector



@export_to_all
def calc_symbol_bbox(part, **options):
    """
    Return the bounding box of the part symbol.

    Args:
        part: Part object for which an SVG symbol will be created.
        options (dict): Various options to control bounding box calculation:
            graphics_only (boolean): If true, compute bbox of graphics (no text).

    Returns: List of BBoxes for all units in the part symbol.
    """

    def find(lst, key):
        """Find an sexpr clause with the given keyword."""
        for item in lst:
            if isinstance(item, (list, tuple)):
                if item[0].lower() == key:
                    return item
        return None

    default_pin_name_offset = 20

    # Go through each graphic object that makes up the component symbol.
    for unit_num, unit in part.unit.items():

        # Bounding box for this part unit.
        unit.bbox = BBox()

        # Process the drawing objects for each unit which are stored in a dict in the part.
        for obj in part.draw[unit_num]:

            # First item is the object type, and the remainder are object parameters.
            obj_type = obj[0].lower()
            obj_params = obj[1:]

            if obj_type == "reference" and not options.get("graphics_only", False):
                raise NotImplementedError

                # obj attributes: x y size orientation visibility halign valign
                # Skip if the object is invisible.
                if obj.visibility.upper() == "I":
                    continue

                # Calculate length and height of part reference.
                # Use ref from the SKiDL part since the ref in the KiCAD part
                # hasn't been updated from its generic value.
                length = len(part.ref) * obj.size
                height = obj.size

                # Create bbox with lower-left point at (0, 0).
                bbox = BBox(Point(0,0), Point(length, height))

                # Rotate bbox around origin.
                rot_tx = {"H": Tx(), "V": tx_rot_90}[obj.orientation.upper()]
                bbox *= rot_tx

                # Horizontally align bbox.
                halign = obj.halign.upper()
                if halign == "L":
                    pass
                elif halign == "R":
                    bbox *= Tx().move(Point(-bbox.w, 0))
                elif halign == "C":
                    bbox *= Tx().move(Point(-bbox.w/2, 0))
                else:
                    raise Exception("Inconsistent horizontal alignment: {}".format(halign))

                # Vertically align bbox.
                valign = obj.valign[:1].upper() # valign is first letter.
                if valign == "B":
                    pass
                elif valign == "T":
                    bbox *= Tx().move(Point(0, -bbox.h))
                elif valign == "C":
                    bbox *= Tx().move(Point(0, -bbox.h/2))
                else:
                    raise Exception("Inconsistent vertical alignment: {}".format(valign))
                
                bbox *= Tx().move(Point(obj.x, obj.y))
                obj_bbox.add(bbox)

            elif obj_type == "value" and not options.get("graphics_only", False):
                raise NotImplementedError
            
                # Skip if the object is invisible.
                if obj.visibility.upper() == "I":
                    continue

                # Calculate length and height of part value.
                # Use value from the SKiDL part since the value in the KiCAD part
                # hasn't been updated from its generic value.
                length = len(str(part.value)) * obj.size
                height = obj.size

                # Create bbox with lower-left point at (0, 0).
                bbox = BBox(Point(0,0), Point(length, height))

                # Rotate bbox around origin.
                rot_tx = {"H": Tx(), "V": tx_rot_90}[obj.orientation.upper()]
                bbox *= rot_tx

                # Horizontally align bbox.
                halign = obj.halign.upper()
                if halign == "L":
                    pass
                elif halign == "R":
                    bbox *= Tx().move(Point(-bbox.w, 0))
                elif halign == "C":
                    bbox *= Tx().move(Point(-bbox.w/2, 0))
                else:
                    raise Exception("Inconsistent horizontal alignment: {}".format(halign))

                # Vertically align bbox.
                valign = obj.valign[:1].upper() # valign is first letter.
                if valign == "B":
                    pass
                elif valign == "T":
                    bbox *= Tx().move(Point(0, -bbox.h))
                elif valign == "C":
                    bbox *= Tx().move(Point(0, -bbox.h/2))
                else:
                    raise Exception("Inconsistent vertical alignment: {}".format(valign))
                
                bbox *= Tx().move(Point(obj.x, obj.y))
                obj_bbox.add(bbox)

            elif obj_type == "arc":
                start = find(obj_params, "start")
                start_pt = Point(start[1], start[2])
                mid = find(obj_params, "mid")
                mid_pt = Point(mid[1], mid[2])
                end = find(obj_params, "end")
                end_pt = Point(end[end[1], end[2]])
                unit_bbox.add(start_pt, mid_pt, end_pt)

            elif obj_type == "circle":
                center = find(obj_params, "center")
                center_pt = Point(center[1], center[2])
                radius = find(obj_params, "radius")
                radius = radius[1]
                radius_pt = Point(radius, radius)
                unit.bbox.add(center_pt + radius_pt, center_pt - radius_pt)

            elif obj_type == "polyline":
                pts = find(obj_params, "pts")
                obj_bbox = BBox()
                for pt in pts[1:]:
                    unit.bbox.add(Point(pt[1], pt[2]))

            elif obj_type == "rectangle":
                start = find(obj_params, "start")
                start_pt = Point(start[1], start[2])
                end = find(obj_params, "end")
                end_pt = Point(end[1], end[2])
                unit.bbox.add(start_pt, end_pt)

            elif obj_type == "text" and not options.get("graphics_only", False):
                pass

            elif obj_type == "pin":
                if "hide" not in obj_params:
                    x, y, angle = find(obj_params, "at")[1:4]
                    length = find(obj_params, "length")[1]
                    pt1 = Point(x, y)
                    pt2 = pt1 + Point(length, 0) * Tx().rot(angle)
                    unit.bbox.add(pt1, pt2)
                    # TODO: Add pin number and name to bbox.

            else:
                active_logger.error(
                    "Unknown graphical object {} in part symbol {}.".format(
                        obj_type, part.name
                    )
                )

        # After the unit bounding box is calculated, change it from mm to mils.
        unit.bbox *= mils_per_mm
        unit.bbox = unit.bbox.round()


@export_to_all
def calc_hier_label_bbox(label, dir):
    """Calculate the bounding box for a hierarchical label.

    Args:
        label (str): String for the label.
        dir (str): Orientation ("U", "D", "L", "R").

    Returns:
        BBox: Bounding box for the label and hierarchical terminal.
    """

    raise NotImplementedError

    # Rotation matrices for each direction.
    lbl_tx = {
        "U": tx_rot_90,  # Pin on bottom pointing upwards.
        "D": tx_rot_270,  # Pin on top pointing down.
        "L": tx_rot_180,  # Pin on right pointing left.
        "R": tx_rot_0,  # Pin on left pointing right.
    }

    # Calculate length and height of label + hierarchical marker.
    lbl_len = len(label) * PIN_LABEL_FONT_SIZE + HIER_TERM_SIZE
    lbl_hgt = max(PIN_LABEL_FONT_SIZE, HIER_TERM_SIZE)

    # Create bbox for label on left followed by marker on right.
    bbox = BBox(Point(0, lbl_hgt / 2), Point(-lbl_len, -lbl_hgt / 2))

    # Rotate the bbox in the given direction.
    bbox *= lbl_tx[dir]

    return bbox
