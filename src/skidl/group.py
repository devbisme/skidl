# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Class and decorator to handle hierarchical grouping of circuit parts and nets..
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import functools
from builtins import str
from collections import Counter

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .utilities import export_to_all


__all__ = ["subcircuit"]


@export_to_all
class Group:
    """Class that supports hierarchical grouping of circuit parts and nets."""

    def __init__(self, name, **kwargs):
        self.name = name
        self.circuit = kwargs.pop("circuit", default_circuit) or default_circuit
        self.tag = kwargs.pop("tag", None)

    def __enter__(self):
        """Create a context for hierarchical grouping of parts and nets."""

        self.circuit.activate(self.name, self.tag)
        return self

    def __exit__(self, type, value, traceback):
        """Exit a hierarchical grouping context."""

        self.circuit.deactivate()


@export_to_all
def SubCircuit(f):
    """
    A @SubCircuit decorator is used to create hierarchical circuits.

    Args:
        f: The function containing SKiDL statements that represents a subcircuit.
    """

    @functools.wraps(f)
    def sub_f(*args, **kwargs):

        circuit = kwargs.pop("circuit", default_circuit)
        tag = kwargs.pop("tag", None)

        # Create a hierarchical group context and call the function within it.
        with Group(name=f.__name__, tag=tag, circuit=circuit):

            # Call the function to create whatever circuitry it handles.
            # The arguments to the function are usually nets to be connected to the
            # parts instantiated in the function, but they may also be user-specific
            # and have no effect on the mechanics of adding parts or nets although
            # they may direct the function as to what parts and nets get created.
            # Store any results it returns as a list. These results are user-specific
            # and have no effect on the mechanics of adding parts or nets.
            results = f(*args, **kwargs)

        return results

    return sub_f


# The decorator can also be called as "@subcircuit".
subcircuit = SubCircuit
