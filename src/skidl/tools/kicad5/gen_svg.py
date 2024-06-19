# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Functions for generating SVG.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from builtins import range, str
from builtins import int, range, zip
from collections import namedtuple

try:
    from future import standard_library

    standard_library.install_aliases()
except ImportError:
    pass

from skidl.logger import active_logger
from skidl.utilities import export_to_all
from .draw_objs import *
from skidl.schematics.geometry import BBox, Point


@export_to_all
def gen_svg_comp(part, symtx, net_stubs=None):
    """
    Generate SVG for this component.

    Args:
        part: Part object for which an SVG symbol will be created.
        net_stubs: List of Net objects whose names will be connected to
            part symbol pins as connection stubs.
        symtx: String such as "HR" that indicates symbol mirroring/rotation.

    Returns: SVG for the part symbol."""

    def tx(obj, ops):
        """Transform Point, number, or direction according to the list of opcodes."""

        def H(obj):
            # Flip horizontally.
            if isinstance(obj, Point):
                return Point(-obj.x, obj.y)
            if isinstance(obj, (float, int)):
                return 180.0 - obj
            else:
                return {"U": "U", "D": "D", "L": "R", "R": "L"}[obj]

        def V(obj):
            # Flip vertically.
            if isinstance(obj, Point):
                return Point(obj.x, -obj.y)
            if isinstance(obj, (float, int)):
                return -obj
            else:
                return {"U": "D", "D": "U", "L": "L", "R": "R"}[obj]

        def R(obj):
            # Rotate right.
            if isinstance(obj, Point):
                return Point(-obj.y, obj.x)
            if isinstance(obj, (float, int)):
                return obj + 90.0
            else:
                return {"U": "R", "D": "L", "L": "U", "R": "D"}[obj]

        def L(obj):
            # Rotate left.
            if isinstance(obj, Point):
                return Point(obj.y, -obj.x)
            if isinstance(obj, (float, int)):
                return obj - 90.0
            else:
                return {"U": "L", "D": "R", "L": "D", "R": "U"}[obj]

        # Each character in ops applies a geometrical transformation.
        for op in ops:
            obj = locals()[op.upper()](obj)  # op selects the H, V, L, or R subroutine.
        return obj

    def draw_text(text, size, justify, origin, rotation, offset, class_, extra=""):
        return " ".join(
            [
                "<text",
                "class='{class_}'",
                "text-anchor='{justify}'",
                "x='{origin.x}' y='{origin.y}'",
                "transform='rotate({rotation} {origin.x} {origin.y}) translate({offset.x} {offset.y})'",
                "style='font-size:{size}px'",
                "{extra}",
                ">",
                "{text}",
                "</text>",
            ]
        ).format(**locals())

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
                Point(0, -1),
                "bottom",
                -90,
                "end",
                "start",
                Point(-abs_xoff, rel_yoff_num),
                Point(abs_xoff, rel_yoff_name),
                Point(abs_xoff, rel_yoff_num),
            ),
            "D": PinDir(
                Point(0, 1),
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

    fill_tbl = {"f": "background_fill", "F": "pen_fill", "N": ""}

    scale = 0.30  # Scale of KiCad units to SVG units.
    default_thickness = 1 / scale  # Default line thickness = 1.
    default_pin_name_offset = 20

    # Named tuple for storing component pin information.
    PinInfo = namedtuple("PinInfo", "x y side pid")

    # Get maximum length of net stub name if any are needed for this part symbol.
    net_stubs = net_stubs or []  # Empty list of stub nets if argument is None.
    max_stub_len = 0  # If no net stubs are needed, this stays at zero.
    for pin in part:
        for net in pin.nets:
            # Don't let names for no-connect nets affect maximum stub length.
            if net in [NC, None]:
                continue
            if net in net_stubs:
                max_stub_len = max(len(net.name), max_stub_len)

    # Go through each graphic object that makes up the component symbol.
    for obj in part.draw:

        obj_pin_info = (
            []
        )  # Component pin info so they can be generated once bbox is known.
        obj_svg = []  # Component graphic objects.
        obj_filled_svg = []  # Filled component graphic objects.
        obj_txt_svg = []  # Component text (because it has to be drawn last).
        obj_bbox = BBox()  # Bounding box of all the component objects.

        if isinstance(obj, DrawDef):
            def_ = obj
            show_name = type(def_.name) is int or def_.name[0] != "~"
            show_nums = def_.show_nums == "Y"
            show_names = def_.show_names == "Y"
            # Make pin direction table with symbol-specific name offset.
            pin_dir_tbl = make_pin_dir_tbl(def_.name_offset or default_pin_name_offset)
            # Make structures for holding info on each part unit.
            num_units = def_.num_units
            unit_pin_info = [[] for _ in range(num_units + 1)]
            unit_svg = [[] for _ in range(num_units + 1)]
            unit_filled_svg = [[] for _ in range(num_units + 1)]
            unit_txt_svg = [[] for _ in range(num_units + 1)]
            unit_bbox = [BBox() for _ in range(num_units + 1)]

        elif isinstance(obj, DrawF0):
            f0 = obj
            if f0.visibility != "I":
                # F0 field is not invisible.
                origin = tx(Point(f0.x, -f0.y), symtx) * scale
                orientation = f0.orientation + f0.halign
                dir = {
                    "HL": "L",
                    "HC": "L",
                    "HR": "R",
                    "VL": "D",
                    "VC": "D",
                    "VR": "U",
                }[orientation]
                dir = tx(dir, symtx)
                angle = pin_dir_tbl[dir].angle
                size = f0.size * scale
                justify = "middle" if f0.halign == "C" else pin_dir_tbl[dir].num_justify
                offset = (
                    tx(
                        {"T": Point(0, 1), "B": Point(0, 0), "C": Point(0, 0.5)}[
                            f0.valign[0]
                        ],
                        symtx,
                    )
                    * size
                )
                class_ = "part_ref_text"
                extra = 's:attribute="ref"'
                obj_txt_svg.append(
                    draw_text("X", size, justify, origin, angle, offset, class_, extra)
                )

        elif isinstance(obj, DrawF1):
            f1 = obj
            if f1.visibility != "I" and show_name:
                # F1 field is not invisible.
                origin = tx(Point(f1.x, -f1.y), symtx) * scale
                orientation = f1.orientation + f1.halign
                dir = {
                    "HL": "L",
                    "HC": "L",
                    "HR": "R",
                    "VL": "D",
                    "VC": "D",
                    "VR": "U",
                }[orientation]
                dir = tx(dir, symtx)
                angle = pin_dir_tbl[dir].angle
                size = f1.size * scale
                justify = "middle" if f1.halign == "C" else pin_dir_tbl[dir].num_justify
                offset = (
                    tx(
                        {"T": Point(0, 1), "B": Point(0, 0), "C": Point(0, 0.5)}[
                            f1.valign[0]
                        ],
                        symtx,
                    )
                    * size
                )
                class_ = "part_name_text"
                extra = 's:attribute="value"'
                obj_txt_svg.append(
                    draw_text("X", size, justify, origin, angle, offset, class_, extra)
                )

        elif isinstance(obj, DrawArc):
            arc = obj
            center = tx(Point(arc.cx, -arc.cy), symtx) * scale
            radius = arc.radius * scale
            start = tx(Point(arc.startx, -arc.starty), symtx) * scale
            end = tx(Point(arc.endx, -arc.endy), symtx) * scale
            start_angle = tx(arc.start_angle / 10, symtx)
            end_angle = tx(arc.end_angle / 10, symtx)
            clock_wise = int(end_angle < start_angle)
            large_arc = int(abs(end_angle - start_angle) > 180)
            thickness = (arc.thickness or default_thickness) * scale
            fill = fill_tbl.get(arc.fill, "")
            radius_pt = Point(radius, radius)
            obj_bbox.add(center - radius_pt)
            obj_bbox.add(center + radius_pt)
            svg = obj_filled_svg if fill else obj_svg
            svg.append(
                " ".join(
                    [
                        "<path",
                        'd="M {start.x} {start.y} A {radius} {radius} 0 {large_arc} {clock_wise} {end.x} {end.y}"',
                        'style="stroke-width:{thickness}"',
                        'class="$cell_id symbol {fill}"',
                        "/>",
                    ]
                ).format(**locals())
            )

        elif isinstance(obj, DrawCircle):
            circle = obj
            center = tx(Point(circle.cx, -circle.cy), symtx) * scale
            radius = circle.radius * scale
            thickness = (circle.thickness or default_thickness) * scale
            fill = fill_tbl.get(circle.fill, "")
            radius_pt = Point(radius, radius)
            obj_bbox.add(center - radius_pt)
            obj_bbox.add(center + radius_pt)
            svg = obj_filled_svg if fill else obj_svg
            svg.append(
                " ".join(
                    [
                        "<circle",
                        'cx="{center.x}" cy="{center.y}" r="{radius}"',
                        'style="stroke-width:{thickness}"',
                        'class="$cell_id symbol {fill}"',
                        "/>",
                    ]
                ).format(**locals())
            )

        elif isinstance(obj, DrawPoly):
            poly = obj
            pts = [
                tx(Point(x, -y), symtx) * scale
                for x, y in zip(poly.points[0::2], poly.points[1::2])
            ]
            path = []
            path_op = "M"
            for pt in pts:
                obj_bbox.add(pt)
                path.append("{path_op} {pt.x} {pt.y}".format(**locals()))
                path_op = "L"
            path = " ".join(path)
            thickness = (poly.thickness or default_thickness) * scale
            fill = fill_tbl.get(poly.fill, "")
            svg = obj_filled_svg if fill else obj_svg
            svg.append(
                " ".join(
                    [
                        "<path",
                        'd="{path}"',
                        'style="stroke-width:{thickness}"',
                        'class="$cell_id symbol {fill}"',
                        "/>",
                    ]
                ).format(**locals())
            )

        elif isinstance(obj, DrawRect):
            rect = obj
            start = tx(Point(rect.x1, -rect.y1), symtx) * scale
            end = tx(Point(rect.x2, -rect.y2), symtx) * scale
            obj_bbox.add(start)
            obj_bbox.add(end)
            rect_bbox = BBox(start, end)
            thickness = (rect.thickness or default_thickness) * scale
            fill = fill_tbl.get(rect.fill, "")
            svg = obj_filled_svg if fill else obj_svg
            svg.append(
                " ".join(
                    [
                        "<rect",
                        'x="{rect_bbox.min.x}" y="{rect_bbox.min.y}"',
                        'width="{rect_bbox.w}" height="{rect_bbox.h}"',
                        'style="stroke-width:{thickness}"',
                        'class="$cell_id symbol {fill}"',
                        "/>",
                    ]
                ).format(**locals())
            )

        elif isinstance(obj, DrawText):
            text = obj
            origin = tx(Point(text.x, -text.y), symtx) * scale
            angle = tx(text.angle, symtx)
            size = text.size * scale
            justify = {"L": "start", "C": "middle", "R": "end"}[text.halign]
            offset = (
                tx(
                    {"T": Point(0, 1), "B": Point(0, 0), "C": Point(0, 0.5)}[
                        text.valign
                    ],
                    symtx,
                )
                * size
            )
            obj_txt_svg.append(
                draw_text(
                    text.text, size, justify, origin, angle, offset, class_="part_text"
                )
            )

        elif isinstance(obj, DrawPin):

            pin = obj
            part_pin = part[
                pin.num
            ]  # Get Pin object associated with this pin drawing object.

            try:
                visible = pin.shape[0] != "N"
            except IndexError:
                visible = True  # No pin shape given, so it is visible by default.

            # Start pin group.
            orientation = tx(pin.orientation, symtx)
            dir = pin_dir_tbl[orientation].direction
            if part_pin.net in [None, NC]:
                # Unconnected pins remain at the length of the default symbol pin.
                extension = Point(0, 0)
            else:
                # Extend the pin if it's connected to a net.
                extension = (
                    dir
                    * (
                        pin.name_size * 0.5 * max_stub_len
                        + 2 * abs(pin_dir_tbl[orientation].net_offset.x)
                    )
                    * scale
                )
            start = tx(Point(pin.x, -pin.y), symtx) * scale - extension
            side = pin_dir_tbl[orientation].side
            obj_pin_info.append(PinInfo(x=start.x, y=start.y, side=side, pid=pin.num))

            if visible:
                # Draw pin if it's not invisible.

                # Create line for pin lead.
                l = dir * pin.length * scale
                end = start + l + extension
                thickness = default_thickness * scale
                obj_bbox.add(start)
                obj_bbox.add(end)
                obj_svg.append(
                    " ".join(
                        [
                            "<path",
                            'd="M {start.x} {start.y} L {end.x} {end.y}"',
                            'style="stroke-width:{thickness}"',
                            'class="$cell_id symbol"' "/>",
                        ]
                    ).format(**locals())
                )

                # Create pin number.
                if show_nums:
                    angle = pin_dir_tbl[orientation].angle
                    num_justify = pin_dir_tbl[orientation].num_justify
                    num_size = pin.num_size * scale
                    num_offset = pin_dir_tbl[orientation].num_offset * scale
                    num_offset.y = num_offset.y * pin.num_size
                    # Pin nums are text, but they go into graphical SVG because they are part of a pin object.
                    obj_svg.append(
                        draw_text(
                            str(pin.num),
                            num_size,
                            num_justify,
                            end,
                            angle,
                            num_offset,
                            "pin_num_text",
                        )
                    )

                # Create pin name.
                if pin.name != "~" and show_names:
                    name_justify = pin_dir_tbl[orientation].name_justify
                    name_size = pin.name_size * scale
                    name_offset = pin_dir_tbl[orientation].name_offset * scale
                    name_offset.y = name_offset.y * pin.name_size
                    # Pin names are text, but they go into graphical SVG because they are part of a pin object.
                    obj_svg.append(
                        draw_text(
                            str(pin.name),
                            name_size,
                            name_justify,
                            end,
                            angle,
                            name_offset,
                            "pin_name_text",
                        )
                    )

                # Create net stub name.
                if max_stub_len:
                    # Only do this if stub length > 0; otherwise, no stubs are needed.
                    for net in part_pin.nets:
                        # Don't create stubs for no-connect nets.
                        if net in [NC, None]:
                            continue
                        if net in net_stubs:
                            net_justify = pin_dir_tbl[orientation].name_justify
                            net_size = (
                                pin.name_size * scale
                            )  # Net name font size same as pin name font size.
                            net_offset = pin_dir_tbl[orientation].net_offset * scale
                            net_offset.y = net_offset.y * pin.name_size
                            obj_svg.append(
                                draw_text(
                                    net.name,
                                    net_size,
                                    net_justify,
                                    start,
                                    angle,
                                    net_offset,
                                    "net_name_text",
                                )
                            )
                            break  # Only one label is needed per stub.

        else:
            active_logger.error(
                "Unknown graphical object {} in part symbol {}.".format(
                    type(obj), part.name
                )
            )

        # Enter the current object into the SVG for this part.
        unit = getattr(obj, "unit", 0)
        if unit == 0:
            # Anything in unit #0 gets added to all units.
            for pin_info in unit_pin_info:
                pin_info.extend(obj_pin_info)
            for svg in unit_svg:
                svg.extend(obj_svg)
            for svg in unit_filled_svg:
                svg.extend(obj_filled_svg)
            for txt_svg in unit_txt_svg:
                txt_svg.extend(obj_txt_svg)
            for bbox in unit_bbox:
                bbox.add(obj_bbox)
        else:
            unit_pin_info[unit].extend(obj_pin_info)
            unit_svg[unit].extend(obj_svg)
            unit_filled_svg[unit].extend(obj_filled_svg)
            unit_txt_svg[unit].extend(obj_txt_svg)
            unit_bbox[unit].add(obj_bbox)

    # End of loop through all the component objects.

    # Assemble and name the SVGs for all the part units.
    svg = []
    for unit in range(1, num_units + 1):
        bbox = unit_bbox[unit]

        # Assign part unit name.
        if max_stub_len:
            # If net stubs are attached to symbol, then it's only to be used
            # for a specific part. Therefore, tag the symbol name with the unique
            # part reference so it will only be used by this part.
            symbol_name = "{part.name}_{part.ref}_{unit}_{symtx}".format(**locals())
        else:
            # No net stubs means this symbol can be used for any part that
            # also has no net stubs, so don't tag it with a specific part reference.
            symbol_name = "{part.name}_{unit}_{symtx}".format(**locals())

        # Begin SVG for part unit. Translate it so the bbox.min is at (0,0).
        translate = bbox.min * -1
        svg.append(
            " ".join(
                [
                    "<g",
                    's:type="{symbol_name}"',
                    's:width="{bbox.w}"',
                    's:height="{bbox.h}"',
                    'transform="translate({translate.x},{translate.y})"',
                    ">",
                ]
            ).format(**locals())
        )

        # Add part alias.
        svg.append('<s:alias val="{symbol_name}"/>'.format(**locals()))

        # Add part unit text and graphics.
        svg.extend(unit_filled_svg[unit])  # Filled items go on the bottom.
        svg.extend(unit_svg[unit])  # Then unfilled items.
        svg.extend(unit_txt_svg[unit])  # Text comes last.

        # Place a visible bounding-box around symbol for trouble-shooting.
        show_bbox = False
        if show_bbox:
            svg.append(
                " ".join(
                    [
                        "<rect",
                        'x="{bbox.min.x}" y="{bbox.min.y}"',
                        'width="{bbox.w}" height="{bbox.h}"',
                        'style="stroke-width:3; stroke:#f00"',
                        'class="$cell_id symbol"',
                        "/>",
                    ]
                ).format(**locals())
            )

        # Keep the pins out of the grouped text & graphics but adjust their coords
        # to account for moving the bbox.
        for pin_info in unit_pin_info[unit]:
            pin_pt = Point(pin_info.x, pin_info.y)
            side = pin_info.side
            pid = pin_info.pid
            pin_svg = '<g s:x="{pin_pt.x}" s:y="{pin_pt.y}" s:pid="{pid}" s:position="{side}"/>'.format(
                **locals()
            )
            svg.append(pin_svg)

        # Finish SVG for part unit.
        svg.append("</g>")

    return "\n".join(svg)
