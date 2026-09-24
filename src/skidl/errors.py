# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Exceptions raised by SKiDL.

Schematic generation is done by the separate ``schematizer`` package, but
``Circuit.generate_schematic()`` translates its failures into the types defined
here so SKiDL callers only ever have to catch SKiDL's own exceptions.
"""

from .utilities import export_to_all


@export_to_all
class PlacementFailure(Exception):
    """Raised when the parts of a schematic cannot be placed."""

    pass


@export_to_all
class RoutingFailure(Exception):
    """Raised when the nets connecting the pins of a schematic cannot be routed."""

    pass
