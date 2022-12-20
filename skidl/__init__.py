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
from .circuit import HIER_SEP, Circuit
from .group import Group, SubCircuit, subcircuit
from .interface import Interface
from .logger import erc_logger
from .net import Net
from .netclass import NetClass
from .netlist_to_skidl import netlist_to_skidl
from .network import Network, tee
from .package import Package, package
from .part import LIBRARY, NETLIST, TEMPLATE, Part, PartTmplt, SkidlPart
from .part_query import (
    search,
    search_footprints,
    search_footprints_iter,
    search_parts,
    search_parts_iter,
    show,
    show_footprint,
    show_part,
)
from .pin import Pin
from .schlib import SchLib
from .skidl import (
    ERC,
    POWER,
    backup_parts,
    erc_assert,
    footprint_search_paths,
    generate_graph,
    generate_netlist,
    generate_pcb,
    generate_schematic,
    generate_svg,
    generate_xml,
    get_backup_lib,
    get_default_tool,
    get_query_backup_lib,
    lib_search_paths,
    load_backup_lib,
    no_files,
    reset,
    set_backup_lib,
    set_default_tool,
    set_query_backup_lib,
)
from .tools import KICAD, SKIDL, SPICE, node

standard_library.install_aliases()
