# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""SKiDL: A Python-Based Schematic Design Language

This module extends Python with the ability to design electronic
circuits. It provides classes for working with:

* Electronic parts (``Part``),
* Collections of part terminals (``Pin``) connected via wires (``Net``), and
* Groups of related nets (``Bus``).

Using these classes, you can concisely describe the interconnection of
parts using a flat or hierarchical structure.
A resulting Python script outputs a netlist that can be
imported into a PCB layout tool or Spice simulator.
The script can also
check the resulting circuitry for electrical rule violations.
"""
from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
from future import standard_library

# from . import tools
from .tools import *
from .alias import *
from .arrange import *
from .bus import *
from .circuit import *
from .common import *
from .config import *
from .erc import *
from .interface import *
from .logger import *
from .net import *
from .netclass import *
from .netlist_to_skidl import *
from .netpinlist import *
from .network import *
from .note import *
from .package import *
from .part import *
from .part_query import *
from .pin import *
from .protonet import *
from .schlib import *
from .skidl import *
from .skidlbaseobj import *
from .utilities import *

standard_library.install_aliases()
