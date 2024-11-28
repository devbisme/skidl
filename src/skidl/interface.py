# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Handles interfaces for subsystems with complicated I/O.
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
    An Interface bundles a group of nets/buses into a single entity with each
    net/bus becoming an attribute.  An Interface is also usable as a dict
    where the attribute names serve as keys. This means the ** operator works
    on an Interface.
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
        """Sets attribute and also a dict entry with a key using the attribute name."""

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
        Return list of part pins selected by identifiers.

        Args:
            io_ids: A list of strings containing I/O names,
                regular expressions, slices, lists or tuples. If empty,
                then it will select all pins.

        Keyword Args:
            criteria: Key/value pairs that specify attribute values the
                I/Os must have in order to be selected.

        Returns:
            A list of I/Os matching the given IDs and satisfying all the criteria,
            or just a single I/O object if only a single match was found.
            Or None if no match was found.

        Notes:
            Pins can be selected from a part by using brackets like so::

                intf = Interface(a=Net(), b=Net())
                net = Net()
                intf['a'] += net  # Connects I/O 'a' of interface to the net.
                net += intf.b     # Connects the net to the 'b' I/O.
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
        """Sets dict entry and also creates attribute with the same name as the dict key."""
        if from_iadd(value):
            # The += flag in the values are no longer needed.
            rmv_iadd(value)
        else:
            # This is for a straight assignment of value to key.
            setattr(self, key, value)

    def __iadd__(self, other_intfc):
        """
        Connects the nets/buses of this interface to the nets/buses of another interface.

        Args:
            other_intfc: The interface to connect to this one.
        """
        return self.connect(other_intfc)

    def connect(self, other_intfc):
        """
        Connects the nets/buses of this interface to the nets/buses of another interface.

        Args:
            other_intfc: The interface to connect to this one.

        Returns:
            The updated interface with the new connections.

        Notes:
            Connections between interfaces can also be made using the += operator.
        """

        # Connect the nets/buses of this interface to the nets/buses of the other interface.
        for k,v in self.unexpio.items():
            if isinstance(v, (Net, Bus, Pin)):
                if k in other_intfc:
                    self[k] += other_intfc[k]

        # Set the flag to indicate this result came from the += operator.
        set_iadd(self, True)

        return self
