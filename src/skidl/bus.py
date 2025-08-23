# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Bus management in SKiDL.

This module provides the Bus class for creating and managing collections of related
nets. Buses can be indexed to access individual nets, sliced to access multiple nets,
interconnected with pins and other buses, and copied to create multiple instances.
Buses are essential for handling multi-bit signals like data paths or address lines.
"""

import re
from copy import copy
from collections.abc import Iterable

try:
    from future import standard_library

    standard_library.install_aliases()
except ImportError:
    pass

from .alias import Alias
from .logger import active_logger
from .net import NET_PREFIX, Net
from .design_class import NetClasses
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
    A collection of related nets that can be indexed and connected as a group.
    
    Bus objects group nets to represent multi-bit signals like data buses, address buses,
    or other related collections of signals. Buses can be created from integer widths,
    existing nets, pins, or other buses. Individual nets in a bus can be accessed using
    integer indices, slices, or net names.
    
    Args:
        name (str, optional): The name of the bus. If None, an implicit name will be generated.
        *args: Various objects to create bus from - can include integers (for width), 
              pins, nets, or other buses.
    
    Keyword Args:
        circuit (Circuit, optional): The Circuit object this bus belongs to.
        attribs: Various attributes to attach to the bus.
        
    Examples:
        >>> data_bus = Bus('DATA', 8)  # Create 8-bit DATA bus
        >>> addr_bus = Bus('ADDR', 16)  # Create 16-bit ADDR bus
        >>> data_bus[0] += some_pin  # Connect a pin to bit 0
        >>> byte_bus = data_bus[7:0]  # Create a slice of the bus
    """

    def __init__(self, *args, **attribs):

        super().__init__()

        # Define the member storing the nets so it's present, but it starts empty.
        self.nets = []

        self.do_erc = True
        self.circuit = None
        self._netclasses = NetClasses()  # Net classes directly assigned to this net.

        # Scan through the kwargs and args to see if there is a name for this bus.
        name = attribs.pop("name", None)
        if not name:
            try:
                # The first string found will be the bus name.
                name = [a for a in args if isinstance(a, (str, type(None)))][0]
                # Remove the name from the list of things to be added to the bus.
                args = list(args)
                args.remove(name)
                # args = [a for a in args if a != name]
            except IndexError:
                # No explicit bus name found, so generate an implicit one.
                name = None

        # Set the net name directly to the passed-in name without any adjustment.
        # The net name will be adjusted when it is added to the circuit which
        # may already have a net with the same name.
        self._name = name

        # For Bus objects, the circuit object that the bus is a member of is passed
        # in with all the other attributes. If a circuit object isn't provided,
        # then use the default circuit object.
        circuit = attribs.pop("circuit", default_circuit)

        # Add the bus to the circuit.
        circuit += self

        # Attach additional attributes to the bus. (The Circuit object also gets
        # set here.)
        for k, v in list(attribs.items()):
            setattr(self, k, v)

        # Build the bus from net widths, existing nets, nets of pins, other buses.
        self.extend(args)

    def __str__(self):
        """
        Return a string representation of the bus.
        
        Returns:
            str: Bus name followed by a list of nets in the bus.
        """
        return self.name + ":\n\t" + "\n\t".join([n.__str__() for n in self.nets])

    __repr__ = __str__  # TODO: This is a temporary fix. Need a better __repr__ for Bus.

    def __iter__(self):
        """
        Return an iterator for stepping through individual nets in the bus.
        
        Returns:
            iterator: An iterator yielding each net in the bus.
        """
        return (self[l] for l in range(len(self)))  # Return generator expr.

    def __getitem__(self, *ids):
        """
        Return a net or NetPinList of nets at the specified indices.
        
        Bus indexing supports integers, net names, and slices. When multiple 
        indices are selected, returns a NetPinList containing the nets.
        
        Args:
            *ids: Indices of nets to get. Can be integers, strings (net names),
                 slices, or nested lists of these.
                 
        Returns:
            Net or NetPinList: The requested net(s) from the bus.
            
        Raises:
            TypeError: If an unsupported index type is used.
        """

        # Use the indices to get the nets from the bus.
        nets = []
        for ident in expand_indices(0, len(self) - 1, False, *ids):
            if isinstance(ident, int):
                nets.append(self.nets[ident])
            elif isinstance(ident, str):
                nets.extend(filter_list(self.nets, name=ident))
            else:
                active_logger.raise_(
                    TypeError, f"Can't index bus with a {type(ident)}."
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
        
        You can't allow use of the +. You must use the += operator.= for making
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
        """
        Connect nets, pins, or buses to this bus.
        
        Args:
            *pins_nets_buses: Objects to connect to the bus.
            
        Returns:
            Bus: The updated bus with new connections.
        """
        return self.connect(*pins_nets_buses)

    def __call__(self, num_copies=None, **attribs):
        """
        Create multiple copies of this bus.
        
        Args:
            num_copies (int, optional): Number of copies to create.
            **attribs: Attributes to apply to the copies.
            
        Returns:
            Bus or list[Bus]: Copy or copies of the bus.
        """
        return self.copy(num_copies=num_copies, **attribs)

    def __mul__(self, num_copies):
        """
        Multiply operator to create multiple copies of the bus.
        
        Args:
            num_copies (int): Number of copies to create.
            
        Returns:
            list[Bus]: List of bus copies.
        """
        if num_copies is None:
            num_copies = 0
        return self.copy(num_copies=num_copies)

    __rmul__ = __mul__  # Make the reverse multiplication operator do the same thing.

    def __len__(self):
        """
        Return the number of nets in the bus.
        
        Returns:
            int: Number of nets in the bus.
        """
        return len(self.nets)

    def __bool__(self):
        """
        Return True if the bus is valid (always True).
        
        Returns:
            bool: Always True for any bus instance.
        """
        return True

    __nonzero__ = __bool__  # Python 2 compatibility.

    @classmethod
    def get(cls, name, circuit=None):
        """
        Get a bus by name from a circuit.
        
        Args:
            name (str): Name or alias of the bus to find.
            circuit (Circuit, optional): Circuit to search in. Defaults to default_circuit.
            
        Returns:
            Bus or None: The found bus object or None if not found.
        """

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
        """
        Get a bus by name from a circuit, or create it if it doesn't exist.
        
        This method is similar to get(), but will create a new bus if one
        with the given name is not found.
        
        Args:
            name (str): Name of the bus to fetch or create.
            *args: Arguments to pass to the Bus constructor if creation is needed.
            **attribs: Keyword arguments to pass to the Bus constructor if creation is needed.
            
        Returns:
            Bus: An existing or newly created bus.
        """

        circuit = attribs.get("circuit", default_circuit)
        return cls.get(name, circuit=circuit) or cls(name, *args, **attribs)

    def insert(self, index, *objects):
        """
        Insert objects into the bus starting at the given index.
        
        Objects can be integers (to create N new nets), existing nets, pins, or buses.
        New nets will be given names based on the bus name and their position.
        
        Args:
            index (int): Position to insert objects.
            *objects: Objects to insert - integers, nets, pins, or buses.
            
        Raises:
            ValueError: If an unsupported object type is inserted.
        """

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
                    f"Adding illegal type of object ({type(obj)}) to Bus {self.name}.",
                )

        # Assign names to all the unnamed nets in the bus.
        # Separate index from bus name if name ends with number.
        sep = "_" if self.name[-1].isdigit() else ""
        for i, net in enumerate(self.nets):
            if net.is_implicit():
                # Net names are the bus name with the index appended.
                net.name = self.name + sep + str(i)

        # Add the net class of the bus to each net it contains. 
        self.propagate_netclasses()

    def extend(self, *objects):
        """
        Extend the bus by adding nets to the end (MSB).
        
        Args:
            *objects: Objects to add - integers, nets, pins, or buses.
        """
        self.insert(len(self.nets), objects)

    def copy(self, num_copies=None, circuit=None, **attribs):
        """
        Create one or more copies of this bus.
        
        Args:
            num_copies (int, optional): Number of copies to create.
                If None, a single copy will be made.
            circuit (Circuit, optional): The circuit the copies will be added to.
            **attribs: Attributes for the copies. If values are lists/tuples,
                each copy gets the corresponding value.
                
        Returns:
            Bus or list[Bus]: A single Bus copy or list of copies.
            
        Raises:
            ValueError: If num_copies is not a non-negative integer.
            
        Examples:
            >>> b = Bus('A', 8)
            >>> b_copy = b(2)  # Get two copies
            >>> b_array = 5 * Bus('A', 8)  # Create an array of 5 buses
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
                f"Can't make a non-integer number ({num_copies}) of copies of a bus!",
            )
        if num_copies < 0:
            active_logger.raise_(
                ValueError,
                f"Can't make a negative number ({num_copies}) of copies of a bus!",
            )

        # If circuit is not specified, then create the copies within circuit of the
        # original, or in the default circuit.
        circuit = circuit or self.circuit or default_circuit

        # If a name is not specified, then copy the name from the original.
        # This will get disambiguated when the copy is created.
        name = attribs.pop("name", self.name)

        # Skip some Bus attributes that would cause an infinite recursion exception
        # or bus naming clashes.
        skip_attrs = ("circuit", "_name", "_aliases")

        copies = []
        for i in range(num_copies):

            # Create a new bus to store the copy.
            cpy = Bus(name=name, circuit=circuit)

            # Copy stuff from the original bus to the copy.
            for k,v in self.__dict__.items():
                if k in skip_attrs:
                    continue
                if isinstance(v, Iterable) and not isinstance(v, str):
                    # Copy the list with shallow copies of its items to the copy.
                    setattr(cpy, k, copy(v))
                else:
                    setattr(cpy, k, v)

            # Attach additional attributes to the bus.
            for k, v in list(attribs.items()):
                setattr(cpy, k, v)

            copies.append(cpy)

        # Return a list of the copies made or just a single copy.
        if return_list:
            return copies
        return copies[0]

    def get_nets(self):
        """
        Return the list of nets contained in this bus.
        
        Returns:
            list[Net]: Nets in this bus.
        """
        return self.nets

    def get_pins(self):
        """
        Raise an error since accessing all pins across a bus is not supported.
        
        Raises:
            Exception: Always raises an error.
        """
        active_logger.raise_("Can't get the list of pins on a bus!")

    def is_movable(self):
        """
        Check if the bus can be moved to another circuit.
        
        A bus is movable if all of its nets are movable.
        
        Returns:
            bool: True if all nets in the bus are movable.
        """
        return all(n.is_movable() for n in self.nets)

    def is_implicit(self):
        """
        Check if the bus name is implicitly generated.
        
        Implicit bus names start with the BUS_PREFIX or NET_PREFIX.
        
        Returns:
            bool: True if the bus has an implicitly generated name.
        """
        prefix_re = f"({re.escape(NET_PREFIX)}|{re.escape(BUS_PREFIX)})+"
        return re.match(prefix_re, self.name)

    def connect(self, *pins_nets_buses):
        """
        Connect pins, nets, or buses to this bus.
        
        Args:
            *pins_nets_buses: Pins, nets, buses or lists/tuples of them to connect.
            
        Returns:
            Bus: The updated bus with the new connections.
            
        Examples:
            >>> b = Bus('B', 2)
            >>> p = Pin()
            >>> n = Net()
            >>> b += p, n  # Connect pin to B[0] and net to B[1]
        """
        nets = NetPinList(self.nets)
        nets += pins_nets_buses

        # Propagate net classes in any buses that were connected.
        self.propagate_netclasses()
        for pnb in pins_nets_buses:
            if isinstance(pnb, Bus):
                pnb.propagate_netclasses()

        return self
    
    def propagate_netclasses(self):

        # Nothing to do if bus has no nets.
        if not self.nets:
            return

        # Propagate the bus net class to all its constituent nets.
        for net in self.nets:
            net.netclasses = self._netclasses

        # Update the bus net classes with the net classes that all its nets have in common.
        # Don't call self.netclasses or you'll get infinite recursion!
        self._netclasses.add(set.intersection(*(set(n.netclasses) for n in self.nets)))


    @property
    def netclasses(self):
        # Add all the net classes for all the hierarchical nodes surrounding this bus.
        total_netclasses = self.node.netclasses

        # Add the netclasses directly assigned to this bus.
        total_netclasses.add(self._netclasses)

        return total_netclasses
    
    @netclasses.setter
    def netclasses(self, *netclasses):
        # Add the passed-in net classes.
        self._netclasses.add(netclasses, circuit=self.circuit)

        # Propagate the netclasses to all the nets in the bus.
        self.propagate_netclasses()

    @netclasses.deleter
    def netclasses(self):
        self._netclasses = NetClasses()
        for net in self.nets:
            del net.netclasses

    @property
    def name(self):
        """
        Get the name of the bus.
        
        When setting the name, if another bus with the same name exists in the
        circuit, the name will be adjusted to make it unique.
        
        Returns:
            str: The bus name.
        """
        return super(Bus, self).name

    @name.setter
    def name(self, name):
        """
        Set the bus name.
        
        Args:
            name (str): The new name for the bus.
        """
        # Remove the existing name so it doesn't cause a collision if the
        # object is renamed with its existing name.
        del self.name

        # Now name the object with the given name or some variation
        # of it that doesn't collide with anything else in the list.
        super(Bus, type(self)).name.fset(
            self, get_unique_name(self.circuit.buses, "name", BUS_PREFIX, name)
        )

    @name.deleter
    def name(self):
        """
        Delete the bus name.
        
        This reverts the bus to having no name.
        """
        super(Bus, type(self)).name.fdel(self)

    @property
    def width(self):
        """
        Get the width of the bus (number of nets).
        
        Returns:
            int: The number of nets in the bus.
        """
        return len(self)

    @property
    def pins(self):
        """
        Get all pins connected to the bus.
        
        Returns:
            list: List of pins connected to the bus nets.
            
        Raises:
            Exception: Always raises an error since accessing all pins across a bus is not supported.
        """
        return self.get_pins()
