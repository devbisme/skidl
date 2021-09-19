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

"""Class for PCBNEW net classes."""

from __future__ import absolute_import, division, print_function, unicode_literals

from builtins import object, str

from future import standard_library

from .common import *
from .logger import logger
from .utilities import *

standard_library.install_aliases()


class NetClass(object):
    def __init__(self, name, **attribs):

        # This object will belong to the default Circuit object or the one
        # that's passed as a parameter.
        circuit = attribs.pop("circuit", builtins.default_circuit)

        # Assign net class name.
        self.name = name

        # Assign the other attributes to this object.
        for k, v in list(attribs.items()):
            setattr(self, k, v)

        # Is this net class already defined?
        if circuit.netclasses.get(name) is not None:
            logger.warning(
                "Cannot redefine existing net class {name}!".format(**locals())
            )
        else:
            circuit.netclasses[name] = self
