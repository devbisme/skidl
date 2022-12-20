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

# Dict of modules, one for each tool.
tool_modules = {}

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
    mod_dict = {k: v for k, v in mod.__dict__.items() if not k.startswith("_")}
    this_module.__dict__.update(mod_dict)

    # Get some info from the imported module.
    try:
        tool_name = getattr(mod, "tool_name")
        lib_suffix = getattr(mod, "lib_suffix")
    except AttributeError:
        # Don't process files without a tool name. They're probably support files.
        continue

    # Add tool module to dict.
    tool_modules[tool_name] = mod

    ALL_TOOLS.append(tool_name)

    # Create a variable with an uppercase name that stores the tool name,
    # so variable KICAD will store "kicad".
    setattr(this_module, tool_name.upper(), tool_name)

    # Store library file suffix for this tool.
    lib_suffixes[tool_name] = lib_suffix
