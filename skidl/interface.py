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
from .bus import Bus
from .net import Net
from .netpinlist import NetPinList
from .protonet import ProtoNet
from .pin import Pin
from .skidlbaseobj import SkidlBaseObject
from .utilities import *

standard_library.install_aliases()


# class Interface(dict, SkidlBaseObject):
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
        self.circuit = kwargs.get("circuit", default_circuit)
        kwargs["circuit"] = self.circuit
        dict.__init__(self, *args, **kwargs)
        # SkidlBaseObject.__init__(self)
        dict.__setattr__(self, 'match_pin_regex', False)
        # self.match_pin_regex = False
        dict.__setattr__(self, 'ios', [])
        # self.ios = []
        for k, v in list(self.items()):
            if isinstance(v, (Pin, Net, ProtoNet)):
                n = Net(circuit=self.circuit)
                n.aliases += k
                n += v
                self.__setattr__(k, n)
                self.ios.append(n)
            elif isinstance(v, (Bus, NetPinList)):
                b = Bus(len(v), circuit=self.circuit)
                b.aliases += k
                b += v
                self.__setattr__(k, b)
                self.ios.append(b)
                for i in range(len(v)):
                    n = Net(circuit=self.circuit)
                    n.aliases += k + str(i)
                    n += b[i]
                    self.__setattr__(k + str(i), n)
                    self.ios.append(n)
            elif isinstance(v, SkidlBaseObject):
                self.__setattr__(k, v)
                # raise Exception(f"Strange object {type(v)}")

    # def __setattr__(self, key, value):
    #     """Sets attribute and also a dict entry with a key using the attribute name."""
    #     dict.__setitem__(self, key, value)
    #     dict.__setattr__(self, key, value)

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

    def get_ios(self, *io_ids, **criteria):
        """
        Return list of part pins selected by pin numbers or names.

        Args:
            io_ids: A list of strings containing pin names, numbers,
                regular expressions, slices, lists or tuples. If empty,
                then it will select all pins.

        Keyword Args:
            criteria: Key/value pairs that specify attribute values the
                pins must have in order to be selected.

        Returns:
            A list of pins matching the given IDs and satisfying all the criteria,
            or just a single Pin object if only a single match was found.
            Or None if no match was found.

        Notes:
            Pins can be selected from a part by using brackets like so::

                atmega = Part('atmel', 'ATMEGA16U2')
                net = Net()
                atmega[1] += net  # Connects pin 1 of chip to the net.
                net += atmega['RESET']  # Connects reset pin to the net.
        """

        from .netpinlist import NetPinList
        from .alias import Alias

        # Extract permission to search for regex matches in pin names/aliases.
        match_regex = criteria.pop("match_regex", False) or self.match_pin_regex

        # If no pin identifiers were given, then use a wildcard that will
        # select all pins.
        if not io_ids:
            io_ids = [".*"]
            match_regex = True

        # Determine the minimum and maximum pin ids if they don't already exist.
        if "min_pin" not in dir(self) or "max_pin" not in dir(self):
            # self.min_pin, self.max_pin = self._find_min_max_pins()
            self.min_pin, self.max_pin = 0, 1000

        # Go through the list of IO IDs one-by-one.
        ios = NetPinList()
        for io_id in expand_indices(self.min_pin, self.max_pin, match_regex, *io_ids):

            # Search IO names.

                # Check IO aliases for an exact match.
                tmp_ios = filter_list(
                    self.ios, aliases=io_id, do_str_match=True, **criteria
                )
                if tmp_ios:
                    ios.extend(tmp_ios)
                    continue

                # Skip regex matching if not enabled.
                if not match_regex:
                    continue

                # OK, pin ID is not a pin number and doesn't exactly match a pin
                # name or alias. Does it match as a regex?
                io_id_re = io_id

                # Check the IO names for a regex match.
                tmp_ios = filter_list(self.ios, name=io_id_re, **criteria)
                if tmp_ios:
                    ios.extend(tmp_ios)
                    continue

        return list_or_scalar(ios)

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
    __getitem__ = get_ios

    def __getattribute__(self, key):
        value = dict.__getattribute__(self, key)
        if isinstance(value, ProtoNet):
            # If the retrieved attribute is a ProtoNet, record where it came from.
            value.intfc_key = key
            value.intfc = self
        return value
