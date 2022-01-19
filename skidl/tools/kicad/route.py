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
from collections import defaultdict

from future import standard_library

from ...logger import active_logger
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

import pygame
from pygame.locals import K_ESCAPE

HORZ, VERT, LEFT, RIGHT = range(4)


class Boundary:
    pass


boundary = Boundary()


class Face:
    """A side of a rectangle bounding a routing switchbox."""

    def __init__(self, part, track, beg, end):
        self.part = set()
        if isinstance(part, set):
            self.part.update(part)
        elif part is not None:
            self.part.add(part)
        self.pins = []
        self.capacity = 0
        self.track = track
        if beg > end:
            beg, end = end, beg
        self.beg = beg
        self.end = end
        self.adjacent = set()

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
            return new_face
        return None

    def coincides_with(self, other_face):
        """Returns True if both faces have the same beginning and ending point on the same track."""
        return (self.beg, self.end) == (other_face.beg, other_face.end)


class Track(list):
    """A horizontal/vertical track holding one or more faces all having the same Y/X coordinate."""

    def __init__(self, *args, **kwargs):
        self.orientation = kwargs.pop("orientation", HORZ)
        self.coord = kwargs.pop("coord", 0)
        self.idx = kwargs.pop("idx")
        super().__init__(self, *args, **kwargs)
        self.splits = set()

    def __hash__(self):
        return self.idx

    def __lt__(self, track):
        return self.coord < track.coord

    def __gt__(self, track):
        return self.coord > track.coord

    def add_split(self, track_idx):
        self.splits.add(track_idx)

    def add_face(self, face):
        self.append(face)
        self.add_split(face.beg)
        self.add_split(face.end)

    def split_faces(self):
        for split in self.splits:
            for face in self[:]:
                new_face = face.split(split)
                if new_face:
                    self.append(new_face)

    def resolve_faces(self):
        for i, face in enumerate(self):
            for other_face in self[i + 1 :]:
                if face.coincides_with(other_face):
                    other_face.part.update(face.part)
                    face.beg = face.end
                    break
        for face in self[:]:
            if face.beg == face.end:
                self.remove(face)


def route(node):
    """Route the wires between part pins in the node.

    Args:
        node (Node): Hierarchical node containing the parts to be connected.

    Returns:
        None

    Note:
        1. Divide the bounding box surrounding the parts into switchboxes.
        2. Do coarse routing of nets through sequences of switchboxes.
        3. Do detailed routing within each switchbox.
    """

    if not node.parts:
        return

    # Find the coords of the horiz/vert tracks that will hold the H/V faces of the routing switchboxes.
    v_track_coord = []
    h_track_coord = []

    for part in node.parts:
        # The upper/lower/left/right of each part's bounding box define the H/V tracks.
        bbox = round(part.bbox.dot(part.tx))
        v_track_coord.append(bbox.min.x)
        v_track_coord.append(bbox.max.x)
        h_track_coord.append(bbox.min.y)
        h_track_coord.append(bbox.max.y)

    # Create delimiting tracks for the routing area from the slightly-expanded total bounding box of the parts.
    expansion = round(Vector(node.bbox.w, node.bbox.h) / 20)
    bbox = node.bbox.resize(expansion)
    v_track_coord.append(bbox.min.x)
    v_track_coord.append(bbox.max.x)
    h_track_coord.append(bbox.min.y)
    h_track_coord.append(bbox.max.y)

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


    # Add routing box faces for each side of a part's bounding box.
    for part in node.parts:
        part_bbox = round(part.bbox.dot(part.tx))
        bbox_to_faces(part, part_bbox)

    # Add routing box faces for each side of the expanded bounding box surrounding all parts.
    bbox_to_faces(boundary, bbox)

    def extend_faces(h_tracks, v_tracks):
        for h_track in h_tracks:
            h_tr_idx = h_track.idx
            for h_face in h_track[:]:
                if not h_face.part:
                    continue
                for dir in (LEFT, RIGHT):
                    if dir == LEFT:
                        start = h_face.beg
                        search = v_tracks[start.idx :: -1]
                    else:
                        start = h_face.end
                        search = v_tracks[start.idx :]

                    blocked = False
                    for v_track in search:
                        for v_face in v_track:
                            if v_face.beg < h_track < v_face.end:
                                v_track.add_split(h_track)
                                h_track.add_split(v_track)
                                if v_face.part:
                                    h_track.add_face(
                                        Face(None, h_track, start, v_track)
                                    )
                                    blocked = True
                                break
                        if blocked:
                            break

    # Generate the horizontal faces in each horizontal track. Then generate the vertical faces.
    extend_faces(h_tracks, v_tracks)
    extend_faces(v_tracks, h_tracks)

    for track in h_tracks + v_tracks:
        track.split_faces()
        track.resolve_faces()

    def generate_adjacencies(h_tracks, v_tracks):
        for h_track in h_tracks[1:]:
            for upper_face in h_track:

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
                    continue

                lower_face = None
                lower_track = left_face.beg
                for face in lower_track:
                    if face.beg.coord == upper_face.beg.coord:
                        lower_face = face
                        break

                upper_face.add_adjacency(lower_face)
                left_face.add_adjacency(right_face)
                left_face.add_adjacency(upper_face)
                left_face.add_adjacency(lower_face)
                right_face.add_adjacency(upper_face)
                right_face.add_adjacency(lower_face)

    generate_adjacencies(h_tracks, v_tracks)

    # Store number of pins on exterior part faces.

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

        scr.fill((255, 255, 255))

        return scr, tx

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

    def draw_track(track, scr, tx):
        face_colors = [(255, 0, 0), (0, 64, 0), (0, 0, 255), (0, 0, 0)]
        for face in track:
            if len(face.part) < 0:
                continue
            face_color = face_colors[len(face.part)]
            draw_seg(face_seg(face), scr, tx, face_color, 3, 4)

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

    def draw_end():
        pygame.display.flip()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()

    draw_scr, draw_tx = draw_init(bbox)
    draw_parts(node.parts, draw_scr, draw_tx)
    for track in h_tracks + v_tracks:
        draw_track(track, draw_scr, draw_tx)
    for track in h_tracks + v_tracks:
        draw_channels(track, draw_scr, draw_tx)
    draw_end()

    return
