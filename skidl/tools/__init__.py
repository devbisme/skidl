# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""
This package contains the handler functions for various EDA tools.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import os
import os.path
import sys

from future import standard_library

from .. import circuit, net, part, schlib

standard_library.install_aliases()

# Reference to this module used for insertion of ECAD tool variables.
this_module = sys.modules[__name__]

# List of all supported ECAD tools.
ALL_TOOLS = []

# Dict of library sufixes for each ECAD tool.
lib_suffixes = {}

# The ECAD tool directories will be found in this directory.
directory = os.path.dirname(__file__)

# Search for the EDA tool modules and import them.
for module_name in os.listdir(directory):

    # Only look for directories.
    if not os.path.isdir(os.path.join(directory, module_name)):
        continue

    # Avoid directories like __pycache__.
    if module_name.startswith("__"):
        continue

    # Import the module.
    mod = __import__(module_name, globals(), locals(), [], level=1)
    for k, v in mod.__dict__.items():
        if k.startswith("_"):
            continue
        this_module.__dict__[k] = v

    # Get some info from the imported module.
    try:
        tool_name = getattr(mod, "tool_name")
        lib_suffix = getattr(mod, "lib_suffix")
    except AttributeError:
        # Don't process files without a tool name. They're probably support files.
        continue

    ALL_TOOLS.append(tool_name)

    # Create a variable with an uppercase name that stores the tool name,
    # so variable KICAD will store "kicad".
    setattr(this_module, tool_name.upper(), tool_name)

    # Store library file suffix for this tool.
    lib_suffixes[tool_name] = lib_suffix

    # Make the methods for this tool available where they are needed.
    for class_, method in (
        (schlib.SchLib, "load_sch_lib"),
        (part.Part, "parse_lib_part"),
        (circuit.Circuit, "gen_netlist"),
        (part.Part, "gen_netlist_comp"),
        (net.Net, "gen_netlist_net"),
        (circuit.Circuit, "gen_pcb"),
        (circuit.Circuit, "gen_xml"),
        (part.Part, "gen_xml_comp"),
        (net.Net, "gen_xml_net"),
        (part.Part, "gen_svg_comp"),
        (circuit.Circuit, "gen_schematic"),
        (part.Part, "calc_bbox_comp"),
        (part.Part, "move_part"),
        (part.Part, "gen_part_eeschema"),
        (part.Part, "copy_pin_labels"),
        (part.Part, "rotate_power_pins"),
    ):
        try:
            setattr(class_, method + '_' + tool_name, getattr(mod, method))
        except AttributeError:
            pass  # No method implemented for this ECAD tool.
