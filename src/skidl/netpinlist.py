# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Specialized list for handling nets, pins, and buses.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from builtins import range

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .alias import Alias
from .logger import active_logger
from .net import Net
from .network import Network
from .pin import Pin
from .protonet import ProtoNet
from .utilities import expand_buses, export_to_all, flatten, set_iadd



@export_to_all
class NetPinList(list):

    def __len__(self):
        """Return the number of individual pins/nets in this interface."""
        return len(expand_buses(self))

    def __and__(self, obj):
        """Attach a NetPinList and another part/pin/net in serial."""

        return Network(self) & obj

    def __rand__(self, obj):
        """Attach a NetPinList and another part/pin/net in serial."""

        return obj & Network(self)

    def __or__(self, obj):
        """Attach a NetPinList and another part/pin/net in parallel."""

        return Network(self) | obj

    def __ror__(self, obj):
        """Attach a NetPinList and another part/pin/net in parallel."""

        return obj | Network(self)

    def __iadd__(self, *nets_pins_buses):
        nets_pins_a = expand_buses(self)
        len_a = len(nets_pins_a)

        # Check the stuff you want to connect to see if it's the right kind.
        nets_pins_b = expand_buses(flatten(nets_pins_buses))
        allowed_types = (Pin, Net, ProtoNet)
        illegal = (np for np in nets_pins_b if not isinstance(np, allowed_types))
        for np in illegal:
            active_logger.raise_(
                ValueError,
                "Can't make connections to a {} ({}).".format(
                    type(np), getattr(np, "__name__", "")
                ),
            )
        len_b = len(nets_pins_b)

        if len_a != len_b:
            if len_a > 1 and len_b > 1:
                active_logger.raise_(
                    ValueError,
                    "Connection mismatch {} != {}!".format(len_a, len_b),
                )

            # If just a single net is to be connected, make a list out of it that's
            # just as long as the list of pins to connect to. This will connect
            # multiple pins to the same net.
            if len_b == 1:
                nets_pins_b = [nets_pins_b[0] for _ in range(len_a)]
                len_b = len(nets_pins_b)
            elif len_a == 1:
                nets_pins_a = [nets_pins_a[0] for _ in range(len_b)]
                len_a = len(nets_pins_a)

        assert len_a == len_b

        for npa, npb in zip(nets_pins_a, nets_pins_b):
            if isinstance(npb, ProtoNet):
                # npb is a ProtoNet so it will get replaced by a real Net by the += op.
                # Should the new Net replace the equivalent ProtoNet in nets_pins_buses?
                # It doesn't appear to be necessary since all tests pass, but be aware
                # of this issue.
                npb += npa
            elif isinstance(npa, ProtoNet):
                # npa is a ProtoNet so it will get replaced by a real Net by the += op.
                # Therefore, find the equivalent ProtoNet in self and replace it with the
                # new Net.
                id_npa = id(npa)
                npa += npb
                for i in range(len(self)):
                    if id_npa == id(self[i]):
                        self[i] = npa
            else:
                # Just regular attachment of nets and/or pins which updates the existing
                # objects within the self and nets_pins_buses lists.
                npa += npb
                pass

        # Set the flag to indicate this result came from the += operator.
        set_iadd(self, True)

        return self

    def create_network(self):
        """Create a network from a list of pins and nets."""

        return Network(*self)  # An error will occur if list has more than 2 items.

    @property
    def circuit(self):
        """Get the circuit the pins/nets are members of."""
        cct = set()
        for pn in self:
            cct.add(pn.circuit)
        if len(cct) == 1:
            return cct.pop()
        active_logger.raise_(
            ValueError,
            "This NetPinList contains nets/pins in {} circuits.".format(len(cct)),
        )

    @property
    def width(self):
        """Return width, which is the same as using the len() operator."""
        return len(self)

    # Setting/clearing the do_erc flag for the list sets/clears the do_erc flags of the pins/nets in the list.
    @property
    def do_erc(self):
        raise NotImplementedError

    @do_erc.setter
    def do_erc(self, on_off):
        for pn in self:
            pn.do_erc = on_off

    @do_erc.deleter
    def do_erc(self):
        for pn in self:
            del pn.do_erc

    # Setting/clearing the drive strength for the list sets/clears the drive of the pins/nets in the list.
    @property
    def drive(self):
        raise NotImplementedError

    @do_erc.setter
    def drive(self, strength):
        for pn in self:
            pn.drive = strength

    @do_erc.deleter
    def drive(self):
        for pn in self:
            del pn.drive

    # Trying to set an alias attribute on a NetPinList is an error.
    # This prevents setting an alias on a list of two or more pins that
    # might be returned by the filter_list() utility.
    @property
    def aliases(self):
        return Alias([])  # No aliases, so just return an empty list.

    @aliases.setter
    def aliases(self, alias):
        raise NotImplementedError

    @aliases.deleter
    def aliases(self):
        raise NotImplementedError
