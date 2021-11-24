# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

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

from future import standard_library

from .common import builtins
from .logger import active_logger, erc_logger
from .utilities import *


standard_library.install_aliases()


class Group:
    """Class that supports hierarchical grouping of circuit parts and nets."""

    group_name_cntr = Counter()

    @classmethod
    def reset(cls):
        cls.group_name_cntr.clear()

    def __init__(self, name, **kwargs):
        self.name = name
        self.circuit = kwargs.pop("circuit", default_circuit) or default_circuit
        self.tag = kwargs.pop("tag", None)

    def __enter__(self):
        """Create a context for hierarchical grouping of parts and nets."""

        name = self.name
        circuit = self.circuit
        tag = self.tag

        # Upon entry to the context, save the reference to the current default Circuit object.
        self.save_default_circuit = default_circuit  # pylint: disable=undefined-variable

        # Set the circuit to which parts and nets will be added.
        builtins.default_circuit = circuit

        # Setup some globals needed in this context.
        builtins.NC = default_circuit.NC  # pylint: disable=undefined-variable

        # Entering the context creates circuitry at a level one
        # greater than the current level. (The top level is zero.)
        self.circuit.level += 1

        # Create a name for this subcircuit from the concatenated names of all
        # the nested groups that were called on all the preceding levels
        # that led to this one. Also, add a distinct tag to the current
        # name to disambiguate multiple uses of the same function.  This is
        # either specified as an argument, or an incrementing value is used.
        if tag is None:
            tag = self.group_name_cntr[name]
            self.group_name_cntr[name] += 1
        circuit.hierarchy = circuit.context[-1][0] + "." + name + str(tag)
        circuit.add_hierarchical_name(circuit.hierarchy)

        # Store the context so it can be used if this group context
        # invokes another group context within itself to add more
        # levels of hierarchy.
        circuit.context.append((circuit.hierarchy,))

        return self

    def __exit__(self, type, value, traceback):
        """Exit a hierarchical grouping context."""

        circuit = self.circuit

        # Restore the context that existed before this context was
        # created. This does not remove the circuitry since it has already been
        # added to the parts and nets lists.
        circuit.context.pop()

        # Restore the hierarchy label and level.
        circuit.hierarchy = circuit.context[-1][0]
        circuit.level -= 1

        # Restore the default circuit and globals.
        builtins.default_circuit = self.save_default_circuit
        builtins.NC = default_circuit.NC  # pylint: disable=undefined-variable


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
