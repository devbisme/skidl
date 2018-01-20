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

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import super  # pylint: disable=redefined-builtin
from builtins import open  # pylint: disable=redefined-builtin
from builtins import int  # pylint: disable=redefined-builtin
from builtins import dict  # pylint: disable=redefined-builtin
from builtins import str  # pylint: disable=redefined-builtin
from builtins import zip  # pylint: disable=redefined-builtin
from builtins import range  # pylint: disable=redefined-builtin
from builtins import object  # pylint: disable=redefined-builtin
from future import standard_library
standard_library.install_aliases()

from .py_2_3 import *  # pylint: disable=wildcard-import
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
from .globals import *
from .defines import *




##############################################################################


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
