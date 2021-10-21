# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""
Arrange part units for best schematic wiring.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import math
import re
from builtins import str, super
from collections import namedtuple
from functools import reduce
from random import randint

from future import standard_library

from .coord import *
from .net import NCNet

standard_library.install_aliases()


# foreach net, record which part units are attached to each net.
# assign each part unit to a region.
# compute cost for placement:
#     foreach region, sum the pins for the part units assigned to that region.
#     foreach net:
#         compute the bounding box.
#         cost of the net is the square-root of the number of pins within its bounding box.
#         add net cost to the total cost.
#
# compute cost of moving a part unit to another region:
#     remove pins from source region and add to destination region.
#     compute new cost


class Region(Point):
    """Stores an (x,y) coord and a list of the parts stored within it."""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.clear()

    def clear(self):
        try:
            for part in self.parts:
                part.region = None
        except AttributeError:
            pass
        self.parts = []
        self.num_pins = 0

    def add(self, part):
        assert part not in self.parts
        self.parts.append(part)
        self.num_pins += len(part)
        part.region = self
        return self

    def rmv(self, part):
        assert part in self.parts
        self.parts.remove(part)
        self.num_pins -= len(part)
        part.region = None
        assert part not in self.parts
        return self

    def cost(self):
        # Cost of a region is the sqrt of the number of pins on the parts in it.
        return math.sqrt(self.num_pins)


class PartNet:
    """Stores the parts attached to a particular net."""

    def __init__(self, net):
        # Find the set of parts having one or more pins attached to this net.
        self.parts = set()
        if not isinstance(net, NCNet):
            # Add the part (or part unit) associated with each pin on the net.
            for pin in net.get_pins():
                part = pin.part
                for name, unit in part.unit.items():
                    if pin in unit.pins:
                        break
                else:
                    unit = part
                self.parts.add(unit)

    def calc_bbox(self):
        # The bounding box of a net surrounds the regions
        # of all the parts on the net.
        self.bbox = BBox()
        for part in list(self.parts):
            self.bbox.add(part.region)
        self.bbox.round()

    def cost(self, regions):
        # The cost of a net is the sum of the costs of the regions
        # within the bounding box of the net.
        cst = 0
        self.calc_bbox()
        for y in range(self.bbox.min.y, self.bbox.max.y + 1):
            for x in range(self.bbox.min.x, self.bbox.max.x + 1):
                cst += regions[x][y].cost()
        return cst


