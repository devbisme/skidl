# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2018 by XESS Corp.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Class for painting a PCB footprint.
"""

from __future__ import print_function

import math
from collections import defaultdict, namedtuple

import wx

# Prescaling constant increases footprint dimensions
# so they won't lose precision when converted to integers
# during painting operations.
PRESCALE = 100000

MIN_SIZE = 1e-7

# KiCad layer colors.
FP_BCK_COLOUR = wx.Colour(0, 0, 0)
FCU_COLOUR = wx.Colour(128, 0, 0)
BCU_COLOUR = wx.Colour(20, 81, 132)
FPASTE_COLOUR = wx.Colour(132, 0, 0)
BPASTE_COLOUR = wx.Colour(0, 194, 194)
FSILK_COLOUR = wx.Colour(0, 132, 132)
BSILK_COLOUR = wx.Colour(132, 0, 132)
FMASK_COLOUR = wx.Colour(132, 0, 132)
BMASK_COLOUR = wx.Colour(132, 132, 0)
FCRTYD_COLOUR = wx.Colour(132, 132, 132)
BCRTYD_COLOUR = wx.Colour(194, 194, 0)
FFAB_COLOUR = wx.Colour(194, 194, 0)
BFAB_COLOUR = wx.Colour(132, 0, 0)
DRILL_COLOUR = FP_BCK_COLOUR  # Same as background color so drills look like holes.

# KiCad layer brushes.
FCU_BRUSH = wx.BRUSHSTYLE_SOLID
BCU_BRUSH = wx.BRUSHSTYLE_SOLID
FFAB_BRUSH = wx.BRUSHSTYLE_SOLID
BFAB_BRUSH = wx.BRUSHSTYLE_SOLID
FCRTYD_BRUSH = wx.BRUSHSTYLE_SOLID
BCRTYD_BRUSH = wx.BRUSHSTYLE_SOLID
FSILK_BRUSH = wx.BRUSHSTYLE_SOLID
BSILK_BRUSH = wx.BRUSHSTYLE_SOLID
DRILL_BRUSH = wx.BRUSHSTYLE_SOLID

layer_style = {
            "B.Cu": (BCU_COLOUR, BCU_BRUSH),
            "F.Cu": (FCU_COLOUR, FCU_BRUSH),
            "F&B.Cu": (FCU_COLOUR, FCU_BRUSH),
            "*.Cu": (FCU_COLOUR, FCU_BRUSH),
            "B.Fab": (BFAB_COLOUR, BFAB_BRUSH),
            "F.Fab": (FFAB_COLOUR, FFAB_BRUSH),
            "F&B.Fab": (FFAB_COLOUR, FFAB_BRUSH),
            "*.Fab": (FFAB_COLOUR, FFAB_BRUSH),
            "B.CrtYd": (BCRTYD_COLOUR, BCRTYD_BRUSH),
            "F.CrtYd": (FCRTYD_COLOUR, FCRTYD_BRUSH),
            "F&B.CrtYd": (FCRTYD_COLOUR, FCRTYD_BRUSH),
            "*.CrtYd": (FCRTYD_COLOUR, FCRTYD_BRUSH),
            "B.SilkS": (BSILK_COLOUR, BSILK_BRUSH),
            "F.SilkS": (FSILK_COLOUR, FSILK_BRUSH),
            "F&B.SilkS": (FSILK_COLOUR, FSILK_BRUSH),
            "*.SilkS": (FSILK_COLOUR, FSILK_BRUSH),
            "Drill": (DRILL_COLOUR, DRILL_BRUSH),
}

# Named tuple for storing a bounding box.
BBox = namedtuple("BBox", "x0 y0 x1 y1")


class Layer(object):
    """Footprint PCB layer."""

    def __init__(self, colour=wx.Colour(63, 63, 63), style=wx.BRUSHSTYLE_SOLID):
        self.set_fill(colour, style)
        self.clear()  # Creates all the empty graphic element lists.

    def set_fill(self, colour, style=wx.BRUSHSTYLE_SOLID):
        self.colour = colour
        if isinstance(colour, wx.Colour):
            self.brush = wx.Brush(colour, style)
        elif isinstance(colour, wx.Bitmap):
            self.brush = wx.Brush(colour)
        else:
            raise NotImplementedError

    def clear(self):
        self.pad_polygons = []
        self.pad_circles = []
        self.lines = []
        self.circles = []

    def add_pad_polygon(self, polygon):
        self.pad_polygons.append(polygon)

    def add_pad_circle(self, circle):
        self.pad_circles.append(circle)

    def add_line(self, line):
        self.lines.append(line)

    def add_circle(self, circle):
        self.circles.append(circle)

    def paint(self, dc):
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), style=wx.PENSTYLE_TRANSPARENT))
        dc.SetBrush(self.brush)
        dc.DrawPolygonList(self.pad_polygons)
        for pad_circle in self.pad_circles:
            circ = list(pad_circle)[:]
            circ[2] = max(circ[2], 2)  # no circle gets painted with radius<2.
            dc.DrawCircle(*circ)
        pen = wx.Pen(self.colour)
        for line in self.lines:
            pen.SetWidth(max(line[0], 1))
            dc.SetPen(pen)
            dc.DrawLine(*line[1:])
        for circle in self.circles:
            pen.SetWidth(max(circle[0], 1))
            dc.SetPen(pen)
            circ = list(circle[1:])
            circ[2] = max(circ[2], 2)  # no circle gets painted with radius<2.
            dc.DrawCircle(*circ)


class Layers(defaultdict):
    """Collection of footprint layers."""

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(Layer)

    def clear(self):
        for layer in self.values():
            layer.clear()

    def paint(self, dc):
        for layer in self.values():
            layer.paint(dc)


class FootprintPainter(object):
    """Footprint painted within a device context."""

    def __init__(self, fp, dc):
        self.footprint = fp  # Set footprint data.
        self.bbox = None  # Clear the bbox so it will be calculated.
        self.paint(dc)  # This will calculate the footprint bbox.

    @staticmethod
    def rect_pts(cx, cy, w, h, rot, tm):
        cx, cy, w, h = [m * PRESCALE for m in [cx, cy, w, h]]
        h2, w2 = h / 2, w / 2
        pts = ((-w2, -h2), (-w2, h2), (w2, h2), (w2, -h2))
        tmp_tm = wx.AffineMatrix2D(tm)
        tmp_tm.Translate(cx, cy)
        tmp_tm.Rotate(rot * math.pi / 180)
        return [list(tmp_tm.TransformPoint(pt)) for pt in pts]

    @staticmethod
    def trapezoid_pts(cx, cy, w, h, dw, dh, rot, tm):
        cx, cy, w, h, dw, dh = [m * PRESCALE for m in [cx, cy, w, h, dw, dh]]
        h2, w2, dw2, dh2 = h / 2, w / 2, dw / 2, dh / 2
        pts = (
            (-w2 + dw2, -h2 - dh2),
            (-w2 - dw2, h2 + dh2),
            (w2 + dw2, h2 - dh2),
            (w2 - dw2, -h2 + dh2),
        )
        tmp_tm = wx.AffineMatrix2D(tm)
        tmp_tm.Translate(cx, cy)
        tmp_tm.Rotate(rot * math.pi / 180)
        return [list(tmp_tm.TransformPoint(pt)) for pt in pts]

    @staticmethod
    def circle_pts(cx, cy, r, tm):
        cx, cy, r = [m * PRESCALE for m in [cx, cy, r]]
        cx, cy = tm.TransformPoint(cx, cy)
        r, _ = tm.TransformDistance(r, 0)
        return (cx, cy, r)

    @staticmethod
    def line_pts(w, x0, y0, x1, y1, tm):
        w, x0, y0, x1, y1 = [m * PRESCALE for m in [w, x0, y0, x1, y1]]
        w, _ = tm.TransformDistance(w, 0)
        x0, y0 = tm.TransformPoint(x0, y0)
        x1, y1 = tm.TransformPoint(x1, y1)
        return (w, x0, y0, x1, y1)

    @staticmethod
    def roundrect_pts(cx, cy, w, h, r, rot, tm):
        # Two overlapped rectangles with corners cut out.
        rects = []
        rects.append(FootprintPainter.rect_pts(cx, cy, w, h - 2 * r, rot, tm))
        rects.append(FootprintPainter.rect_pts(cx, cy, w - 2 * r, h, rot, tm))

        # Four circles to fill-in corners.
        circles = []
        # Matrix for rotating circle centers and translating by pad center.
        tmp_tm = wx.AffineMatrix2D()
        tmp_tm.Translate(cx, cy)
        tmp_tm.Rotate(rot * math.pi / 180)
        # Circle at NE corner cutout.
        ccx, ccy = tmp_tm.TransformPoint(w / 2 - r, h / 2 - r)
        circles.append(FootprintPainter.circle_pts(ccx, ccy, r, tm))
        # Circle at NW corner cutout.
        ccx, ccy = tmp_tm.TransformPoint(-w / 2 + r, h / 2 - r)
        circles.append(FootprintPainter.circle_pts(ccx, ccy, r, tm))
        # Circle at SE corner cutout.
        ccx, ccy = tmp_tm.TransformPoint(w / 2 - r, -h / 2 + r)
        circles.append(FootprintPainter.circle_pts(ccx, ccy, r, tm))
        # Circle at SW corner cutout.
        ccx, ccy = tmp_tm.TransformPoint(-w / 2 + r, -h / 2 + r)
        circles.append(FootprintPainter.circle_pts(ccx, ccy, r, tm))
        return rects, circles

    @staticmethod
    def mk_bmp(w, h, colour, pctg):
        sz = len(colour)
        n = w * h * sz
        buff = bytearray(n)
        acc = 0
        for i in range(0, n, sz):
            acc += pctg
            if acc >= 1:
                buff[i : i + sz] = colour
                acc -= 1
        if sz == 4:
            bmp = wx.Bitmap.FromBufferRGBA(w, h, buff)
        elif sz == 3:
            bmp = wx.Bitmap.FromBuffer(w, h, buff)
        else:
            raise NotImplementedError
        bmp_mask = wx.Mask(bmp, wx.Colour(0, 0, 0))
        bmp.SetMask(bmp_mask)
        return bmp

    def paint(self, dc, paint_actual_size=False):
        bbox = self.bbox
        if bbox:
            # The bbox for the footprint exists, so set the
            # scaling and translation for painting it within the DC.
            panel_w, panel_h = dc.GetSize()
            if paint_actual_size:
                scale_x = dc.GetPPI().GetWidth() * 1.0 / (25.4 * PRESCALE)
                scale_y = dc.GetPPI().GetHeight() * 1.0 / (25.4 * PRESCALE)
            else:
                scale_x = panel_w / (bbox.x1 - bbox.x0)
                scale_y = panel_h / (bbox.y1 - bbox.y0)
            scale = min(scale_x, scale_y)

            # Compute translation to place footprint center at center of panel.
            bbox_cx, bbox_cy = (bbox.x1 + bbox.x0) / 2, (bbox.y1 + bbox.y0) / 2
            panel_cx, panel_cy = (panel_w / 2) / scale, (panel_h / 2) / scale
            tx, ty = panel_cx - bbox_cx, panel_cy - bbox_cy

            # Transformation matrices (TMs) operate opposite of expected:
            # the first scale/trans operation you add is the last operation
            # that's applied to a point.
            tm = wx.AffineMatrix2D()  # Start with identity matrix.
            tm.Scale(scale, scale)  # Apply scaling from real to screen dimensions.
            tm.Translate(tx, ty)
        else:
            # No bbox, so this must be first time the footprint is being painted.
            # Therefore, paint it without scaling to determine the physical dimensions.
            # This will be used later to scale it to the panel display.
            tm = wx.AffineMatrix2D()  # Identity matrix so no scaling.

        layers = Layers()
        dc.SetBackground(wx.Brush(FP_BCK_COLOUR))
        dc.Clear()
        fp = self.footprint

        for pad in fp.pads:
            attr = pad.attributes

            # Process the pad.
            w, h = (attr["size"] + [0])[0:2]
            cx, cy, rot = (attr["at"] + [0])[0:3]
            rot = -rot

            # Apply the offset from the drill.
            try:
                offset_x, offset_y = attr["drill"].attributes["offset"]
            except (AttributeError, KeyError, TypeError):
                pass  # Either no drill or no pad offset w.r.t. the drill.
            else:
                # The pad is offset w.r.t. the drill, so it goes in the opposite dir.
                offset_x, offset_y = -offset_x, -offset_y
                # Rotate the offset as needed.
                rot_tm = wx.AffineMatrix2D()
                rot_tm.Rotate(rot * math.pi / 180)
                offset_x, offset_y = rot_tm.TransformPoint(offset_x, offset_y)
                # Apply the offset to the center of the pad.
                cx -= offset_x
                cy -= offset_y

            # Paint the appropriate pad shape.
            if attr["shape"] == "rect":
                pts = self.rect_pts(cx, cy, w, h, rot, tm)
                for lyr_nm in attr["layers"]:
                    layers[lyr_nm].add_pad_polygon(pts)
            elif attr["shape"] == "circle":
                r = w / 2
                pts = self.circle_pts(cx, cy, r, tm)
                for lyr_nm in attr["layers"]:
                    layers[lyr_nm].add_pad_circle(pts)
            elif attr["shape"] == "roundrect":
                r_ratio = attr["roundrect_rratio"]
                r = r_ratio * min(w, h)
                pts_sets = self.roundrect_pts(cx, cy, w, h, r, rot, tm)
                for lyr_nm in attr["layers"]:
                    for rect_pts in pts_sets[0]:
                        layers[lyr_nm].add_pad_polygon(rect_pts)
                    for circle_pts in pts_sets[1]:
                        layers[lyr_nm].add_pad_circle(circle_pts)
            elif attr["shape"] == "oval":
                r_ratio = 0.5
                r = r_ratio * min(w, h)
                pts_sets = self.roundrect_pts(cx, cy, w, h, r, rot, tm)
                for lyr_nm in attr["layers"]:
                    for rect_pts in pts_sets[0]:
                        layers[lyr_nm].add_pad_polygon(rect_pts)
                    for circle_pts in pts_sets[1]:
                        layers[lyr_nm].add_pad_circle(circle_pts)
            elif attr["shape"] == "trapezoid":
                try:
                    dh, dw = attr["rect_delta"]
                except TypeError:
                    dh, dw = 0, 0
                pts = self.trapezoid_pts(cx, cy, w, h, dw, dh, rot, tm)
                for lyr_nm in attr["layers"]:
                    layers[lyr_nm].add_pad_polygon(pts)
            else:
                raise NotImplementedError

            # Process any drill in the pad.
            cx, cy, rot = (attr["at"] + [0])[0:3]
            try:
                # See if there's a drill in this pad.
                drill_attr = attr["drill"].attributes
            except (KeyError, AttributeError):
                pass  # No drill for this pad.
            else:
                # Yes, there is a drill.
                lyr_nm = "Drill"
                size = drill_attr["size"]
                try:
                    # See if this pad is oval (i.e., has w, h).
                    w, h = size
                    r_ratio = 0.5
                    r = r_ratio * min(w, h)
                    pts_sets = self.roundrect_pts(cx, cy, w, h, r, rot, tm)
                    for rect_pts in pts_sets[0]:
                        layers[lyr_nm].add_pad_polygon(rect_pts)
                    for circle_pts in pts_sets[1]:
                        layers[lyr_nm].add_pad_circle(circle_pts)
                except TypeError:
                    # No, pad is circular.
                    r = size / 2
                    pts = self.circle_pts(cx, cy, r, tm)
                    layers[lyr_nm].add_pad_circle(pts)

        for line in fp.lines:
            attr = line.attributes
            w = attr["width"]
            x0, y0 = attr["start"]
            x1, y1 = attr["end"]
            pts = self.line_pts(w, x0, y0, x1, y1, tm)
            lyr_nm = attr["layer"]
            layers[lyr_nm].add_line(pts)

        for circle in fp.circles:
            attr = circle.attributes
            w = attr["width"]
            cx, cy = attr["center"]
            x1, y1 = attr["end"]
            # Use line_pts routine to calc coords of center and endpoint and line width.
            w, cx, cy, x1, y1 = self.line_pts(w, cx, cy, x1, y1, tm)
            r = math.hypot(cx - x1, cy - y1)
            lyr_nm = attr["layer"]
            layers[lyr_nm].add_circle((w, cx, cy, r))

        for lyr_nm in (
            "B.Cu",
            "F.Cu",
            "F&B.Cu",
            "*.Cu",
            "B.Fab",
            "F.Fab",
            "F&B.Fab",
            "*.Fab",
            "B.CrtYd",
            "F.CrtYd",
            "F&B.CrtYd",
            "*.CrtYd",
            "B.SilkS",
            "F.SilkS",
            "F&B.SilkS",
            "*.SilkS",
            "Drill",
        ):
            layers[lyr_nm].set_fill(*layer_style[lyr_nm])
            layers[lyr_nm].paint(dc)

        # layers['F.Mask'].set_fill(FMASK_COLOUR, wx.BRUSHSTYLE_CROSS_HATCH)
        # bmp = self.mk_bmp(4,4,(0,255,0), 1.0/16)
        # layers['F.Paste'].set_fill(bmp)

        if not self.bbox:
            self.bbox = BBox(*dc.GetBoundingBox())

            # make the bbox a little bigger to put some margin along each side.
            delta = 0.025 * max(
                self.bbox.x1 - self.bbox.x0, self.bbox.y1 - self.bbox.y0
            )

            # Correct point-sized bounding boxes to prevent divide-by-zero errors during scaling.
            if delta < MIN_SIZE:
                delta = MIN_SIZE

            self.bbox = BBox(
                self.bbox.x0 - delta,
                self.bbox.y0 - delta,
                self.bbox.x1 + delta,
                self.bbox.y1 + delta,
            )
