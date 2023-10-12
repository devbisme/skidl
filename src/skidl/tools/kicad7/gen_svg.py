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

from collections import namedtuple
try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from skidl.utilities import export_to_all


def symbol_to_dict(symbol):
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
            item_name, item_dict = symbol_to_dict(item)
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

    # Sometimes the pins are drawn from the tip towards the part 
    # and sometimes from the part towards the tip. Assuming the 
    # part center is close to the origin, we can flip this by 
    # considering the point farthest from the origin to be the tip
    if math.dist([endx,endy], [0,0]) > math.dist([x,y], [0,0]):
        return [x,y], [endx, endy], side
    else:
        side = {
                "right":"left",
                "top":"bottom",
                "left":"right",
                "bottom":"top",
                }[side]
        return [endx, endy], [x,y], side
    
def symbol_to_svg(symbol):
    shape_type, shape = symbol_to_dict(symbol)

    shape_bbox = BBox()

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
        points = []
        for pt in shape["pts"]["xy"]:
            x = pt[0]
            y = -pt[1]
            shape_bbox.add(Point(x,y))
            points.append(x)
            points.append(y)
        points_str=" ".join( [str(pt) for pt in points] )
        stroke= shape["stroke"]["type"],
        stroke_width= shape["stroke"]["width"]
        fill= shape["fill"]["type"]

        shape_svg = " ".join(
                [
                    "<polyline",
                    'points="{points_str}"',
                    'style="stroke-width:{stroke_width}"',
                    'class="$cell_id symbol {fill}"',
                    "/>",
                ]
            ).format(**locals())
    elif shape_type == "circle":
        cx = shape["center"][0]
        cy = -shape["center"][1]
        r = shape["radius"]
        shape_bbox.add(Point(cx,cy) + Point(r,r))
        shape_bbox.add(Point(cx,cy) - Point(r,r))
        stroke= shape["stroke"]["type"]
        stroke_width= shape["stroke"]["width"]
        fill= shape["fill"]["type"]
        shape_svg = " ".join(
                [
                    "<circle",
                    'cx="{cx}" cy="{cy}" r="{r}"',
                    'style="stroke-width:{stroke_width}"',
                    'class="$cell_id symbol {fill}"',
                    "/>",
                ]
            ).format(**locals())
    elif shape_type == "rectangle":
        x = shape["start"][0]
        y = -shape["start"][1]
        endx = shape["end"][0]
        endy = -shape["end"][1]
        newx = min(x, endx)
        newy = min(y, endy)
        width = abs(endx-x)
        height = abs(endy-y)
        shape_bbox.add(Point(x,y))
        shape_bbox.add(Point(endx, endy))
        stroke= shape["stroke"]["type"]
        stroke_width= shape["stroke"]["width"]
        fill= shape["fill"]["type"]
        shape_svg =  " ".join(
            [
                "<rect",
                'x="{newx}" y="{newy}"',
                'width="{width}" height="{height}"',
                'style="stroke-width:{stroke_width}"',
                'class="$cell_id symbol {fill}"',
                "/>",
            ]
        ).format(**locals())
    elif shape_type == "arc":
        a = [shape["start"][0], -shape["start"][1]]
        b = [shape["end"][0], -shape["end"][1]]
        c = [shape["mid"][0], -shape["mid"][1]]
        shape_bbox.add(Point(*a))
        shape_bbox.add(Point(*b))
        shape_bbox.add(Point(*c))

        A = math.dist(b,c)
        B = math.dist(a,c)
        C = math.dist(a,b)

        angle = math.acos( (A*A + B*B - C*C)/(2*A*B) )
        K = .5*A*B*math.sin(angle)
        r = A*B*C/4/K

        large_arc = int(math.pi/2 > angle)
        sweep = int((b[0] - a[0])*(c[1] - a[1]) - (b[1] - a[1])*(c[0] - a[0]) < 0)
        stroke= shape["stroke"]["type"]
        stroke_width= shape["stroke"]["width"]
        fill= shape["fill"]["type"]
        shape_svg = " ".join(
            [
                "<path",
                'd="M {a[0]} {a[1]} A {r} {r} 0 {large_arc} {sweep} {b[0]} {b[1]}"',
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
            raise RuntimeError("Unknown property {} is not hidden.".format(symbol[1]))
        x = shape["at"][0]
        y = -shape["at"][1]
        rotation = shape["at"][2]
        font_size = shape["effects"]["font"]["size"][0]
        justify = shape["justify"]
        stroke= shape["stroke"]["type"]
        stroke_width= shape["stroke"]["width"]
        fill= shape["fill"]["type"]
        class_ = class_
        extra = extra
        shape_text=shape["misc"][1]

        char_width = font_size*0.6
        rect_start_x=x
        rect_start_y=y

        text_width=len(shape_text)*char_width
        text_height=font_size

        dx = math.cos( math.radians(rotation))
        dy = math.sin( math.radians(rotation))

        rect_end_x=x+dx*text_width+dy*text_height
        rect_end_y=y-dx*text_height+dy*text_width

        rect_width=abs(rect_end_x-rect_start_x)
        rect_height=abs(rect_end_y-rect_start_y)
        rect_start_x = min(rect_start_x, rect_end_x)
        rect_start_y = min(rect_start_y, rect_end_y)

        pivotx = x
        pivoty = y
        #x -= rect_width/2
        #y += rect_height/2

        shape_svg = " ".join(
            [
                "<text",
                "class='{class_}'",
                "text-anchor='{justify}'",
                "x='{x}' y='{y}'",
                "transform='rotate({rotation} {pivotx} {pivoty}) translate(0 0)'",
                "style='font-size:{font_size}px'",
                "{extra}",
                ">",
                "{shape_text}",
                "</text>",
            ]
        ).format(**locals())

        # Should the text be considered when computing the bounding box
        extend_bbox_by_text = True
        if extend_bbox_by_text:
            shape_bbox.add(Point(rect_start_x, rect_start_y))
            shape_bbox.add(Point(rect_start_x+rect_width, rect_start_y+rect_height))

            # Add the following to visualize the rectangle enclosing the text.
            # Note that the text is modified later to include the reference number 
            # of the element and the value (e.g. R -> R1, V -> 10K) so the box may 
            # not correctly enclose the modified labels.
            #shape_svg += " ".join(
            #    [
            #        "\n<rect",
            #        'x="{rect_start_x}" y="{rect_start_y}"',
            #        'width="{rect_width}" height="{rect_height}"',
            #        'style="stroke-width:{stroke_width}"',
            #        'class="$cell_id symbol none"',
            #        "/>",
            #    ]
            #).format(**locals())
            pass

    elif shape_type == "pin":
        x=shape["at"][0]
        y=-shape["at"][1]
        rotation=shape["at"][2]
        length=shape["length"]
        start, end, side = get_pin_info(x,y,rotation,length)
        points_str = "{start[0]}, {start[1]}, {end[0]}, {end[1]}".format(**locals())
        name = shape["name"]["misc"]
        number = shape["number"]["misc"]
        stroke= shape["stroke"]["type"]
        stroke_width= shape["stroke"]["width"]
        fill= shape["fill"]["type"]
        circle_stroke_width = 2*stroke_width
        shape_bbox.add(Point(*start))
        shape_bbox.add(Point(*end))
        shape_svg = " ".join(
                [
                    # Draw a dot at the tip of the pin
                    "<circle",
                    'cx="{end[0]}" cy="{end[1]}" r="{circle_stroke_width}"',
                    'style="stroke-width:{circle_stroke_width}"',
                    'class="$cell_id symbol {fill}"',
                    "/>",
                    # Draw the pin
                    "\n<polyline",
                    'points="{points_str}"',
                    'style="stroke-width:{stroke_width}"',
                    'class="$cell_id symbol {fill}"',
                    "/>",
                ]
            ).format(**locals())
    elif shape_type == "text":
        x = shape["at"][0]
        y = -shape["at"][1]
        rotation = shape["at"][2]
        font_size = shape["effects"]["font"]["size"][0]
        justify = shape["justify"]
        stroke= shape["stroke"]["type"]
        stroke_width= shape["stroke"]["width"]
        fill= shape["fill"]["type"]
        shape_text=shape["misc"][0]

        char_width = font_size*0.6
        rect_start_x=x
        rect_start_y=y

        text_width=len(shape_text)*char_width
        text_height=font_size

        dx = math.cos( math.radians(rotation))
        dy = math.sin( math.radians(rotation))

        rect_end_x=x+dx*text_width+dy*text_height
        rect_end_y=y-dx*text_height+dy*text_width

        rect_width=abs(rect_end_x-rect_start_x)
        rect_height=abs(rect_end_y-rect_start_y)
        rect_start_x = min(rect_start_x, rect_end_x)
        rect_start_y = min(rect_start_y, rect_end_y)

        pivotx = x
        pivoty = y

        shape_svg = " ".join(
            [
                "<text",
                "text-anchor='{justify}'",
                "x='{x}' y='{y}'",
                "transform='rotate({rotation} {pivotx} {pivoty}) translate(0 0)'",
                "style='font-size:{font_size}px'",
                ">",
                "{shape_text}",
                "</text>",
            ]
        ).format(**locals())

        # Should the text be considered when computing the bounding box
        extend_bbox_by_text = True
        if extend_bbox_by_text:
            shape_bbox.add(Point(rect_start_x, rect_start_y))
            shape_bbox.add(Point(rect_start_x+rect_width, rect_start_y+rect_height))

    else:
        raise RuntimeError("Unrecognized shape type: {shape_type}".format(**locals()))
    #print(shape_svg)
    return shape_svg, shape_bbox

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

    # Assemble and name the SVGs for all the part units.
    svg = []
    for unit in range(1, part.num_units):
        bbox = part.unit_bboxes[unit]
        bbox.add(part.unit_bboxes[0])

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


        class TxBBox:
            x=0
            y=0
            w=0
            h=0

        tx_bbox = TxBBox()
        tx_bbox.x = bbox.min.x
        tx_bbox.y = bbox.min.y
        tx_bbox.w = bbox.w
        tx_bbox.h = bbox.h
        if "H" in symtx:
            tx_bbox.x = -(bbox.min.x+bbox.w)
            tx_bbox.y = bbox.min.y
            tx_bbox.w = bbox.w
            tx_bbox.h = bbox.h
        elif "V" in symtx:
            tx_bbox.x = bbox.min.x
            tx_bbox.y = -(bbox.min.y+bbox.h)
            tx_bbox.w = bbox.w
            tx_bbox.h = bbox.h

        if "R" in symtx:
            newx = -(tx_bbox.y + tx_bbox.h)
            newy = tx_bbox.x
            neww = tx_bbox.h
            newh = tx_bbox.w
            tx_bbox.x = newx
            tx_bbox.y = newy
            tx_bbox.w = neww
            tx_bbox.h = newh
        elif "L" in symtx:
            newx = tx_bbox.y
            newy = -(tx_bbox.x + tx_bbox.w)
            neww = tx_bbox.h
            newh = tx_bbox.w
            tx_bbox.x = newx
            tx_bbox.y = newy
            tx_bbox.w = neww
            tx_bbox.h = newh

        tx_bbox.x *= scale
        tx_bbox.y *= scale
        tx_bbox.w *= scale
        tx_bbox.h *= scale

        bbox_scale = 1.0
        w_diff = tx_bbox.w*(1-bbox_scale)
        h_diff = tx_bbox.h*(1-bbox_scale)
        tx_bbox.x += w_diff/2.0
        tx_bbox.y += h_diff/2.0
        tx_bbox.w *= bbox_scale
        tx_bbox.h *= bbox_scale


        # Begin SVG for part unit. Translate it so the bbox.min is at (0,0).
        translate = bbox.min * -1
        translate = Point(tx_bbox.x, tx_bbox.y) * -1
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

        if "H" in symtx:
            scale_x = -1
            scale_y = 1
        elif "V" in symtx:
            scale_x = 1
            scale_y = -1
        else:
            scale_x = 1
            scale_y = 1

        if "R" in symtx:
            rotation = 90
        elif "L" in symtx:
            rotation = 270
        else:
            rotation = 0

        svg.append(
            " ".join(
                [
                    "<g",
                    'transform="scale({scale} {scale}) rotate({rotation} 0 0)"',
                    ">",
                ]
            ).format(**locals())
        )

        svg.append(
            " ".join(
                [
                    "<g",
                    'transform="scale({scale_x}, {scale_y})"',
                    ">",
                ]
            ).format(**locals())
        )
        # Everything from unit 0 gets added to all units
        for item in part.unit_svgs[0]:
            if "text" not in item:
                svg.append(item)
        for item in part.unit_svgs[unit]:
            if "text" not in item:
                svg.append(item)
        svg.append("</g>")

        for item in part.unit_svgs[0]:
            if "text" in item:
                svg.append(item)
        for item in part.unit_svgs[unit]:
            if "text" in item:
                svg.append(item)
        svg.append("</g>")

        # Place a visible bounding-box around symbol for trouble-shooting.
        show_bbox = False
        bbox_stroke_width = scale * 0.1
        if show_bbox:
            svg.append(
                " ".join(
                    [
                        "<rect",
                        'x="{tx_bbox.x}" y="{tx_bbox.y}"',
                        'width="{tx_bbox.w}" height="{tx_bbox.h}"',
                        'style="stroke-width:{bbox_stroke_width}; stroke:#f00"',
                        'class="$cell_id symbol"',
                        "/>",
                    ]
                ).format(**locals())
            )

        # Keep the pins out of the grouped text & graphics but adjust their coords
        # to account for moving the bbox.
        for pin_info in part.unit_pin_info[unit]:
            pin_pt = Point(pin_info.x, pin_info.y)

            #print("pin_pt", pin_pt)
            #print("symtx", symtx)
            side = pin_info.side
            if "H" in symtx:
                pin_pt.x = -pin_pt.x
                side = {
                        "right":"left",
                        "top":"top",
                        "left":"right",
                        "bottom":"bottom",
                        }[side]
            elif "V" in symtx:
                side = {
                        "right":"right",
                        "top":"bottom",
                        "left":"left",
                        "bottom":"top",
                        }[side]
                pin_pt.y = -pin_pt.y

            if "L" in symtx:
                side = {
                        "right":"top",
                        "top":"left",
                        "left":"bottom",
                        "bottom":"right",
                        }[side]
                newx = pin_pt.y
                pin_pt.y = -pin_pt.x
                pin_pt.x = newx
            elif "R" in symtx:
                side = {
                        "right":"bottom",
                        "top":"right",
                        "left":"top",
                        "bottom":"left",
                        }[side]
                newx = -pin_pt.y
                pin_pt.y = pin_pt.x
                pin_pt.x = newx

            pin_pt *= scale

            pid = pin_info.pid
            font_size = 12
            justify="left"
            pin_svg = " ".join([
                "<text",
                "text-anchor='{justify}'",
                "x='{pin_pt.x}' y='{pin_pt.y}'",
                "style='font-size:{font_size}px'",
                ">",
                "{pid}",
                #"{side}", # Uncomment this to visualize/verify which side the pin is on
                "</text>",
                '<g s:x="{pin_pt.x}" s:y="{pin_pt.y}" s:pid="{pid}" s:position="{side}">',
                '</g>']).format(
                **locals()
            )
            svg.append(pin_svg)

        # Finish SVG for part unit.
        svg.append("</g>\n")

    return "\n".join(svg)