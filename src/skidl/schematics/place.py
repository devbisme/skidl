# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Autoplacer for arranging symbols in a schematic.
"""

import functools
import itertools
import math
import random
import sys
from collections import defaultdict
from copy import copy

from skidl import Pin
from skidl.logger import active_logger
from skidl.utilities import export_to_all, rmv_attr, sgn


def _sch_progress(options, message):
    """schematic_progress=True 时输出布局阶段日志。"""
    if options.get("schematic_progress", False):
        active_logger.info(message)
from .debug_draw import (
    draw_end,
    draw_pause,
    draw_placement,
    draw_redraw,
    draw_start,
    draw_text,
)
from skidl.geometry import BBox, Point, Segment, Tx, Vector
from .topology import apply_topology_or_trunk_layout
from .trunk_layout import build_part_adjacency, expand_main_ic_keepout


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
print("USING MY MODIFIED ROUTER")

class PlacementFailure(Exception):
    """Exception raised when parts or blocks could not be placed."""

    pass


# Small functions for summing Points and Vectors.
pt_sum = lambda pts: sum(pts, Point(0, 0))
force_sum = lambda forces: sum(forces, Vector(0, 0))


def is_net_terminal(part):
    from skidl.schematics.net_terminal import NetTerminal

    return isinstance(part, NetTerminal)


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
    from skidl.schematics.net_terminal import NetTerminal

    for part in parts:
        # Placement bbox starts off with the part bbox (including any net labels).
        part.place_bbox = BBox()
        part.place_bbox.add(part.lbl_bbox)

        # Compute the routing area for each side based on the number of pins on each side.
        padding = {"U": 1, "D": 1, "L": 1, "R": 1}  # Min padding of 1 channel per side.
        for pin in part:
            if pin.stub is False and pin.is_connected():
                padding[pin.orientation] += 1

        # expansion_factor > 1 is used to expand the area for routing around each part,
        # usually in response to a failed routing phase. But don't expand the routing
        # around NetTerminals since those are just used to label wires.
        # spacing 因子叠加到 expansion_factor 上，控制全局留白松紧
        if isinstance(part, NetTerminal):
            expansion_factor = 1
        else:
            spacing = options.get("spacing", 1.0)
            expansion_factor = options.get("expansion_factor", 1.0) * spacing

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


def get_enclosing_bbox(parts):
    """Return bounding box that encloses all the parts."""
    return BBox().add(*(part.place_bbox * part.tx for part in parts))


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

    # Remove any existing anchor and pull pins before making new ones.
    rmv_attr(parts, ("anchor_pins", "pull_pins"))

    # Add dicts for anchor/pull pins and pin centroids to each movable part.
    for part in parts:
        part.anchor_pins = defaultdict(list)
        part.pull_pins = defaultdict(list)
        part.pin_ctrs = dict()

    if nets:
        # If nets exist, then these parts are interconnected so
        # assign pins on each net to part anchor and pull pin lists.
        for net in nets:
            # Get net pins that are on movable parts.
            pins = {pin for pin in net.pins if pin.part in parts}

            # Get the set of parts with pins on the net.
            net.parts = {pin.part for pin in pins}

            # Add each pin as an anchor on the part that contains it and
            # as a pull pin on all the other parts that will be pulled by this part.
            for pin in pins:
                pin.part.anchor_pins[net].append(pin)
                add_place_pt(pin.part, pin)
                for part in net.parts - {pin.part}:
                    # NetTerminals are pulled towards connected parts, but
                    # those parts are not attracted towards NetTerminals.
                    if not is_net_terminal(pin.part):
                        part.pull_pins[net].append(pin)

        # For each net, assign the centroid of the part's anchor pins for that net.
        for net in nets:
            for part in net.parts:
                if part.anchor_pins[net]:
                    part.pin_ctrs[net] = pt_sum(
                        pin.place_pt for pin in part.anchor_pins[net]
                    ) / len(part.anchor_pins[net])

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


def save_anchor_pull_pins(parts):
    """Save anchor/pull pins for each part before they are changed."""
    for part in parts:
        part.saved_anchor_pins = copy(part.anchor_pins)
        part.saved_pull_pins = copy(part.pull_pins)


def restore_anchor_pull_pins(parts):
    """Restore the original anchor/pull pin lists for each Part."""

    for part in parts:
        if hasattr(part, "saved_anchor_pins"):
            # Saved pin lists exist, so restore them to the original anchor/pull pin lists.
            part.anchor_pins = part.saved_anchor_pins
            part.pull_pins = part.saved_pull_pins

    # Remove the attributes where the original lists were saved.
    rmv_attr(parts, ("saved_anchor_pins", "saved_pull_pins"))


def adjust_orientations(parts, **options):
    """Adjust orientation of parts.

    Args:
        parts (list): List of Parts to adjust.
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        bool: True if one or more part orientations were changed. Otherwise, False.
    """

    def find_best_orientation(part):
        """Each part has 8 possible orientations. Find the best of the 7 alternatives from the starting one."""

        # Store starting orientation.
        part.prev_tx = copy(part.tx)

        # Get centerpoint of part for use when doing rotations/flips.
        part_ctr = (part.place_bbox * part.tx).ctr

        # Now find the orientation that has the largest decrease (or smallest increase) in cost.
        # Go through four rotations, then flip the part and go through the rotations again.
        best_delta_cost = float("inf")
        calc_starting_cost = True
        for i in range(2):
            for j in range(4):

                if calc_starting_cost:
                    # Calculate the cost of the starting orientation before any changes in orientation.
                    starting_cost = net_tension(part, **options)
                    # Skip the starting orientation but set flag to process the others.
                    calc_starting_cost = False
                else:
                    # Calculate the cost of the current orientation.
                    delta_cost = net_tension(part, **options) - starting_cost
                    if delta_cost < best_delta_cost:
                        # Save the largest decrease in cost and the associated orientation.
                        best_delta_cost = delta_cost
                        best_tx = copy(part.tx)

                # Proceed to the next rotation.
                part.tx = part.tx.move(-part_ctr).rot_90cw().move(part_ctr)

            # Flip the part and go through the rotations again.
            part.tx = part.tx.move(-part_ctr).flip_x().move(part_ctr)

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

    # Kernighan-Lin algorithm for finding near-optimal part orientations.
    # Because of the way the tension for part alignment is computed based on
    # the nearest part, it is possible for an infinite loop to occur.
    # Hence the ad-hoc loop limit.
    for iter_cnt in range(10):
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
        # delta_cost at location i is the change in cost *before* part i is moved.
        # Start with cost change of zero before any parts are moved.
        delta_costs = [0,]
        delta_costs.extend((part.delta_cost for part in moved_parts))
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
        for part in moved_parts[min_index:]:
            part.tx = part.prev_tx

        # Terminate the search if no part orientations were changed.
        if min_index == 0:
            break

    rmv_attr(parts, ("prev_tx", "delta_cost", "delta_cost_tx"))

    # Return True if one or more iterations were done, indicating part orientations were changed.
    return iter_cnt > 0


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


def net_torque_dist(part, **options):
    """Calculate the torque of the nets trying to rotate/flip the part.

    Args:
        part (Part): Part affected by forces from other connected parts.
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        float: Total torque on the part.
    """

    # Part centroid for computing torque.
    ctr = part.place_bbox.ctr * part.tx

    # Get the force multiplier applied to point-to-point nets.
    pt_to_pt_mult = options.get("pt_to_pt_mult", 1)

    # Compute the torque for each net attached to the part.
    torque = 0.0
    for net, anchor_pins in part.anchor_pins.items():
        pull_pins = part.pull_pins[net]

        if not anchor_pins or not pull_pins:
            # Skip nets without pulling or anchor points.
            continue

        pull_pin_pts = [pin.place_pt * pin.part.tx for pin in pull_pins]

        # Multiply the force exerted by point-to-point nets.
        force_mult = pt_to_pt_mult if len(pull_pin_pts) <= 1 else 1

        # Compute the net torque acting on each anchor point on the part.
        for anchor_pin in anchor_pins:
            # Compute the anchor point's (x,y).
            anchor_pt = anchor_pin.place_pt * part.tx

            # Compute torque around part center from force between anchor & pull pins.
            normalize = len(pull_pin_pts)
            lever_norm = (anchor_pt - ctr).norm
            for pull_pt in pull_pin_pts:
                frc_norm = (pull_pt - anchor_pt).norm
                torque += lever_norm.xprod(frc_norm) * force_mult / normalize

    return abs(torque)


# Select the net tension method used for the adjusting the orientation of parts.
net_tension = net_tension_dist
# net_tension = net_torque_dist


@export_to_all
def net_force_dist(part, **options):
    """Compute attractive force on a part from all the other parts connected to it.

    Args:
        part (Part): Part affected by forces from other connected parts.
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        Vector: Force upon given part.
    """

    # Get the anchor and pull pins for each net connected to this part.
    anchor_pins = part.anchor_pins
    pull_pins = part.pull_pins

    # Get the force multiplier applied to point-to-point nets.
    pt_to_pt_mult = options.get("pt_to_pt_mult", 1)

    # Compute the total force on the part from all the anchor/pulling points on each net.
    total_force = Vector(0, 0)

    # Parts with a lot of pins can accumulate large net forces that move them very quickly.
    # Accumulate the number of individual net forces and use that to attenuate
    # the total force, effectively normalizing the forces between large & small parts.
    net_normalizer = 0

    # Compute the force for each net attached to the part.
    for net in anchor_pins.keys():
        if not anchor_pins[net] or not pull_pins[net]:
            # Skip nets without pulling or anchor points.
            continue

        # Multiply the force exerted by point-to-point nets.
        force_mult = pt_to_pt_mult if len(pull_pins[net]) <= 1 else 1

        # Initialize net force.
        net_force = Vector(0, 0)

        pin_normalizer = 0

        # Compute the anchor and pulling point (x,y)s for the net.
        anchor_pts = [pin.place_pt * pin.part.tx for pin in anchor_pins[net]]
        pull_pts = [pin.place_pt * pin.part.tx for pin in pull_pins[net]]

        # Compute the net force acting on each anchor point on the part.
        for anchor_pt in anchor_pts:
            # Sum the forces from each pulling point on the anchor point.
            for pull_pt in pull_pts:
                # Get the distance from the pull pt to the anchor point.
                dist_vec = pull_pt - anchor_pt

                # Add the force on the anchor pin from the pulling pin.
                net_force += dist_vec

                # Increment the normalizer for every pull force added to the net force.
                pin_normalizer += 1

        if options.get("pin_normalize"):
            # Normalize the net force across all the anchor & pull pins.
            pin_normalizer = pin_normalizer or 1  # Prevent div-by-zero.
            net_force /= pin_normalizer

        # Accumulate force from this net into the total force on the part.
        # Multiply force if the net meets stated criteria.
        total_force += net_force * force_mult

        # Increment the normalizer for every net force added to the total force.
        net_normalizer += 1

    if options.get("net_normalize"):
        # Normalize the total force across all the nets.
        net_normalizer = net_normalizer or 1  # Prevent div-by-zero.
        total_force /= net_normalizer

    return total_force


# Select the net force method used for the attraction of parts during placement.
attractive_force = net_force_dist


@export_to_all
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
            # Compute the movement needed to separate the bboxes in left/right/up/down directions.
            # Add some small random offset to break symmetry when parts exactly overlay each other.
            # Move right edge of part to the left of other part's left edge, etc...
            moves = []
            rnd = Vector(random.random()-0.5, random.random()-0.5)
            for edges, dir in ((("ll", "lr"), Vector(1,0)), (("ul", "ll"), Vector(0,1))):
                move = (getattr(other_part_bbox, edges[0]) - getattr(part_bbox, edges[1]) - rnd) * dir
                moves.append([move.magnitude, move])
                # Flip edges...
                move = (getattr(other_part_bbox, edges[1]) - getattr(part_bbox, edges[0]) - rnd) * dir
                moves.append([move.magnitude, move])

            # Select the smallest move that separates the parts.
            move = min(moves, key=lambda m: m[0])

            # Add the move to the total force on the part.
            total_force += move[1]
                
    return total_force


@export_to_all
def overlap_force_rand(part, parts, **options):
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
            # Add some small random offset to break symmetry when parts exactly overlay each other.
            # Move right edge of part to the left of other part's left edge.
            moves = []
            rnd = Vector(random.random()-0.5, random.random()-0.5)
            for edges, dir in ((("ll", "lr"), Vector(1,0)), (("lr", "ll"), Vector(1,0)),
                          (("ul", "ll"), Vector(0,1)), (("ll", "ul"), Vector(0,1))):
                move = (getattr(other_part_bbox, edges[0]) - getattr(part_bbox, edges[1]) - rnd) * dir
                moves.append([move.magnitude, move])
            accum = 0
            for move in moves:
                accum += move[0]
            for move in moves:
                move[0] = accum - move[0]
            new_accum = 0
            for move in moves:
                move[0] += new_accum
                new_accum = move[0]
            select = new_accum * random.random()
            for move in moves:
                if move[0] >= select:
                    total_force += move[1]
                    break
                
    return total_force


# Select the overlap force method used for the repulsion of parts during placement.
repulsive_force = overlap_force
# repulsive_force = overlap_force_rand


def scale_attractive_repulsive_forces(parts, force_func, **options):
    """Set scaling between attractive net forces and repulsive part overlap forces."""

    # Store original part placement.
    for part in parts:
        part.original_tx = copy(part.tx)

    # Find attractive forces when they are maximized by random part placement.
    random_placement(parts, **options)
    attractive_forces_sum = sum(
        force_func(p, parts, alpha=0, scale=1, **options).magnitude for p in parts
    )

    # Find repulsive forces when they are maximized by compacted part placement.
    central_placement(parts, **options)
    repulsive_forces_sum = sum(
        force_func(p, parts, alpha=1, scale=1, **options).magnitude for p in parts
    )

    # Restore original part placement.
    for part in parts:
        part.tx = part.original_tx
    rmv_attr(parts, ["original_tx"])

    # Return scaling factor that makes attractive forces about the same as repulsive forces.
    try:
        return repulsive_forces_sum / attractive_forces_sum
    except ZeroDivisionError:
        # No attractive forces, so who cares about scaling? Set it to 1.
        return 1


def total_part_force(part, parts, scale, alpha, **options):
    """Compute the total of the attractive net and repulsive overlap forces on a part.

    Args:
        part (Part): Part affected by forces from other overlapping parts.
        parts (list): List of parts to check for overlaps.
        scale (float): Scaling factor for net forces to make them equivalent to overlap forces.
        alpha (float): Fraction of the total that is the overlap force (range [0,1]).
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        Vector: Weighted total of net attractive and overlap repulsion forces.
    """
    force = scale * (1 - alpha) * attractive_force(
        part, **options
    ) + alpha * repulsive_force(part, parts, **options)
    part.force = force  # For debug drawing.
    return force


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


def total_similarity_force(part, parts, similarity, scale, alpha, **options):
    """Compute the total of the attractive similarity and repulsive overlap forces on a part.

    Args:
        part (Part): Part affected by forces from other overlapping parts.
        parts (list): List of parts to check for overlaps.
        similarity (dict): Similarity score for any pair of parts used as keys.
        scale (float): Scaling factor for similarity forces to make them equivalent to overlap forces.
        alpha (float): Proportion of the total that is the overlap force (range [0,1]).
        options (dict): Dict of options and values that enable/disable functions.

    Returns:
        Vector: Weighted total of net attractive and overlap repulsion forces.
    """
    force = scale * (1 - alpha) * similarity_force(
        part, parts, similarity, **options
    ) + alpha * repulsive_force(part, parts, **options)
    part.force = force  # For debug drawing.
    return force


def define_placement_bbox(parts, **options):
    """Return a bounding box big enough to hold the parts being placed."""

    # Compute appropriate size to hold the parts based on their areas.
    area = 0
    for part in parts:
        area += part.place_bbox.area
    side = 3 * math.sqrt(area)  # HACK: Multiplier is ad-hoc.
    return BBox(Point(0, 0), Point(side, side))


def central_placement(parts, **options):
    """Cluster all part centroids onto a common point.

    Args:
        parts (list): List of Parts.
        options (dict): Dict of options and values that enable/disable functions.
    """

    if len(parts) <= 1:
        # No need to do placement if there's less than two parts.
        return

    # Find the centroid of all the parts.
    ctr = get_enclosing_bbox(parts).ctr

    # Collapse all the parts to the centroid.
    for part in parts:
        mv = ctr - part.place_bbox.ctr * part.tx
        part.tx *= Tx(dx=mv.x, dy=mv.y)


def random_placement(parts, **options):
    """Randomly place parts within an appropriately-sized area.

    Args:
        parts (list): List of Parts to place.
    """

    # Compute appropriate size to hold the parts based on their areas.
    bbox = define_placement_bbox(parts, **options)

    # Place parts randomly within area.
    for part in parts:
        pt = Point(random.random() * bbox.w, random.random() * bbox.h)
        part.tx = part.tx.move(pt)


def push_and_pull(anchored_parts, mobile_parts, nets, force_func, **options):
    """Move parts under influence of attractive nets and repulsive part overlaps.

    Args:
        anchored_parts (list): Set of immobile Parts whose position affects placement.
        mobile_parts (list): Set of Parts that can be moved.
        nets (list): List of nets that interconnect parts.
        force_func: Function for calculating forces between parts.
        options (dict): Dict of options and values that enable/disable functions.
    """

    if not options.get("use_push_pull"):
        # Abort if push & pull of parts is disabled.
        return

    if not mobile_parts:
        # No need to do placement if there's nothing to move.
        return

    def cost(parts, alpha):
        """Cost function for use in debugging. Should decrease as parts move."""
        for part in parts:
            part.force = force_func(part, parts, scale=scale, alpha=alpha, **options)
        return sum((part.force.magnitude for part in parts))

    # Get PyGame screen, real-to-screen coord Tx matrix, font for debug drawing.
    scr = options.get("draw_scr")
    tx = options.get("draw_tx")
    font = options.get("draw_font")
    txt_org = Point(10, 10)

    # Create the total set of parts exerting forces on each other.
    parts = anchored_parts + mobile_parts

    # If there are no anchored parts, then compute the overall drift force
    # across all the parts. This will be subtracted so the
    # entire group of parts doesn't just continually drift off in one direction.
    # This only needs to be done if ALL parts are mobile (i.e., no anchored parts).
    rmv_drift = not anchored_parts

    # Set scale factor between attractive net forces and repulsive part overlap forces.
    scale = scale_attractive_repulsive_forces(parts, force_func, **options)

    # Setup the schedule for adjusting the alpha coefficient that weights the
    # combination of the attractive net forces and the repulsive part overlap forces.
    # Start at 0 (all attractive) and gradually progress to 1 (all repulsive).
    # Also, set parameters for determining when parts are stable and for restricting
    # movements in the X & Y directions when parts are being aligned.
    force_schedule = [
        (0.50, 0.0, 0.1, False, (1, 1)),  # Attractive forces only.
        (0.25, 0.0, 0.01, False, (1, 1)),  # Attractive forces only.
        # (0.25, 0.2, 0.01, False, (1,1)), # Some repulsive forces.
        (0.25, 0.4, 0.1, False, (1, 1)),  # More repulsive forces.
        # (0.25, 0.6, 0.01, False, (1,1)), # More repulsive forces.
        (0.25, 0.8, 0.1, False, (1, 1)),  # More repulsive forces.
        # (0.25, 0.7, 0.01, True, (1,0)), # Align parts horiz.
        # (0.25, 0.7, 0.01, True, (0,1)), # Align parts vert.
        # (0.25, 0.7, 0.01, True, (1,0)), # Align parts horiz.
        # (0.25, 0.7, 0.01, True, (0,1)), # Align parts vert.
        (0.25, 1.0, 0.01, False, (1, 1)),  # Remove any part overlaps.
    ]
    # N = 7
    # force_schedule = [(0.50, i/N, 0.01, False, (1,1)) for i in range(N+1)]

    # Step through the alpha sequence going from all-attractive to all-repulsive forces.
    for speed, alpha, stability_coef, align_parts, force_mask in force_schedule:
        if align_parts:
            # Align parts by only using forces between the closest anchor/pull pins.
            retain_closest_anchor_pull_pins(mobile_parts)
        else:
            # For general placement, use forces between all anchor/pull pins.
            restore_anchor_pull_pins(mobile_parts)

        # This stores the threshold below which all the parts are assumed to be stabilized.
        # Since it can never be negative, set it to -1 to indicate it's uninitialized.
        stable_threshold = -1

        # Move parts for this alpha until they all settle into fixed positions.
        # Place an iteration limit to prevent an infinite loop.
        for _ in range(1000):  # HACK: Ad-hoc iteration limit.
            # Compute forces exerted on the parts by each other.
            sum_of_forces = 0
            for part in mobile_parts:
                part.force = force_func(
                    part, parts, scale=scale, alpha=alpha, **options
                )
                # Mask X or Y component of force during part alignment.
                part.force = part.force.mask(force_mask)
                sum_of_forces += part.force.magnitude

            if rmv_drift:
                # Calculate the drift force across all parts and subtract it from each part
                # to prevent them from continually drifting in one direction.
                drift_force = force_sum([part.force for part in mobile_parts]) / len(
                    mobile_parts
                )
                for part in mobile_parts:
                    part.force -= drift_force

            # Apply movements to part positions.
            for part in mobile_parts:
                part.mv = part.force * speed
                part.tx *= Tx(dx=part.mv.x, dy=part.mv.y)

            # Keep iterating until all the parts are still.
            if stable_threshold < 0:
                # Set the threshold after the first iteration.
                initial_sum_of_forces = sum_of_forces
                stable_threshold = sum_of_forces * stability_coef
            elif sum_of_forces <= stable_threshold:
                # Part positions have stabilized if forces have dropped below threshold.
                break
            elif sum_of_forces > 10 * initial_sum_of_forces:
                # If the forces are getting higher, then that usually means the parts are
                # spreading out. This can happen if speed is too large, so reduce it so
                # the forces may start to decrease.
                speed *= 0.50

        if scr:
            # Draw current part placement for debugging purposes.
            draw_placement(parts, nets, scr, tx, font)
            draw_text(
                f"alpha:{alpha:3.2f} iter:{_} force:{sum_of_forces:.1f} stable:{stable_threshold}",
                txt_org,
                scr,
                tx,
                font,
                color=(0, 0, 0),
                real=False,
            )
            draw_redraw()


def evolve_placement(anchored_parts, mobile_parts, nets, force_func, **options):
    """Evolve part placement looking for optimum using force function.

    Args:
        anchored_parts (list): Set of immobile Parts whose position affects placement.
        mobile_parts (list): Set of Parts that can be moved.
        nets (list): List of nets that interconnect parts.
        force_func (function): Computes the force affecting part positions.
        options (dict): Dict of options and values that enable/disable functions.
    """

    parts = anchored_parts + mobile_parts

    # Force-directed placement.
    push_and_pull(anchored_parts, mobile_parts, nets, force_func, **options)

    # Snap parts to grid.
    for part in parts:
        snap_to_grid(part)


def place_net_terminals(net_terminals, placed_parts, nets, force_func, **options):
    """Place net terminals around already-placed parts.

    Args:
        net_terminals (list): List of NetTerminals
        placed_parts (list): List of placed Parts.
        nets (list): List of nets that interconnect parts.
        force_func (function): Computes the force affecting part positions.
        options (dict): Dict of options and values that enable/disable functions.
    """

    def trim_pull_pins(terminals, bbox):
        """Trim pullpins of NetTerminals to the part pins closest to an edge of the bounding box of placed parts.

        Args:
            terminals (list): List of NetTerminals.
            bbox (BBox): Bounding box of already-placed parts.

        Note:
            The rationale for this is that pin closest to an edge of the bounding box will be easier to access.
        """

        for terminal in terminals:
            for net, pull_pins in terminal.pull_pins.items():
                insets = []
                for pull_pin in pull_pins:
                    pull_pt = pull_pin.place_pt * pull_pin.part.tx

                    # Get the inset of the terminal pulling pin from each side of the placement area.
                    # Left side.
                    insets.append((abs(pull_pt.x - bbox.ll.x), pull_pin))
                    # Right side.
                    insets.append((abs(pull_pt.x - bbox.lr.x), pull_pin))
                    # Top side.
                    insets.append((abs(pull_pt.y - bbox.ul.y), pull_pin))
                    # Bottom side.
                    insets.append((abs(pull_pt.y - bbox.ll.y), pull_pin))

                # Retain only the pulling pin closest to an edge of the bounding box (i.e., minimum inset).
                terminal.pull_pins[net] = [min(insets, key=lambda off: off[0])[1]]

    def orient(terminals, bbox):
        """Set orientation of NetTerminals to point away from closest bounding box edge.

        Args:
            terminals (list): List of NetTerminals.
            bbox (BBox): Bounding box of already-placed parts.
        """

        for terminal in terminals:
            # A NetTerminal should already be trimmed so it is attached to a single pin of a part on a single net.
            pull_pin = list(terminal.pull_pins.values())[0][0]
            pull_pt = pull_pin.place_pt * pull_pin.part.tx

            # Get the inset of the terminal pulling pin from each side of the placement area
            # and the Tx() that should be applied if the terminal is placed on that side.
            insets = []
            # Left side, so terminal label juts out to the left.
            insets.append((abs(pull_pt.x - bbox.ll.x), Tx()))
            # Right side, so terminal label flipped to jut out to the right.
            insets.append((abs(pull_pt.x - bbox.lr.x), Tx().flip_x()))
            # Top side, so terminal label rotated by 270 to jut out to the top.
            insets.append((abs(pull_pt.y - bbox.ul.y), Tx().rot_90cw().rot_90cw().rot_90cw()))
            # Bottom side. so terminal label rotated 90 to jut out to the bottom.
            insets.append((abs(pull_pt.y - bbox.ll.y), Tx().rot_90cw()))

            # Apply the Tx() for the side the terminal is closest to.
            terminal.tx = min(insets, key=lambda inset: inset[0])[1]

    def move_to_pull_pin(terminals):
        """Move NetTerminals immediately to their pulling pins."""
        for terminal in terminals:
            anchor_pin = list(terminal.anchor_pins.values())[0][0]
            anchor_pt = anchor_pin.place_pt * anchor_pin.part.tx
            pull_pin = list(terminal.pull_pins.values())[0][0]
            pull_pt = pull_pin.place_pt * pull_pin.part.tx
            terminal.tx = terminal.tx.move(pull_pt - anchor_pt)

    def evolution(net_terminals, placed_parts, bbox):
        """Evolve placement of NetTerminals starting from outermost from center to innermost."""

        evolution_type = options.get("terminal_evolution", "all_at_once")

        if evolution_type == "all_at_once":
            evolve_placement(
                placed_parts, net_terminals, nets, total_part_force, **options
            )

        elif evolution_type == "outer_to_inner":
            # Start off with the previously-placed parts as anchored parts. NetTerminals will be added to this as they are placed.
            anchored_parts = copy(placed_parts)

            # Sort terminals from outermost to innermost w.r.t. the center.
            def dist_to_bbox_edge(term):
                pt = term.pins[0].place_pt * term.tx
                return min((
                    abs(pt.x - bbox.ll.x),
                    abs(pt.x - bbox.lr.x),
                    abs(pt.y - bbox.ll.y),
                    abs(pt.y - bbox.ul.y))
                )

            terminals = sorted(
                net_terminals,
                key=lambda term: dist_to_bbox_edge(term),
                reverse=True,
            )

            # Grab terminals starting from the outside and work towards the inside until a terminal intersects a previous one.
            mobile_terminals = []
            mobile_bboxes = []
            for terminal in terminals:
                terminal_bbox = terminal.place_bbox * terminal.tx
                mobile_terminals.append(terminal)
                mobile_bboxes.append(terminal_bbox)
                for bbox in mobile_bboxes[:-1]:
                    if terminal_bbox.intersects(bbox):
                        # The current NetTerminal intersects one of the previously-selected mobile terminals, so evolve the
                        # placement of all the mobile terminals except the current one.
                        evolve_placement(
                            anchored_parts,
                            mobile_terminals[:-1],
                            nets,
                            force_func,
                            **options
                        )
                        # Anchor the mobile terminals after their placement is done.
                        anchored_parts.extend(mobile_terminals[:-1])
                        # Remove the placed terminals, leaving only the current terminal.
                        mobile_terminals = mobile_terminals[-1:]
                        mobile_bboxes = mobile_bboxes[-1:]

            if mobile_terminals:
                # Evolve placement of any remaining terminals.
                evolve_placement(
                    anchored_parts, mobile_terminals, nets, total_part_force, **options
                )

    bbox = get_enclosing_bbox(placed_parts)
    save_anchor_pull_pins(net_terminals)
    trim_pull_pins(net_terminals, bbox)
    orient(net_terminals, bbox)
    move_to_pull_pin(net_terminals)
    evolution(net_terminals, placed_parts, bbox)
    restore_anchor_pull_pins(net_terminals)


@export_to_all
class Placer:
    """Mixin to add place function to Node class."""

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

    # 超过此数量的连通组走 rowbased+结构化 human_readable；TG032 等 ~10 件小板也需分区摆放。
    _ROW_PLACE_THRESHOLD = 8

    def _part_ref_key(node, part):
        """Return a stable sort key for parts."""
        ref = str(getattr(part, "ref", "") or "")
        name = str(getattr(part, "name", "") or "")
        value = str(getattr(part, "value", "") or "")
        return (ref.lower(), name.lower(), value.lower(), id(part))

    def _net_names_of(node, part):
        """Safely return set of connected net names for a part."""
        names = set()
        for pin in getattr(part, "pins", []):
            if not getattr(pin, "is_connected", lambda: False)():
                continue
            net = getattr(pin, "net", None)
            if net is None:
                continue
            name = getattr(net, "name", None)
            if name:
                names.add(str(name))
        return names

    def _is_power_net_name(node, name):
        """Heuristic detection of power/ground net names."""
        if not name:
            return False
        text = str(name).upper()
        power_tokens = (
            "VCC",
            "VDD",
            "VSS",
            "GND",
            "AGND",
            "DGND",
            "PGND",
            "VBUS",
            "VIN",
            "VOUT",
            "3V3",
            "5V",
            "12V",
            "1V8",
            "2V5",
            "PWR",
        )
        return any(token in text for token in power_tokens)

    def _is_bus_net_name(node, name):
        """Heuristic detection of bus-like or globally-named nets."""
        if not name:
            return False
        text = str(name).upper()
        bus_tokens = (
            "BUS",
            "ADDR",
            "ADDRESS",
            "DATA",
            "GPIO",
            "USB",
            "PCIE",
            "ETH",
            "MDIO",
            "RGMII",
        )
        return (
            "[" in text
            or "]" in text
            or any(token in text for token in bus_tokens)
        )

    def _part_ref_prefix(node, part):
        """Return the alphabetic prefix of a part reference."""
        ref = str(getattr(part, "ref", "") or "").upper()
        prefix = []
        for ch in ref:
            if ch.isalpha():
                prefix.append(ch)
            elif prefix:
                break
        return "".join(prefix)

    def _net_connected_parts(node, net, allowed_parts=None):
        """Return unique non-terminal parts connected to a net."""
        parts = []
        seen = set()
        allowed_ids = None if allowed_parts is None else {id(part) for part in allowed_parts}
        for pin in getattr(net, "pins", []):
            part = getattr(pin, "part", None)
            if part is None or is_net_terminal(part):
                continue
            if allowed_ids is not None and id(part) not in allowed_ids:
                continue
            if id(part) in seen:
                continue
            seen.add(id(part))
            parts.append(part)
        return parts

    def _part_effective_bbox(node, part):
        """Return the current placement bbox for a part."""
        bbox = getattr(part, "place_bbox", None) or getattr(part, "lbl_bbox", None)
        if bbox is None:
            bbox = getattr(part, "bbox", BBox(Point(0, 0), Point(0, 0)))
        return bbox * getattr(part, "tx", Tx())

    def _bbox_manhattan_gap(node, bbox_a, bbox_b):
        """Return the manhattan gap between two bboxes (0 if they overlap/touch)."""
        dx = max(0, bbox_a.min.x - bbox_b.max.x, bbox_b.min.x - bbox_a.max.x)
        dy = max(0, bbox_a.min.y - bbox_b.max.y, bbox_b.min.y - bbox_a.max.y)
        return dx + dy

    def _pin_abs_pt(node, pin):
        """Return the absolute placed point for a pin."""
        pin_pt = getattr(pin, "place_pt", getattr(pin, "pt", Point(pin.x, pin.y)))
        return pin_pt * getattr(pin.part, "tx", Tx())

    def _net_geometry_stats(node, pins):
        """Return max pin distance, min pin distance, and bbox span for a net."""
        if len(pins) < 2:
            return 0, 0, 0

        pts = [node._pin_abs_pt(pin) for pin in pins]
        bbox = BBox()
        for pt in pts:
            bbox.add(pt)

        max_dist = 0
        min_dist = float("inf")
        for i, pt_a in enumerate(pts):
            for pt_b in pts[i + 1:]:
                dist = abs(pt_a.x - pt_b.x) + abs(pt_a.y - pt_b.y)
                max_dist = max(max_dist, dist)
                min_dist = min(min_dist, dist)

        if min_dist == float("inf"):
            min_dist = 0

        return max_dist, min_dist, bbox.w + bbox.h

    def _same_functional_block(node, net, part_a, part_b):
        """Heuristically detect parts that should stay visually wired together."""
        if part_a is part_b:
            return True

        role_a = node._classify_part_role(part_a)
        role_b = node._classify_part_role(part_b)
        roles = {role_a, role_b}
        prefixes = {
            node._part_ref_prefix(part_a),
            node._part_ref_prefix(part_b),
        }

        if "decoupling" in roles and roles.intersection({"ic", "passive", "power"}):
            return True
        if "ic" in roles and roles.intersection({"passive", "power"}):
            return True
        if prefixes.intersection({"Q", "U"}) and prefixes.intersection({"R", "C", "D", "L"}):
            return True
        if prefixes.intersection({"D", "LED"}) and prefixes.intersection({"R", "C"}):
            return True

        net_name = str(getattr(net, "name", "") or "")
        if node._is_power_net_name(net_name):
            local_roles = {"ic", "passive", "decoupling", "power", "other"}
            if roles <= local_roles and not roles.intersection({"connector"}):
                return True

        return False

    def _cluster_pins_by_distance(node, net, pins, **options):
        """Cluster net pins that are close enough to stay visibly wired."""
        if len(pins) < 2:
            return [list(pins)]

        grid = globals().get("GRID", 100)
        local_wire_threshold = options.get(
            "auto_stub_local_wire_threshold", grid * 12
        )

        parents = {id(pin): id(pin) for pin in pins}
        def find(pin_id):
            while parents[pin_id] != pin_id:
                parents[pin_id] = parents[parents[pin_id]]
                pin_id = parents[pin_id]
            return pin_id

        def union(pin_a, pin_b):
            root_a = find(id(pin_a))
            root_b = find(id(pin_b))
            if root_a != root_b:
                parents[root_b] = root_a

        for i, pin_a in enumerate(pins):
            pt_a = node._pin_abs_pt(pin_a)
            for pin_b in pins[i + 1:]:
                pt_b = node._pin_abs_pt(pin_b)
                dist = abs(pt_a.x - pt_b.x) + abs(pt_a.y - pt_b.y)
                if dist <= local_wire_threshold or node._same_functional_block(
                    net, pin_a.part, pin_b.part
                ):
                    union(pin_a, pin_b)

        clusters = defaultdict(list)
        for pin in pins:
            clusters[find(id(pin))].append(pin)

        def cluster_key(cluster):
            max_dist, min_dist, bbox_span = node._net_geometry_stats(cluster)
            return (len(cluster), -bbox_span, -max_dist, -min_dist)

        return sorted(clusters.values(), key=cluster_key, reverse=True)

    def _is_local_functional_cluster(node, net, parts):
        """Detect small motifs that read better with visible local wiring."""
        if len(parts) < 2 or len(parts) > 4:
            return False

        prefixes = {node._part_ref_prefix(part) for part in parts}
        roles = {part: node._classify_part_role(part) for part in parts}

        if any(role == "decoupling" for role in roles.values()):
            return True
        if "R" in prefixes and "D" in prefixes:
            return True
        if "R" in prefixes and "C" in prefixes:
            return True
        if "Q" in prefixes and prefixes.intersection({"R", "C", "D"}):
            return True
        if any(role == "ic" for role in roles.values()) and any(
            role in ("passive", "decoupling") for role in roles.values()
        ):
            return True

        name = str(getattr(net, "name", "") or "")
        if len(parts) == 2 and not (
            node._is_power_net_name(name) or node._is_bus_net_name(name)
        ):
            return True

        return False

    def _prefer_visible_wire_preplacement(node, net, part_to_group, **options):
        """Decide if a net should stay explicit before detailed geometry exists."""
        parts = node._net_connected_parts(net)
        if len(parts) < 2:
            return True

        name = str(getattr(net, "name", "") or "")
        if node._is_bus_net_name(name):
            return False

        max_groups = options.get("auto_stub_visible_group_span", 2)
        pin_groups = {
            part_to_group[id(part)]
            for part in parts
            if id(part) in part_to_group
        }
        if len(pin_groups) > max_groups:
            return False

        max_pins = options.get("auto_stub_visible_pins", 4)
        if len(parts) > max_pins:
            return False

        if node._is_power_net_name(name):
            return node._is_local_functional_cluster(net, parts)

        return node._is_local_functional_cluster(net, parts)

    def _prefer_visible_wire_postplacement(node, net, pins, **options):
        """Decide if a placed net should remain visible for local readability."""
        parts = node._net_connected_parts(net, allowed_parts={pin.part for pin in pins})
        if len(parts) < 2:
            return True

        name = str(getattr(net, "name", "") or "")
        if node._is_bus_net_name(name):
            return False

        grid = globals().get("GRID", 100)
        local_wire_threshold = options.get(
            "auto_stub_local_wire_threshold", grid * 12
        )
        local_cluster_threshold = options.get(
            "auto_stub_local_cluster_threshold", grid * 18
        )
        max_wire_pins = options.get("auto_stub_max_wire_pins", 3)
        max_wire_dist = options.get("auto_stub_max_wire_dist", 2000)

        max_dist, min_dist, bbox_span = node._net_geometry_stats(pins)
        min_part_gap = float("inf")
        if len(parts) >= 2:
            part_bboxes = [node._part_effective_bbox(part) for part in parts]
            for i, bbox_a in enumerate(part_bboxes):
                for bbox_b in part_bboxes[i + 1:]:
                    min_part_gap = min(
                        min_part_gap, node._bbox_manhattan_gap(bbox_a, bbox_b)
                    )
        if min_part_gap == float("inf"):
            min_part_gap = 0
        is_local_cluster = node._is_local_functional_cluster(net, parts)
        clusters = node._cluster_pins_by_distance(net, pins, **options)
        largest_cluster = clusters[0] if clusters else []
        largest_cluster_ratio = float(len(largest_cluster)) / max(len(pins), 1)

        if node._is_power_net_name(name):
            if (
                is_local_cluster
                and largest_cluster
                and len(largest_cluster) == len(pins)
                and max_dist <= local_cluster_threshold
            ):
                return True
            if (
                largest_cluster
                and len(largest_cluster) >= 2
                and largest_cluster_ratio >= 0.75
                and min_part_gap <= local_wire_threshold
            ):
                return True
            return False

        if is_local_cluster and max_dist <= local_cluster_threshold:
            return True
        if len(parts) <= max_wire_pins and min_dist <= local_wire_threshold:
            return True
        if len(parts) <= max_wire_pins and min_part_gap <= local_wire_threshold:
            return True
        if len(parts) <= 2 and bbox_span <= max_wire_dist:
            return True

        return False

    def _classify_part_role(node, part):
        """Classify part role with conservative heuristics."""
        ref = str(getattr(part, "ref", "") or "").upper()
        name = str(getattr(part, "name", "") or "").upper()
        value = str(getattr(part, "value", "") or "").upper()
        net_names = node._net_names_of(part)
        power_nets = [n for n in net_names if node._is_power_net_name(n)]
        has_power = bool(power_nets)
        has_gnd = any("GND" in n.upper() for n in net_names)
        pin_count = len(getattr(part, "pins", []))

        if ref.startswith(("PWR", "V", "GND")) or node._is_power_net_name(name) or node._is_power_net_name(value):
            return "power"

        if ref.startswith("C"):
            value_norm = value.replace(" ", "")
            decap_tokens = ("100NF", "0.1UF", "0.1U", "1UF", "10NF", "47NF")
            if (has_power and has_gnd) or any(token in value_norm for token in decap_tokens):
                return "decoupling"

        if ref.startswith("U") or pin_count >= 8:
            return "ic"

        if ref.startswith(("J", "P", "CN")):
            return "connector"

        if ref.startswith(("R", "C", "L", "D", "Q")):
            return "passive"

        return "other"

    def _find_main_part(node, parts, adjacency=None):
        """Find a stable main part for a connected group."""
        if not parts:
            return None
        role_map = {part: node._classify_part_role(part) for part in parts}
        ic_parts = [part for part in parts if role_map[part] == "ic"]
        if ic_parts:
            # 使用稳定排序打破并列，确保同样输入始终落在同一主控器件上。
            ranked = sorted(ic_parts, key=node._part_ref_key)
            return max(ranked, key=lambda part: len(getattr(part, "pins", [])))

        def degree(part):
            if adjacency is not None:
                return len(adjacency.get(id(part), set()))
            return len(node._net_names_of(part))

        ranked = sorted(parts, key=node._part_ref_key)
        return max(ranked, key=degree)

    def _place_row(node, parts, start_x, start_y, direction=1, gap=None):
        """Place parts in one row and return row bbox."""
        if gap is None:
            gap = BLK_INT_PAD

        x = start_x
        min_x = float("inf")
        min_y = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")
        max_h = 0
        for part in parts:
            bbox = part.place_bbox
            w = max(bbox.w, GRID)
            h = max(bbox.h, GRID)
            if direction >= 0:
                part.tx = Tx().move(Point(x, start_y))
                x += w + gap
            else:
                part.tx = Tx().move(Point(x - w, start_y))
                x -= w + gap

            placed = part.place_bbox * part.tx
            min_x = min(min_x, placed.min.x)
            min_y = min(min_y, placed.min.y)
            max_x = max(max_x, placed.max.x)
            max_y = max(max_y, placed.max.y)
            max_h = max(max_h, h)

        if min_x == float("inf"):
            return BBox(Point(start_x, start_y), Point(start_x, start_y))

        return BBox(Point(min_x, min_y), Point(max_x, max_y))

    def _placement_ctr(node, part):
        """返回器件放置 bbox 的中心，供几何对齐后处理使用。"""
        return (part.place_bbox * part.tx).ctr

    def _set_part_center_y(node, part, target_y):
        """仅沿 Y 平移器件，使中心落在 target_y（吸附到网格）。"""
        ctr = node._placement_ctr(part)
        snapped_y = Point(ctr.x, target_y).snap(GRID).y
        dy = snapped_y - ctr.y
        if dy:
            part.tx *= Tx(dx=0, dy=dy)

    def _set_part_center_x(node, part, target_x):
        """仅沿 X 平移器件，使中心落在 target_x（吸附到网格）。"""
        ctr = node._placement_ctr(part)
        snapped_x = Point(target_x, ctr.y).snap(GRID).x
        dx = snapped_x - ctr.x
        if dx:
            part.tx *= Tx(dx=dx, dy=0)

    def _identify_trunk_parts(node, main_part, adjacency, roles):
        """识别水平主干候选：主器件 + 已在同一水平带内的近邻。

        不把“所有直接邻居”都拉进主干，避免小电路（如 LED 链）被压成一行后
        引脚落在同一路由坐标上引发 TerminalClash。
        """
        trunk = {main_part}
        main_ctr = node._placement_ctr(main_part)
        main_h = max(main_part.place_bbox.h, GRID)
        neighbors = sorted(
            adjacency.get(id(main_part), set()), key=node._part_ref_key
        )
        for neighbor in neighbors:
            if roles.get(neighbor) in ("decoupling", "power"):
                continue
            n_ctr = node._placement_ctr(neighbor)
            tol = max(main_h, max(neighbor.place_bbox.h, GRID))
            if abs(n_ctr.y - main_ctr.y) <= tol:
                trunk.add(neighbor)
        return trunk

    def _nudge_part_if_clear(node, part, parts, dx, dy):
        """平移器件；若与组内其它 place_bbox 相交则回滚。"""
        if not dx and not dy:
            return False
        old_tx = copy(part.tx)
        part.tx *= Tx(dx=dx, dy=dy)
        bbox = part.place_bbox * part.tx
        for other in parts:
            if other is part:
                continue
            if bbox.intersects(other.place_bbox * other.tx):
                part.tx = old_tx
                return False
        return True

    def _set_part_center_y_safe(node, part, parts, target_y):
        """对齐 Y；若会与其它器件重叠则跳过（保持原位置）。"""
        ctr = node._placement_ctr(part)
        snapped_y = Point(ctr.x, target_y).snap(GRID).y
        dy = snapped_y - ctr.y
        if dy:
            node._nudge_part_if_clear(part, parts, 0, dy)

    def _align_connected_geometry(node, parts, adjacency, roles, main_part):
        """human_readable 专用：启发式摆放后的保守几何对齐后处理。

        主干共线、上下支路分层、左右近似对称，末尾做有限轮垂直去重叠。
        不移动主器件锚点，避免打乱分区布局的“中心”语义。
        """
        if not parts or main_part is None or len(parts) < 2:
            return

        main_ctr = node._placement_ctr(main_part)
        main_y = main_ctr.y
        main_x = main_ctr.x

        trunk = node._identify_trunk_parts(main_part, adjacency, roles)

        # 第 1 步：主干器件共线（水平主干，统一 Y；主器件本身不动）
        for part in sorted(trunk - {main_part}, key=node._part_ref_key):
            node._set_part_center_y_safe(part, parts, main_y)

        max_h = max((max(p.place_bbox.h, GRID) for p in parts), default=GRID)
        branch_gap = max(BLK_INT_PAD + GRID, max_h + GRID)
        y_top = main_y - branch_gap
        y_bottom = main_y + branch_gap

        # 第 2 步：非主干器件按当前相对主干的上下关系分层
        # 电源/去耦/连接器保留分区启发式的位置，避免把左侧纵向连接器压成一行。
        layer_skip_roles = ("connector", "power", "decoupling")
        upper = []
        lower = []
        for part in sorted(parts, key=node._part_ref_key):
            if part in trunk:
                continue
            if roles.get(part) in layer_skip_roles:
                continue
            ctr = node._placement_ctr(part)
            if ctr.y < main_y - GRID * 0.25:
                upper.append(part)
            elif ctr.y > main_y + GRID * 0.25:
                lower.append(part)
            else:
                # 与主干同高带的器件：按 X 相对主器件分到上/下层，避免全挤在主干上
                if ctr.x <= main_x:
                    upper.append(part)
                else:
                    lower.append(part)

        for part in upper:
            node._set_part_center_y_safe(part, parts, y_top)
        for part in lower:
            node._set_part_center_y_safe(part, parts, y_bottom)

        # 第 3 步：左右对称——同 role、相近连接度的成对器件仅对齐 Y（不改 X，避免引脚共线）
        branch_parts = [p for p in parts if p not in trunk]
        left_by_sig = defaultdict(list)
        right_by_sig = defaultdict(list)
        for part in branch_parts:
            ctr = node._placement_ctr(part)
            degree = len(adjacency.get(id(part), set()))
            sig = (roles.get(part), degree)
            if ctr.x < main_x - GRID:
                left_by_sig[sig].append(part)
            elif ctr.x > main_x + GRID:
                right_by_sig[sig].append(part)

        all_sigs = sorted(
            set(left_by_sig.keys()) | set(right_by_sig.keys()),
            key=lambda s: (s[0], s[1]),
        )
        for sig in all_sigs:
            left_list = sorted(left_by_sig.get(sig, []), key=node._part_ref_key)
            right_list = sorted(right_by_sig.get(sig, []), key=node._part_ref_key)
            pair_count = min(len(left_list), len(right_list))
            for i in range(pair_count):
                lp = left_list[i]
                rp = right_list[i]
                l_ctr = node._placement_ctr(lp)
                r_ctr = node._placement_ctr(rp)
                avg_y = (l_ctr.y + r_ctr.y) / 2.0
                node._set_part_center_y_safe(lp, parts, avg_y)
                node._set_part_center_y_safe(rp, parts, avg_y)

        # 第 4 步：保守去重叠——组内任意器件，先垂直再水平小步推开
        for _ in range(25):
            moved = False
            for part in sorted(parts, key=node._part_ref_key):
                bbox = part.place_bbox * part.tx
                for other in parts:
                    if other is part:
                        continue
                    other_bbox = other.place_bbox * other.tx
                    if not bbox.intersects(other_bbox):
                        continue
                    ctr = node._placement_ctr(part)
                    other_ctr = node._placement_ctr(other)
                    dy = BLK_INT_PAD if ctr.y <= other_ctr.y else -BLK_INT_PAD
                    if node._nudge_part_if_clear(part, parts, 0, dy):
                        moved = True
                        break
                    dx = BLK_INT_PAD if ctr.x <= other_ctr.x else -BLK_INT_PAD
                    if node._nudge_part_if_clear(part, parts, dx, 0):
                        moved = True
                        break
                if moved:
                    break
            if not moved:
                break

    def place_connected_parts_rowbased(node, parts, nets, **options):
        """Place connected parts using a BFS row-based layout (O(n)).

        For large groups (>_ROW_PLACE_THRESHOLD), the O(n²) force-directed
        placer is too slow. This places parts in rows following BFS order
        from the most-connected seed part.

        Args:
            node (Node): Node with parts.
            parts (list): List of Parts connected by nets.
            nets (list): List of internal Nets connecting the parts.
            options (dict): Dict of options and values that enable/disable functions.
        """
        from collections import deque

        if not parts:
            return

        # Add bboxes and anchor/pull pins (needed by router).
        add_placement_bboxes(parts, **options)
        add_anchor_pull_pins(parts, nets, **options)

        human_readable = options.get("human_readable", False)

        # Separate the NetTerminals from the other parts.
        net_terminals = [p for p in parts if is_net_terminal(p)]
        real_parts = [p for p in parts if not is_net_terminal(p)]
        if not real_parts:
            return

        # Build adjacency graph: part → set of neighbors.
        adjacency = build_part_adjacency(real_parts, nets)

        if human_readable:
            # 用稳定可读布局替代随机/机械 BFS，减少多次运行时版图漂移。
            # spacing 缩放分区间距，>1 更松散，<1 更紧凑
            _sp = options.get("spacing", 1.0)
            _gap = int(BLK_INT_PAD * _sp)

            roles = {part: node._classify_part_role(part) for part in real_parts}
            main_part = node._find_main_part(real_parts, adjacency=adjacency)
            node._human_readable_main_part = main_part
            main_part.tx = Tx().move(Point(0, 0))
            expand_main_ic_keepout(main_part, GRID)
            main_bbox = main_part.place_bbox * main_part.tx

            def connected_to(part_a, part_b):
                return part_b in adjacency.get(id(part_a), set())

            def io_side_score(part):
                names = [n.upper() for n in node._net_names_of(part)]
                right_tokens = ("OUT", "TX", "MISO", "SCL", "CS", "PWM")
                left_tokens = ("IN", "RX", "MOSI", "SDA", "ADC", "SENSE")
                right = sum(any(token in n for token in right_tokens) for n in names)
                left = sum(any(token in n for token in left_tokens) for n in names)
                return right - left

            remaining = [p for p in real_parts if p is not main_part]
            power_parts = [p for p in remaining if roles[p] == "power"]
            decoupling_parts = [p for p in remaining if roles[p] == "decoupling"]
            connector_parts = [p for p in remaining if roles[p] == "connector"]
            passive_parts = [p for p in remaining if roles[p] == "passive"]
            other_parts = [p for p in remaining if p not in (set(power_parts) | set(decoupling_parts) | set(connector_parts) | set(passive_parts))]

            power_parts = sorted(power_parts, key=node._part_ref_key)
            connector_parts = sorted(connector_parts, key=node._part_ref_key)
            passive_parts = sorted(passive_parts, key=node._part_ref_key)
            other_parts = sorted(other_parts, key=node._part_ref_key)

            left_connectors = []
            right_connectors = []
            for part in connector_parts:
                if io_side_score(part) > 0:
                    right_connectors.append(part)
                else:
                    left_connectors.append(part)

            decoup_near_main = []
            decoup_power = []
            for part in sorted(decoupling_parts, key=node._part_ref_key):
                if connected_to(part, main_part):
                    decoup_near_main.append(part)
                else:
                    decoup_power.append(part)

            # 主器件放中心，其它器件按角色分区，优先形成人读图习惯的左右/上下结构。
            # 分区间距受 spacing 缩放
            top_y = main_bbox.min.y - (_gap + 2 * GRID)
            left_x = main_bbox.min.x - (3 * _gap)
            right_x = main_bbox.max.x + (2 * _gap)
            bottom_y = main_bbox.max.y + (2 * _gap)

            top_row = power_parts + decoup_power
            if top_row:
                node._place_row(top_row, left_x, top_y, direction=1, gap=_gap)

            if decoup_near_main:
                node._place_row(
                    decoup_near_main,
                    main_bbox.min.x,
                    main_bbox.min.y - _gap,
                    direction=1,
                    gap=GRID,
                )

            if left_connectors:
                y = main_bbox.min.y
                for part in left_connectors:
                    bbox = part.place_bbox
                    part.tx = Tx().move(Point(left_x - bbox.w, y))
                    y += max(bbox.h, GRID) + _gap

            if right_connectors:
                y = main_bbox.min.y
                for part in right_connectors:
                    part.tx = Tx().move(Point(right_x, y))
                    y += max(part.place_bbox.h, GRID) + _gap

            passive_near = []
            passive_far = []
            for part in passive_parts:
                if connected_to(part, main_part):
                    passive_near.append(part)
                else:
                    passive_far.append(part)

            if passive_near:
                node._place_row(
                    passive_near,
                    main_bbox.max.x + _gap,
                    main_bbox.max.y + _gap,
                    direction=1,
                    gap=_gap,
                )
            if passive_far:
                node._place_row(
                    passive_far,
                    main_bbox.min.x - _gap,
                    bottom_y,
                    direction=1,
                    gap=_gap,
                )

            if other_parts:
                node._place_row(other_parts, right_x, bottom_y, direction=1, gap=_gap)

            # 分区摆放后再做几何对齐（主干共线、支路分层、左右对称、去重叠）。
            node._align_connected_geometry(
                real_parts, adjacency, roles, main_part
            )

            apply_topology_or_trunk_layout(
                node,
                real_parts,
                nets,
                roles,
                main_part,
                grid=GRID,
                blk_int_pad=BLK_INT_PAD,
                **options,
            )

            for part in real_parts:
                snap_to_grid(part)
        else:
            # Pick seed: part with most connections.
            seed = max(real_parts, key=lambda p: len(adjacency.get(id(p), set())))

            # BFS traversal, placing in rows.
            visited = {id(seed)}
            queue = deque([seed])
            order = []
            while queue:
                part = queue.popleft()
                order.append(part)
                for neighbor in adjacency.get(id(part), set()):
                    if id(neighbor) not in visited:
                        visited.add(id(neighbor))
                        queue.append(neighbor)

            # Add any parts not reached by BFS (disconnected within the group).
            for part in sorted(real_parts, key=node._part_ref_key):
                if id(part) not in visited:
                    order.append(part)

            # Compute total area to determine max row width.
            total_area = sum(
                max(p.place_bbox.w, 1) * max(p.place_bbox.h, 1) for p in order
            )
            max_row_width = math.sqrt(total_area) * 2

            # Place parts in rows.
            col_x = 0
            row_y = 0
            row_max_h = 0
            for part in order:
                w = max(part.place_bbox.w, 100)
                h = max(part.place_bbox.h, 100)

                if col_x > 0 and col_x + w > max_row_width:
                    # Start new row.
                    row_y += row_max_h + BLK_INT_PAD
                    col_x = 0
                    row_max_h = 0

                part.tx = Tx().move(Point(col_x, row_y))
                col_x += w + BLK_INT_PAD
                row_max_h = max(row_max_h, h)

            # Snap to grid.
            for part in order:
                snap_to_grid(part)

        if net_terminals:
            place_net_terminals(
                net_terminals, real_parts, nets, total_part_force, **options
            )

    def place_connected_parts(node, parts, nets, **options):
        """Place individual parts.

        Args:
            node (Node): Node with parts.
            parts (list): List of Part sets connected by nets.
            nets (list): List of internal Nets connecting the parts.
            options (dict): Dict of options and values that enable/disable functions.
        """

        if not parts:
            # Abort if nothing to place.
            return

        # Use row-based placement for large groups.
        real_count = sum(1 for p in parts if not is_net_terminal(p))
        if real_count > node._ROW_PLACE_THRESHOLD:
            return node.place_connected_parts_rowbased(parts, nets, **options)

        # Add bboxes with surrounding area so parts are not butted against each other.
        add_placement_bboxes(parts, **options)

        # Set anchor and pull pins that determine attractive forces between parts.
        add_anchor_pull_pins(parts, nets, **options)

        # Randomly place connected parts.
        random_placement(parts)

        if options.get("draw_placement"):
            # Draw the placement for debug purposes.
            bbox = get_enclosing_bbox(parts)
            draw_scr, draw_tx, draw_font = draw_start(bbox)
            options.update(
                {"draw_scr": draw_scr, "draw_tx": draw_tx, "draw_font": draw_font}
            )

        if options.get("compress_before_place"):
            central_placement(parts, **options)

        # Do force-directed placement of the parts in the parts.

        # Separate the NetTerminals from the other parts.
        net_terminals = [part for part in parts if is_net_terminal(part)]
        real_parts = [part for part in parts if not is_net_terminal(part)]

        # Do the first trial placement.
        evolve_placement([], real_parts, nets, total_part_force, **options)

        if options.get("rotate_parts"):
            # Adjust part orientations after first trial placement is done.
            if adjust_orientations(real_parts, **options):
                # Some part orientations were changed, so re-do placement.
                evolve_placement([], real_parts, nets, total_part_force, **options)

        if options.get("human_readable", False) and len(real_parts) >= 2:
            from skidl.schematics.place_small_group import beautify_small_connected_group

            # 小组力导向之后做弱美化（独立模块），避免过强共线引发 routing 冲突。
            beautify_small_connected_group(
                real_parts,
                classify_role=node._classify_part_role,
                part_ref_key=node._part_ref_key,
                grid=GRID,
                blk_int_pad=BLK_INT_PAD,
            )
            roles = {part: node._classify_part_role(part) for part in real_parts}
            main_part = node._find_main_part(real_parts)
            node._human_readable_main_part = main_part
            expand_main_ic_keepout(main_part, GRID)
            apply_topology_or_trunk_layout(
                node,
                real_parts,
                nets,
                roles,
                main_part,
                grid=GRID,
                blk_int_pad=BLK_INT_PAD,
                **options,
            )
            for part in real_parts:
                snap_to_grid(part)

        # Place NetTerminals after all the other parts.
        place_net_terminals(
            net_terminals, real_parts, nets, total_part_force, **options
        )

        if options.get("draw_placement"):
            # Pause to look at placement for debugging purposes.
            draw_pause()

    def place_floating_parts(node, parts, **options):
        """Place individual parts.

        Args:
            node (Node): Node with parts.
            parts (list): List of Parts not connected by explicit nets.
            options (dict): Dict of options and values that enable/disable functions.
        """

        if not parts:
            # Abort if nothing to place.
            return

        human_readable = options.get("human_readable", False)

        # For large numbers of floating parts, skip the O(n^2) similarity
        # computation and force-directed evolution. Just grid-place them.
        # This avoids the 100+ second penalty for 60+ identical decoupling caps.
        _FLOAT_GRID_THRESHOLD = 20
        if human_readable:
            add_placement_bboxes(parts)
            role_buckets = defaultdict(list)
            for part in parts:
                role_buckets[node._classify_part_role(part)].append(part)

            role_order = ["power", "decoupling", "passive", "ic", "connector", "other"]
            y = 0
            for role in role_order:
                bucket = role_buckets.get(role, [])
                if not bucket:
                    continue

                # 同类器件按 value/ref 稳定排序，避免每次生成顺序漂移。
                if role == "passive":
                    subtype = defaultdict(list)
                    for part in bucket:
                        ref = str(getattr(part, "ref", "") or "").upper()
                        prefix = ref[:1]
                        subtype[prefix].append(part)
                    sub_order = ["R", "C", "L", "D", "Q", ""]
                    for key in sub_order:
                        sub_parts = subtype.get(key, [])
                        if not sub_parts:
                            continue
                        sub_parts = sorted(
                            sub_parts,
                            key=lambda p: (
                                str(getattr(p, "value", "") or "").lower(),
                                node._part_ref_key(p),
                            ),
                        )
                        row_bbox = node._place_row(sub_parts, 0, y, direction=1, gap=BLK_INT_PAD)
                        y = row_bbox.max.y + BLK_INT_PAD
                else:
                    bucket = sorted(
                        bucket,
                        key=lambda p: (
                            str(getattr(p, "value", "") or "").lower(),
                            node._part_ref_key(p),
                        ),
                    )
                    row_bbox = node._place_row(bucket, 0, y, direction=1, gap=BLK_INT_PAD)
                    y = row_bbox.max.y + BLK_INT_PAD

            for part in parts:
                snap_to_grid(part)
            return

        if len(parts) > _FLOAT_GRID_THRESHOLD and options.get("auto_stub", False):
            add_placement_bboxes(parts)
            # Simple grid layout for floating parts.
            cols = max(1, int(len(parts) ** 0.5))
            for i, part in enumerate(parts):
                row, col = divmod(i, cols)
                bbox = part.place_bbox
                w = bbox.w if bbox.w > 0 else 200
                h = bbox.h if bbox.h > 0 else 200
                part.tx = Tx().move(Point(col * w * 1.2, row * h * 1.2))
            return

        # Add bboxes with surrounding area so parts are not butted against each other.
        add_placement_bboxes(parts)

        # Set anchor and pull pins that determine attractive forces between similar parts.
        add_anchor_pull_pins(parts, [], **options)

        # Randomly place the floating parts.
        random_placement(parts)

        if options.get("draw_placement"):
            # Compute the drawing area for the floating parts
            bbox = get_enclosing_bbox(parts)
            draw_scr, draw_tx, draw_font = draw_start(bbox)
            options.update(
                {"draw_scr": draw_scr, "draw_tx": draw_tx, "draw_font": draw_font}
            )

        # For non-connected parts, do placement based on their similarity to each other.
        part_similarity = defaultdict(lambda: defaultdict(lambda: 0))
        for part in parts:
            for other_part in parts:
                # Don't compute similarity of a part to itself.
                if other_part is part:
                    continue

                # HACK: Get similarity forces right-sized.
                part_similarity[part][other_part] = part.similarity(other_part) / 100
                # part_similarity[part][other_part] = 0.1

            # Select the top-most pin in each part as the anchor point for force-directed placement.
            # tx = part.tx
            # part.anchor_pin = max(part.anchor_pins, key=lambda pin: (pin.place_pt * tx).y)

        force_func = functools.partial(
            total_similarity_force, similarity=part_similarity
        )

        if options.get("compress_before_place"):
            # Compress all floating parts together.
            central_placement(parts, **options)

        # Do force-directed placement of the parts in the group.
        evolve_placement([], parts, [], force_func, **options)

        if options.get("draw_placement"):
            # Pause to look at placement for debugging purposes.
            draw_pause()

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

        # Global dict of pull pins for all blocks as they each pull on each other the same way.
        block_pull_pins = defaultdict(list)

        # Class for movable groups of parts/child nodes.
        class PartBlock:
            def __init__(self, src, bbox, anchor_pt, snap_pt, tag):
                self.src = src  # Source for this block.
                self.place_bbox = bbox  # FIXME: Is this needed if place_bbox includes room for routing?

                # Create anchor pin to which forces are applied to this block.
                anchor_pin = Pin()
                anchor_pin.part = self
                anchor_pin.place_pt = anchor_pt

                # This block has only a single anchor pin, but it needs to be in a list
                # in a dict so it can be processed by the part placement functions.
                self.anchor_pins = dict()
                self.anchor_pins["similarity"] = [anchor_pin]

                # Anchor pin for this block is also a pulling pin for all other blocks.
                block_pull_pins["similarity"].append(anchor_pin)

                # All blocks have the same set of pulling pins because they all pull each other.
                self.pull_pins = block_pull_pins

                self.snap_pt = snap_pt  # For snapping to grid.
                self.tx = Tx()  # For placement.
                self.ref = "REF"  # Name for block in debug drawing.
                self.tag = tag  # FIXME: what is this for?

        # Create a list of blocks from the groups of interconnected parts and the group of floating parts.
        part_blocks = []
        for part_list in connected_parts + [floating_parts]:
            if not part_list:
                # No parts in this list for some reason...
                continue

            # Find snapping point and bounding box for this group of parts.
            snap_pt = None
            bbox = BBox()
            for part in part_list:
                bbox.add(part.lbl_bbox * part.tx)
                if not snap_pt:
                    # Use the first snapping point of a part you can find.
                    snap_pt = get_snap_pt(part)

            # Tag indicates the type of part block.
            tag = 2 if (part_list is floating_parts) else 1

            # 块间外部留白受 spacing 缩放
            _sp = options.get("spacing", 1.0)
            pad = int(BLK_EXT_PAD * _sp)
            bbox = bbox.resize(Vector(pad, pad))

            # Create the part block and place it on the list.
            part_blocks.append(PartBlock(part_list, bbox, bbox.ctr, snap_pt, tag))

        # Add part blocks for child nodes.
        for child in children:
            # Calculate bounding box of child node.
            bbox = child.calc_bbox()

            # 子节点块间留白同样受 spacing 缩放
            _sp = options.get("spacing", 1.0)
            if child.flattened:
                pad = int((BLK_INT_PAD + BLK_EXT_PAD) * _sp)
            else:
                pad = int(BLK_EXT_PAD * _sp)
            bbox = bbox.resize(Vector(pad, pad))

            # Set the grid snapping point and tag for this child node.
            snap_pt = child.get_snap_pt()
            tag = 3  # Standard child node.
            if not snap_pt:
                # No snap point found, so just use the center of the bounding box.
                snap_pt = bbox.ctr
                tag = 4  # A child node with no snapping point.

            # Create the child block and place it on the list.
            part_blocks.append(PartBlock(child, bbox, bbox.ctr, snap_pt, tag))

        # Get ordered list of all block tags. Use this list to tell if tags are
        # adjacent since there may be missing tags if a particular type of block
        # isn't present.
        tags = sorted({blk.tag for blk in part_blocks})

        # Tie the blocks together with strong links between blocks with the same tag,
        # and weaker links between blocks with adjacent tags. This ties similar
        # blocks together into "super blocks" and ties the super blocks into a linear
        # arrangement (1 -> 2 -> 3 ->...).
        blk_attr = defaultdict(lambda: defaultdict(lambda: 0))
        for blk in part_blocks:
            for other_blk in part_blocks:
                if blk is other_blk:
                    # No attraction between a block and itself.
                    continue
                if blk.tag == other_blk.tag:
                    # Large attraction between blocks of same type.
                    blk_attr[blk][other_blk] = 1
                elif abs(tags.index(blk.tag) - tags.index(other_blk.tag)) == 1:
                    # Some attraction between blocks of adjacent types.
                    blk_attr[blk][other_blk] = 0.1
                else:
                    # Otherwise, no attraction between these blocks.
                    blk_attr[blk][other_blk] = 0

        if not part_blocks:
            # Abort if nothing to place.
            return

        human_readable = options.get("human_readable", False)

        # For large block counts, use a simple grid layout instead of
        # O(n²) force-directed placement.
        if len(part_blocks) > node._ROW_PLACE_THRESHOLD:
            if human_readable:
                # 分区摆放块对象，让主连通块在中部、浮动块在下方、子层级块在右侧，增强阅读方向感。
                def blk_key(blk):
                    src = blk.src
                    ref = str(getattr(src, "ref", getattr(src, "name", "")) or "")
                    return (blk.tag, -(blk.place_bbox.w * blk.place_bbox.h), ref.lower())

                connected_blks = sorted([b for b in part_blocks if b.tag == 1], key=blk_key)
                floating_blks = sorted([b for b in part_blocks if b.tag == 2], key=blk_key)
                child_blks = sorted([b for b in part_blocks if b.tag in (3, 4)], key=blk_key)

                y = 0
                if connected_blks:
                    row_bbox = node._place_row(
                        connected_blks, 0, y, direction=1, gap=BLK_EXT_PAD
                    )
                    y = row_bbox.max.y + BLK_EXT_PAD

                if floating_blks:
                    row_bbox = node._place_row(
                        floating_blks, 0, y + BLK_EXT_PAD, direction=1, gap=BLK_EXT_PAD
                    )
                    y = row_bbox.max.y + BLK_EXT_PAD

                if child_blks:
                    right_x = 0
                    if connected_blks or floating_blks:
                        total_bbox = get_enclosing_bbox(connected_blks + floating_blks)
                        right_x = total_bbox.max.x + BLK_EXT_PAD
                    node._place_row(
                        child_blks, right_x, BLK_EXT_PAD, direction=1, gap=BLK_EXT_PAD
                    )

                for blk in part_blocks:
                    snap_to_grid(blk)
            else:
                cols = max(1, int(len(part_blocks) ** 0.5))
                for i, blk in enumerate(part_blocks):
                    row, col = divmod(i, cols)
                    w = blk.place_bbox.w if blk.place_bbox.w > 0 else 500
                    h = blk.place_bbox.h if blk.place_bbox.h > 0 else 500
                    blk.tx = Tx().move(Point(col * (w + BLK_EXT_PAD), row * (h + BLK_EXT_PAD)))
                    snap_to_grid(blk)

            # Apply the placement moves of the part blocks to their underlying sources.
            for blk in part_blocks:
                try:
                    blk.src.tx = blk.tx
                except AttributeError:
                    for part in blk.src:
                        part.tx *= blk.tx
            return

        # Start off with a random placement of part blocks.
        random_placement(part_blocks)

        if options.get("draw_placement"):
            # Setup to draw the part block placement for debug purposes.
            bbox = get_enclosing_bbox(part_blocks)
            draw_scr, draw_tx, draw_font = draw_start(bbox)
            options.update(
                {"draw_scr": draw_scr, "draw_tx": draw_tx, "draw_font": draw_font}
            )

        # Arrange the part blocks with similarity force-directed placement.
        force_func = functools.partial(total_similarity_force, similarity=blk_attr)
        evolve_placement([], part_blocks, [], force_func, **options)

        if options.get("draw_placement"):
            # Pause to look at placement for debugging purposes.
            draw_pause()

        # Apply the placement moves of the part blocks to their underlying sources.
        for blk in part_blocks:
            try:
                # Update the Tx matrix of the source (usually a child node).
                blk.src.tx = blk.tx
            except AttributeError:
                # The source doesn't have a Tx so it must be a collection of parts.
                # Apply the block placement to the Tx of each part.
                for part in blk.src:
                    part.tx *= blk.tx

    def get_attrs(node):
        """Return dict of attribute sets for the parts, pins, and nets in a node."""
        attrs = {"parts": set(), "pins": set(), "nets": set()}
        for part in node.parts:
            attrs["parts"].update(set(dir(part)))
            for pin in part.pins:
                attrs["pins"].update(set(dir(pin)))
        for net in node.get_internal_nets():
            attrs["nets"].update(set(dir(net)))
        return attrs

    def show_added_attrs(node):
        """Show attributes that were added to parts, pins, and nets in a node."""
        current_attrs = node.get_attrs()
        for key in current_attrs.keys():
            print(
                f"added {key} attrs: {current_attrs[key] - node.attrs[key]}"
            )

    def rmv_placement_stuff(node):
        """Remove attributes added to parts, pins, and nets of a node during the placement phase."""

        for part in node.parts:
            rmv_attr(part.pins, ("route_pt", "place_pt"))
        rmv_attr(
            node.parts,
            ("anchor_pins", "pull_pins", "pin_ctrs", "force", "mv"),
        )
        rmv_attr(node.get_internal_nets(), ("parts",))

    def _auto_stub_cross_group(node, groups, **options):
        """Stub nets that span multiple placement groups.

        When auto_stub is enabled, nets connecting parts in different groups
        can create long or congested routes. However, stubbing every
        cross-group net destroys local topology, so keep small local motifs as
        visible wires and reserve labels for clearly global connections.

        Args:
            node: The SchNode being placed.
            groups: List of sets of parts from group_parts().
            options: Dict of options; requires auto_stub=True to take effect.
        """
        if not options.get("auto_stub", False):
            return

        part_to_group = {}
        for i, group in enumerate(groups):
            for part in group:
                part_to_group[id(part)] = i

        for part in node.parts:
            for pin in part:
                if not pin.is_connected():
                    continue
                net = pin.net
                if getattr(net, "_stub_explicit", False) or getattr(
                    net, "stub", False
                ):
                    continue
                pin_groups = {
                    part_to_group[id(p.part)]
                    for p in net.pins
                    if id(p.part) in part_to_group
                }
                if len(pin_groups) > 1 and not node._prefer_visible_wire_preplacement(
                    net, part_to_group, **options
                ):
                    net._stub = True
                    net._stub_explicit = False
                    for p in net.get_pins():
                        p.stub = True

    def _auto_stub_large_groups(node, groups, internal_nets, **options):
        """Split oversized placement groups by stubbing 2-pin chain nets.

        Large groups (e.g. 138-part LED daisy chains) overwhelm the O(n^2)
        force-directed placer. This finds 2-pin nets within large groups and
        stubs enough of them to break the group into smaller chunks.

        Args:
            node: The SchNode being placed.
            groups: List of sets of parts from group_parts().
            internal_nets: Dict mapping net id to net objects.
            options: Dict of options; requires auto_stub=True to take effect.
                auto_stub_max_group (int): Max parts per group. Default 30.
        """
        if not options.get("auto_stub", False):
            return

        max_group = options.get("auto_stub_max_group", 20)
        human_readable = options.get("human_readable", False)

        for group in groups:
            if len(group) <= max_group:
                continue

            # Collect low-fanout internal nets in this group (chain links
            # and small-fanout connections). Prioritize 2-pin nets (chains),
            # then 3-pin, then 4-pin.
            group_ids = {id(p) for p in group}
            chain_nets = []
            for net in internal_nets:
                if getattr(net, "_stub_explicit", False) or getattr(
                    net, "stub", False
                ):
                    continue
                net_parts = {
                    id(p.part) for p in net.pins if id(p.part) in group_ids
                }
                if 2 <= len(net_parts) <= 4:
                    parts = [p for p in node._net_connected_parts(net) if id(p) in group_ids]
                    if node._is_local_functional_cluster(net, parts):
                        continue
                    name = str(getattr(net, "name", "") or "")
                    is_power = node._is_power_net_name(name)
                    chain_nets.append((len(net_parts), 0 if is_power else 1, name.lower(), net))

            if human_readable:
                # 人类可读模式优先 stub 电源/跨域感强的连线，尽量保留近距离两点线条的连线感。
                chain_nets.sort(key=lambda x: (x[1], -x[0], x[2]))
            else:
                chain_nets.sort(key=lambda x: x[0])
            chain_nets = [net for _, _, _, net in chain_nets]

            if not chain_nets:
                continue

            active_logger.info(
                f"  [auto_stub_large_groups] Group of {len(group)} parts, "
                f"{len(chain_nets)} chain nets, splitting..."
            )

            # Stub evenly-spaced chain nets to split the group into chunks
            # of ~max_group parts. We need ceil(len/max)-1 cuts minimum.
            n_cuts = max(1, (len(group) + max_group - 1) // max_group)
            stubbed = 0
            if human_readable:
                # 保守地只打必要数量的 stub，避免“全图都是标签”导致可读性下降。
                for net in chain_nets[:n_cuts]:
                    net._stub = True
                    net._stub_explicit = False
                    for p in net.get_pins():
                        p.stub = True
                    stubbed += 1
            else:
                step = max(1, len(chain_nets) // (n_cuts + 1))
                if step < 1:
                    step = 1
                for i in range(step, len(chain_nets), step):
                    net = chain_nets[i]
                    net._stub = True
                    net._stub_explicit = False
                    for p in net.get_pins():
                        p.stub = True
                    stubbed += 1

            active_logger.info(
                f"  [auto_stub_large_groups] Stubbed {stubbed} nets"
            )

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

        tool = tool or skidl.config.tool
        this_module = sys.modules[__name__]
        this_module.__dict__.update(tool_modules[tool].constants.__dict__)

        seed = options.get("seed")
        if options.get("human_readable", False) and seed is None:
            # 人类可读模式默认固定随机种子，保证同一输入的输出稳定可回归。
            seed = 0
        random.seed(seed)

        # Store the starting attributes of the node's parts, pins, and nets.
        node.attrs = node.get_attrs()

        sheet = getattr(node, "name", "?")

        try:
            # First, recursively place children of this node.
            # TODO: Child nodes are independent, so can they be processed in parallel?
            for child in node.children.values():
                child.place(tool=tool, **options)

            if node.parts:
                _sch_progress(
                    options,
                    f"[schematic] 布局 sheet={sheet}：{len(node.parts)} 件",
                )

            # Group parts into those that are connected by explicit nets and
            # those that float freely connected only by stub nets.
            connected_parts, internal_nets, floating_parts = node.group_parts(**options)

            # Auto-stub nets spanning multiple placement groups.
            node._auto_stub_cross_group(connected_parts, **options)

            # Split oversized groups by stubbing chain nets.
            node._auto_stub_large_groups(
                connected_parts, internal_nets, **options
            )

            if options.get("auto_stub", False):
                # Re-group after stubbing may have changed connectivity.
                connected_parts, internal_nets, floating_parts = node.group_parts(
                    **options
                )

            # Place each group of connected parts.
            for group in connected_parts:
                node.place_connected_parts(list(group), internal_nets, **options)

            # Place the floating parts that have no connections to anything else.
            node.place_floating_parts(list(floating_parts), **options)

            # Now arrange all the blocks of placed parts and the child nodes within this node.
            node.place_blocks(
                connected_parts, floating_parts, node.children.values(), **options
            )

            # Remove any stuff leftover from this place & route run.
            node.rmv_placement_stuff()

            # Calculate the bounding box for the node after placement of parts and children.
            node.calc_bbox()

            if node.parts:
                _sch_progress(options, f"[schematic] 布局完成 sheet={sheet}")

        except PlacementFailure:
            node.rmv_placement_stuff()
            raise PlacementFailure

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