class Arranger:
    def __init__(self, circuit, grid_hgt=3, grid_wid=3):
        """
        Create a W x H array of regions to store arrangement of circuit parts.
        """
        self.w, self.h = grid_wid, grid_hgt
        self.regions = [[Region(x, y) for y in range(self.h)] for x in range(self.w)]
        self.parts = []
        for part in circuit.parts:
            if part.unit:
                # Append the units comprising a part.
                for unit in part.unit.values():
                    self.parts.append(unit)
            else:
                # Append the entire part if it isn't broken into units.
                self.parts.append(part)
        for part in self.parts:
            part.move_box = BBox(Point(0, 0), Point(grid_wid - 1, grid_hgt - 1))
        self.nets = [PartNet(net) for net in circuit.nets if net.pins]
        self.clear()

    def clear(self):
        """Clear the parts from the regions."""
        for x in range(self.w):
            for y in range(self.h):
                self.regions[x][y].clear()

    def cost(self):
        """Compute the cost of the arrangement of parts to regions."""
        return sum([net.cost(self.regions) for net in self.nets])

    def apply(self):
        """Apply an assignment stored in regions to parts."""
        for y in range(self.h):
            for x in range(self.w):
                region = self.regions[x][y]
                for part in region.parts:
                    part.region = region

    def prearranged(self):
        """Apply the (x,y) position of parts to update the regions."""
        self.clear()
        for part in self.parts:
            x, y = part.xy
            self.regions[x][y].add(part)

    def arrange_randomly(self):
        """Arrange the parts randomly across the regions."""
        self.clear()
        for part in self.parts:
            if hasattr(part, "fix"):
                x, y = part.xy
            else:
                min_pt = part.move_box.min
                max_pt = part.move_box.max
                x = randint(min_pt.x, max_pt.x - 1)
                y = randint(min_pt.y, max_pt.y - 1)
            self.regions[x][y].add(part)
            assert part.region == self.regions[x][y]
            assert part in self.regions[x][y].parts

    def expand_grid(self, mul_hgt, mul_wid):
        """Expand the number of rows/columns in the grid of regions."""
        new_regions = [
            [Region(x, y) for y in range(self.h * mul_hgt)]
            for x in range(self.w * mul_wid)
        ]
        for part in self.parts:
            x0, y0 = part.region.x * mul_wid, part.region.y * mul_hgt
            x1, y1 = x0 + mul_wid - 1, y0 + mul_hgt - 1
            new_regions[x0][y0].add(part)
            part.move_box = BBox(Point(x0, y0), Point(x1, y1))
        del self.regions
        self.regions = new_regions
        self.h *= mul_hgt
        self.w *= mul_wid

    def arrange_kl(self):
        """Optimally arrange the parts across regions using Kernighan-Lin."""

        class Move:
            # Class for storing the move of a part to a region.
            def __init__(self, part, region, cost):
                self.part = part  # Part being moved.
                self.region = region  # Region being moved to.
                self.cost = cost  # Cost after the move.

        def kl_iteration():
            # Kernighan-Lin algorithm to optimize symbol placement:
            #   A. Compute cost of moving each part to each region while
            #      keeping all the other parts fixed.
            #   B. Select the part and region that has the lowest cost
            #      and move that part to that region.
            #   C. Repeat the A & B for the remaining parts until no
            #      parts remain.
            #   D. Find the point in the sequence of moves where the
            #      cost reaches its lowest value. Reverse all moves
            #      after that point.

            def find_best_move(parts):
                # Find the best of all possible movements of parts to regions.

                # This stores the best move found across all parts & regions.
                best_move = Move(None, None, float("inf"))

                # Move each part to each region, looking for the best cost improvement.
                for part in parts:

                    # Don't move a part that is fixed to a particular region.
                    if hasattr(part, "fix"):
                        continue

                    # Save the region of the current part and remove the
                    # part from that region.
                    saved_region = part.region
                    saved_region.rmv(part)
                    assert part.region == None
                    assert part not in saved_region.parts

                    # Move the current part to each region and store the move if cost goes down.
                    for x in range(part.move_box.min.x, part.move_box.max.x + 1):
                        for y in range(part.move_box.min.y, part.move_box.max.y + 1):

                            # Don't move a part to the region it's already in.
                            if self.regions[x][y] is part.region:
                                continue

                            # Move part to region.
                            self.regions[x][y].add(part)

                            # Get cost when part is in that region.
                            cost = self.cost()

                            # Record move if it's the best seen so far.
                            if cost < best_move.cost:
                                best_move = Move(part, part.region, cost)

                            # Remove part from the region.
                            self.regions[x][y].rmv(part)
                            assert part.region == None

                    # Return the part to its original region.
                    assert part.region == None
                    saved_region.add(part)
                    assert part in saved_region.parts
                    assert part.region == saved_region

                # Return the move with the lowest cost.
                return best_move

            # Store the beginning arrangement of parts.
            beginning_arrangement = {part: part.region for part in self.parts}
            beginning_cost = self.cost()

            # Get the list of parts that can be moved.
            movable = [part for part in self.parts if not hasattr(part, "fix")]

            # Process all the movable parts until every one has been moved.
            moves = []
            while movable:

                # Find and save the best move of all the movable parts.
                best_move = find_best_move(movable)
                moves.append(best_move)

                # Move the selected part from the region where it was to its new region.
                best_move.part.region.rmv(best_move.part)
                best_move.region.add(best_move.part)

                # Remove the part from the list of removable parts once it has been moved.
                movable.remove(best_move.part)

            # Find where the cost was lowest across the sequence of moves.
            low_pt = min(moves, key=lambda mv: mv.cost)
            low_pt_idx = moves.index(low_pt)
            if low_pt.cost >= beginning_cost:
                # No improvement in cost, so put everything back the way it was.
                low_pt_idx = -1
                low_pt.cost = beginning_cost

            # Reverse all the part moves after the lowest point to their original regions.
            for move in moves[low_pt_idx + 1 :]:
                part = move.part
                new_region = move.region
                original_region = beginning_arrangement[part]
                new_region.rmv(part)
                original_region.add(part)

            # Recompute the cost.
            cost = self.cost()
            assert math.isclose(low_pt.cost, cost, rel_tol=0.0001)
            return cost

        # Iteratively apply KL until cost doesn't go down anymore.
        cost = self.cost()
        best_cost = cost + 1  # Make it higher so the following loop will run.
        while cost < best_cost:
            best_cost = cost
            cost = kl_iteration()

        assert math.isclose(best_cost, self.cost(), rel_tol=0.0001)
