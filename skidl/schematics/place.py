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
    "Placer",
    "PlacementFailure",
]

from builtins import range, zip
from collections import defaultdict
import functools
import itertools
import math
import random

from future import standard_library

from ..pin import Pin
from ..circuit import Circuit
from ..utilities import *
from .geometry import *
from .route import *
from .debug_draw import *

standard_library.install_aliases()

###################################################################
#
# OVERVIEW OF AUTOPLACER
#
# The input is a Node containing parts and child nodes, each with
# a bounding box.
#
# The positions of each part are set and then the block of parts
# is arranged with the blocks of the child nodes.
#
###################################################################

# Global constant placeholders defined by the particular backend tool.
# These will get filled-in when the placement function is activated.
GRID = 0
BLK_INT_PAD = 0
BLK_EXT_PAD = 0

def random_placement(parts):
    """Randomly place parts within an appropriately-sized area.

    Args:
        parts (list): List of Parts to place.
    """

    # Compute appropriate size to hold the parts based on their areas.
    area = 0
    for part in parts:
        area += part.place_bbox.area
    side = 3 * math.sqrt(area)  # Multiplier is ad-hoc.

    # Place parts randomly within area.
    for part in parts:
        part.tx.origin = Point(random.random() * side, random.random() * side)


def get_snap_pt(part_or_blk):
    """Get the point for snapping the Part or PartBlock to the grid.

    Args:
        part_or_blk (Part | PartBlock): Object with snap point.

    Returns:
        Point: Point for snapping to grid or None if no point found.
    """
    try:
        return part_or_blk.pins[0].pt
    except AttributeError:
        try:
            return part_or_blk.snap_pt
        except AttributeError:
            return None


def snap_to_grid(part_or_blk):
    """Snap Part or PartBlock to grid.

    Args:
        part (Part | PartBlk): Object to snap to grid.
    """

    # Get the position of the current snap point.
    pt = get_snap_pt(part_or_blk) * part_or_blk.tx

    # This is where the snap point should be on the grid.
    snap_pt = pt.snap(GRID)

    # This is the required movement to get on-grid.
    mv = snap_pt - pt

    # Update the object's transformation matrix.
    snap_tx = Tx(dx=mv.x, dy=mv.y)
    part_or_blk.tx *= snap_tx


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


def add_placement_bboxes(parts):
    """Expand part bounding boxes to include space for subsequent routing."""

    for part in parts:
        part.place_bbox = BBox()
        part.place_bbox.add(part.lbl_bbox)
        padding = {"U": 1, "D": 1, "L": 1, "R": 1}  # Min padding of 1 channel per side.
        for pin in part:
            if pin.stub is False and pin.is_connected():
                padding[pin.orientation] += 1
        part.place_bbox.add(
            part.place_bbox.max + Point(padding["L"], padding["D"]) * GRID
        )
        part.place_bbox.add(
            part.place_bbox.min - Point(padding["R"], padding["U"]) * GRID
        )


def rmv_placement_bboxes(parts):
    """Remove expanded bounding boxes."""

    for part in parts:
        try:
            del part.place_bbox
        except AttributeError:
            pass


