# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""
Routing for schematics.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from builtins import range, zip
from enum import Enum, auto
from itertools import zip_longest, chain

from future import standard_library

from ...logger import active_logger
from ...part import Part
from ...utilities import *
from .common import *
from .geometry import *

standard_library.install_aliases()

###################################################################
# Routing schematic nets:
#
# Create a list of horizontal and vertical endpoints of the part BBoxes.
# Use the endpoints to divide the routing area into an array of rectangles.
# Create the faces of each rectangle, each face shared between adjacent rects.
# Capacity of each face is its length / wiring grid, except for faces
#    inside part boundaries which have 0 capacity.
# Assign part pins to each face that lies on a part BBox and zero the
#    capacity of that face.
# For each face, store the indices of adjacent faces except for those that
#    have zero capacity AND no part pins (i.e., faces internal to part boundaries).
# For each net:
#    For each pin on net:
#        Create list of cell faces and route cost occupied by pin.
#    While # face lists > 1:
#        For each frontier cell face:
#            Compute the cost to reach each adjacent, unvisited cell face.
#        Select the lowest-cost, unvisited cell face.
#        If the cell face has already been visited by another net pin,
#          then connect the pins by combining their face lists.
#
# Use net to find pins.
# Use pin to find part.
# Use part, pin to find cell.
# Use pin to find cell face.
# Route from cell face.
###################################################################

class Orientation(Enum):
    HORZ = auto()
    VERT = auto()
    LEFT = auto()
    RIGHT = auto()

HORZ = Orientation.HORZ
VERT = Orientation.VERT
LEFT = Orientation.LEFT
RIGHT = Orientation.RIGHT


class Boundary:
    pass


boundary = Boundary()


class Terminal:
    """Terminal on a Face from which a net is routed within a switchbox."""

    def __init__(self, net, face, coord):
        self.net = net
        self.face = face
        self.coord = coord


