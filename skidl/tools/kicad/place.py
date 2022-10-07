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
import functools
import itertools
import math
import random

from future import standard_library

from ...logger import active_logger
from ...part import Part
from ...pin import Pin
from ...utilities import *
from .common import GRID
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


def list_parts(parts):
    part_refs = [part.ref for part in parts]
    print(", ".join(part_refs))


def draw_force(part, force, scr, tx, font, color=(128, 0, 0)):
    force *= 200
    anchor = part.bbox.ctr.dot(part.tx)
    draw_seg(
        Segment(anchor, anchor + force), scr, tx, color=color, thickness=5, dot_radius=5
    )


def draw_placement(parts, nets, scr, tx, font):
    draw_clear(scr)
    for part in parts:
        draw_part(part, scr, tx, font)
    for net in nets:
        draw_net(net, parts, scr, tx, font)
    draw_redraw()


def random_placement(parts):
    """Randomly place parts within an appropriately-sized area.

    Args:
        parts (list): List of Parts to place.
    """

    # Compute appropriate size to hold the parts based on their areas.
    area = 0
    for part in parts:
        area += part.bbox.area
    side = 3 * math.sqrt(area)  # Multiplier is ad-hoc.

    # Place parts randomly within area.
    for part in parts:
        part.tx.origin = Point(random.random() * side, random.random() * side)


def get_unsnapped_pt(part):
    try:
        return part.pins[0].pt.dot(part.tx)
    except AttributeError:
        try:
            return part.bbox.dot(part.tx).ctr
        except AttributeError:
            return part.ctr


def snap_to_grid(part):
    """Snap part to grid.

    Args:
        part (Part): Part to snap to grid.
    """

    pt = get_unsnapped_pt(part)
    snap_pt = pt.snap(GRID)
    mv = snap_pt - pt
    snap_tx = Tx(dx=mv.x, dy=mv.y)
    part.tx = part.tx.dot(snap_tx)
    return


use_mass = False
use_fanout_1 = False
use_fanout_2 = False


def adjust_orientations(parts, nets, alpha):
    for part in parts:
        smallest_force = float("inf")
        for i in range(2):
            for j in range(4):
                force = total_force(part, parts, nets, alpha)
                if force.magnitude < smallest_force:
                    smallest_force = frc.magnitude
                    smallest_tx = copy(part.tx)
                part.tx.rot_cw_90()
            part.tx.flip_x()
        part.tx = smallest_tx


def add_anchor_and_pull_pins(parts, nets):
    """Add positions of anchor and pull pins for attractive net forces between parts.

    Args:
        part (list): List of movable parts.
        nets (list): List of attractive nets between parts.
    """

    for part in parts:

        # These store the anchor pins where each net attaches to the given part
        # and the pulling pins where each net attaches to other parts.
        anchor_pins = defaultdict(list)
        pull_pins = defaultdict(list)

        # Find anchor pins on the part and pulling pins on other parts.
        for part_pin in part.pins:
            net = part_pin.net
            if net in nets:
                # Only find anchor/pulling points on active internal nets.
                for pin in net.pins:
                    if pin.part is part:
                        # Anchor parts for this net are on the given part.
                        anchor_pins[net].append(pin)
                    elif pin.part in parts:
                        # Everything else is a pulling point, but it has to
                        # be on a part that is in the set of movable parts.
                        pull_pins[net].append(pin)

        # Store the anchor & pulling points in the Part object.
        part.anchor_pins = anchor_pins
        part.pull_pins = pull_pins


def rmv_anchor_and_pull_pins(parts):
    """Remove anchor and pull pin information from Part objects.

    Args:
        parts (list): List of movable parts.
    """

    for part in parts:
        delattr(part, "anchor_pins")
        delattr(part, "pull_pins")