def add_anchor_and_pull_pins(parts, nets):
    """Add positions of anchor and pull pins for attractive net forces between parts.

    Args:
        part (list): List of movable parts.
        nets (list): List of attractive nets between parts.
    """

    def add_place_pt(part, pin):
        """Add the point for a pin on the placement boundary of a part."""

        pin.route_pt = pin.pt  # For drawing of nets during debugging.
        pin.place_pt = Point(pin.pt.x, pin.pt.y)
        if pin.orientation == "U":
            pin.place_pt.y = part.place_bbox.min.y
        elif pin.orientation == "D":
            pin.place_pt.y = part.place_bbox.max.y
        elif pin.orientation == "L":
            pin.place_pt.x = part.place_bbox.max.x
        elif pin.orientation == "R":
            pin.place_pt.x = part.place_bbox.min.x
        else:
            raise RuntimeError("Unknown pin orientation.")

    for part in parts:

        # These store the anchor pins where each net attaches to the given part
        # and the pulling pins where each net attaches to other parts.
        anchor_pins = defaultdict(list)
        pull_pins = defaultdict(list)

        # Find anchor pins on the part and pulling pins on other parts.
        # TODO: instead of iterating through parts, iterate through pins of nets.
        for part_pin in part.pins:
            net = part_pin.net
            if net in nets:
                # Only find anchor/pulling points on active internal nets.
                for pin in net.pins:
                    if pin.part is part:
                        # Anchor parts for this net are on the given part.
                        anchor_pins[net].append(pin)
                        add_place_pt(part, pin)
                    elif pin.part in parts:
                        # Everything else is a pulling point, but it has to
                        # be on a part that is in the set of movable parts.
                        pull_pins[net].append(pin)

        # Store the anchor & pulling points in the Part object.
        part.anchor_pins = anchor_pins
        part.pull_pins = pull_pins

        # Part anchor pin for floating parts.
        try:
            # Set anchor at top-most pin so floating part tops will align.
            anchor_pin = max(part.pins, key=lambda pin: pin.pt.y)
            anchor_pin.place_pt = anchor_pin.pt
            part.anchor_pin = anchor_pin
        except ValueError:
            # Set anchor for part with no pins at all.
            part.anchor_pin = Pin()
            part.anchor_pin.place_pt = part.place_bbox.max


def rmv_anchor_and_pull_pins(parts):
    """Remove anchor and pull pin information from Part objects.

    Args:
        parts (list): List of movable parts.
    """

    for part in parts:
        for pin in part:
            try:
                del pin.route_pt
                del pin.place_pt
            except AttributeError:
                pass
        try:
            del part.anchor_pin
            del part.anchor_pins
            del part.pull_pins
        except AttributeError:
            pass


def net_force_dist(part, nets):
    """Compute attractive force on a part from all the other parts connected to it.

    Args:
        part (Part): Part affected by forces from other connected parts.
        nets (list): List of active internal nets connecting parts.

    Returns:
        Vector: Force upon given part.

    Notes:
        This force function needs careful adjustment of the speed parameter
        or else highly-connected parts are moved so quickly they jump over
        each other in an increasing cascade and actually move farther apart.
    """

    anchor_pins = part.anchor_pins
    pull_pins = part.pull_pins

    # Compute the combined force of all the anchor/pulling points on each net.
    total_force = Vector(0, 0)

    for net in anchor_pins.keys():
        for anchor_pin in anchor_pins[net]:
            anchor_pt = anchor_pin.place_pt * anchor_pin.part.tx
            for pull_pin in pull_pins[net]:
                pull_pt = pull_pin.place_pt * pull_pin.part.tx
                dist_vec = pull_pt - anchor_pt
                # Add force from pulling to anchor point that is proportional to distance.
                total_force += dist_vec

    return total_force


def net_force_dist_min(part, nets):
    """Compute attractive force on a part from all the other parts connected to it.

    Args:
        part (Part): Part affected by forces from other connected parts.
        nets (list): List of active internal nets connecting parts.

    Returns:
        Vector: Force upon given part.

    Notes:
        This force function reduces the movement of a part to the distance of
        its closest connection. This keeps the parts from jumping over each
        other, but can cause a problem if there are two or more clusters
        of parts on the same net in that the attraction between clusters
        is reduced to the attraction within each cluster and ignores the
        distance between clusters.
    """

    anchor_pins = part.anchor_pins
    pull_pins = part.pull_pins

    # Compute the combined force of all the anchor/pulling points on each net.
    total_force = Vector(0, 0)

    for net in anchor_pins.keys():

        min_dist = float("inf")
        for anchor_pin in anchor_pins[net]:
            anchor_pt = anchor_pin.place_pt * anchor_pin.part.tx
            for pull_pin in pull_pins[net]:
                pull_pt = pull_pin.place_pt * pull_pin.part.tx
                dist_vec = pull_pt - anchor_pt
                dist = dist_vec.magnitude
                min_dist = min(dist, min_dist)
                # Force from pulling to anchor point is proportional to distance.
                total_force += dist_vec

    if total_force.magnitude > min_dist:
        total_force *= min_dist / total_force.magnitude

    return total_force


