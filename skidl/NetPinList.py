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
Specialized list for handling nets, pins, and buses.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from builtins import range
from future import standard_library
standard_library.install_aliases()
from .utilities import *


class NetPinList(list):
    def __iadd__(self, *nets_pins_buses):

        from .Net import Net
        from .Pin import Pin

        nets_pins = []
        for item in expand_buses(flatten(nets_pins_buses)):
            if isinstance(item, (Pin, Net)):
                nets_pins.append(item)
            else:
                logger.error("Can't make connections to a {} ({}).".format(
                    type(item), item.__name__))
                raise Exception

        if len(nets_pins) != len(self):
            if Net in [type(item) for item in self] or len(nets_pins) > 1:
                logger.error("Connection mismatch {} != {}!".format(
                    len(self), len(nets_pins)))
                raise Exception

            # If just a single net is to be connected, make a list out of it that's
            # just as long as the list of pins to connect to. This will connect
            # multiple pins to the same net.
            if len(nets_pins) == 1:
                nets_pins = [nets_pins[0] for _ in range(len(self))]

        # Connect the nets to the nets in the bus.
        for i, np in enumerate(nets_pins):
            self[i] += np

        # Set the flag to indicate this result came from the += operator.
        self.iadd_flag = True  # pylint: disable=attribute-defined-outside-init

        return self

    def create_network(self):
        """Create a network from a list of pins and nets."""
        from .Network import Network

        return Network(
            *self)  # An error will occur if list has more than 2 items.

    def __and__(self, obj):
        """Attach a NetPinList and another part/pin/net in serial."""
        from .Network import Network

        return Network(self) & obj

    def __rand__(self, obj):
        """Attach a NetPinList and another part/pin/net in serial."""
        from .Network import Network

        return obj & Network(self)

    def __or__(self, obj):
        """Attach a NetPinList and another part/pin/net in parallel."""
        from .Network import Network

        return Network(self) | obj

    def __ror__(self, obj):
        """Attach a NetPinList and another part/pin/net in parallel."""
        from .Network import Network

        return obj | Network(self)

    @property
    def width(self):
        """Return width, which is the same as using the len() operator."""
        return len(self)

    # Trying to set an alias attribute on a NetPinList is an error.
    # This prevents setting an alias on a list of two or more pins that
    # might be returned by the filter_list() utility.
    @property
    def alias(self):
        raise Exception

    @alias.setter
    def alias(self, alias):
        raise Exception

    @alias.deleter
    def alias(self):
        raise Exception
