# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
SKiDL: A Python-Based Schematic Design Language

SKiDL is a module that allows you to compactly describe electronic
circuits using Python. The resulting Python program performs electrical rules
checking for common mistakes and outputs a netlist that serves as input to
a PCB layout tool.

SKiDL reads in libraries of electronic parts and converts them into
Python objects. The objects can be instantiated into components and connected
into a circuit using net objects. The circuit can be checked for
common errors automatically by the ERC (electrical rules checking)
module, and then a netlist can be generated for input to
a PCB layout tool.

Full documentation is available at https://devbisme.github.io/skidl

Here's a simple example of SKiDL used to describe a circuit with a resistor
and LED in series powered by a battery:

    import skidl
    from skidl import *

    # Create a resistor and LED.
    r1 = Part('Device', 'R', value='1K')  # Create a 1K resistor.
    led = Part('Device', 'LED')           # Create a LED.

    # Create a battery.
    bat = Part('Device', 'Battery_Cell')

    # Connect the components.
    vcc = Net('VCC')      # Net for VCC.
    gnd = Net('GND')      # Net for ground.
    vcc += bat['+']       # Connect the battery positive terminal to VCC.
    gnd += bat['-']       # Connect the battery negative terminal to GND.
    vcc += r1[1]          # Connect one end of the resistor to VCC.
    r1[2] += led['A']     # Connect the other end to the LED anode.
    led['K'] += gnd       # Connect the LED cathode to GND.

    # Output the netlist to a file.
    generate_netlist()
"""

from .pckg_info import __version__
from .alias import Alias  # Class for creating aliases for part names
from .bus import Bus  # Class for managing groups of related nets
from .circuit import Circuit  # Circuit management
from .node import Group, SubCircuit, subcircuit  # Grouping related components
from .interface import Interface  # Standardized connections between subcircuits
from .logger import erc_logger  # Logger for ERC (Electrical Rule Checking)
from .net import Net  # Class for electrical connections between pins
from .design_class import PartClass  # Class for assigning properties to groups of parts
from .design_class import NetClass  # Class for assigning properties to groups of nets
from .netlist_to_skidl import netlist_to_skidl  # Function to import netlists
from .network import Network, tee  # Network management and connection splitting
from .part import LIBRARY, NETLIST, TEMPLATE, Part, PartTmplt, SkidlPart  # Component handling
from .part_query import (  # Component search and visualization functions
    search,
    search_footprints,
    search_footprints_iter,
    search_parts,
    search_parts_iter,
    show,
    show_footprint,
    show_part,
)
from .pin import Pin  # Class for component connection points
from .schlib import SchLib, load_backup_lib  # Schematic library management
from .skidl import (  # Core SKiDL functionality
    ERC,
    POWER,
    backup_parts,
    config,
    empty_footprint_handler,
    erc_assert,
    footprint_search_paths,
    generate_graph,
    generate_dot,
    generate_netlist,
    generate_pcb,
    generate_schematic,
    generate_svg,
    generate_xml,
    lib_search_paths,
    no_files,
    reset,
    get_default_tool,
    set_default_tool,
    KICAD,  # References the latest version of KiCad.
)
from .utilities import Rgx  # Regular expression utilities
from . import scripts  # Necessary to get access to netlist_to_skidl_main.
