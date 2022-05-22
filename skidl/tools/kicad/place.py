# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""
Autoplacer for arranging symbols in a schematic.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

__all__ = [
    "place",
    "PlacementFailure",
]

from builtins import range, zip
from collections import defaultdict
from enum import Enum, auto
from itertools import zip_longest, chain
from random import randint, choice

from future import standard_library

from ...logger import active_logger
from ...part import Part
from ...utilities import *
from .common import *
from .geometry import *
from .route import *

standard_library.install_aliases()

###################################################################
#
# OVERVIEW OF AUTOPLACER
#
# The input is a Node containing parts, each with a bounding box.
#
# The positions of each part are set.
#
###################################################################

def draw_net(net, parts, scr, tx, font):
    pts = []
    for pin in net.pins:
        part = pin.part
        if part in parts:
            pt = pin.pt.dot(part.tx)
            pts.append(pt)
    for pt1, pt2 in zip(pts[:-1], pts[1:]):
        draw_seg(Segment(pt1, pt2), scr, tx, thickness=2, dot_radius=5)

def part_force(part, parts, nets):
    anchor_pts = defaultdict(list)
    pulling_pts = defaultdict(list)
    for net in nets:
        for pin in net.pins:
            if pin.part is part:
                anchor_pts[net].append(pin.pt.dot(part.tx))
            else:
                pulling_pts[net].append(pin.pt.dot(pin.part.tx))
    force = Vector(0,0)
    for net in anchor_pts.keys():
        for anchor_pt in anchor_pts[net]:
            for pulling_pt in pulling_pts[net]:
                force += pulling_pt - anchor_pt
    return force/20

def draw_force(part, parts, nets, scr, tx, font):
    force = part_force(part, parts, nets)
    anchor = part.bbox.ctr.dot(part.tx)
    draw_seg(Segment(anchor, anchor+force), scr, tx, color=(128,0,0), thickness=5, dot_radius=0)


def place(node, flags=["draw", "draw_switchbox", "draw_routing"]):
    """Place the parts in the node.

    Steps:
        1. ...
        2. ...

    Args:
        node (Node): Hierarchical node containing the parts to be placed.
        flags (list): List of text flags to control drawing of placement
            for debugging purposes. Available flags are "draw", "draw_routing".

    Returns:
        The Node with the part positions set.
    """

    # Exit if no parts to route.
    if not node.parts:
        return node

    # Extract list of nets internal to the node for routing.
    processed_nets = []
    internal_nets = []
    for part in node.parts:
        for part_pin in part:

            # A label means net is stubbed so there won't be any explicit wires.
            if len(part_pin.label) > 0:
                continue

            # No explicit wires if the pin is not connected to anything.
            if not part_pin.is_connected():
                continue

            net = part_pin.net

            if net in processed_nets:
                continue

            processed_nets.append(net)

            # No explicit wires for power nets.
            if net.netclass == "Power":
                continue

            def is_internal(net):

                # Determine if all the pins on this net reside in the node.
                for net_pin in net.pins:

                    # Don't consider stubs.
                    if len(net_pin.label) > 0:
                        continue

                    # If a pin is outside this node, then the net is not internal.
                    if net_pin.part.hierarchy != part_pin.part.hierarchy:
                        return False

                # All pins are within the node, so the net is internal.
                return True

            if is_internal(net):
                internal_nets.append(net)

    # Exit if no nets to route.
    if not internal_nets:
        pass

    # If enabled, draw the global and detailed routing for debug purposes.
    if "draw" in flags:

        bbox = BBox()
        for part in node.parts:
            tx_bbox = part.bbox.dot(part.tx)
            bbox.add(tx_bbox)

        draw_scr, draw_tx, draw_font = draw_start(bbox)

        # Draw parts.
        for part in node.parts:
            draw_part(part, draw_scr, draw_tx, draw_font)

        for part in node.parts:
            draw_force(part, node.parts, internal_nets, draw_scr, draw_tx, draw_font)

        for net in internal_nets:
            draw_net(net, node.parts, draw_scr, draw_tx, draw_font)

        draw_end()

    return node
