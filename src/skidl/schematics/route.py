# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Autorouter for generating wiring between symbols in a schematic.
"""

import copy
import heapq
import random
import sys
from collections import Counter, defaultdict
from enum import Enum
from itertools import chain, zip_longest

from skidl import Part
from skidl.utilities import export_to_all, rmv_attr
from .debug_draw import draw_end, draw_endpoint, draw_routing, draw_seg, draw_start, draw_text
from skidl.geometry import BBox, Point, Segment, Tx, Vector, tx_rot_90
from .topology import (
    build_driver_rail_plan,
    restore_driver_wire_nets,
    topology_route_rank_bias,
)
from .trunk_layout import is_trunk_net_name, trunk_route_rank_bias


__all__ = ["RoutingFailure", "GlobalRoutingFailure", "SwitchboxRoutingFailure"]


def _build_route_part_obstacles(node, human_readable=False):
    """构建布线障碍 bbox；human_readable 下主控 IC 外扩 keepout。"""
    grid = globals().get("GRID", 100)
    main_part = getattr(node, "_human_readable_main_part", None)
    obstacles = []
    for part in node.parts:
        bbox = part.bbox * part.tx
        if human_readable and part is main_part:
            bbox = bbox.resize(Vector(grid * 1.5, grid * 1.5))
        obstacles.append((part, bbox))
    return obstacles


def _sch_progress(options, message):
    """schematic_progress=True 时输出阶段日志，便于定位 place/route/cleanup 卡点。"""
    if options.get("schematic_progress", False):
        from skidl.logger import active_logger

        active_logger.info(message)


def _driver_rail_corridor_hits_bbox(bb, rail_y, x_min, x_max, grid, side="top"):
    """与 topology._rail_corridor_intersects_bbox 相同，供预布线避让。"""
    if x_max < bb.min.x or x_min > bb.max.x:
        return False
    if side == "top":
        band_lo, band_hi = rail_y, rail_y + grid
    else:
        band_lo, band_hi = rail_y - grid, rail_y
    return not (bb.max.y < band_lo or bb.min.y > band_hi)


def _shift_driver_rail_y(node, rail_y, x_min, x_max, grid, side, max_tries=5):
    """预布线前再次外移 rail_y，避免水平线穿过器件可见外框（非 place_bbox 膨胀）。"""
    from skidl.schematics.topology import _part_visual_bbox

    real = [p for p in node.parts if getattr(p, "ref", None) and getattr(p, "tx", None)]
    for _ in range(max_tries):
        blocked = False
        for part in real:
            bb = _part_visual_bbox(part)
            if bb is None:
                continue
            if _driver_rail_corridor_hits_bbox(bb, rail_y, x_min, x_max, grid, side):
                blocked = True
                break
        if not blocked:
            return rail_y
        if side == "top":
            rail_y -= grid
        else:
            rail_y += grid
    return rail_y


def _refresh_driver_rail_plan(node, nets, options):
    """布线前按当前可见外框重算 rail 走廊（lbl_bbox，不受 place 膨胀影响）。"""
    topology = getattr(node, "_last_topology_result", None) or {}
    if topology.get("kind") != "generic_driver" or topology.get("fallback") is not False:
        return getattr(node, "_driver_rail_plan", None) or {"enabled": False}
    parts = [p for p in node.parts if getattr(p, "ref", None)]
    main = topology.get("main_part") or getattr(node, "_human_readable_main_part", None)
    if not parts or main is None:
        return {"enabled": False}
    plan = build_driver_rail_plan(node, parts, nets, topology, main, **options)
    node._driver_rail_plan = plan
    return plan


def _driver_route_pins(node, net):
    """driver 预布线用引脚：不受 auto_stub 的 pin.stub 影响。"""
    from skidl.schematics.place import is_net_terminal

    return [
        pin
        for pin in net.pins
        if pin.part in node.parts and not is_net_terminal(pin.part)
    ]


def _driver_chain_bus_y(pin_pts, grid):
    """
    主链行内水平母线的 Y。
    不用 (top_y + bottom_y) / 2：place 膨胀 bbox 会把 plan 的 bottom_y 拉得很远。
    用引脚 Y 中位数下移一格，避免离群 pin 或膨胀 bbox 把母线甩到页面底部。
    """
    if not pin_pts:
        return 0
    ys = sorted(pt.y for pt in pin_pts)
    row_y = ys[len(ys) // 2]
    return Point(0, row_y + grid).snap(grid).y


def route_driver_chain_local_nets(node, nets, **options):
    """
    主链行内网（含 Net-(D1-A)/Net-(D1-K)）：水平短母线 + 竖 stub，不走 switchbox 绕框。
    """
    plan = getattr(node, "_driver_rail_plan", None) or {}
    if not plan.get("enabled"):
        return set()
    row_parts = set(getattr(node, "_driver_chain_parts", set()) or [])
    if not row_parts:
        return set()

    grid = int(plan.get("grid", options.get("grid", 100)))
    rail_handled = set(getattr(node, "_driver_rail_routed_nets", set()) or [])
    handled = set()

    for net in nets:
        if net in rail_handled:
            continue
        pins = _driver_route_pins(node, net)
        if len(pins) < 2:
            continue
        if {pin.part for pin in pins} - row_parts:
            continue

        pin_pts = [(pin.pt * pin.part.tx).round() for pin in pins]
        bus_y = _driver_chain_bus_y(pin_pts, grid)
        x_min = min(pt.x for pt in pin_pts)
        x_max = max(pt.x for pt in pin_pts)
        segs = [Segment(Point(x_min, bus_y), Point(x_max, bus_y))]
        for pt in pin_pts:
            stub_end = Point(pt.x, bus_y)
            if pt != stub_end:
                segs.append(Segment(copy.copy(pt), stub_end))
        node.wires[net] = segs
        handled.add(net)

    if options.get("schematic_progress", False) and handled:
        from skidl.logger import active_logger

        active_logger.info(
            "[schematic] driver chain pre-route: %d nets %s"
            % (len(handled), [_net_name_for_log(n) for n in handled])
        )
    return handled


def route_driver_rails(node, nets, **options):
    """
    generic_driver rail 预布线：顶/底水平长线 + 引脚短竖 stub。
    不经过 switchbox；handled 网由后续 global/switchbox 跳过。
    """
    plan = _refresh_driver_rail_plan(node, nets, options)
    if not plan.get("enabled"):
        return set()
    if not options.get("driver_rail_routing", True):
        return set()
    if not options.get("human_readable", False):
        return set()

    grid = int(plan.get("grid", options.get("grid", 100)))
    handled = set()
    top_set = set(plan.get("top_nets", []))
    bottom_set = set(plan.get("bottom_nets", []))
    net_set = set(nets)

    def _net_side(net):
        if net in top_set:
            return "top", plan["top_y"]
        if net in bottom_set:
            return "bottom", plan["bottom_y"]
        return None, None

    for net in list(top_set) + list(bottom_set):
        if net not in net_set:
            continue
        side, rail_y = _net_side(net)
        if side is None:
            continue

        pins = _driver_route_pins(node, net)
        if not pins:
            continue

        pin_pts = [(pin.pt * pin.part.tx).round() for pin in pins]
        x_min = min(plan["x_min"], min(pt.x for pt in pin_pts))
        x_max = max(plan["x_max"], max(pt.x for pt in pin_pts))
        rail_y = _shift_driver_rail_y(node, rail_y, x_min, x_max, grid, side)

        segs = [Segment(Point(x_min, rail_y), Point(x_max, rail_y))]
        for pt in pin_pts:
            if pt.y == rail_y and pt.x >= x_min and pt.x <= x_max:
                continue
            stub_end = Point(pt.x, rail_y)
            if pt != stub_end:
                segs.append(Segment(copy.copy(pt), stub_end))

        node.wires[net] = segs
        handled.add(net)

    node._driver_rail_routed_nets = handled
    chain_handled = route_driver_chain_local_nets(node, nets, **options)
    handled |= chain_handled
    node._driver_prerouted_nets = handled
    if options.get("schematic_progress", False) and handled:
        from skidl.logger import active_logger

        names = [_net_name_for_log(n) for n in handled]
        active_logger.info(
            "[schematic] driver rail pre-route: %d nets %s"
            % (len(handled), names)
        )
    return handled


def _net_name_for_log(net):
    return str(getattr(net, "name", "") or "")


###################################################################
#
# OVERVIEW OF SCHEMATIC AUTOROUTER
#
# The input is a Node containing child nodes and parts, each with a
# bounding box and an assigned (x,y) position. The following operations
# are done for each child node, and then for the parts within this node.
#
# The edges of each part bbox are extended to form tracks that divide the
# routing area into a set of four-sided, non-overlapping switchboxes. Each
# side of a switchbox is a Face, and each Face is a member of two adjoining
# switchboxes (except those Faces on the boundary of the total
# routing area.) Each face is adjacent to the six other faces of
# the two switchboxes it is part of.
#
# Each face has a capacity that indicates the number of wires that can
# cross through it. The capacity is the length of the face divided by the
# routing grid. (Faces on a part boundary have zero capacity to prevent
# routing from entering a part.)
#
# Each face on a part bbox is assigned terminals associated with the I/O
# pins of that symbol.
#
# After creating the faces and terminals, the global routing phase creates
# wires that connect the part pins on the nets. Each wire passes from
# a face of a switchbox to one of the other three faces, either directly
# across the switchbox to the opposite face or changing direction to
# either of the right-angle faces. The global router is basically a maze
# router that uses the switchboxes as high-level grid squares.
#
# After global routing, each net has a sequence of switchbox faces
# through which it will transit. The exact coordinate that each net
# enters a face is then assigned to create a Terminal.
#
# At this point there are a set of switchboxes which have fixed terminals located
# along their four faces. A greedy switchbox router
# (https://doi.org/10.1016/0167-9260(85)90029-X)
# does the detailed routing within each switchbox.
#
# The detailed wiring within all the switchboxes is combined and output
# as the total wiring for the parts in the Node.
#
###################################################################


# Orientations and directions.
class Orientation(Enum):
    HORZ = 1
    VERT = 2


class Direction(Enum):
    LEFT = 3
    RIGHT = 4


# Put the orientation/direction enums in global space to make using them easier.
for orientation in Orientation:
    globals()[orientation.name] = orientation.value
for direction in Direction:
    globals()[direction.name] = direction.value


# Dictionary for storing colors to visually distinguish routed nets.
net_colors = defaultdict(
    lambda: (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
)


class NoSwitchBox(Exception):
    """Exception raised when a switchbox cannot be generated."""

    pass


class TerminalClashException(Exception):
    """Exception raised when trying to place two terminals at the same coord on a Face."""

    pass


class RoutingFailure(Exception):
    """Exception raised when a net connecting pins cannot be routed."""

    pass


class GlobalRoutingFailure(RoutingFailure):
    """Failure during global routing phase."""

    pass


class SwitchboxRoutingFailure(RoutingFailure):
    """Failure during switchbox routing phase."""

    pass


class Boundary:
    """Class for indicating a boundary.

    When a Boundary object is placed in the part attribute of a Face, it
    indicates the Face is on the outer boundary of the Node routing area
    and no routes can pass through it.
    """

    pass


# Boundary object for placing in the bounding Faces of the Node routing area.
boundary = Boundary()

# Absolute coords of all part pins. Used when trimming stub nets.
pin_pts = []


class Terminal:
    def __init__(self, net, face, coord):
        """Terminal on a Face from which a net is routed within a SwitchBox.

        Args:
            net (Net): Net upon which the Terminal resides.
            face (Face): SwitchBox Face upon which the Terminal resides.
            coord (int): Absolute position along the track the face is in.

        Notes:
            A terminal exists on a Face and is assigned to a net.
            The terminal's (x,y) position is determined by the terminal's
            absolute coordinate along the track parallel to the face,
            and by the Face's absolute coordinate in the orthogonal direction.
        """

        self.net = net
        self.face = face
        self.coord = coord

    @property
    def route_pt(self):
        """Return (x,y) Point for a Terminal on a Face."""
        track = self.face.track
        if track.orientation == HORZ:
            return Point(self.coord, track.coord)
        else:
            return Point(track.coord, self.coord)

    def get_next_terminal(self, next_face):
        """Get the terminal on the next face that lies on the same net as this terminal.

        This method assumes the terminal's face and the next face are faces of the
        same switchbox. Hence, they're either parallel and on opposite sides, or they're
        at right angles so they meet at a corner.

        Args:
            next_face (Face): Face to search for a terminal on the same net as this.

        Raises:
            RoutingFailure: If no terminal exists.

        Returns:
            Terminal: The terminal found on the next face.
        """

        from_face = self.face
        if next_face.track in (from_face.beg, from_face.end):
            # The next face bounds the interval of the terminals's face, so
            # they're at right angles. With right angle faces, we want to
            # select a terminal on the next face that's close to this corner
            # because that will minimize the length of wire needed to make
            # the connection.
            if next_face.beg == from_face.track:
                # next_face is oriented upward or rightward w.r.t. from_face.
                # Start searching for a terminal from the lowest index
                # because this is closest to the corner.
                search_terminals = next_face.terminals
            elif next_face.end == from_face.track:
                # next_face is oriented downward or leftward w.r.t. from_face.
                # Start searching for a terminal from the highest index
                # because this is closest to the corner.
                search_terminals = next_face.terminals[::-1]
            else:
                raise GlobalRoutingFailure
        else:
            # The next face must be the parallel face on the other side of the
            # switchbox. With parallel faces, we want to selected a terminal
            # having close to the same position as the given terminal.
            # So if the given terminal is at position i, then search for the
            # next terminal on the other face at positions i, i+1, i-1, i+2, i-2...
            coord = self.coord
            lower_terminals = [t for t in next_face.terminals if t.coord <= coord]
            lower_terminals.sort(key=lambda t: t.coord, reverse=True)
            upper_terminals = [t for t in next_face.terminals if t.coord > coord]
            upper_terminals.sort(key=lambda t: t.coord, reverse=False)
            search_terminals = list(
                chain(*zip_longest(lower_terminals, upper_terminals))
            )
            search_terminals = [t for t in search_terminals if t is not None]

        # Search to find a terminal on the same net.
        for terminal in search_terminals:
            if terminal.net is self.net:
                return terminal  # Return found terminal.

        # No terminal on the same net, so search to find an unassigned terminal.
        for terminal in search_terminals:
            if terminal.net is None:
                terminal.net = self.net  # Assign net to terminal.
                return terminal  # Return newly-assigned terminal.

        # Well, something went wrong. Should have found *something*!
        raise GlobalRoutingFailure

    def draw(self, scr, tx, **options):
        """Draw a Terminal for debugging purposes.

        Args:
            scr (PyGame screen): Screen object for PyGame drawing.
            tx (Tx): Transformation matrix from real to screen coords.
            options (dict, optional): Dictionary of options and values. Defaults to {}.
        """

        # Don't draw terminal if it isn't on a net. It's just a placeholder.
        if self.net or options.get("draw_all_terminals"):
            draw_endpoint(self.route_pt, scr, tx, color=(255, 0, 0))
            # draw_endpoint(self.route_pt, scr, tx, color=net_colors[self.net])


class Interval(object):
    def __init__(self, beg, end):
        """Define an interval with a beginning and an end.

        Args:
            beg (GlobalTrack): Beginning orthogonal track that bounds interval.
            end (GlobalTrack): Ending orthogonal track that bounds interval.

        Note: The beginning and ending Tracks are orthogonal to the Track containing the interval.
              Also, beg and end are sorted so beg <= end.
        """

        # Order beginning and end so beginning <= end.
        if beg > end:
            beg, end = end, beg
        self.beg = beg
        self.end = end

    def __bool__(self):
        """An Interval object always returns True."""
        return True

    @property
    def len(self):
        """Return the length of the interval."""
        return self.end - self.beg

    def __len__(self):
        """Return the length of the interval."""
        return self.len

    def intersects(self, other):
        """Return True if the intervals overlap (even if only at one point)."""
        return not ((self.beg > other.end) or (self.end < other.beg))

    def interval_intersection(self, other):
        """Return intersection of two intervals as an interval, otherwise None."""
        if self.intersects(other):
            beg = max(self.beg, other.beg)
            end = min(self.end, other.end)
            assert beg <= end
            if beg != end:
                return Interval(beg, end)
        return None

    def merge(self, other):
        """Return a merged interval if the given intervals intersect, otherwise return None."""
        if Interval.intersects(self, other):
            return Interval(min(self.beg, other.beg), max(self.end, other.end))
        return None


class NetInterval(Interval):
    def __init__(self, net, beg, end):
        """Define an Interval with an associated net (useful for wire traces in a switchbox).

        Args:
            net (Net): Net associated with interval.
            beg (GlobalTrack): Beginning orthogonal track that bounds interval.
            end (GlobalTrack): Ending track that bounds interval.
        """
        super().__init__(beg, end)
        self.net = net

    def obstructs(self, other):
        """Return True if the intervals intersect and have different nets."""
        return super().intersects(other) and (self.net is not other.net)

    def merge(self, other):
        """Return a merged interval if the given intervals intersect and are on the same net, otherwise return None."""
        if self.net is other.net:
            merged_intvl = super().merge(other)
            if merged_intvl:
                merged_intvl = NetInterval(self.net, merged_intvl.beg, merged_intvl.end)
            return merged_intvl
        return None


class Adjacency:
    def __init__(self, from_face, to_face):
        """Define an adjacency between two Faces.

        Args:
            from_face (Face): One Face.
            to_face (Face): The other Face.

        Note: The Adjacency object will be associated with the from_face object, so there's
            no need to store from_face in the Adjacency object.
        """

        self.face = to_face
        if from_face.track.orientation == to_face.track.orientation:
            # Parallel faces, either both vertical or horizontal.
            # Distance straight-across from one face to the other.
            dist_a = abs(from_face.track.coord - to_face.track.coord)
            # Average distance parallel to the faces.
            dist_b = (from_face.length + to_face.length) / 2
            # Compute the average distance from a terminal on one face to the other.
            self.dist = dist_a + dist_b / 2
        else:
            # Else, orthogonal faces.
            # Compute the average face-to-face distance.
            dist_a = from_face.length
            dist_b = to_face.length
            # Average distance of dogleg route from a terminal on one face to the other.
            self.dist = (dist_a + dist_b) / 2


class Face(Interval):
    """A side of a rectangle bounding a routing switchbox."""

    def __init__(self, part, track, beg, end):
        """One side of a routing switchbox.

        Args:
            part (set,Part,Boundary): Element(s) the Face is part of.
            track (GlobalTrack): Horz/vert track the Face is on.
            beg (GlobalTrack): Vert/horz track the Face begins at.
            end (GlobalTrack): Vert/horz track the Face ends at.

        Notes:
            The beg and end tracks have to be in the same direction
            (i.e., both vertical or both horizontal) and orthogonal
            to the track containing the face.
        """

        # Initialize the interval beginning and ending defining the Face.
        super().__init__(beg, end)

        # Store Part/Boundary the Face is part of, if any.
        self.part = set()
        if isinstance(part, set):
            self.part.update(part)
        elif part is not None:
            self.part.add(part)

        # Storage for any part pins that lie along this Face.
        self.pins = []

        # Storage for routing terminals along this face.
        self.terminals = []

        # Set of Faces adjacent to this one. (Starts empty.)
        self.adjacent = set()

        # Add this new face to the track it belongs to so it isn't lost.
        self.track = track
        track.add_face(self)

        # Storage for switchboxes this face is part of.
        self.switchboxes = set()

    def combine(self, other):
        """Combine information from other face into this one.

        Args:
            other (Face): Other Face.

        Returns:
            None.
        """

        self.pins.extend(other.pins)
        self.terminals.extend(other.terminals)
        self.part.update(other.part)
        self.adjacent.update(other.adjacent)
        self.switchboxes.update(other.switchboxes)

    @property
    def length(self):
        """Return the length of the face."""
        return self.end.coord - self.beg.coord

    @property
    def bbox(self):
        """Return the bounding box of the 1-D face segment."""
        bbox = BBox()

        if self.track.orientation == VERT:
            # Face runs vertically, so bbox width is zero.
            bbox.add(Point(self.track.coord, self.beg.coord))
            bbox.add(Point(self.track.coord, self.end.coord))
        else:
            # Face runs horizontally, so bbox height is zero.
            bbox.add(Point(self.beg.coord, self.track.coord))
            bbox.add(Point(self.end.coord, self.track.coord))

        return bbox

    def add_terminal(self, net, coord):
        """Create a Terminal on the Face.

        Args:
            net (Net): The net the terminal is on.
            coord (int): The absolute coordinate along the track containing the Face.

        Raises:
            TerminalClashException:
        """

        if self.part and not net:
            # Don't add pin terminals with no net to a Face on a part or boundary.
            return

        # Search for pre-existing terminal at the same coordinate.
        for terminal in self.terminals:
            if terminal.coord == coord:
                # There is a pre-existing terminal at this coord.
                if not net:
                    # The new terminal has no net (i.e., non-pin terminal),
                    # so just quit and don't bother to add it. The pre-existing
                    # terminal is retained.
                    return
                elif terminal.net and terminal.net is not net:
                    # The pre-existing and new terminals have differing nets, so
                    # raise an exception.
                    raise TerminalClashException
                # The pre-existing and new terminals have the same net.
                # Remove the pre-existing terminal. It will be replaced
                # with the new terminal below.
                self.terminals.remove(terminal)

        # Create a new Terminal and add it to the list of terminals for this face.
        self.terminals.append(Terminal(net, self, coord))

    def trim_repeated_terminals(self):
        """Remove all but one terminal of each individual net from the face.

        Notes:
            A non-part Face with multiple terminals on the same net will lead
            to multi-path routing.
        """

        # Find the intersection of every non-part face in the track with this one.
        intersections = []
        for face in self.track:
            if not face.part:
                intersection = self.interval_intersection(face)
                if intersection:
                    intersections.append(intersection)

        # Merge any overlapping intersections to create larger ones.
        for i in range(len(intersections)):
            for j in range(i + 1, len(intersections)):
                merge = intersections[i].merge(intersections[j])
                if merge:
                    intersections[j] = merge
                    intersections[i] = None
                    break

        # Remove None from the list of intersections.
        intersections = list(set(intersections) - {None})

        # The intersections are now as large as they can be and not associated
        # with any parts, so there are no terminals associated with part pins.
        # Look for terminals within an intersection on the same net and
        # remove all but one of them.
        for intersection in intersections:
            # Make a dict with nets and the terminals on each one.
            net_term_dict = defaultdict(list)
            for terminal in self.terminals:
                if intersection.beg.coord <= terminal.coord <= intersection.end.coord:
                    net_term_dict[terminal.net].append(terminal)
            if None in net_term_dict.keys():
                del net_term_dict[None]  # Get rid of terminals not assigned to nets.

            # For each multi-terminal net, remove all but one terminal.
            # This terminal must be removed from all faces on the track.
            for terminals in net_term_dict.values():
                for terminal in terminals[1:]:  # Keep only the 1st terminal.
                    self.track.remove_terminal(terminal)

    def create_nonpin_terminals(self):
        """Create unassigned terminals along a non-part Face with GRID spacing.

        These terminals will be used during global routing of nets from
        face-to-face and during switchbox routing.
        """

        # Add terminals along a Face. A terminal can be right at the start if the Face
        # starts on a grid point, but there cannot be a terminal at the end
        # if the Face ends on a grid point. Otherwise, there would be two terminals
        # at exactly the same point (one at the ending point of a Face and the
        # other at the beginning point of the next Face).
        # FIXME: This seems to cause wiring with a lot of doglegs.
        if self.end.coord - self.beg.coord <= GRID:
            # Allow a terminal right at the start of the Face if the Face is small.
            beg = (self.beg.coord + GRID - 1) // GRID * GRID
        else:
            # For larger faces with lengths greater than the GRID spacing,
            # don't allow terminals right at the start of the Face.
            beg = (self.beg.coord + GRID) // GRID * GRID
        end = self.end.coord

        # Create terminals along the Face.
        for coord in range(beg, end, GRID):
            self.add_terminal(None, coord)

    def set_capacity(self):
        """Set the wire routing capacity of a Face."""

        if self.part:
            # Part/boundary faces have zero capacity for wires to pass thru.
            self.capacity = 0
        else:
            # Wire routing capacity for other faces is the number of terminals they have.
            self.capacity = len(self.terminals)

    def has_nets(self):
        """Return True if any Terminal on the Face is attached to a net."""
        return any((terminal.net for terminal in self.terminals))

    def add_adjacencies(self):
        """Add adjacent faces of the switchbox having this face as the top face."""

        # Create a temporary switchbox.
        try:
            swbx = SwitchBox(self)
        except NoSwitchBox:
            # This face doesn't belong to a valid switchbox.
            return

        def add_adjacency(from_, to):
            # Faces on the boundary can never accept wires so they are never
            # adjacent to any other face.
            if boundary in from_.part or boundary in to.part:
                return

            # If a face is an edge of a part, then it can never be adjacent to
            # another face on the *same part* or else wires might get routed over
            # the part bounding box.
            if from_.part.intersection(to.part):
                return

            # OK, no parts in common between the two faces so they can be adjacent.
            from_.adjacent.add(Adjacency(from_, to))
            to.adjacent.add(Adjacency(to, from_))

        # Add adjacent faces.
        add_adjacency(swbx.top_face, swbx.bottom_face)
        add_adjacency(swbx.left_face, swbx.right_face)
        add_adjacency(swbx.left_face, swbx.top_face)
        add_adjacency(swbx.left_face, swbx.bottom_face)
        add_adjacency(swbx.right_face, swbx.top_face)
        add_adjacency(swbx.right_face, swbx.bottom_face)

        # Get rid of the temporary switchbox.
        del swbx

    def extend(self, orthogonal_tracks):
        """Extend a Face along its track until it is blocked by an orthogonal face.

        This is used to create Faces that form the irregular grid of switchboxes.

        Args:
            orthogonal_tracks (list): List of tracks at right-angle to this face.
        """

        # Only extend faces that compose part bounding boxes.
        if not self.part:
            return

        # Extend the face backward from its beginning and forward from its end.
        for start, dir in ((self.beg, -1), (self.end, 1)):
            # Get tracks to extend face towards.
            search_tracks = orthogonal_tracks[start.idx :: dir]

            # The face extension starts off non-blocked by any orthogonal faces.
            blocked = False

            # Search for a orthogonal face in a track that intersects this extension.
            for ortho_track in search_tracks:
                for ortho_face in ortho_track:
                    # Intersection only occurs if the extending face hits the open
                    # interval of the orthogonal face, not if it touches an endpoint.
                    if ortho_face.beg < self.track < ortho_face.end:
                        # OK, this face intersects the extension. It also means the
                        # extending face will block the face just found, so split
                        # each track at the intersection point.
                        ortho_track.add_split(self.track)
                        self.track.add_split(ortho_track)

                        # If the intersecting face is also a face of a part bbox,
                        # then the extension is blocked, so create the extended face
                        # and stop the extension.
                        if ortho_face.part:
                            # This creates a face and adds it to the track.
                            Face(None, self.track, start, ortho_track)
                            blocked = True

                        # Stop checking faces in this track after an intersection is found.
                        break

                # Stop checking any further tracks once the face extension is blocked.
                if blocked:
                    break

    def split(self, trk):
        """If a track intersects in the middle of a face, split the face into two faces."""

        if self.beg < trk < self.end:
            # Add a Face from beg to trk to self.track.
            Face(self.part, self.track, self.beg, trk)
            # Move the beginning of the original Face to trk.
            self.beg = trk

    def coincides_with(self, other_face):
        """Return True if both faces have the same beginning and ending point on the same track."""
        return (self.beg, self.end) == (other_face.beg, other_face.end)

    def has_overlap(self, other_face):
        """Return True if the two faces overlap."""
        return self.beg < other_face.end and self.end > other_face.beg

    def audit(self):
        """Raise exception if face is malformed."""
        assert len(self.switchboxes) <= 2

    @property
    def seg(self):
        """Return a Segment that coincides with the Face."""

        if self.track.orientation == VERT:
            p1 = Point(self.track.coord, self.beg.coord)
            p2 = Point(self.track.coord, self.end.coord)
        else:
            p1 = Point(self.beg.coord, self.track.coord)
            p2 = Point(self.end.coord, self.track.coord)

        return Segment(p1, p2)

    def draw(
        self, scr, tx, font, color=(128, 128, 128), thickness=2, dot_radius=0, **options
    ):
        """Draw a Face in the drawing area.

        Args:
            scr (PyGame screen): Screen object for PyGame drawing.
            tx (Tx): Transformation matrix from real to screen coords.
            font (PyGame font): Font for rendering text.
            options (dict, optional): Dictionary of options and values.

        Returns:
            None.
        """

        # Draw a line segment for the Face.
        draw_seg(
            self.seg, scr, tx, color=color, thickness=thickness, dot_radius=dot_radius
        )

        # Draw the terminals on the Face.
        for terminal in self.terminals:
            terminal.draw(scr, tx, **options)

        if options.get("show_capacities"):
            # Show the wiring capacity at the midpoint of the Face.
            mid_pt = (self.seg.p1 + self.seg.p2) / 2
            draw_text(str(self.capacity), mid_pt, scr, tx, font=font, color=color)


class GlobalWire(list):
    def __init__(self, net, *args, **kwargs):
        """A list connecting switchbox faces and terminals.

        Global routes start off as a sequence of switchbox faces that the route
        goes thru. Later, these faces are converted to terminals at fixed positions
        on their respective faces.

        Args:
            net (Net): The net associated with the wire.
            *args: Positional args passed to list superclass __init__().
            **kwargs: Keyword args passed to list superclass __init__().
        """
        self.net = net
        super().__init__(*args, **kwargs)

    def cvt_faces_to_terminals(self):
        """Convert global face-to-face route to switchbox terminal-to-terminal route."""

        if not self:
            # Global route is empty so do nothing.
            return

        # Non-empty global routes should always start from a face on a part.
        assert self[0].part

        # All part faces already have terminals created from the part pins. Find all
        # the route faces on part boundaries and convert them to pin terminals if
        # one or more pins are attached to the same net as the route.
        for i, face in enumerate(self[:]):
            if face.part:
                # This route face is on a part boundary, so find the terminal with the route's net.
                for terminal in face.terminals:
                    if self.net is terminal.net:
                        # Replace the route face with the terminal on the part.
                        self[i] = terminal
                        break
                else:
                    # Route should never touch a part face if there is no terminal with the route's net.
                    raise RuntimeError

        # Proceed through all the Faces/Terminals on the GlobalWire, converting
        # all the Faces to Terminals.
        for i in range(len(self) - 1):
            # The current element on a GlobalWire should always be a Terminal. Use that terminal
            # to convert the next Face on the wire to a Terminal (if it isn't one already).
            if isinstance(self[i], Face):
                # Logic error if the current element has not been converted to a Terminal.
                raise RuntimeError

            if isinstance(self[i + 1], Face):
                # Convert the next Face element into a Terminal on this net. This terminal will
                # be the current element on the next iteration.
                self[i + 1] = self[i].get_next_terminal(self[i + 1])

    def draw(self, scr, tx, color=(0, 0, 0), thickness=1, dot_radius=10, **options):
        """Draw a global wire from Face-to-Face in the drawing area.

        Args:
            scr (PyGame screen): Screen object for PyGame drawing.
            tx (Tx): Transformation matrix from real to screen coords.
            color (list): Three-element list of RGB integers with range [0, 255].
            thickness (int): Thickness of drawn wire in pixels.
            dot_radius (int): Radius of drawn terminal in pixels.
            options (dict, optional): Dictionary of options and values. Defaults to {}.

        Returns:
            None.
        """

        # Draw pins on the net associated with the wire.
        for pin in self.net.pins:
            # Only draw pins in the current node being routed which have the route_pt attribute.
            if hasattr(pin, "route_pt"):
                pt = pin.route_pt * pin.part.tx
                track = pin.face.track
                pt = {
                    HORZ: Point(pt.x, track.coord),
                    VERT: Point(track.coord, pt.y),
                }[track.orientation]
                draw_endpoint(pt, scr, tx, color=color, dot_radius=10)

        # Draw global wire segment.
        face_to_face = zip(self[:-1], self[1:])
        for terminal1, terminal2 in face_to_face:
            p1 = terminal1.route_pt
            p2 = terminal2.route_pt
            draw_seg(
                Segment(p1, p2), scr, tx, color=color, thickness=thickness, dot_radius=0
            )


class GlobalRoute(list):
    def __init__(self, *args, **kwargs):
        """A list containing GlobalWires that form an entire routing of a net.

        Args:
            net (Net): The net associated with the wire.
            *args: Positional args passed to list superclass __init__().
            **kwargs: Keyword args passed to list superclass __init__().
        """
        super().__init__(*args, **kwargs)

    def cvt_faces_to_terminals(self):
        """Convert GlobalWires in route to switchbox terminal-to-terminal route."""
        for wire in self:
            wire.cvt_faces_to_terminals()

    def draw(
        self, scr, tx, font, color=(0, 0, 0), thickness=1, dot_radius=10, **options
    ):
        """Draw the GlobalWires of this route in the drawing area.

        Args:
            scr (PyGame screen): Screen object for PyGame drawing.
            tx (Tx): Transformation matrix from real to screen coords.
            font (PyGame font): Font for rendering text.
            color (list): Three-element list of RGB integers with range [0, 255].
            thickness (int): Thickness of drawn wire in pixels.
            dot_radius (int): Radius of drawn terminal in pixels.
            options (dict, optional): Dictionary of options and values. Defaults to {}.

        Returns:
            None.
        """

        for wire in self:
            wire.draw(scr, tx, color, thickness, dot_radius, **options)


class GlobalTrack(list):
    def __init__(self, orientation=HORZ, coord=0, idx=None, *args, **kwargs):
        """A horizontal/vertical track holding zero or more faces all having the same Y/X coordinate.

        These global tracks are made by extending the edges of part bounding boxes to
        form a non-regular grid of rectangular switchboxes. These tracks are *NOT* the same
        as the tracks used within a switchbox for the detailed routing phase.

        Args:
            orientation (Orientation): Orientation of track (horizontal or vertical).
            coord (int): Coordinate of track on axis orthogonal to track direction.
            idx (int): Index of track into a list of X or Y coords.
            *args: Positional args passed to list superclass __init__().
            **kwargs: Keyword args passed to list superclass __init__().
        """

        self.orientation = orientation
        self.coord = coord
        self.idx = idx
        super().__init__(*args, **kwargs)

        # This stores the orthogonal tracks that intersect this one.
        self.splits = set()

    def __eq__(self, track):
        """Used for ordering tracks."""
        return self.coord == track.coord

    def __ne__(self, track):
        """Used for ordering tracks."""
        return self.coord != track.coord

    def __lt__(self, track):
        """Used for ordering tracks."""
        return self.coord < track.coord

    def __le__(self, track):
        """Used for ordering tracks."""
        return self.coord <= track.coord

    def __gt__(self, track):
        """Used for ordering tracks."""
        return self.coord > track.coord

    def __ge__(self, track):
        """Used for ordering tracks."""
        return self.coord >= track.coord

    def __sub__(self, other):
        """Subtract coords of two tracks."""
        return self.coord - other.coord

    def extend_faces(self, orthogonal_tracks):
        """Extend the faces in a track.

        This is part of forming the irregular grid of switchboxes.

        Args:
            orthogonal_tracks (list): List of tracks orthogonal to this one (L/R vs. H/V).
        """

        for face in self[:]:
            face.extend(orthogonal_tracks)

    def __hash__(self):
        """This method lets a track be inserted into a set of splits."""
        return self.idx

    def add_split(self, orthogonal_track):
        """Store the orthogonal track that intersects this one."""
        self.splits.add(orthogonal_track)

    def add_face(self, face):
        """Add a face to a track.

        Args:
            face (Face): Face to be added to track.
        """

        self.append(face)

        # The orthogonal tracks that bound the added face will split this track.
        self.add_split(face.beg)
        self.add_split(face.end)

    def split_faces(self):
        """Split track faces by any intersecting orthogonal tracks."""

        for split in self.splits:
            for face in self[:]:
                # Apply the split track to the face. The face will only be split
                # if the split track intersects it. Any split faces will be added
                # to the track this face is on.
                face.split(split)

    def remove_duplicate_faces(self):
        """Remove faces from the track having the same endpoints."""

        # Create lists of faces having the same endpoints.
        dup_faces_dict = defaultdict(list)
        for face in self:
            key = (face.beg, face.end)
            dup_faces_dict[key].append(face)

        # Remove all but the first face from each list.
        for dup_faces in dup_faces_dict.values():
            retained_face = dup_faces[0]
            for dup_face in dup_faces[1:]:
                # Add info from duplicate face to the retained face.
                retained_face.combine(dup_face)
                self.remove(dup_face)

    def remove_terminal(self, terminal):
        """Remove a terminal from any non-part Faces in the track."""

        coord = terminal.coord
        # Look for the terminal in all non-part faces on the track.
        for face in self:
            if not face.part:
                for term in face.terminals[:]:
                    if term.coord == coord:
                        face.terminals.remove(term)

    def add_adjacencies(self):
        """Add adjacent switchbox faces to each face in a track."""

        for top_face in self:
            top_face.add_adjacencies()

    def audit(self):
        """Raise exception if track is malformed."""

        for i, first_face in enumerate(self):
            first_face.audit()
            for second_face in self[i + 1 :]:
                if first_face.has_overlap(second_face):
                    raise AssertionError

    def draw(self, scr, tx, font, **options):
        """Draw the Faces in a track.

        Args:
            scr (_type_): _descriptio            scr (PyGame screen): Screen object for PyGame drawing.
            tx (Tx): Transformation matrix from real to screen coords.
            font (PyGame font): Font for rendering text.
            options (dict, optional): Dictionary of options and values. Defaults to {}.
        """
        for face in self:
            face.draw(scr, tx, font, **options)


class Target:
    def __init__(self, net, row, col):
        """A point on a switchbox face that switchbox router has not yet reached.

        Targets are used to direct the switchbox router towards terminals that
        need to be connected to nets. So wiring will be nudged up/down to
        get closer to terminals along the upper/lower faces. Wiring will also
        be nudged toward the track rows where terminals on the right face reside
        as the router works from the left to the right.

        Args:
            net (Net): Target net.
            row (int): Track row for the target, including top or bottom faces.
            col (int): Switchbox column for the target.
        """
        self.row = row
        self.col = col
        self.net = net

    def __lt__(self, other):
        """Used for ordering Targets in terms of priority."""

        # Targets in the left-most columns are given priority since they will be reached
        # first as the switchbox router proceeds from left-to-right.
        return (self.col, self.row, id(self.net)) < (
            other.col,
            other.row,
            id(other.net),
        )


class SwitchBox:
    # Indices for faces of the switchbox.
    TOP, LEFT, BOTTOM, RIGHT = 0, 1, 2, 3

    def __init__(self, top_face, left_face=None, bottom_face=None, right_face=None):
        """Routing switchbox.

        A switchbox is a rectangular region through which wires are routed.
        It has top, bottom, left and right faces.

        Args:
            top_face (Face): The top face of the switchbox (needed to find the other faces).
            bottom_face (Face): The bottom face. Will be calculated if set to None.
            left_face (Face): The left face. Will be calculated if set to None.
            right_face (Face): The right face. Will be calculated if set to None.

        Raises:
            NoSwitchBox: Exception raised if the switchbox is an
                unroutable region inside a part bounding box.
        """

        # Find the left face in the left track that bounds the top face.
        if left_face == None:
            left_track = top_face.beg
            for face in left_track:
                # The left face will end at the track for the top face.
                if face.end.coord == top_face.track.coord:
                    left_face = face
                    break
            else:
                raise NoSwitchBox("Unroutable switchbox (left)!")

        # Find the right face in the right track that bounds the top face.
        if right_face == None:
            right_track = top_face.end
            for face in right_track:
                # The right face will end at the track for the top face.
                if face.end.coord == top_face.track.coord:
                    right_face = face
                    break
            else:
                raise NoSwitchBox("Unroutable switchbox (right)!")

        # For a routable switchbox, the left and right faces should each
        # begin at the same point.
        if left_face.beg != right_face.beg:
            # Inequality only happens when two parts are butted up against each other
            # to form a non-routable switchbox inside a part bounding box.
            raise NoSwitchBox("Unroutable switchbox (left-right)!")

        # Find the bottom face in the track where the left/right faces begin.
        if bottom_face == None:
            bottom_track = left_face.beg
            for face in bottom_track:
                # The bottom face should begin/end in the same places as the top face.
                if (face.beg.coord, face.end.coord) == (
                    top_face.beg.coord,
                    top_face.end.coord,
                ):
                    bottom_face = face
                    break
            else:
                raise NoSwitchBox("Unroutable switchbox (bottom)!")

        # If all four sides have a part in common, then the switchbox is inside
        # a part bbox that wires cannot be routed through.
        if top_face.part & bottom_face.part & left_face.part & right_face.part:
            raise NoSwitchBox("Unroutable switchbox (part)!")

        # Store the faces.
        self.top_face = top_face
        self.bottom_face = bottom_face
        self.left_face = left_face
        self.right_face = right_face

        # Each face records which switchboxes it belongs to.
        self.top_face.switchboxes.add(self)
        self.bottom_face.switchboxes.add(self)
        self.left_face.switchboxes.add(self)
        self.right_face.switchboxes.add(self)

        def find_terminal_net(terminals, terminal_coords, coord):
            """Return the net attached to a terminal at the given coordinate.

            Args:
                terminals (list): List of Terminals to search.
                terminal_coords (list): List of integer coordinates for Terminals.
                coord (int): Terminal coordinate to search for.

            Returns:
                Net/None: Net at given coordinate or None if no net exists.
            """
            try:
                return terminals[terminal_coords.index(coord)].net
            except ValueError:
                return None

        # Find the coordinates of all the horizontal routing tracks
        left_coords = [terminal.coord for terminal in self.left_face.terminals]
        right_coords = [terminal.coord for terminal in self.right_face.terminals]
        tb_coords = [self.top_face.track.coord, self.bottom_face.track.coord]
        # Remove duplicate coords.
        self.track_coords = list(set(left_coords + right_coords + tb_coords))

        if len(self.track_coords) == 2:
            # This is a weird case. If the switchbox channel is too narrow to hold
            # a routing track in the middle, then place two pseudo-tracks along the
            # top and bottom faces to allow routing to proceed. The routed wires will
            # end up in the top or bottom faces, but maybe that's OK.
            # FIXME: Should this be extending with tb_coords?
            # FIXME: Should we always extend with tb_coords?
            self.track_coords.extend(self.track_coords)

        # Sort horiz. track coords from bottom to top.
        self.track_coords = sorted(self.track_coords)

        # Create a list of nets for each of the left/right faces.
        self.left_nets = [
            find_terminal_net(self.left_face.terminals, left_coords, coord)
            for coord in self.track_coords
        ]
        self.right_nets = [
            find_terminal_net(self.right_face.terminals, right_coords, coord)
            for coord in self.track_coords
        ]

        # Find the coordinates of all the vertical columns and then create
        # a list of nets for each of the top/bottom faces.
        top_coords = [terminal.coord for terminal in self.top_face.terminals]
        bottom_coords = [terminal.coord for terminal in self.bottom_face.terminals]
        lr_coords = [self.left_face.track.coord, self.right_face.track.coord]
        self.column_coords = sorted(set(top_coords + bottom_coords + lr_coords))
        self.top_nets = [
            find_terminal_net(self.top_face.terminals, top_coords, coord)
            for coord in self.column_coords
        ]
        self.bottom_nets = [
            find_terminal_net(self.bottom_face.terminals, bottom_coords, coord)
            for coord in self.column_coords
        ]

        # Remove any nets that only have a single terminal in the switchbox.
        all_nets = self.left_nets + self.right_nets + self.top_nets + self.bottom_nets
        net_counts = Counter(all_nets)
        single_terminal_nets = [net for net, count in net_counts.items() if count <= 1]
        if single_terminal_nets:
            for side_nets in (
                self.left_nets,
                self.right_nets,
                self.top_nets,
                self.bottom_nets,
            ):
                for i, net in enumerate(side_nets):
                    if net in single_terminal_nets:
                        side_nets[i] = None

        # Handle special case when a terminal is right on the corner of the switchbox.
        self.move_corner_nets()

        # Storage for detailed routing.
        self.segments = defaultdict(list)

    def audit(self):
        """Raise exception if switchbox is malformed."""

        for face in self.face_list:
            face.audit()
        assert self.top_face.track.orientation == HORZ
        assert self.bottom_face.track.orientation == HORZ
        assert self.left_face.track.orientation == VERT
        assert self.right_face.track.orientation == VERT
        assert len(self.top_nets) == len(self.bottom_nets)
        assert len(self.left_nets) == len(self.right_nets)

    @property
    def face_list(self):
        """Return list of switchbox faces in CCW order, starting from top face."""
        flst = [None] * 4
        flst[self.TOP] = self.top_face
        flst[self.LEFT] = self.left_face
        flst[self.BOTTOM] = self.bottom_face
        flst[self.RIGHT] = self.right_face
        return flst

    def move_corner_nets(self):
        """
        Move any nets at the edges of the left/right faces
        (i.e., the corners) to the edges of the top/bottom faces.
        This will allow these nets to be routed within the switchbox columns
        as the routing proceeds from left to right.
        """

        if self.left_nets[0]:
            # Move bottommost net on left face to leftmost net on bottom face.
            self.bottom_nets[0] = self.left_nets[0]
            self.left_nets[0] = None

        if self.left_nets[-1]:
            # Move topmost net on left face to leftmost net on top face.
            self.top_nets[0] = self.left_nets[-1]
            self.left_nets[-1] = None

        if self.right_nets[0]:
            # Move bottommost net on right face to rightmost net on bottom face.
            self.bottom_nets[-1] = self.right_nets[0]
            self.right_nets[0] = None

        if self.right_nets[-1]:
            # Move topmost net on right face to rightmost net on top face.
            self.top_nets[-1] = self.right_nets[-1]
            self.right_nets[-1] = None

    def flip_xy(self):
        """Flip X-Y of switchbox to route from top-to-bottom instead of left-to-right."""

        # Flip coords of tracks and columns.
        self.column_coords, self.track_coords = self.track_coords, self.column_coords

        # Flip top/right and bottom/left nets.
        self.top_nets, self.right_nets = self.right_nets, self.top_nets
        self.bottom_nets, self.left_nets = self.left_nets, self.bottom_nets

        # Flip top/right and bottom/left faces.
        self.top_face, self.right_face = self.right_face, self.top_face
        self.bottom_face, self.left_face = self.left_face, self.bottom_face

        # Move any corner nets from the new left/right faces to the new top/bottom faces.
        self.move_corner_nets()

        # Flip X/Y coords of any routed segments.
        for segments in self.segments.values():
            for seg in segments:
                seg.flip_xy()

    def coalesce(self, switchboxes):
        """Group switchboxes around a seed switchbox into a larger switchbox.

        Args:
            switchboxes (list): List of seed switchboxes that have not yet been coalesced into a larger switchbox.

        Returns:
            A coalesced switchbox or None if the seed was no longer available for coalescing.
        """

        # Abort if the switchbox is no longer a potential seed (it was already merged into a previous switchbox).
        if self not in switchboxes:
            return None

        # Remove the switchbox from the list of seeds.
        switchboxes.remove(self)

        # List the switchboxes along the top, left, bottom and right borders of the coalesced switchbox.
        box_lists = [[self], [self], [self], [self]]

        # Iteratively search to the top, left, bottom, and right for switchboxes to add.
        active_directions = {self.TOP, self.LEFT, self.BOTTOM, self.RIGHT}
        while active_directions:
            # Grow in the shortest dimension so the coalesced switchbox stays "squarish".
            bbox = BBox()
            for box_list in box_lists:
                bbox.add(box_list[0].bbox)
            if bbox.w == bbox.h:
                # Already square, so grow in any direction.
                growth_directions = {self.TOP, self.LEFT, self.BOTTOM, self.RIGHT}
            elif bbox.w < bbox.h:
                # Taller than wide, so grow left or right.
                growth_directions = {self.LEFT, self.RIGHT}
            else:
                # Wider than tall, so grow up or down.
                growth_directions = {self.TOP, self.BOTTOM}

            # Only keep growth directions that are still active.
            growth_directions = growth_directions & active_directions

            # If there is no active growth direction, then stop the growth iterations.
            if not growth_directions:
                break

            # Take a random choice of the active growth directions.
            direction = random.choice(list(growth_directions))

            # Check the switchboxes along the growth side to see if further expansion is possible.
            box_list = box_lists[direction]
            for box in box_list:
                # Get the face of the box from which growth will occur.
                box_face = box.face_list[direction]
                if box_face.part:
                    # This box butts up against a part, so expansion in this direction is blocked.
                    active_directions.remove(direction)
                    break
                # Get the box which will be added if expansion occurs.
                # Every face borders two switchboxes, so the adjacent box is the other one.
                # 人类可读布局等情况下邻接集偶发为空，pop 会 KeyError；保守放弃该方向的本次生长。
                adjacent = box_face.switchboxes - {box}
                if not adjacent:
                    active_directions.remove(direction)
                    break
                adj_box = min(adjacent, key=id)
                if adj_box not in switchboxes:
                    # This box cannot be added, so expansion in this direction is blocked.
                    active_directions.remove(direction)
                    break
            else:
                # All the switchboxes along the growth side are available for expansion,
                # so replace the current boxes in the growth side with these new ones.
                adjacent_pairs = []
                ok_expand = True
                for i, box in enumerate(box_list[:]):
                    # Get the adjacent box for the current box on the growth side.
                    box_face = box.face_list[direction]
                    adjacent = box_face.switchboxes - {box}
                    if not adjacent:
                        ok_expand = False
                        break
                    adjacent_pairs.append((i, min(adjacent, key=id)))
                if not ok_expand:
                    active_directions.remove(direction)
                    continue
                for i, adj_box in adjacent_pairs:
                    # Replace the current box with the new box from the expansion.
                    box_list[i] = adj_box
                    # Remove the newly added box from the list of available boxes for growth.
                    switchboxes.remove(adj_box)

                # Add the first box on the growth side to the end of the list of boxes on the
                # preceding direction: (top,left,bottom,right) if current direction is (left,bottom,right,top).
                box_lists[direction - 1].append(box_list[0])

                # Add the last box on the growth side to the start of the list of boxes on the
                # next direction: (bottom,right,top,left) if current direction is (left,bottom,right,top).
                box_lists[(direction + 1) % 4].insert(0, box_list[-1])

        # Create new faces that bound the coalesced group of switchboxes.
        total_faces = [None, None, None, None]
        directions = (self.TOP, self.LEFT, self.BOTTOM, self.RIGHT)
        for direction, box_list in zip(directions, box_lists):
            # Create a face that spans all the faces of the boxes along one side.
            face_list = [box.face_list[direction] for box in box_list]
            beg = min([face.beg for face in face_list])
            end = max([face.end for face in face_list])
            total_face = Face(None, face_list[0].track, beg, end)

            # Add terminals from the box faces along one side.
            total_face.create_nonpin_terminals()
            for face in face_list:
                for terminal in face.terminals:
                    if terminal.net:
                        total_face.add_terminal(terminal.net, terminal.coord)

            # Set the routing capacity of the new face.
            total_face.set_capacity()

            # Store the new face for this side.
            total_faces[direction] = total_face

        # Return the coalesced switchbox created from the new faces.
        return SwitchBox(*total_faces)

    def trim_repeated_terminals(self):
        """Trim terminals on each face."""
        for face in self.face_list:
            face.trim_repeated_terminals()

    @property
    def bbox(self):
        """Return bounding box for a switchbox."""
        return BBox().add(self.top_face.bbox).add(self.left_face.bbox)

    def has_nets(self):
        """Return True if switchbox has any terminals on any face with nets attached."""
        return (
            self.top_face.has_nets()
            or self.bottom_face.has_nets()
            or self.left_face.has_nets()
            or self.right_face.has_nets()
        )

    def route(self, **options):
        """Route wires between terminals on the switchbox faces.

        Args:
            options (dict, optional): Dictionary of options and values. Defaults to {}.

        Raises:
            RoutingFailure: Raised if routing could not be completed.

        Returns:
            List of Segments: List of wiring segments for switchbox routes.
        """

        if not self.has_nets():
            # Return what should be an empty dict.
            assert not self.segments.keys()
            return self.segments

        def collect_targets(top_nets, bottom_nets, right_nets):
            """Collect target nets along top, bottom, right faces of switchbox."""

            min_row = 1
            max_row = len(right_nets) - 2
            max_col = len(top_nets)
            targets = []

            # Collect target nets along top and bottom faces of the switchbox.
            for col, (t_net, b_net) in enumerate(zip(top_nets, bottom_nets)):
                if t_net is not None:
                    targets.append(Target(t_net, max_row, col))
                if b_net is not None:
                    targets.append(Target(b_net, min_row, col))

            # Collect target nets on the right face of the switchbox.
            for row, r_net in enumerate(right_nets):
                if r_net is not None:
                    targets.append(Target(r_net, row, max_col))

            # Sort the targets by increasing column order so targets closer to
            # the left-to-right routing have priority.
            targets.sort()

            return targets

        def connect_top_btm(track_nets):
            """Connect nets from top/bottom terminals in a column to nets in horizontal tracks of the switchbox."""

            def find_connection(net, tracks, direction):
                """
                Searches for the closest track with the same net followed by the
                closest empty track. The indices of these tracks are returned.
                If the net cannot be connected to any track, return [].
                If the net given to connect is None, then return a list of [None].

                Args:
                    net (Net): Net to be connected.
                    tracks (list): Nets on tracks
                    direction (int): Search direction for connection (-1: down, +1:up).

                Returns:
                    list: Indices of tracks where the net can connect.
                """

                if net:
                    if direction < 0:
                        # Searching down so reverse tracks.
                        tracks = tracks[::-1]

                    connections = []

                    try:
                        # Find closest track with the given net.
                        connections.append(tracks[1:-1].index(net) + 1)
                    except ValueError:
                        pass

                    try:
                        # Find closest empty track.
                        connections.append(tracks[1:-1].index(None) + 1)
                    except ValueError:
                        pass

                    if direction < 0:
                        # Reverse track indices if searching down.
                        l = len(tracks)
                        connections = [l - 1 - cnct for cnct in connections]
                else:
                    # No net so return no connections.
                    connections = [None]

                return connections

            # Stores net intervals connecting top/bottom nets to horizontal tracks.
            column_intvls = []

            # Top/bottom nets for this switchbox column. Horizontal track nets are
            # at indexes 1..-2.
            b_net = track_nets[0]
            t_net = track_nets[-1]

            if t_net and (t_net is b_net):
                # If top & bottom nets are the same, just create a single net interval
                # connecting them and that's it.
                column_intvls.append(NetInterval(t_net, 0, len(track_nets) - 1))
                return column_intvls

            # Find which tracks the top/bottom nets can connect to.
            t_cncts = find_connection(t_net, track_nets, -1)
            b_cncts = find_connection(b_net, track_nets, 1)

            # Create all possible pairs of top/bottom connections.
            tb_cncts = [(t, b) for t in t_cncts for b in b_cncts]

            if not tb_cncts:
                # No possible connections for top and/or bottom.
                if options.get("allow_routing_failure"):
                    return column_intvls  # Return empty column.
                else:
                    raise SwitchboxRoutingFailure

            # Test each possible pair of connections to find one that is free of interference.
            for t_cnct, b_cnct in tb_cncts:
                if t_cnct is None or b_cnct is None:
                    # No possible interference if at least one connection is None.
                    break
                if t_cnct > b_cnct:
                    # Top & bottom connections don't interfere.
                    break
                if t_cnct == b_cnct and t_net is b_net:
                    # Top & bottom connect to the same track but they're the same net so that's OK.
                    break
            else:
                if options.get("allow_routing_failure"):
                    return column_intvls
                else:
                    raise SwitchboxRoutingFailure

            if t_cnct is not None:
                # Connection from track to terminal on top of switchbox.
                column_intvls.append(NetInterval(t_net, t_cnct, len(track_nets) - 1))
            if b_cnct is not None:
                # Connection from terminal on bottom of switchbox to track.
                column_intvls.append(NetInterval(b_net, 0, b_cnct))

            # Return connection segments.
            return column_intvls

        def prune_targets(targets, current_col):
            """Remove targets in columns to the left of the current left-to-right routing column"""
            return [target for target in targets if target.col > current_col]

        def insert_column_nets(track_nets, column_intvls):
            """Return the active nets with the added nets of the column's vertical intervals."""

            nets = track_nets[:]
            for intvl in column_intvls:
                nets[intvl.beg] = intvl.net
                nets[intvl.end] = intvl.net
            return nets

        def net_search(net, start, track_nets):
            """Search for the closest points for the net before and after the start point."""

            # illegal offset past the end of the list of track nets.
            large_offset = 2 * len(track_nets)

            try:
                # Find closest occurrence of net going up.
                up = track_nets[start:].index(net)
            except ValueError:
                # Net not found, so use out-of-bounds index.
                up = large_offset

            try:
                # Find closest occurrence of net going down.
                down = track_nets[start::-1].index(net)
            except ValueError:
                # Net not found, so use out-of-bounds index.
                down = large_offset

            if up <= down:
                return up
            else:
                return -down

        def insert_target_nets(track_nets, targets, right_nets):
            """Return copy of active track nets with additional prioritized targets from the top, bottom, right faces."""

            # Allocate storage for potential target nets to be added to the list of active track nets.
            placed_target_nets = [None] * len(track_nets)

            # Get a list of nets on the right face that are being actively routed right now
            # so we can steer the routing as it proceeds rightward.
            active_right_nets = [
                net if net in track_nets else None for net in right_nets
            ]

            # Strip-off the top/bottom rows where terminals are and routing doesn't go.
            search_nets = track_nets[1:-1]

            for target in targets:
                target_net, target_row = target.net, target.row

                # Skip target nets that aren't currently active or have already been
                # placed (prevents multiple insertions of the same target net).
                # Also ignore targets on the far right face until the last step.
                if (
                    target_net not in track_nets  # TODO: Use search_nets???
                    or target_net in placed_target_nets
                    or target_net in active_right_nets
                ):
                    continue

                # Assign the target net to the closest row to the target row that is either
                # empty or has the same net.
                net_row_offset = net_search(target_net, target_row, search_nets)
                empty_row_offset = net_search(None, target_row, search_nets)
                if abs(net_row_offset) <= abs(empty_row_offset):
                    row_offset = net_row_offset
                else:
                    row_offset = empty_row_offset
                try:
                    placed_target_nets[target_row + row_offset + 1] = target_net
                    search_nets[target_row + row_offset] = target_net
                except IndexError:
                    # There was no place for this target net
                    pass

            return [
                active_net or target_net or right_net
                # active_net or right_net or target_net
                for (active_net, right_net, target_net) in zip(
                    track_nets, active_right_nets, placed_target_nets
                )
            ]

        def connect_splits(track_nets, column):
            """Vertically connect nets on multiple tracks."""

            # Make a copy so the original isn't disturbed.
            track_nets = track_nets[:]

            # Find nets that are running on multiple tracks.
            multi_nets = set(
                net for net in set(track_nets) if track_nets.count(net) > 1
            )
            multi_nets.discard(None)  # Ignore empty tracks.

            # Find possible intervals for multi-track nets.
            net_intervals = []
            for net in multi_nets:
                net_trk_idxs = [idx for idx, nt in enumerate(track_nets) if nt is net]
                for index, trk1 in enumerate(net_trk_idxs[:-1], 1):
                    for trk2 in net_trk_idxs[index:]:
                        net_intervals.append(NetInterval(net, trk1, trk2))

            # Sort interval lengths from smallest to largest.
            net_intervals.sort(key=lambda ni: len(ni))
            # Sort interval lengths from largest to smallest.
            # net_intervals.sort(key=lambda ni: -len(ni))

            # Connect tracks for each interval if it doesn't intersect an
            # already existing connection.
            for net_interval in net_intervals:
                for col_interval in column:
                    if net_interval.obstructs(col_interval):
                        break
                else:
                    # No conflicts found with existing connections.
                    column.append(net_interval)

            # Get the nets that have vertical wires in the column.
            column_nets = set(intvl.net for intvl in column)

            # Merge segments of each net in the column.
            for net in column_nets:
                # Extract intervals if the current net has more than one interval.
                intervals = [intvl for intvl in column if intvl.net is net]
                if len(intervals) < 2:
                    # Skip if there's only a single interval for this net.
                    continue

                # Remove the intervals so they can be replaced with joined intervals.
                for intvl in intervals:
                    column.remove(intvl)

                # Merge the extracted intervals as much as possible.

                # Sort intervals by their beginning coordinates.
                intervals.sort(key=lambda intvl: intvl.beg)

                # Try merging consecutive pairs of intervals.
                for i in range(len(intervals) - 1):
                    # Try to merge consecutive intervals.
                    merged_intvl = intervals[i].merge(intervals[i + 1])
                    if merged_intvl:
                        # Keep only the merged interval and place it so it's compared to the next one.
                        intervals[i : i + 2] = None, merged_intvl

                # Remove the None entries that are inserted when segments get merged.
                intervals = [intvl for intvl in intervals if intvl]

                # Place merged intervals back into column.
                column.extend(intervals)

            return column

        def extend_tracks(track_nets, column, targets):
            """Extend track nets into the next column."""

            # These are nets to the right of the current column.
            rightward_nets = set(target.net for target in targets)

            # Keep extending nets to next column if they do not intersect intervals in the
            # current column with the same net.
            flow_thru_nets = track_nets[:]
            for intvl in column:
                for trk_idx in range(intvl.beg, intvl.end + 1):
                    if flow_thru_nets[trk_idx] is intvl.net:
                        # Remove net from track since it intersects an interval with the
                        # same net. The net may be extended from the interval in the next phase,
                        # or it may terminate here.
                        flow_thru_nets[trk_idx] = None

            next_track_nets = flow_thru_nets[:]

            # Extend track net if net has multiple column intervals that need further interconnection
            # or if there are terminals in rightward columns that need connections to this net.
            first_track = 0
            last_track = len(track_nets) - 1
            column_nets = set([intvl.net for intvl in column])
            for net in column_nets:
                # Get all the vertical intervals for this net in the current column.
                net_intervals = [i for i in column if i.net is net]

                # No need to extend tracks for this net into next column if there aren't multiple
                # intervals or further terminals to connect.
                if net not in rightward_nets and len(net_intervals) < 2:
                    continue

                # Sort the net's intervals from bottom of the column to top.
                net_intervals.sort(key=lambda e: e.beg)

                # Find the nearest target to the right matching the current net.
                target_row = None
                for target in targets:
                    if target.net is net:
                        target_row = target.row
                        break

                for i, intvl in enumerate(net_intervals):
                    # Sanity check: should never get here if interval goes from top-to-bottom of
                    # column (hence, only one interval) and there is no further terminal for this
                    # net to the right.
                    assert not (
                        intvl.beg == first_track
                        and intvl.end == last_track
                        and not target_row
                    )

                    if intvl.beg == first_track and intvl.end < last_track:
                        # Interval starts on bottom of column, so extend net in the track where it ends.
                        assert i == 0
                        assert track_nets[intvl.end] in (net, None)
                        exit_row = intvl.end
                        next_track_nets[exit_row] = net
                        continue

                    if intvl.end == last_track and intvl.beg > first_track:
                        # Interval ends on top of column, so extend net in the track where it begins.
                        assert i == len(net_intervals) - 1
                        assert track_nets[intvl.beg] in (net, None)
                        exit_row = intvl.beg
                        next_track_nets[exit_row] = net
                        continue

                    if target_row is None:
                        # No target to the right, so we must be trying to connect multiple column intervals for this net.
                        if i == 0:
                            # First interval in column so extend from its top-most point.
                            exit_row = intvl.end
                            next_track_nets[exit_row] = net
                        elif i == len(net_intervals) - 1:
                            # Last interval in column so extend from its bottom-most point.
                            exit_row = intvl.beg
                            next_track_nets[exit_row] = net
                        else:
                            # This interval is between the top and bottom intervals.
                            beg_end = (
                                bool(flow_thru_nets[intvl.beg]),
                                bool(flow_thru_nets[intvl.end]),
                            )
                            if beg_end == (True, False):
                                # The net enters this interval at its bottom, so extend from the top (dogleg).
                                exit_row = intvl.end
                                next_track_nets[exit_row] = net
                            elif beg_end == (False, True):
                                # The net enters this interval at its top, so extend from the bottom (dogleg).
                                exit_row = intvl.beg
                                next_track_nets[exit_row] = net
                            else:
                                raise RuntimeError
                        continue

                    else:
                        # Target to the right, so aim for it.

                        if target_row > intvl.end:
                            # target track is above the interval's end, so bound it to the end.
                            target_row = intvl.end
                        elif target_row < intvl.beg:
                            # target track is below the interval's start, so bound it to the start.
                            target_row = intvl.beg

                        # Search for the closest track to the target row that is either open
                        # or occupied by the same target net.
                        intvl_nets = track_nets[intvl.beg : intvl.end + 1]
                        net_row = (
                            net_search(net, target_row - intvl.beg, intvl_nets)
                            + target_row
                        )
                        open_row = (
                            net_search(None, target_row - intvl.beg, intvl_nets)
                            + target_row
                        )
                        net_dist = abs(net_row - target_row)
                        open_dist = abs(open_row - target_row)
                        if net_dist <= open_dist:
                            exit_row = net_row
                        else:
                            exit_row = open_row
                        assert intvl.beg <= exit_row <= intvl.end
                        next_track_nets[exit_row] = net
                        continue

            return next_track_nets

        def trim_column_intervals(column, track_nets, next_track_nets):
            """Trim stubs from column intervals."""

            # All nets entering and exiting the column.
            trk_nets = list(enumerate(zip(track_nets, next_track_nets)))

            for intvl in column:
                # Get all the entry/exit track positions having the same net as the interval
                # and that are within the bounds of the interval.
                net = intvl.net
                beg = intvl.beg
                end = intvl.end
                trks = [i for (i, nets) in trk_nets if net in nets and beg <= i <= end]

                # Chop off any stubs of the interval that extend past where it could
                # connect to an entry/exit point of its net.
                intvl.beg = min(trks)
                intvl.end = max(trks)

        ########################################
        # Main switchbox routing loop.
        ########################################

        # Get target nets as routing proceeds from left-to-right.
        targets = collect_targets(self.top_nets, self.bottom_nets, self.right_nets)

        # Store the nets in each column that are in the process of being routed,
        # starting with the nets in the left-hand face of the switchbox.
        nets_in_column = [self.left_nets[:]]

        # Store routing intervals in each column.
        all_column_intvls = []

        # Route left-to-right across the columns connecting the top & bottom nets
        # on each column to tracks within the switchbox.
        for col, (t_net, b_net) in enumerate(zip(self.top_nets, self.bottom_nets)):
            # Nets in the previous column become the currently active nets being routed
            active_nets = nets_in_column[-1][:]

            if col == 0 and not t_net and not b_net:
                # Nothing happens in the first column if there are no top & bottom nets.
                # Just continue the active nets from the left-hand face to the next column.
                column_intvls = []
                next_active_nets = active_nets[:]

            else:
                # Bring any nets on the top & bottom of this column into the list of active nets.
                active_nets[0] = b_net
                active_nets[-1] = t_net

                # Generate the intervals that will vertically connect the top & bottom nets to
                # horizontal tracks in the switchbox.
                column_intvls = connect_top_btm(active_nets)

                # Add the nets from the new vertical connections to the active nets.
                augmented_active_nets = insert_column_nets(active_nets, column_intvls)

                # Remove the nets processed in this column from the list of target nets.
                targets = prune_targets(targets, col)

                # Insert target nets from rightward columns into this column to direct
                # the placement of additional vertical intervals towards them.
                augmented_active_nets = insert_target_nets(
                    augmented_active_nets, targets, self.right_nets
                )

                # Make vertical connections between tracks in the column having the same net.
                column_intvls = connect_splits(augmented_active_nets, column_intvls)

                # Get the nets that will be active in the next column.
                next_active_nets = extend_tracks(active_nets, column_intvls, targets)

                # Trim any hanging stubs from vertical routing intervals in the current column.
                trim_column_intervals(column_intvls, active_nets, next_active_nets)

            # Store the active nets for the next column.
            nets_in_column.append(next_active_nets)

            # Store the vertical routing intervals for this column.
            all_column_intvls.append(column_intvls)

        ########################################
        # End of switchbox routing loop.
        ########################################

        # After routing from left-to-right, verify the active track nets coincide
        # with the positions of the nets on the right-hand face of the switchbox.
        for track_net, right_net in zip(nets_in_column[-1], self.right_nets):
            if track_net is not right_net:
                if not options.get("allow_routing_failure"):
                    raise SwitchboxRoutingFailure

        # Create wiring segments along each horizontal track.
        # Add left and right faces to coordinates of the vertical columns.
        column_coords = (
            [self.left_face.track.coord]
            + self.column_coords
            + [self.right_face.track.coord]
        )
        # Proceed column-by-column from left-to-right creating horizontal wires.
        for col_idx, nets in enumerate(nets_in_column):
            beg_col_coord = column_coords[col_idx]
            end_col_coord = column_coords[col_idx + 1]
            # Create segments for each track (skipping bottom & top faces).
            for trk_idx, net in enumerate(nets[1:-1], start=1):
                if net:
                    # Create a wire segment for the net in this horizontal track of the column.
                    trk_coord = self.track_coords[trk_idx]
                    p1 = Point(beg_col_coord, trk_coord)
                    p2 = Point(end_col_coord, trk_coord)
                    seg = Segment(p1, p2)
                    self.segments[net].append(seg)

        # Create vertical wiring segments for each switchbox column.
        for idx, column in enumerate(all_column_intvls):
            # Get X coord of this column.
            col_coord = self.column_coords[idx]
            # Create vertical wire segments for wire interval in the column.
            for intvl in column:
                p1 = Point(col_coord, self.track_coords[intvl.beg])
                p2 = Point(col_coord, self.track_coords[intvl.end])
                self.segments[intvl.net].append(Segment(p1, p2))

        return self.segments

    def draw(
        self, scr=None, tx=None, font=None, color=(128, 0, 128), thickness=2, **options
    ):
        """Draw a switchbox and its routing for debugging purposes.

        Args:
            scr (PyGame screen): Screen object for PyGame drawing. Initialize PyGame if None.
            tx (Tx): Transformation matrix from real to screen coords.
            font (PyGame font): Font for rendering text.
            color (tuple, optional): Switchbox boundary color. Defaults to (128, 0, 128).
            thickness (int, optional): Switchbox boundary thickness. Defaults to 2.
            options (dict, optional): Dictionary of options and values. Defaults to {}.
        """

        # If the screen object is not None, then PyGame drawing is enabled so set flag
        # to initialize PyGame.
        do_start_end = not bool(scr)

        if do_start_end:
            # Initialize PyGame.
            scr, tx, font = draw_start(
                self.bbox.resize(Vector(DRAWING_BOX_RESIZE, DRAWING_BOX_RESIZE))
            )

        if options.get("draw_switchbox_boundary"):
            # Draw switchbox boundary.
            self.top_face.draw(scr, tx, font, color, thickness, **options)
            self.bottom_face.draw(scr, tx, font, color, thickness, **options)
            self.left_face.draw(scr, tx, font, color, thickness, **options)
            self.right_face.draw(scr, tx, font, color, thickness, **options)

        if options.get("draw_switchbox_routing"):
            # Draw routed wire segments.
            try:
                for segments in self.segments.values():
                    for segment in segments:
                        draw_seg(segment, scr, tx, dot_radius=0)
            except AttributeError:
                pass

        if options.get("draw_routing_channels"):
            # Draw routing channels from midpoint of one switchbox face to midpoint of another.

            def draw_channel(face1, face2):
                seg1 = face1.seg
                seg2 = face2.seg
                p1 = (seg1.p1 + seg1.p2) / 2
                p2 = (seg2.p1 + seg2.p2) / 2
                draw_seg(Segment(p1, p2), scr, tx, (128, 0, 128), 1, dot_radius=0)

            draw_channel(self.top_face, self.bottom_face)
            draw_channel(self.top_face, self.left_face)
            draw_channel(self.top_face, self.right_face)
            draw_channel(self.bottom_face, self.left_face)
            draw_channel(self.bottom_face, self.right_face)
            draw_channel(self.left_face, self.right_face)

        if do_start_end:
            # Terminate PyGame.
            draw_end()


