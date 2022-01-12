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

class Face:
    def __init__(self, part, track, beg, end):
        self.part = part
        self.pins = []
        self.capacity = 0
        self.track = track
        if beg > end:
            beg, end = end, beg
        self.beg = beg
        self.end = end
        self.adjacent = set()

    def split(self, mid):
        new_face = Face(self.part, self.track, mid, self.end)
        self.end = mid
        return new_face

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
    v_tracks = [[] for _ in v_track_coord]
    h_tracks = [[] for _ in h_track_coord]

    # Add routing box faces for each side of a part's bounding box.
    for part in node.parts:
        part_bbox = round(part.bbox.dot(part.tx))
        left = v_track_coord.index(part_bbox.min.x)
        right = v_track_coord.index(part_bbox.max.x)
        bottom = h_track_coord.index(part_bbox.min.y)
        top = h_track_coord.index(part_bbox.max.y)
        v_tracks[left].append(Face(part, left, bottom, top))
        v_tracks[right].append(Face(part, right, bottom, top))
        h_tracks[bottom].append(Face(part, bottom, left, right))
        h_tracks[top].append(Face(part, top, left, right))
    
    # Add routing box faces for each side of the expanded bounding box surrounding all parts.
    left = v_track_coord.index(bbox.min.x)
    right = v_track_coord.index(bbox.max.x)
    bottom = h_track_coord.index(bbox.min.y)
    top = h_track_coord.index(bbox.max.y)
    v_tracks[left].append(Face(None, left, bottom, top))
    v_tracks[right].append(Face(None, right, bottom, top))
    h_tracks[bottom].append(Face(None, bottom, left, right))
    h_tracks[top].append(Face(None, top, left, right))

    def generate_faces(h_tracks, v_tracks):
        for h_faces in h_tracks:
            for h_face in h_faces[:]:
                h_track = h_face.track
                for dir in ("L", "R"):
                    if dir == "L":
                        start = h_face.beg
                        rng = range(start, -1, -1)
                    else:
                        start = h_face.end
                        rng = range(start, len(v_tracks))

                    done = False
                    for v_track in rng:
                        for v_face in v_tracks[v_track][:]:
                            split_v_face = v_face.beg < h_track < v_face.end
                            if v_face.track == start and not split_v_face:
                                continue
                            if v_face.beg <= h_track <= v_face.end:
                                new_h_face = Face(None, h_track, start, v_track)
                                h_faces.append(new_h_face)
                                start = v_track
                                if split_v_face:
                                    # Split vertical face.
                                    v_tracks[v_track].append(v_face.split(h_track))
                                if v_face.part != None:
                                    done = True
                                    break
                        if done:
                            break

    # Generate the horizontal faces in each horizontal track. Then generate the vertical faces.
    generate_faces(h_tracks, v_tracks)
    generate_faces(v_tracks, h_tracks)

    # Store number of pins on exterior part faces.

    def draw_init(bbox):
        scr_bbox = BBox(Point(0,0), Point(2000,1500))

        border = max(bbox.w, bbox.h) / 20
        bbox = bbox.resize(Vector(border, border))
        bbox = round(bbox)

        scale = min(scr_bbox.w / bbox.w, scr_bbox.h / bbox.h)

        tx = Tx(a=scale, d=scale).dot(Tx(d = -1))
        new_bbox = bbox.dot(tx)
        move = scr_bbox.ctr - new_bbox.ctr
        tx = tx.dot(Tx(dx = move.x, dy = move.y))

        pygame.init()
        scr = pygame.display.set_mode((scr_bbox.w, scr_bbox.h))

        return scr, tx

    def draw_seg(seg, scr, tx, color=(100,100,100), thickness=1):
        seg = seg.dot(tx)
        pygame.draw.line(scr, color, (seg.p1.x, seg.p1.y), (seg.p2.x, seg.p2.y), width=thickness)
        pygame.draw.circle(scr, color, (seg.p1.x, seg.p1.y), 5)
        pygame.draw.circle(scr, color, (seg.p2.x, seg.p2.y), 5)

    def draw_h_tracks(faces, scr, tx):
        for face in faces:
            y = h_track_coord[face.track]
            x0 = v_track_coord[face.beg]
            x1 = v_track_coord[face.end]
            seg = Segment(Point(x0, y), Point(x1, y))
            draw_seg(seg, scr, tx)

    def draw_v_tracks(faces, scr, tx):
        for face in faces:
            x = v_track_coord[face.track]
            y0 = h_track_coord[face.beg]
            y1 = h_track_coord[face.end]
            seg = Segment(Point(x, y0), Point(x, y1))
            draw_seg(seg, scr, tx)

    def draw_channels(faces, scr, tx):
        for face in faces:
            p1 = (face.seg.p1 + face.seg.p2) / 2
            adjacent_face_indexes = face.adjacent
            for adj_face_idx in adjacent_face_indexes:
                adj_face = faces[adj_face_idx]
                if not adj_face:
                    continue
                p2 = (adj_face.seg.p1 + adj_face.seg.p2) / 2
                draw_seg(Segment(p1,p2), scr, tx, color=(128,0,128), thickness=1)

    def draw_box(bbox, scr, tx):
        bbox = bbox.dot(tx)
        corners = (bbox.min, Point(bbox.min.x, bbox.max.y), bbox.max, Point(bbox.max.x, bbox.min.y))
        corners = ((bbox.min.x, bbox.min.y), (bbox.min.x, bbox.max.y), (bbox.max.x, bbox.max.y), (bbox.max.x, bbox.min.y))
        pygame.draw.polygon(scr, (0,192,0), corners, 2)

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
    for faces in v_tracks:
        draw_v_tracks(faces, draw_scr, draw_tx)
    for faces in h_tracks:
        draw_h_tracks(faces, draw_scr, draw_tx)
    # draw_channels(faces, draw_scr, draw_tx)
    draw_parts(node.parts, draw_scr, draw_tx)
    draw_end()

    return
