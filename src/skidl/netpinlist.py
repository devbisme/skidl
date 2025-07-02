# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Specialized list for handling nets, pins, and buses.

This module provides the NetPinList class, which is a specialized list that
handles collections of pins and nets. It supports operations for connecting
pins and nets in series or parallel configurations and provides access to
common properties across all pins and nets in the list.
"""

from .alias import Alias
from .logger import active_logger
from .net import Net
from .network import Network
from .pin import Pin
from .utilities import expand_buses, export_to_all, flatten, set_iadd


@export_to_all
class NetPinList(list):
    """
    Specialized list for handling collections of nets and pins.
    
    NetPinList extends the Python list with additional functionality for
    working with collections of pins and nets. It handles bus expansion and
    provides operations to connect nets and pins in series or parallel.
    """

    def __len__(self):
        """
        Return the number of individual pins/nets in this interface.
        
        This performs bus expansion to count the actual number of pins or nets.
        
        Returns:
            An integer representing the total count of pins/nets after bus expansion.
        """
        return len(expand_buses(self))

    def __and__(self, obj):
        """
        Attach a NetPinList and another part/pin/net in series.
        
        The & operator creates a serial connection between this NetPinList and
        another object.
        
        Args:
            obj: The part, pin, net, or bus to connect in series.
            
        Returns:
            A Network object representing the series connection.
            
        Examples:
            net_list & resistor  # Connect nets in series with a resistor
        """
        return Network(self) & obj

    def __rand__(self, obj):
        """
        Attach a NetPinList and another part/pin/net in series.
        
        This is called when the & operator is used with the NetPinList on the right side.
        
        Args:
            obj: The part, pin, net, or bus to connect in series.
            
        Returns:
            A Network object representing the series connection.
        """
        return obj & Network(self)

    def __or__(self, obj):
        """
        Attach a NetPinList and another part/pin/net in parallel.
        
        The | operator creates a parallel connection between this NetPinList and
        another object.
        
        Args:
            obj: The part, pin, net, or bus to connect in parallel.
            
        Returns:
            A Network object representing the parallel connection.
            
        Examples:
            net_list | resistor  # Connect nets in parallel with a resistor
        """
        return Network(self) | obj

    def __ror__(self, obj):
        """
        Attach a NetPinList and another part/pin/net in parallel.
        
        This is called when the | operator is used with the NetPinList on the right side.
        
        Args:
            obj: The part, pin, net, or bus to connect in parallel.
            
        Returns:
            A Network object representing the parallel connection.
        """
        return obj | Network(self)

    def __iadd__(self, *nets_pins_buses):
        """
        Connect pins/nets with another pin/net/bus.
        
        The += operator connects pins or nets in this list with pins or nets
        in other lists or objects.
        
        Args:
            *nets_pins_buses: One or more pins, nets, or buses to connect.
            
        Returns:
            The updated NetPinList after making the connections.
            
        Raises:
            ValueError: If trying to connect to an illegal type or if connection
                        counts don't match.
                        
        Examples:
            bus1 += bus2  # Connect all pins in bus1 to corresponding pins in bus2
        """
        nets_pins_a = expand_buses(self)
        len_a = len(nets_pins_a)

        # Check the stuff you want to connect to see if it's the right kind.
        nets_pins_b = expand_buses(flatten(nets_pins_buses))
        allowed_types = (Pin, Net)
        illegal = (np for np in nets_pins_b if not isinstance(np, allowed_types))
        for np in illegal:
            active_logger.raise_(
                ValueError,
                f"Can't make connections to a {type(np)} ({getattr(np, '__name__', '')})."
            )
        len_b = len(nets_pins_b)

        if len_a != len_b:
            if len_a > 1 and len_b > 1:
                active_logger.raise_(
                    ValueError,
                    f"Connection mismatch {len_a} != {len_b}!",
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
            # Attachment of nets and/or pins which updates the existing
            # objects within the self and nets_pins_buses lists.
            npa += npb

        # Set the flag to indicate this result came from the += operator.
        set_iadd(self, True)

        return self

    def create_network(self):
        """
        Create a network from a list of pins and nets.
        
        Returns:
            A Network object created from the pins and nets in this list.
            
        Raises:
            ValueError: If the list has more than 2 items.
        """
        return Network(*self)  # An error will occur if list has more than 2 items.

    @property
    def circuit(self):
        """
        Get the circuit the pins/nets are members of.
        
        Returns:
            The Circuit object that the pins/nets belong to.
            
        Raises:
            ValueError: If pins/nets belong to different circuits.
        """
        cct = set()
        for pn in self:
            cct.add(pn.circuit)
        if len(cct) == 1:
            return cct.pop()
        active_logger.raise_(
            ValueError,
            f"This NetPinList contains nets/pins in {len(cct)} circuits.",
        )

    @property
    def width(self):
        """
        Return the width (number of pins/nets) in this list.
        
        Returns:
            An integer representing the number of pins/nets after bus expansion.
        """
        return len(self)

    # Setting/clearing the do_erc flag for the list sets/clears the do_erc flags of the pins/nets in the list.
    @property
    def do_erc(self):
        """
        Get the electrical rule checking status for pins/nets in the list.
        
        Raises:
            NotImplementedError: This property can only be set or deleted, not read.
        """
        raise NotImplementedError

    @do_erc.setter
    def do_erc(self, on_off):
        """
        Set the electrical rule checking status for all pins/nets in the list.
        
        Args:
            on_off: Boolean indicating whether to perform ERC on the pins/nets.
        """
        for pn in self:
            pn.do_erc = on_off

    @do_erc.deleter
    def do_erc(self):
        """
        Restore the default electrical rule checking status for all pins/nets in the list.
        """
        for pn in self:
            del pn.do_erc

    # Setting/clearing the drive strength for the list sets/clears the drive of the pins/nets in the list.
    @property
    def drive(self):
        """
        Get the drive strength of pins/nets in the list.
        
        Raises:
            NotImplementedError: This property can only be set or deleted, not read.
        """
        raise NotImplementedError

    @do_erc.setter
    def drive(self, strength):
        """
        Set the drive strength for all pins/nets in the list.
        
        Args:
            strength: The drive strength value to set for all pins/nets.
        """
        for pn in self:
            pn.drive = strength

    @do_erc.deleter
    def drive(self):
        """
        Restore the default drive strength for all pins/nets in the list.
        """
        for pn in self:
            del pn.drive

    # Trying to set an alias attribute on a NetPinList is an error.
    # This prevents setting an alias on a list of two or more pins that
    # might be returned by the filter_list() utility.
    @property
    def aliases(self):
        """
        Get the aliases for this NetPinList.
        
        For NetPinList, no aliases are allowed, so returns an empty Alias object.
        
        Returns:
            An empty Alias object.
        """
        return Alias([])  # No aliases, so just return an empty list.

    @aliases.setter
    def aliases(self, alias):
        """
        Setting aliases on a NetPinList is not allowed.
        
        Raises:
            NotImplementedError: Always raised since aliases cannot be set on a NetPinList.
        """
        raise NotImplementedError

    @aliases.deleter
    def aliases(self):
        """
        Deleting aliases from a NetPinList is not allowed.
        
        Raises:
            NotImplementedError: Always raised since aliases cannot be deleted from a NetPinList.
        """
        raise NotImplementedError
