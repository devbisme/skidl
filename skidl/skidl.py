# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2016 by XESS Corp.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import os
from builtins import open, super

from future import standard_library

from . import tools  # Import EDA tool-specific stuff.
from .circuit import Circuit
from .common import *
from .defines import *
from .logger import erc_logger, get_script_name, logger
from .part_query import footprint_cache
from .pin import Pin
from .utilities import *

standard_library.install_aliases()


class SkidlCfg(dict):
    """Class for holding SKiDL configuration."""

    CFG_FILE_NAME = ".skidlcfg"

    def __init__(self, *dirs):
        super().__init__()
        self.load(*dirs)

    def load(self, *dirs):
        """Load SKiDL configuration from JSON files in given dirs."""
        for dir in dirs:
            path = os.path.join(dir, self.CFG_FILE_NAME)
            path = os.path.expanduser(path)
            path = os.path.abspath(path)
            try:
                with open(path) as cfg_fp:
                    merge_dicts(self, json.load(cfg_fp))
            except (FileNotFoundError, IOError):
                pass

    def store(self, dir="."):
        """Store SKiDL configuration as JSON in directory as .skidlcfg file."""
        path = os.path.join(dir, self.CFG_FILE_NAME)
        path = os.path.expanduser(path)
        path = os.path.abspath(path)
        with open(path, "w") as cfg_fp:
            json.dump(self, cfg_fp, indent=4)


def get_kicad_lib_tbl_dir():
    """Get the path to where the global fp-lib-table file is found."""

    paths = (
        "$HOME/.config/kicad",
        "~/.config/kicad",
        "%APPDATA%/kicad",
        "$HOME/Library/Preferences/kicad",
        "~/Library/Preferences/kicad",
    )
    for path in paths:
        path = os.path.normpath(os.path.expanduser(os.path.expandvars(path)))
        if os.path.lexists(path):
            return path
    return ""


###############################################################################
# Globals that are used by everything else.
###############################################################################

# Get SKiDL configuration.
skidl_cfg = SkidlCfg("/etc", "~", ".")

# If no configuration files were found, set some default lib search paths.
if "lib_search_paths" not in skidl_cfg:
    skidl_cfg["lib_search_paths"] = {tool: ["."] for tool in ALL_TOOLS}

    # Add the location of the default KiCad part libraries.
    try:
        skidl_cfg["lib_search_paths"][KICAD].append(os.environ["KICAD_SYMBOL_DIR"])
    except KeyError:
        logger.warning(
            "KICAD_SYMBOL_DIR environment variable is missing, so the default KiCad symbol libraries won't be searched."
        )

    # Add the location of the default SKiDL part libraries.
    default_skidl_libs = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "libs"
    )
    skidl_cfg["lib_search_paths"][SKIDL].append(default_skidl_libs)

# Shortcut to library search paths.
lib_search_paths = skidl_cfg["lib_search_paths"]

# If no configuration files were found, set some default footprint search paths.
if "footprint_search_paths" not in skidl_cfg:
    dir_ = get_kicad_lib_tbl_dir()
    skidl_cfg["footprint_search_paths"] = {tool: [dir_] for tool in ALL_TOOLS}

# Cause the footprint cache to be invalidated if the footprint search path changes.
def invalidate_footprint_cache(self, k, v):
    footprint_cache.reset()


skidl_cfg["footprint_search_paths"] = TriggerDict(skidl_cfg["footprint_search_paths"])
skidl_cfg["footprint_search_paths"].trigger_funcs[KICAD] = invalidate_footprint_cache

# Shortcut to footprint search paths.
footprint_search_paths = skidl_cfg["footprint_search_paths"]

# Set default toolset being used with SKiDL.
def set_default_tool(tool):
    """Set the ECAD tool that will be used by default."""
    skidl_cfg["default_tool"] = tool


def get_default_tool():
    return skidl_cfg["default_tool"]


if "default_tool" not in skidl_cfg:
    set_default_tool(KICAD)

# Make the various EDA tool library suffixes globally available.
lib_suffixes = tools.lib_suffixes

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
generate_xml = default_circuit.generate_xml
generate_schematic = default_circuit.generate_schematic
generate_svg = default_circuit.generate_svg
generate_graph = default_circuit.generate_graph
reset = default_circuit.reset
backup_parts = default_circuit.backup_parts

# Define a tag for nets that convey power (e.g., VCC or GND).
POWER = Pin.drives.POWER


def no_files(circuit=default_circuit):
    """Prevent creation of output files (netlists, ERC, logs) by this Circuit object."""
    circuit.no_files = True
    erc_logger.stop_file_output()
    logger.stop_file_output()
