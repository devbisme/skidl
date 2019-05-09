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
Object for for handling series and parallel networks of two-pin parts, nets, and pins.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from builtins import range
from future import standard_library
standard_library.install_aliases()
from .utilities import *


class Network(list):
    def __init__(self, *objs):
        """Create a Network object from a list of pins, nets, and parts."""
        super(Network, self).__init__()
        for obj in objs:
            try:
                ntwk = obj.create_network(
                )  # Create a Network from each object.
            except AttributeError:
                raise ValueError(
                    "Can't create a network from a {} object ({}).".format(
                        type(obj), obj.__name__))


            # Add the in & out ports of the object network to this network.
            self.extend(ntwk)

            # A Network cannot have more than two ports. But it may have only
            # one which will be used as both an input and an output. Or it may
            # have zero, in which case it is just an empty container waiting to
            # have ports added to it.
            if len(self) > 2:
                raise ValueError("A Network object can't have more than two nodes.")


    def __and__(self, obj):
        """Combine two networks by placing them in series."""

        # First, convert the object to a network.
        try:
            ntwk = obj.create_network()
        except AttributeError:
            raise ValueError(
                "Unable to create a Network from a {} object ({}).".format(
                    type(obj), obj.__name__))


        # Attach the output of the first network to the input of the second.
        # (Use -1 index to get the output port instead of 1 because the network
        # may only have a single port serving as both the input and output.)
        self[-1] += ntwk[0]

        # Return a network consisting of the input of the first and the output of the second.
        return Network(self[0], ntwk[-1])

    def __rand__(self, obj):
        """Combine two networks by placing them in series. (Reverse-ordered operation.)"""

        # Create a network from the first object and then place it in series with the second network.
        return Network(obj) & self

    def __or__(self, obj):
        """Combine two networks by placing them in parallel."""

        # First, convert the object to a network.
        try:
            ntwk = obj.create_network()
        except AttributeError:
            raise ValueError(
                "Unable to create a Network from a {} object ({}).".format(
                    type(obj), obj.__name__))

        # Attach the inputs of both networks and the outputs of both networks to
        # place them in parallel.
        self[0] += ntwk[0]
        self[-1] += ntwk[-1]

        # Just return one of the original networks since its I/O ports are attached to both.
        return self

    def create_network(self):
        """Creating a network from a network just returns the original network."""
        return self
