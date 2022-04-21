# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""
Autorouter for generating wiring between symbols in a schematic.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

__all__ = ['route', 'Face', 'GlobalTrack', 'HORZ', 'VERT', 'SwitchBox', 'RoutingFailure']

from builtins import range, zip
from collections import defaultdict
from enum import Enum, auto
from itertools import zip_longest, chain
from random import randint

from future import standard_library

from ...logger import active_logger
from ...part import Part
from ...utilities import *
from .common import *
from .geometry import *

standard_library.install_aliases()

###################################################################
# Overview of Schematic Autorouter
#
# The input is a Node containing parts, each with a bounding box and an
# assigned (x,y) position.
#
# The edges of each part bbox are extended form tracks that divide the
# routing area into a set of four-sided switchboxes. Each side of a 
# switchbox is a Face, and each Face is a member of two adjoining 
# switchboxes (except those Faces on the boundary of the total 
# routing area.) Each face is adjacent to the six other faces of 
# the two switchboxes it is part of.
#
# Each face has a capacity that indicates the number of wires that can
# cross it. The capacity is the length of the face divided by the routing
# grid. (Faces on a part boundary have zero capacity to prevent routing
# from entering a part.)
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
# along their four faces. A greedy switchbox router (https://doi.org/10.1016/0167-9260(85)90029-X)
# does the detailed routing within each switchbox.
#
# The detailed wiring within all the switchboxes is combined and output
# as the total wiring for the parts in the Node.
#
# 
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
###################################################################


# Orientations and directions.
class Orientation(Enum):
    HORZ = auto()
    VERT = auto()

class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()

# Put the orientation/direction enums in global space to make using them easier.
_g = globals()
for orientation in Orientation:
    _g[orientation.name] = orientation.value
for direction in Direction:
    _g[direction.name] = direction.value


# Dictionary for storing colors to visually distinguish routed nets.
net_colors = defaultdict(lambda: (randint(0,200),randint(0,200), randint(0,200)))


#
# Drawing functions to display routing for debugging purposes.
#

def draw_start(bbox):
    """
    Initialize PyGame drawing area.
    
    Args:
        bbox: Bounding box of object to be drawn.

    Returns:
        scr: PyGame screen that is drawn upon.
        tx: Matrix to transform from real coords to screen coords.
        font: PyGame font for rendering text.
    """

    # Only import pygame if drawing is being done to avoid the startup message.
    import pygame
    import pygame.freetype

    # Make pygame module available to other functions.
    globals()['pygame'] = pygame

    # Screen drawing area.
    scr_bbox = BBox(Point(0, 0), Point(2000, 1500))

    # Place a blank region around the object by expanding it's bounding box.
    border = max(bbox.w, bbox.h) / 20
    bbox = bbox.resize(Vector(border, border))
    bbox = round(bbox)

    # Compute the scaling from real to screen coords.
    scale = min(scr_bbox.w / bbox.w, scr_bbox.h / bbox.h)
    scale_tx = Tx(a=scale, d=scale)

    # Flip the Y coord.
    flip_tx = Tx(d=-1)

    # Compute the translation of the object center to the drawing area center
    new_bbox = bbox.dot(scale_tx).dot(flip_tx)  # Object bbox transformed to screen coords.
    move = scr_bbox.ctr - new_bbox.ctr  # Vector to move object ctr to drawing ctr.
    move_tx = Tx(dx=move.x, dy=move.y)

    # The final transformation matrix will scale the object's real coords,
    # flip the Y coord, and then move the object to the center of the drawing area.
    tx = scale_tx.dot(flip_tx).dot(move_tx)

    # Initialize drawing area.
    pygame.init()
    scr = pygame.display.set_mode((scr_bbox.w, scr_bbox.h))

    # Set font for text rendering.
    font = pygame.freetype.SysFont("consolas", 24)

    # Clear drawing area.
    scr.fill((255, 255, 255))

    # Return drawing screen, transformation matrix, and font.
    return scr, tx, font

def draw_box(bbox, scr, tx, color=(192, 255, 192)):
    """Draw a box in the drawing area.

    Args:
        bbox (BBox): Bounding box for the box.
        scr (PyGame screen): Screen object for PyGame drawing.
        tx (Tx): Transformation matrix from real to screen coords.
        color (tuple, optional): Box color. Defaults to (192, 255, 192).

    Returns:
        None.
    """

    bbox = bbox.dot(tx)
    corners = (
        (bbox.min.x, bbox.min.y),
        (bbox.min.x, bbox.max.y),
        (bbox.max.x, bbox.max.y),
        (bbox.max.x, bbox.min.y),
    )
    pygame.draw.polygon(scr, color, corners, 0)

def draw_endpoint(pt, scr, tx, color=(100,100,100), dot_radius=10):
    """Draw a line segment endpoint in the drawing area.

    Args:
        pt (Point): A point with (x,y) coords.
        scr (PyGame screen): Screen object for PyGame drawing.
        tx (Tx): Transformation matrix from real to screen coords.
        color (tuple, optional): Segment color. Defaults to (192, 255, 192).
        dot_Radius (int, optional): Endpoint dot radius. Defaults to 3.
    """

    pt = pt.dot(tx) # Convert to drawing coords.

    # Draw diamond for terminal.
    sz = dot_radius/2 * tx.a  # Scale for drawing coords.
    corners = (
        (pt.x, pt.y + sz),
        (pt.x + sz, pt.y),
        (pt.x, pt.y - sz),
        (pt.x - sz, pt.y),
    )
    pygame.draw.polygon(scr, color, corners, 0)

    # Draw dot for terminal.
    radius = dot_radius * tx.a
    pygame.draw.circle(scr, color, (pt.x, pt.y), radius)

