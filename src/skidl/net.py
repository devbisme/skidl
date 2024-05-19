# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Handles nets.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import collections
import re
from builtins import range, super
from copy import copy, deepcopy

try:
    from future import standard_library

    standard_library.install_aliases()
except ImportError:
    pass

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
    Lists of connected pins are stored as nets using this class.

    Args:
        name: A string with the name of the net. If None or '', then
            a unique net name will be assigned.
        circuit: The Circuit object this net belongs to.
        *pins_nets_buses: One or more Pin, Net, or Bus objects or
            lists/tuples of them to be connected to this net.

    Keyword Args:
        attribs: A dictionary of attributes and values to attach to
            the Net object.
    """

    # Set the default ERC functions for all Net instances.
    erc_list = [dflt_net_erc]

    def __init__(self, name=None, circuit=None, *pins_nets_buses, **attribs):
        from .pin import Pin

        super().__init__()

        self._valid = True  # Make net valid before doing anything else.
        self.do_erc = True
        self._drive = Pin.drives.NONE
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
        """Any valid Net is True"""
        return True

    __nonzero__ = __bool__  # Python 2 compatibility.

    def __str__(self):
        """Return a list of the pins on this net as a string."""
        self.test_validity()
        pins = self.pins
        return (
            self.name + ": " + ", ".join([p.__str__() for p in sorted(pins, key=str)])
        )

    __repr__ = __str__  # TODO: This is a temporary fix. The __repr__ should be more informative.

    # Use += to connect to nets.
    def __iadd__(self, *pins_nets_buses):
        """Return the net after connecting other pins, nets, and buses to it."""
        return self.connect(*pins_nets_buses)

    def __and__(self, obj):
        """Attach a net and another part/pin/net in serial."""
        from .network import Network

        return Network(self) & obj

    def __rand__(self, obj):
        """Attach a net and another part/pin/net in serial."""
        from .network import Network

        return obj & Network(self)

    def __or__(self, obj):
        """Attach a net and another part/pin/net in parallel."""
        from .network import Network

        return Network(self) | obj

    def __ror__(self, obj):
        """Attach a net and another part/pin/net in parallel."""
        from .network import Network

        return obj | Network(self)

    def __len__(self):
        """Return the number of pins attached to this net."""
        self.test_validity()
        return len(self.pins)

    def __getitem__(self, *ids):
        """
        Return the net if the indices resolve to a single index of 0.

        Args:
            ids: A list of indices. These can be individual
                numbers, net names, nested lists, or slices.

        Returns:
            The net, otherwise None or raises an Exception.
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
        You can't assign to Nets. You must use the += operator.

        This method is a work-around that allows the use of the += for making
        connections to nets while prohibiting direct assignment. Python
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
        """
        # You can only iterate a Net one time.
        return (self[i] for i in [0])  # Return generator expr.

    def __call__(self, num_copies=None, circuit=None, **attribs):
        """Make one or more copies of this net."""
        return self.copy(num_copies=num_copies, circuit=circuit, **attribs)

    def __mul__(self, num_copies):
        """Use multiplication operator to make copies of a net."""
        if num_copies is None:
            num_copies = 0
        return self.copy(num_copies=num_copies)

    __rmul__ = __mul__

    @classmethod
    def get(cls, name, circuit=None):
        """Get the net with the given name from a circuit, or return None."""

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
        """Get the net with the given name from a circuit, or create it if not found."""

        circuit = attribs.get("circuit", default_circuit)
        return cls.get(name, circuit=circuit) or cls(name, *args, **attribs)

    def get_pins(self):
        """Return a list of pins attached to this net."""
        self.test_validity()
        return self._traverse().pins

    def get_nets(self):
        """Return a list of nets attached to this net, including this net."""
        self.test_validity()
        return self._traverse().nets

    def is_attached(self, pin_net_bus):
        """Return true if the pin, net or bus is attached to this one."""
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
        Return true if the net is movable to another circuit.

        A net is movable if it's not part of a Circuit or if there are no pins
        attached to it.
        """

        from .circuit import Circuit

        return not isinstance(self.circuit, Circuit) or not self._pins

    def is_implicit(self):
        """Return true if the net name is implicit."""

        from .bus import BUS_PREFIX

        self.test_validity()
        prefix_re = "({}|{})+".format(re.escape(NET_PREFIX), re.escape(BUS_PREFIX))
        return re.match(prefix_re, self.name)

    def copy(self, num_copies=None, circuit=None, **attribs):
        """
        Make zero or more copies of this net.

        Args:
            num_copies: Number of copies to make of this net.

        Keyword Args:
            attribs: Name/value pairs for setting attributes for the copy.

        Returns:
            A list of Net copies or a Net if num_copies==1.

        Raises:
            Exception if the requested number of copies is a non-integer or negative.

        Notes:
            An instance of a net can be copied just by calling it like so::

                n = Net('A')    # Create a net.
                n_copy = n()    # Copy the net.

            You can also use the multiplication operator to make copies::

                n = 10 * Net('A')  # Create an array of nets.
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
        for i in range(num_copies):

            # Create a new net to store the copy.
            cpy = Net(circuit=circuit)

            # Deep copy attributes from the source net to the copy.
            # Skip some attributes that would cause an infinite recursion exception.
            for k,v in self.__dict__.items():
                if k not in ['circuit', 'traversal']:
                    setattr(cpy, k, deepcopy(v))

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
        Return the net after connecting other pins, nets, and buses to it.

        Args:
            *pins_nets_buses: One or more Pin, Net, or Bus objects or
                lists/tuples of them to be connected to this net.

        Returns:
            The updated net with the new connections.

        Notes:
            Connections to nets can also be made using the += operator like so::

                atmega = Part('atmel', 'ATMEGA16U2')
                net = Net()
                net += atmega[1]  # Connects pin 1 of chip to the net.
        """

        from .pin import PhantomPin, Pin
        from .protonet import ProtoNet

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
            if isinstance(pn, ProtoNet):
                pn += self
            elif isinstance(pn, Net):
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
        """Remove the pin from this net but not any other nets it's attached to."""
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
        """For multi-segment nets, select a common name for all the segments."""

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
        """Create a network from a single net."""
        from .network import Network

        ntwk = Network()
        ntwk.append(self)
        return ntwk

    def generate_netlist_net(self, tool=None):
        """
        Generate the net information for inclusion in a netlist.

        Args:
            tool: The format for the netlist file (e.g., KICAD).
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
            tool: The format for the XML file (e.g., KICAD).
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
        """Return all the nets and pins attached to this net, including itself."""

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
        """Return width of a Net, which is always 1."""
        return 1

    @property
    def name(self):
        """
        Get, set and delete the name of this net.

        When setting the net name, if another net with the same name
        is found, the name for this net is adjusted to make it unique.
        """
        return super(Net, self).name

    @name.setter
    def name(self, name):

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
        self.test_validity()
        super(Net, self.__class__).name.fdel(self)

    @property
    def pins(self):
        return self.get_pins()

    @property
    def nets(self):
        return self.get_nets()

    @property
    def netclass(self):
        """
        Get, set and delete the net class assigned to this net.

        If not net class is set, then reading the net class returns None.

        You can't overwrite the net class of a net once it's set.
        You'll have to delete it and then set it to a new value.

        Also, assigning a net class of None will have no affect on the
        existing net class of a net.
        """
        self.test_validity()
        return getattr(self, "_netclass", None)

    @netclass.setter
    def netclass(self, netclass):
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
        Get, set and delete the drive strength of this net.

        The drive strength cannot be set to a value less than its current
        value. So as pins are added to a net, the drive strength reflects the
        maximum drive value of the pins currently on the net.
        """
        self.test_validity()
        nets = self.nets  # Get all interconnected subnets.
        max_drive = max(nets, key=lambda n: n._drive)._drive
        return max_drive

    @drive.setter
    def drive(self, drive):
        self.test_validity()
        nets = self.nets  # Get all interconnected subnets.
        max_drive = max(nets, key=lambda n: n._drive)._drive
        max_drive = max(drive, max_drive)
        for n in nets:
            n._drive = max_drive

    @drive.deleter
    def drive(self):
        self.test_validity()
        nets = self.nets  # Get all interconnected subnets.
        for n in nets:
            del n._drive

    @property
    def stub(self):
        return self._stub

    @stub.setter
    def stub(self, val):
        self._stub = val
        for pin in self.get_pins():
            pin.stub = val

    @property
    def valid(self):
        return self._valid

    @valid.setter
    def valid(self, val):
        self.test_validity()
        self._valid = val

    def test_validity(self):
        if self.valid:
            return
        active_logger.raise_(
            ValueError,
            "Net {} is no longer valid. Do not use it!".format(self.name),
        )


