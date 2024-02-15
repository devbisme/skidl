# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Handles buses.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import builtins
import re
from builtins import range, str, super

try:
    from future import standard_library

    standard_library.install_aliases()
except ImportError:
    pass

from .alias import Alias
from .logger import active_logger
from .net import NET_PREFIX, Net
from .netpinlist import NetPinList
from .pin import Pin
from .skidlbaseobj import SkidlBaseObject
from .utilities import (
    expand_indices,
    export_to_all,
    filter_list,
    find_num_copies,
    flatten,
    from_iadd,
    get_unique_name,
    list_or_scalar,
    rmv_iadd,
)

# Prefix for implicit buses.
BUS_PREFIX = "B$"


__all__ = ["BUS_PREFIX"]


@export_to_all
class Bus(SkidlBaseObject):
    """
    This class collects one or more nets into a group that can be indexed.

    Args:
        name: A string with the name of the bus.
        args: A list of ints, pins, nets, buses to attach to the net.

    Keyword Args:
        attribs: A dictionary of attributes and values to attach to
            the Net object.

    Example:
        ::

            n = Net()
            led1 = Part("Device", 'LED')
            b = Bus('B', 8, n, led1['K'])
    """

    def __init__(self, *args, **attribs):

        super().__init__()

        # Define the member storing the nets so it's present, but it starts empty.
        self.nets = []

        # For Bus objects, the circuit object the bus is a member of is passed
        # in with all the other attributes. If a circuit object isn't provided,
        # then the default circuit object is added to the attributes.
        attribs["circuit"] = attribs.get("circuit", default_circuit)

        # Scan through the kwargs and args to see if there is a name for this bus.
        name = attribs.pop("name", None)
        if not name:
            try:
                # The first string found will be the bus name.
                name = [a for a in args if isinstance(a, (basestring, type(None)))][0]
                # Remove the name from the list of things to be added to the bus.
                args = list(args)
                args.remove(name)
                # args = [a for a in args if a != name]
            except IndexError:
                # No explicit bus name found, so generate an implicit one.
                name = None

        # Attach additional attributes to the bus. (The Circuit object also gets
        # set here.)
        for k, v in list(attribs.items()):
            setattr(self, k, v)

        # The bus name is set after the circuit is assigned so the name can be
        # checked against the other bus names already in that circuit.
        self.name = name

        # Add the bus to the circuit.
        self.circuit = None  # Make sure bus isn't seen as part of circuit.
        attribs["circuit"] += self  # Add bus to circuit (also sets self.circuit).

        # Build the bus from net widths, existing nets, nets of pins, other buses.
        self.extend(args)

    def __str__(self):
        """Return a list of the nets in this bus as a string."""
        return self.name + ":\n\t" + "\n\t".join([n.__str__() for n in self.nets])

    __repr__ = __str__  # TODO: This is a temporary fix. Need a better __repr__ for Bus.

    def __iter__(self):
        """
        Return an iterator for stepping thru individual lines of the bus.
        """
        return (self[l] for l in range(len(self)))  # Return generator expr.

    def __getitem__(self, *ids):
        """
        Return a NetPinList made up of the nets at the given indices.

        Args:
            ids: A list of indices of bus lines. These can be individual
                numbers, net names, nested lists, or slices.

        Returns:
            A NetPinList if the indices are valid, otherwise None.
        """

        # Use the indices to get the nets from the bus.
        nets = []
        for ident in expand_indices(0, len(self) - 1, False, *ids):
            if isinstance(ident, int):
                nets.append(self.nets[ident])
            elif isinstance(ident, basestring):
                nets.extend(filter_list(self.nets, name=ident))
            else:
                active_logger.raise_(
                    TypeError, "Can't index bus with a {}.".format(type(ident))
                )

        if len(nets) == 0:
            # No nets were selected from the bus, so return None.
            return None

        if len(nets) == 1:
            # Just one net selected, so return the Net object.
            return nets[0]

        # Multiple nets selected, so return them as a NetPinList list.
        return NetPinList(nets)

    def __setitem__(self, ids, pins_nets_buses):
        """
        You can't assign to bus lines. You must use the += operator.

        This method is a work-around that allows the use of the += for making
        connections to bus lines while prohibiting direct assignment. Python
        processes something like my_bus[7:0] += 8 * Pin() as follows::

            1. Bus.__getitem__ is called with '7:0' as the index. This
               returns a NetPinList of eight nets from my_bus.
            2. The NetPinList.__iadd__ method is passed the NetPinList and
               the thing to connect to the it (eight pins in this case). This
               method makes the actual connection to the part pin or pins. Then
               it creates an iadd_flag attribute in the object it returns.
            3. Finally, Bus.__setitem__ is called. If the iadd_flag attribute
               is true in the passed argument, then __setitem__ was entered
               as part of processing the += operator. If there is no
               iadd_flag attribute, then __setitem__ was entered as a result
               of using a direct assignment, which is not allowed.
        """

        # If the iadd_flag is set, then it's OK that we got
        # here and don't issue an error. Also, delete the flag.
        if from_iadd(pins_nets_buses):
            rmv_iadd(pins_nets_buses)
            return

        # No iadd_flag or it wasn't set. This means a direct assignment
        # was made to the pin, which is not allowed.
        active_logger.raise_(TypeError, "Can't assign to a bus! Use the += operator.")

    def __iadd__(self, *pins_nets_buses):
        """Connect nets, pins, or buses to the bus."""
        return self.connect(*pins_nets_buses)

    def __call__(self, num_copies=None, **attribs):
        """Calling the Bus object will make multiple copies of the bus."""
        return self.copy(num_copies=num_copies, **attribs)

    def __mul__(self, num_copies):
        """Use the multiplication operator to make multiple copies of the bus."""
        if num_copies is None:
            num_copies = 0
        return self.copy(num_copies=num_copies)

    __rmul__ = __mul__  # Make the reverse multiplication operator do the same thing.

    def __len__(self):
        """Return the number of nets in this bus."""
        return len(self.nets)

    def __bool__(self):
        """Any valid Bus is True."""
        return True

    __nonzero__ = __bool__  # Python 2 compatibility.

    @classmethod
    def get(cls, name, circuit=None):
        """Get the bus with the given name from a circuit, or return None."""

        circuit = circuit or default_circuit

        search_params = (
            ("name", name, True),
            ("aliases", name, True),
            # ('name', ''.join(('.*',name,'.*')), False),
            # ('aliases', Alias(''.join(('.*',name,'.*'))), False)
        )

        for attr, name, do_str_match in search_params:
            buses = filter_list(
                circuit.buses, do_str_match=do_str_match, **{attr: name}
            )
            if buses:
                return list_or_scalar(buses)

        return None

    @classmethod
    def fetch(cls, name, *args, **attribs):
        """Get the bus with the given name from a circuit, or create it if not found."""

        circuit = attribs.get("circuit", default_circuit)
        return cls.get(name, circuit=circuit) or cls(name, *args, **attribs)

    def insert(self, index, *objects):
        """Insert objects into bus starting at indexed position."""

        for obj in flatten(objects):
            if isinstance(obj, int):
                # Add a number of new nets to the bus.
                for _ in range(obj):
                    self.nets.insert(index, Net(circuit=self.circuit))
                index += obj
            elif isinstance(obj, Net):
                # Add an existing net to the bus.
                self.nets.insert(index, obj)
                index += 1
            elif isinstance(obj, Pin):
                # Add a pin to the bus.
                try:
                    # Add the pin's net to the bus.
                    self.nets.insert(index, obj.get_nets()[0])
                except IndexError:
                    # OK, the pin wasn't already connected to a net,
                    # so create a new net, connect the pin to it,
                    # and add it to the bus.
                    n = Net(circuit=self.circuit)
                    n += obj
                    self.nets.insert(index, n)
                index += 1
            elif isinstance(obj, Bus):
                # Add an existing bus to this bus.
                for n in reversed(obj.nets):
                    self.nets.insert(index, n)
                index += len(obj)
            else:
                active_logger.raise_(
                    ValueError,
                    "Adding illegal type of object ({}) to Bus {}.".format(
                        type(obj), self.name
                    ),
                )

        # Assign names to all the unnamed nets in the bus.
        # Separate index from bus name if name ends with number.
        sep = "_" if self.name[-1].isdigit() else ""
        for i, net in enumerate(self.nets):
            if net.is_implicit():
                # Net names are the bus name with the index appended.
                net.name = self.name + sep + str(i)

    def extend(self, *objects):
        """Extend bus by appending objects to the end (MSB)."""
        self.insert(len(self.nets), objects)

    def copy(self, num_copies=None, **attribs):
        """
        Make zero or more copies of this bus.

        Args:
            num_copies: Number of copies to make of this bus.

        Keyword Args:
            attribs: Name/value pairs for setting attributes for the copy.

        Returns:
            A list of Bus copies or a Bus if num_copies==1.

        Raises:
            Exception if the requested number of copies is a non-integer or negative.

        Notes:
            An instance of a bus can be copied just by calling it like so::

                b = Bus('A', 8)  # Create a bus.
                b_copy = b(2)   # Get two copies of the bus.

            You can also use the multiplication operator to make copies::

                b = 10 * Bus('A', 8)  # Create an array of buses.
        """

        # If the number of copies is None, then a single copy will be made
        # and returned as a scalar (not a list). Otherwise, the number of
        # copies will be set by the num_copies parameter or the number of
        # values supplied for each part attribute.
        num_copies_attribs = find_num_copies(**attribs)
        return_list = (num_copies is not None) or (num_copies_attribs > 1)
        if num_copies is None:
            num_copies = max(1, num_copies_attribs)

        # Check that a valid number of copies is requested.
        if not isinstance(num_copies, int):
            active_logger.raise_(
                ValueError,
                "Can't make a non-integer number ({}) of copies of a bus!".format(
                    num_copies
                ),
            )
        if num_copies < 0:
            active_logger.raise_(
                ValueError,
                "Can't make a negative number ({}) of copies of a bus!".format(
                    num_copies
                ),
            )

        copies = []
        for i in range(num_copies):

            cpy = Bus(self.name, self)

            # Attach additional attributes to the bus.
            for k, v in list(attribs.items()):
                if isinstance(v, (list, tuple)):
                    try:
                        v = v[i]
                    except IndexError:
                        active_logger.raise_(
                            ValueError,
                            "{} copies of bus {} were requested, but too few elements in attribute {}!".format(
                                num_copies, self.name, k
                            ),
                        )
                setattr(cpy, k, v)

            copies.append(cpy)

        # Return a list of the copies made or just a single copy.
        if return_list:
            return copies
        return copies[0]

    def get_nets(self):
        """Return the list of nets contained in this bus."""
        return self.nets

    def get_pins(self):
        """It's an error to get the list of pins attached to all bus lines."""
        active_logger.raise_("Can't get the list of pins on a bus!")

    def is_movable(self):
        """
        Return true if all the nets in a bus are movable to another circuit.
        """
        return all(n.is_movable() for n in self.nets)

    def is_implicit(self):
        """Return true if the bus name is implicit."""
        prefix_re = "({}|{})+".format(re.escape(NET_PREFIX), re.escape(BUS_PREFIX))
        return re.match(prefix_re, self.name)

    def connect(self, *pins_nets_buses):
        """
        Return the bus after connecting one or more nets, pins, or buses.

        Args:
            pins_nets_buses: One or more Pin, Net or Bus objects or
                lists/tuples of them.

        Returns:
            The updated bus with the new connections.

        Notes:
            You can connect nets or pins to a bus like so::

                p = Pin()       # Create a pin.
                n = Net()       # Create a net.
                b = Bus('B', 2) # Create a two-wire bus.
                b += p,n        # Connect pin and net to B[0] and B[1].
        """
        nets = NetPinList(self.nets)
        nets += pins_nets_buses
        return self

    @property
    def name(self):
        """
        Get, set and delete the name of the bus.

        When setting the bus name, if another bus with the same name
        is found, the name for this bus is adjusted to make it unique.
        """
        return super(Bus, self).name

    @name.setter
    def name(self, name):
        # Remove the existing name so it doesn't cause a collision if the
        # object is renamed with its existing name.
        del self.name

        # Now name the object with the given name or some variation
        # of it that doesn't collide with anything else in the list.
        super(Bus, self.__class__).name.fset(
            self, get_unique_name(self.circuit.buses, "name", BUS_PREFIX, name)
        )

    @name.deleter
    def name(self):
        """Delete the bus name."""
        super(Bus, self.__class__).name.fdel(self)

    @property
    def width(self):
        """Return width of a Bus, which is the same as using the len() operator."""
        return len(self)

    @property
    def pins(self):
        return self.get_pins()
