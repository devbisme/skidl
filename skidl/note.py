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

"""
Supports user-specified notes that can be attached to other SKiDL objects.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from builtins import str, super

from future import standard_library

standard_library.install_aliases()


class Note(list):
    """Stores one or more strings as notes."""

    def __init__(self, *notes):
        """Create a note.

        Args:
            notes: Either a string or an iterable containing multiple strings.

        Returns:
            A Note object containing note strings.
        """
        super().__init__()
        self.__iadd__(*notes)

    def __iadd__(self, *notes):
        """Add new notes to a Note object.

        Args:
            notes: Either a string or an iterable containing multiple strings.

        Returns:
            A Note object containing note strings.
        """
        for note in notes:
            if isinstance(note, (tuple, list, set)):
                self.extend(note)
            else:
                self.append(note)
        return self

    def __str__(self):
        """Return notes as a concatenated set of strings.

        Returns:
            A string made up of the concatenated notes in the object joined by newlines.
        """
        return "\n".join(self)
