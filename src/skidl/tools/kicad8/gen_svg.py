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

import math
from collections import namedtuple

try:
    from future import standard_library

    standard_library.install_aliases()
except ImportError:
    pass

from skidl.schematics.geometry import Tx, Point, BBox, tx_flip_y
from skidl.utilities import export_to_all


def draw_cmd_to_dict(symbol):
    """
    Convert a list of symbols from a KICAD part definition into a
    dictionary for easier access to properties.
    """
    d = {}
    name = symbol[0].value()
    items = symbol[1:]
    d = {}
    is_named_present = False
    item_names = []
    for item in items:
        # If the object is a list, recursively convert to dict
        if isinstance(item, list):
            item_name, item_dict = draw_cmd_to_dict(item)
            is_named_present = True
        # If the object is unnamed, put it in the "misc" list
        # ["key", item1, item2, ["xy", 0, 0]] -> "key": {"misc":[item1, item2], "xy":[0,0]
        else:
            item_name = "misc"
            item_dict = item

        # Multiple items with the same key (e.g. ("xy" 0 0) ("xy" 1 0))
        # get put into a list {"xy": [[0,0],[1,0]]}
        if item_name not in item_names:
            item_names.append(item_name)
        if item_name not in d:
            d[item_name] = [item_dict]
        else:
            d[item_name].append(item_dict)

    # if a list has only one item, remove it from the list
    for item_name in item_names:
        if len(d[item_name]) == 1:
            d[item_name] = d[item_name][0]

    if not is_named_present:
        d = d["misc"]

    return name, d


def bbox_to_svg(bbox, stroke_wid):
    return " ".join(
        [
            "<rect",
            'x="{bbox.min.x:.3f}" y="{bbox.min.y:.3f}"',
            'width="{bbox.w:.3f}" height="{bbox.h:.3f}"',
            'style="stroke-width:{stroke_wid:.3f}; stroke:#606060"',
            'class="$cell_id symbol"',
            "/>",
            "\n",
        ]
    ).format(**locals())


