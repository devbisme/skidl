# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Handles aliases for Circuit, Part, Pin, Net, Bus objects.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import re
from builtins import super

try:
    from future import standard_library

    standard_library.install_aliases()
except ImportError:
    pass

from .utilities import export_to_all, flatten


@export_to_all
class Alias(set):
    """
    Multiple aliases can be added to another object to give it other names.

    Args:
        aliases: A single string or a list of strings.
    """

    def __init__(self, *aliases):
        super().__init__(flatten(aliases))

    def __str__(self):
        """Return the aliases as a delimited string."""
        return "/".join(list(self))

    def __eq__(self, other):
        """
        Return true if both lists of aliases have at least one alias in common.

        Args:
            other: The Alias object which self will be compared to.
        """
        return bool(self.intersection(Alias(other)))

    def __iadd__(self, *aliases):
        """Add new aliases."""
        self.update(set(flatten(aliases)))
        self.clean()  # Remove any empty stuff that was added.
        return self

    def __isub__(self, *aliases):
        self.difference_update(flatten(aliases))
        return self

    def clean(self):
        """Remove any empty aliases."""
        self.discard(None)
        self.discard("")
