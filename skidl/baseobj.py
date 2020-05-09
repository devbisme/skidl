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
Base object for Circuit, Interface, Package, Part, Net, Bus, Pin objects.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import re
from builtins import object, str, super
from copy import deepcopy

from future import standard_library

from .Alias import Alias
from .AttrDict import AttrDict
from .Note import Note
from .utilities import exec_function_list, eval_stmnt_list

standard_library.install_aliases()


class SkidlBaseObject(object):
    def __init__(self):
        self.fields = AttrDict(attr_obj=self)

    def __setattr__(self, key, value):
        if key == "fields":
            # Whatever is assigned to the fields attribute is cast to an AttrDict.
            super().__setattr__(key, AttrDict(attr_obj=self, **value))

        else:
            super().__setattr__(key, value)

            # Whenever an attribute is changed, then also sync it with the fields dict
            # in case it is mirroring one of the dict entries.
            self.fields.sync(key)

    @property
    def aliases(self):
        try:
            return self._aliases
        except AttributeError:
            return Alias([])  # No aliases, so just return an empty list.

    @aliases.setter
    def aliases(self, name_or_list):
        if not name_or_list:
            return
        self._aliases = Alias(name_or_list)

    @aliases.deleter
    def aliases(self):
        try:
            del self._aliases
        except AttributeError:
            pass

    @property
    def notes(self):
        try:
            return self._notes
        except AttributeError:
            return Note([])  # No notes, so just return empty list.

    @notes.setter
    def notes(self, text_or_notes):
        if not text_or_notes:
            return
        self._notes = Note(text_or_notes)

    @notes.deleter
    def notes(self):
        try:
            del self._notes
        except AttributeError:
            pass

    def copy(self):
        cpy = SkidlBaseObject()
        cpy.fields = deepcopy(self.fields)
        try:
            cpy.aliases = deepcopy(self.aliases)
        except AttributeError:
            pass
        try:
            cpy.notes = deepcopy(self.notes)
        except AttributeError:
            pass
        return cpy

    def ERC(self, *args, **kwargs):
        """Run ERC functions on this object."""

        exec_function_list(self, "erc_list", *args, **kwargs)

    def ERC_asserts(self, *args, **kwargs):
        """Run ERC assertions on this object."""
        eval_stmnt_list(self, "erc_assertion_list")
