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

import functools
import itertools
import math
import random
import sys
from builtins import range, zip
from collections import defaultdict, Counter
from copy import copy

from future import standard_library

from ..circuit import Circuit
from ..pin import Pin
from ..utilities import export_to_all, rmv_attr
from .debug_draw import draw_end, draw_pause, draw_placement, draw_start
from .geometry import BBox, Point, Tx, Vector

standard_library.install_aliases()

__all__ = [
    "PlacementFailure",
]


###################################################################
#
# OVERVIEW OF AUTOPLACER
#
# The input is a Node containing child nodes and parts. The parts in
# each child node are placed, and then the blocks for each child are
# placed along with the parts in this node.
#
# The individual parts in a node are separated into groups:
# 1) multiple groups of parts that are all interconnected by one or
# more nets, and 2) a single group of parts that are not connected
# by any explicit nets (i.e., floating parts).
#
# Each group of connected parts are placed using force-directed placement.
# Each net exerts an attractive force pulling parts together, and
# any overlap of parts exerts a repulsive force pushing them apart.
# Initially, the attractive force is dominant but, over time, it is
# decreased while the repulsive force is increased using a weighting
# factor. After that, any part overlaps are cleared and the parts
# are aligned to the routing grid.
#
# Force-directed placement is also used with the floating parts except
# the non-existent net forces are replaced by a measure of part similarity.
# This collects similar parts (such as bypass capacitors) together.
#
# The child-node blocks are then arranged with the blocks of connected
# and floating parts to arrive at a total placement for this node.
#
###################################################################


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


def add_placement_bboxes(parts, **options):
    """Expand part bounding boxes to include space for subsequent routing."""

    expansion_factor = options.get("expansion_factor", 1.0)
    for part in parts:

        # Placement bbox starts off with the part bbox (including any net labels).
        part.place_bbox = BBox()
        part.place_bbox.add(part.lbl_bbox)

        # Compute the routing area for each side based on the number of pins on each side.
        padding = {"U": 1, "D": 1, "L": 1, "R": 1}  # Min padding of 1 channel per side.
        for pin in part:
            if pin.stub is False and pin.is_connected():
                padding[pin.orientation] += 1

        # Add padding for routing to the right and upper sides.
        part.place_bbox.add(
            part.place_bbox.max
            + (Point(padding["L"], padding["D"]) * GRID * expansion_factor)
        )

        # Add padding for routing to the left and lower sides.
        part.place_bbox.add(
            part.place_bbox.min
            - (Point(padding["R"], padding["U"]) * GRID * expansion_factor)
        )


def rmv_placement_bboxes(parts):
    """Remove expanded bounding boxes."""

    rmv_attr(parts, "place_bbox")


def add_anchor_pull_pins(parts, nets, **options):
    """Add positions of anchor and pull pins for attractive net forces between parts.

    Args:
        part (list): List of movable parts.
        nets (list): List of attractive nets between parts.
        options (dict): Dict of options and values that enable/disable functions.
    """

    def add_place_pt(part, pin):
        """Add the point for a pin on the placement boundary of a part."""

        pin.route_pt = pin.pt  # For drawing of nets during debugging.
        pin.place_pt = Point(pin.pt.x, pin.pt.y)
        offset = 1 * GRID
        if pin.orientation == "U":
            pin.place_pt.y = part.lbl_bbox.min.y - offset
        elif pin.orientation == "D":
            pin.place_pt.y = part.lbl_bbox.max.y + offset
        elif pin.orientation == "L":
            pin.place_pt.x = part.lbl_bbox.max.x + offset
        elif pin.orientation == "R":
            pin.place_pt.x = part.lbl_bbox.min.x - offset
        else:
            raise RuntimeError("Unknown pin orientation.")

    # Add dicts for anchor and pull pins to each movable part.
    for part in parts:
        part.anchor_pins = defaultdict(list)
        part.pull_pins = defaultdict(list)

    if nets:
        # If nets exist, then these parts are interconnected so
        # assign pins on each net to part anchor and pull pin lists.
        for net in nets:

            # Get net pins that are on movable parts.
            pins = {pin for pin in net.pins if pin.part in parts}

            # Get the set of parts with pins on the net.
            net_parts = {pin.part for pin in pins}

            # Add each pin as an anchor on the part that contains it and
            # as a pull pin on all the other parts that will be pulled by this part.
            for pin in pins:
                pin.part.anchor_pins[net].append(pin)
                add_place_pt(pin.part, pin)
                for part in net_parts - {pin.part}:
                    part.pull_pins[net].append(pin)

    else:
        # There are no nets so these parts are floating freely.
        # Floating parts are all pulled by each other.
        all_pull_pins = []
        for part in parts:
            try:
                # Set anchor at top-most pin so floating part tops will align.
                anchor_pull_pin = max(part.pins, key=lambda pin: pin.pt.y)
                add_place_pt(part, anchor_pull_pin)
            except ValueError:
                # Set anchor for part with no pins at all.
                anchor_pull_pin = Pin()
                anchor_pull_pin.place_pt = part.place_bbox.max
            part.anchor_pins["similarity"] = [anchor_pull_pin]
            part.pull_pins["similarity"] = all_pull_pins
            all_pull_pins.append(anchor_pull_pin)


