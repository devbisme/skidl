# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Interface management in SKiDL.

This module provides the Interface class, which bundles nets, buses, and pins into
a single entity that can be used for connecting subsystems with complex I/O.
Interfaces make it easier to handle groups of related signals and enable 
connecting subsystems with matching interfaces using simple operators.
"""

from .alias import Alias
from .bus import Bus
from .net import Net
from .netpinlist import NetPinList
from .pin import Pin
from .skidlbaseobj import SkidlBaseObject
from .utilities import (
    expand_indices,
    export_to_all,
    filter_list,
    from_iadd,
    list_or_scalar,
    rmv_iadd,
    set_iadd,
)



@export_to_all
class Interface(dict):
    """
    A bundle of nets, buses, and pins that can be accessed as attributes or dict entries.
    
    An Interface groups related nets, buses, and pins into a single entity where each
    item can be accessed either as an attribute (obj.item) or as a dictionary key (obj['item']).
    This makes Interfaces useful for standardizing connections between subsystems or
    for creating reusable connection patterns.
    
    Args:
        *args: Positional arguments passed to dict constructor.
        **kwargs: Keyword arguments defining nets/buses to include in the interface.
        
    Keyword Args:
        unbundle (bool, optional): Whether to automatically unbundle buses into individual
            nets that can be accessed directly. Defaults to True.
            
    Examples:
        >>> power = Interface(vcc=Net('VCC'), gnd=Net('GND'))
        >>> power.vcc += part1['VCC']  # Connect using attribute access
        >>> power['gnd'] += part1['GND']  # Connect using dictionary access
    """

    # Set the default ERC functions for all Interface instances.
    erc_list = []

    def __init__(self, *args, **kwargs):

        # By default, buses are unbundled into individual nets.
        unbundle = kwargs.pop("unbundle", True)

        self.unexpio = dict()

        # Start with a standard dictionary of objects.
        super().__init__(*args, **kwargs)

        super().__setattr__("match_pin_regex", False)

        for k, v in list(self.items()):
            if isinstance(v, (Pin, Net, Bus, NetPinList, SkidlBaseObject)):
                # Add SKiDL-type objects.
                self.__setattr__(k, v, unbundle=unbundle)
            else:
                # Add standard Python objects.
                super().__setattr__(k, v)

    def __setattr__(self, key, value, unbundle=True):
        """
        Set an attribute and corresponding dict entry in the interface.
        
        This method handles creating net-like objects for pin-like inputs,
        setting up aliases for the keys, and optionally unbundling buses
        into individual nets.
        
        Args:
            key (str): Name for the attribute/dict entry.
            value: The value to associate with the key.
            unbundle (bool, optional): Whether to unbundle buses. Defaults to True.
        """

        # Create net-like objects for pin-like objects.
        if isinstance(value, NetPinList):
            # Convert NetPinList into a Bus.
            value = Bus(value)
        elif isinstance(value, Pin):
            # Convert Pin into a Net.
            n = Net()
            n += value
            value = n

        # Assign the key as an alias to any net-like object.
        if isinstance(value, (Net, Bus)):
            value.aliases += key
            self.unexpio[key] = value

        # Add the value to the dictionary and as an attribute.
        if isinstance(value, SkidlBaseObject):
            # Only SKiDL-type objects get added as dictionary items.
            super().__setitem__(key, value)
        super().__setattr__(key, value)

        # If enabled, expand a bus and add its individual nets.
        if isinstance(value, Bus) and unbundle:
            for i, v in enumerate(value):
                n = Net(circuit=v.circuit)
                n.aliases += key + str(i)
                n += v
                super().__setitem__(key + str(i), n)
                super().__setattr__(key + str(i), n)
                # self.setattr(self, key + str(i), n)

    def __getitem__(self, *io_ids, **criteria):
        """
        Get interface items by name, regex, or other criteria.
        
        This method allows retrieving individual items or groups of items
        from the interface based on names, regular expressions, or other
        attribute criteria.
        
        Args:
            io_ids: Names or patterns of interface items to retrieve.
                If empty, all items may be retrieved.
                
        Keyword Args:
            match_regex (bool, optional): Whether to use regex matching. Default is False.
            criteria: Attribute values that items must match to be retrieved.
            
        Returns:
            Net, Pin, Bus, NetPinList, or None: The selected item(s) or None if no match.
        """

        # Extract permission to search for regex matches in pin names/aliases.
        match_regex = criteria.pop("match_regex", False) or self.match_pin_regex

        # If no pin identifiers were given, then use a wildcard that will
        # select all pins.
        if not io_ids:
            io_ids = [".*"]
            match_regex = True

        # An interface doesn't have pins, so set pin slice bounds to zero.
        min_pin, max_pin = 0, 0

        # Get I/O entries.
        io_types = (Net, Pin, NetPinList, Bus)
        ios = [io for io in self.values() if isinstance(io, io_types)]

        # Use this for looking up the dict key using the id of a given I/O.
        id_to_key = {id(v): k for k, v in self.items()}

        # Go through the I/O entries and find the ones selected by the IDs.
        selected_ios = NetPinList()
        for io_id in expand_indices(min_pin, max_pin, match_regex, *io_ids):

            # Look for an exact match of the I/O key name with the current ID.
            try:
                io = dict.__getitem__(self, io_id)
            except KeyError:
                # No exact match on I/O key name, so keep looking below.
                pass
            else:
                # Add exact match to the list of selected I/Os and go to the next ID.
                selected_ios.append(io)
                continue

            # Check I/O aliases for an exact match with the current ID.
            tmp_ios = filter_list(ios, aliases=io_id, do_str_match=True, **criteria)
            for io in tmp_ios:
                selected_ios.append(io)
            if tmp_ios:
                # Found exact match between alias and ID, so done with this ID and go to next ID.
                continue

            # Skip regex matching if not enabled.
            if not match_regex:
                continue

            # OK, ID doesn't exactly match an I/O name or alias. Does it match as a regex?
            tmp_ios = filter_list(ios, aliases=Alias(io_id), **criteria)
            for io in tmp_ios:
                selected_ios.append(io)

        # Return list of I/Os that were selected by the IDs.
        return list_or_scalar(selected_ios)

    def __setitem__(self, key, value):
        """
        Set a dictionary entry and attribute with the same name.
        
        This method handles assignments to dictionary keys, ensuring that
        attribute access and dictionary access remain synchronized.
        
        Args:
            key (str): The key to assign to.
            value: The value to assign.
        """
        if from_iadd(value):
            # The += flag in the values are no longer needed.
            rmv_iadd(value)
        else:
            # This is for a straight assignment of value to key.
            setattr(self, key, value)

    def __iadd__(self, other_intfc):
        """
        Connect this interface to another interface using the += operator.
        
        This connects matching nets and buses between the two interfaces.
        
        Args:
            other_intfc (Interface): The interface to connect to this one.
            
        Returns:
            Interface: This interface with connections to the other interface.
        """
        return self.connect(other_intfc)

    def connect(self, other_intfc):
        """
        Connect this interface to another interface.
        
        This method connects nets and buses in this interface to those
        with matching names in another interface.
        
        Args:
            other_intfc (Interface): The interface to connect to this one.
            
        Returns:
            Interface: This interface with connections to the other interface.
            
        Examples:
            >>> intf1 = Interface(a=Net('a'), b=Net('b'))
            >>> intf2 = Interface(a=Net('a2'), b=Net('b2'))
            >>> intf1.connect(intf2)  # Connect matching nets
            >>> # Alternative: intf1 += intf2
        """

        # Connect the nets/buses of this interface to the nets/buses of the other interface.
        for k,v in self.unexpio.items():
            if isinstance(v, (Net, Bus, Pin)):
                if k in other_intfc:
                    self[k] += other_intfc[k]

        # Set the flag to indicate this result came from the += operator.
        set_iadd(self, True)

        return self
