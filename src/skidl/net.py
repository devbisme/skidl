# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Network connection management in SKiDL.

This module provides the Net class which represents electrical connections between
component pins. Nets can be named, connected to pins, merged with other nets, and
checked for electrical rule violations. The module also provides the NCNet subclass
for explicitly marking pins as not connected.
"""

import collections
import re
from copy import copy, deepcopy

from .erc import dflt_net_erc
from .logger import active_logger
from .skidlbaseobj import SkidlBaseObject
from .utilities import (
    expand_buses,
    expand_indices,
    export_to_all,
    filter_list,
    find_num_copies,
    flatten,
    from_iadd,
    get_unique_name,
    rmv_iadd,
    set_iadd,
)


__all__ = ["NET_PREFIX"]

# Prefix for implicit nets.
NET_PREFIX = "N$"

Traversal = collections.namedtuple("Traversal", ["nets", "pins"])


@export_to_all
class Net(SkidlBaseObject):
    """
    A collection of electrically connected component pins.
    
    Nets represent electrical connections in a circuit and can have names, 
    drive strengths, and electrical rules checking (ERC) applied to them. 
    Pins can be connected to nets using the += operator.
    
    Args:
        name (str, optional): Name of the net. If None or empty, a unique name will be generated.
        circuit (Circuit, optional): The circuit this net belongs to. If None, the default circuit is used.
        *pins_nets_buses: One or more Pin, Net, or Bus objects to connect to this net.
        
    Keyword Args:
        attribs: Arbitrary keyword=value attributes to attach to the net.
        
    Examples:
        >>> gnd = Net('GND')  # Create a net called GND
        >>> gnd += part1['GND']  # Connect pin of part1 to GND
        >>> net1 = Net()  # Create a net with an automatically assigned name
        >>> net1 += part2[1], part3[6]  # Connect pins from two parts to the net
    """

    # Set the default ERC functions for all Net instances.
    erc_list = [dflt_net_erc]

    def __init__(self, name=None, circuit=None, *pins_nets_buses, **attribs):
        from .pin import pin_drives

        super().__init__()

        self._valid = True  # Make net valid before doing anything else.
        self.do_erc = True
        self._drive = pin_drives.NONE
        self._pins = []
        self.circuit = None
        self.code = None  # This is the net number used in a KiCad netlist file.
        self.stub = False  # Net is not a stub for schematic generation.

        # Set the net name directly to the passed-in name without any adjustment.
        # The net name will be adjusted when it is added to the circuit which
        # may already have a net with the same name.
        self._name = name

        # Add the net to the passed-in circuit or to the default circuit.
        circuit = circuit or default_circuit
        circuit += self

        # Attach whatever pins were given.
        self.connect(pins_nets_buses)
        del self.iadd_flag  # Remove the += flag inserted by connect().

        # Attach additional attributes to the net.
        for k, v in list(attribs.items()):
            setattr(self, k, v)

    def __bool__(self):
        """
        Return True if this is a valid net.
        
        Returns:
            bool: Always True for valid nets.
        """
        return True

    __nonzero__ = __bool__  # Python 2 compatibility.

    def __str__(self):
        """
        Return a string representation of the net and its connected pins.
        
        Returns:
            str: Net name followed by the pins connected to it, sorted alphabetically.
        """
        self.test_validity()
        pins = self.pins
        return (
            self.name + ": " + ", ".join([p.__str__() for p in sorted(pins, key=str)])
        )

    __repr__ = __str__  # TODO: This is a temporary fix. The __repr__ should be more informative.

    # Use += to connect to nets.
    def __iadd__(self, *pins_nets_buses):
        """
        Connect pins, nets, or buses to this net.
        
        Args:
            *pins_nets_buses: One or more Pin, Net, or Bus objects to connect.
            
        Returns:
            Net: Updated net with new connections.
        """
        return self.connect(*pins_nets_buses)

    def __and__(self, obj):
        """
        Connect this net and another object in series.
        
        Args:
            obj: Another part, pin, or net to connect in series with this net.
            
        Returns:
            Network: A series network containing this net and the other object.
        """
        from .network import Network

        return Network(self) & obj

    def __rand__(self, obj):
        """
        Connect another object and this net in series.
        
        Args:
            obj: Another part, pin, or net to connect in series with this net.
            
        Returns:
            Network: A series network containing the other object and this net.
        """
        from .network import Network

        return obj & Network(self)

    def __or__(self, obj):
        """
        Connect this net and another object in parallel.
        
        Args:
            obj: Another part, pin, or net to connect in parallel with this net.
            
        Returns:
            Network: A parallel network containing this net and the other object.
        """
        from .network import Network

        return Network(self) | obj

    def __ror__(self, obj):
        """
        Connect another object and this net in parallel.
        
        Args:
            obj: Another part, pin, or net to connect in parallel with this net.
            
        Returns:
            Network: A parallel network containing the other object and this net.
        """
        from .network import Network

        return obj | Network(self)

    def __len__(self):
        """
        Return the number of pins attached to this net.
        
        Returns:
            int: Number of pins connected to this net.
        """
        self.test_validity()
        return len(self.pins)

    def __getitem__(self, *ids):
        """
        Return the net if the indices resolve to a single index of 0.
        
        A net only has one element (itself), so the only valid index is 0.
        
        Args:
            *ids: A list of indices to apply to the net.
            
        Returns:
            Net: This net if the index is 0, otherwise None or raises an exception.
            
        Raises:
            ValueError: If multiple indices or a non-zero index is used.
        """

        # Resolve the indices.
        indices = list(set(expand_indices(0, self.width - 1, False, *ids)))
        if indices is None or len(indices) == 0:
            return None
        if len(indices) > 1:
            active_logger.raise_(ValueError, "Can't index a net with multiple indices.")
        if indices[0] != 0:
            active_logger.raise_(ValueError, "Can't use a non-zero index for a net.")
        return self

    def __setitem__(self, ids, *pins_nets_buses):
        """
        Prohibit direct assignment to nets. Use the += operator instead.
        
        This method is a work-around that allows the use of the += for making
