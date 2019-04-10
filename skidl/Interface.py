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
Handles interfaces for subsystems with complicated I/O.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import str
from future import standard_library
standard_library.install_aliases()

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

from .utilities import *


class Interface(object):
    """
    An Interface bundles a group of signals into a single entity with each
    signal becoming an attribute.
    """

    # Set the default ERC functions for all Interface instances.
    erc_list = []

    def __init__(self, prefix, circuit=None):

        self.circuit = None  # New interface is not a member of any circuit.
        self._name = None  # New interface has no assigned name.
        self.prefix = prefix  # Prefix string for this particular interface.

        # Set the Circuit object for the interface first because setting the
        # interface name requires a lookup of existing names in the circuit.
        # Add the interface to the passed-in circuit or to the default circuit.
        if circuit is None:
            circuit = builtins.default_circuit
        circuit += self  # Add the interface to the circuit. Also assigns name.

    def is_movable(self):
        return True

    def ERC(self, *args, **kwargs):
        """Run class-wide and local ERC functions on this interface."""

        exec_function_list(self, 'erc_list', *args, **kwargs)

    @property
    def name(self):
        """
        Get, set and delete the name of this interface.

        When setting the name, if another interface with the same name
        is found, the name for this interface is adjusted to make it unique.
        """
        return self._name

    @name.setter
    def name(self, name):
        # Remove the existing name so it doesn't cause a collision if the
        # object is renamed with its existing name.
        self._name = None

        # Now name the object with the given name or some variation
        # of it that doesn't collide with anything else in the list.
        self._name = get_unique_name(self.circuit.interfaces, 'name',
                                     self.prefix, name)

    @name.deleter
    def name(self):
        del self._name