def trim_anchor_pull_pins(parts):
    """Selectively remove anchor and pull pins from Part objects.

    Args:
        parts (list): List of movable parts.
    """

    if options.get("trim_anchor_pull_pins"):
        for part in parts:

            # Some nets attach to multiple pins on the same part. Trim the
            # anchor and pull pins for each net to a single pin for each part.

            # Only leave one randomly-chosen anchor point for a net on each part.
            anchor_pins = part.anchor_pins
            for net in anchor_pins.keys():
                anchor_pins[net] = [
                    random.choice(anchor_pins[net]),
                ]
            for net in anchor_pins.keys():
                assert len(anchor_pins[net]) == 1

            # Remove nets that have unusually large number of pulling points.
            # import statistics
            # fanouts = [len(pins) for pins in pull_pins.values()]
            # stdev = statistics.pstdev(fanouts)
            # avg = statistics.fmean(fanouts)
            # threshold = avg + 1*stdev
            # anchor_pins = {net: pins for net, pins in anchor_pins.items() if len(pull_pins[net]) <= threshold}
            # pull_pins = {net: pins for net, pins in pull_pins.items() if len(pins) <= threshold}

            # # Only leave one randomly-chosen pulling point for a net on each part.
            # for net, pins in pull_pins.items():
            #     part_pins = defaultdict(list)
            #     for pin in pins:
            #         part_pins[pin.part].append(pin)
            #     pull_pins[net].clear()
            #     for prt in part_pins.keys():
            #         pull_pins[net].append(random.choice(part_pins[prt]))
            # for net, pins in pull_pins.items():
            #     prts = [pin.part for pin in pins]
            #     assert len(prts) == len(set(prts))


def rmv_anchor_and_pull_pins(parts):
    """Remove anchor and pull pin information from Part objects.

    Args:
        parts (list): List of movable parts.
    """

    for part in parts:
        for attr in ("route_pt", "place_pt"):
            rmv_attr(part.pins, attr)
    for attr in ("anchor_pins", "pull_pins"):
        rmv_attr(parts, attr)


def random_placement(parts):
    """Randomly place parts within an appropriately-sized area.

    Args:
        parts (list): List of Parts to place.
    """

    # Compute appropriate size to hold the parts based on their areas.
    area = 0
    for part in parts:
        area += part.place_bbox.area
    side = 3 * math.sqrt(area)  # FIXME: Multiplier is ad-hoc.

    # Place parts randomly within area.
    for part in parts:
        pt = Point(random.random() * side, random.random() * side)
        part.tx.move_to(pt)
        # The following setter doesn't work in Python 2.7.18.
        # part.tx.origin = Point(random.random() * side, random.random() * side)


def adjust_orientations(parts, **options):
    """Adjust orientation of parts.

    Args:
        parts (list): List of Parts to adjust.
        options (dict): Dict of options and values that enable/disable functions.
    """

    def find_best_orientation(part):
        # Each part has 8 possible orientations. Find the best of the 7 alternatives from the current one.

        # Store starting orientation and its cost.
        part.prev_tx = copy(part.tx)
        current_cost = net_tension(part, **options)

        # Now find the orientation that has the largest decrease in cost.
        best_delta_cost = float("inf")

        # Skip cost calculations for the starting orientation.
        skip_original_tx = True

        # Go through four rotations, then flip the part and go through the rotations again.
        for i in range(2):
            for j in range(4):

                if skip_original_tx:
                    # Skip the starting orientation but set flag to process the others.
                    skip_original_tx = False
                    delta_cost = 0

                else:
                    # Calculate the cost of the current orientation.
                    delta_cost = net_tension(part, **options) - current_cost
                    if delta_cost < best_delta_cost:
                        # Save the largest decrease in cost and the associated orientation.
                        best_delta_cost = delta_cost
                        best_tx = copy(part.tx)

                # Proceed to the next rotation.
                part.tx.rot_cw_90()

            # Flip the part and go through the rotations again.
            part.tx.flip_x()

        # Save the largest decrease in cost and the associated orientation.
        part.delta_cost = best_delta_cost
        part.delta_cost_tx = best_tx

        # Restore the original orientation.
        part.tx = part.prev_tx

    # Get the list of parts that don't have their orientations locked.
    movable_parts = [part for part in parts if not part.orientation_locked]

    if not movable_parts:
        # No movable parts, so exit without doing anything.
        return

    orientation_cost_history = []

    # Kernighan-Lin algorithm for finding near-optimal part orientations.
    # Because of the way the tension for part alignment is computed based on
    # the nearest part, it is possible for an infinite loop to occur.
    # Hence the ad-hoc loop limit.
    for _ in range(10):

        # Find the best part to move and move it until there are no more parts to move.
        moved_parts = []
        unmoved_parts = movable_parts[:]
        while unmoved_parts:

            # Find the best current orientation for each unmoved part.
            for part in unmoved_parts:
                find_best_orientation(part)

            # Find the part that has the largest decrease in cost.
            part_to_move = min(unmoved_parts, key=lambda p: p.delta_cost)

            # Reorient the part with the Tx that created the largest decrease in cost.
            part_to_move.tx = part_to_move.delta_cost_tx

            # Transfer the part from the unmoved to the moved part list.
            unmoved_parts.remove(part_to_move)
            moved_parts.append(part_to_move)

        # Find the point at which the cost reaches its lowest point.
        delta_costs = (part.delta_cost for part in moved_parts)
        try:
            cost_seq = list(itertools.accumulate(delta_costs))
        except AttributeError:
            # Python 2.7 doesn't have itertools.accumulate().
            cost_seq = list(delta_costs)
            for i in range(1, len(cost_seq)):
                cost_seq[i] = cost_seq[i - 1] + cost_seq[i]
        min_cost = min(cost_seq)
        min_index = cost_seq.index(min_cost)

        # Move all the parts after that point back to their starting positions.
        for part in moved_parts[min_index + 1 :]:
            part.tx = part.prev_tx

        orientation_cost_history.append(min_cost)

        # Terminate the search once the cost stops decreasing.
        if min_cost >= 0:
            break

    if options.get("show_orientation_cost"):
        import matplotlib.pyplot as plt

        plt.scatter(range(len(orientation_cost_history)), orientation_cost_history)
        plt.show()

    rmv_attr(parts, ("prev_tx", "delta_cost"))


