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
Handles aliases for Circuit, Part, Pin, Net, Bus, Interface objects.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import re
from builtins import str

from future import standard_library

from .utilities import *

standard_library.install_aliases()


class Alias(set):
    """
    Multiple aliases can be added to another object to give it other names.

    Args:
        aliases: A single string or a list of strings.
    """

    def __init__(self, *aliases):
        super(Alias, self).__init__()
        self.__iadd__(*aliases)

    def __iadd__(self, *aliases):
        """Add new aliases."""
        for alias in aliases:
            if isinstance(alias, (tuple, list, set)):
                for a in list(alias):
                    self.add(a)
            else:
                self.add(alias)
        return self

    def __str__(self):
        """Return the aliases as a delimited string."""
        return "/".join(list(self))

    def __eq__(self, other):
        """
        Return true if both lists of aliases have at least one alias in common.

        Args:
            other: The Alias object which self will be compared to.
        """
        return bool(self.intersection(other))
