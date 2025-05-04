# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Alias module for SKiDL.

This module provides the Alias class which allows multiple names to be assigned
to SKiDL objects like Circuit, Part, Pin, Net, and Bus. Aliases enable objects to
be referenced by alternative names, making circuit design more flexible and expressive.
"""

try:
    from future import standard_library

    standard_library.install_aliases()
except ImportError:
    pass

from .utilities import export_to_all, flatten


@export_to_all
class Alias(set):
    """
    A collection of alternative names for SKiDL objects.
    
    The Alias class extends the Python set to store multiple name strings
    that can be used interchangeably to identify Circuit, Part, Pin, Net, and Bus objects.
    When comparing two Alias objects, they are considered equal if they share at least one alias.
    
    Args:
        *aliases: A string or multiple strings, or lists/tuples of strings to use as aliases.
    
    Examples:
        >>> part_aliases = Alias('resistor', 'res', 'R')
        >>> 'R' in part_aliases
        True
        >>> part_aliases += 'resistor_std'  # Add another alias
        >>> part_aliases -= 'res'  # Remove an alias
    """

    def __init__(self, *aliases):
        super().__init__(flatten(aliases))

    def __str__(self):
        """
        Return the aliases as a forward-slash delimited string.
        
        Returns:
            str: All aliases joined with '/' character.
        """
        return "/".join(list(self))

    def __eq__(self, other):
        """
        Check if self and other have at least one alias in common.
        
        Args:
            other: Another Alias object or something that can be converted to one.
            
        Returns:
            bool: True if there's at least one common alias, False otherwise.
        """
        return bool(self.intersection(Alias(other)))

    def __iadd__(self, *aliases):
        """
        Add new aliases to the existing set.
        
        Args:
            *aliases: One or more aliases to add.
            
        Returns:
            Alias: The updated Alias object.
        """
        self.update(set(flatten(aliases)))
        self.clean()  # Remove any empty stuff that was added.
        return self

    def __isub__(self, *aliases):
        """
        Remove aliases from the existing set.
        
        Args:
            *aliases: One or more aliases to remove.
            
        Returns:
            Alias: The updated Alias object.
        """
        self.difference_update(flatten(aliases))
        return self

    def clean(self):
        """
        Remove any empty aliases from the set.
        
        This removes None values and empty strings from the alias set.
        """
        self.discard(None)
        self.discard("")