def net_tension_dist(part, **options):
    """Calculate the tension of the nets trying to rotate/flip the part.

    Args:
        part (Part): Part affected by forces from other connected parts.
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        float: Total tension on the part.
    """

    # Compute the force for each net attached to the part.
    tension = 0.0
    for net, anchor_pins in part.anchor_pins.items():

        pull_pins = part.pull_pins[net]

        if not anchor_pins or not pull_pins:
            # Skip nets without pulling or anchor points.
            continue

        # Compute the net force acting on each anchor point on the part.
        for anchor_pin in anchor_pins:

            # Compute the anchor point's (x,y).
            anchor_pt = anchor_pin.place_pt * anchor_pin.part.tx

            # Find the dist from the anchor point to each pulling point.
            dists = [
                (anchor_pt - pp.place_pt * pp.part.tx).magnitude for pp in pull_pins
            ]

            # Only the closest pulling point affects the tension since that is
            # probably where the wire routing will go to.
            tension += min(dists)

    return tension


# Select the net tension method used for the adjusting the orientation of parts.
net_tension = net_tension_dist


def net_force_dist(part, **options):
    """Compute attractive force on a part from all the other parts connected to it.

    Args:
        part (Part): Part affected by forces from other connected parts.
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        Vector: Force upon given part.
    """

    anchor_pins = part.anchor_pins
    pull_pins = part.pull_pins

    # Compute the total force on the part from all the anchor/pulling points on each net.
    total_force = Vector(0, 0)
    normalizer = 0

    # Compute the force for each net attached to the part.
    for net in anchor_pins.keys():

        if not anchor_pins[net] or not pull_pins[net]:
            # Skip nets without pulling or anchor points.
            continue

        # Compute the net force acting on each anchor point on the part.
        for anchor_pin in anchor_pins[net]:

            # Compute the anchor point's (x,y).
            anchor_pt = anchor_pin.place_pt * anchor_pin.part.tx

            # Sum the vectors from the anchor point to each pulling point.
            for pull_pin in pull_pins[net]:

                # Compute the pulling point's (x,y).
                pull_pt = pull_pin.place_pt * pull_pin.part.tx

                total_force += pull_pt - anchor_pt
                normalizer += 1

    if options.get("normalize"):
        # Normalize the total force to adjust for parts with a lot of pins.
        normalizer = normalizer or 1  # Prevent div-by-zero.
        total_force /= normalizer

    return total_force


def net_force_inv_dist(part, **options):
    """Compute attractive force on a part from all the other parts connected to it.

    Args:
        part (Part): Part affected by forces from other connected parts.
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        Vector: Force upon given part.
    """

    anchor_pins = part.anchor_pins
    pull_pins = part.pull_pins

    # Compute the total force on the part from all the anchor/pulling points on each net.
    total_force = Vector(0, 0)
    normalizer = 0

    # Compute the force for each net attached to the part.
    for net in anchor_pins.keys():

        if not anchor_pins[net] or not pull_pins[net]:
            # Skip nets without pulling or anchor points.
            continue

        # Compute the net force acting on each anchor point on the part.
        for anchor_pin in anchor_pins[net]:

            # Compute the anchor point's (x,y).
            anchor_pt = anchor_pin.place_pt * anchor_pin.part.tx

            # Sum the vectors from the anchor point to each pulling point.
            for pull_pin in pull_pins[net]:

                # Compute the pulling point's (x,y).
                pull_pt = pull_pin.place_pt * pull_pin.part.tx

                vec = pull_pt - anchor_pt
                mag = vec.magnitude

                # total_force += vec.norm
                total_force += vec.norm / (mag + GRID)

                normalizer += 1

    if options.get("normalize"):
        # Normalize the total force to adjust for parts with a lot of pins.
        normalizer = normalizer or 1  # Prevent div-by-zero.
        total_force /= normalizer

    return total_force