@export_to_all
class NCNet(Net):
    """
    Lists of unconnected pins are stored using this Net subclass.

    This is a netlist subclass used for storing lists of pins which are
    explicitly specified as not being connected. This means the ERC won't
    flag these pins as floating, but no net connections for these pins
    will be placed in the netlist so there will actually be no
    connections to these pins in the physical circuit.

    Args:
        name: A string with the name of the net. If None or '', then
            a unique net name will be assigned.
        *pins_nets_buses: One or more Pin, Net, or Bus objects or
            lists/tuples of them to be connected to this net.

    Keyword Args:
        attribs: A dictionary of attributes and values to attach to
            the object.
    """

    def __init__(self, name=None, circuit=None, *pins_nets_buses, **attribs):
        from .pin import Pin

        super().__init__(name=name, circuit=circuit, *pins_nets_buses, **attribs)
        self._drive = Pin.drives.NOCONNECT
        self.do_erc = False  # No need to do ERC on no-connect nets.

    def generate_netlist_net(self, tool=None):
        """NO_CONNECT nets don't generate anything for netlists."""
        return ""

    @property
    def drive(self):
        """
        Get the drive strength of this net.

        The drive strength is always NOCONNECT_DRIVE. It can't be changed.
        The drive strength cannot be deleted.
        """
        return self._drive