def draw_seg(seg, scr, tx, color=(100, 100, 100), thickness=5, dot_radius=10):
    """Draw a line segment in the drawing area.

    Args:
        seg (Segment, Interval, NetInterval): An object with two endpoints.
        scr (PyGame screen): Screen object for PyGame drawing.
        tx (Tx): Transformation matrix from real to screen coords.
        color (tuple, optional): Segment color. Defaults to (192, 255, 192).
        seg_thickness (int, optional): Segment line thickness. Defaults to 5.
        dot_Radius (int, optional): Endpoint dot radius. Defaults to 3.
    """

    # Use net color if object has a net. Otherwise set color to black.
    try:
        color = net_colors[seg.net]
    except AttributeError:
        color = (0, 0, 0)

    # draw endpoints.
    draw_endpoint(seg.p1, scr, tx, color, dot_radius=dot_radius)
    draw_endpoint(seg.p2, scr, tx, color, dot_radius=dot_radius)

    # Transform segment coords to screen coords.
    seg = seg.dot(tx)

    # Draw segment.
    pygame.draw.line(
        scr, color, (seg.p1.x, seg.p1.y), (seg.p2.x, seg.p2.y), width=thickness
    )

def draw_text(txt, pt, scr, tx, font, color=(100, 100, 100)):
    """Render text in drawing area.

    Args:
        txt (str): Text string to be rendered.
        pt (Point): Real coord for start of rendered text.
        scr (PyGame screen): Screen object for PyGame drawing.
        tx (Tx): Transformation matrix from real to screen coords.
        font (PyGame font): Font for rendering text.
        color (tuple, optional): Segment color. Defaults to (100,100,100).
    """

    # Transform text starting point to screen coords.
    pt = pt.dot(tx)

    # Render text.
    font.render_to(scr, (pt.x, pt.y), txt, color)

def draw_end():
    """Display drawing and wait for user to close PyGame window."""

    # Display drawing.
    pygame.display.flip()

    # Wait for user to close PyGame window.
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()


class NoSwitchBox(Exception):
    """Exception raised when a switchbox cannot be generated.

    Args:
        Exception (Exception): Raised when a switchbox cannot be generated for a given Face.
    """
    pass


class RoutingFailure(Exception):
    """Exception raised when a net connecting terminals cannot be routed.

    Args:
        Exception (Exception): Raised when terminals on a net cannot be connected.
    """
    pass


class Boundary:
    """Class for indicating a boundary.

    When a Boundary object is placed in the part attribute of a Face, it
    indicates the Face is on the outer boundary of the Node routing area.
    """
    pass

# Boundary object for placing in Faces on the bounding Faces of the Node routing area.
boundary = Boundary()


class Terminal:

    def __init__(self, net, face, coord):
        """Terminal on a Face from which a net is routed within a SwitchBox.

        Args:
            net (Net): Net upon which the Terminal resides.
            face (Face): SwitchBox Face upon which the Terminal resides.
            coord (int): Position along the Face.
        """

        self.net = net
        self.face = face
        self.coord = coord

    @property
    def pt(self):
        """Return (x,y) Point for a Terminal on a Face."""
        track = self.face.track
        if track.orientation == HORZ:
            return Point(self.coord, track.coord)
        else:
            return Point(track.coord, self.coord)

    def get_next_terminal(self, next_face):
        """Get the next terminal from the given face that lies on the same net as this terminal.

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
                search_range = range(len(next_face.terminals))
            elif next_face.end == from_face.track:
                # next_face is oriented downward or leftward w.r.t. from_face.
                # Start searching for a terminal from the highest index
                # because this is closest to the corner.
                search_range = range(len(next_face.terminals) - 1, -1, -1)
            else:
                raise RoutingFailure
        else:
            # The next face must be the parallel face on the other side of the
            # switchbox. With parallel faces, we want to selected a terminal
            # having close to the same position as the given terminal.
            # So if the given terminal is at position i, then search for the
            # next terminal on the other face at positions i, i+1, i-1, i+2, i-2...
            from_len = len(from_face.terminals)
            from_idx = from_face.terminals.index(self)
            search_range = chain(
                *zip_longest(range(from_idx, -1, -1), range(from_idx + 1, from_len))
            )

        # Use the computed search range to find a terminal on the next face that
        # is not assigned to a net, or is already assigned to the same net as the
        # given terminal.
        for idx in search_range:
            if idx is not None:
                terminal = next_face.terminals[idx]
                if terminal.net in (None, self.net):
                    return terminal

        # Well, something went wrong...
        raise RoutingFailure

    def draw(self, scr, tx, flags=[]):
        """Draw a Terminal.

        Args:
            scr (PyGame screen): Screen object for PyGame drawing.
            tx (Tx): Transformation matrix from real to screen coords.
            flags (list, optional): List of option strings. Defaults to [].
        """

        # Don't draw terminal if it isn't on a net. It's just a placeholder.
        if not self.net:
            return

        # Compute the terminal (x,y) based on whether it's on a horiz or vert Face.
        if self.face.track.orientation == HORZ:
            pt = Point(self.coord, self.face.track.coord)
        else:
            pt = Point(self.face.track.coord, self.coord)

        draw_endpoint(pt, scr, tx, net_colors[self.net])


class Interval:
    def __init__(self, beg, end):
        """Define an interval with a beginning and an end.

        Args:
            beg (GlobalTrack): Beginning track that bounds interval.
            end (GlobalTrack): Ending track that bounds interval.
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

    def merge(self, other):
        """Return a merged interval if the given intervals intersect, otherwise return None."""
        if Interval.intersects(self,other):
            return Interval(min(self.beg, other.beg), max(self.end, other.end))
        return None