def net_force(part, nets):
    """Compute attractive force on a part from all the other parts connected to it.

    Args:
        part (Part): Part affected by forces from other connected parts.
        nets (list): List of active internal nets connecting parts.

    Returns:
        Vector: Force upon given part.
    """

    anchor_pins = part.anchor_pins
    pull_pins = part.pull_pins

    # Compute the combined force of all the anchor/pulling points on each net.
    total_force = Vector(0, 0)
    for net in anchor_pins.keys():

        if use_fanout_1:
            try:
                net_frc = 1 / (len(net.pins) - 1) ** 3
            except ZeroDivisionError:
                net_frc = 1
        elif use_fanout_2:
            if len(net.pins) > 4:
                net_frc = 0
            else:
                net_frc = 1
        else:
            net_frc = 1

        for anchor_pin in anchor_pins[net]:
            anchor_pt = anchor_pin.pt.dot(anchor_pin.part.tx)
            for pull_pin in pull_pins[net]:
                pull_pt = pull_pin.pt.dot(pull_pin.part.tx)
                # Force from pulling to anchor point is proportional to distance.
                total_force += (pull_pt - anchor_pt) * net_frc

    if use_mass:
        return total_force / len(part.pins)
    else:
        return total_force


def overlap_force(part, parts):
    """Compute the repulsive force on a part from overlapping other parts.

    Args:
        part (Part): Part affected by forces from other overlapping parts.
        parts (list): List of parts to check for overlaps.

    Returns:
        Vector: Force upon given part.
    """

    total_force = Vector(0, 0)

    part_bbox = part.bbox.dot(part.tx)
    for other_part in set(parts) - {part}:
        other_part_bbox = other_part.bbox.dot(other_part.tx)

        # No force unless parts overlap.
        if part_bbox.intersects(other_part_bbox):

            # Compute the movement needed to clear the bboxes in left/right/up/down directions.
            # Move right edge of part to the left of other part's left edge.
            mv_left = other_part_bbox.ll - part_bbox.lr
            # Move left edge of part to the right of other part's right edge.
            mv_right = other_part_bbox.lr - part_bbox.ll
            # Move bottom edge of part above other part's upper edge.
            mv_up = other_part_bbox.ul - part_bbox.ll
            # Move upper edge of part below other part's bottom edge.
            mv_down = other_part_bbox.ll - part_bbox.ul

            # Find the minimal movements in the left/right and up/down directions.
            mv_lr = mv_left if abs(mv_left.x) < abs(mv_right.x) else mv_right
            mv_ud = mv_up if abs(mv_up.y) < abs(mv_down.y) else mv_down

            # Remove any orthogonal component of the left/right and up/down movements.
            mv_lr.y = 0  # Remove up/down component.
            mv_ud.x = 0  # Remove left/right component.

            # Pick the smaller of the left/right and up/down movements.
            mv = mv_lr if abs(mv_lr.x) < abs(mv_ud.y) else mv_ud

            # Add movement for this part overlap to the total force.
            total_force += mv

    return total_force


def total_net_force(part, parts, nets, alpha):
    """Compute the total of the net attractive and overlap repulsive forces on a part.

    Args:
        part (Part): Part affected by forces from other overlapping parts.
        parts (list): List of parts to check for overlaps.
        nets (list): List of nets connecting parts.
        alpha (float): Proportion of the total that is the overlap force (range [0,1]).

    Returns:
        Vector: Weighted total of net attractive and overlap repulsion forces.
    """
    return (1 - alpha) * net_force(part, nets) + alpha * overlap_force(part, parts)


def similarity_force(part, parts, similarity):
    """Compute attractive force on a part from all the other parts connected to it.

    Args:
        part (Part): Part affected by forces from other connected parts.
        parts (list): List of parts to check for overlaps.
        similarity (dict): Similarity score for any pair of parts used as keys.

    Returns:
        Vector: Force upon given part.
    """

    # These store the anchor points where each net attaches to the given part
    # and the pulling points where each net attaches to other parts.
    anchor_pt = part.anchor_pin.pt.dot(part.tx)

    # Compute the combined force of all the anchor/pulling points on each net.
    total_force = Vector(0, 0)
    for other in set(parts) - {part}:
        pull_pt = other.anchor_pin.pt.dot(other.tx)
        # Force from pulling to anchor point is proportional to part similarity and distance.
        total_force += (pull_pt - anchor_pt) * similarity[part][other]

    return total_force


