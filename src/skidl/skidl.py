# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
SKiDL: A Python-Based Schematic Design Language

This module is the main entry point for SKiDL and provides global functions
and configuration for creating electronic circuit designs programmatically.
It initializes the default circuit and provides functions that operate on it.
"""

import builtins
import sys

from .circuit import Circuit
from .config_ import SkidlConfig
from .part import default_empty_footprint_handler
from .pin import pin_drives
from .utilities import export_to_all
from skidl import KICAD9


__all__ = [
    "config",
    "lib_search_paths",
    "footprint_search_paths",
    "ERC",
    "erc_assert",
    "generate_netlist",
    "generate_pcb",
    "generate_xml",
    "generate_schematic",
    "generate_svg",
    "generate_graph",
    "generate_dot",
    "reset",
    "backup_parts",
    "empty_footprint_handler",
    "POWER",
    "KICAD",
]


###############################################################################
# Globals that are used by everything else.
###############################################################################

# Get SKiDL configuration and set global search paths.
KICAD = KICAD9 # Reference to the latest version of KiCad.
config = SkidlConfig(KICAD) # Sets default tool.
lib_search_paths = config.lib_search_paths
footprint_search_paths = config.footprint_search_paths

# Create the default Circuit object that will be used unless another is explicitly created.
builtins.default_circuit = Circuit()

# NOCONNECT net for attaching pins that are intentionally left open.
builtins.NC = default_circuit.NC  # pylint: disable=undefined-variable

# Create calls to functions on whichever Circuit object is the current default.
ERC = default_circuit.ERC
erc_assert = default_circuit.add_erc_assertion
generate_netlist = default_circuit.generate_netlist
generate_pcb = default_circuit.generate_pcb
generate_xml = default_circuit.generate_xml
generate_schematic = default_circuit.generate_schematic
generate_svg = default_circuit.generate_svg
generate_graph = default_circuit.generate_graph
generate_dot = generate_graph
reset = default_circuit.reset
backup_parts = default_circuit.backup_parts
no_files = default_circuit.no_files

empty_footprint_handler = default_empty_footprint_handler

# Define a tag for nets that convey power (e.g., VCC or GND).
POWER = pin_drives.POWER


@export_to_all
def get_default_tool():
    """
    Get the ECAD tool that will be used by default.
    
    Returns:
        The currently configured default ECAD tool.
    """
    return config.tool


@export_to_all
def set_default_tool(tool):
    """
    Set the ECAD tool that will be used by default.
    
    Args:
        tool: The ECAD tool to use as the default.
    """
    config.tool = tool