def net_force_dist_avg(part, nets):
    """Compute attractive force on a part from all the other parts connected to it.

    Args:
        part (Part): Part affected by forces from other connected parts.
        nets (list): List of active internal nets connecting parts.

    Returns:
        Vector: Force upon given part.

    Notes:
        Maximum pulling force for each net can be no more than the average
        distance from the anchor point to the pulling points.
        Seems to solve the problems of net_force_dist() and net_force_dist_min().
    """

    anchor_pins = part.anchor_pins
    pull_pins = part.pull_pins

    # Compute the combined force of all the anchor/pulling points on each net.
    total_force = Vector(0, 0)

    for net in anchor_pins.keys():

        if not anchor_pins[net] or not pull_pins[net]:
            # Skip nets without pulling or anchor points.
            continue

        net_force = Vector(0, 0)
        dist_sum = 0
        dist_cnt = 0

        for anchor_pin in anchor_pins[net]:
            anchor_pt = anchor_pin.place_pt * anchor_pin.part.tx
            for pull_pin in pull_pins[net]:
                pull_pt = pull_pin.place_pt * pull_pin.part.tx
                dist_vec = pull_pt - anchor_pt
                dist_sum += dist_vec.magnitude
                dist_cnt += 1
                # Force from pulling to anchor point is proportional to distance.
                net_force += dist_vec

        avg_dist = dist_sum / dist_cnt
        if net_force.magnitude > avg_dist:
            net_force *= avg_dist / net_force.magnitude

        total_force += net_force

    return total_force


def net_force_fanout_1(part, nets):
    """Compute attractive force on a part from all the other parts connected to it.

    Args:
        part (Part): Part affected by forces from other connected parts.
        nets (list): List of active internal nets connecting parts.

    Returns:
        Vector: Force upon given part.

    Notes:
        Reduces the force by the cube of the number of pins on a net, thus
        reducing the influence of high-fanout nets.
    """

    anchor_pins = part.anchor_pins
    pull_pins = part.pull_pins

    # Compute the combined force of all the anchor/pulling points on each net.
    total_force = Vector(0, 0)
    for net in anchor_pins.keys():

        try:
            influence_factor = 1 / (len(net.pins) - 1) ** 3
        except ZeroDivisionError:
            influence_factor = 1

        for anchor_pin in anchor_pins[net]:
            anchor_pt = anchor_pin.place_pt * anchor_pin.part.tx
            for pull_pin in pull_pins[net]:
                pull_pt = pull_pin.place_pt * pull_pin.part.tx
                dist_vec = pull_pt - anchor_pt
                total_force += dist_vec * influence_factor

    return total_force


def net_force_fanout_2(part, nets):
    """Compute attractive force on a part from all the other parts connected to it.

    Args:
        part (Part): Part affected by forces from other connected parts.
        nets (list): List of active internal nets connecting parts.

    Returns:
        Vector: Force upon given part.

    Notes:
        Any net with more than four pins on it doesn't influence part placement,
        thus reducing the influence of high-fanout nets. This is not a very
        good solution.
    """

    anchor_pins = part.anchor_pins
    pull_pins = part.pull_pins

    # Compute the combined force of all the anchor/pulling points on each net.
    total_force = Vector(0, 0)
    for net in anchor_pins.keys():

        if len(net.pins) > 4:
            influence_factor = 0
        else:
            influence_factor = 1

        for anchor_pin in anchor_pins[net]:
            anchor_pt = anchor_pin.place_pt * anchor_pin.part.tx
            for pull_pin in pull_pins[net]:
                pull_pt = pull_pin.place_pt * pull_pin.part.tx
                dist_vec = pull_pt - anchor_pt
                total_force += dist_vec * influence_factor

    return total_force


# Select the net force method used for the attraction of parts during placement.
# net_force = net_force_fanout_1
net_force = net_force_dist_avg


