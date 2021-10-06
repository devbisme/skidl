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
Specialized list for handling nets, pins, and buses.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from builtins import range

from future import standard_library

from .logger import logger
from .net import Net
from .network import Network
from .pin import Pin
from .protonet import ProtoNet
from .utilities import *

standard_library.install_aliases()


class NetPinList(list):
    def __iadd__(self, *nets_pins_buses):

        nets_pins_a = expand_buses(self)
        len_a = len(nets_pins_a)

        nets_pins_b = []
        for item in expand_buses(flatten(nets_pins_buses)):
            if isinstance(item, (Pin, Net, ProtoNet)):
                nets_pins_b.append(item)
            else:
                log_and_raise(
                    logger,
                    ValueError,
                    "Can't make connections to a {} ({}).".format(
                        type(item), item.__name__
                    ),
                )
        len_b = len(nets_pins_b)

        if len_a != len_b:
            if len_a > 1 and len_b > 1:
                log_and_raise(
                    logger,
                    ValueError,
                    "Connection mismatch {} != {}!".format(len_a, len_b),
                )

            # If just a single net is to be connected, make a list out of it that's
            # just as long as the list of pins to connect to. This will connect
            # multiple pins to the same net.
            if len_b == 1:
                nets_pins_b = [nets_pins_b[0] for _ in range(len_a)]
                len_b = len(nets_pins_b)
            elif len_a == 1:
                nets_pins_a = [nets_pins_a[0] for _ in range(len_b)]
                len_a = len(nets_pins_a)

        assert len_a == len_b

        # Connect the nets to the nets in the bus.
        for npa, npb in zip(nets_pins_a, nets_pins_b):
            if isinstance(npb, ProtoNet):
                npb += npa
            else:
                npa += npb

        # Set the flag to indicate this result came from the += operator.
        self.iadd_flag = True  # pylint: disable=attribute-defined-outside-init

        return self

    def create_network(self):
        """Create a network from a list of pins and nets."""

        return Network(*self)  # An error will occur if list has more than 2 items.

    def __and__(self, obj):
        """Attach a NetPinList and another part/pin/net in serial."""

        return Network(self) & obj

    def __rand__(self, obj):
        """Attach a NetPinList and another part/pin/net in serial."""

        return obj & Network(self)

    def __or__(self, obj):
        """Attach a NetPinList and another part/pin/net in parallel."""

        return Network(self) | obj

    def __ror__(self, obj):
        """Attach a NetPinList and another part/pin/net in parallel."""

        return obj | Network(self)

    def __len__(self):
        """Return the number of individual pins/nets in this interface."""
        return len(expand_buses(self))

    @property
    def width(self):
        """Return width, which is the same as using the len() operator."""
        return len(self)

    # Setting/clearing the do_erc flag for the list sets/clears the do_erc flags of the pins/nets in the list.
    @property
    def do_erc(self):
        raise NotImplementedError

    @do_erc.setter
    def do_erc(self, on_off):
        for pn in self:
            pn.do_erc = on_off

    @do_erc.deleter
    def do_erc(self):
        for pn in self:
            del pn.do_erc

    # Setting/clearing the drive strength for the list sets/clears the drive of the pins/nets in the list.
    @property
    def drive(self):
        raise NotImplementedError

    @do_erc.setter
    def drive(self, strength):
        for pn in self:
            pn.drive = strength

    @do_erc.deleter
    def drive(self):
        for pn in self:
            del pn.drive

    # Trying to set an alias attribute on a NetPinList is an error.
    # This prevents setting an alias on a list of two or more pins that
    # might be returned by the filter_list() utility.
    @property
    def aliases(self):
        raise NotImplementedError

    @aliases.setter
    def aliases(self, alias):
        raise NotImplementedError

    @aliases.deleter
    def aliases(self):
        raise NotImplementedError
