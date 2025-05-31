# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Supports user-specified notes that can be attached to other SKiDL objects.

This module provides the Note class that allows textual annotations to be
attached to various SKiDL objects such as parts, pins, nets, and buses.
Notes can be used for documentation purposes or to provide additional
information about design elements.
"""

from .utilities import export_to_all


@export_to_all
class Note(list):
    """
    Stores one or more strings as notes.
    
    The Note class extends the Python list to store textual annotations.
    Notes can be attached to SKiDL objects to provide additional information
    or documentation about the design.
    """

    def __init__(self, *notes):
        """
        Create a note object containing one or more text strings.

        Args:
            notes: Either a string or an iterable containing multiple strings.
                  Each string becomes an element in the Note list.

        Returns:
            A Note object containing note strings.
            
        Examples:
            note1 = Note("This is a note")
            note2 = Note("First line", "Second line")
            note3 = Note(["Line 1", "Line 2"])
        """
        super().__init__()
        self.__iadd__(*notes)

    def __str__(self):
        """
        Return notes as a concatenated set of strings.

        Returns:
            A string made up of the concatenated notes in the object joined by newlines.
            
        Examples:
            >>> print(Note("Line 1", "Line 2"))
            Line 1
            Line 2
        """
        return "\n".join(self)

    def __iadd__(self, *notes):
        """
        Add new notes to a Note object.

        Args:
            notes: Either a string or an iterable containing multiple strings.
                  These will be added to the existing notes.

        Returns:
            A Note object containing the original and new note strings.
            
        Examples:
            >>> n = Note("Original note")
            >>> n += "Additional note"
            >>> n += ["Multiple", "Notes"]
        """
        for note in notes:
            if isinstance(note, (tuple, list, set)):
                self.extend(note)
            else:
                self.append(note)
        return self
