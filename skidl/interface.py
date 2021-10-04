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
Handles interfaces for subsystems with complicated I/O.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from builtins import str

from future import standard_library

from .alias import Alias
from .protonet import ProtoNet
from .skidlbaseobj import SkidlBaseObject
from .utilities import *

standard_library.install_aliases()


class Interface(dict, SkidlBaseObject):
    """
    An Interface bundles a group of nets/buses into a single entity with each
    net/bus becoming an attribute.  An Interface is also usable as a dict
    where the attribute names serve as keys. This means the ** operator works
    on an Interface.
    """

    # Set the default ERC functions for all Interface instances.
    erc_list = []

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        for k, v in list(self.items()):
            dict.__setattr__(self, k, v)

    def __setattr__(self, key, value):
        """Sets attribute and also a dict entry with a key using the attribute name."""
        dict.__setitem__(self, key, value)
        dict.__setattr__(self, key, value)

    def __setitem__(self, key, value):
        """Sets dict entry and also creates attribute with the same name as the dict key."""
        if from_iadd(value):
            # If interface items are being changed as a result of += operator...
            for v in to_list(value):
                # Look for interface key name attached to each value.
                # Only ProtoNets should have them because they need to be
                # changed to a Net or Bus once they are connected to something.
                key = getattr(v, "intfc_key", None)
                if key:
                    # Set the ProtoNet in the interface entry with key to its new Net or Bus value.
                    dict.__setitem__(self, key, v)
                    dict.__setattr__(self, key, v)
            # The += flag in the values are no longer needed.
            rmv_attr(value, "iadd_flag")
        else:
            # This is for a straight assignment of value to key.
            dict.__setitem__(self, key, value)
            dict.__setattr__(self, key, value)

    def get_io(self, *io_ids):
        """
        Return list of I/O selected by names.

        Args:
            io_ids: A list of strings containing names, numbers,
                regular expressions, slices, lists or tuples. If empty,
                then it will select all pins.

        Returns:
            A list of ios matching the given IDs,
            or just a single object if only a single match was found.
            Or None if no match was found.
        """

        from .netpinlist import NetPinList

        # If no I/O identifiers were given, then use a wildcard that will
        # select all of them.
        if not io_ids:
            io_ids = [".*"]

        # Determine the minimum and maximum I/Os if they don't already exist.
        min_io = 0
        max_io = len(self)

        # Go through the list of I/Os one-by-one.
        ios = NetPinList()
        for io_id in expand_indices(min_io, max_io, False, *io_ids):
            try:
                # Look for an exact match of the ID.
                io = dict.__getitem__(self, io_id)
                if isinstance(io, ProtoNet):
                    # Store the key for this ProtoNet I/O so we'll know where to update it later.
                    io.intfc_key = io_id
                    io.intfc = self
                ios.append(io)
            except KeyError:
                # OK, I/O id is doesn't exactly match a name. Does it match a substring
                # within an I/O name? Store the I/Os in a named tuple with a 'name'
                # attribute to filter_list can be used to find matches.
                from collections import namedtuple

                IO_Net = namedtuple("IO", "name, net")
                io_nets = [IO_Net(k, v) for k, v in list(self.items())]
                io_id_re = "".join([".*", io_id, ".*"])
                for io in filter_list(io_nets, name=io_id_re):
                    if isinstance(io.net, ProtoNet):
                        # Store the key for this ProtoNet I/O so we'll know where to update it later.
                        io.net.intfc_key = io.name
                        io.net.intfc = self
                    ios.append(io.net)

                # No match found on I/O names, so search I/O aliases.
                if not ios:
                    for io_name, io_net in list(self.items()):
                        try:
                            if io_id in io_net.aliases:
                                if isinstance(io_net, ProtoNet):
                                    # Store the key for this ProtoNet I/O so we'll know where to update it later.
                                    io_net.intfc_key = io_name
                                    io_net.intfc = self
                                ios.append(io_net)
                        except AttributeError:
                            pass  # Ignore stuff without an aliases attribute.

        return list_or_scalar(ios)

    # Get I/Os from an interface using brackets, e.g. ['A, B'].
    __getitem__ = get_io

    def __getattribute__(self, key):
        value = dict.__getattribute__(self, key)
        if isinstance(value, ProtoNet):
            # If the retrieved attribute is a ProtoNet, record where it came from.
            value.intfc_key = key
            value.intfc = self
        return value