connections to nets while         prohibiting direct assignment. Python
        processes something like net[0] += Pin() as follows::

            1. Net.__getitem__ is called with '0' as the index. This
               returns a single Net.
            2. The Net.__iadd__ method is passed the net and
               the thing to connect to it (a Pin in this case). This
               method makes the actual connection to the pin. Then
               it creates an iadd_flag attribute in the object it returns.
            3. Finally, Net.__setitem__ is called. If the iadd_flag attribute
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
        active_logger.raise_(TypeError, "Can't assign to a Net! Use the += operator.")

    def __iter__(self):
        """
        Return an iterator for stepping through the net.
        
        A net iterator only yields the net itself because a net has only one element.
        
        Returns:
            iterator: Generator that yields this net.
        """
        # You can only iterate a Net one time.
        return (self[i] for i in [0])  # Return generator expr.

    def __call__(self, num_copies=None, circuit=None, **attribs):
        """
        Create one or more copies of this net.
        
        Args:
            num_copies (int, optional): Number of copies to create.
            circuit (Circuit, optional): Circuit to add the copies to.
            **attribs: Additional attributes to apply to the copies.
            
        Returns:
            Net or list[Net]: Single net or list of net copies.
        """
        return self.copy(num_copies=num_copies, circuit=circuit, **attribs)

    def __mul__(self, num_copies):
        """
        Create multiple copies of this net using the multiplication operator.
        
        Args:
            num_copies (int): Number of copies to create.
            
        Returns:
            list[Net]: List of net copies.
        """
        if num_copies is None:
            num_copies = 0
        return self.copy(num_copies=num_copies)

    __rmul__ = __mul__

    @classmethod
    def get(cls, name, circuit=None):
        """
        Get a net by name from a circuit.
        
        Args:
            name (str): Name or alias of the net to find.
            circuit (Circuit, optional): Circuit to search in. Defaults to default_circuit.
            
        Returns:
            Net or None: The found net object or None if not found.
        """

        from .alias import Alias

        circuit = circuit or default_circuit

        search_params = (("name", name, True), ("aliases", name, True))

        for attr, name, do_str_match in search_params:
            # filter_list() always returns a list. A net can consist of multiple
            # interconnected Net objects. If the list is non-empty,
            # just return the first Net object on the list.
            nets = filter_list(circuit.nets, do_str_match=do_str_match, **{attr: name})
            try:
                return nets[0]
            except IndexError:
                pass

        return None

    @classmethod
    def fetch(cls, name, *args, **attribs):
        """
        Get a net by name from a circuit, or create it if not found.
        
        This method tries to find a net with the given name in the circuit.
        If not found, it creates a new net with that name.
        
        Args:
            name (str): Name of the net to fetch or create.
            *args: Arguments to pass to the Net constructor if creation is needed.
            **attribs: Keyword arguments to pass to the Net constructor if creation is needed.
            
        Returns:
            Net: An existing or newly created net.
        """

        circuit = attribs.get("circuit", default_circuit)
        return cls.get(name, circuit=circuit) or cls(name, *args, **attribs)

    def get_pins(self):
        """
        Get all pins connected to this net.
        
        Returns:
            list: List of pins attached to this net, including pins attached
                 to electrically connected segments.
        """
        self.test_validity()
        return self._traverse().pins

    def get_nets(self):
        """
        Get all connected net segments including this one.
        
        Returns:
            list: List of all net segments connected to this net, including this net.
        """
        self.test_validity()
        return self._traverse().nets

    def is_attached(self, pin_net_bus):
        """
        Check if a pin, net, or bus is electrically connected to this net.
        
        Args:
            pin_net_bus: A Pin, Net, or Bus object to check for attachment.
            
        Returns:
            bool: True if the object is electrically connected to this net.
            
        Raises:
            TypeError: If the given object is not a Pin, Net, or Bus.
        """
        if isinstance(pin_net_bus, Net):
            return pin_net_bus in self.nets
        if isinstance(pin_net_bus, Pin):
            return pin_net_bus.is_attached(self)
        if isinstance(pin_net_bus, Bus):
            for net in pin_net_bus[:]:
                if self.is_attached(net):
                    return True
            return False
        active_logger.raise_(
            TypeError, "Nets can't be attached to {}!".format(type(pin_net_bus))
        )

    def is_movable(self):
        """
        Check if the net can be moved to another circuit.
        
        A net is movable if it's not part of a Circuit or if it has no pins
        attached to it.
        
        Returns:
            bool: True if the net is movable.
        """

        from .circuit import Circuit

        return not isinstance(self.circuit, Circuit) or not self._pins

    def is_implicit(self):
        """
        Check if the net has an implicitly generated name.
        
        Implicit net names start with NET_PREFIX or BUS_PREFIX.
        
        Returns:
            bool: True if the net name is implicitly generated.
        """

        from .bus import BUS_PREFIX

        self.test_validity()
        prefix_re = "({}|{})+".format(re.escape(NET_PREFIX), re.escape(BUS_PREFIX))
        return re.match(prefix_re, self.name)

    def copy(self, num_copies=None, circuit=None, **attribs):
        """
        Create one or more copies of this net.
        
        Args:
            num_copies (int, optional): Number of copies to create.
                If None, a single copy will be made.
            circuit (Circuit, optional): The circuit the copies will be added to.
            **attribs: Attributes to apply to the copies.
                
        Returns:
            Net or list[Net]: A single Net copy or list of copies.
            
        Raises:
            ValueError: If num_copies is not a non-negative integer.
            ValueError: If trying to copy a net that already has pins attached.
            
        Examples:
            >>> n = Net('A')    # Create a net.
            >>> n_copy = n()    # Copy the net.
            >>> n_array = 10 * Net('A')  # Create an array of 10 nets.
        """

        self.test_validity()

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
                "Can't make a non-integer number "
                "({}) of copies of a net!".format(num_copies),
            )
        if num_copies < 0:
            active_logger.raise_(
                ValueError,
                "Can't make a negative number "
                "({}) of copies of a net!".format(num_copies),
            )

        # If circuit is not specified, then create the copies within circuit of the
        # original, or in the default circuit.
        circuit = circuit or self.circuit or default_circuit

        # Can't make a distinct copy of a net which already has pins on it
        # because what happens if a pin is connected to the copy? Then we have
        # to search for all the other copies to add the pin to those.
        # And what's the value of that?
        if self._pins:
            active_logger.raise_(
                ValueError,
                "Can't make copies of a net that already has " "pins attached to it!",
            )

        # Create a list of copies of this net.
        copies = []

        # Skip some Net attributes that would cause an infinite recursion exception
        # or net naming clashes.
        copy_attrs = vars(self).keys() - ["circuit", "traversal", "_name", "_aliases"]
        
        for i in range(num_copies):

            # Create a new net to store the copy.
            cpy = Net(circuit=circuit)

            # Deep copy attributes from the source net to the copy.
            for k in copy_attrs:
                setattr(cpy, k, deepcopy(getattr(self, k)))

            # Add other attributes to the net copy.
            for k, v in list(attribs.items()):
                if isinstance(v, (list, tuple)):
                    try:
                        v = v[i]
                    except IndexError:
                        active_logger.raise_(
                            ValueError,
                            (
                                "{} copies of net {} were requested, but too "
                                "few elements in attribute {}!"
                            ).format(num_copies, self.name, k),
                        )
                setattr(cpy, k, v)

            # Place the copy into the list of copies.
            copies.append(cpy)

        # Return a list of the copies made or just a single copy.
        if return_list:
            return copies
        return copies[0]

    def connect(self, *pins_nets_buses):
        """
        Connect pins, nets, and buses to this net.
        
        This method connects the provided pins, nets, and buses to this net,
        creating electrical connections between them. It's also accessible via
        the += operator.
        
        Args:
            *pins_nets_buses: One or more Pin, Net, Bus objects or lists/tuples of them
                              to connect to this net.
                
        Returns:
            Net: The updated net with new connections.
            
        Raises:
            ValueError: If attempting to connect nets from different circuits.
            ValueError: If attempting to connect parts from different circuits.
            TypeError: If attempting to connect something other than a Pin or Net.
            
        Examples:
            >>> net1 = Net('NET1')
            >>> net1.connect(part1['GND'], part2[7])  # Connect pins to net
            >>> net1 += part3['A']  # Alternate syntax using += operator
        """

        from .pin import PhantomPin, Pin

        def join(net):
            """
            Join nets by giving them each a pin in common.

            Args:
                net: The net to join with self.
            """

            if isinstance(self, NCNet):
                active_logger.raise_(
                    ValueError,
                    "Can't join with a no-connect net {}!".format(self.name),
                )

            if isinstance(net, NCNet):
                active_logger.raise_(
                    ValueError,
                    "Can't join with a no-connect net {}!".format(net.name),
                )

            # No need to do anything if merging a net with itself.
            if self == net:
                return

            # If this net has pins, just attach the other net to one of them.
            if self._pins:
                self._pins[0].nets.append(net)
                net._pins.append(self._pins[0])
            # If the other net has pins, attach this net to a pin on the other net.
            elif net._pins:
                net._pins[0].nets.append(self)
                self._pins.append(net._pins[0])
            # If neither net has any pins, then attach a phantom pin to one net
            # and then connect the nets together.
            else:
                p = PhantomPin()
                connect_pin(p)
                self._pins[0].nets.append(net)
                net._pins.append(self._pins[0])

            # Update the drive of the joined nets. When setting the drive of a
            # net the net drive will be the maximum of its current drive or the
            # new drive. So the following two operations will set each net
            # drive to the same maximum value.
            self.drive = net.drive
            net.drive = self.drive

            # Update the net class of the joined nets. The following two
            # operations will set each net's class to the same value, or
            # throw an error if they are in different classes.
            self.netclass = net.netclass
            net.netclass = self.netclass

        def connect_pin(pin):
            """Connect a pin to this net."""
            if pin not in self._pins:
                if not pin.is_connected():
                    # Remove the pin from the no-connect net if it is attached to it.
                    pin.disconnect()
                self._pins.append(pin)
                pin.nets.append(self)
                pin.stub = self.stub  # Update pin stub net for generating schematics.
            return

        self.test_validity()

        # Go through all the pins and/or nets and connect them to this net.
        for pn in expand_buses(flatten(pins_nets_buses)):
            if isinstance(pn, Net):
                if pn.circuit == self.circuit:
                    join(pn)
                else:
                    active_logger.raise_(
                        ValueError,
                        "Can't attach nets in different circuits ({}, {})!".format(
                            pn.circuit.name, self.circuit.name
                        ),
                    )
            elif isinstance(pn, Pin):
                if not pn.part or pn.part.circuit == self.circuit:
                    if not pn.part:
                        active_logger.warning(
                            "Attaching non-part Pin {} to a Net {}.".format(
                                pn.name, self.name
                            )
                        )
                    connect_pin(pn)
                elif not pn.part.circuit:
                    active_logger.warning(
                        "Attaching part template Pin {} to a Net {}.".format(
                            pn.name, self.name
                        )
                    )
                else:
                    active_logger.raise_(
                        ValueError,
                        "Can't attach a part to a net in different circuits ({}, {})!".format(
                            pn.part.circuit.name, self.circuit.name
                        ),
                    )
            else:
                active_logger.raise_(
                    TypeError,
                    "Cannot attach non-Pin/non-Net {} to Net {}.".format(
                        type(pn), self.name
                    ),
                )

        # If something has been connected to a net, then recompute its traversal so the
        # correct number of connected pins and nets is recorded.
        try:
            del self.traversal
        except AttributeError:
            pass  # No traversal to delete.
        self._traverse()

        # Add the net to the global netlist. (It won't be added again
        # if it's already there.)
        self.circuit += self

        # Set the flag to indicate this result came from the += operator.
        set_iadd(self, True)

        return self

    def disconnect(self, pin):
        """
        Remove a pin from this net but not from other nets it's attached to.
        
        Args:
            pin (Pin): The pin to disconnect from this net.
        """
        try:
            self._pins.remove(pin)
        except ValueError:
            return  # Pin wasn't in the list, so abort.

        # If a pin has been disconnected from a net, then remove any existing traversal
        # so it will be recomputed the next time it is needed.
        try:
            del self.traversal
        except AttributeError:
            pass  # No traversal to delete.

    def merge_names(self):
        """
        For multi-segment nets, select a common name for all segments.
        
        When nets are joined, they can have different names. This method
        chooses the best name among connected net segments and assigns
        it to all of them.
        """

        def select_name(nets):
            """Return the net with the best name among a list of nets."""

            if len(nets) == 0:
                return None  # No nets, return None.
            if len(nets) == 1:
                return nets[0]  # One net, return it.
            if len(nets) == 2:
                # Two nets, return the best of them.
                name0 = getattr(nets[0], "name")
                name1 = getattr(nets[1], "name")
                fixed0 = getattr(nets[0], "fixed_name", False)
                fixed1 = getattr(nets[1], "fixed_name", False)
                if not name1:
                    return nets[0]
                if not name0:
                    return nets[1]
                if fixed0 and not fixed1:
                    return nets[0]
                if fixed1 and not fixed0:
                    return nets[1]
                if fixed0 and fixed1:
                    active_logger.raise_(
                        ValueError,
                        "Cannot merge two nets with fixed names: {} and {}.".format(
                            name0, name1
                        ),
                    )
                if nets[1].is_implicit():
                    return nets[0]
                if nets[0].is_implicit():
                    return nets[1]
                if name0 != name1:
                    active_logger.warning(
                        "Merging two named nets ({name0} and {name1}) into {name0}.".format(
                            **locals()
                        )
                    )
                return nets[0]

            # More than two nets, so bisect the list into two smaller lists and
            # recursively find the best name from each list and then return the
            # best name of those two.
            mid_point = len(nets) // 2
            return select_name(
                [select_name(nets[0:mid_point]), select_name(nets[mid_point:])]
            )

        # Assign the same name to all the nets that are connected to this net.
        nets = self.nets
        selected_name = getattr(select_name(nets), "name")
        for net in nets:
            # Assign the name directly to each net. Using the name property
            # would cause the names to be changed so they were unique.
            net._name = selected_name  # pylint: disable=protected-access

    def create_network(self):
        """
        Create a Network object containing just this net.
        
        Returns:
            Network: A network containing this net.
        """
        from .network import Network

        ntwk = Network()
        ntwk.append(self)
        return ntwk

    def generate_netlist_net(self, tool=None):
        """
        Generate the net information for inclusion in a netlist.
        
        Args:
            tool (str, optional): The format for the netlist file (e.g., KICAD).
            
        Returns:
            str: The net information formatted for the specified tool.
        """

        import skidl

        from .tools import tool_modules

        tool = tool or skidl.config.tool

        self.test_validity()

        # Don't add anything to the netlist if no pins are on this net.
        if not self.pins:
            return

        return tool_modules[tool].gen_netlist_net(self)

    def generate_xml_net(self, tool=None):
        """
        Generate the net information for inclusion in an XML file.
        
        Args:
            tool (str, optional): The format for the XML file (e.g., KICAD).
            
        Returns:
            str: The net information formatted as XML for the specified tool.
        """

        import skidl

        from .tools import tool_modules

        tool = tool or skidl.config.tool

        self.test_validity()

        # Don't add anything to the XML if no pins are on this net.
        if not self.pins:
            return

        return tool_modules[tool].gen_xml_net(self)

    def _traverse(self):
        """
        Traverse all nets and pins connected to this net.
        
        This method builds a complete list of all pins and nets that are
        electrically connected to this net, either directly or indirectly.
        
        Returns:
            Traversal: A namedtuple containing lists of all connected nets and pins.
        """

        try:
            return self.traversal  # Return pre-existing traversal.
        except AttributeError:
            pass  # Compute the traversal if it's not available.

        from .pin import PhantomPin

        self.test_validity()
        prev_nets = set([self])
        nets = set([self])
        prev_pins = set([])
        pins = set(self._pins)
        while pins != prev_pins:

            # Add the nets attached to any unvisited pins.
            for pin in pins - prev_pins:
                # No use visiting a pin that is not connected to a net.
                if pin.is_connected():
                    nets |= set(pin.nets)

            # Update the set of previously visited pins.
            prev_pins = copy(pins)

            # Add the pins attached to any unvisited nets.
            for net in nets - prev_nets:
                pins |= set(net._pins)

            # Update the set of previously visited nets.
            prev_nets = copy(nets)

        # Remove any phantom pins that may have existed for tieing nets together.
        pins = set([p for p in pins if not isinstance(p, PhantomPin)])

        # Store the traversal.
        self.traversal = Traversal(nets=list(nets), pins=list(pins))

        # Every net connected to this one should have the same traversal.
        for n in self.traversal.nets:
            n.traversal = self.traversal

        return self.traversal

    @property
    def width(self):
        """
        Get the width of the net.
        
        Returns:
            int: Always 1 for a Net object.
        """
        return 1

    @property
    def name(self):
        """
        Get or set the name of this net.
        
        When setting the net name, if another net with the same name
        exists in the circuit, the name for this net will be adjusted
        to make it unique.
        
        Returns:
            str: Net name.
        """
        return super(Net, self).name

    @name.setter
    def name(self, name):
        """
        Set the name of this net.
        
        Args:
            name (str): The new name for the net.
        """
        self.test_validity()
        # Remove the existing name so it doesn't cause a collision if the
        # object is renamed with its existing name.
        del self.name

        # Now name the object with the given name or some variation
        # of it that doesn't collide with anything else in the list.
        super(Net, self.__class__).name.fset(
            self, get_unique_name(self.circuit.nets, "name", NET_PREFIX, name)
        )

    @name.deleter
    def name(self):
        """Delete the net name."""
        self.test_validity()
        super(Net, self.__class__).name.fdel(self)

    @property
    def pins(self):
        """
        Get the pins attached to this net.
        
        Returns:
            list: List of pins attached to this net.
        """
        return self.get_pins()

    @property
    def nets(self):
        """
        Get all net segments connected to this net.
        
        Returns:
            list: List of all net segments electrically connected to this net.
        """
        return self.get_nets()

    @property
    def netclass(self):
        """
        Get, set or delete the net class assigned to this net.
        
        Net classes can be used to group nets and apply specific attributes to them.
        Once set, a net class cannot be overwritten - it must be deleted first.
        
        Returns:
            NetClass or None: The net class object assigned to this net, or None if no class is assigned.
            
        Raises:
            ValueError: When trying to assign a different net class to a net that already has one.
        """
        self.test_validity()
        return getattr(self, "_netclass", None)

    @netclass.setter
    def netclass(self, netclass):
        """
        Set the net class for this net.
        
        Args:
            netclass (NetClass): The net class to assign to this net.
            
        Raises:
            ValueError: If trying to assign a different net class to a net that already has one.
        """
        self.test_validity()

        # Just leave the existing net class at its current value if setting the
        # net class to None. This is useful when merging nets because you just
        # assign each net the net class of the other and they should both get
        # the same net class (either None or the value of the net class of one,
        # the other, or both.)
        if netclass is None:
            return

        # A net class can only be assigned if there is no existing net class
        # or if the existing net class matches the net class parameter (in
        # which case this is redundant).
        nets = self.nets  # Get all interconnected subnets.
        netclasses = set([getattr(n, "_netclass", None) for n in nets])
        netclasses.discard(None)
        if len(netclasses) == 0:
            pass
        elif len(netclasses) == 1:
            if netclass not in netclasses:
                active_logger.raise_(
                    ValueError,
                    "Can't assign net class {netclass.name} to net {self.name} that's already assigned net class {netclasses}".format(
                        **locals()
                    ),
                )
        else:
            active_logger.raise_(
                ValueError,
                "Too many netclasses assigned to net {self.name}".format(**locals()),
            )

        for n in nets:
            n._netclass = netclass

    @netclass.deleter
    def netclass(self):
        """
        Delete the net class from this net.
        
        This removes the net class from all connected net segments.
        """
        self.test_validity()
        nets = self.nets  # Get all interconnected subnets.
        for n in nets:
            try:
                del self._netclass
            except AttributeError:
                pass

    @property
    def drive(self):
        """
        Get, set or delete the drive strength of this net.
        
        The drive strength represents the electrical driving capability of the net.
        It is automatically set to the maximum drive value of any pin connected to
        the net, and cannot be set to a lower value than the current maximum.
        
        Returns:
            int: The drive strength value.
        """
        self.test_validity()
        nets = self.nets  # Get all interconnected subnets.
        max_drive = max(nets, key=lambda n: n._drive)._drive
        return max_drive

    @drive.setter
    def drive(self, drive):
        """
        Set the drive strength for this net.
        
        Args:
            drive (int): The new drive strength value. If less than the current
                         value, the current value will be maintained.
        """
        self.test_validity()
        nets = self.nets  # Get all interconnected subnets.
        max_drive = max(nets, key=lambda n: n._drive)._drive
        max_drive = max(drive, max_drive)
        for n in nets:
            n._drive = max_drive

    @drive.deleter
    def drive(self):
        """Delete the drive strength from this net."""
        self.test_validity()
        nets = self.nets  # Get all interconnected subnets.
        for n in nets:
            del n._drive

    @property
    def stub(self):
        """
        Get or set the stub status of this net.
        
        A stub net is not routed in schematic generation, but
        is represented as a short stub connected to the pin.
        
        Returns:
            bool: True if this is a stub net.
        """
        return self._stub

    @stub.setter
    def stub(self, val):
        """
        Set the stub status for this net.
        
        Args:
            val (bool): True to make this a stub net, False otherwise.
        """
        self._stub = val
        for pin in self.get_pins():
            pin.stub = val

    @property
    def valid(self):
        """
        Check if this net is still valid.
        
        Returns:
            bool: True if the net is valid, False if it has been invalidated.
        """
        return self._valid

    @valid.setter
    def valid(self, val):
        """
        Set the validity status of this net.
        
        Args:
            val (bool): True to mark the net as valid, False to invalidate it.
        """
        self.test_validity()
        self._valid = val

    def test_validity(self):
        """
        Test if the net is valid for use.
        
        Raises:
            ValueError: If the net is no longer valid.
        """
        if self.valid:
            return
        active_logger.raise_(
            ValueError,
            "Net {} is no longer valid. Do not use it!".format(self.name),
        )


