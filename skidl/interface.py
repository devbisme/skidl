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

from builtins import str, super

from future import standard_library

from .alias import Alias
from .bus import Bus
from .net import Net
from .netpinlist import NetPinList
from .protonet import ProtoNet
from .pin import Pin
from .skidlbaseobj import SkidlBaseObject
from .utilities import *

standard_library.install_aliases()


class Interface(dict):
    """
    An Interface bundles a group of nets/buses into a single entity with each
    net/bus becoming an attribute.  An Interface is also usable as a dict
    where the attribute names serve as keys. This means the ** operator works
    on an Interface.
    """

    # Set the default ERC functions for all Interface instances.
    erc_list = []

    def __init__(self, *args, **kwargs):
        # dict is used instead of super() throughout because using super()
        # caused the tests to run forever under Python 2.7.18.
        dict.__init__(self, *args, **kwargs)
        dict.__setattr__(self, "match_pin_regex", False)
        for k, v in list(self.items()):
            if isinstance(v, ProtoNet):
                # Store the ProtoNet directly in the Interface.
                # It will get promoted to a Net when it gets connected to something.
                v.aliases += k
                setattr(self, k, v)
            elif isinstance(v, (Pin, Net)):
                cct = v.circuit
                n = Net(circuit=cct)
                n.aliases += k
                n += v
                setattr(self, k, n)
            elif isinstance(v, (Bus, NetPinList)):
                cct = v.circuit
                b = Bus(len(v), circuit=cct)
                b.aliases += k
                b += v
                setattr(self, k, b)
                for i in range(len(v)):
                    n = Net(circuit=cct)
                    n.aliases += k + str(i)
                    n += b[i]
                    setattr(self, k + str(i), n)
            elif isinstance(v, SkidlBaseObject):
                setattr(self, k, v)
            else:
                dict.__setattr__(self, k, v)

    def __getattribute__(self, key):
        value = dict.__getattribute__(self, key)
        if isinstance(value, ProtoNet):
            # If the retrieved attribute is a ProtoNet, record where it came from.
            value.intfc_key = key
            value.intfc = self
        return value

    def __setattr__(self, key, value):
        """Sets attribute and also a dict entry with a key using the attribute name."""
        dict.__setitem__(self, key, value)
        dict.__setattr__(self, key, value)

    def __getitem__(self, *io_ids, **criteria):
        """
        Return list of part pins selected by identifiers.

        Args:
            io_ids: A list of strings containing I/O names,
                regular expressions, slices, lists or tuples. If empty,
                then it will select all pins.

        Keyword Args:
            criteria: Key/value pairs that specify attribute values the
                I/Os must have in order to be selected.

        Returns:
            A list of I/Os matching the given IDs and satisfying all the criteria,
            or just a single I/O object if only a single match was found.
            Or None if no match was found.

        Notes:
            Pins can be selected from a part by using brackets like so::

                intf = Interface(a=Net(), b=Net())
                net = Net()
                intf['a'] += net  # Connects I/O 'a' of interface to the net.
                net += intf.b     # Connects the net to the 'b' I/O.
        """

        # Extract permission to search for regex matches in pin names/aliases.
        match_regex = criteria.pop("match_regex", False) or self.match_pin_regex

        # If no pin identifiers were given, then use a wildcard that will
        # select all pins.
        if not io_ids:
            io_ids = [".*"]
            match_regex = True

        # An interface doesn't have pins, so set pin slice bounds to zero.
        min_pin, max_pin = 0, 0

        # Get I/O entries.
        io_types = (Net, ProtoNet, Pin, NetPinList, Bus)
        ios = [io for io in self.values() if isinstance(io, io_types)]

        # Use this for looking up the dict key using the id of a given I/O.
        id_to_key = {id(v): k for k, v in self.items()}

        # Go through the I/O entries and find the ones selected by the IDs.
        selected_ios = NetPinList()
        for io_id in expand_indices(min_pin, max_pin, match_regex, *io_ids):

            # Look for an exact match of the I/O key name with the current ID.
            try:
                io = dict.__getitem__(self, io_id)
            except KeyError:
                # No exact match on I/O key name, so keep looking below.
                pass
            else:
                # Add exact match to the list of selected I/Os and go to the next ID.
                if isinstance(io, ProtoNet):
                    # Store key for this ProtoNet I/O so we'll know where to update it later.
                    io.intfc = self
                    io.intfc_key = io_id
                selected_ios.append(io)
                continue

            # Check I/O aliases for an exact match with the current ID.
            tmp_ios = filter_list(ios, aliases=io_id, do_str_match=True, **criteria)
            for io in tmp_ios:
                if isinstance(io, ProtoNet):
                    # Store key for this ProtoNet I/O so we'll know where to update it later.
                    io.intfc = self
                    io.intfc_key = id_to_key[id(io)]
                selected_ios.append(io)
            if tmp_ios:
                # Found exact match between alias and ID, so done with this ID and go to next ID.
                continue

            # Skip regex matching if not enabled.
            if not match_regex:
                continue

            # OK, ID doesn't exactly match an I/O name or alias. Does it match as a regex?
            tmp_ios = filter_list(ios, aliases=Alias(io_id), **criteria)
            for io in tmp_ios:
                if isinstance(io, ProtoNet):
                    # Store key for this ProtoNet I/O so we'll know where to update it later.
                    io.intfc = self
                    io.intfc_key = id_to_key[id(io)]
                selected_ios.append(io)

        # Return list of I/Os that were selected by the IDs.
        return list_or_scalar(selected_ios)

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
                rmv_attr(v, "iadd_flag")
        else:
            # This is for a straight assignment of value to key.
            setattr(self, key, value)
