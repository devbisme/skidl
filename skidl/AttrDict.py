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
Dictionary class where dict entries are also accessible as attributes of the
dict or of another object.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from builtins import str
from copy import copy

from future import standard_library

standard_library.install_aliases()


class AttrDict(dict):
    """
    Create a dictionary where the entries are also accessible as attributes
    of the dictionary or some other object.

    Keyword Args:
        attr_obj: The object whose attributes will mirror the entries in
            the dictionary. If not specified, then the attributes of the
            dict will be used.
    """

    def __init__(self, *args, **kwargs):
        dict.__setattr__(self, "attr_obj", kwargs.pop("attr_obj", self))
        dict.__init__(self, *args, **kwargs)
        for k, v in list(self.items()):
            self.attr_obj.__setattr__(k, v)

    def _setattr_setitem(self, key, value):
        """Sets  value of attribute and dict entry for the given key."""
        dict.__setitem__(self, key, value)
        if self.attr_obj is self:
            dict.__setattr__(self, key, value)
        else:
            self.attr_obj.__setattr__(key, value)

    __setattr__ = _setattr_setitem
    __setitem__ = _setattr_setitem

    def __repr__(self):
        return "AttrDict({})".format(dict.__repr__(self))

    def copy(self, attr_obj):
        """Copy and set the object whose attributes will mirror the copy dict entires."""
        cpy = AttrDict(attr_obj=attr_obj)
        for k, v in self.items():
            cpy[k] = copy(v)
        return cpy

    def sync(self, *keys):
        """
        Sync the attribute values with the dictionary entries.

        Args:
            keys: List of keys to be synced between the object attributes and
                the dict entries. If no keys are given, then all the dict entries
                are synced.
        """

        # If the attribute object is the same as the dict, then the attributes and
        # dict entries are always synced. Syncing is only needed if the attribute
        # object is different from the dict object.
        if self.attr_obj is not self:
            # If no keys are specified, then use all the keys in the dict.
            keys = set(keys or list(self.keys()))

            # Remove any keys not found in the dict.
            keys = keys & set(self.keys())

            # Update the dict entries with the attribute values.
            for key in keys:
                dict.__setitem__(self, key, self.attr_obj.__getattribute__(key))