def overlap_force(part, parts):
    """Compute the repulsive force on a part from overlapping other parts.

    Args:
        part (Part): Part affected by forces from other overlapping parts.
        parts (list): List of parts to check for overlaps.

    Returns:
        Vector: Force upon given part.
    """

    total_force = Vector(0, 0)

    part_bbox = part.place_bbox * part.tx
    for other_part in set(parts) - {part}:
        other_part_bbox = other_part.place_bbox * other_part.tx

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
    anchor_pt = part.anchor_pin.place_pt * part.tx

    # Compute the combined force of all the anchor/pulling points on each net.
    total_force = Vector(0, 0)
    for other in set(parts) - {part}:
        pull_pt = other.anchor_pin.place_pt * other.tx
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

    # Make list of parts that will be moved.
    # mobile_parts = parts[:-1]  # Keep one part stationary as an anchor.
    mobile_parts = parts[:]  # Move all parts.

    # Arrange parts under influence of net attractions and part overlaps.
    prev_mobility = 0  # Stores part mobility from previous iteration.
    num_iters = round(50 / speed)
    iter = 0
    while iter < num_iters:
        alpha = iter / num_iters  # Attraction/repulsion weighting.
        mobility = 0  # Stores total part movement this iteration.
        random.shuffle(mobile_parts)  # Move parts in random order.
        for part in mobile_parts:
            force = force_func(part, alpha=alpha)
            mv_dist = force * speed
            mobility += mv_dist.magnitude
            mv_tx = Tx(dx=mv_dist.x, dy=mv_dist.y)
            part.tx = part.tx * mv_tx
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

    # Make list of parts that will be moved.
    # mobile_parts = parts[:-1]  # Keep one part stationary as an anchor.
    mobile_parts = parts[:]  # Move all parts.

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
                part.tx = part.tx * shove_tx
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

    # Make list of parts that will be moved.
    # mobile_parts = parts[:-1]  # Keep one part stationary as an anchor.
    mobile_parts = parts[:]  # Move all parts.

    moved = True
    while moved:
        moved = False
        random.shuffle(mobile_parts)
        for part in mobile_parts:
            smallest_force = net_force(part, nets).magnitude
            best_tx = copy(part.tx)
            for dx, dy in ((-GRID, 0), (GRID, GRID), (GRID, -GRID), (-GRID, -GRID)):
                mv_tx = Tx(dx=dx, dy=dy)
                part.tx = part.tx * mv_tx
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


def group_parts(node, options=[]):
    """Group parts in the Node that are connected by internal nets

    Args:
        node (Node): Node with parts.
        options (list, optional): List of option strings. Defaults to [].

    Returns:
        list: List of lists of Parts that are connected.
        list: List of internal nets connecting parts.
        list: List of Parts that are not connected to anything (floating).
    """

    if not node.parts:
        return [], [], []

    # Extract list of nets having at least one pin in the node.
    internal_nets = node.get_internal_nets()

    # Remove some nets according to options.
    if "remove_power" in options:

        def is_pwr(net):
            return net.netclass == "Power" or "vcc" in net.name.lower() or "gnd" in net.name.lower()

        internal_nets = [net for net in internal_nets if not is_pwr(net)]

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
    # Start with groups of parts on each individual net.
    connected_parts = [
        set(pin.part for pin in net.pins if pin.part in node.parts) for net in internal_nets
    ]

    # Now join groups that have parts in common.
    for i in range(len(connected_parts) - 1):
        group1 = connected_parts[i]
        for j in range(i + 1, len(connected_parts)):
            group2 = connected_parts[j]
            if group1 & group2:
                # If part groups intersect, collect union of parts into one group
                # and empty-out the other.
                connected_parts[j] = connected_parts[i] | connected_parts[j]
                connected_parts[i] = set()
                # No need to check against group1 any more since it has been
                # unioned into group2 that will be checked later in the loop.
                break

    # Remove any empty groups that were unioned into other groups.
    connected_parts = [group for group in connected_parts if group]

    # Find parts that aren't connected to anything.
    floating_parts = set(node.parts) - set(itertools.chain(*connected_parts))

    return connected_parts, internal_nets, floating_parts


