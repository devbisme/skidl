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
Handles aliases for parts and other stuff.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import str
from future import standard_library
standard_library.install_aliases()

import re

from .utilities import *


class Alias(object):
    """
    An alias can be added to another object to give it another name.
    Since an object might have several aliases, each alias can be tagged
    with an identifier to discriminate between them.

    Args:
        name: The alias name.
        id_tag: The identifier tag.
    """

    def __init__(self, name, id_tag=None):
        self.name = name
        self.id_ = id_tag

    def __str__(self):
        """Return the alias."""
        # This function was added to make filter_list simpler when searching
        # for an alias in a list of pins since the actual name is hidden
        # as an attribute of the Alias class.
        return str(self.name)

    def __eq__(self, other):
        """
        Return true if one alias is equal to another.

        The aliases are equal if the following conditions are both true::

            1. The ids must match or one or both ids must be something
                that evaluates to False (i.e., None, empty string or list, etc.).

            2. The names must match based on using one name as a
                regular expression to compare to the other.

        Args:
            other: The Alias object which self will be compared to.
        """
        return (not self.id_ or not other.id_ or other.id_ == self.id_) and \
            (fullmatch(str(other.name), str(self.name), flags=re.IGNORECASE) or
             fullmatch(str(self.name), str(other.name), flags=re.IGNORECASE))
