# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import sys
from builtins import open

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .circuit import Circuit
from .common import builtins
from .config_ import SkidlConfig
from .part import default_empty_footprint_handler
from .pin import Pin
from .utilities import export_to_all


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
    "reset",
    "backup_parts",
    "empty_footprint_handler",
    "POWER",
]

try:
    # Set char encoding to UTF-8 in Python 2.
    reload(sys)  # Causes exception in Python 3.
    sys.setdefaultencoding("utf8")
except NameError:
    # Do nothing with char encoding in Python 3.
    pass


###############################################################################
# Globals that are used by everything else.
###############################################################################

# Get SKiDL configuration and set global search paths.
config = SkidlConfig()
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
reset = default_circuit.reset
backup_parts = default_circuit.backup_parts
no_files = default_circuit.no_files

empty_footprint_handler = default_empty_footprint_handler

# Define a tag for nets that convey power (e.g., VCC or GND).
POWER = Pin.drives.POWER


@export_to_all
def get_default_tool():
    """Get the ECAD tool that will be used by default."""
    return config.tool

@export_to_all
def set_default_tool(tool):
    """Set the ECAD tool that will be used by default."""
    config.tool = tool
