# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Import this file to reconfigure SKiDL for doing SPICE simulations.

This module configures SKiDL to work with SPICE simulations by:
1. Importing necessary SPICE-related modules and classes
2. Setting up the default ground net
3. Loading SPICE-specific parts libraries
4. Making all PySpice parts available in the module namespace
"""

import sys

from .bus import Bus
from .group import subcircuit
from .interface import Interface
from .logger import active_logger
from .net import Net
from .part import TEMPLATE, Part
from .schlib import SchLib
from .skidl import (
    generate_netlist,
    generate_svg,
    lib_search_paths,
    reset,
    set_default_tool,
)
from .tools.spice import Parameters, XspiceModel, node

# InSpice may not be installed because of Python version.
try:
    from InSpice import *
    from InSpice.Unit import *
except ImportError:
    pass

from skidl import SKIDL, SPICE
from .tools.skidl.libs.pyspice_sklib import *

_splib = SchLib("pyspice", tool=SKIDL)  # Read-in the SPICE part library.

set_default_tool(SPICE)  # Set the library format for reading SKiDL libraries.

GND = gnd = Net("0")  # Instantiate the default ground net for SPICE.
gnd.fixed_name = True  # Make sure ground keeps it's name of "0" during net merges.

# Place all the PySpice parts into the namespace so they can be instantiated easily.
_this_module = sys.modules[__name__]
for p in _splib.get_parts():
    # Add the part name to the module namespace.
    setattr(_this_module, p.name, p)
    # Add all the part aliases to the module namespace.
    try:
        for alias in p.aliases:
            setattr(_this_module, alias, p)
    except AttributeError:
        pass
