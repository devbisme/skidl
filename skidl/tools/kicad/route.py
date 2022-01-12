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
    def __init__(self, part, track, b0, b1):
        self.part = part
        self.pins = []
        self.capacity = 0
        self.track = track
        self.b0 = b0
        self.b1 = b1
        self.adjacent = set()

    def split(self, b):
        new_face = Face(self.part, self.track, b, self.b1)
        self.b1 = b
        return new_face

def route(node):
    if not node.parts:
        return

    x_tracks = []
    y_tracks = []
    for part in node.parts:
        bbox = round(part.bbox.dot(part.tx))
        x_tracks.append(bbox.min.x)
        x_tracks.append(bbox.max.x)
        y_tracks.append(bbox.min.y)
        y_tracks.append(bbox.max.y)
    expansion = round(Vector(node.bbox.w, node.bbox.h) / 20)
    bbox = node.bbox.resize(expansion)
    x_tracks.append(bbox.min.x)
    x_tracks.append(bbox.max.x)
    y_tracks.append(bbox.min.y)
    y_tracks.append(bbox.max.y)
    x_tracks.sort()
    y_tracks.sort()

    # Create faces.
    # 1. Create faces for each part BBox.
    # 2. Create faces for surrounding BBox.
    # 3. Create horizontal faces from each part BBox corner to next vertical face.
    # 4. Create vertical faces from each BBox corner to next horizontal face.
    #        If blocking face is not a part face, then start a new face and continue.
    # 5. Go through faces looking for adjacencies.

    v_faces = [[] for _ in x_tracks]
    h_faces = [[] for _ in y_tracks]
    for part in node.parts:
        part_bbox = round(part.bbox.dot(part.tx))
        x0 = x_tracks.index(part_bbox.min.x)
        x1 = x_tracks.index(part_bbox.max.x)
        y0 = y_tracks.index(part_bbox.min.y)
        y1 = y_tracks.index(part_bbox.max.y)
        v_faces[x0].append(Face(part, x0, y0, y1))
        v_faces[x1].append(Face(part, x1, y0, y1))
        h_faces[y0].append(Face(part, y0, x0, x1))
        h_faces[y1].append(Face(part, y1, x0, x1))
    
    x0 = x_tracks.index(bbox.min.x)
    x1 = x_tracks.index(bbox.max.x)
    y0 = y_tracks.index(bbox.min.y)
    y1 = y_tracks.index(bbox.max.y)
    v_faces[x0].append(Face(None, x0, y0, y1))
    v_faces[x1].append(Face(None, x1, y0, y1))
    h_faces[y0].append(Face(None, y0, x0, x1))
    h_faces[y1].append(Face(None, y1, x0, x1))

    # Go through the horizontal faces and create new vertical faces.
    for h_faces_in_track in h_faces:
        for h_face in h_faces_in_track[:]:
            track = h_face.track

            done = False
            b0 = h_face.b0
            for x in range(b0, -1, -1):
                if done:
                    break
                for v_face in v_faces[x][:]:
                    if v_face.track == b0 and not (v_face.b0 < track < v_face.b1):
                        continue
                    if v_face.b0 <= track <= v_face.b1:
                        new_h_face = Face(None, track, x, b0)
                        h_faces_in_track.append(new_h_face)
                        b0 = x
                        if v_face.b0 < track < v_face.b1:
                            # Split the vertical face.
                            v_faces[x].append(v_face.split(track))
                        if v_face.part != None:
                            done = True
                            break

            done = False
            b1 = h_face.b1
            for x in range(b1, len(x_tracks)):
                if done:
                    break
                for v_face in v_faces[x][:]:
                    if v_face.track == b1 and not (v_face.b0 < track < v_face.b1):
                        continue
                    if v_face.b0 <= track <= v_face.b1:
                        new_h_face = Face(None, track, b1, x)
                        h_faces_in_track.append(new_h_face)
                        b1 = x
                        if v_face.b0 < track < v_face.b1:
                            # Split the vertical face.
                            v_faces[x].append(v_face.split(track))
                        if v_face.part != None:
                            done = True
                            break

    # Go through the vertical faces and create new horizontal faces.
    for v_faces_in_track in v_faces:
        for v_face in v_faces_in_track[:]:
            track = v_face.track

            done = False
            b0 = v_face.b0
            for y in range(b0, -1, -1):
                if done:
                    break
                for h_face in h_faces[y][:]:
                    if h_face.track == b0 and not (h_face.b0 < track < h_face.b1):
                        continue
                    if h_face.b0 <= track <= h_face.b1:
                        new_v_face = Face(None, track, y, b0)
                        v_faces_in_track.append(new_v_face)
                        b0 = y
                        if h_face.b0 < track < h_face.b1:
                            # Split the horizontal face.
                            h_faces[y].append(h_face.split(track))
                        if h_face.part != None:
                            done = True
                            break

            done = False
            b1 = v_face.b1
            for y in range(b1, len(y_tracks)):
                if done:
                    break
                for h_face in h_faces[y][:]:
                    if h_face.track == b1 and not (h_face.b0 < track < h_face.b1):
                        continue
                    if h_face.b0 <= track <= h_face.b1:
                        new_v_face = Face(None, track, b1, y)
                        v_faces_in_track.append(new_v_face)
                        b1 = y
                        if h_face.b0 < track < h_face.b1:
                            # Split the horizontal face.
                            h_faces[y].append(h_face.split(track))
                        if h_face.part != None:
                            done = True
                            break
            
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

    def draw_h_faces(faces, scr, tx):
        for face in faces:
            y = y_tracks[face.track]
            x0 = x_tracks[face.b0]
            x1 = x_tracks[face.b1]
            seg = Segment(Point(x0, y), Point(x1, y))
            draw_seg(seg, scr, tx)

    def draw_v_faces(faces, scr, tx):
        for face in faces:
            x = x_tracks[face.track]
            y0 = y_tracks[face.b0]
            y1 = y_tracks[face.b1]
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
    for faces in v_faces:
        draw_v_faces(faces, draw_scr, draw_tx)
    for faces in h_faces:
        draw_h_faces(faces, draw_scr, draw_tx)
    # draw_channels(faces, draw_scr, draw_tx)
    draw_parts(node.parts, draw_scr, draw_tx)
    draw_end()

    return