class NetInterval(Interval):
    def __init__(self, net, beg, end):
        """Define an Interval with an associated net (useful for wire traces in a switchbox).

        Args:
            net (Net): Net associated with interval.
            beg (GlobalTrack): Beginning track that bounds interval.
            end (GlobalTrack): Ending track that bounds interval.
        """
        super().__init__(beg, end)
        self.net = net

    def obstructs(self, other):
        """Return True if the intervals intersect and have different nets."""
        return super().intersects(other) and (self.net is not other.net)

    def merge(self, other):
        """Return a merged interval if the given intervals intersect, otherwise return None."""
        if self.net is other.net:
            merged_intvl = super().merge(other)
            if merged_intvl:
                merged_intvl = NetInterval(self.net, merged_intvl.beg, merged_intvl.end)
            return merged_intvl
        return None


class Face(Interval):
    """A side of a rectangle bounding a routing switchbox."""

    def __init__(self, part, track, beg, end):
        """One side of a routing switchbox.

        Args:
            part (set,Part,Boundary): Element(s) the Face is part of.
            track (GlobalTrack): Horz/vert track the Face is on.
            beg (GlobalTrack): Vert/horz track the Face begins at.
            end (GlobalTrack): Vert/horz track the Face ends at.
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

        # Set of Faces adjacent to this one. (Starts empty.)
        self.adjacent = set()

        # Add this new face to the track it belongs to so it isn't lost.
        self.track = track
        track.add_face(self)

    def combine(self, other):
        """Combine information from other face into this one.

        Args:
            other (Face): Other Face.

        Returns:
            None.
        """

        self.pins.extend(other.pins)
        self.part.update(other.part)
        self.adjacent.update(other.adjacent)

    @property
    def bbox(self):
        """Return the bounding box of the 1-D face segment."""
        bbox = BBox()

        # Start off assuming the Face bbox is vertical.
        bbox.add(Point(self.track.coord, self.beg.coord))
        bbox.add(Point(self.track.coord, self.end.coord))

        # Rotate the bbox if the Face is actually horizontal.
        if self.track.orientation == HORZ:
            bbox = bbox.dot(Tx(a=0, b=1, c=1, d=0))

        return bbox

    def create_nonpin_terminals(self):
        """Create non-net terminals along a non-part Face with GRID spacing."""
        
        # Don't add terminals if the Face is on a part or a boundary.
        if self.part:
            self.terminals = []
            return

        # Add terminals along Face, but keep terminals off the beginning or end points.
        from .gen_schematic import GRID
        beg = (self.beg.coord + GRID // 2 + GRID) // GRID * GRID
        end = self.end.coord - GRID // 2
        self.terminals = [
            Terminal(None, self, coord) for coord in range(beg, end, GRID)
        ]

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

    def add_adjacency(self, adj_face):
        """Make two faces adjacent to one another."""

        # Faces on the boundary can never accept wires so they are never
        # adjacent to any other face.
        if boundary in self.part or boundary in adj_face.part:
            return

        # If a face is an edge of a part, then it can never be adjacent to
        # another face on the same part or else wires might get routed through
        # the part bounding box.
        if not self.part.intersection(adj_face.part):
            # OK, no parts in common between the two faces so they can be adjacent.
            self.adjacent.add(adj_face)
            adj_face.adjacent.add(self)

    def add_adjacencies(self):
        """Add adjacent faces of the switchbox having this face as the top face."""

        # Create a temporary switchbox.
        try:
            swbx = SwitchBox(self)
        except NoSwitchBox:
            # This face doesn't belong to a valid switchbox.
            return

        # Add adjacent faces.
        swbx.top_face.add_adjacency(swbx.bottom_face)
        swbx.left_face.add_adjacency(swbx.right_face)
        swbx.left_face.add_adjacency(swbx.top_face)
        swbx.left_face.add_adjacency(swbx.bottom_face)
        swbx.right_face.add_adjacency(swbx.top_face)
        swbx.right_face.add_adjacency(swbx.bottom_face)

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
        for dir in (0, 1):
            if dir == 0:
                # Search for intersecting faces from the face beginning down to 0.
                start = self.beg
                search = orthogonal_tracks[start.idx :: -1]
            else:
                # Search for intersecting faces from the face end up to max index.
                start = self.end
                search = orthogonal_tracks[start.idx :]

            # The face extension starts off non-blocked by any orthogonal faces.
            blocked = False

            # Search for a face in a track that intersects this extension.
            for ortho_track in search:
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

    @property
    def seg(self):
        """Return a Segment that coincides with the Face."""

        # Start off assuming it's a vertical face.
        p1 = Point(self.track.coord, self.beg.coord)
        p2 = Point(self.track.coord, self.end.coord)
        seg = Segment(p1, p2)

        # If the face is actually horizontal, then rotate the segment.
        if self.track.orientation == HORZ:
            seg = seg.dot(Tx(a=0, b=1, c=1, d=0))

        return seg

    def draw(self, scr, tx, font, flags=[]):
        """Draw a Face in the drawing area.

        Args:
            scr (PyGame screen): Screen object for PyGame drawing.
            tx (Tx): Transformation matrix from real to screen coords.
            font (PyGame font): Font for rendering text.
            flags (list, optional): List of option strings. Defaults to [].

        Returns:
            None.
        """

        # Draw a line segment for the Face.
        color = (128, 128, 128)
        draw_seg(self.seg, scr, tx, color, thickness=2, dot_radius=0)

        # Draw the terminals on the Face.
        for terminal in self.terminals:
            terminal.draw(scr, tx)

        if "show_capacities" in flags:
            # Show the wiring capacity at the midpoint of the Face.
            mid_pt = (self.seg.p1 + self.seg.p2) / 2
            draw_text(str(self.capacity), mid_pt, scr, tx, font, color)


class GlobalWire(list):

    def __init__(self, *args, net=None, **kwargs):
        """Global-routing wire connecting switchbox faces and terminals.

        Global routes start off as a sequence of switchbox faces that the route
        goes thru. Later, these faces are converted to terminals at fixed positions
        on their respective faces.

        Args:
            *args: Positional args passed to list superclass __init__().
            net (Net): The net associated with the wire.
            **kwargs: Keyword args passed to list superclass __init__().
        """
        self.net = net
        super().__init__(*args, **kwargs)

    def cvt_faces_to_terminals(self):
        """Convert face-to-face global route to switchbox terminal-to-terminal route."""

        # All part faces already have terminals created from the part pins. Find all
        # the route faces on part boundaries and convert them to pin terminals for
        # any pins that are attached to the same net as the route.
        for i, face in enumerate(self[:]):
            if face.part:
                for terminal in face.terminals:
                    if terminal.net is self.net:
                        self[i] = terminal
                        # TODO: What if net goes to multiple pins on a part face?
                        break
                else:
                    raise RoutingFailure

        # The remaining faces on the global route are on switchboxes where a
        # terminal point must be selected and assigned to the route net.
        # Iterate thru the faces until they've all been converted to Terminals.
        keep_iterating = True
        while keep_iterating:
            keep_iterating = False
            for i in range(0, len(self) - 1):

                # Get two sequential points of the route.
                from_, to_ = self[i], self[i + 1]
                
                if Face in (from_, to_):
                    # If either is a Face, then the entire route hasn't been converted
                    # to Terminals so keep iterating.
                    keep_iterating = True

                if isinstance(from_, Terminal) and isinstance(to_, Terminal):
                    # Both points are already terminals, so no need to do anything.
                    continue

                if isinstance(from_, Face) and isinstance(to_, Face):
                    # Both points are Faces, so don't do anything and wait for one of them
                    # to get converted to a Terminal later on.
                    continue

                # One of the points is a Terminal and the other is a Face,
                # so use the terminal to convert the face to a terminal and
                # assign it to the route net.
                if isinstance(from_, Face) and isinstance(to_, Terminal):
                    terminal = to_.get_next_terminal(from_)
                    terminal.net = self.net
                    self[i] = terminal # Replace from_ Face with Terminal.
                    continue
                if isinstance(from_, Terminal) and isinstance(to_, Face):
                    terminal = from_.get_next_terminal(to_)
                    terminal.net = self.net
                    self[i + 1] = terminal # Replace to_ Face with Terminal.
                    continue

                raise RoutingFailure

    def draw(self, scr, tx, flags=[]):
        """Draw a global wire from Face-to-Face in the drawing area.

        Args:
            scr (PyGame screen): Screen object for PyGame drawing.
            tx (Tx): Transformation matrix from real to screen coords.
            flags (list, optional): List of option strings. Defaults to [].

        Returns:
            None.
        """

        # Draw pins on the net associated with the wire.
        for pin in self.net.pins:
            pt = pin.pt.dot(pin.part.tx)
            track = pin.face.track
            pt = {
                HORZ: Point(pt.x, track.coord),
                VERT: Point(track.coord, pt.y),
            }[track.orientation]
            draw_endpoint(pt, scr, tx, color=(0,0,0), dot_radius=10)

        # Draw global wire segment.
        face_to_face = zip(self[:-1], self[1:])
        for terminal1, terminal2 in face_to_face:
            p1 = terminal1.pt
            p2 = terminal2.pt
            draw_seg(Segment(p1, p2), scr, tx, (0, 0, 0), 1, 0)


class GlobalTrack(list):

    def __init__(self, *args, orientation=HORZ, coord=0, idx=None, **kwargs):
        """A horizontal/vertical track holding zero or more faces all having the same Y/X coordinate.

        These global tracks are made by extending the edges of part bounding boxes to
        form a non-regular grid of rectangular switchboxes. These tracks are *NOT* the same
        as the tracks used within the switchbox for the detailed routing phase.

        Args:
            *args: Positional args passed to list superclass __init__().
            orientation (Orientation): Orientation of track (horizontal or vertical).
            coord (int): Coordinate of track on axis orthogonal to track direction.
            idx (int): Index of track into a list of X or Y coords.
            **kwargs: Keyword args passed to list superclass __init__().
        """

        self.orientation = orientation
        self.coord = coord
        self.idx = idx
        super().__init__(*args, **kwargs)

        # This stores the orthogonal tracks that intersect this one.
        self.splits = set()

    def __lt__(self, track):
        """Used for ordering tracks."""
        return self.coord < track.coord

    def __gt__(self, track):
        """Used for ordering tracks."""
        return self.coord > track.coord

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
        """Store the orthogonal track that intersects this one.

        Args:
            orthogonal_track (GlobalTrack): Track intersecting this one.
        """
        self.splits.add(orthogonal_track)

    def add_face(self, face):
        """Add a face to a track.

        Args:
            face (Face): Face to be added to track.
        """
        self.append(face)

        # The added face will also split the orthogonal tracks that define its endpoints.
        self.add_split(face.beg)
        self.add_split(face.end)

    def split_faces(self):
        """Apply split tracks to all the faces in a track."""

        for split in self.splits:
            for face in self[:]:
                # Apply the split track to the face. The face will only be split
                # if the split track intersects it. Any split faces will be added
                # to the track this face is on.
                face.split(split)

    def remove_duplicate_faces(self):
        """Remove duplicate faces having the same endpoints."""

        # Search for pairs of faces with identical endpoints.
        for i, first_face in enumerate(self[:]):
            for second_face in self[i + 1 :]:
                if first_face.coincides_with(second_face):
                    
                    # Update the second face with the info from the first face.
                    second_face.combine(first_face)
                    
                    # Remove the first face since it's redundant.
                    self.remove(first_face)

                    # Stop searching for dups of the first face because the
                    # equivalent of that can be done using the second face
                    # on a later iteration.
                    break

    def add_adjacencies(self):
        """Add adjacent faces to each face in a track."""
        for top_face in self:
            top_face.add_adjacencies()


class Target:
    def __init__(self, net, row, col):
        """A point on a switchbox face that wiring has not yet reached.

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
        return (self.col, self.row, id(self.net)) < (other.col, other.row, id(other.net))