speed = 0.25
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

        # Add bboxes with surrounding area so parts are not butted against each other.
        add_placement_bboxes(group)

        # Set anchor and pull pins that determine attractive forces between parts.
        add_anchor_and_pull_pins(group, internal_nets)

        # Randomly place connected parts.
        random_placement(group)

        if "draw" in options:
            # Draw the placement for debug purposes.
            bbox = BBox()
            for part in group:
                tx_bbox = part.place_bbox * part.tx
                bbox.add(tx_bbox)
            draw_scr, draw_tx, draw_font = draw_start(bbox)
        else:
            draw_scr, draw_tx, draw_font = None, None, None

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

        if "draw" in options:
            draw_end()

        # Placement done so anchor and pull pins for each part are no longer needed.
        rmv_anchor_and_pull_pins(group)

        # Placement done, so placement bounding boxes for each part are no longer needed.
        rmv_placement_bboxes(group)

    # Place the floating parts.
    if floating_parts:

        floating_parts = list(floating_parts)

        # Add bboxes with surrounding area so parts are not butted against each other.
        add_placement_bboxes(floating_parts)

        # Set anchor and pull pins that determine attractive forces between similar parts.
        add_anchor_and_pull_pins(floating_parts, internal_nets)

        # Randomly place the floating parts.
        random_placement(floating_parts)

        if "draw" in options:
            # Compute the drawing area for the floating parts
            bbox = BBox()
            for part in floating_parts:
                tx_bbox = part.place_bbox * part.tx
                bbox.add(tx_bbox)
            draw_scr, draw_tx, draw_font = draw_start(bbox)
        else:
            draw_scr, draw_tx, draw_font = None, None, None

        # For non-connected parts, do placement based on their similarity to each other.
        part_similarity = defaultdict(lambda: defaultdict(lambda: 0))
        for part in floating_parts:
            for other_part in floating_parts:

                # Don't compute similarity of a part to itself.
                if other_part is part:
                    continue

                # TODO: Get similarity forces right-sized.
                part_similarity[part][other_part] = part.similarity(other_part) / 10
                # part_similarity[part][other_part] = 0.1

            # Select the top-most pin in each part as the anchor point for force-directed placement.
            # tx = part.tx
            # part.anchor_pin = max(part.anchor_pins, key=lambda pin: (pin.place_pt * tx).y)

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

        # Placement done so anchor and pull pins for each part are no longer needed.
        rmv_anchor_and_pull_pins(floating_parts)

        # Placement done, so placement bounding boxes for each part are no longer needed.
        rmv_placement_bboxes(floating_parts)

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
        def __init__(self, src, bbox, anchor_pt, snap_pt, tag):
            self.src = src
            self.place_bbox = bbox # FIXME: Is this needed if place_bbox includes room for routing?
            self.lbl_bbox = bbox  # Needed for drawing during debug.
            self.anchor_pt = anchor_pt
            self.anchor_pin = Pin()
            self.anchor_pin.place_pt = anchor_pt
            self.snap_pt = snap_pt
            self.tx = Tx()
            self.ref = "REF"
            self.tag = tag

    part_blocks = []
    for part_list in [
        floating_parts,
    ] + connected_parts:
        if not part_list:
            continue
        snap_pt = None
        bbox = BBox()
        for part in part_list:
            bbox.add(part.lbl_bbox * part.tx)
            if not snap_pt:
                snap_pt = get_snap_pt(part)
        tag = 2 if (part_list is floating_parts) else 1
        pad = BLK_EXT_PAD
        bbox = bbox.resize(Vector(pad, pad))
        blk = PartBlock(part_list, bbox, bbox.ctr, snap_pt, tag)
        part_blocks.append(blk)
    for child in children:
        snap_pt = child.get_snap_pt()
        if child.flattened:
            pad = BLK_INT_PAD + BLK_EXT_PAD
        else:
            pad = BLK_EXT_PAD
        bbox = child.calc_bbox().resize(Vector(pad, pad))
        if snap_pt:
            blk = PartBlock(child, bbox, bbox.ctr, snap_pt, 3)
        else:
            blk = PartBlock(child, bbox, bbox.ctr, bbox.ctr, 4)
        part_blocks.append(blk)

    # Re-label blocks with sequential tags (i.e., remove gaps).
    tags = {blk.tag for blk in part_blocks}
    tag_tbl = {old_tag: new_tag for old_tag, new_tag in zip(tags, range(len(tags)))}
    for blk in part_blocks:
        blk.tag = tag_tbl[blk.tag]

    # Tie the blocks together with strong links between blocks with the same tag,
    # and weaker links between blocks with tags that differ by 1. This ties similar
    # blocks together into "super blocks" and ties the super blocks into a linear
    # arrangement (1 -> 2 -> 3 ->...).
    blk_attr = defaultdict(lambda: defaultdict(lambda: 0))
    for blk in part_blocks:
        for other_blk in part_blocks:
            if blk is other_blk:
                continue
            if blk.tag == other_blk.tag:
                blk_attr[blk][other_blk] = 1
            elif abs(blk.tag - other_blk.tag) == 1:
                blk_attr[blk][other_blk] = 0.1
            else:
                blk_attr[blk][other_blk] = 0

    # Start off with a random placement of part blocks.
    random_placement(part_blocks)

    if "draw" in options:
        # Draw the global and detailed routing for debug purposes.
        bbox = BBox()
        for blk in part_blocks:
            tx_bbox = blk.place_bbox * blk.tx
            bbox.add(tx_bbox)
        draw_scr, draw_tx, draw_font = draw_start(bbox)
    else:
        draw_scr, draw_tx, draw_font = None, None, None

    # Arrange the part blocks with force-directed placement.
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

    # Apply the placement moves to the part blocks.
    for blk in part_blocks:
        try:
            blk.src.tx = blk.tx
        except AttributeError:
            for part in blk.src:
                part.tx = part.tx * blk.tx


