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
Prototype of a net which can become a Net or a Bus depending upon what is connected to it.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from builtins import range

from future import standard_library

from .Bus import Bus
from .logger import logger
from .Net import Net
from .Pin import Pin
from .utilities import *

standard_library.install_aliases()


class ProtoNet(object):
    def __init__(self, name=None):
        self._name = name

    def __iadd__(self, *nets_pins_buses):

        nets_pins = []
        for item in expand_buses(flatten(nets_pins_buses)):
            if isinstance(item, (Pin, Net)):
                nets_pins.append(item)
            else:
                log_and_raise(
                    logger,
                    ValueError,
                    "Can't make connections to a {} ({}).".format(
                        type(item), item.__name__
                    ),
                )

        sz = len(nets_pins)
        if sz == 0:
            log_and_raise(
                logger,
                ValueError,
                "Connecting empty set of pins, nets, busses to a {}".format(
                    self.__class__.__name__
                ),
            )
        elif sz == 1:
            n = Net(self._name)
            n += nets_pins[0]
            return n
        else:
            b = Bus(self._name, sz)
            b += nets_pins
            return b