def total_similarity_force(part, parts, similarity, alpha):
    """Compute the total of the net attractive and overlap repulsive forces on a part.

    Args:
        part (Part): Part affected by forces from other overlapping parts.
        parts (list): List of parts to check for overlaps.
        similarity (dict): Similarity score for any pair of parts used as keys.
        alpha (float): Proportion of the total that is the overlap force (range [0,1]).

    Returns:
        Vector: Weighted total of net attractive and overlap repulsion forces.
    """
    return (1 - alpha) * similarity_force(
        part, parts, similarity
    ) + alpha * overlap_force(part, parts)


def push_and_pull(parts, nets, force_func, speed, scr, tx, font):
    """Move parts under influence of attracting nets and repulsive part overlaps.

    Args:
        parts (list): List of Parts.
        nets (list): List of nets that interconnect parts.
        force_func:
        speed (float): How fast parts move under the influence of forces.
        scr (PyGame screen): Screen object for PyGame debug drawing.
        tx (Tx): Transformation matrix from real to screen coords.
        font (PyGame font): Font for rendering text.
    """

    if len(parts) <= 1:
        # No need to do placement if there's less than two parts.
        return

    # Keep one part stationary to serve as an anchor for all the rest.
    mobile_parts = parts[:-1]

    # Arrange parts under influence of net attractions and part overlaps.
    prev_mobility = 0  # Stores part mobility from previous iteration.
    num_iters = round(100 / speed)
    iter = 0
    while iter < num_iters:
        alpha = iter / num_iters  # Attraction/repulsion weighting.
        mobility = 0  # Stores total part movement this iteration.
        random.shuffle(mobile_parts)  # Move parts in random order.
        for part in mobile_parts:
            force = force_func(part, alpha=alpha)
            mv_dist = force * 0.5 * speed  # 0.5 is ad-hoc.
            mobility += mv_dist.magnitude
            mv_tx = Tx(dx=mv_dist.x, dy=mv_dist.y)
            part.tx = part.tx.dot(mv_tx)
        if mobility < prev_mobility / 2:
            # Parts aren't moving much, so make a bigger inc
            # of iter to decrease alpha which might lead to more
            # movement as the balance of attractive/repulsive forces
            # changes. Also keep the previous mobility as a baseline
            # to compare against instead of updating with the
            # current low mobility.
            iter += 4
        else:
            # Parts are moving adequately, so proceed normally.
            iter += 1
            prev_mobility = mobility
        if scr:
            # Draw current part placement for debugging purposes.
            draw_placement(parts, nets, scr, tx, font)


def remove_overlaps(parts, nets, scr, tx, font):
    """Remove any overlaps using horz/vert grid movements.

    Args:
        parts (list): List of Parts.
        nets (list): List of nets that interconnect parts.
        scr (PyGame screen): Screen object for PyGame debug drawing.
        tx (Tx): Transformation matrix from real to screen coords.
        font (PyGame font): Font for rendering text.
    """

    if len(parts) <= 1:
        # No need to do placement if there's less than two parts.
        return

    # Keep one part stationary to serve as an anchor for all the rest.
    mobile_parts = parts[:-1]

    overlaps = True
    while overlaps:
        overlaps = False
        random.shuffle(mobile_parts)
        for part in mobile_parts:
            shove_force = overlap_force(part, parts)
            if shove_force.magnitude > 0:
                overlaps = True
                shove_tx = Tx()
                if shove_force.x < 0:
                    shove_tx.dx = -GRID
                elif shove_force.x > 0:
                    shove_tx.dx = GRID
                if shove_force.y < 0:
                    shove_tx.dy = -GRID
                elif shove_force.y > 0:
                    shove_tx.dy = GRID
                part.tx = part.tx.dot(shove_tx)
        if scr:
            draw_placement(parts, nets, scr, tx, font)


