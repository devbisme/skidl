# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""
Package a subcircuit so it can be used like a Part.
"""

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from builtins import super, zip
from copy import copy

from future import standard_library

from .bus import Bus
from .circuit import subcircuit
from .interface import Interface
from .net import Net
from .part import NETLIST
from .protonet import ProtoNet

standard_library.install_aliases()


class Package(Interface):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self["circuit"] = None

        # Don't use update(). It doesn't seem to call __setitem__.
        for k, v in list(kwargs.items()):
            self[k] = v  # Use __setitem__ so both dict item and attribute are created.

    def __call__(self, *args, **kwargs):
        """Create a copy of a package."""

        # Get circuit that will contain the package subcircuitry.
        circuit = kwargs.pop("circuit", default_circuit)

        # See if this package should be instantiated into the netlist or used as a template.
        dest = kwargs.pop("dest", NETLIST)

        pckg = Package(**self.copy())  # Create a shallow copy of the package.

        # Set the circuit that the ProtoNets belong to. Also, make copies of any
        # implicit buses or nets that were specified as default I/Os in the
        # package definition.
        for k, v in pckg.items():
            if isinstance(v, ProtoNet):
                v.circuit = circuit
            elif isinstance(v, (Net, Bus)):
                if v.is_implicit():
                    pckg[k] = v.__class__()
                    # pckg[k] = v.copy()

        # Don't use update(). It doesn't seem to call __setitem__.
        for k, v in list(kwargs.items()):
            pckg[k] = v  # Use __setitem__ so both dict item and attribute are created.

        pckg.subcircuit = self.subcircuit  # Assign subcircuit creation function.

        # Remove creation function so it's not passed as a parameter.
        del pckg["subcircuit"]

        # Add package to circuit only if it's supposed to be instantiated.
        if dest == NETLIST:
            circuit += pckg

        return pckg

    def is_movable(self):
        return True
        for obj in self.values():
            try:
                if not obj.is_movable():
                    return False  # Interface is not movable if any object in it is not movable.
            except AttributeError:
                pass  # Objects without is_movable() are always movable.
        return True  # Every object in the Interface that could move was movable.


def package(subcirc_func):
    """Decorator that creates a package for a subcircuit routine."""

    pckg = Package()  # Create the package.

    # Store the parameter names passed to the subcircuit.
    code = subcirc_func.__code__
    num_args = code.co_argcount
    arg_names = code.co_varnames[:num_args]

    # By default, set parameters to a package to be ProtoNets.
    for arg_name in arg_names:
        pn = ProtoNet(arg_name, circuit=None)
        pn.intfc = pckg
        pn.intfc_key = arg_name
        pckg[arg_name] = pn

    # Set any default values for the parameters.
    if getattr(subcirc_func, "__defaults__", None):
        for arg_name, dflt_value in zip(
            reversed(arg_names), reversed(subcirc_func.__defaults__)
        ):
            pckg[arg_name] = dflt_value
    if getattr(subcirc_func, "__kwdefaults__", None):
        for arg_name, dflt_value in subcirc_func.__kwdefaults__.items():
            pckg[arg_name] = dflt_value

    # Create the subcircuit function that will be called to insantiate this package.
    pckg.subcircuit = subcircuit(subcirc_func)

    # Remove the subcircuit key from the dict so it won't be passed to subcirc_func().
    del pckg["subcircuit"]

    return pckg
