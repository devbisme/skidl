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
Installs handlers for various EDA tools.
"""

import os
import os.path
from .. import SchLib
from .. import Circuit
from .. import Part

lib_suffixes = {}

# The ECAD tool directories will be found in this directory.
directory = os.path.dirname(__file__)

# Search for the EDA tool modules and import them.
for module in os.listdir(directory):

    # Avoid directories like __pycache__.
    if module.startswith('__'):
        continue

    module_name, module_ext = os.path.splitext(os.path.basename(module))

    # Don't import anything but Python files.
    if module_ext not in ('.py',):
        continue

    # Import the module.
    mod = __import__(module_name, globals(), locals(), [], level=1)

    # Get some info from the imported module.
    tool_name = getattr(mod, 'tool_name')
    lib_suffix = getattr(mod, 'lib_suffix')

    # Store
    lib_suffixes[tool_name] = lib_suffix

    for class_, method in (
            (SchLib.SchLib, '_load_sch_lib_'),
            (Circuit.Circuit, '_gen_netlist_'),
            (Circuit.Circuit, '_gen_xml_'),
            (Part.Part, '_parse_'),
            (Part.Part, '_gen_netlist_comp_'),
            (Part.Part, '_gen_xml_comp_'),
            ):
        try:
            setattr(class_, method+tool_name, getattr(mod, method))
        except AttributeError:
            pass  # No method implemented for this ECAD tool.
