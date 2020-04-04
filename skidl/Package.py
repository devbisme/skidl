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
from copy import deepcopy

from future import standard_library

from .baseobj import SkidlBaseObject
from .Circuit import subcircuit
from .Interface import Interface
from .ProtoNet import ProtoNet

standard_library.install_aliases()

try:
    import __builtin__ as builtins
except ImportError:
    import builtins


class Package(SkidlBaseObject):

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        circuit = kwargs.pop("circuit", default_circuit)
        pckg = deepcopy(self)
        pckg.interface.update(kwargs)
        circuit += pckg
        return pckg.interface

def package(f):
    code = f.__code__
    num_args = code.co_argcount
    arg_names = code.co_varnames[:num_args]
    intfc = Interface()
    for arg_name in arg_names:
        intfc[arg_name] = ProtoNet(arg_name)
    pckg = Package()
    pckg.interface = intfc
    pckg.subcircuit = subcircuit(f)
    return pckg
