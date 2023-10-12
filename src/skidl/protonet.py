# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Prototype of a net which can become a Net or a Bus depending upon what is connected to it.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from builtins import range, super

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .logger import active_logger
from .net import Net
from .network import Network
from .pin import Pin
from .skidlbaseobj import SkidlBaseObject
from .utilities import expand_buses, export_to_all, flatten



@export_to_all
class ProtoNet(SkidlBaseObject):
    def __init__(self, name=None, circuit=None):
        super().__init__()
        self.name = name
        self.circuit = circuit or default_circuit

    def __iadd__(self, *nets_pins_buses):
        from .bus import Bus

        # Check the stuff you want to connect to see if it's the right kind.
        nets_pins = expand_buses(flatten(nets_pins_buses))
        allowed_types = (Pin, Net, ProtoNet)
        illegal = (np for np in nets_pins if type(np) not in allowed_types)
        for np in illegal:
            active_logger.raise_(
                ValueError,
                "Can't make connections to a {} ({}).".format(
                    type(np), getattr(np, "__name__", "")
                ),
            )

        sz = len(nets_pins)
        if sz == 0:
            active_logger.raise_(
                ValueError,
                "Connecting empty set of pins, nets, busses to a {}".format(
                    self.__class__.__name__
                ),
            )
        else:
            # Create implicitly-named net/bus so the name will be overridden
            # by whatever connects to it.
            if sz == 1:
                cnct = Net(name=None, circuit=self.circuit)
            else:
                cnct = Bus(None, sz, circuit=self.circuit)
            try:
                self.intfc[self.intfc_key] = cnct
            except AttributeError:
                pass
            cnct += nets_pins
            return cnct

    def __len__(self):
        # ProtoNets never have attached pins because then they would become Nets.
        return 0

    def create_network(self):
        """Create a network from a single ProtoNet."""

        self += Net()  # Turn ProtoNet into a Net.
        ntwk = Network()
        ntwk.append(self)
        return ntwk

    def __and__(self, obj):
        """Attach a net and another part/pin/net in serial."""

        return Network(self) & obj

    def __rand__(self, obj):
        """Attach a net and another part/pin/net in serial."""

        return obj & Network(self)

    def __or__(self, obj):
        """Attach a net and another part/pin/net in parallel."""

        return Network(self) | obj

    def __ror__(self, obj):
        """Attach a net and another part/pin/net in parallel."""

        return obj | Network(self)

    def __iter__(self):
        """
        Return an iterator for stepping through the ProtoNet.
        """
        # You can only iterate a ProtoNet one time.
        return (self for _ in [self])  # Return generator expr.

    def is_movable(self):
        return True  # A ProtoNet is never connected, so it's always movable.
