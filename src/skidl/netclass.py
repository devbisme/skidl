# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""Class for PCBNEW net classes."""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from builtins import object, str

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .logger import active_logger
from .utilities import export_to_all



@export_to_all
class NetClass(object):
    def __init__(self, name, **attribs):

        # This object will belong to the default Circuit object or the one
        # that's passed as a parameter.
        circuit = attribs.pop("circuit", default_circuit)

        # Assign net class name.
        self.name = name

        # Assign the other attributes to this object.
        for k, v in list(attribs.items()):
            setattr(self, k, v)

        # Is this net class already defined?
        if circuit.netclasses.get(name) is not None:
            active_logger.warning(
                "Cannot redefine existing net class {name}!".format(**locals())
            )
        else:
            circuit.netclasses[name] = self
