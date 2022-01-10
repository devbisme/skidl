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
from collections import namedtuple

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
    def __init__(self, seg=None):
        self.adj = []
        self.pins = []
        self.capacity = 0
        self.seg = seg
        self.adjacent = set()

class Cell:
    def __init__(self):
        self.bbox = BBox()
        self.n = Face()
        self.s = Face()
        self.w = Face()
        self.e = Face()

    def add(self, obj):
        self.bbox = round(self.bbox.add(obj))

class PartCell(Cell):
    def __init__(self, part):
        super().__init__(self)
        self.part = part
        self.add(part.bbox.dot(part.tx))

def route(node):
    if not node.parts:
        return

    x_marks = []
    y_marks = []
    for part in node.parts:
        bbox = round(part.bbox.dot(part.tx))
        x_marks.append(bbox.min.x)
        x_marks.append(bbox.max.x)
        y_marks.append(bbox.min.y)
        y_marks.append(bbox.max.y)
    expansion = round(Vector(node.bbox.w, node.bbox.h) / 20)
    node.bbox.resize(expansion)
    bbox = node.bbox
    x_marks.append(bbox.min.x)
    x_marks.append(bbox.max.x)
    y_marks.append(bbox.min.y)
    y_marks.append(bbox.max.y)
    x_marks.sort()
    y_marks.sort()

    # Create faces.
    w = len(x_marks) - 1
    h = len(y_marks) - 1
    num_faces = w * (h+1) + (w+1) * h
    faces = [None for _ in range(num_faces)]

    def calc_face_indexes(x_idx, y_idx):
        n_idx = (h + 1) * x_idx + y_idx
        s_idx = n_idx + 1
        w_idx = w * (h + 1) + (w + 1) * y_idx + x_idx
        e_idx = w_idx + 1
        return n_idx, s_idx, e_idx, w_idx

    for x_idx, (x0, x1) in enumerate(zip(x_marks[:-1], x_marks[1:])):
        for y_idx, (y0, y1) in enumerate(zip(y_marks[:-1], y_marks[1:])):
            n_idx, s_idx, e_idx, w_idx = calc_face_indexes(x_idx, y_idx)
            n_seg = Segment(Point(x0, y0), Point(x1, y0))
            s_seg = Segment(Point(x0, y1), Point(x1, y1))
            w_seg = Segment(Point(x0, y0), Point(x0, y1))
            e_seg = Segment(Point(x1, y0), Point(x1, y1))
            face_indexes = [n_idx, s_idx, w_idx, e_idx]
            face_segs = [n_seg, s_seg, w_seg, e_seg]
            for i, seg in zip(face_indexes, face_segs):
                if not faces[i]:
                    faces[i] = Face(seg)
                faces[i].adjacent.update(set(face_indexes) - set((i,)))

    def rmv_adjacency(face1_idx, face2_idx):
        faces[face1_idx].adjacent.remove(face2_idx)
        faces[face2_idx].adjacent.remove(face1_idx)

    # Trim off adjacencies to faces internal to part bounding boxes.
    if True:
        for part in node.parts:
            part_bbox = round(part.bbox.dot(part.tx))
            x0_idx = x_marks.index(part_bbox.min.x)
            x1_idx = x_marks.index(part_bbox.max.x)
            y0_idx = y_marks.index(part_bbox.min.y)
            y1_idx = y_marks.index(part_bbox.max.y)
            for x_idx in range(x0_idx, x1_idx):
                for y_idx in range(y0_idx, y1_idx):
                    n_idx, s_idx, e_idx, w_idx = calc_face_indexes(x_idx, y_idx)
                    rmv_adjacency(n_idx, s_idx)
                    rmv_adjacency(n_idx, e_idx)
                    rmv_adjacency(n_idx, w_idx)
                    rmv_adjacency(s_idx, e_idx)
                    rmv_adjacency(s_idx, w_idx)
                    rmv_adjacency(e_idx, w_idx)
                
    # Store number of pins on exterior part faces.

    def draw_init(bbox):
        scr_bbox = BBox(Point(0,0), Point(2000,1500))

        border = max(bbox.w, bbox.h) / 20
        bbox.resize(Vector(border, border))
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

    def draw_faces(faces, scr, tx):
        for face in faces:
            draw_seg(face.seg, scr, tx)

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
    draw_faces(faces, draw_scr, draw_tx)
    draw_channels(faces, draw_scr, draw_tx)
    draw_parts(node.parts, draw_scr, draw_tx)
    draw_end()

    return
