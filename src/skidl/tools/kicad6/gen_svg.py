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

from skidl.schematics.geometry import Tx, Point, BBox
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


def get_pin_info(x, y, rotation, length):
    quadrant = (rotation+45)//90
    side = {
            0: "right",
            1: "top",
            2: "left",
            3: "bottom",
            }[quadrant]

    dx = math.cos( math.radians(rotation))
    dy = -math.sin( math.radians(rotation))
    endx = x+dx*length
    endy = y+dy*length
    return [endx,endy], [x,y], side
# TODO: Figure out if the stuff below is needed.

    # Sometimes the pins are drawn from the tip towards the part 
    # and sometimes from the part towards the tip. Assuming the 
    # part center is close to the origin, we can flip this by 
    # considering the point farthest from the origin to be the tip
    # if math.dist([endx,endy], [0,0]) > math.dist([x,y], [0,0]):
    if endx**2 + endy**2 > x**2 + y**2:
        return [x,y], [endx, endy], side
    else:
        side = {
                "right":"left",
                "top":"bottom",
                "left":"right",
                "bottom":"top",
                }[side]
        return [endx, endy], [x,y], side


def draw_cmd_to_svg(draw_cmd, tx):
    """Convert symbol drawing command into SVG string and an associated bounding box.

    Args:
        draw_cmd (str): Contains textual information about the shape to be drawn.
        tx (Tx): Transformation matrix to be applied to the shape.

    Returns:
        shape_svg (str): SVG command for the shape.
        shape_bbox (BBox): Bounding box for the shape.
    """

    def text_to_svg(text, tx, x, y, rotation, font_size, justify, class_, attr):
        font_dim = abs(font_size * tx.scale) * 0.35
        char_width = font_dim*0.6
        start = Point(x, y) * tx
        end = start + Point(len(text)*char_width, font_dim) * Tx().rot(rotation)
        bbox = BBox(start, end)
        svg = " ".join(
            [
                "<text",
                "class='{class_}'",
                "text-anchor='{justify}'",
                "x='{start.x}' y='{start.y}'",
                "transform='rotate({rotation} {start.x} {start.y})'",
                "style='font-size:{font_dim}mm'",
                "{attr}",
                ">{text}</text>",

                 "<rect",
                'x="{bbox.min.x}" y="{bbox.min.y}"',
                'width="{bbox.w}" height="{bbox.h}"',
                # 'style="stroke-width:2px"',
                # 'class="$cell_id symbol {fill}"',
                "/>",
           ]
        ).format(**locals())
        return svg, bbox

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
        points = [Point(*pt[0:2])*tx for pt in shape["pts"]["xy"]]
        bbox = BBox(*points)
        points_str=" ".join( [pt.svg for pt in points] )
        stroke= shape["stroke"]["type"],
        stroke_width= abs(shape["stroke"]["width"] * tx.scale)
        fill= shape["fill"]["type"]
        svg = " ".join(
                [
                    "<polyline",
                    'points="{points_str}"',
                    'style="stroke-width:{stroke_width}"',
                    'class="$cell_id symbol {fill}"',
                    "/>",
                ]
            ).format(**locals())

    elif shape_type == "circle":
        ctr = Point(*shape["center"]) * tx
        radius = Point(shape["radius"], shape["radius"]) * tx.scale
        r = abs(radius.x)
        bbox = BBox(ctr+radius, ctr-radius)
        stroke= shape["stroke"]["type"]
        stroke_width= abs(shape["stroke"]["width"] * tx.scale)
        fill= shape["fill"]["type"]
        svg = " ".join(
                [
                    "<circle",
                    'cx="{ctr.x}" cy="{ctr.y}" r="{r}"',
                    'style="stroke-width:{stroke_width}"',
                    'class="$cell_id symbol {fill}"',
                    "/>",
                ]
            ).format(**locals())

    elif shape_type == "rectangle":
        start = Point(*shape["start"]) * tx
        end = Point(*shape["end"]) * tx
        bbox = BBox(start, end)
        stroke= shape["stroke"]["type"]
        stroke_width= abs(shape["stroke"]["width"] * tx.scale)
        fill= shape["fill"]["type"]
        svg =  " ".join(
            [
                "<rect",
                'x="{bbox.min.x}" y="{bbox.min.y}"',
                'width="{bbox.w}" height="{bbox.h}"',
                'style="stroke-width:{stroke_width}"',
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

        angle = math.acos( (A*A + B*B - C*C)/(2*A*B) )
        K = .5*A*B*math.sin(angle)
        r = A*B*C/4/K

        large_arc = int(math.pi/2 > angle)
        sweep = int((b.x - a.x)*(c.y - a.y) - (b.y - a.y)*(c.x - a.x) < 0)
        stroke= shape["stroke"]["type"]
        stroke_width= abs(shape["stroke"]["width"] * tx.scale)
        fill= shape["fill"]["type"]
        svg = " ".join(
            [
                "<path",
                'd="M {a.x} {a.y} A {r} {r} 0 {large_arc} {sweep} {b.x} {b.y}"',
                'style="stroke-width:{stroke_width}"',
                'class="$cell_id symbol {fill}"',
                "/>",
            ]
        ).format(**locals())

    elif shape_type == "property":
        if shape["misc"][0].lower() == "reference":
            class_ = "part_ref_text"
            extra = 's:attribute="ref"'
        elif shape["misc"][0].lower() == "value":
            class_ = "part_name_text"
            extra = 's:attribute="value"'
        elif "hide" not in shape["effects"]["misc"]:
            raise RuntimeError("Unknown property {symbol[1]} is not hidden.".format(**locals()))
        svg, bbox = text_to_svg(shape["misc"][1], tx, *shape["at"][0:3], shape["effects"]["font"]["size"][0], shape["justify"], class_, extra)

    elif shape_type == "pin":
        start = Point(*shape["at"][0:2]) * tx
        rotation = shape["at"][2]
        length = shape["length"]
        vec = Point(shape["length"], 0) * Tx().rot(rotation) * tx
        end = start + vec
        if vec.x > vec.y:
            side = "right"
        elif vec.y > vec.x:
            side = "top"
        elif -vec.x > vec.y:
            side = "left"
        elif -vec.y > vec.x:
            side = "bottom"
        else:
            raise RuntimeError("Impossible pin orientation.")
        points_str = start.svg + " " + end.svg
        bbox = BBox(start, end)
        name = shape["name"]["misc"]
        number = shape["number"]["misc"]
        pid = number
        stroke= shape["stroke"]["type"]
        stroke_width= abs(shape["stroke"]["width"] * tx.scale)
        fill= shape["fill"]["type"]
        circle_stroke_width = 2*stroke_width
        font_size = shape["number"]["effects"]["font"]["size"][0]
        justify="left"
        pid_svg, pid_bbox = text_to_svg(pid, tx, *shape["at"][0:3], font_size, justify, "pin_name_text", "")
        bbox += pid_bbox
        svg = " ".join(
                [
                    # Draw a dot at the tip of the pin.
                    "<circle",
                    'cx="{start.x}" cy="{start.y}" r="{circle_stroke_width}"',
                    # 'cx="{end[0]}" cy="{end[1]}" r="{circle_stroke_width}"',
                    'style="stroke-width:{circle_stroke_width}"',
                    'class="$cell_id symbol {fill}"',
                    "/>",
                    # Draw the pin.
                    "\n<polyline",
                    'points="{points_str}"',
                    'style="stroke-width:{stroke_width}"',
                    'class="$cell_id symbol {fill}"',
                    "/>",
                    # Draw the pin number.
                    pid_svg,
                    # "<text",
                    # "text-anchor='{justify}'",
                    # "x='{start.x}' y='{start.y}'",
                    # "style='font-size:{font_size}px'",
                    # ">",
                    # "{pid}",
                    # "</text>",
                    # Give netlistsvg the info it needs to connect nets to pins.
                    '<g s:x="{start.x}" s:y="{start.y}" s:pid="{pid}" s:position="{side}"/>',
                ]
            ).format(**locals())

    elif shape_type == "text":
        class_ = "text"
        extra = ""
        svg, bbox = text_to_svg(shape["misc"], tx, *shape["at"][0:3], shape["effects"]["font"]["size"][0], shape["justify"], class_, extra)

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

    scale = 10  # Scale of KiCad units to SVG units.
    tx = Tx.from_symtx(symtx) * scale

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
        bbox = BBox()
        unit_svg = []
        for cmd in part.draw_cmds[unit.num]:
            s, bb = draw_cmd_to_svg(cmd, tx)
            # s, bb = draw_cmd_to_svg(cmd, Tx())
            bbox.add(bb)
            unit_svg.append(s)
        tx_bbox = bbox

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
        # translate = bbox.min * -1
        # translate = Point(tx_bbox.x, tx_bbox.y) * -1
        translate = -tx_bbox.min
        svg.append(
            " ".join(
                [
                    "<g",
                    's:type="{symbol_name}"',
                    's:width="{tx_bbox.w}"',
                    's:height="{tx_bbox.h}"',
                    'transform="translate({translate.x} {translate.y})"',
                    ">",
                ]
            ).format(**locals())
        )

        # Add part alias.
        svg.append('<s:alias val="{symbol_name}"/>'.format(**locals()))

        # Add part unit text and graphics.

        # if "H" in symtx:
        #     scale_x = -1
        #     scale_y = 1
        # elif "V" in symtx:
        #     scale_x = 1
        #     scale_y = -1
        # else:
        #     scale_x = 1
        #     scale_y = 1

        # if "R" in symtx:
        #     rotation = 90
        # elif "L" in symtx:
        #     rotation = 270
        # else:
        #     rotation = 0

        # netlistsvg seems to look for pins in groups on the top level and it gets
        # confused by the transform groups without a pid attribute.
        # So surround these transform groups with a group having a pid attribute.
        # netlistsvg will see that and won't bother the enclosed groups.
        # svg.append('<g s:pid="">')

        # svg.append(
        #     " ".join(
        #         [
        #             "<g>",
        #             # "<g",
        #             # 'transform="scale({scale} {scale}) rotate({rotation} 0 0)"',
        #             # ">",
        #         ]
        #     ).format(**locals())
        # )

        # svg.append(
        #     " ".join(
        #         [
        #             "<g>",
        #             # "<g",
        #             # 'transform="scale({scale_x}, {scale_y})"',
        #             # ">",
        #         ]
        #     ).format(**locals())
        # )

        for item in unit_svg:
            if "text" not in item:
                svg.append(item)
        # svg.append("</g>")

        for item in unit_svg:
            if "text" in item:
                svg.append(item)
        # svg.append("</g>")

        # svg.append("</g>") # Close the group with the pid attribute.

        # Place a visible bounding-box around symbol for trouble-shooting.
        show_bbox = True
        bbox_stroke_width = scale * 0.1
        if show_bbox:
            svg.append(
                " ".join(
                    [
                        "<rect",
                        'x="{tx_bbox.min.x}" y="{tx_bbox.min.y}"',
                        # 'x="{tx_bbox.ctr.x}" y="{tx_bbox.ctr.y}"',
                        # 'x="{tx_bbox.x}" y="{tx_bbox.y}"',
                        'width="{tx_bbox.w}" height="{tx_bbox.h}"',
                        'style="stroke-width:{bbox_stroke_width}; stroke:#f00"',
                        'class="$cell_id symbol"',
                        "/>",
                    ]
                ).format(**locals())
            )

        # Keep the pins out of the grouped text & graphics but adjust their coords
        # to account for moving the bbox.
        # for pin in unit.pins:
        #     _, pin_pt, side = get_pin_info(pin.x, pin.y, pin.rotation, pin.length)
        #     pin_pt = Point(pin_pt[0], pin_pt[1])

        #     #print("pin_pt", pin_pt)
        #     #print("symtx", symtx)
        #     if "H" in symtx:
        #         pin_pt.x = -pin_pt.x
        #         side = {
        #                 "right":"left",
        #                 "top":"top",
        #                 "left":"right",
        #                 "bottom":"bottom",
        #                 }[side]
        #     elif "V" in symtx:
        #         side = {
        #                 "right":"right",
        #                 "top":"bottom",
        #                 "left":"left",
        #                 "bottom":"top",
        #                 }[side]
        #         pin_pt.y = -pin_pt.y

        #     if "L" in symtx:
        #         side = {
        #                 "right":"top",
        #                 "top":"left",
        #                 "left":"bottom",
        #                 "bottom":"right",
        #                 }[side]
        #         newx = pin_pt.y
        #         pin_pt.y = -pin_pt.x
        #         pin_pt.x = newx
        #     elif "R" in symtx:
        #         side = {
        #                 "right":"bottom",
        #                 "top":"right",
        #                 "left":"top",
        #                 "bottom":"left",
        #                 }[side]
        #         newx = -pin_pt.y
        #         pin_pt.y = pin_pt.x
        #         pin_pt.x = newx

        #     pin_pt *= scale

        #     # pid = pin.name
        #     pid = pin.num
        #     font_size = 12
        #     justify="left"
        #     pin_svg = " ".join([
        #         "<text",
        #         "text-anchor='{justify}'",
        #         "x='{pin_pt.x}' y='{pin_pt.y}'",
        #         "style='font-size:{font_size}px'",
        #         ">",
        #         "{pid}",
        #         #"{side}", # Uncomment this to visualize/verify which side the pin is on
        #         "</text>",
        #         '<g s:x="{pin_pt.x}" s:y="{pin_pt.y}" s:pid="{pid}" s:position="{side}">',
        #         '</g>']).format(
        #         **locals()
        #     )
        #     svg.append(pin_svg)

        # Finish SVG for part unit.
        svg.append("</g>\n")

    return "\n".join(svg)
