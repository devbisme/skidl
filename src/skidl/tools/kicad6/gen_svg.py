# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Functions for generating SVG.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from future import standard_library

from skidl.utilities import export_to_all

standard_library.install_aliases()


@export_to_all
def gen_svg_comp(part, symtx, net_stubs=None):
    """
    Generate SVG for this component.

    Args:
        part: Part object for which an SVG symbol will be created.
        net_stubs: List of Net objects whose names will be connected to
            part symbol pins as connection stubs.
        symtx: String such as "HR" that indicates symbol mirroring/rotation.

    Returns: SVG for the part symbol."""

    raise NotImplementedError
