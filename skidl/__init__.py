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

from .skidl import *
from .netlist_to_skidl import *
