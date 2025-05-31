# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Object for handling series and parallel networks of two-pin parts, nets, and pins.

This module provides the Network class which allows electronic components to be
connected in series and parallel using operators like '&' and '|'. This enables 
a concise, algebraic notation for creating complex circuits.
"""

from .logger import active_logger
from .utilities import export_to_all


@export_to_all
class Network(list):
    """
    A container for arranging pins, nets, and parts in series and parallel.
    
    The Network class extends the list type to store input and output nodes (ports)
    which can be connected to form series and parallel arrangements using the '&' and '|'
    operators. A Network can have up to two nodes representing its input and output ports.
    """
    
    def __init__(self, *objs):
        """
        Create a Network object from a list of pins, nets, and parts.
        
        Converts each provided object to a Network (if possible) and combines
        their ports into a single Network object.
        
        Args:
            *objs: Variable number of objects to be converted to Networks.
            
        Raises:
            TypeError: If an object cannot be converted to a Network.
            ValueError: If the resulting Network would have more than two nodes.
        """
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
        """
        Combine two networks by placing them in series.
        
        Implements the '&' operator to create a series connection between Networks.
        The output port of this Network is connected to the input port of the
        provided object's Network.
        
        Args:
            obj: Object to be converted to a Network and placed in series.
            
        Returns:
            Network: A new Network with input from self and output from obj.
            
        Raises:
            TypeError: If obj cannot be converted to a Network.
        """
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
        """
        Combine two networks by placing them in series (right-side '&' operation).
        
        Implements the right-side '&' operator to create a series connection when
        this Network is on the right side of the '&' operator.
        
        Args:
            obj: Object to be converted to a Network and placed in series.
            
        Returns:
            Network: A new Network with input from obj and output from self.
        """
        return Network(obj) & self

    def __or__(self, obj):
        """
        Combine two networks by placing them in parallel.
        
        Implements the '|' operator to create a parallel connection between Networks.
        Both the input and output ports of this Network are connected to the
        corresponding ports of the provided object's Network.
        
        Args:
            obj: Object to be converted to a Network and placed in parallel.
            
        Returns:
            Network: This Network object with ports connected to obj's Network.
            
        Raises:
            TypeError: If obj cannot be converted to a Network.
        """
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
        """
        Create a Network from this object.
        
        For Network objects, this simply returns self since it's already a Network.
        
        Returns:
            Network: This Network object.
        """
        return self


@export_to_all
def tee(ntwk):
    """
    Create a network "tee" by returning the first terminal of a Network object.
    
    This function allows for the creation of branch points in networks, enabling
    more complex circuit topologies beyond simple series and parallel arrangements.
    
    Args:
        ntwk: Object to be converted to a Network if not already.
        
    Returns:
        Node: The first terminal (input port) of the Network.
        
    Example:
        vi & r1 & r2 & tee(r3 & r4 & gnd) & r5 & gnd
        
        This creates:
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