def slip_and_slide(parts, nets, scr, tx, font):
    """Move parts on horz/vert grid looking for improvements without causing overlaps.

    Args:
        parts (list): List of Parts.
        nets (list): List of nets that interconnect parts.
        scr (PyGame screen): Screen object for PyGame debug drawing.
        tx (Tx): Transformation matrix from real to screen coords.
        font (PyGame font): Font for rendering text.
    """

    if len(parts) <= 1:
        # No need to do placement if there's less than two parts.
        return

    if not nets:
        # No need to do this if there are no nets attracting parts together.
        return

    # Keep one part stationary to serve as an anchor for all the rest.
    mobile_parts = parts[:-1]

    moved = True
    while moved:
        moved = False
        random.shuffle(mobile_parts)
        for part in mobile_parts:
            smallest_force = net_force(part, nets).magnitude
            best_tx = copy(part.tx)
            for dx, dy in ((-GRID, 0), (GRID, GRID), (GRID, -GRID), (-GRID, -GRID)):
                mv_tx = Tx(dx=dx, dy=dy)
                part.tx = part.tx.dot(mv_tx)
                force = net_force(part, nets).magnitude
                if force < smallest_force:
                    if overlap_force(part, parts).magnitude == 0:
                        smallest_force = force
                        best_tx = copy(part.tx)
                        moved = True
            part.tx = best_tx
        if scr:
            draw_placement(parts, nets, scr, tx, font)


def evolve_placement(parts, nets, force_func, speed, scr=None, tx=None, font=None):
    """Evolve part placement looking for optimum using force function.

    Args:
        parts (list): List of Parts.
        nets (list): List of nets that interconnect parts.
        force_func (function): Computes the force affecting part positions.
        speed (float): Amount of part movement per unit of force.
        scr (PyGame screen): Screen object for PyGame debug drawing.
        tx (Tx): Transformation matrix from real to screen coords.
        font (PyGame font): Font for rendering text.
    """

    # Force-directed placement.
    push_and_pull(parts, nets, force_func, speed, scr, tx, font)

    # Snap parts to grid.
    for part in parts:
        snap_to_grid(part)

    # Remove part overlaps.
    remove_overlaps(parts, nets, scr, tx, font)

    # Look for local improvements.
    slip_and_slide(parts, nets, scr, tx, font)


def group_parts(parts, options=[]):
    if not parts:
        return [], [], []

    # Extract list of nets internal to the node.
    processed_nets = []
    internal_nets = []
    for part in parts:
        for part_pin in part:

            # A label means net is stubbed so there won't be any explicit wires.
            if "keep_stubs" not in options:
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
            # TODO: Is this necessary?
            if (
                net.netclass == "Power"
                or "vcc" in net.name.lower()
                or "gnd" in net.name.lower()
            ) and "remove_power" in options:
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

    if "remove_high_fanout" in options:
        import statistics

        fanouts = [len(net) for net in internal_nets]
        try:
            fanout_mean = statistics.mean(fanouts)
            fanout_stdev = statistics.stdev(fanouts)
        except statistics.StatisticsError:
            pass
        else:
            fanout_threshold = fanout_mean + 2 * fanout_stdev
            internal_nets = [
                net for net in internal_nets if len(net) < fanout_threshold
            ]

    # Group all the parts that have some interconnection to each other.
    # Start with groups of parts on each individual net, and then join groups that
    # have parts in common.
    connected_parts = [
        set(pin.part for pin in net.pins if pin.part in parts) for net in internal_nets
    ]
    for i in range(len(connected_parts) - 1):
        group1 = connected_parts[i]
        for j in range(i + 1, len(connected_parts)):
            group2 = connected_parts[j]
            if group1 & group2:
                # If part groups intersect, collect union of parts into one group
                # and empty-out the other.
                connected_parts[j] = connected_parts[i] | connected_parts[j]
                connected_parts[i] = set()
                # No need to check against this group any more since it has been
                # unioned into a group that will be checked later in the loop.
                break
    # Remove any empty groups that were unioned into other groups.
    connected_parts = [group for group in connected_parts if group]

    # Find parts that aren't connected to anything.
    floating_parts = set(parts) - set(itertools.chain(*connected_parts))

    return connected_parts, internal_nets, floating_parts