@export_to_all
class Router:
    """Mixin to add routing function to Node class."""

    def add_routing_points(node, nets):
        """Add routing points by extending wires from pins out to the edge of the part bounding box.

        Args:
            nets (list): List of nets to be routed.
        """

        def add_routing_pt(pin):
            """Add the point for a pin on the boundary of a part."""

            bbox = pin.part.lbl_bbox
            pin.route_pt = copy.copy(pin.pt)
            if pin.orientation == "U":
                # Pin points up, so extend downward to the bottom of the bounding box.
                pin.route_pt.y = bbox.min.y
            elif pin.orientation == "D":
                # Pin points down, so extend upward to the top of the bounding box.
                pin.route_pt.y = bbox.max.y
            elif pin.orientation == "L":
                # Pin points left, so extend rightward to the right-edge of the bounding box.
                pin.route_pt.x = bbox.max.x
            elif pin.orientation == "R":
                # Pin points right, so extend leftward to the left-edge of the bounding box.
                pin.route_pt.x = bbox.min.x
            else:
                raise RuntimeError("Unknown pin orientation.")

        for net in nets:
            # Add routing points for all pins on the net that are inside this node.
            for pin in node.get_internal_pins(net):
                # Store the point where the pin is. (This is used after routing to trim wire stubs.)
                pin_pt = (pin.pt * pin.part.tx).round()
                if pin_pt not in pin_pts:
                    pin_pts.append(pin_pt)

                # Add the point to which the wiring should be extended.
                add_routing_pt(pin)

                # Add a wire to connect the part pin to the routing point on the bounding box periphery.
                if pin.route_pt != pin.pt:
                    seg = Segment(pin.pt, pin.route_pt) * pin.part.tx
                    node.wires[pin.net].append(seg)

    def _segment_obstructed(node, segment, net=None, ignored_parts=None):
        """Return True if a segment intersects another part or overlaps another net."""

        ignored_parts = ignored_parts or set()
        route_opts = getattr(node, "_route_options", {}) or {}
        part_obstacles = _build_route_part_obstacles(
            node, route_opts.get("human_readable", False)
        )

        segment_bbox = BBox(segment.p1, segment.p2)
        for part, part_bbox in part_obstacles:
            if part in ignored_parts:
                continue
            if part_bbox.intersects(segment_bbox):
                return True

        segment_bbox = segment_bbox.resize(Vector(2, 2))
        for other_net, other_segments in node.wires.items():
            if other_net is net:
                continue
            for other_seg in other_segments:
                if segment.p1.x == segment.p2.x == other_seg.p1.x == other_seg.p2.x:
                    if segment.p1.y <= other_seg.p2.y and segment.p2.y >= other_seg.p1.y:
                        return True
                elif segment.p1.y == segment.p2.y == other_seg.p1.y == other_seg.p2.y:
                    if segment.p1.x <= other_seg.p2.x and segment.p2.x >= other_seg.p1.x:
                        return True

        return False

    def route_straight_nets(node, nets):
        """Route aligned 2-pin nets directly before invoking the general router."""

        direct_routed = []

        for net in nets:
            pins = list(node.get_internal_pins(net))
            if len(pins) != 2:
                continue

            p1 = (pins[0].pt * pins[0].part.tx).round()
            p2 = (pins[1].pt * pins[1].part.tx).round()
            if p1 == p2 or (p1.x != p2.x and p1.y != p2.y):
                continue

            seg = Segment(copy.copy(p1), copy.copy(p2))
            if seg.p2 < seg.p1:
                seg.p1, seg.p2 = seg.p2, seg.p1

            if node._segment_obstructed(
                seg, net=net, ignored_parts={pins[0].part, pins[1].part}
            ):
                continue

            node.wires[net].append(seg)
            for pt in (p1, p2):
                if pt not in pin_pts:
                    pin_pts.append(pt)
            direct_routed.append(net)

        return direct_routed

    def create_routing_tracks(node, routing_bbox):
        """Create horizontal & vertical global routing tracks."""

        # Find the coords of the horiz/vert tracks that will hold the H/V faces of the routing switchboxes.
        v_track_coord = []
        h_track_coord = []

        # The top/bottom/left/right of each part's labeled bounding box define the H/V tracks.
        for part in node.parts:
            bbox = (part.lbl_bbox * part.tx).round()
            v_track_coord.append(bbox.min.x)
            v_track_coord.append(bbox.max.x)
            h_track_coord.append(bbox.min.y)
            h_track_coord.append(bbox.max.y)

        # Create delimiting tracks around the routing area. Just take the number of nets to be routed
        # and create a channel that size around the periphery. That's guaranteed to be big enough.
        # This is overkill but probably not worth optimizing since any excess boundary area is ignored.
        v_track_coord.append(routing_bbox.min.x)
        v_track_coord.append(routing_bbox.max.x)
        h_track_coord.append(routing_bbox.min.y)
        h_track_coord.append(routing_bbox.max.y)

        # Remove any duplicate track coords and then sort them.
        v_track_coord = list(set(v_track_coord))
        h_track_coord = list(set(h_track_coord))
        v_track_coord.sort()
        h_track_coord.sort()

        # Create an H/V track for each H/V coord containing a list for holding the faces in that track.
        v_tracks = [
            GlobalTrack(orientation=VERT, idx=idx, coord=coord)
            for idx, coord in enumerate(v_track_coord)
        ]
        h_tracks = [
            GlobalTrack(orientation=HORZ, idx=idx, coord=coord)
            for idx, coord in enumerate(h_track_coord)
        ]

        def bbox_to_faces(part, bbox):
            left_track = v_tracks[v_track_coord.index(bbox.min.x)]
            right_track = v_tracks[v_track_coord.index(bbox.max.x)]
            bottom_track = h_tracks[h_track_coord.index(bbox.min.y)]
            top_track = h_tracks[h_track_coord.index(bbox.max.y)]
            Face(part, left_track, bottom_track, top_track)
            Face(part, right_track, bottom_track, top_track)
            Face(part, bottom_track, left_track, right_track)
            Face(part, top_track, left_track, right_track)
            if isinstance(part, Part):
                part.left_track = left_track
                part.right_track = right_track
                part.top_track = top_track
                part.bottom_track = bottom_track

        # Add routing box faces for each side of a part's labeled bounding box.
        for part in node.parts:
            part_bbox = (part.lbl_bbox * part.tx).round()
            bbox_to_faces(part, part_bbox)

        # Add routing box faces for each side of the expanded bounding box surrounding all parts.
        bbox_to_faces(boundary, routing_bbox)

        # Extend the part faces in each horizontal track and then each vertical track.
        for track in h_tracks:
            track.extend_faces(v_tracks)
        for track in v_tracks:
            track.extend_faces(h_tracks)

        # Apply splits to all faces and combine coincident faces.
        for track in h_tracks + v_tracks:
            track.split_faces()
            track.remove_duplicate_faces()

        # Add adjacencies between faces that define global routing paths within switchboxes.
        for h_track in h_tracks[1:]:
            h_track.add_adjacencies()

        return h_tracks, v_tracks

    def create_terminals(node, internal_nets, h_tracks, v_tracks):
        """Create terminals on the faces in the routing tracks."""

        # Add terminals to all non-part/non-boundary faces.
        for track in h_tracks + v_tracks:
            for face in track:
                face.create_nonpin_terminals()

        # Add terminals to switchbox faces for all part pins on internal nets.
        for net in internal_nets:
            for pin in node.get_internal_pins(net):
                # Find the track (top/bottom/left/right) that the pin is on.
                part = pin.part
                pt = pin.route_pt * part.tx
                closest_dist = abs(pt.y - part.top_track.coord)
                pin_track = part.top_track
                coord = pt.x  # Pin coord within top track.
                dist = abs(pt.y - part.bottom_track.coord)
                if dist < closest_dist:
                    closest_dist = dist
                    pin_track = part.bottom_track
                    coord = pt.x  # Pin coord within bottom track.
                dist = abs(pt.x - part.left_track.coord)
                if dist < closest_dist:
                    closest_dist = dist
                    pin_track = part.left_track
                    coord = pt.y  # Pin coord within left track.
                dist = abs(pt.x - part.right_track.coord)
                if dist < closest_dist:
                    closest_dist = dist
                    pin_track = part.right_track
                    coord = pt.y  # Pin coord within right track.

                # Now search for the face in the track that the pin is on.
                for face in pin_track:
                    if part in face.part and face.beg.coord <= coord <= face.end.coord:
                        if not getattr(pin, "face", None):
                            # Only assign pin to face if it hasn't already been assigned to
                            # another face. This handles the case where a pin is exactly
                            # at the end coordinate and beginning coordinate of two
                            # successive faces in the same track.
                            pin.face = face
                            face.pins.append(pin)
                            terminal = Terminal(pin.net, face, coord)
                            face.terminals.append(terminal)
                        break

        # Set routing capacity of faces based on # of terminals on each face.
        for track in h_tracks + v_tracks:
            for face in track:
                face.set_capacity()

    def global_router(node, nets):
        human_readable = False
        prefer_straight = False
        bend_penalty = 0.0
        length_weight = 1.0
        try:
            human_readable = node._route_options.get("human_readable", False)
            prefer_straight = node._route_options.get("prefer_straight", False)
            bend_penalty = float(node._route_options.get("bend_penalty", 0.0))
            length_weight = float(
                node._route_options.get(
                    "route_length_weight", 0.6 if prefer_straight else 1.0
                )
            )
        except AttributeError:
            pass

        def stable_face_key(face):
            """Create a deterministic key for selecting a face."""
            return (
                getattr(face.track, "orientation", 0),
                getattr(face.track, "coord", 0),
                getattr(face.beg, "coord", 0),
                getattr(face.end, "coord", 0),
                len(getattr(face, "pins", [])),
                len(getattr(face, "terminals", [])),
            )

        def face_route_axis(face):
            """Return the primary routing axis when traversing through a face."""
            if face.track.orientation == VERT:
                return HORZ
            return VERT

        """Globally route a list of nets from face to face.

        Args:
            nets (list): List of Nets to be routed.

        Returns:
            List: List of GlobalRoutes.
        """

        # This maze router assembles routes from each pin sequentially.
        #
        # 1. Find faces with net pins on them and place them on the
        #    start_faces list.
        # 2. Randomly select one of the start faces. Add all the other
        #    faces to the stop_faces list.
        # 3. Find a route from the start face to closest stop face.
        #    This concludes the initial phase of the routing.
        # 4. Iterate through the remaining faces on the start_faces list.
        #        a. Randomly select a start face.
        #        b. Set stop faces to be all the faces currently on
        #           global routes.
        #        c. Find a route from the start face to any face on
        #           the global routes, thus enlarging the set of
        #           contiguous routes while reducing the number of
        #           unrouted start faces.
        #        d. Add the faces on the new route to the stop_faces list.

        # Core routing function.
        def rt_srch(start_face, stop_faces):
            """Return a minimal-distance path from the start face to one of the stop faces.

            Args:
                start_face (Face): Face from which path search begins
                stop_faces (List): List of Faces at which search will end.

            Raises:
                RoutingFailure: No path was found.

            Returns:
                GlobalWire: List of Faces from start face to one of the stop faces.
            """

            # Return empty path if no stop faces or already starting from a stop face.
            if start_face in stop_faces or not stop_faces:
                return GlobalWire(net)

            # Path searches are allowed to touch a Face on a Part if it
            # has a Pin on the net being routed or if it is one of the stop faces.
            # This is necessary to allow a search to terminate on a stop face or to
            # pass through a face with a net pin on the way to finding a connection
            # to one of the stop faces.
            unconstrained_faces = stop_faces | net_pin_faces
            start_state = (start_face, face_route_axis(start_face))
            best_metric = {start_state: (0.0, 0)}
            prev_state = {}
            frontier = [(0.0, 0, 0, start_state)]
            search_order = 1

            # 方向被纳入搜索状态后，可以在总代价里显式加入 bend penalty，
            # 从而让“略长但更直”的路径击败“更短但反复转向”的路径。
            while frontier:
                metric_cost, metric_bends, _, state = heapq.heappop(frontier)
                if (metric_cost, metric_bends) != best_metric.get(state):
                    continue

                visited_face, route_axis = state

                if visited_face in stop_faces:
                    face_path = [visited_face]
                    while state != start_state:
                        state = prev_state[state]
                        face_path.append(state[0])

                    for face in face_path[:-1]:
                        if face.capacity > 0:
                            face.capacity -= 1

                    return GlobalWire(net, reversed(face_path))

                for adj in sorted(visited_face.adjacent, key=lambda a: stable_face_key(a.face)):
                    if (
                        adj.face not in unconstrained_faces
                        and adj.face.capacity <= 0
                    ):
                        continue

                    next_axis = face_route_axis(adj.face)
                    bend_count = 1 if next_axis != route_axis else 0
                    next_state = (adj.face, next_axis)
                    next_metric = (
                        metric_cost + adj.dist * length_weight + bend_count * bend_penalty,
                        metric_bends + bend_count,
                    )

                    if next_metric < best_metric.get(next_state, (float("inf"), float("inf"))):
                        best_metric[next_state] = next_metric
                        prev_state[next_state] = state
                        heapq.heappush(
                            frontier,
                            (next_metric[0], next_metric[1], search_order, next_state),
                        )
                        search_order += 1

            raise GlobalRoutingFailure(
                f"Global routing failure: {net.name} {net} {start_face.pins}"
            )

        # Key function for setting the order in which nets will be globally routed.
        def rank_net(net):
            """Rank net based on W/H of bounding box of pins and the # of pins."""

            # Nets with a small bounding box probably have fewer routing resources
            # so they should be routed first.

            bbox = BBox()
            for pin in node.get_internal_pins(net):
                bbox.add(pin.route_pt)
            name = str(getattr(net, "name", "") or "")
            if human_readable:
                topo = getattr(node, "_last_topology_result", None)
                if topo and topo.get("kind") == "generic_driver" and topo.get("matched"):
                    route_bias = topology_route_rank_bias(net, topo)
                else:
                    route_bias = trunk_route_rank_bias(name)
            else:
                route_bias = 0
            return (route_bias + bbox.w + bbox.h, len(net.pins))

        # Set order in which nets will be routed.
        nets.sort(key=rank_net)

        # Globally route each net.
        global_routes = []

        for net in nets:
            # List for storing GlobalWires connecting pins on net.
            global_route = GlobalRoute()

            # Faces with pins from which paths/routing originate.
            net_pin_faces = {pin.face for pin in node.get_internal_pins(net)}
            start_faces = set(net_pin_faces)

            # 人类可读模式优先稳定起点，减少重复运行时路径抖动。
            if human_readable:
                start_face = sorted(start_faces, key=stable_face_key)[0]
            else:
                # Select a random start face and look for a route to *any* of the other start faces.
                start_face = random.choice(list(start_faces))
            start_faces.discard(start_face)
            stop_faces = set(start_faces)
            initial_route = rt_srch(start_face, stop_faces)
            global_route.append(initial_route)

            # The faces on the route that was found now become the stopping faces for any further routing.
            stop_faces = set(initial_route)

            # Go thru the other start faces looking for a connection to any existing route.
            for start_face in start_faces:
                next_route = rt_srch(start_face, stop_faces)
                global_route.append(next_route)

                # Update the set of stopping faces with the faces on the newest route.
                stop_faces |= set(next_route)

            # Add the complete global route for this net to the list of global routes.
            global_routes.append(global_route)

        return global_routes

    def create_switchboxes(node, h_tracks, v_tracks, **options):
        """Create routing switchboxes from the faces in the horz/vert tracks.

        Args:
            h_tracks (list): List of horizontal Tracks.
            v_tracks (list): List of vertical Tracks.
            options (dict, optional): Dictionary of options and values.

        Returns:
            list: List of Switchboxes.
        """

        # Clear any switchboxes associated with faces because we'll be making new ones.
        for track in h_tracks + v_tracks:
            for face in track:
                face.switchboxes.clear()

        # For each horizontal Face, create a switchbox where it is the top face of the box.
        switchboxes = []
        for h_track in h_tracks[1:]:
            for face in h_track:
                try:
                    # Create a Switchbox with the given Face on top and add it to the list.
                    switchboxes.append(SwitchBox(face))
                except NoSwitchBox:
                    continue

        # Check the switchboxes for problems.
        for swbx in switchboxes:
            swbx.audit()

        # Small switchboxes are more likely to fail routing so try to combine them into larger switchboxes.
        # Use switchboxes containing nets for routing as seeds for coalescing into larger switchboxes.
        seeds = [swbx for swbx in switchboxes if swbx.has_nets()]

        # Sort seeds by perimeter so smaller ones are coalesced before larger ones.
        seeds.sort(key=lambda swbx: swbx.bbox.w + swbx.bbox.h)

        # Coalesce smaller switchboxes into larger ones having more routing area.
        # The smaller switchboxes are removed from the list of switchboxes.
        switchboxes = [seed.coalesce(switchboxes) for seed in seeds]
        switchboxes = [swbx for swbx in switchboxes if swbx]  # Remove None boxes.

        # A coalesced switchbox may have non-part faces containing multiple terminals
        # on the same net. Remove all but one to prevent multi-path routes.
        for switchbox in switchboxes:
            switchbox.trim_repeated_terminals()

        return switchboxes

    def switchbox_router(node, switchboxes, **options):
        """Create detailed wiring between the terminals along the sides of each switchbox.

        Args:
            switchboxes (list): List of SwitchBox objects to be individually routed.
            options (dict, optional): Dictionary of options and values.

        Returns:
            None
        """

        # Do detailed routing inside each switchbox.
        # TODO: Switchboxes are independent so could they be routed in parallel?
        for swbx in switchboxes:
            try:
                # Try routing switchbox from left-to-right.
                swbx.route(**options)

            except RoutingFailure:
                # Routing failed, so try routing top-to-bottom instead.
                swbx.flip_xy()
                # If this fails, then a routing exception will terminate the whole routing process.
                swbx.route(**options)
                swbx.flip_xy()

            # Add switchbox routes to existing node wiring.
            for net, segments in swbx.segments.items():
                node.wires[net].extend(segments)

    def cleanup_wires(node):
        """Try to make wire segments look prettier."""

        route_opts = getattr(node, "_route_options", {}) or {}
        human_readable = route_opts.get("human_readable", False)
        reuse_junctions = route_opts.get("reuse_junctions", True)
        sheet = getattr(node, "name", "?")

        def plog(msg):
            _sch_progress(route_opts, msg)

        def order_seg_points(segments):
            """Order endpoints in a horizontal or vertical segment."""
            for seg in segments:
                if seg.p2 < seg.p1:
                    seg.p1, seg.p2 = seg.p2, seg.p1

        def segments_bbox(segments):
            """Return bounding box containing the given list of segments."""
            seg_pts = list(chain(*((s.p1, s.p2) for s in segments)))
            return BBox(*seg_pts)

        def extract_horz_vert_segs(segments):
            """Separate segments and return lists of horizontal & vertical segments."""
            horz_segs = [seg for seg in segments if seg.p1.y == seg.p2.y]
            vert_segs = [seg for seg in segments if seg.p1.x == seg.p2.x]
            assert len(horz_segs) + len(vert_segs) == len(segments)
            return horz_segs, vert_segs

        def split_segments(segments, net_pin_pts):
            """Return list of net segments split into the smallest intervals without intersections with other segments."""

            # Check each horizontal segment against each vertical segment and split each one if they intersect.
            # (This clunky iteration is used so the horz/vert lists can be updated within the loop.)
            horz_segs, vert_segs = extract_horz_vert_segs(segments)
            i = 0
            while i < len(horz_segs):
                hseg = horz_segs[i]
                hseg_y = hseg.p1.y
                j = 0
                while j < len(vert_segs):
                    vseg = vert_segs[j]
                    vseg_x = vseg.p1.x
                    if (
                        hseg.p1.x <= vseg_x <= hseg.p2.x
                        and vseg.p1.y <= hseg_y <= vseg.p2.y
                    ):
                        int_pt = Point(vseg_x, hseg_y)
                        if int_pt != hseg.p1 and int_pt != hseg.p2:
                            horz_segs.append(
                                Segment(copy.copy(int_pt), copy.copy(hseg.p2))
                            )
                            hseg.p2 = copy.copy(int_pt)
                        if int_pt != vseg.p1 and int_pt != vseg.p2:
                            vert_segs.append(
                                Segment(copy.copy(int_pt), copy.copy(vseg.p2))
                            )
                            vseg.p2 = copy.copy(int_pt)
                    j += 1
                i += 1

            i = 0
            while i < len(horz_segs):
                hseg = horz_segs[i]
                hseg_y = hseg.p1.y
                for pt in net_pin_pts:
                    if pt.y == hseg_y and hseg.p1.x < pt.x < hseg.p2.x:
                        horz_segs.append(Segment(copy.copy(pt), copy.copy(hseg.p2)))
                        hseg.p2 = copy.copy(pt)
                i += 1

            j = 0
            while j < len(vert_segs):
                vseg = vert_segs[j]
                vseg_x = vseg.p1.x
                for pt in net_pin_pts:
                    if pt.x == vseg_x and vseg.p1.y < pt.y < vseg.p2.y:
                        vert_segs.append(Segment(copy.copy(pt), copy.copy(vseg.p2)))
                        vseg.p2 = copy.copy(pt)
                j += 1

            return horz_segs + vert_segs

        def merge_segments(segments):
            """Return segments after merging those that run the same direction and overlap."""

            # Preprocess the segments.
            horz_segs, vert_segs = extract_horz_vert_segs(segments)

            merged_segs = []

            # Separate horizontal segments having the same Y coord.
            horz_segs_v = defaultdict(list)
            for seg in horz_segs:
                horz_segs_v[seg.p1.y].append(seg)

            # Merge overlapping segments having the same Y coord.
            for segs in horz_segs_v.values():
                # Order segments by their starting X coord.
                segs.sort(key=lambda s: s.p1.x)
                # Append first segment to list of merged segments.
                merged_segs.append(segs[0])
                # Go thru the remaining segments looking for overlaps with the last entry on the merge list.
                for seg in segs[1:]:
                    if seg.p1.x <= merged_segs[-1].p2.x:
                        # Segments overlap, so update the extent of the last entry.
                        merged_segs[-1].p2.x = max(seg.p2.x, merged_segs[-1].p2.x)
                    else:
                        # No overlap, so append the current segment to the merge list and use it for
                        # further checks of intersection with remaining segments.
                        merged_segs.append(seg)

            # Separate vertical segments having the same X coord.
            vert_segs_h = defaultdict(list)
            for seg in vert_segs:
                vert_segs_h[seg.p1.x].append(seg)

            # Merge overlapping segments having the same X coord.
            for segs in vert_segs_h.values():
                # Order segments by their starting Y coord.
                segs.sort(key=lambda s: s.p1.y)
                # Append first segment to list of merged segments.
                merged_segs.append(segs[0])
                # Go thru the remaining segments looking for overlaps with the last entry on the merge list.
                for seg in segs[1:]:
                    if seg.p1.y <= merged_segs[-1].p2.y:
                        # Segments overlap, so update the extent of the last entry.
                        merged_segs[-1].p2.y = max(seg.p2.y, merged_segs[-1].p2.y)
                    else:
                        # No overlap, so append the current segment to the merge list and use it for
                        # further checks of intersection with remaining segments.
                        merged_segs.append(seg)

            return merged_segs

        def break_cycles(segments):
            """Remove segments to break any cycles of a net's segments."""

            # Create a dict storing set of segments adjacent to each endpoint.
            adj_segs = defaultdict(set)
            for seg in segments:
                # Add segment to set for each endpoint.
                adj_segs[seg.p1].add(seg)
                adj_segs[seg.p2].add(seg)

            # Create a dict storing the list of endpoints adjacent to each endpoint.
            adj_pts = dict()
            for pt, segs in adj_segs.items():
                # Store endpoints of all segments adjacent to endpoint, then remove the endpoint.
                adj_pts[pt] = list({p for seg in segs for p in (seg.p1, seg.p2)})
                adj_pts[pt].remove(pt)

            # Start at any endpoint and visit adjacent endpoints until all have been visited.
            # If an endpoint is seen more than once, then a cycle exists. Remove the segment forming the cycle.
            visited_pts = []  # List of visited endpoints.
            frontier_pts = list(adj_pts.keys())[:1]  # Arbitrary starting point.
            while frontier_pts:
                # Visit a point on the frontier.
                frontier_pt = frontier_pts.pop()
                visited_pts.append(frontier_pt)

                # Check each adjacent endpoint for cycles.
                for adj_pt in adj_pts[frontier_pt][:]:
                    if adj_pt in visited_pts + frontier_pts:
                        # This point was already reached by another path so there is a cycle.
                        # Break it by removing segment between frontier_pt and adj_pt.
                        loop_seg = (adj_segs[frontier_pt] & adj_segs[adj_pt]).pop()
                        segments.remove(loop_seg)
                        adj_segs[frontier_pt].remove(loop_seg)
                        adj_segs[adj_pt].remove(loop_seg)
                        adj_pts[frontier_pt].remove(adj_pt)
                        adj_pts[adj_pt].remove(frontier_pt)
                    else:
                        # First time adjacent point has been reached, so add it to frontier.
                        frontier_pts.append(adj_pt)
                        # Keep this new frontier point from backtracking to the current frontier point later.
                        adj_pts[adj_pt].remove(frontier_pt)

            return segments

        def is_pin_pt(pt):
            """Return True if the point is on one of the part pins."""
            return pt in pin_pts

        def contains_pt(seg, pt):
            """Return True if the point is contained within the horz/vert segment."""
            return seg.p1.x <= pt.x <= seg.p2.x and seg.p1.y <= pt.y <= seg.p2.y

        def obstructed_by_parts_or_other_nets(
            segment, net, wires, net_bboxes, part_obstacles, ignored_parts=None
        ):
            """Return True if a segment would collide with a part or overlap another net."""

            ignored_parts = ignored_parts or set()

            segment_bbox = BBox(segment.p1, segment.p2)
            for part, part_bbox in part_obstacles:
                if part in ignored_parts:
                    continue
                if part_bbox.intersects(segment_bbox):
                    return True

            # Expand slightly so coincident overlays with other nets are detected.
            segment_bbox = segment_bbox.resize(Vector(2, 2))

            for nt, nt_bbox in net_bboxes.items():
                if nt is net or not segment_bbox.intersects(nt_bbox):
                    continue

                for seg in wires[nt]:
                    if segment.p1.x == segment.p2.x == seg.p1.x == seg.p2.x:
                        if segment.p1.y <= seg.p2.y and segment.p2.y >= seg.p1.y:
                            return True
                    elif segment.p1.y == segment.p2.y == seg.p1.y == seg.p2.y:
                        if segment.p1.x <= seg.p2.x and segment.p2.x >= seg.p1.x:
                            return True

            return False

        def straighten_aligned_pin_connection(
            net, segments, wires, net_bboxes, part_obstacles, net_pins
        ):
            """Replace an unnecessary detour on a 2-pin aligned net with one straight segment."""

            if len(net_pins) != 2 or len(segments) <= 1:
                return segments, True

            pin_pts = [(pin.pt * pin.part.tx).round() for pin in net_pins]
            p1, p2 = pin_pts
            if p1 == p2 or (p1.x != p2.x and p1.y != p2.y):
                return segments, True

            direct_seg = Segment(copy.copy(p1), copy.copy(p2))
            order_seg_points([direct_seg])

            if obstructed_by_parts_or_other_nets(
                direct_seg,
                net,
                wires,
                net_bboxes,
                part_obstacles,
                ignored_parts={pin.part for pin in net_pins},
            ):
                return segments, True

            if len(segments) == 1:
                seg = segments[0]
                order_seg_points([seg])
                if seg.p1 == direct_seg.p1 and seg.p2 == direct_seg.p2:
                    return segments, True

            return [direct_seg], False

        def trim_stubs(segments):
            """Return segments after removing stubs that have an unconnected endpoint."""

            def get_stubs(segments):
                """Return set of stub segments."""

                # For end point, the dict entry contains a list of the segments that meet there.
                stubs = defaultdict(list)

                # Process the segments looking for points that are on only a single segment.
                for seg in segments:
                    # Add the segment to the segment list of each end point.
                    stubs[seg.p1].append(seg)
                    stubs[seg.p2].append(seg)

                # Keep only the segments with an unconnected endpoint that is not on a part pin.
                stubs = {
                    segs[0]
                    for endpt, segs in stubs.items()
                    if len(segs) == 1 and not is_pin_pt(endpt)
                }
                return stubs

            trimmed_segments = set(segments[:])
            stubs = get_stubs(trimmed_segments)
            while stubs:
                trimmed_segments -= stubs
                stubs = get_stubs(trimmed_segments)
            return list(trimmed_segments)

        def remove_jogs_old(net, segments, wires, net_bboxes, part_bboxes):
            """Remove jogs in wiring segments.

            Args:
                net (Net): Net whose wire segments will be modified.
                segments (list): List of wire segments for the given net.
                wires (dict): Dict of lists of wire segments indexed by nets.
                net_bboxes (dict): Dict of BBoxes for wire segments indexed by nets.
                part_bboxes (list): List of BBoxes for the placed parts.
            """

            def get_touching_segs(seg, ortho_segs):
                """Return list of orthogonal segments that touch the given segment."""
                touch_segs = set()
                for oseg in ortho_segs:
                    # oseg horz, seg vert. Do they intersect?
                    if contains_pt(oseg, Point(seg.p2.x, oseg.p1.y)):
                        touch_segs.add(oseg)
                    # oseg vert, seg horz. Do they intersect?
                    elif contains_pt(oseg, Point(oseg.p2.x, seg.p1.y)):
                        touch_segs.add(oseg)
                return list(touch_segs)  # Convert to list with no dups.

            def get_overlap(*segs):
                """Find extent of overlap of parallel horz/vert segments and return as (min, max) tuple."""
                ov1 = float("-inf")
                ov2 = float("inf")
                for seg in segs:
                    if seg.p1.y == seg.p2.y:
                        # Horizontal segment.
                        p1, p2 = seg.p1.x, seg.p2.x
                    else:
                        # Vertical segment.
                        p1, p2 = seg.p1.y, seg.p2.y
                    ov1 = max(ov1, p1)  # Max of extent minimums.
                    ov2 = min(ov2, p2)  # Min of extent maximums.
                # assert ov1 <= ov2
                return ov1, ov2

            def obstructed(segment):
                """Return true if segment obstructed by parts or segments of other nets."""

                # Obstructed if segment bbox intersects one of the part bboxes.
                segment_bbox = BBox(segment.p1, segment.p2)
                for part_bbox in part_bboxes:
                    if part_bbox.intersects(segment_bbox):
                        return True

                # BBoxes don't intersect if they line up exactly edge-to-edge.
                # So expand the segment bbox slightly so intersections with bboxes of
                # other segments will be detected.
                segment_bbox = segment_bbox.resize(Vector(1, 1))

                # Look for an overlay intersection with a segment of another net.
                for nt, nt_bbox in net_bboxes.items():
                    if nt is net:
                        # Don't check this segment with other segments of its own net.
                        continue

                    if not segment_bbox.intersects(nt_bbox):
                        # Don't check this segment against segments of another net whose
                        # bbox doesn't even intersect this segment.
                        continue

                    # Check for overlay intersectionss between this segment and the
                    # parallel segments of the other net.
                    for seg in wires[nt]:
                        if segment.p1.x == segment.p2.x == seg.p1.x == seg.p2.x:
                            # Segments are both aligned vertically on the same track X coord.
                            if segment.p1.y <= seg.p2.y and segment.p2.y >= seg.p1.y:
                                # Segments overlap so segment is obstructed.
                                return True
                        elif segment.p1.y == segment.p2.y == seg.p1.y == seg.p2.y:
                            # Segments are both aligned horizontally on the same track Y coord.
                            if segment.p1.x <= seg.p2.x and segment.p2.x >= seg.p1.x:
                                # Segments overlap so segment is obstructed.
                                return True

                # No obstructions found, so return False.
                return False

            # Make sure p1 <= p2 for segment endpoints.
            order_seg_points(segments)

            # Split segments into horizontal/vertical groups.
            horz_segs, vert_segs = extract_horz_vert_segs(segments)

            # Look for a segment touched by ends of orthogonal segments all pointing in the same direction.
            # Then slide this segment to the other end of the interval by which the touching segments
            # overlap. This will reduce or eliminate the jog.
            stop = True
            for segs, ortho_segs in ((horz_segs, vert_segs), (vert_segs, horz_segs)):
                for seg in segs:
                    # Don't move a segment if one of its endpoints connects to a part pin.
                    if is_pin_pt(seg.p1) or is_pin_pt(seg.p2):
                        continue

                    # Find all orthogonal segments that touch this one.
                    touching_segs = get_touching_segs(seg, ortho_segs)

                    # Find extent of overlap of all orthogonal segments.
                    ov1, ov2 = get_overlap(*touching_segs)

                    if ov1 >= ov2:
                        # No overlap, so this segment can't be moved one way or the other.
                        continue

                    if seg in horz_segs:
                        # Move horz segment vertically to other end of overlap to remove jog.
                        test_seg = Segment(seg.p1, seg.p2)
                        seg_y = test_seg.p1.y
                        if seg_y == ov1:
                            # Segment is at one end of the overlay, so move it to the other end.
                            test_seg.p1.y = ov2
                            test_seg.p2.y = ov2
                            if not obstructed(test_seg):
                                # Segment move is not obstructed, so accept it.
                                seg.p1 = test_seg.p1
                                seg.p2 = test_seg.p2
                                # If one segment is moved, maybe more can be moved so don't stop.
                                stop = False
                        elif seg_y == ov2:
                            # Segment is at one end of the overlay, so move it to the other end.
                            test_seg.p1.y = ov1
                            test_seg.p2.y = ov1
                            if not obstructed(test_seg):
                                # Segment move is not obstructed, so accept it.
                                seg.p1 = test_seg.p1
                                seg.p2 = test_seg.p2
                                # If one segment is moved, maybe more can be moved so don't stop.
                                stop = False
                        else:
                            # Segment in interior of overlay, so it's not a jog. Don't move it.
                            pass
                    else:
                        # Move vert segment horizontally to other end of overlap to remove jog.
                        test_seg = Segment(seg.p1, seg.p2)
                        seg_x = seg.p1.x
                        if seg_x == ov1:
                            # Segment is at one end of the overlay, so move it to the other end.
                            test_seg.p1.x = ov2
                            test_seg.p2.x = ov2
                            if not obstructed(test_seg):
                                # Segment move is not obstructed, so accept it.
                                seg.p1 = test_seg.p1
                                seg.p2 = test_seg.p2
                                # If one segment is moved, maybe more can be moved so don't stop.
                                stop = False
                        elif seg_x == ov2:
                            # Segment is at one end of the overlay, so move it to the other end.
                            test_seg.p1.x = ov1
                            test_seg.p2.x = ov1
                            if not obstructed(test_seg):
                                # Segment move is not obstructed, so accept it.
                                seg.p1 = test_seg.p1
                                seg.p2 = test_seg.p2
                                # If one segment is moved, maybe more can be moved so don't stop.
                                stop = False
                        else:
                            # Segment in interior of overlay, so it's not a jog. Don't move it.
                            pass

            # Return updated segments. If no segments for this net were updated, then stop is True.
            return segments, stop

        def remove_jogs(net, segments, wires, net_bboxes, part_bboxes):
            """Remove jogs and staircases in wiring segments.

            Args:
                net (Net): Net whose wire segments will be modified.
                segments (list): List of wire segments for the given net.
                wires (dict): Dict of lists of wire segments indexed by nets.
                net_bboxes (dict): Dict of BBoxes for wire segments indexed by nets.
                part_bboxes (list): List of BBoxes for the placed parts.
            """

            def obstructed(segment):
                """Return true if segment obstructed by parts or segments of other nets."""

                # Obstructed if segment bbox intersects one of the part bboxes.
                segment_bbox = BBox(segment.p1, segment.p2)
                for part_bbox in part_bboxes:
                    if part_bbox.intersects(segment_bbox):
                        return True

                # BBoxes don't intersect if they line up exactly edge-to-edge.
                # So expand the segment bbox slightly so intersections with bboxes of
                # other segments will be detected.
                segment_bbox = segment_bbox.resize(Vector(2, 2))

                # Look for an overlay intersection with a segment of another net.
                for nt, nt_bbox in net_bboxes.items():
                    if nt is net:
                        # Don't check this segment with other segments of its own net.
                        continue

                    if not segment_bbox.intersects(nt_bbox):
                        # Don't check this segment against segments of another net whose
                        # bbox doesn't even intersect this segment.
                        continue

                    # Check for overlay intersectionss between this segment and the
                    # parallel segments of the other net.
                    for seg in wires[nt]:
                        if segment.p1.x == segment.p2.x == seg.p1.x == seg.p2.x:
                            # Segments are both aligned vertically on the same track X coord.
                            if segment.p1.y <= seg.p2.y and segment.p2.y >= seg.p1.y:
                                # Segments overlap so segment is obstructed.
                                return True
                        elif segment.p1.y == segment.p2.y == seg.p1.y == seg.p2.y:
                            # Segments are both aligned horizontally on the same track Y coord.
                            if segment.p1.x <= seg.p2.x and segment.p2.x >= seg.p1.x:
                                # Segments overlap so segment is obstructed.
                                return True

                # No obstructions found, so return False.
                return False

            def get_corners(segments):
                """Return dictionary of right-angle corner points and lists of associated segments."""

                # For each corner point, the dict entry contains a list of the segments that meet there.
                corners = defaultdict(list)

                # Process the segments so that any potential right-angle corner has the horizontal
                # segment followed by the vertical segment.
                horz_segs, vert_segs = extract_horz_vert_segs(segments)
                for seg in horz_segs + vert_segs:
                    # Add the segment to the segment list of each end point.
                    corners[seg.p1].append(seg)
                    corners[seg.p2].append(seg)

                # Keep only the corner points where two segments meet at right angles at a point not on a part pin.
                corners = {
                    corner: segs
                    for corner, segs in corners.items()
                    if len(segs) == 2
                    and not is_pin_pt(corner)
                    and segs[0] in horz_segs
                    and segs[1] in vert_segs
                }
                return corners

            def get_jogs(segments):
                """Yield the three segments and starting and end points of a staircase or tophat jog."""

                # Get dict of right-angle corners formed by segments.
                corners = get_corners(segments)

                # Look for segments with both endpoints on right-angle corners, indicating this segment
                # is in the middle of a three-segment staircase or tophat jog.
                for segment in segments:
                    if segment.p1 in corners and segment.p2 in corners:
                        # Get the three segments in the jog.
                        jog_segs = set()
                        jog_segs.add(corners[segment.p1][0])
                        jog_segs.add(corners[segment.p1][1])
                        jog_segs.add(corners[segment.p2][0])
                        jog_segs.add(corners[segment.p2][1])

                        # Get the points where the three-segment jog starts and stops.
                        start_stop_pts = set()
                        for seg in jog_segs:
                            start_stop_pts.add(seg.p1)
                            start_stop_pts.add(seg.p2)
                        start_stop_pts.discard(segment.p1)
                        start_stop_pts.discard(segment.p2)

                        # Send the jog that was found.
                        yield list(jog_segs), list(start_stop_pts)

            # 人类可读模式关闭洗牌，优先保证输出可重复与可比对。
            if human_readable:
                segments.sort(
                    key=lambda seg: (
                        min(seg.p1.x, seg.p2.x),
                        min(seg.p1.y, seg.p2.y),
                        max(seg.p1.x, seg.p2.x),
                        max(seg.p1.y, seg.p2.y),
                    )
                )
            else:
                # Shuffle segments to vary the order of detected jogs.
                random.shuffle(segments)

            # Get iterator for jogs.
            jogs = get_jogs(segments)

            # Search for jogs and break from the loop if a correctable jog is found or we run out of jogs.
            while True:
                # Get the segments and start-stop points for the next jog.
                try:
                    jog_segs, start_stop_pts = next(jogs)
                except StopIteration:
                    # No more jogs and no corrections made, so return segments and stop flag is true.
                    return segments, True

                # Get the start-stop points and order them so p1 < p3.
                p1, p3 = sorted(start_stop_pts)

                # These are the potential routing points for correcting the jog.
                # Either start at p1 and move vertically and then horizontally to p3, or
                # move horizontally from p1 and then vertically to p3.
                p2s = [Point(p1.x, p3.y), Point(p3.x, p1.y)]

                # 人类可读模式固定尝试顺序，避免同网表多次输出方向不一致。
                if human_readable:
                    p2s = sorted(p2s, key=lambda p: (p.x, p.y))
                else:
                    # Shuffle the routing points so the applied correction isn't always the same orientation.
                    random.shuffle(p2s)

                # Check each routing point to see if it leads to a valid routing.
                for p2 in p2s:
                    # Replace the three-segment jog with these two right-angle segments.
                    new_segs = [
                        Segment(copy.copy(pa), copy.copy(pb))
                        for pa, pb in ((p1, p2), (p2, p3))
                        if pa != pb
                    ]
                    order_seg_points(new_segs)

                    # Check the new segments to see if they run into parts or segments of other nets.
                    if not any((obstructed(new_seg) for new_seg in new_segs)):
                        # OK, segments are good so replace the old segments in the jog with them.
                        for seg in jog_segs:
                            segments.remove(seg)
                        segments.extend(new_segs)

                        # Return updated segments and set stop flag to false because segments were modified.
                        return segments, False

        def _straighten_local_detours(
            net,
            segments,
            wires,
            net_bboxes,
            part_bboxes,
            net_pins,
            visited_patterns=None,
        ):
            """压平 human_readable 下 cleanup 仍残留的小凸起（保守，每次至多改一处）。

            global/switchbox 路由优先保证连通，terminal 离散采样易留下 H-V-H / V-H-V
            小台阶；remove_jogs 主要处理标准三段 jog，本 pass 专门收掉“几乎可拉直”的局部 detour。

            cleanup 后同 net 常已有 junction / T 分叉 / 短 stub，端点未必 degree=2；
            允许在端点挂同 net 分支，只要压平后分支连接点仍落在新路径上（junction-aware）。
            """

            def obstructed(segment):
                """与 remove_jogs 一致：器件 bbox 或其它 net 同轨 overlay 视为阻挡。"""
                segment_bbox = BBox(segment.p1, segment.p2)
                for part_bbox in part_bboxes:
                    if part_bbox.intersects(segment_bbox):
                        return True
                segment_bbox = segment_bbox.resize(Vector(2, 2))
                for nt, nt_bbox in net_bboxes.items():
                    if nt is net:
                        continue
                    if not segment_bbox.intersects(nt_bbox):
                        continue
                    for seg in wires[nt]:
                        if segment.p1.x == segment.p2.x == seg.p1.x == seg.p2.x:
                            if segment.p1.y <= seg.p2.y and segment.p2.y >= seg.p1.y:
                                return True
                        elif segment.p1.y == segment.p2.y == seg.p1.y == seg.p2.y:
                            if segment.p1.x <= seg.p2.x and segment.p2.x >= seg.p1.x:
                                return True
                return False

            def seg_key(seg):
                return (
                    min(seg.p1.x, seg.p2.x),
                    min(seg.p1.y, seg.p2.y),
                    max(seg.p1.x, seg.p2.x),
                    max(seg.p1.y, seg.p2.y),
                )

            def is_horz(seg):
                return seg.p1.y == seg.p2.y

            def is_vert(seg):
                return seg.p1.x == seg.p2.x

            def far_end(seg, junction):
                return seg.p2 if seg.p1 == junction else seg.p1

            def pattern_key(*candidate_segs):
                """Build a stable key so the same tiny detour is not retried repeatedly."""
                return tuple(sorted(seg_key(seg) for seg in candidate_segs))

            def pins_on_path(to_remove, new_segs):
                """本 net 落在待移除路径上的 pin 必须仍落在新路径上。"""
                for pt in net_pins:
                    on_old = any(contains_pt(s, pt) for s in to_remove)
                    if not on_old:
                        continue
                    if not any(contains_pt(s, pt) for s in new_segs):
                        return False
                return True

            def attachment_points_ok(to_remove, new_segs):
                """待移除段与保留分支的交汇点必须仍落在新路径上（junction-aware）。"""
                to_remove_set = set(to_remove)
                checked = set()
                for seg in to_remove:
                    for pt in (seg.p1, seg.p2):
                        if pt in checked:
                            continue
                        checked.add(pt)
                        at_pt = pt_segs[pt]
                        has_remove = any(s in to_remove_set for s in at_pt)
                        has_keep = any(s not in to_remove_set for s in at_pt)
                        if not (has_remove and has_keep):
                            continue
                        if not any(contains_pt(ns, pt) for ns in new_segs):
                            return False
                return True

            def try_apply(to_remove, new_segs):
                order_seg_points(new_segs)
                new_segs = [s for s in new_segs if s.p1 != s.p2]
                if not new_segs:
                    return False
                if any(obstructed(s) for s in new_segs):
                    return False
                if not pins_on_path(to_remove, new_segs):
                    return False
                if not attachment_points_ok(to_remove, new_segs):
                    return False
                for seg in to_remove:
                    segments.remove(seg)
                segments.extend(
                    Segment(copy.copy(s.p1), copy.copy(s.p2)) for s in new_segs
                )
                return True

            def main_legs_at(junction, mid, parallel_horz):
                """在 junction 上选取与 mid 组成凸起主通路的平行侧线段（确定性排序）。"""
                others = [s for s in pt_segs[junction] if s is not mid]
                if parallel_horz:
                    legs = [s for s in others if is_horz(s)]
                else:
                    legs = [s for s in others if is_vert(s)]
                return sorted(legs, key=seg_key)

            # 只处理明显小凸起，避免大范围改线
            if visited_patterns is None:
                visited_patterns = set()

            # Skip this pass on large schematics because even a local scan becomes
            # too expensive when repeated inside cleanup_wires().
            if len(segments) > 1000:
                return segments, True

            # Only handle very small local detours. Wider rewrites belong to the
            # main jog-removal pass and are intentionally left alone here.
            detour_thresh = max(GRID, GRID * 2)

            order_seg_points(segments)

            pt_segs = defaultdict(list)
            for seg in segments:
                pt_segs[seg.p1].append(seg)
                pt_segs[seg.p2].append(seg)

            # Restrict this pass to simple local H-V-H / V-H-V patterns so it
            # stays predictable and does not turn into a whole-graph optimizer.
            for mid in sorted(segments, key=seg_key):
                # 中间拐角若接 pin，不移动拓扑（最保守）
                if is_pin_pt(mid.p1) or is_pin_pt(mid.p2):
                    continue

                # ---------- H-V-H：两水平 夹 短竖 ----------
                if is_vert(mid):
                    legs_p1 = main_legs_at(mid.p1, mid, parallel_horz=True)
                    legs_p2 = main_legs_at(mid.p2, mid, parallel_horz=True)
                    if not legs_p1 or not legs_p2:
                        continue

                    j1, j2 = mid.p1, mid.p2
                    detour_h = abs(j1.y - j2.y)
                    if detour_h == 0 or detour_h > detour_thresh:
                        continue
                    if abs(mid.p1.y - mid.p2.y) > detour_thresh:
                        continue

                    for seg_a in legs_p1:
                        for seg_c in legs_p2:
                            if seg_a is seg_c:
                                continue
                            to_remove = [seg_a, mid, seg_c]
                            candidate_key = pattern_key(seg_a, mid, seg_c)
                            if candidate_key in visited_patterns:
                                continue
                            visited_patterns.add(candidate_key)

                            p_start = far_end(seg_a, j1)
                            p_end = far_end(seg_c, j2)
                            ya, yc = seg_a.p1.y, seg_c.p1.y

                            # 情况 A：两水平已共线，可用单段替代整段小凸起
                            if ya == yc:
                                x_lo = min(p_start.x, p_end.x, j1.x, j2.x)
                                x_hi = max(p_start.x, p_end.x, j1.x, j2.x)
                                new_seg = Segment(
                                    copy.copy(Point(x_lo, ya)),
                                    copy.copy(Point(x_hi, ya)),
                                )
                                if try_apply(to_remove, [new_seg]):
                                    return segments, False
                                continue

                            # 情况 B：小高度差，用 L 形绕开中间竖台阶
                            corners = sorted(
                                [
                                    Point(p_end.x, p_start.y),
                                    Point(p_start.x, p_end.y),
                                ],
                                key=lambda p: (p.x, p.y),
                            )
                            for corner in corners:
                                new_segs = []
                                if p_start != corner:
                                    new_segs.append(
                                        Segment(
                                            copy.copy(p_start), copy.copy(corner)
                                        )
                                    )
                                if corner != p_end:
                                    new_segs.append(
                                        Segment(
                                            copy.copy(corner), copy.copy(p_end)
                                        )
                                    )
                                if try_apply(to_remove, new_segs):
                                    return segments, False
                    continue

                # ---------- V-H-V：两竖直 夹 短横 ----------
                if is_horz(mid):
                    legs_p1 = main_legs_at(mid.p1, mid, parallel_horz=False)
                    legs_p2 = main_legs_at(mid.p2, mid, parallel_horz=False)
                    if not legs_p1 or not legs_p2:
                        continue

                    j1, j2 = mid.p1, mid.p2
                    detour_w = abs(j1.x - j2.x)
                    if detour_w == 0 or detour_w > detour_thresh:
                        continue
                    if abs(mid.p1.x - mid.p2.x) > detour_thresh:
                        continue

                    for seg_a in legs_p1:
                        for seg_c in legs_p2:
                            if seg_a is seg_c:
                                continue
                            to_remove = [seg_a, mid, seg_c]
                            candidate_key = pattern_key(seg_a, mid, seg_c)
                            if candidate_key in visited_patterns:
                                continue
                            visited_patterns.add(candidate_key)

                            p_start = far_end(seg_a, j1)
                            p_end = far_end(seg_c, j2)
                            xa, xc = seg_a.p1.x, seg_c.p1.x

                            if xa == xc:
                                y_lo = min(p_start.y, p_end.y, j1.y, j2.y)
                                y_hi = max(p_start.y, p_end.y, j1.y, j2.y)
                                new_seg = Segment(
                                    copy.copy(Point(xa, y_lo)),
                                    copy.copy(Point(xa, y_hi)),
                                )
                                if try_apply(to_remove, [new_seg]):
                                    return segments, False
                                continue

                            corners = sorted(
                                [
                                    Point(p_end.x, p_start.y),
                                    Point(p_start.x, p_end.y),
                                ],
                                key=lambda p: (p.x, p.y),
                            )
                            for corner in corners:
                                new_segs = []
                                if p_start != corner:
                                    new_segs.append(
                                        Segment(
                                            copy.copy(p_start), copy.copy(corner)
                                        )
                                    )
                                if corner != p_end:
                                    new_segs.append(
                                        Segment(
                                            copy.copy(corner), copy.copy(p_end)
                                        )
                                    )
                                if try_apply(to_remove, new_segs):
                                    return segments, False

            return segments, True

        def _reuse_wire_junctions(net, segments, net_pins, part_bboxes, wires, net_bboxes):
            """同 net 端点复用已有 junction 或线段 T 接入点，避免在拐点旁另开通道。

            路由搜索阶段只有 face 级树，不知道最终导线几何；本 pass 在 cleanup 里
            把“差一格未接上”的端点 snap 到已有 junction，或在同 net 线段内部 T 接入。
            每次至多改一处，便于与 merge/split/remove_jogs 交替收敛。
            """

            net_name = str(getattr(net, "name", "") or "")
            snap_dist = GRID * 3 if is_trunk_net_name(net_name) else GRID * 2

            def manhattan_dist(a, b):
                return abs(a.x - b.x) + abs(a.y - b.y)

            def is_net_pin(pt):
                if is_pin_pt(pt):
                    return True
                return any(pt == pin_pt for pin_pt in net_pins)

            def obstructed(segment):
                segment_bbox = BBox(segment.p1, segment.p2)
                for part_bbox in part_bboxes:
                    if part_bbox.intersects(segment_bbox):
                        return True
                segment_bbox = segment_bbox.resize(Vector(1, 1))
                for nt, nt_bbox in net_bboxes.items():
                    if nt is net:
                        continue
                    if not segment_bbox.intersects(nt_bbox):
                        continue
                    for seg in wires[nt]:
                        if segment.p1.x == segment.p2.x == seg.p1.x == seg.p2.x:
                            if segment.p1.y <= seg.p2.y and segment.p2.y >= seg.p1.y:
                                return True
                        elif segment.p1.y == segment.p2.y == seg.p1.y == seg.p2.y:
                            if segment.p1.x <= seg.p2.x and segment.p2.x >= seg.p1.x:
                                return True
                return False

            def collect_junction_points(segs):
                horz_segs, vert_segs = extract_horz_vert_segs(segs)
                jpts = set()
                for hseg in horz_segs:
                    for vseg in vert_segs:
                        ix, iy = vseg.p1.x, hseg.p1.y
                        if hseg.p1.x <= ix <= hseg.p2.x and vseg.p1.y <= iy <= vseg.p2.y:
                            jpts.add(Point(ix, iy))
                return jpts

            def point_on_interior(seg, pt):
                order_seg_points([seg])
                if seg.p1.y == seg.p2.y:
                    return pt.y == seg.p1.y and seg.p1.x < pt.x < seg.p2.x
                return pt.x == seg.p1.x and seg.p1.y < pt.y < seg.p2.y

            def endpoint_is(seg, pt):
                return seg.p1 == pt or seg.p2 == pt

            def split_segment_at(segs, seg, pt):
                if endpoint_is(seg, pt) or not point_on_interior(seg, pt):
                    return False
                segs.remove(seg)
                segs.append(Segment(copy.copy(seg.p1), copy.copy(pt)))
                segs.append(Segment(copy.copy(pt), copy.copy(seg.p2)))
                return True

            def move_endpoint(seg, ep, new_pt):
                if seg.p1 == ep:
                    seg.p1 = copy.copy(new_pt)
                elif seg.p2 == ep:
                    seg.p2 = copy.copy(new_pt)
                else:
                    return False
                return seg.p1 != seg.p2

            def colinear_target(seg, target):
                if seg.p1.y == seg.p2.y:
                    if target.y == seg.p1.y:
                        return target
                elif seg.p1.x == seg.p2.x:
                    if target.x == seg.p1.x:
                        return target
                return None

            def try_snap_endpoint(segs, seg, ep, target):
                if colinear_target(seg, target) is None or ep == target:
                    return False
                if manhattan_dist(ep, target) > snap_dist:
                    return False
                test = Segment(copy.copy(seg.p1), copy.copy(seg.p2))
                if test.p1 == ep:
                    test.p1 = copy.copy(target)
                else:
                    test.p2 = copy.copy(target)
                if test.p1 == test.p2 or obstructed(test):
                    return False
                if not move_endpoint(seg, ep, target):
                    segs.remove(seg)
                return True

            def try_t_tap(segs, seg, ep, other):
                if other.p1.y == other.p2.y:
                    tap = Point(ep.x, other.p1.y)
                else:
                    tap = Point(other.p1.x, ep.y)
                if manhattan_dist(ep, tap) > snap_dist:
                    return False
                if not point_on_interior(other, tap):
                    return False
                if seg.p1.y == seg.p2.y:
                    if ep.y != tap.y or ep.y != seg.p1.y:
                        return False
                else:
                    if ep.x != tap.x or ep.x != seg.p1.x:
                        return False
                test = Segment(copy.copy(seg.p1), copy.copy(seg.p2))
                if test.p1 == ep:
                    test.p1 = copy.copy(tap)
                else:
                    test.p2 = copy.copy(tap)
                if test.p1 == test.p2 or obstructed(test):
                    return False
                if not move_endpoint(seg, ep, tap):
                    segs.remove(seg)
                if not endpoint_is(other, tap):
                    split_segment_at(segs, other, tap)
                return True

            order_seg_points(segments)
            junction_pts = collect_junction_points(segments)
            candidates = []

            for seg in segments:
                for ep in (seg.p1, seg.p2):
                    if is_net_pin(ep):
                        continue
                    for jpt in sorted(junction_pts, key=lambda p: (p.x, p.y)):
                        if ep == jpt:
                            continue
                        dist = manhattan_dist(ep, jpt)
                        if dist and dist <= snap_dist:
                            candidates.append(
                                (
                                    "junction",
                                    dist,
                                    id(seg),
                                    ep.x,
                                    ep.y,
                                    seg,
                                    ep,
                                    jpt,
                                    None,
                                )
                            )
                    for other in segments:
                        if other is seg:
                            continue
                        if other.p1.y == other.p2.y:
                            tap = Point(ep.x, other.p1.y)
                        else:
                            tap = Point(other.p1.x, ep.y)
                        dist = manhattan_dist(ep, tap)
                        if dist and dist <= snap_dist and point_on_interior(other, tap):
                            candidates.append(
                                (
                                    "ttap",
                                    dist,
                                    id(seg),
                                    ep.x,
                                    ep.y,
                                    seg,
                                    ep,
                                    tap,
                                    other,
                                )
                            )

            candidates.sort(key=lambda c: (c[0], c[1], c[2], c[3], c[4]))
            for kind, _, _, _, _, seg, ep, target, other in candidates:
                if seg not in segments:
                    continue
                if kind == "junction":
                    if try_snap_endpoint(segments, seg, ep, target):
                        return segments, False
                elif other in segments and try_t_tap(segments, seg, ep, other):
                    return segments, False

            return segments, True

        # Get part bounding boxes so parts can be avoided when modifying net segments.
        part_obstacles = _build_route_part_obstacles(node, human_readable)
        part_bboxes = [bbox for _, bbox in part_obstacles]

        # Get dict of bounding boxes for the nets in this node.
        net_bboxes = {net: segments_bbox(segs) for net, segs in node.wires.items()}

        # Get locations for part pins of each net. (For use when splitting net segments.)
        net_internal_pins = dict()
        net_pin_pts = dict()
        for net in node.wires.keys():
            pins = _driver_route_pins(node, net)
            if not pins:
                pins = list(node.get_internal_pins(net))
            net_internal_pins[net] = pins
            net_pin_pts[net] = [
                (pin.pt * pin.part.tx).round() for pin in net_internal_pins[net]
            ]

        plog(
            f"[schematic] cleanup 开始 sheet={sheet}，"
            f"{len(node.wires)} 网 / {sum(len(s) for s in node.wires.values())} 段"
        )

        prerouted = set(getattr(node, "_driver_prerouted_nets", set()) or [])

        # Do a generalized cleanup of the wire segments of each net.
        for net, segments in node.wires.items():
            if net in prerouted:
                segments = [seg.round() for seg in segments]
                segments = [seg for seg in segments if seg.p1 != seg.p2]
                order_seg_points(segments)
                node.wires[net] = segments
                continue

            # Round the wire segment endpoints to integers.
            segments = [seg.round() for seg in segments]

            # Keep only non zero-length segments.
            segments = [seg for seg in segments if seg.p1 != seg.p2]

            # Make sure the segment endpoints are in the right order.
            order_seg_points(segments)

            # Merge colinear, overlapping segments. Also removes any duplicated segments.
            segments = merge_segments(segments)

            # Split intersecting segments.
            segments = split_segments(segments, net_pin_pts[net])

            # Break loops of segments.
            segments = break_cycles(segments)

            # Keep only non zero-length segments.
            segments = [seg for seg in segments if seg.p1 != seg.p2]

            # Trim wire stubs.
            segments = trim_stubs(segments)

            if reuse_junctions:
                segments, _ = _reuse_wire_junctions(
                    net,
                    segments,
                    net_pin_pts[net],
                    part_bboxes,
                    node.wires,
                    net_bboxes,
                )
                segments = merge_segments(segments)
                segments = split_segments(segments, net_pin_pts[net])
                segments = [seg for seg in segments if seg.p1 != seg.p2]

            node.wires[net] = segments

        # Remove jogs in the wire segments of each net.
        keep_cleaning = True
        clean_round = 0
        max_clean_rounds = int(route_opts.get("cleanup_max_rounds", 12))
        local_detour_visited = defaultdict(set)
        while keep_cleaning:
            clean_round += 1
            if clean_round > max_clean_rounds:
                plog(
                    f"[schematic] cleanup 达到轮次上限 {max_clean_rounds}，"
                    f"sheet={sheet}，强制结束"
                )
                break
            plog(f"[schematic] cleanup 轮次 {clean_round} sheet={sheet}")
            keep_cleaning = False

            max_inner_iters = int(route_opts.get("cleanup_max_inner_iters", 64))
            net_changed = False

            for net, segments in node.wires.items():
                net_label = getattr(net, "name", str(net))
                if net in prerouted:
                    # rail/主链预布线不再 split/去 jog，避免把水平母线拆成绕框折线。
                    segments = [seg for seg in segments if seg.p1 != seg.p2]
                    node.wires[net] = segments
                    continue

                # 先 split 一次，再只跑 remove_jogs；避免「去 jog → split → 又出现 jog」振荡。
                segments = split_segments(segments, net_pin_pts[net])

                segments, stop_direct = straighten_aligned_pin_connection(
                    net,
                    segments,
                    node.wires,
                    net_bboxes,
                    part_obstacles,
                    net_internal_pins[net],
                )
                if not stop_direct:
                    net_changed = True

                inner_iter = 0
                while inner_iter < max_inner_iters:
                    inner_iter += 1
                    if inner_iter == 1 or inner_iter % 20 == 0:
                        plog(
                            f"[schematic] cleanup 网 {net_label} "
                            f"去 jog {inner_iter} sheet={sheet}"
                        )
                    segments, stop_jogs = remove_jogs(
                        net, segments, node.wires, net_bboxes, part_bboxes
                    )
                    segments = [seg for seg in segments if seg.p1 != seg.p2]
                    if not stop_jogs:
                        net_changed = True
                    if stop_jogs:
                        break
                else:
                    plog(
                        f"[schematic] cleanup 网 {net_label} 去 jog 达上限 "
                        f"{max_inner_iters}，sheet={sheet}"
                    )

                segments = merge_segments(segments)
                segments = split_segments(segments, net_pin_pts[net])
                segments = [seg for seg in segments if seg.p1 != seg.p2]
                segments = trim_stubs(segments)

                if human_readable:
                    segments, stop_detour = _straighten_local_detours(
                        net,
                        segments,
                        node.wires,
                        net_bboxes,
                        part_bboxes,
                        net_pin_pts[net],
                        local_detour_visited[net],
                    )
                    if not stop_detour:
                        net_changed = True
                        segments = merge_segments(segments)
                        segments = split_segments(segments, net_pin_pts[net])
                        segments = [
                            seg for seg in segments if seg.p1 != seg.p2
                        ]
                        segments = trim_stubs(segments)

                net_bboxes[net] = segments_bbox(segments)
                node.wires[net] = segments

            if net_changed:
                keep_cleaning = True

        plog(f"[schematic] cleanup 结束 sheet={sheet}，共 {clean_round} 轮")

        if human_readable:
            # 在通用清理后追加保守的人类化处理：只做不改变连通性的局部简化。
            plog(f"[schematic] humanize_wires sheet={sheet}")
            node.humanize_wires()

    def humanize_wires(node):
        """Apply conservative post-cleanup wiring simplifications."""

        def seg_key(seg):
            return (
                min(seg.p1.x, seg.p2.x),
                min(seg.p1.y, seg.p2.y),
                max(seg.p1.x, seg.p2.x),
                max(seg.p1.y, seg.p2.y),
            )

        # 使用 part bbox 作为硬障碍，避免“美化”导致导线穿过器件。
        part_bboxes = [p.bbox * p.tx for p in node.parts]

        prerouted = set(getattr(node, "_driver_prerouted_nets", set()) or [])

        for net, segments in node.wires.items():
            if net in prerouted:
                continue

            cleaned = []
            for seg in segments:
                if seg.p1 == seg.p2:
                    continue
                if seg.p2 < seg.p1:
                    seg = Segment(seg.p2, seg.p1)
                cleaned.append(seg)

            # 先按几何顺序稳定排序，便于后续重复运行获得相同结果。
            cleaned = sorted(cleaned, key=seg_key)

            net_name = str(getattr(net, "name", "") or "")
            if is_trunk_net_name(net_name) and len(cleaned) >= 2:
                merged = []
                horz = sorted(
                    [s for s in cleaned if s.p1.y == s.p2.y], key=seg_key
                )
                vert = sorted(
                    [s for s in cleaned if s.p1.x == s.p2.x], key=seg_key
                )
                other = [s for s in cleaned if s not in horz and s not in vert]

                def merge_axis(segs, axis):
                    if not segs:
                        return []
                    out = [segs[0]]
                    for seg in segs[1:]:
                        prev = out[-1]
                        if axis == "h" and prev.p1.y == seg.p1.y:
                            if prev.p2.x == seg.p1.x:
                                prev.p2 = Point(max(prev.p2.x, seg.p2.x), prev.p1.y)
                                continue
                            if seg.p2.x == prev.p1.x:
                                prev.p1 = Point(min(prev.p1.x, seg.p1.x), prev.p1.y)
                                continue
                        if axis == "v" and prev.p1.x == seg.p1.x:
                            if prev.p2.y == seg.p1.y:
                                prev.p2 = Point(prev.p1.x, max(prev.p2.y, seg.p2.y))
                                continue
                            if seg.p2.y == prev.p1.y:
                                prev.p1 = Point(prev.p1.x, min(prev.p1.y, seg.p1.y))
                                continue
                        out.append(seg)
                    return out

                cleaned = merge_axis(horz, "h") + merge_axis(vert, "v") + other

            # 删除非常短的 stub，保留连接主干的必要线段。
            # Segment 无 length 属性；用端点差的 magnitude（正交线段即几何长度）。
            stub_thresh = max(1, GRID // 2)
            trimmed = []
            for seg in cleaned:
                seg_len = (seg.p2 - seg.p1).magnitude
                if seg_len < stub_thresh:
                    pt1_refs = 0
                    pt2_refs = 0
                    for other in cleaned:
                        if other is seg:
                            continue
                        if seg.p1 in (other.p1, other.p2):
                            pt1_refs += 1
                        if seg.p2 in (other.p1, other.p2):
                            pt2_refs += 1
                    if pt1_refs + pt2_refs <= 1:
                        continue
                trimmed.append(seg)

            node.wires[net] = trimmed

    def add_junctions(node):
        """Add X & T-junctions where wire segments in the same net meet."""

        def find_junctions(route):
            """Find junctions where segments of a net intersect.

            Args:
                route (List): List of Segment objects.

            Returns:
                List: List of Points, one for each junction.

            Notes:
                You must run merge_segments() before finding junctions
                or else the segment endpoints might not be ordered
                correctly with p1 < p2.
            """

            # Separate route into vertical and horizontal segments.
            horz_segs = [seg for seg in route if seg.p1.y == seg.p2.y]
            vert_segs = [seg for seg in route if seg.p1.x == seg.p2.x]

            junctions = []

            # Check each pair of horz/vert segments for an intersection, except
            # where they form a right-angle turn.
            for hseg in horz_segs:
                hseg_y = hseg.p1.y  # Horz seg Y coord.
                for vseg in vert_segs:
                    vseg_x = vseg.p1.x  # Vert seg X coord.
                    if (hseg.p1.x < vseg_x < hseg.p2.x) and (
                        vseg.p1.y <= hseg_y <= vseg.p2.y
                    ):
                        # The vert segment intersects the interior of the horz seg.
                        junctions.append(Point(vseg_x, hseg_y))
                    elif (vseg.p1.y < hseg_y < vseg.p2.y) and (
                        hseg.p1.x <= vseg_x <= hseg.p2.x
                    ):
                        # The horz segment intersects the interior of the vert seg.
                        junctions.append(Point(vseg_x, hseg_y))

            return junctions

        for net, segments in node.wires.items():
            # Add X & T-junctions between segments in the same net.
            junctions = find_junctions(segments)
            node.junctions[net].extend(junctions)

    def rmv_routing_stuff(node):
        """Remove attributes added to parts/pins during routing."""

        rmv_attr(node.parts, ("left_track", "right_track", "top_track", "bottom_track"))
        for part in node.parts:
            rmv_attr(part.pins, ("route_pt", "face"))

    def route(node, tool=None, **options):
        """Route the wires between part pins in this node and its children.

        Steps:
            1. Divide the bounding box surrounding the parts into switchboxes.
            2. Do global routing of nets through sequences of switchboxes.
            3. Do detailed routing within each switchbox.

        Args:
            node (Node): Hierarchical node containing the parts to be connected.
            tool (str): Backend tool for schematics.
            options (dict, optional): Dictionary of options and values:
                "allow_routing_failure", "draw", "draw_all_terminals", "show_capacities",
                "draw_switchbox", "draw_routing", "draw_channels"
        """

        # Inject the constants for the backend tool into this module.
        import skidl
        from skidl.tools import tool_modules

        tool = tool or skidl.config.tool
        this_module = sys.modules[__name__]
        this_module.__dict__.update(tool_modules[tool].constants.__dict__)

        seed = options.get("seed")
        if options.get("human_readable", False) and seed is None:
            # 人类可读模式默认固定随机种子，保证同输入多次运行可重现。
            seed = 0
        random.seed(seed)
        node._route_options = options
        sheet = getattr(node, "name", "?")

        # Remove any stuff leftover from a previous place & route run.
        node.rmv_routing_stuff()

        # First, recursively route any children of this node.
        # TODO: Child nodes are independent so could they be processed in parallel?
        for child in node.children.values():
            child.route(tool=tool, **options)

        # Exit if no parts to route in this node.
        if not node.parts:
            return

        # Get all the nets that have one or more pins within this node.
        internal_nets = node.get_internal_nets()

        # Exit if no nets to route.
        if not internal_nets:
            return

        restore_driver_wire_nets(node, internal_nets, **options)

        try:
            if options.get("human_readable"):
                real_parts = [p for p in node.parts if getattr(p, "ref", None)]
                if real_parts and not getattr(node, "_human_readable_main_part", None):
                    node._human_readable_main_part = node._find_main_part(real_parts)

            _sch_progress(
                options,
                f"[schematic] 布线 sheet={sheet}，{len(node.parts)} 件 / "
                f"{len(internal_nets)} 网",
            )
            # Clear pin endpoints from any previous routing pass in this node.
            del pin_pts[:]  # Clear the list. Works for Python 2 and 3.

            # Priority 1: directly route aligned point-to-point nets when unobstructed.
            direct_nets = set(node.route_straight_nets(internal_nets))
            rail_handled = route_driver_rails(node, internal_nets, **options)
            routed_nets = [
                net
                for net in internal_nets
                if net not in direct_nets and net not in rail_handled
            ]

            if not routed_nets:
                node.cleanup_wires()
                node.add_junctions()
                node.rmv_routing_stuff()
                rmv_attr(node, ("_route_options",))
                return

            # Extend routing points of part pins to the edges of their bounding boxes.
            node.add_routing_points(routed_nets)

            # Create the surrounding box that contains the entire routing area.
            channel_sz = (len(routed_nets) + 1) * GRID
            routing_bbox = (
                node.internal_bbox().resize(Vector(channel_sz, channel_sz))
            ).round()

            # Create horizontal & vertical global routing tracks and faces.
            h_tracks, v_tracks = node.create_routing_tracks(routing_bbox)

            # Create terminals on the faces in the routing tracks.
            node.create_terminals(routed_nets, h_tracks, v_tracks)

            # Draw part outlines, routing tracks and terminals.
            if options.get("draw_routing_channels"):
                draw_routing(
                    node, routing_bbox, node.parts, h_tracks, v_tracks, **options
                )

            # Do global routing of nets internal to the node.
            _sch_progress(options, f"[schematic] 全局路径 sheet={sheet} ...")
            global_routes = node.global_router(routed_nets)

            # Convert the global face-to-face routes into terminals on the switchboxes.
            for route in global_routes:
                route.cvt_faces_to_terminals()

            # If enabled, draw the global routing for debug purposes.
            if options.get("draw_global_routing"):
                draw_routing(
                    node,
                    routing_bbox,
                    node.parts,
                    h_tracks,
                    v_tracks,
                    global_routes,
                    **options
                )

            # Create detailed wiring using switchbox routing for the global routes.
            switchboxes = node.create_switchboxes(h_tracks, v_tracks)
            _sch_progress(
                options,
                f"[schematic] switchbox 布线 sheet={sheet}，{len(switchboxes)} 盒 ...",
            )

            # Draw switchboxes and routing channels.
            if options.get("draw_assigned_terminals"):
                draw_routing(
                    node,
                    routing_bbox,
                    node.parts,
                    switchboxes,
                    global_routes,
                    **options
                )

            node.switchbox_router(switchboxes, **options)
            _sch_progress(options, f"[schematic] switchbox 完成 sheet={sheet}")

            # If enabled, draw the global and detailed routing for debug purposes.
            if options.get("draw_switchbox_routing"):
                draw_routing(
                    node,
                    routing_bbox,
                    node.parts,
                    global_routes,
                    switchboxes,
                    **options
                )

            # Now clean-up the wires and add junctions.
            _sch_progress(options, f"[schematic] cleanup_wires sheet={sheet} ...")
            node.cleanup_wires()
            _sch_progress(options, f"[schematic] add_junctions sheet={sheet}")
            node.add_junctions()
            _sch_progress(options, f"[schematic] 布线完成 sheet={sheet}")

            # If enabled, draw the global and detailed routing for debug purposes.
            if options.get("draw_switchbox_routing"):
                draw_routing(node, routing_bbox, node.parts, **options)

            # Remove any stuff leftover from this place & route run.
            node.rmv_routing_stuff()
            rmv_attr(node, ("_route_options",))

        except RoutingFailure:
            # Remove any stuff leftover from this place & route run.
            node.rmv_routing_stuff()
            rmv_attr(node, ("_route_options",))
            raise RoutingFailure