def net_force_dist_avg(part, **options):
    """Compute attractive force on a part from all the other parts connected to it.

    Args:
        part (Part): Part affected by forces from other connected parts.
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        Vector: Force upon given part.
    """

    # Notes:
    #     Computing net force proportional to distance between part pins
    #     can lead to highly-connected parts moving quickly and jumping over
    #     each other because of the total accumulated force. This can lead
    #     to a cascade where the parts actually start moving farther apart.
    #
    #     Limiting the movement of a part to the distance of its closest
    #     connection keeps the parts from jumping over each
    #     other, but can cause a problem if there are two or more clusters
    #     of parts on the same net in that parts in a cluster are attracted
    #     to each other, but the overall clusters are not attracted to each other.
    #
    #     A compromise is to limit the maximum pulling force for each net to
    #     be no more than the average distance from the anchor point to the pulling points.
    #     This seems to solve some of the problems of the first two techniques.

    anchor_pins = part.anchor_pins
    pull_pins = part.pull_pins

    # Compute the total force on the part from all the anchor/pulling points on each net.
    total_force = Vector(0, 0)

    # Parts with a lot of pins can accumulate large net forces that move them very quickly.
    # Accumulate the number of individual net forces and use that to attenuate
    # the total force, effectively normalizing the forces between large & small parts.
    normalizer = 0

    # Compute the force for each net attached to the part.
    for net in anchor_pins.keys():

        if not anchor_pins[net] or not pull_pins[net]:
            # Skip nets without pulling or anchor points.
            continue

        # Initialize net force and average pin-to-pin distance.
        net_force = Vector(0, 0)
        dist_sum = 0
        dist_cnt = 0

        # Compute the net force acting on each anchor point on the part.
        for anchor_pin in anchor_pins[net]:

            # Compute the anchor point's (x,y).
            anchor_pt = anchor_pin.place_pt * anchor_pin.part.tx

            # Sum the forces from each pulling point on the anchor point.
            for pull_pin in pull_pins[net]:

                # Compute the pulling point's (x,y).
                pull_pt = pull_pin.place_pt * pull_pin.part.tx

                # Get the distance from the pull pt to the anchor point.
                dist_vec = pull_pt - anchor_pt

                # Update the values for computing the average distance.
                dist_sum += dist_vec.magnitude
                dist_cnt += 1

                # Force from pulling to anchor point is proportional to distance.
                net_force += dist_vec

            if options.get("fanout_attenuation"):
                # Reduce the influence of high-fanout nets.
                fanout = len(pull_pins[net])
                net_force /= fanout**2

        # Attenuate the net force if it's greater than the average distance btw anchor/pull pins.
        avg_dist = dist_sum / dist_cnt
        nt_frc_mag = net_force.magnitude
        if nt_frc_mag > avg_dist:
            net_force *= avg_dist / nt_frc_mag

        # Accumulate force from this net into the total force on the part.
        total_force += net_force

        # Increment the normalizer for every net force added to the total force.
        normalizer += 1

    if options.get("normalize"):
        # Normalize the total force to adjust for parts with a lot of pins.
        normalizer = normalizer or 1  # Prevent div-by-zero.
        total_force /= normalizer

    return total_force


# Select the net force method used for the attraction of parts during placement.
# net_force = net_force_dist
# net_force = net_force_inv_dist
net_force = net_force_dist_avg


def overlap_force(part, parts, **options):
    """Compute the repulsive force on a part from overlapping other parts.

    Args:
        part (Part): Part affected by forces from other overlapping parts.
        parts (list): List of parts to check for overlaps.
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        Vector: Force upon given part.
    """

    # Bounding box of given part.
    part_bbox = part.place_bbox * part.tx

    # Compute the overlap force of the bbox of this part with every other part.
    total_force = Vector(0, 0)
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

            # Pick the smaller of the left/right and up/down movements because that will
            # cause movement in the direction that will clear the overlap most quickly.
            mv = mv_lr if abs(mv_lr.x) < abs(mv_ud.y) else mv_ud

            # Add movement for this part overlap to the total force.
            total_force += mv

    return total_force


def total_part_force(part, parts, alpha, **options):
    """Compute the total of the attractive net and repulsive overlap forces on a part.

    Args:
        part (Part): Part affected by forces from other overlapping parts.
        parts (list): List of parts to check for overlaps.
        alpha (float): Proportion of the total that is the overlap force (range [0,1]).
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        Vector: Weighted total of net attractive and overlap repulsion forces.
    """
    if alpha == 0:
        return net_force(part, **options)
    elif alpha == 1:
        return overlap_force(part, parts, **options)
    else:
        nt_frc = net_force(part, **options)
        ov_frc = overlap_force(part, parts, **options)
        return (1 - alpha) * nt_frc + alpha * ov_frc


def similarity_force(part, parts, similarity, **options):
    """Compute attractive force on a part from all the other parts connected to it.

    Args:
        part (Part): Part affected by similarity forces with other parts.
        similarity (dict): Similarity score for any pair of parts used as keys.
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        Vector: Force upon given part.
    """

    # Get the single anchor point for similarity forces affecting this part.
    anchor_pt = part.anchor_pins["similarity"][0].place_pt * part.tx

    # Compute the combined force of all the similarity pulling points.
    total_force = Vector(0, 0)
    for pull_pin in part.pull_pins["similarity"]:
        pull_pt = pull_pin.place_pt * pull_pin.part.tx
        # Force from pulling to anchor point is proportional to part similarity and distance.
        total_force += (pull_pt - anchor_pt) * similarity[part][pull_pin.part]

    return total_force


