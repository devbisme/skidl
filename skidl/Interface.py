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

from __future__ import absolute_import, division, print_function, unicode_literals

from builtins import str

from future import standard_library

from .baseobj import SkidlBaseObject

standard_library.install_aliases()


class Interface(dict, SkidlBaseObject):
    """
    An Interface bundles a group of nets/buses into a single entity with each
    net/bus becoming an attribute.  An Interface is also usable as a dict
    where the attribute names serve as keys. This means the ** operator works
    on an Interface.
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        for k, v in self.items():
            dict.__setattr__(self, k, v)

    def __setattr__(self, key, value):
        """Sets attribute and also a dict entry with a key using the attribute name."""
        dict.__setitem__(self, key, value)
        dict.__setattr__(self, key, value)

    def __setitem__(self, key, value):
        """Sets dict entry and also creates attribute with the same name as the dict key."""
        dict.__setitem__(self, key, value)
        dict.__setattr__(self, key, value)