# -*- coding: utf-8 -*-

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
from __future__ import absolute_import, division, print_function, unicode_literals

from future import standard_library

from . import tools
from .Alias import *
from .baseobj import *
from .Bus import *
from .Circuit import *
from .common import *
from .defines import *
from .erc import *
from .Interface import *
from .logger import *
from .Net import *
from .netclass import *
from .netlist_to_skidl import *
from .NetPinList import *
from .Network import *
from .Note import *
from .Package import *
from .Part import *
from .part_query import *
from .Pin import *
from .ProtoNet import *
from .SchLib import *
from .skidl import *
from .utilities import *

standard_library.install_aliases()