def total_similarity_force(part, parts, similarity, alpha, **options):
    """Compute the total of the attractive similarity and repulsive overlap forces on a part.

    Args:
        part (Part): Part affected by forces from other overlapping parts.
        parts (list): List of parts to check for overlaps.
        similarity (dict): Similarity score for any pair of parts used as keys.
        alpha (float): Proportion of the total that is the overlap force (range [0,1]).
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        Vector: Weighted total of net attractive and overlap repulsion forces.
    """
    if alpha == 0:
        return similarity_force(part, parts, similarity, **options)
    elif alpha == 1:
        return overlap_force(part, parts, **options)
    else:
        sim_frc = similarity_force(part, parts, similarity, **options)
        ov_frc = overlap_force(part, parts, **options)
        return (1 - alpha) * sim_frc + alpha * ov_frc


def compress_parts(parts, nets, force_func, **options):
    """Move parts under influence of attractive nets only.

    Args:
        parts (list): List of Parts.
        nets (list): List of nets that interconnect parts.
        force_func: Function for calculating forces between parts.
        options (dict): Dict of options and values that enable/disable functions.
    """

    if len(parts) <= 1:
        # No need to do placement if there's less than two parts.
        return
    
    # Get PyGame screen, real-to-screen coord Tx matrix, font for debug drawing.
    scr = options.get("draw_scr")
    tx = options.get("draw_tx")
    font = options.get("draw_font")

    # Make list of parts that will be moved, but keep one stationary to act as an anchor.
    mobile_parts = parts[:]
    random.shuffle(mobile_parts)
    mobile_parts[0].force = Vector(0, 0)  # For debug drawing purposes.
    mobile_parts = mobile_parts[1:]

    # Set a threshold for detecting when the parts have stopped moving
    # to be the average movement of individual parts dropping to much less
    # than the length of a grid space.
    # TODO: better convergence threshold.
    all_still = GRID / 100 * len(mobile_parts)

    # Repetitively arrange parts under influence of net attractions only,
    # thus compressing them tightly together. Stop when part mobility
    # drops below a threshold.
    mobility_history = []
    while True:

        random.shuffle(mobile_parts)  # Move parts in random order.

        # Move each part under the influence of the forces of attached nets.
        mobility = 0.0
        for part in mobile_parts:
            force = force_func(part, parts, alpha=0, **options)
            part.force = force  # For debug drawing purposes.
            mv = force
            mobility += mv.magnitude
            mv_tx = Tx(dx=mv.x, dy=mv.y)
            part.tx *= mv_tx  # Move part.

        if scr:
            # Draw current part placement for debugging purposes.
            draw_placement(parts, nets, scr, tx, font)

        mobility_history.append(mobility)

        if mobility < all_still:
            # Parts aren't moving much, so exit while loop.
            # Be sure to anchor one part or else the drift of the entire group will
            # prevent this test from ever converging.
            break

    if options.get("show_mobility"):
        import matplotlib.pyplot as plt

        try:
            mobility_history = [math.log10(m) for m in mobility_history]
            plt.plot(mobility_history)
            plt.show()
        except ValueError:
            pass


def push_and_pull(parts, nets, force_func, speed, **options):
    """Move parts under influence of attractive nets and repulsive part overlaps.

    Args:
        parts (list): List of Parts.
        nets (list): List of nets that interconnect parts.
        force_func: Function for calculating forces between parts.
        speed (float): How fast parts move under the influence of forces.
        options (dict): Dict of options and values that enable/disable functions.
    """

    if len(parts) <= 1:
        # No need to do placement if there's less than two parts.
        return
    
    # Get PyGame screen, real-to-screen coord Tx matrix, font for debug drawing.
    scr = options.get("draw_scr")
    tx = options.get("draw_tx")
    font = options.get("draw_font")

    # Make list of parts that will be moved, but keep one stationary to act as an anchor.
    mobile_parts = parts[:]
    random.shuffle(mobile_parts)
    mobile_parts[0].force = Vector(0, 0)  # For debug drawing purposes.
    mobile_parts = mobile_parts[1:]

    # Set a threshold for detecting when the parts have stopped moving
    # to be the average movement of individual parts dropping to much less
    # than the length of a grid space.
    # TODO: better convergence threshold.
    all_still = GRID / 10 * len(mobile_parts)

    # Setup the schedule for adjusting the alpha coefficient that weights the
    # combination of the attractive net forces and the repulsive part overlap forces.
    # Start at 0 (all attractive) and progress to 1 (all repulsive).
    # alpha_schedule = [0.1, 0.2, 0.5, 0.75, 1.0]
    # alpha_schedule = [0.1, 0.2, 0.3, 0.7, 0.8, 0.9, 1.0]
    # alpha_schedule = [0.1, 0.3, 0.5, 0.7, 1.0]
    alpha_schedule = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    # alpha_schedule = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.2, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    if not options.get("compress_before_place"):
        alpha_schedule.insert(0, 0.0)

    # Arrange parts under influence of net attractions and part overlaps.
    mobility_history = []
    for alpha in alpha_schedule:

        # Repetitively arrange parts under influence of net attractions and
        # part overlap repulsions. Stop when part mobility drops below a threshold.
        while True:

            random.shuffle(mobile_parts)  # Move parts in random order.

            mobility = 0.0
            for part in mobile_parts:
                force = force_func(part, parts, alpha=alpha, **options)
                part.force = force  # For debug drawing purposes.
                mv = force * speed
                mobility += mv.magnitude
                mv_tx = Tx(dx=mv.x, dy=mv.y)
                part.tx *= mv_tx  # Move part.

            mobility_history.append(mobility)

            if scr:
                # Draw current part placement for debugging purposes.
                draw_placement(parts, nets, scr, tx, font)

            if mobility <= all_still:
                # Parts aren't moving much, so exit while loop.
                # Be sure to anchor one part or else the drift of the entire group will
                # prevent this test from ever converging.
                break

        # After the parts have settled down, calculate the attractive forces only on each part
        # and move them if it's above a threshold. This allows parts to "jump" to better
        # positions that they couldn't reach because they were blocked by repulsive forces.
        # TODO: Don't do this until repulsive forces start to predominate.
        if options.get("allow_jumps"):
            for part in mobile_parts:
                # TODO: Decide which of these functions gives the best results.
                # mv = net_force_dist(part, nets, **options)  # Fails when placing part blocks.
                mv = force_func(part, parts, alpha=0, **options)
                if mv.magnitude > GRID * 5:
                    mv_tx = Tx(dx=mv.x, dy=mv.y)
                    part.tx *= mv_tx

    if options.get("allow_jumps"):
        for part in mobile_parts:
            while True:
                mv = force_func(part, parts, alpha=0, **options)
                mv_tx = Tx(dx=mv.x, dy=mv.y)
                part.tx *= mv_tx

                if scr:
                    # Draw current part placement for debugging purposes.
                    draw_placement(parts, nets, scr, tx, font)

                if mv.magnitude < GRID:
                    break

    if options.get("show_mobility"):
        import matplotlib.pyplot as plt

        try:
            mobility_history = [math.log10(m) for m in mobility_history]
            plt.plot(mobility_history)
            plt.show()
        except ValueError:
            pass


