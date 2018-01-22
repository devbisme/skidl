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

"""
SKiDL: A Python-Based Schematic Design Language

This module extends Python with the ability to design electronic
circuits. It provides classes for working with **1)** electronic parts (``Part``),
**2)** collections of part terminals (``Pin``) connected via wires (``Net``), and
**3)** groups of related nets (``Bus``). Using these classes, you can
concisely describe the interconnection of components using a linear
and/or hierarchical structure. It also provides the capability to
check the resulting circuitry for the violation of electrical rules.
The output of a SKiDL-enabled Python script is a netlist that can be
imported into a PCB layout tool.
"""


from .py_2_3 import *  # pylint: disable=wildcard-import
from .defines import *
from .utilities import *  # pylint: disable=wildcard-import
from .SchLib import *
from .Pin import *
from .Alias import *
from .Part import *
from .Net import *
from .Bus import *
from .NetPinList import *
from .Circuit import *
from .part_query import *


###############################################################################
# Globals that are used by everything else.
###############################################################################


# Supported ECAD tools.
DEFAULT_TOOL = INITIAL_DEFAULT_TOOL = KICAD
print('Initializing DEFAULT_TOOL =', DEFAULT_TOOL)

def set_default_tool(tool):
    """Set the ECAD tool that will be used by default."""
    global DEFAULT_TOOL
    DEFAULT_TOOL = tool

def get_default_tool():
    return DEFAULT_TOOL


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
default_skidl_libs = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs')
lib_search_paths[SKIDL].append(default_skidl_libs)

# Library suffixes for the various ECAD tools.
lib_suffixes = {
    KICAD: '.lib',
    SKIDL: '_sklib.py'
}

# Definitions for backup library of circuit parts.
BACKUP_LIB_NAME = get_script_name() + '_lib'
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
ERC = default_circuit.ERC                            # pylint: disable=undefined-variable
generate_netlist = default_circuit.generate_netlist  # pylint: disable=undefined-variable
generate_xml = default_circuit.generate_xml          # pylint: disable=undefined-variable
generate_graph = default_circuit.generate_graph      # pylint: disable=undefined-variable
backup_parts = default_circuit.backup_parts          # pylint: disable=undefined-variable

# Define a tag for nets that convey power (e.g., VCC or GND).
POWER = Pin.POWER_DRIVE
