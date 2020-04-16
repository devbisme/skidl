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
from .utilities import *

standard_library.install_aliases()

try:
    import __builtin__ as builtins
except ImportError:
    import builtins


class Package(Interface):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        circuit = kwargs.pop("circuit", default_circuit)
        pckg = deepcopy(self)
        pckg.update(kwargs)
        circuit += pckg
        return pckg

    def get_io(self, *io_ids, **criteria):
        """
        Return list of part pins selected by pin numbers or names.

        Args:
            io_ids: A list of strings containing names, numbers,
                regular expressions, slices, lists or tuples. If empty,
                then it will select all pins.

        Keyword Args:
            criteria: Key/value pairs that specify attribute values the
                ios must have in order to be selected.

        Returns:
            A list of ios matching the given IDs and satisfying all the criteria,
            or just a single object if only a single match was found.
            Or None if no match was found.
        """

        from .NetPinList import NetPinList
        from .Alias import Alias

        # If no I/O identifiers were given, then use a wildcard that will
        # select all of them.
        if not io_ids:
            io_ids = [".*"]

        # Determine the minimum and maximum I/Os if they don't already exist.
        min_io = 0
        max_io = len(self.keys())

        # Go through the list of I/Os one-by-one.
        ios = NetPinList()
        io_nets = self.values()
        for io_id in expand_indices(min_io, max_io, *io_ids):
            # OK, assume it's a pin name. Look for an exact match.
            tmp_ios = filter_list(
                io_nets, name=io_id, do_str_match=True, **criteria
            )
            if tmp_ios:
                ios.extend(tmp_ios)
                continue

            # OK, I/O id is doesn't exactly match a pin
            # name or alias. Does it match a substring within an I/O name?
            io_id_re = "".join([".*", io_id, ".*"])
            tmp_ios = filter_list(io_nets, name=io_id_re, **criteria)
            if tmp_ios:
                ios.extend(tmp_ios)
                continue

        return list_or_scalar(ios)


    # Get I/Os from a package using brackets, e.g. [1,5:9,'A[0-9]+'].
    __getitem__ = get_io


def package(f):
    pckg = Package()
    code = f.__code__
    num_args = code.co_argcount
    arg_names = code.co_varnames[:num_args]
    for arg_name in arg_names:
        pckg[arg_name] = ProtoNet(arg_name)
    pckg.subcircuit = subcircuit(f)
    del pckg['subcircuit']
    return pckg