def draw_cmd_to_svg(draw_cmd, tx, part, net_stubs, max_stub_len):
    """Convert symbol drawing command into SVG string and an associated bounding box.

    Args:
        draw_cmd (str): Contains textual information about the shape to be drawn.
        tx (Tx): Transformation matrix to be applied to the shape.
        part (Part): Part object that the drawing command belongs to (used to get pin information.)
        net_stubs (list): List of Net objects whose names will be connected to part symbol pins as connection stubs.
        max_stub_len (int): Maximum length of a net stub name.

    Returns:
        shape_svg (str): SVG command for the shape.
        shape_bbox (BBox): Bounding box for the shape.
    """
    
    # Use this when determining width of a text string based on its number of characters.
    char_sz_fudge_factor = 0.6

    tx_scale = tx.scale  # Compute this only once.

    def points_to_str(*points):
        pt2str = lambda pt: "{pt.x:.3f},{pt.y:.3f}".format(pt=pt)
        return " ".join((pt2str(pt) for pt in points))

    def pin_side(vec):
        """Determine the side of the symbol based on the pin's direction vector."""
        if vec.x > vec.y and vec.x > -vec.y:
            return "left"
        elif vec.x < vec.y and vec.x > -vec.y:
            return "top"
        elif vec.x < vec.y and vec.x < -vec.y:
            return "right"
        elif vec.x > vec.y and vec.x < -vec.y:
            return "bottom"
        else:
            raise RuntimeError("Impossible pin orientation.")

    def pin_text_to_svg(text, pin_attr, side, pt, char_wid):
        spc = "&#8201;&#8201;"  # Whitespaces for padding around pin text.
        svg_template = {
            "left": {
                "pin_name": '<text class="pin_name_text" x="{x:.3f}" y="{y:.3f}" transform="rotate(0 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline="central" text-anchor="start">{spc}{text}</text>\n',
                "pin_num": '<text class="pin_num_text"  x="{x:.3f}" y="{y:.3f}" transform="rotate(0 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline=""        text-anchor="end">{text}{spc}</text>\n',
                "net_name": '<text class="net_name_text" x="{x:.3f}" y="{y:.3f}" transform="rotate(0 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline="central" text-anchor="end">{text}{spc}</text>\n',
            },
            "right": {
                "pin_name": '<text class="pin_name_text" x="{x:.3f}" y="{y:.3f}" transform="rotate(0 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline="central" text-anchor="end">{text}{spc}</text>\n',
                "pin_num": '<text class="pin_num_text"  x="{x:.3f}" y="{y:.3f}" transform="rotate(0 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline=""        text-anchor="start">{spc}{text}</text>\n',
                "net_name": '<text class="net_name_text" x="{x:.3f}" y="{y:.3f}" transform="rotate(0 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline="central" text-anchor="start">{spc}{text}</text>\n',
            },
            "top": {
                "pin_name": '<text class="pin_name_text" x="{x:.3f}" y="{y:.3f}" transform="rotate(-90 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline="central" text-anchor="end">{text}{spc}</text>\n',
                "pin_num": '<text class="pin_num_text"  x="{x:.3f}" y="{y:.3f}" transform="rotate(-90 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline=""        text-anchor="start">{spc}{text}</text>\n',
                "net_name": '<text class="net_name_text" x="{x:.3f}" y="{y:.3f}" transform="rotate(-90 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline="central" text-anchor="start">{spc}{text}</text>\n',
            },
            "bottom": {
                "pin_name": '<text class="pin_name_text" x="{x:.3f}" y="{y:.3f}" transform="rotate(-90 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline="central" text-anchor="start">{spc}{text}</text>\n',
                "pin_num": '<text class="pin_num_text"  x="{x:.3f}" y="{y:.3f}" transform="rotate(-90 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline=""        text-anchor="end">{text}{spc}</text>\n',
                "net_name": '<text class="net_name_text" x="{x:.3f}" y="{y:.3f}" transform="rotate(-90 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline="central" text-anchor="end">{text}{spc}</text>\n',
            },
        }
        return svg_template[side][pin_attr].format(
            x=pt.x, y=pt.y, char_wid=char_wid, text=text, spc=spc
        )

    def text_to_svg(text, side, pt, char_wid, class_, attr):
        svg_template = {
            "right": '<text class="{class_}" x="{x:.3f}" y="{y:.3f}" transform="rotate(0 {x:.3f} {y:.3f})"   style="font-size:{char_wid:.3f}" dominant-baseline="central" text-anchor="end"   {attr}>{text}</text>\n',
            "left": '<text class="{class_}" x="{x:.3f}" y="{y:.3f}" transform="rotate(0 {x:.3f} {y:.3f})"   style="font-size:{char_wid:.3f}" dominant-baseline="central" text-anchor="start" {attr}>{text}</text>\n',
            "bottom": '<text class="{class_}" x="{x:.3f}" y="{y:.3f}" transform="rotate(-90 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline="central" text-anchor="start" {attr}>{text}</text>\n',
            "top": '<text class="{class_}" x="{x:.3f}" y="{y:.3f}" transform="rotate(-90 {x:.3f} {y:.3f})" style="font-size:{char_wid:.3f}" dominant-baseline="central" text-anchor="end"   {attr}>{text}</text>\n',
        }
        return svg_template[side].format(
            x=pt.x, y=pt.y, char_wid=char_wid, text=text, class_=class_, attr=attr
        )

    def text_bbox(text, start, dir, char_wid, char_hgt):
        char_wid *= char_sz_fudge_factor  # Fudge-factor to make bbox turn out right.
        char_hgt *= char_sz_fudge_factor  # Fudge-factor to make bbox turn out right.
        ortho_dir = dir * Tx().rot(90)
        p1 = start - ortho_dir * char_hgt / 2
        p2 = start + ortho_dir * char_hgt / 2
        p3 = p1 + dir * char_wid * len(text)
        p4 = p2 + dir * char_wid * len(text)
        return BBox(p1, p2, p3, p4)

    shape_type, shape = draw_cmd_to_dict(draw_cmd)

    default_stroke_width = "1"
    default_stroke = "#000"

    if not "stroke" in shape:
        shape["stroke"] = {}
    if not "type" in shape["stroke"]:
        shape["stroke"]["type"] = "default"
    if not "width" in shape["stroke"]:
        shape["stroke"]["width"] = 0

    if not "fill" in shape:
        shape["fill"] = {}
    if not "type" in shape["fill"]:
        shape["fill"]["type"] = "none"
    if not "justify" in shape:
        shape["justify"] = "right"

    if shape["stroke"]["type"] == "default":
        shape["stroke"]["type"] = "#000"
    if shape["stroke"]["width"] == 0:
        shape["stroke"]["width"] = 0.1

    if shape_type == "polyline":
        points = [Point(*pt[0:2]) * tx for pt in shape["pts"]["xy"]]
        bbox = BBox(*points)
        points_str = points_to_str(*points)
        stroke = (shape["stroke"]["type"],)
        stroke_width = abs(shape["stroke"]["width"] * tx_scale)
        fill = shape["fill"]["type"]
        svg = " ".join(
            [
                "<polyline",
                'points="{points_str}"',
                'style="stroke-width:{stroke_width:.3f}"',
                'class="$cell_id symbol {fill}"',
                "/>",
            ]
        ).format(**locals())

    elif shape_type == "circle":
        ctr = Point(*shape["center"]) * tx
        radius = Point(shape["radius"], shape["radius"]) * tx_scale
        r = abs(radius.x)
        bbox = BBox(ctr + radius, ctr - radius)
        stroke = shape["stroke"]["type"]
        stroke_width = abs(shape["stroke"]["width"] * tx_scale)
        fill = shape["fill"]["type"]
        svg = " ".join(
            [
                "<circle",
                'cx="{ctr.x:.3f}" cy="{ctr.y:.3f}" r="{r:.3f}"',
                'style="stroke-width:{stroke_width:.3f}"',
                'class="$cell_id symbol {fill}"',
                "/>",
            ]
        ).format(**locals())

    elif shape_type == "rectangle":
        start = Point(*shape["start"]) * tx
        end = Point(*shape["end"]) * tx
        bbox = BBox(start, end)
        stroke = shape["stroke"]["type"]
        stroke_width = abs(shape["stroke"]["width"] * tx_scale)
        fill = shape["fill"]["type"]
        svg = " ".join(
            [
                "<rect",
                'x="{bbox.min.x:.3f}" y="{bbox.min.y:.3f}"',
                'width="{bbox.w:.3f}" height="{bbox.h:.3f}"',
                'style="stroke-width:{stroke_width:.3f}"',
                'class="$cell_id symbol {fill}"',
                "/>",
            ]
        ).format(**locals())

    elif shape_type == "arc":
        a = Point(*shape["start"]) * tx
        b = Point(*shape["end"]) * tx
        c = Point(*shape["mid"]) * tx
        bbox = BBox(a, b, c)

        A = (b - c).magnitude
        B = (a - c).magnitude
        C = (a - b).magnitude

        angle = math.acos((A * A + B * B - C * C) / (2 * A * B))
        K = 0.5 * A * B * math.sin(angle)
        r = A * B * C / 4 / K

        large_arc = int(math.pi / 2 > angle)
        sweep = int((b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x) < 0)
        stroke = shape["stroke"]["type"]
        stroke_width = abs(shape["stroke"]["width"] * tx_scale)
        fill = shape["fill"]["type"]
        svg = " ".join(
            [
                "<path",
                'd="M {a.x:.3f} {a.y:.3f} A {r:.3f} {r:.3f} 0 {large_arc} {sweep} {b.x:.3f} {b.y:.3f}"',
                'style="stroke-width:{stroke_width:.3f}"',
                'class="$cell_id symbol {fill}"',
                "/>",
            ]
        ).format(**locals())

    elif shape_type == "property":
        if "hide" in shape["effects"]:
            svg, bbox = "", BBox()
        else:
            if shape["misc"][0].lower() == "reference":
                class_ = "part_ref_text"
                attr = 's:attribute="ref"'
            elif shape["misc"][0].lower() == "value":
                class_ = "part_name_text"
                attr = 's:attribute="value"'
            else:
                raise RuntimeError(
                    "Unknown property {symbol[1]} is not hidden.".format(**locals())
                )
            start = Point(*shape["at"][0:2])
            rotation = shape["at"][2]
            justify = (
                shape["effects"].get("justify", shape.get("justify", "left")).lower()
            )
            dir = {"right": Point(-1, 0), "left": Point(1, 0)}[justify] * Tx().rot(
                rotation
            )
            end = start + dir
            start *= tx
            end *= tx
            side = pin_side(dir * tx.no_translate())
            char_wid, char_hgt = shape["effects"]["font"]["size"][:]
            char_wid *= tx_scale
            char_hgt *= tx_scale
            text = shape["misc"][1]
            svg = text_to_svg(text, side, start, char_wid, class_, attr)
            bbox = text_bbox(text, start, (end - start).norm, char_wid, char_hgt)

    elif shape_type == "pin":
        num_char_wid, num_char_hgt = shape["number"]["effects"]["font"]["size"][:]
        name_char_wid, name_char_hgt = shape["name"]["effects"]["font"]["size"][:]
        net_name_char_wid, net_name_char_hgt = name_char_wid, name_char_hgt

        # Get the pin object associated with this drawing command.
        pin_name = shape["name"]["misc"]
        pin_num = shape["number"]["misc"]
        pin = part[pin_num]
        if pin.net in [None, NC]:
            # Unconnected pins remain at the length of the default symbol pin.
            extension = 0
        elif pin.net in net_stubs:
            # Don't extend the pin since the net name for the stub will be
            # connected directly to the pin.
            extension = 0
        else:
            # The pin is connected to a non-stub (routed) net.
            # Extend the pin to the edge of the symbol bounding box so it
            # can be routed to.
            extension = net_name_char_wid * max_stub_len * char_sz_fudge_factor

        start = Point(*shape["at"][0:2])
        rotation = shape["at"][2]
        length = shape["length"]
        dir = Point(1, 0) * Tx().rot(rotation)
        end = start + dir * length
        start -= dir * extension
        end *= tx
        start *= tx
        side = pin_side(dir * tx.no_translate())

        # Bounding box for the pin.
        bbox = BBox(start, end)

        num_char_wid *= tx_scale
        num_char_hgt *= tx_scale
        name_char_wid *= tx_scale
        name_char_hgt *= tx_scale
        net_name_char_hgt *= tx_scale
        net_name_char_wid *= tx_scale

        # Now add bounding boxes for the pin number, name, and net name.
        bbox += text_bbox(
            pin_num, start, (end - start).norm, num_char_wid, num_char_hgt
        )
        bbox += text_bbox(
            pin_name, start, (end - start).norm, name_char_wid, name_char_hgt
        )
        if pin.net in net_stubs:
            bbox += text_bbox(
                pin.net.name,
                start,
                (start - end).norm,
                net_name_char_wid,
                net_name_char_hgt,
            )

        stroke = shape["stroke"]["type"]
        stroke_width = abs(shape["stroke"]["width"] * tx_scale)
        fill = shape["fill"]["type"]
        circle_stroke_width = 2 * stroke_width

        points_str = points_to_str(start, end)
        pin_svg = '<polyline points="{points_str}" style="stroke-width:{stroke_width:.3f}" class="$cell_id symbol {fill}" />\n'.format(
            **locals()
        )
        # pin_circle_svg = '<circle cx="{start.x:.3f}" cy="{start.y:.3f}" r="{circle_stroke_width:.3f}" style="stroke-width:{circle_stroke_width:.3f}" class="$cell_id symbol {fill}" />\n'.format(**locals())
        pin_circle_svg = ""
        pin_num_svg = pin_text_to_svg(pin_num, "pin_num", side, end, num_char_wid)
        pin_name_svg = pin_text_to_svg(pin_name, "pin_name", side, end, name_char_wid)
        if pin.net in net_stubs:
            net_name_svg = pin_text_to_svg(
                pin.net.name, "net_name", side, start, net_name_char_wid
            )
        else:
            net_name_svg = ""
        connection_svg = '<g s:x="{start.x:.3f}" s:y="{start.y:.3f}" s:pid="{pin_num}" s:position="{side}"/>\n'.format(
            **locals()
        )
        svg = "".join(
            [
                pin_svg,
                pin_circle_svg,
                pin_num_svg,
                pin_name_svg,
                net_name_svg,
                connection_svg,
            ]
        )

    elif shape_type == "text":
        class_ = "text"
        attr = ""
        start = Point(*shape["at"][0:2])
        rotation = shape["at"][2]
        dir = {"right": Point(1, 0), "left": Point(-1, 0)}[
            shape["justify"].lower()
        ] * Tx().rot(rotation)
        end = start + dir
        start *= tx
        end *= tx
        side = pin_side(dir * tx.no_translate())
        char_wid, char_hgt = shape["effects"]["font"]["size"][:]
        char_wid *= tx_scale
        char_hgt *= tx_scale
        text = shape["misc"]
        svg = text_to_svg(text, side, start, char_wid, class_, attr)
        bbox = text_bbox(text, start, (end - start).norm, char_wid, char_hgt)

    else:
        raise RuntimeError("Unrecognized shape type: {shape_type}".format(**locals()))

    return svg, bbox


