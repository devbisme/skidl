# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.


from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import re
from builtins import range, super
from collections import Counter, defaultdict
from itertools import chain

from future import standard_library

from ..net import NCNet
from ..part import Part
from ..pin import Pin
from ..scriptinfo import get_script_name
from ..tools.kicad.constants import GRID
from ..tools.kicad.eeschema_v5 import Eeschema_V5, pin_label_to_eeschema
from ..utilities import export_to_all, rmv_attr
from .geometry import BBox, Point, Tx, Vector
from .place import PlacementFailure, Placer
from .route import Router, RoutingFailure

standard_library.install_aliases()

"""
Net_Terminal class for handling net labels.
"""

@export_to_all
class NetTerminal(Part):
    def __init__(self, net):
        """Specialized Part with a single pin attached to a net.

        This is intended for attaching to nets to label them, typically when
        the net spans across levels of hierarchical nodes.
        """

        from ..tools.kicad.kicad import calc_hier_label_bbox

        # Create a Part.
        from ..skidl import SKIDL

        super().__init__(name="NT", ref_prefix="NT", tool=SKIDL)

        # Set a default transformation matrix for this part.
        self.tx = Tx()

        # Add a single pin to the part.
        pin = Pin(num="1", name="~")
        self.add_pins(pin)

        # Set the pin at point (0,0) and pointing leftward toward the part body
        # (consisting of just the net label for this type of part) so any attached routing
        # will go to the right.
        pin.x, pin.y = 0, 0
        pin.pt = Point(pin.x, pin.y)
        pin.orientation = "L"

        # Calculate the bounding box, but as if the pin were pointed right so
        # the associated label text would go to the left.
        self.bbox = calc_hier_label_bbox(net.name, "R")

        # Resize bbox so it's an integer number of GRIDs.
        self.bbox = self.bbox.snap_resize(GRID)

        # Extend the bounding box a bit so any attached routing will come straight in.
        self.bbox.max += Vector(GRID, 0)
        self.lbl_bbox = self.bbox

        # Flip the NetTerminal horizontally if it is an output net (label on the right).
        netio = getattr(net, "netio", "").lower()
        self.orientation_locked = bool(netio in ("i", "o"))
        if getattr(net, "netio", "").lower() == "o":
            origin = Point(0, 0)
            term_origin = self.tx.origin
            self.tx = (
                self.tx.move(origin - term_origin).flip_x().move(term_origin - origin)
            )

        # Connect the pin to the net.
        pin += net

    def to_eeschema(self, tx):
        """Generate the EESCHEMA code for the net terminal.

        Args:
            tx (Tx): Transformation matrix for the node containing this net terminal.

        Returns:
            str: EESCHEMA code string.
        """
        self.pins[0].stub = True
        self.pins[0].orientation = "R"
        return pin_label_to_eeschema(self.pins[0], tx)
        # return pin_label_to_eeschema(self.pins[0], tx) + bbox_to_eeschema(self.bbox, self.tx * tx)