speed = 0.5
speed_mult = 2.0


def place_parts(connected_parts, internal_nets, floating_parts, options):
    """Place individual parts.

    Args:
        connected_parts (list): List of Part sets connected by nets.
        internal_nets (list): List of Nets connecting parts.
        floating_parts (set): Set of Parts not connected by any of the internal nets.
        options (list): List of strings that enable/disable functions.

    Returns:
        tuple: Connected and floating parts with placement information.
    """

    # Place each group of connected parts.
    for group in connected_parts:
        group = list(group)

        # Randomly place connected parts.
        random_placement(group)

        if "draw" in options:
            # Draw the global and detailed routing for debug purposes.
            bbox = BBox()
            for part in group:
                tx_bbox = part.bbox.dot(part.tx)
                bbox.add(tx_bbox)
            draw_scr, draw_tx, draw_font = draw_start(bbox)
        else:
            draw_scr, draw_tx, draw_font = None, None, None

        # Set anchor and pull pins that determine attractive forces between parts.
        add_anchor_and_pull_pins(group, internal_nets)

        # Do force-directed placement of the parts in the group.
        force_func = functools.partial(total_net_force, parts=group, nets=internal_nets)
        evolve_placement(
            group,
            internal_nets,
            force_func,
            speed=speed,
            scr=draw_scr,
            tx=draw_tx,
            font=draw_font,
        )
        evolve_placement(
            group,
            internal_nets,
            force_func,
            speed=speed * speed_mult,
            scr=draw_scr,
            tx=draw_tx,
            font=draw_font,
        )

        # Remove the anchor and pull pins from the parts.
        rmv_anchor_and_pull_pins(group)

        if "draw" in options:
            draw_end()

    # Place the floating parts.
    if floating_parts:

        # For non-connected parts, do placement based on their similarity to each other.
        part_similarity = defaultdict(lambda: defaultdict(lambda: 0))
        for part in floating_parts:
            for other_part in floating_parts - {part}:
                # TODO: Get similarity forces right-sized.
                part_similarity[part][other_part] = part.similarity(other_part) / 10
                # part_similarity[part][other_part] = 0.1

            # Select the top-most pin in each part as the anchor point for force-directed placement.
            tx = part.tx
            part.anchor_pin = max(part, key=lambda pin: pin.pt.dot(tx).y)

        floating_parts = list(floating_parts)

        # Randomly place the floating parts.
        random_placement(floating_parts)

        if "draw" in options:
            # Draw the global and detailed routing for debug purposes.
            bbox = BBox()
            for part in floating_parts:
                tx_bbox = part.bbox.dot(part.tx)
                bbox.add(tx_bbox)
            draw_scr, draw_tx, draw_font = draw_start(bbox)
        else:
            draw_scr, draw_tx, draw_font = None, None, None

        force_func = functools.partial(
            total_similarity_force, parts=floating_parts, similarity=part_similarity
        )
        evolve_placement(
            floating_parts,
            [],
            force_func,
            speed=speed,
            scr=draw_scr,
            tx=draw_tx,
            font=draw_font,
        )

        if "draw" in options:
            draw_end()

    return connected_parts, floating_parts