@export_to_all
def gen_svg_comp(part, symtx, net_stubs=None):
    """
    Generate SVG for this component.

    Args:
        part: Part object for which an SVG symbol will be created.
        net_stubs: List of Net objects whose names will be connected to
            part symbol pins as connection stubs.
        symtx: String such as "HR" that indicates symbol mirroring/rotation.

    Returns: SVG for the part symbol.
    """

    # Create transformation matrix for the symbol from symtx, flip Y axis, and scale.
    px = 96  # Pixels per inch. SVG uses pixels.
    mm = 25.4  # Millimeters per inch. KiCad uses millimeters.
    scale = px / mm  # Scale for converting KiCad units (mm) to SVG units (pixels).
    scale *= 2.54  # Adjustment for matching symbol sizes with netlistsvg's I/O ports.
    tx = Tx.from_symtx(symtx) * tx_flip_y * scale

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

    # Assemble and name the SVGs for all the part units.
    svg = []
    for unit in part.unit.values():

        # First, compute the bounding box of the part symbol.
        bbox = BBox()
        for cmd in part.draw_cmds[unit.num]:
            _, bb = draw_cmd_to_svg(cmd, tx, part, net_stubs, max_stub_len)
            bbox.add(bb)

        # Add translation to the transformation matrix so the part's bounding box
        # starts at (0,0). (netlistsvg seems to malfunction, otherwise.)
        trans_tx = tx.move(-bbox.min)

        # Finally, recalculate the part symbol with the added translation.
        bbox = BBox()
        unit_svg = []
        for cmd in part.draw_cmds[unit.num]:
            s, bb = draw_cmd_to_svg(cmd, trans_tx, part, net_stubs, max_stub_len)
            bbox.add(bb)
            unit_svg.append(s)

        # Assign part unit name.
        if max_stub_len:
            # If net stubs are attached to symbol, then it's only to be used
            # for a specific part. Therefore, tag the symbol name with the unique
            # part reference so it will only be used by this part.
            symbol_name = "{part.name}_{part.ref}_{unit.num}_{symtx}".format(**locals())
        else:
            # No net stubs means this symbol can be used for any part that
            # also has no net stubs, so don't tag it with a specific part reference.
            symbol_name = "{part.name}_{unit.num}_{symtx}".format(**locals())

        # Begin SVG for part unit. Translate it so the bbox.min is at (0,0).
        translate = -bbox.min
        svg.append(
            " ".join(
                [
                    "<g",
                    's:type="{symbol_name}"',
                    's:width="{bbox.w:.3f}"',
                    's:height="{bbox.h:.3f}"',
                    'transform="translate({translate.x:.3f} {translate.y:.3f})"',
                    ">\n",
                ]
            ).format(**locals())
        )

        # Add part alias.
        svg.append('<s:alias val="{symbol_name}"/>\n'.format(**locals()))

        for item in unit_svg:
            if "text" not in item:
                svg.append(item)

        for item in unit_svg:
            if "text" in item:
                svg.append(item)

        # Place a visible bounding-box around symbol for trouble-shooting.
        show_bbox = False
        bbox_stroke_width = scale * 0.1
        if show_bbox:
            svg.append(bbox_to_svg(bbox, bbox_stroke_width))

        # Finish SVG for part unit.
        svg.append("</g>\n")

    return "".join(svg)
