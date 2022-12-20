# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import os
import sys
from builtins import open

from future import standard_library

from .circuit import Circuit
from .common import builtins
from .config import SkidlConfig
from .logger import get_script_name, stop_log_file_output
from .part import default_empty_footprint_handler
from .pin import Pin
from .tools import KICAD, SKIDL, lib_suffixes
from .utilities import norecurse

standard_library.install_aliases()

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
skidl_cfg = SkidlConfig()
lib_search_paths = skidl_cfg["lib_search_paths"]
footprint_search_paths = skidl_cfg["footprint_search_paths"]

# Set default toolset being used with SKiDL.
def set_default_tool(tool):
    """Set the ECAD tool that will be used by default."""
    skidl_cfg["default_tool"] = tool


def get_default_tool():
    return skidl_cfg["default_tool"]


if "default_tool" not in skidl_cfg:
    set_default_tool(KICAD)

# Definitions for backup library of circuit parts.
BACKUP_LIB_NAME = get_script_name() + "_lib"
BACKUP_LIB_FILE_NAME = BACKUP_LIB_NAME + lib_suffixes[SKIDL]

# Boolean controls whether backup lib will be searched for missing parts.
QUERY_BACKUP_LIB = INITIAL_QUERY_BACKUP_LIB = True


def set_query_backup_lib(val):
    """Set the boolean that controls searching for the backup library."""
    global QUERY_BACKUP_LIB
    QUERY_BACKUP_LIB = val


def get_query_backup_lib():
    return QUERY_BACKUP_LIB


# Backup lib for storing parts in a Circuit.
backup_lib = None


def set_backup_lib(lib):
    """Set the backup library."""
    global backup_lib
    backup_lib = lib


def get_backup_lib():
    return backup_lib


@norecurse
def load_backup_lib():
    """Load a backup library that stores the parts used in the circuit."""

    global backup_lib

    # Don't keep reloading the backup library once it's loaded.
    if not backup_lib:
        try:
            # The backup library is a SKiDL lib stored as a Python module.
            exec(open(BACKUP_LIB_FILE_NAME).read())
            # Copy the backup library in the local storage to the global storage.
            backup_lib = locals()[BACKUP_LIB_NAME]

        except (FileNotFoundError, ImportError, NameError, IOError):
            pass

    return backup_lib


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

empty_footprint_handler = default_empty_footprint_handler

# Define a tag for nets that convey power (e.g., VCC or GND).
POWER = Pin.drives.POWER


def no_files(circuit=default_circuit):
    """Prevent creation of output files (netlists, ERC, logs) by this Circuit object."""
    circuit.no_files = True
    stop_log_file_output()
