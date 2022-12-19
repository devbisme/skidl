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

from .alias import Alias
from .bus import Bus
from .circuit import Circuit, HIER_SEP
from .group import Group, SubCircuit, subcircuit
from .interface import Interface
from .logger import erc_logger
from .net import Net
from .netclass import NetClass
from .netlist_to_skidl import netlist_to_skidl
from .network import Network, tee
from .package import Package, package
from .part import Part, PartTmplt, SkidlPart, NETLIST, LIBRARY, TEMPLATE
from .part_query import search, show, search_parts_iter, search_parts, show_part, search_footprints_iter, search_footprints, show_footprint
from .pin import Pin
from .schlib import SchLib
from .skidl import lib_search_paths, footprint_search_paths, set_default_tool, get_default_tool, set_query_backup_lib, get_query_backup_lib, set_backup_lib, get_backup_lib, load_backup_lib, ERC, erc_assert, generate_netlist, generate_pcb, generate_xml, generate_schematic, generate_svg, generate_graph, reset, backup_parts, POWER, no_files
from .tools import KICAD, SKIDL, SPICE, node

standard_library.install_aliases()