def place_blocks(connected_parts, floating_parts, children, options):
    """Place blocks of parts and hierarchical sheets.

    Args:
        connected_parts (list): List of Part sets connected by nets.
        floating_parts (set): Set of Parts not connected by any of the internal nets.
        non_sheets (list): Hierarchical set of Parts that are visible.
        sheets (list): List of hierarchical blocks.
        options (list): List of strings that enable/disable functions.
    """

    class PartBlock:
        def __init__(self, src, bbox, anchor_pt, snap_pt):
            self.src = src
            self.bbox = bbox
            self.anchor_pt = anchor_pt
            self.anchor_pin = Pin()
            self.anchor_pin.pt = anchor_pt
            self.snap_pt = snap_pt
            self.tx = Tx()
            self.ref = "REF"

        def update(self):
            """Apply the transformation matrix to the objects."""
            for part in self.parts:
                part.tx = part.tx.dot(self.tx)

    part_blocks = []
    for part_list in connected_parts:
        if not part_list:
            continue
        bbox = BBox()
        for part in part_list:
            bbox.add(part.bbox.dot(part.tx))
        snap_part = list(part_list)[0]
        blk = PartBlock(part_list, bbox, bbox.ctr, get_unsnapped_pt(snap_part))
        part_blocks.append(blk)
    for part_list in (floating_parts,):
        if not part_list:
            continue
        bbox = BBox()
        for part in part_list:
            bbox.add(part.bbox.dot(part.tx))
        snap_part = list(part_list)[0]
        blk = PartBlock(part_list, bbox, bbox.ctr, get_unsnapped_pt(snap_part))
        part_blocks.append(blk)
    for child in children:
        bbox = child.calc_bbox()
        if child.flattened:
            blk = PartBlock(child, bbox, bbox.ctr, get_unsnapped_pt(child.parts[0]))
        else:
            blk = PartBlock(child, bbox, bbox.ctr, bbox.ctr)
        part_blocks.append(blk)

    blk_attr = defaultdict(lambda: defaultdict(lambda: 0))
    for blk in part_blocks:
        for other_blk in part_blocks:
            if blk is other_blk:
                continue
            blk_attr[blk][other_blk] = 0.1  # TODO: Replace adhoc value.

    random_placement(part_blocks)
    if "draw" in options:
        # Draw the global and detailed routing for debug purposes.
        bbox = BBox()
        for blk in part_blocks:
            tx_bbox = blk.bbox.dot(blk.tx)
            bbox.add(tx_bbox)
        draw_scr, draw_tx, draw_font = draw_start(bbox)
    else:
        draw_scr, draw_tx, draw_font = None, None, None

    force_func = functools.partial(
        total_similarity_force, parts=part_blocks, similarity=blk_attr
    )
    evolve_placement(
        part_blocks,
        [],
        force_func,
        speed=speed,
        scr=draw_scr,
        tx=draw_tx,
        font=draw_font,
    )

    if "draw" in options:
        draw_end()

    for blk in part_blocks:
        try:
            blk.src.tx = blk.tx
        except AttributeError:
            for part in blk.src:
                part.tx = part.tx.dot(blk.tx)


class Placer:
    """Mixin to add routing function to Node class."""

    def place(node, options=["no_keep_stubs", "remove_power"]):
        # def place(node, options=["draw","no_keep_stubs","remove_power"]):
        """Place the parts and children in this node.

        Steps:
            1. ...
            2. ...

        Args:
            node (Node): Hierarchical node containing the parts and children to be placed.
            options (list): List of text options to control drawing of placement
                for debugging purposes. Available options are "draw".
        """

        # Place children of this node.
        for child in node.children.values():
            child.place()

        # Use the larger bounding box when placing parts in this node.
        for part in node.parts:
            part.bbox = part.place_bbox

        # Place parts in this node.
        connected_parts, internal_nets, floating_parts = group_parts(
            node.parts, options
        )
        place_parts(connected_parts, internal_nets, floating_parts, options)

        # Place blocks of parts in this node.
        place_blocks(connected_parts, floating_parts, node.children.values(), options)

        # Calculate the bounding box for the node after placement of parts and children.
        node.calc_bbox()