class Placer:
    """Mixin to add place function to Node class."""

    def place(node, options=["no_keep_stubs", "remove_power"]):
    # def place(node, options=["draw", "no_keep_stubs", "remove_power"]):
        """Place the parts and children in this node.

        Args:
            node (Node): Hierarchical node containing the parts and children to be placed.
            options (list): List of text options to control drawing of placement
                for debugging purposes. Available options are "draw".
        """

        # Set the constants for the backend tool.
        global GRID, BLK_INT_PAD, BLK_EXT_PAD
        constants = Circuit.get_constants()
        GRID = constants.GRID
        BLK_INT_PAD = constants.BLK_INT_PAD
        BLK_EXT_PAD = constants.BLK_EXT_PAD

        # First, recursively place children of this node.
        for child in node.children.values():
            child.place()

        # Group parts into those that are connected by explicit nets and
        # those that float freely connected only by stub nets.
        connected_parts, internal_nets, floating_parts = group_parts(node, options)

        # Place node parts.
        place_parts(connected_parts, internal_nets, floating_parts, options)

        # Place blocks of parts in this node.
        place_blocks(connected_parts, floating_parts, node.children.values(), options)

        # Calculate the bounding box for the node after placement of parts and children.
        node.calc_bbox()

    def get_snap_pt(node):
        """Get a Point to use for snapping the node to the grid.

        Args:
            node (Node): The Node to which the snapping point applies.

        Returns:
            Point: The snapping point or None.
        """

        if node.flattened:

            # Look for a snapping point based on one of its parts.
            for part in node.parts:
                snap_pt = get_snap_pt(part)
                if snap_pt:
                    return snap_pt

            # If no part snapping point, look for one in its children.
            for child in node.children.values():
                if child.flattened:
                    snap_pt = child.get_snap_pt()
                    if snap_pt:
                        # Apply the child transformation to its snapping point.
                        return snap_pt * child.tx

        # No snapping point if node is not flattened or no parts in it or its children.
        return None
