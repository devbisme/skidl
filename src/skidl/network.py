# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Object for for handling series and parallel networks of two-pin parts, nets, and pins.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from builtins import super

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .logger import active_logger
from .utilities import export_to_all



@export_to_all
class Network(list):
    def __init__(self, *objs):
        """Create a Network object from a list of pins, nets, and parts."""
        super().__init__()
        for obj in objs:
            try:
                ntwk = obj.create_network()  # Create a Network from each object.
            except AttributeError:
                active_logger.raise_(
                    TypeError,
                    "Can't create a network from a {} object ({}).".format(
                        type(obj), obj.__name__
                    ),
                )

            # Add the in & out ports of the object network to this network.
            self.extend(ntwk)

            # A Network cannot have more than two ports. But it may have only
            # one which will be used as both an input and an output. Or it may
            # have zero, in which case it is just an empty container waiting to
            # have ports added to it.
            if len(self) > 2:
                active_logger.raise_(
                    ValueError,
                    "A Network object can't have more than two nodes.",
                )

    def __and__(self, obj):
        """Combine two networks by placing them in series."""

        # First, convert the object to a network.
        try:
            ntwk = obj.create_network()
        except AttributeError:
            active_logger.raise_(
                TypeError,
                "Unable to create a Network from a {} object ({}).".format(
                    type(obj), obj.__name__
                ),
            )

        # Attach the output of the first network to the input of the second.
        # (Use -1 index to get the output port instead of 1 because the network
        # may only have a single port serving as both the input and output.)
        self[-1] += ntwk[0]

        # Return a network consisting of the input of the first and the output of the second.
        return Network(self[0], ntwk[-1])

    def __rand__(self, obj):
        """Combine two networks by placing them in series. (Reverse-ordered operation.)"""

        # Create a network from the first object and then place it in series with the second network.
        return Network(obj) & self

    def __or__(self, obj):
        """Combine two networks by placing them in parallel."""

        # First, convert the object to a network.
        try:
            ntwk = obj.create_network()
        except AttributeError:
            active_logger.raise_(
                TypeError,
                "Unable to create a Network from a {} object ({}).".format(
                    type(obj), obj.__name__
                ),
            )

        # Attach the inputs of both networks and the outputs of both networks to
        # place them in parallel.
        self[0] += ntwk[0]
        self[-1] += ntwk[-1]

        # Just return one of the original networks since its I/O ports are attached to both.
        return self

    def create_network(self):
        """Creating a network from a network just returns the original network."""
        return self


@export_to_all
def tee(ntwk):
    """
    Create a network "tee" by returning the first terminal of a Network object.
    Then you can create tee'ed networks like so: vi & r1 & r2 & tee(r3 & r4 & gnd) & r5 & gnd
    which becomes:

        vi---r1---r2-+-r5---gnd
                     |
                     |
                     r3---r4---gnd

    """
    if not isinstance(ntwk, Network):
        # Convert an object into a Network if it isn't already.
        ntwk = Network(ntwk)

    # Return the first terminal of the network.
    return ntwk[0]
