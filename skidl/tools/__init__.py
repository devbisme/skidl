# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (c) 2016-2021, Dave Vandenbout.
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
This package contains the handler functions for various EDA tools.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import os.path

from future import standard_library

from .. import circuit, net, part, schlib

standard_library.install_aliases()


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

    # Get some info from the imported module.
    try:
        tool_name = getattr(mod, "tool_name")
        lib_suffix = getattr(mod, "lib_suffix")
    except AttributeError:
        # Don't process files without a tool name. They're probably support files.
        continue

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
        (part.Part, "gen_pinboxes"),
    ):
        try:
            setattr(class_, "_".join(("", method, tool_name)), getattr(mod, method))
        except AttributeError:
            pass  # No method implemented for this ECAD tool.
