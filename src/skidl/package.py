# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Package a subcircuit so it can be used like a Part.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from builtins import super, zip
from copy import copy

from deprecation import deprecated

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .bus import Bus
from .group import subcircuit
from .interface import Interface
from .net import Net
from .part import NETLIST
from .protonet import ProtoNet
from .utilities import export_to_all



@export_to_all
class Package(Interface):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self["circuit"] = None

        # Don't use update(). It doesn't seem to call __setitem__.
        for k, v in list(kwargs.items()):
            self[k] = v  # Use __setitem__ so both dict item and attribute are created.

    def __call__(self, **kwargs):
        # def __call__(self, *args, **kwargs):
        """Create a copy of a package."""

        # Get circuit that will contain the package subcircuitry.
        circuit = kwargs.pop("circuit", default_circuit)

        # See if this package should be instantiated into the netlist or used as a template.
        dest = kwargs.pop("dest", NETLIST)

        # Create a blank Package object.
        pckg = Package()

        # Add I/O and anything else to the blank Package.
        for k, v in self.items():
            if isinstance(v, ProtoNet):
                pckg[k] = copy(v)
                pckg[k].circuit = circuit
            elif isinstance(v, (Net, Bus)):
                if v.is_implicit():
                    pckg[k] = v.__class__(circuit=circuit)
                else:
                    # Should this use copy()?
                    pckg[k] = v
                    pckg[k].circuit = circuit
            else:
                pckg[k] = v

        # Add passed-in attributes to the package.
        # Don't use update(). It doesn't seem to call __setitem__.
        for k, v in list(kwargs.items()):
            pckg[k] = v  # Use __setitem__ so both dict item and attribute are created.

        # Assign subcircuit creation function.
        pckg.subcircuit = self.subcircuit

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


@export_to_all
@deprecated(deprecated_in="1.2.0", removed_in="2.0.0", details="Use Interface instead.")
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
