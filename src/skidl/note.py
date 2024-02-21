# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Supports user-specified notes that can be attached to other SKiDL objects.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from builtins import str, super

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .utilities import export_to_all



@export_to_all
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

    def __str__(self):
        """Return notes as a concatenated set of strings.

        Returns:
            A string made up of the concatenated notes in the object joined by newlines.
        """
        return "\n".join(self)

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