def align_parts(parts, **options):
    """Move parts to align their I/O pins with each other and reduce routing jagginess.

    Args:
        parts (list): List of Parts.
        options (dict): Dict of options and values that enable/disable functions.
    """

    try:
        # Align higher pin-count parts first so smaller parts can align to them later without changes messing it up.
        mobile_parts = sorted(parts[:], key=lambda prt: -len(prt.pins))
    except AttributeError:
        # Not a set of Parts. Must be PartBlocks. Skip alignment.
        return

    # Get PyGame screen, real-to-screen coord Tx matrix, font for debug drawing.
    scr = options.get("draw_scr")
    tx = options.get("draw_tx")
    font = options.get("draw_font")

    for part in mobile_parts:

        # Collect moves to align each pin connected to pins on other parts.
        align_moves = []
        for net, anchor_pins in part.anchor_pins.items():
            pull_pins = part.pull_pins[net]
            for pull_pin in pull_pins:
                pull_pt = pull_pin.place_pt * pull_pin.part.tx
                for anchor_pin in anchor_pins:
                    anchor_pt = anchor_pin.place_pt * anchor_pin.part.tx
                    align_moves.append(pull_pt - anchor_pt)

        if not align_moves:
            # The part wasn't connected to any other parts, so skip alignment.
            continue

        # Select the smallest alignment move that occurs most frequently,
        # meaning it will align the most pins with the least movement.
        best_moves = Counter(align_moves).most_common(1)
        best_moves.sort(key=lambda mv: min(abs(mv[0].x), abs(mv[0].y)))
        best_move = best_moves[0][0]

        # Align either in X or Y direction, whichever requires the smallest movement.
        if abs(best_move.x) > abs(best_move.y):
            # Align by moving in Y direction.
            best_move.x = 0
        else:
            # Align by moving in X direction.
            best_move.y = 0

        # Align the part.
        tx = Tx(dx=best_move.x, dy=best_move.y)
        part.tx *= tx

        if scr:
            # Draw current part placement for debugging purposes.
            draw_placement(parts, [], scr, tx, font)


def remove_overlaps(parts, nets, **options):
    """Remove any overlaps using horz/vert grid movements.

    Args:
        parts (list): List of Parts.
        nets (list): List of nets that interconnect parts.
        options (dict): Dict of options and values that enable/disable functions.
    """

    if len(parts) <= 1:
        # No need to do placement if there's less than two parts.
        return

    # Get PyGame screen, real-to-screen coord Tx matrix, font for debug drawing.
    scr = options.get("draw_scr")
    tx = options.get("draw_tx")
    font = options.get("draw_font")

    # Make list of parts that will be moved.
    # mobile_parts = parts[:-1]  # Keep one part stationary as an anchor.
    mobile_parts = parts[:]  # Move all parts.

    overlaps = True
    while overlaps:
        overlaps = False
        random.shuffle(mobile_parts)
        for part in mobile_parts:
            shove_force = overlap_force(part, parts, **options)
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