class Face:
    """A side of a rectangle bounding a routing switchbox."""

    def __init__(self, part, track, beg, end):
        self.part = set()
        if isinstance(part, set):
            self.part.update(part)
        elif part is not None:
            self.part.add(part)
        self.pins = []
        self.track = track
        if beg > end:
            beg, end = end, beg
        self.beg = beg
        self.end = end
        self.adjacent = set()
        self.create_terminals()
        self.set_capacity()

    def create_terminals(self):
        from .gen_schematic import GRID
        beg = (self.beg.coord + GRID//2 + GRID) // GRID * GRID
        end = self.end.coord - GRID//2
        self.terminals = [Terminal(None, self, coord) for coord in range(beg, end, GRID)]

    @property
    def connection_pts(self):
        return [terminal.coord for terminal in self.terminals]

    def set_capacity(self):
        if self.part:
            self.capacity = 0
        else:
            self.capacity = len(self.connection_pts)

    def add_adjacency(self, adj_face):
        """Make two faces adjacent to one another."""

        # Faces on the boundary can never accept wires so they are never
        # adjacent to any face.
        if boundary in list(self.part) + list(adj_face.part):
            return

        # If a face is an edge of a part, then it can never be adjacent to
        # another face on the same part or else wires might get routed through
        # the part bounding box.
        if not self.part.intersection(adj_face.part):
            self.adjacent.add(adj_face)
            adj_face.adjacent.add(self)

    def split(self, mid):
        """If a point is in the middle of a face, split it and return the remainder."""
        if self.beg < mid < self.end:
            new_face = Face(self.part, self.track, self.beg, mid)
            self.beg = mid
            self.create_terminals()
            return new_face
        return None

    def coincides_with(self, other_face):
        """Returns True if both faces have the same beginning and ending point on the same track."""
        return (self.beg, self.end) == (other_face.beg, other_face.end)

    def get_switchbox_faces(upper_face):
        """Get faces of switchbox.

        Args:
            upper_face (Face): The upper face of the switchbox.

        Raises:
            Exception: If this is a malformed switchbox.

        Returns:
            [list]: upper, right, lower, and left Faces of switchbox.
        """

        left_face = None
        left_track = upper_face.beg
        for face in left_track:
            if face.end.coord == upper_face.track.coord:
                left_face = face
                break

        right_face = None
        right_track = upper_face.end
        for face in right_track:
            if face.end.coord == upper_face.track.coord:
                right_face = face
                break

        if left_face.beg != right_face.beg:
            # This only happens when two parts are butted up against each other
            # to form a non-routable switchbox inside a part bounding box.
            raise Exception("Unroutable switchbox!")

        lower_face = None
        lower_track = left_face.beg
        for face in lower_track:
            if face.beg.coord == upper_face.beg.coord:
                lower_face = face
                break

        return upper_face, right_face, lower_face, left_face


class GlobalWire(list):
    """Global-routing wire connecting switchbox faces and terminals."""

    def __init__(self, *args, **kwargs):
        self.net = kwargs.pop("net")
        super().__init__(*args, **kwargs)


class Track(list):
    """A horizontal/vertical track holding one or more faces all having the same Y/X coordinate."""

    def __init__(self, *args, **kwargs):
        self.orientation = kwargs.pop("orientation", HORZ)
        self.coord = kwargs.pop("coord", 0)
        self.idx = kwargs.pop("idx")
        super().__init__(*args, **kwargs)
        self.splits = set()

    def __hash__(self):
        return self.idx

    def __lt__(self, track):
        return self.coord < track.coord

    def __gt__(self, track):
        return self.coord > track.coord

    def add_face(self, face):
        self.append(face)
        self.add_split(face.beg)
        self.add_split(face.end)

    def extend_faces(self, orthogonal_tracks):
        for h_face in self[:]:
            if not h_face.part:
                continue
            for dir in (LEFT, RIGHT):
                if dir == LEFT:
                    start = h_face.beg
                    search = orthogonal_tracks[start.idx :: -1]
                else:
                    start = h_face.end
                    search = orthogonal_tracks[start.idx :]

                blocked = False
                for ortho_track in search:
                    for ortho_face in ortho_track:
                        if ortho_face.beg < self < ortho_face.end:
                            ortho_track.add_split(self)
                            self.add_split(ortho_track)
                            if ortho_face.part:
                                self.add_face(
                                    Face(None, self, start, ortho_track)
                                )
                                blocked = True
                            break
                    if blocked:
                        break

    def add_split(self, track_idx):
        self.splits.add(track_idx)

    def split_faces(self):
        for split in self.splits:
            for face in self[:]:
                new_face = face.split(split)
                if new_face:
                    self.append(new_face)

    def combine_faces(self):
        for i, face in enumerate(self):
            for other_face in self[i + 1 :]:
                if face.coincides_with(other_face):
                    other_face.part.update(face.part)
                    face.beg = face.end
                    break
        for face in self[:]:
            if face.beg == face.end:
                self.remove(face)

    def add_adjacencies(self):
        for upper_face in self:

            try:
                upper_face, right_face, lower_face, left_face = upper_face.get_switchbox_faces() 
            except Exception:
                continue

            upper_face.add_adjacency(lower_face)
            left_face.add_adjacency(right_face)
            left_face.add_adjacency(upper_face)
            left_face.add_adjacency(lower_face)
            right_face.add_adjacency(upper_face)
            right_face.add_adjacency(lower_face)

def route_globally(net):
    """Route a net from face to face.

    Args:
        net (Net): The net to be routed.

    Returns:
        List: Sequence of faces the net travels through.
    """

    routed_wires = []

    net_route_cnt = 0
    for pin in net.pins:
        if hasattr(pin.face, "seed_pin"):
            pin.do_route = False  # Only route one pin per face.
        else:
            pin.face.seed_pin = pin
            pin.face.dist = 0
            pin.face.prev = pin.face # Indicates terminal pin.
            pin.frontier = set([pin.face])
            pin.visited = set()
            pin.do_route = True
            net_route_cnt += 1

    while net_route_cnt > 1:
        for pin in net.pins:
            if pin.do_route:

                try:
                    visit_face = min(pin.frontier, key=lambda face: face.dist)
                except ValueError:
                    print("No route found!")
                    pin.do_route = False
                    net_route_cnt -= 1
                    continue

                pin.frontier.remove(visit_face)
                pin.visited.add(visit_face)

                for next_face in visit_face.adjacent - pin.visited - pin.frontier:

                    if hasattr(next_face, "prev"):
                        # Found a connection with another pin on the net!
                        # Combine faces that have been visited and on the frontier.
                        # Turn off routing for one of the pins.
                        # Store sequence of faces connecting the two pins.
                        other_pin = next_face.seed_pin
                        pin.frontier.update(other_pin.frontier)
                        pin.visited.update(other_pin.visited)
                        other_pin.visited = set()
                        other_pin.frontier = set()
                        other_pin.do_route = False
                        net_route_cnt -= 1
                        def get_face_path(f):
                            path = [f,]
                            while f.prev is not f:
                                path.append(f.prev)
                                f = f.prev
                            return path
                        wire = GlobalWire(get_face_path(visit_face)[::-1] + get_face_path(next_face)[:], net=net)
                        for face in wire:
                            if face.capacity > 0:
                                face.capacity -= 1
                        routed_wires.append(wire)

                    elif next_face.capacity > 0:
                        pin.frontier.add(next_face)
                        next_face.seed_pin = pin
                        next_face.prev = visit_face
                        next_face.dist = visit_face.dist + 1

    for pin in net.pins:
        delattr(pin, "do_route")
        for face in pin.visited | pin.frontier:
            delattr(face, "dist")
            delattr(face, "prev")
            delattr(face, "seed_pin")
        delattr(pin, "frontier")
        delattr(pin, "visited")

    return routed_wires

def assign_switchbox_terminals(global_routes):
    """Assign global routes to terminals in switchbox faces."""

    for route in global_routes:
        for wire in route:
            for i, face in enumerate(wire[:]):
                if face.part:
                    for terminal in face.terminals:
                        if terminal.net == wire.net:
                            wire[i] = terminal
                            break
                    else:
                        raise Exception

    def find_to_terminal_idx(from_terminal, to_face):
        from_face = from_terminal.face
        if to_face.track in (from_face.beg, from_face.end):
            # Right-angle faces.
            # to_face is positioned left/below w.r.t. from_face.
            if to_face.beg == from_face.track:
                # to_face is oriented upward/rightward w.r.t. from_face.
                search_range = range(len(to_face.terminals))
            elif to_face.end == from_face.track:
                # to_face is oriented downward/leftward w.r.t. from_face.
                search_range = range(len(to_face.terminals)-1, -1, -1)
            else:
                raise Exception
        else:
            # Parallel faces.
            from_len = len(from_face.terminals)
            from_idx = from_face.terminals.index(from_terminal)
            search_range = chain(*zip_longest(range(from_idx, -1, -1), range(from_idx+1, from_len)))

        for idx in search_range:
            if idx is not None:
                if to_face.terminals[idx].net in (None, from_terminal.net):
                    return idx
        raise Exception

    for route in global_routes:
        done = False
        while not done:
            done = True
            for wire in route:
                for i in range(0, len(wire)-1):
                    face1, face2 = wire[i], wire[i+1]
                    if isinstance(face1, Terminal) and isinstance(face2, Terminal):
                        continue
                    if isinstance(face1, Face) and isinstance(face2, Terminal):
                        terminal_idx = find_to_terminal_idx(face2, face1)
                        terminal = face1.terminals[terminal_idx]
                        terminal.net = wire.net
                        wire[i] = terminal
                        done = False
                        continue
                    if isinstance(face1, Terminal) and isinstance(face2, Face):
                        terminal_idx = find_to_terminal_idx(face1, face2)
                        terminal = face2.terminals[terminal_idx]
                        terminal.net = wire.net
                        wire[i+1] = terminal
                        done = False
                        continue
                    if isinstance(face1, Face) and isinstance(face2, Face):
                        continue

                    raise Exception

def rank_net(net):
    """Rank net based on W/H of bounding box of pins and the # of pins."""
    bbox = BBox()
    for pin in net.pins:
        bbox.add(pin.pt)
    return (bbox.w + bbox.h, len(net.pins))

def fix_net_switchbox_terminals():
    pass

def route_switchbox(lower_face):
    pass
    # Get switchbox sides.
    # Greedy route.


def route(node):
    """Route the wires between part pins in the node.

    Args:
        node (Node): Hierarchical node containing the parts to be connected.

    Returns:
        None

    Note:
        1. Divide the bounding box surrounding the parts into switchboxes.
        2. Do global routing of nets through sequences of switchboxes.
        3. Do detailed routing within each switchbox.
    """

    # Exit if no parts to route.
    if not node.parts:
        return

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
        return

    # Find the coords of the horiz/vert tracks that will hold the H/V faces of the routing switchboxes.
    v_track_coord = []
    h_track_coord = []

    # The upper/lower/left/right of each part's bounding box define the H/V tracks.
    for part in node.parts:
        bbox = round(part.bbox.dot(part.tx))
        v_track_coord.append(bbox.min.x)
        v_track_coord.append(bbox.max.x)
        h_track_coord.append(bbox.min.y)
        h_track_coord.append(bbox.max.y)

    # Create delimiting tracks for the routing area from the slightly-expanded total bounding box of the parts.
    expansion = Vector(node.bbox.w, node.bbox.h) / 20
    routing_bbox = round(node.bbox.resize(expansion))
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
        Track(orientation=VERT, idx=idx, coord=coord)
        for idx, coord in enumerate(v_track_coord)
    ]
    h_tracks = [
        Track(orientation=HORZ, idx=idx, coord=coord)
        for idx, coord in enumerate(h_track_coord)
    ]

    def bbox_to_faces(part, bbox):
        left_track = v_tracks[v_track_coord.index(bbox.min.x)]
        right_track = v_tracks[v_track_coord.index(bbox.max.x)]
        bottom_track = h_tracks[h_track_coord.index(bbox.min.y)]
        top_track = h_tracks[h_track_coord.index(bbox.max.y)]
        left_track.add_face(Face(part, left_track, bottom_track, top_track))
        right_track.add_face(Face(part, right_track, bottom_track, top_track))
        bottom_track.add_face(Face(part, bottom_track, left_track, right_track))
        top_track.add_face(Face(part, top_track, left_track, right_track))
        if isinstance(part,Part):
            part.left_track = left_track
            part.right_track = right_track
            part.top_track = top_track
            part.bottom_track = bottom_track


    # Add routing box faces for each side of a part's bounding box.
    for part in node.parts:
        part_bbox = round(part.bbox.dot(part.tx))
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
        track.combine_faces()

    # Add adjacencies between faces that define routing paths within switchboxes.
    for h_track in h_tracks[1:]:
        h_track.add_adjacencies()

    # Associate pins with faces.
    from .gen_schematic import calc_pin_dir
    for net in internal_nets:
        for pin in net.pins:
            part = pin.part
            pt = pin.pt.dot(part.tx)
            dir = calc_pin_dir(pin)
            pin_track = {
                "U": part.bottom_track,
                "D": part.top_track,
                "L": part.right_track,
                "R": part.left_track,
            }[dir]
            coord = {
                "U": pt.x,
                "D": pt.x,
                "L": pt.y,
                "R": pt.y,
            }[dir]
            for face in pin_track:
                if face.beg.coord <= coord <= face.end.coord:
                    assert pin.part in face.part
                    pin.face = face
                    face.pins.append(pin)
                    connection_pts = face.connection_pts
                    idx = connection_pts.index(coord)
                    face.terminals[idx].net = net
                    break

    # Set routing capacity of faces.
    for track in h_tracks + v_tracks:
        for face in track:
            face.set_capacity()

    # Do global routing of nets internal to the node.
    internal_nets.sort(key=rank_net)
    global_routes = [route_globally(net) for net in internal_nets]
    assign_switchbox_terminals(global_routes)


    import pygame
    import pygame.freetype

    def draw_init(bbox):
        scr_bbox = BBox(Point(0, 0), Point(2000, 1500))

        border = max(bbox.w, bbox.h) / 20
        bbox = bbox.resize(Vector(border, border))
        bbox = round(bbox)

        scale = min(scr_bbox.w / bbox.w, scr_bbox.h / bbox.h)

        tx = Tx(a=scale, d=scale).dot(Tx(d=-1))
        new_bbox = bbox.dot(tx)
        move = scr_bbox.ctr - new_bbox.ctr
        tx = tx.dot(Tx(dx=move.x, dy=move.y))

        pygame.init()
        scr = pygame.display.set_mode((scr_bbox.w, scr_bbox.h))

        font = pygame.freetype.SysFont("consolas", 24)

        scr.fill((255, 255, 255))

        return scr, tx, font

    def draw_seg(seg, scr, tx, color=(100, 100, 100), line_thickness=1, dot_thickness=3):
        seg = seg.dot(tx)
        pygame.draw.line(
            scr, color, (seg.p1.x, seg.p1.y), (seg.p2.x, seg.p2.y), width=line_thickness
        )
        pygame.draw.circle(scr, color, (seg.p1.x, seg.p1.y), dot_thickness)
        pygame.draw.circle(scr, color, (seg.p2.x, seg.p2.y), dot_thickness)

    def face_seg(face):
        track = face.track
        orientation = track.orientation
        if orientation == HORZ:
            p1 = Point(face.beg.coord, track.coord)
            p2 = Point(face.end.coord, track.coord)
        else:
            p1 = Point(track.coord, face.beg.coord)
            p2 = Point(track.coord, face.end.coord)
        return Segment(p1, p2)

    def draw_text(txt, pt, scr, tx, font, color=(100,100,100)):
        pt = pt.dot(tx)
        font.render_to(scr, (pt.x, pt.y), txt, color)

    def draw_face(face, color, line_width, dot_width, scr, tx, font):
        if len(face.part) < 0:
            return
        seg = face_seg(face)
        draw_seg(face_seg(face), scr, tx, color, line_width, dot_width)
        mid_pt = (seg.p1 + seg.p2) / 2
        draw_text(str(face.capacity), mid_pt, scr, tx, font, color)

    def draw_track(track, scr, tx, font):
        face_colors = [(255, 0, 0), (0, 64, 0), (0, 0, 255), (0, 0, 0)]
        for face in track:
            if len(face.part) < 0:
                continue
            face_color = face_colors[len(face.part)]
            draw_face(face, face_color, 3, 4, scr, tx, font)

    def draw_channels(track, scr, tx):
        for face in track:
            seg = face_seg(face)
            p1 = (seg.p1 + seg.p2) / 2
            for adj_face in face.adjacent:
                seg = face_seg(adj_face)
                p2 = (seg.p1 + seg.p2) / 2
                draw_seg(Segment(p1, p2), scr, tx, (128, 0, 128), 1, 3)

    def draw_box(bbox, scr, tx):
        bbox = bbox.dot(tx)
        corners = (
            bbox.min,
            Point(bbox.min.x, bbox.max.y),
            bbox.max,
            Point(bbox.max.x, bbox.min.y),
        )
        corners = (
            (bbox.min.x, bbox.min.y),
            (bbox.min.x, bbox.max.y),
            (bbox.max.x, bbox.max.y),
            (bbox.max.x, bbox.min.y),
        )
        pygame.draw.polygon(scr, (192, 255, 192), corners, 0)

    def draw_parts(parts, scr, tx):
        for part in parts:
            draw_box(part.bbox.dot(part.tx), scr, tx)

    def draw_pin(pin, scr, tx):
        pt = pin.pt.dot(pin.part.tx)
        track = pin.face.track
        pt = {
            HORZ: Point(pt.x, track.coord),
            VERT: Point(track.coord, pt.y),
        }[track.orientation]
        pt = pt.dot(tx)
        sz = 5
        corners = (
            (pt.x, pt.y+sz),
            (pt.x+sz, pt.y),
            (pt.x, pt.y-sz),
            (pt.x-sz, pt.y),
        )
        pygame.draw.polygon(scr, (0,0,0), corners, 0)
        # draw_face(pin.face, (0,0,0), 4, 4, scr, tx)

    def draw_wire(wire, scr, tx):
        for pin in wire.net.pins:
            draw_pin(pin, scr, tx)

        def terminal_pt(terminal):
            track = terminal.face.track
            if track.orientation == HORZ:
                return Point(terminal.coord, track.coord)
            else:
                return Point(track.coord, terminal.coord)

        face_to_face = zip(wire[:-1], wire[1:])
        for terminal1, terminal2 in face_to_face:
            p1 = terminal_pt(terminal1)
            p2 = terminal_pt(terminal2)
            draw_seg(Segment(p1, p2), scr, tx, (0,0,0), 2, 0)

    def draw_end():
        pygame.display.flip()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()

    draw_scr, draw_tx, font = draw_init(routing_bbox)
    draw_parts(node.parts, draw_scr, draw_tx)
    for track in h_tracks + v_tracks:
        draw_track(track, draw_scr, draw_tx, font)
    # for track in h_tracks + v_tracks:
    #     draw_channels(track, draw_scr, draw_tx)
    for route in global_routes:
        for wire in route:
            draw_wire(wire, draw_scr, draw_tx)
    draw_end()

    return