@export_to_all
class NCNet(Net):
    """
    A specialized Net class for unconnected pins.
    
    NCNet is used for marking pins as explicitly not connected. These pins won't
    be flagged as floating during ERC, but no actual connections will be made
    to them in the physical circuit.
    
    Args:
        name (str, optional): Name of the no-connect net. If None, a unique name is generated.
        circuit (Circuit, optional): The circuit this no-connect net belongs to.
        *pins_nets_buses: One or more Pin, Net, or Bus objects to mark as not connected.
        
    Keyword Args:
        attribs: Various attributes to attach to the no-connect net.
    """

    def __init__(self, name=None, circuit=None, *pins_nets_buses, **attribs):
        from .pin import pin_drives

        super().__init__(name=name, circuit=circuit, *pins_nets_buses, **attribs)
        self._drive = pin_drives.NOCONNECT
        self.do_erc = False  # No need to do ERC on no-connect nets.

    def generate_netlist_net(self, tool=None):
        """
        Generate empty string as NO_CONNECT nets don't appear in netlists.
        
        Args:
            tool (str, optional): The netlist generation tool.
            
        Returns:
            str: Always returns an empty string.
        """
        return ""

    @property
    def drive(self):
        """
        Get the drive strength of this no-connect net.
        
        The drive strength is always NOCONNECT_DRIVE for NCNets and cannot be changed.
        
        Returns:
            int: The NOCONNECT drive strength value.
        """
        return self._drive