class SwitchBox:
    def __init__(self, top_face):

        left_face = None
        left_track = top_face.beg
        for face in left_track:
            if face.end.coord == top_face.track.coord:
                left_face = face
                break

        if not left_face:
            raise NoSwitchBox("Unroutable switchbox!")

        right_face = None
        right_track = top_face.end
        for face in right_track:
            if face.end.coord == top_face.track.coord:
                right_face = face
                break

        if not right_face:
            raise NoSwitchBox("Unroutable switchbox!")

        if left_face.beg != right_face.beg:
            # This only happens when two parts are butted up against each other
            # to form a non-routable switchbox inside a part bounding box.
            raise NoSwitchBox("Unroutable switchbox!")

        bottom_face = None
        bottom_track = left_face.beg
        for face in bottom_track:
            if face.beg.coord == top_face.beg.coord:
                bottom_face = face
                break

        if not bottom_face:
            raise NoSwitchBox("Unroutable switchbox!")

        # If all four sides have a common part, then its a part bbox with no routing.
        if top_face.part & bottom_face.part & left_face.part & right_face.part:
            raise NoSwitchBox("Part switchbox")

        top_face.set_capacity()
        bottom_face.set_capacity()
        left_face.set_capacity()
        right_face.set_capacity()

        self.top_face = top_face
        self.bottom_face = bottom_face
        self.left_face = left_face
        self.right_face = right_face

        def find_terminal_net(terminals, terminal_coords, coord):
            try:
                return terminals[terminal_coords.index(coord)].net
            except ValueError:
                return None

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

        left_coords = [terminal.coord for terminal in self.left_face.terminals]
        right_coords = [terminal.coord for terminal in self.right_face.terminals]
        tb_coords = [self.top_face.track.coord, self.bottom_face.track.coord]
        self.track_coords = sorted(set(left_coords + right_coords + tb_coords))
        if len(self.track_coords) == 2:
            # This is a weird case. If the switchbox channel is too narrow to hold
            # a routing track in the middle, then place two pseudo-tracks along the
            # top and bottom faces to allow routing to proceed. The routed wires will
            # end up in the top or bottom faces, but maybe that's OK.
            self.track_coords.extend(self.track_coords)
            self.track_coords.sort()  # Re-sort after adding top/bottom coords.
        self.left_nets = [
            find_terminal_net(self.left_face.terminals, left_coords, coord)
            for coord in self.track_coords
        ]
        self.right_nets = [
            find_terminal_net(self.right_face.terminals, right_coords, coord)
            for coord in self.track_coords
        ]
        assert len(self.top_nets) == len(self.bottom_nets)
        assert len(self.left_nets) == len(self.right_nets)

    def flip_xy(self):
        """Flip X-Y of switchbox to route from top-to-bottom instead of left-to-right."""
        self.column_coords, self.track_coords = self.track_coords, self.column_coords
        self.top_nets, self.right_nets, = self.right_nets, self.top_nets
        self.bottom_nets, self.left_nets = self.left_nets, self.bottom_nets
        self.top_face, self.right_face = self.right_face, self.top_face
        self.bottom_face, self.left_face = self.left_face, self.bottom_face
        try:
            for seg in self.segments:
                seg.p1.x, seg.p1.y = seg.p1.y, seg.p1.x
                seg.p2.x, seg.p2.y = seg.p2.y, seg.p2.x
        except AttributeError:
            pass

    @property
    def bbox(self):
        bbox = BBox()
        bbox.add(self.top_face.bbox)
        bbox.add(self.bottom_face.bbox)
        bbox.add(self.left_face.bbox)
        bbox.add(self.right_face.bbox)
        return bbox

    def has_nets(self):
        for face in (self.top_face, self.bottom_face, self.left_face, self.right_face):
            if face.has_nets():
                return True
        return False

    def route(self, flags=[]):

        self.segments = []

        if not self.has_nets():
            return self.segments

        def connect_top_btm(track_nets):
            """Connect top/bottom net to nets in horizontal tracks."""

            def find_connection(net, tracks, direction):
                """
                Searches for the closest track with the same net followed by the
                closest empty track. The indices of these tracks are returned.
                If the net cannot be connected to any track, return [].
                If the net given to connect is None, then return a list of [None].

                Args:
                    net (Net): Net to be connected.
                    tracks (list): Nets on tracks
                    direction (int): Search direction for connection.

                Returns:
                    list: Indices of tracks where the net can connect.
                """
                if net:
                    connections = []
                    if direction < 0:
                        tracks = tracks[::-1]
                    try:
                        connections.append(tracks[1:-1].index(net)+1)
                    except ValueError:
                        pass
                    try:
                        connections.append(tracks[1:-1].index(None)+1)
                    except ValueError:
                        pass
                    if direction < 0:
                        l = len(tracks)
                        connections = [l - 1 - cnct for cnct in connections]
                else:
                    connections = [None]
                return connections

            b_net = track_nets[0]
            t_net = track_nets[-1]
            column = []
            t_cncts = find_connection(t_net, track_nets, -1)
            b_cncts = find_connection(b_net, track_nets, 1)

            # Test each possible pair of connections to find one that is free of interference.
            tb_cncts = [(t,b) for t in t_cncts for b in b_cncts]

            if not tb_cncts:
                # Top and/or bottom could not be connected.
                if "allow_routing_failure" in flags:
                    return column
                else:
                    raise RoutingFailure
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
                if "allow_routing_failure" in flags:
                    return column
                else:
                    raise RoutingFailure

            if t_cnct is not None:
                # Connection from track to terminal on top of switchbox.
                column.append(NetInterval(t_net, t_cnct, len(track_nets)-1))
            if b_cnct is not None:
                # Connection from terminal on bottom of switchbox to track.
                column.append(NetInterval(b_net, 0, b_cnct))

            # Return connection segments.
            return column

        def prune_targets(targets, col):
            return [target for target in targets if target.col > col]

        def net_search(net, start, track_nets):
            large_offset = 2 * len(track_nets)
            try:
                up = track_nets[start:-1].index(net)
            except ValueError:
                up = large_offset
            try:
                down = track_nets[start:0:-1].index(net)
            except ValueError:
                down = large_offset
            return up, down

        def insert_column_nets(track_nets, column):
            track_nets = track_nets[:]
            for intvl in column:
                track_nets[intvl.beg] = intvl.net
                track_nets[intvl.end] = intvl.net
            return track_nets

        def insert_target_nets(track_nets, targets, right_nets):
            target_track_nets = [None] * len(track_nets)
            used_target_nets = []

            right_nets = [net if net in track_nets else None for net in right_nets]

            for target in targets:

                # Skip target nets that aren't currently active or have already been 
                # placed (prevents multiple insertions of the same target net).
                net = target.net
                if net not in track_nets or net in used_target_nets or net in right_nets:
                    continue

                row = target.row

                net_up, net_down = net_search(net, row, track_nets)
                empty_up, empty_down = net_search(None, row, track_nets)
                up = min(net_up, empty_up)
                down = min(net_down, empty_down)

                try:
                    if up <= down:
                        target_track_nets[row+up] = net
                    else:
                        target_track_nets[row-down] = net
                    used_target_nets.append(net)
                except IndexError:
                    # There was no place for this target net.
                    pass 

            return [net or r_net or target for (net, r_net, target) in zip(track_nets, right_nets, target_track_nets)]
            # return [net or target for (net, target) in zip(track_nets, target_track_nets)]

        def connect_splits(track_nets, column):

            # Make a copy so the original isn't disturbed.
            track_nets = track_nets[:]

            # Find nets that are running on multiple tracks.
            multi_nets = set(net for net in set(track_nets) if track_nets.count(net)>1)
            multi_nets.discard(None)  # Ignore empty tracks.

            # Find intervals for multi-track nets.
            net_intervals = []
            for net in multi_nets:
                net_trk_idxs = [idx for idx, nt in enumerate(track_nets) if nt is net]
                for index, trk1 in enumerate(net_trk_idxs[:-1],1):
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

            column_nets = set(intvl.net for intvl in column)
            for net in column_nets:

                # Extract intervals if the current net has more than one interval.
                intervals = [intvl for intvl in column if intvl.net is net]
                if len(intervals) < 2:
                    continue
                for intvl in intervals:
                    column.remove(intvl)

                # Merge the extracted intervals as much as possible.
                merged = True
                while merged and len(intervals)>1:
                    merged = False
                    merged_intervals = []

                    # Sort intervals by their beginning coordinates.
                    intervals.sort(key=lambda intvl: intvl.beg)

                    # Try merging consecutive pairs of intervals.
                    for intvl1, intvl2 in zip(intervals[:-1], intervals[1:]):
                        merged_intvl = intvl1.merge(intvl2)
                        if merged_intvl:
                            # Replace separate intervals with merged interval.
                            merged_intervals.append(merged_intvl)
                            # Merging happened, so iterate through intervals again
                            # to find more merges.
                            merged = True
                        else:
                            # Intervals couldn't be merged, so keep both.
                            merged_intervals.extend((intvl1, intvl2))
                    
                    # Update list of intervals to include merges and remove duplicates.
                    intervals = list(set(merged_intervals))

                # Place merged intervals back into column.
                column.extend(set(merged_intervals))

            return column

        def extend_tracks(track_nets, column, targets):
            rightward_nets = set(target.net for target in targets)

            # Keep extending nets in current tracks if they do not intersect intervals in the 
            # current column with the same net.
            flow_thru_nets = track_nets[:]
            for intvl in column:
                for trk_idx in range(intvl.beg, intvl.end+1):
                    if flow_thru_nets[trk_idx] is intvl.net:
                        # Remove net from track since it intersects an interval with the 
                        # same net. The net may be extended from the interval in the next phase,
                        # or it may terminate here.
                        flow_thru_nets[trk_idx] = None

            next_track_nets = flow_thru_nets[:]

            # Extend track net if net has multiple column intervals that need further interconnection
            # or if there are terminals in rightward columns that need connections to this net.
            column_nets = [intvl.net for intvl in column]
            for intvl in column:
                net = intvl.net

                num_net_intvls = column_nets.count(net) + flow_thru_nets.count(net)
                if num_net_intvls == 1 and net not in rightward_nets:
                    continue

                target_row = None
                for target in targets:
                    if target.net is net:
                        target_row = target.row
                        break

                beg = max(intvl.beg, 1)
                end = min(intvl.end, len(track_nets)-2)
                if target_row is None:
                    if track_nets[beg] is None:
                        row = beg
                    else:
                        row = end
                else:
                    if target_row > end:
                        target_row = end
                    elif target_row < beg:
                        target_row = beg
                    if track_nets[target_row] in (net, None):
                        row = target_row
                    elif track_nets[beg] is None:
                        row = beg
                    elif track_nets[end] is None:
                        row = end
                    elif track_nets[beg] is net:
                        row = beg
                    elif track_nets[end] is net:
                        row = end

                next_track_nets[row] = net

            return next_track_nets

        def trim_column_intervals(column, track_nets, next_track_nets):
            new_column = []
            for intvl in column:
                net = intvl.net
                beg = intvl.beg
                end = intvl.end
                if net in (track_nets[beg], next_track_nets[beg]) and net in (track_nets[end], next_track_nets[end]):
                    new_column.append(intvl)
            return new_column

        # Collect target nets along top, bottom, right faces of switchbox.
        min_row = 1
        max_row = len(self.left_nets)-2
        max_col = len(self.top_nets)
        targets = []
        for col, (t_net, b_net) in enumerate(zip(self.top_nets, self.bottom_nets)):
            if t_net is not None:
                targets.append(Target(t_net, max_row, col))
            if b_net is not None:
                targets.append(Target(b_net, min_row, col))
        for row, r_net in enumerate(self.right_nets):
            if r_net is not None:
                targets.append(Target(r_net, row, max_col))
        targets.sort()

        # Main switchbox routing loop.
        tracks = [self.left_nets[:]]
        track_nets = tracks[0]
        columns = [[], ]
        for col, (t_net, b_net) in enumerate(zip(self.top_nets[1:-1], self.bottom_nets[1:-1]), start=1):
            track_nets[0] = b_net
            track_nets[-1] = t_net
            column = connect_top_btm(track_nets)
            augmented_track_nets = insert_column_nets(track_nets, column)
            targets = prune_targets(targets, col)
            augmented_track_nets = insert_target_nets(augmented_track_nets, targets, self.right_nets)
            column = connect_splits(augmented_track_nets, column)
            track_nets = extend_tracks(track_nets, column, targets)
            tracks.append(track_nets)
            column = trim_column_intervals(column, tracks[-2], tracks[-1])
            columns.append(column)

        for track_net, right_net in zip(tracks[-1], self.right_nets):
            if track_net is not right_net:
                if "allow_routing_failure" not in flags:
                    raise RoutingFailure

        # Create horizontal wiring segments.
        for col_idx, trks in enumerate(tracks):
            beg_col_coord = self.column_coords[col_idx]
            end_col_coord = self.column_coords[col_idx+1]
            for trk_idx, net in enumerate(trks[1:-1], start=1):
                if net:
                    trk_coord = self.track_coords[trk_idx]
                    p1 = Point(beg_col_coord, trk_coord)
                    p2 = Point(end_col_coord, trk_coord)
                    seg = Segment(p1,p2)
                    seg.net = net
                    self.segments.append(seg)

        # Create vertical wiring segments.
        for idx, column in enumerate(columns[1:], start=1):
            col_coord = self.column_coords[idx]
            for intvl in column:
                beg_trk_coord = self.track_coords[intvl.beg]
                end_trk_coord = self.track_coords[intvl.end]
                p1 = Point(col_coord, beg_trk_coord)
                p2 = Point(col_coord, end_trk_coord)
                seg = Segment(p1, p2)
                seg.net = intvl.net
                self.segments.append(seg)

        return self.segments

    def draw(self, scr=None, tx=None, font=None, flags=["draw_switchbox", "draw_routing"]):
        do_start_end = not bool(scr)

        if do_start_end:
            scr, tx, font = draw_start(self.bbox.resize(Vector(100,100)))

        if self.top_face.part:
            for prt in (self.top_face.part):
                if isinstance(prt, Part):
                    draw_box(prt.bbox.dot(prt.tx), scr, tx)

        if "draw_switchbox" in flags:
            self.top_face.draw(scr, tx, font, flags)
            self.bottom_face.draw(scr, tx, font, flags)
            self.left_face.draw(scr, tx, font, flags)
            self.right_face.draw(scr, tx, font, flags)

        if "draw_routing" in flags:
            try:
                for segment in self.segments:
                    draw_seg(segment, scr, tx, dot_radius=0)
            except AttributeError:
                pass

        def draw_channel(face1, face2):
            seg1 = face1.seg
            seg2 = face2.seg
            p1 = (seg1.p1 + seg1.p2) / 2
            p2 = (seg2.p1 + seg2.p2) / 2
            draw_seg(Segment(p1, p2), scr, tx, (128,0,128), 1, dot_radius=0)

        if "draw_channels" in flags:
            draw_channel(self.top_face, self.bottom_face)
            draw_channel(self.top_face, self.left_face)
            draw_channel(self.top_face, self.right_face)
            draw_channel(self.bottom_face, self.left_face)
            draw_channel(self.bottom_face, self.right_face)
            draw_channel(self.left_face, self.right_face)

        if do_start_end:
            draw_end()


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
            pin.face.prev = pin.face  # Indicates terminal pin.
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
                            path = [f]
                            while f.prev is not f:
                                path.append(f.prev)
                                f = f.prev
                            return path

                        wire = GlobalWire(
                            get_face_path(visit_face)[::-1]
                            + get_face_path(next_face)[:],
                            net=net,
                        )
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
        if hasattr(pin, "frontier"):
            for face in pin.visited | pin.frontier:
                delattr(face, "dist")
                delattr(face, "prev")
                delattr(face, "seed_pin")
            delattr(pin, "frontier")
            delattr(pin, "visited")

    return routed_wires