def slip_and_slide(parts, nets, force_func, **options):
    """Move parts on horz/vert grid looking for improvements without causing overlaps.

    Args:
        parts (list): List of Parts.
        nets (list): List of nets that interconnect parts.
        force_func: Function for calculating forces between parts.
        options (dict): Dict of options and values that enable/disable functions.
    """

    if len(parts) <= 1:
        # No need to do placement if there's less than two parts.
        return

    if not nets:
        # No need to do this if there are no nets attracting parts together.
        return

    # Get PyGame screen, real-to-screen coord Tx matrix, font for debug drawing.
    scr = options.get("draw_scr")
    tx = options.get("draw_tx")
    font = options.get("draw_font")

    # Make list of parts that will be moved.
    # mobile_parts = parts[:-1]  # Keep one part stationary as an anchor.
    mobile_parts = parts[:]  # Move all parts.

    moved = True
    iterations = 20  # TODO: Ad-hoc from observation on test_generate.py.
    while moved and iterations:
        moved = False
        random.shuffle(mobile_parts)
        for part in mobile_parts:
            smallest_force = force_func(part, parts, alpha=0, **options).magnitude
            best_tx = copy(part.tx)
            for dx, dy in ((-GRID, 0), (GRID, GRID), (GRID, -GRID), (-GRID, -GRID)):
                mv_tx = Tx(dx=dx, dy=dy)
                part.tx = part.tx * mv_tx
                force = force_func(part, parts, alpha=0, **options).magnitude
                if force < smallest_force:
                    if overlap_force(part, parts).magnitude == 0:
                        smallest_force = force
                        best_tx = copy(part.tx)
                        moved = True
            part.tx = best_tx
        iterations -= 1
        if scr:
            draw_placement(parts, nets, scr, tx, font)


def evolve_placement(
    parts, nets, force_func, speeds, **options
):
    """Evolve part placement looking for optimum using force function.

    Args:
        parts (list): List of Parts.
        nets (list): List of nets that interconnect parts.
        force_func (function): Computes the force affecting part positions.
        speeds (list): List of floating speeds of part movement per unit of force.
        options (dict): Dict of options and values that enable/disable functions.
    """

    # Force-directed placement.
    for speed in speeds:
        push_and_pull(parts, nets, force_func, speed, **options)

    # Line-up the parts to reduce routing jagginess.
    align_parts(parts, **options)

    # Snap parts to grid.
    for part in parts:
        snap_to_grid(part)

    # Remove part overlaps.
    remove_overlaps(parts, nets, **options)

    # Look for local improvements.
    slip_and_slide(parts, nets, force_func, **options)


