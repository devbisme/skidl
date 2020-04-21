# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2020 by XESS Corp.
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
Package a subcircuit so it can be used like a Part.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from builtins import range
from copy import copy

from future import standard_library

from .Circuit import subcircuit
from .Interface import Interface
from .ProtoNet import ProtoNet

standard_library.install_aliases()

try:
    import __builtin__ as builtins
except ImportError:
    import builtins


class Package(Interface):
    def __init__(self, **kwargs):
        # Don't use update(). It doesn't seem to call __setitem__.
        for k,v in kwargs.items():
            self[k] = v  # Use __setitem__ so both dict item and attribute are created.

    def __call__(self, *args, **kwargs):
        """Create a copy of a package."""

        # Get circuit that will contain the package subcircuitry.
        circuit = kwargs.pop("circuit", default_circuit)

        pckg = Package(**self.copy())  # Create a shallow copy of the package.
        # Don't use update(). It doesn't seem to call __setitem__.
        for k,v in kwargs.items():
            pckg[k] = v  # Use __setitem__ so both dict item and attribute are created.
        pckg.subcircuit = self.subcircuit  # Assign subcircuit creation function.
        del pckg['subcircuit']  # Remove creation function so it's not passed as a parameter. 
        circuit += pckg  # Add package to circuit.

        return pckg


def package(subcirc_func):
    """Decorator that creates a package for a subcircuit routine."""

    pckg = Package()  # Create the package.

    # Store the parameter names passed to the subcircuit.
    code = subcirc_func.__code__
    num_args = code.co_argcount
    arg_names = code.co_varnames[:num_args]
    for arg_name in arg_names:
        # Adding an arg name adds it to both dict and as an attribute.
        pckg[arg_name] = ProtoNet(arg_name)

    # Remove the subcircuit key from the dict so it won't be passed to subcirc_f().
    pckg.subcircuit = subcircuit(subcirc_func)
    del pckg['subcircuit']

    return pckg
