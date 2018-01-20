# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2018 by XESS Corp.
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

"""
Globals variables.
"""


try:
    import __builtin__ as builtins
except ImportError:
    import builtins

import skidl
from .defines import *
from .utilities import *


# Supported ECAD tools.
DEFAULT_TOOL = INITIAL_DEFAULT_TOOL = KICAD

def set_default_tool(tool):
    """Set the ECAD tool that will be used by default."""
    global DEFAULT_TOOL
    DEFAULT_TOOL = tool


# These are the paths to search for part libraries of the ECAD tools.
# Start off with a path that allows absolute file names, and then searches
# within the current directory.
lib_search_paths = {
    KICAD: ['', '.'],
    SKIDL: ['', '.']
}

# Add the location of the default KiCad schematic part libs to the search path.
try:
    lib_search_paths[KICAD].append(os.path.join(os.environ['KISYSMOD'], '..', 'library'))
except KeyError:
    logger.warning("KISYSMOD environment variable is missing, so default KiCad libraries won't be searched.")

# Add the location of the default SKiDL part libraries.
#from . import libs
#lib_search_paths[SKIDL].append(skidl.libs.__path__[0])


lib_suffixes = {
    KICAD: '.lib',
    SKIDL: '_sklib.py'
}

# Definitions for backup library of circuit parts.
BACKUP_LIB_NAME = get_script_name() + '_lib'
BACKUP_LIB_FILE_NAME = BACKUP_LIB_NAME + lib_suffixes[SKIDL]


QUERY_BACKUP_LIB = INITIAL_QUERY_BACKUP_LIB = True

def set_query_backup_lib(val):
    global _QUERY_BACKUP_LIB
    QUERY_BACKUP_LIB = val


backup_lib = None

def set_backup_lib(lib):
    global backup_lib
    backup_lib = lib


# Create the default Circuit object that will be used unless another is explicitly created.
builtins.default_circuit = skidl.Circuit()
# NOCONNECT net for attaching pins that are intentionally left open.
builtins.NC = default_circuit.NC  # pylint: disable=undefined-variable

# Create calls to functions on whichever Circuit object is the current default.
ERC = default_circuit.ERC                            # pylint: disable=undefined-variable
generate_netlist = default_circuit.generate_netlist  # pylint: disable=undefined-variable
generate_xml = default_circuit.generate_xml          # pylint: disable=undefined-variable
generate_graph = default_circuit.generate_graph      # pylint: disable=undefined-variable
backup_parts = default_circuit.backup_parts          # pylint: disable=undefined-variable

# Define a tag for nets that convey power (e.g., VCC or GND).
POWER = skidl.Pin.POWER_DRIVE