@export_to_all
class Placer:
    """Mixin to add place function to Node class."""

    # Speed of part movement during placement.
    speed = 0.25

    def group_parts(node, **options):
        """Group parts in the Node that are connected by internal nets

        Args:
            node (Node): Node with parts.
            options (dict, optional): Dictionary of options and values. Defaults to {}.

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
        if options.get("remove_power"):

            def is_pwr(net):
                return (
                    net.netclass == "Power"
                    or "vcc" in net.name.lower()
                    or "gnd" in net.name.lower()
                )

            internal_nets = [net for net in internal_nets if not is_pwr(net)]

        if options.get("remove_high_fanout"):
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
            set(pin.part for pin in net.pins if pin.part in node.parts)
            for net in internal_nets
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

    def place_connected_parts(node, parts, nets, **options):
        """Place individual parts.

        Args:
            node (Node): Node with parts.
            parts (list): List of Part sets connected by nets.
            nets (list): List of internal Nets connecting the parts.
            options (dict): Dict of options and values that enable/disable functions.
        """

        # Add bboxes with surrounding area so parts are not butted against each other.
        add_placement_bboxes(parts, **options)

        # Set anchor and pull pins that determine attractive forces between parts.
        add_anchor_pull_pins(parts, nets, **options)

        # Randomly place connected parts.
        random_placement(parts)

        if options.get("draw_placement"):
            # Draw the placement for debug purposes.
            bbox = BBox()
            for part in parts:
                tx_bbox = part.place_bbox * part.tx
                bbox.add(tx_bbox)
            draw_scr, draw_tx, draw_font = draw_start(bbox)
            options.update({"draw_scr": draw_scr, "draw_tx": draw_tx, "draw_font": draw_font})

        if options.get("compress_before_place"):
            compress_parts(parts, nets, total_part_force, **options)

        if options.get("rotate_parts"):

            evolve_placement(                parts,                nets,                total_part_force,                speeds=(1.0 * Placer.speed,),                **options            )

            adjust_orientations(                parts,                **options            )

        # Do force-directed placement of the parts in the parts.
        evolve_placement( parts, nets, total_part_force, speeds=(1.0 * Placer.speed,), **options )

        # Placement done so anchor and pull pins for each part are no longer needed.
        rmv_anchor_and_pull_pins(parts)

        # Placement done, so placement bounding boxes for each part are no longer needed.
        rmv_placement_bboxes(parts)

    def place_floating_parts(node, parts, **options):
        """Place individual parts.

        Args:
            node (Node): Node with parts.
            parts (list): List of Parts not connected by explicit nets.
            options (dict): Dict of options and values that enable/disable functions.
        """

        # Add bboxes with surrounding area so parts are not butted against each other.
        add_placement_bboxes(parts)

        # Set anchor and pull pins that determine attractive forces between similar parts.
        add_anchor_pull_pins(parts, [], **options)

        # Randomly place the floating parts.
        random_placement(parts)

        if options.get("draw_placement"):
            # Compute the drawing area for the floating parts
            bbox = BBox()
            for part in parts:
                tx_bbox = part.place_bbox * part.tx
                bbox.add(tx_bbox)
            draw_scr, draw_tx, draw_font = draw_start(bbox)
            options.update({"draw_scr": draw_scr, "draw_tx": draw_tx, "draw_font": draw_font})

        # For non-connected parts, do placement based on their similarity to each other.
        part_similarity = defaultdict(lambda: defaultdict(lambda: 0))
        for part in parts:
            for other_part in parts:

                # Don't compute similarity of a part to itself.
                if other_part is part:
                    continue

                # TODO: Get similarity forces right-sized.
                part_similarity[part][other_part] = part.similarity(other_part) / 100
                # part_similarity[part][other_part] = 0.1

            # Select the top-most pin in each part as the anchor point for force-directed placement.
            # tx = part.tx
            # part.anchor_pin = max(part.anchor_pins, key=lambda pin: (pin.place_pt * tx).y)

        force_func = functools.partial(
            total_similarity_force, similarity=part_similarity
        )

        if options.get("compress_before_place"):
            # Compress all floating parts together under influence of similarity forces only (no replusion).
            compress_parts( parts, [], force_func, **options )

        # Do force-directed placement of the parts in the group.
        evolve_placement( parts, [], force_func, speeds=(Placer.speed,), **options )

        # Placement done so anchor and pull pins for each part are no longer needed.
        rmv_anchor_and_pull_pins(parts)

        # Placement done, so placement bounding boxes for each part are no longer needed.
        rmv_placement_bboxes(parts)

    def place_blocks(node, connected_parts, floating_parts, children, **options):
        """Place blocks of parts and hierarchical sheets.

        Args:
            node (Node): Node with parts.
            connected_parts (list): List of Part sets connected by nets.
            floating_parts (set): Set of Parts not connected by any of the internal nets.
            children (list): Child nodes in the hierarchy.
            non_sheets (list): Hierarchical set of Parts that are visible.
            sheets (list): List of hierarchical blocks.
            options (dict): Dict of options and values that enable/disable functions.
        """

        block_pull_pins = defaultdict(list)

        class PartBlock:
            def __init__(self, src, bbox, anchor_pt, snap_pt, tag):
                self.src = src
                self.place_bbox = bbox  # FIXME: Is this needed if place_bbox includes room for routing?
                self.lbl_bbox = bbox  # Needed for drawing during debug.
                self.force = Vector(0, 0)  # Need for drawing during debug.
                anchor_pin = Pin()
                anchor_pin.part = self
                anchor_pin.place_pt = anchor_pt
                self.anchor_pins = dict()
                self.anchor_pins["similarity"] = [anchor_pin]
                self.pull_pins = block_pull_pins
                block_pull_pins["similarity"].append(anchor_pin)
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
            if child.flattened:
                pad = BLK_INT_PAD + BLK_EXT_PAD
            else:
                pad = BLK_EXT_PAD
            bbox = child.calc_bbox().resize(Vector(pad, pad))
            snap_pt = child.get_snap_pt()
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

        if options.get("draw_placement"):
            # Draw the part block placement for debug purposes.
            bbox = BBox()
            for blk in part_blocks:
                tx_bbox = blk.place_bbox * blk.tx
                bbox.add(tx_bbox)
            draw_scr, draw_tx, draw_font = draw_start(bbox)
            options.update({"draw_scr": draw_scr, "draw_tx": draw_tx, "draw_font": draw_font})

        # Arrange the part blocks with force-directed placement.
        force_func = functools.partial(total_similarity_force, similarity=blk_attr)
        evolve_placement( part_blocks, [], force_func, speeds=(Placer.speed,), **options )

        # Apply the placement moves to the part blocks.
        for blk in part_blocks:
            try:
                blk.src.tx = blk.tx
            except AttributeError:
                for part in blk.src:
                    part.tx = part.tx * blk.tx

    def place(node, tool=None, **options):
        """Place the parts and children in this node.

        Args:
            node (Node): Hierarchical node containing the parts and children to be placed.
            tool (str): Backend tool for schematics.
            options (dict): Dictionary of options and values to control placement.
        """

        # Inject the constants for the backend tool into this module.
        import skidl
        from skidl.tools import tool_modules

        tool = tool or skidl.get_default_tool()
        this_module = sys.modules[__name__]
        this_module.__dict__.update(tool_modules[tool].constants.__dict__)

        random.seed(options.get("seed"))

        # First, recursively place children of this node.
        # TODO: Child nodes are independent, so can they be processed in parallel?
        for child in node.children.values():
            child.place(tool=tool, **options)

        # Group parts into those that are connected by explicit nets and
        # those that float freely connected only by stub nets.
        connected_parts, internal_nets, floating_parts = node.group_parts(**options)

        # Place each group of connected parts.
        for group in connected_parts:
            node.place_connected_parts(list(group), internal_nets, **options)

        if options.get("draw_placement"):
            # Pause to look at placement for debugging purposes.
            draw_pause()

        # Place the floating parts that have no connections to anything else.
        if floating_parts:
            node.place_floating_parts(list(floating_parts), **options)

        if options.get("draw_placement"):
            # Pause to look at placement for debugging purposes.
            draw_pause()

        # Now arrange all the blocks of placed parts and the child nodes within this node.
        node.place_blocks(
            connected_parts, floating_parts, node.children.values(), **options
        )

        if options.get("draw_placement"):
            # Pause to look at placement for debugging purposes.
            draw_pause()

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