def route(node, flags=["draw", "draw_switchbox"]):
    """Route the wires between part pins in the node.

    Args:
        node (Node): Hierarchical node containing the parts to be connect

    Returns:
        A list of detailed wire routes.

    Note:
        1. Divide the bounding box surrounding the parts into switchboxes.
        2. Do global routing of nets through sequences of switchboxes.
        3. Do detailed routing within each switchbox.
    """

    # Exit if no parts to route.
    if not node.parts:
        return []

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
        return []

    # Find the coords of the horiz/vert tracks that will hold the H/V faces of the routing switchboxes.
    v_track_coord = []
    h_track_coord = []

    # The top/bottom/left/right of each part's bounding box define the H/V tracks.
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
        track.remove_duplicate_faces()

    # Add terminals to all non-part/non-boundary faces.
    for track in h_tracks + v_tracks:
        for face in track:
            face.create_nonpin_terminals()

    # Add terminals to switchbox faces for all part pins on internal nets.
    from .gen_schematic import calc_pin_dir
    for net in internal_nets:
        for pin in net.pins:
            dir = calc_pin_dir(pin)
            part = pin.part
            pin_track = {
                "U": part.bottom_track,
                "D": part.top_track,
                "L": part.right_track,
                "R": part.left_track,
            }[dir]
            pt = pin.pt.dot(part.tx)
            coord = {
                "U": pt.x,
                "D": pt.x,
                "L": pt.y,
                "R": pt.y,
            }[dir]
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

    # Add adjacencies between faces that define global routing paths within switchboxes.
    for h_track in h_tracks[1:]:
        h_track.add_adjacencies()

    # Set routing capacity of faces.
    for track in h_tracks + v_tracks:
        for face in track:
            face.set_capacity()

    # Do global routing of nets internal to the node.

    def rank_net(net):
        """Rank net based on W/H of bounding box of pins and the # of pins."""
        bbox = BBox()
        for pin in net.pins:
            bbox.add(pin.pt)
        return (bbox.w + bbox.h, len(net.pins))

    internal_nets.sort(key=rank_net)
    global_routes = [route_globally(net) for net in internal_nets]
    for route in global_routes:
        for wire in route:
            wire.cvt_faces_to_terminals()

    # Do detailed routing inside switchboxes.
    detailed_routes = []
    switchboxes = []
    for h_track in h_tracks[1:]:
        for face in h_track:
            try:
                swbx = SwitchBox(face)
                switchboxes.append(swbx)
            except NoSwitchBox:
                continue
            else:
                try:
                    swbx.route(flags=[])
                except RoutingFailure:
                    swbx.flip_xy()
                    swbx.route(flags=["allow_routing_failure"])
                detailed_routes.extend(swbx.segments)

    if "draw" in flags:
        draw_scr, draw_tx, draw_font = draw_start(routing_bbox)
        for route in global_routes:
            for wire in route:
                wire.draw(draw_scr, draw_tx, flags)
        for swbx in switchboxes:
            swbx.draw(draw_scr, draw_tx, draw_font, flags=["draw_switchbox", "draw_routing"])
        draw_end()

    return detailed_routes
