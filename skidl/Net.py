# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2018 by XESS Corp.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Handles nets.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from builtins import super
from builtins import range
from future import standard_library
standard_library.install_aliases()

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

from copy import deepcopy, copy
import collections

from .defines import *
from .utilities import *


class Net(object):
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

    def __init__(self, name=None, circuit=None, *pins_nets_buses, **attribs):
        from .Pin import Pin

        self._valid = True  # Make net valid before doing anything else.
        self.do_erc = True
        self._drive = Pin.NO_DRIVE
        self.pins = []
        self._name = None
        self.circuit = None
        self.code = None  # This is the net number used in a KiCad netlist file.

        # Set the Circuit object for the net first because setting the net name
        # requires a lookup of existing names in the circuit.
        # Add the net to the passed-in circuit or to the default circuit.
        if circuit:
            circuit += self
        else:
            builtins.default_circuit += self

        # Set the net name *after* the net is assigned to a circuit so the
        # net can be assigned a unique name that doesn't conflict with existing
        # nets names in the circuit.
        if name:
            self.name = name

        # Attach whatever pins were given.
        self.connect(pins_nets_buses)
        del self.iadd_flag  # Remove the += flag inserted by connect().

        # Attach additional attributes to the net.
        for k, v in attribs.items():
            setattr(self, k, v)

    def _traverse(self):
        """Return all the nets and pins attached to this net, including itself."""

        from .Pin import PhantomPin

        self.test_validity()
        prev_nets = set([self])
        nets = set([self])
        prev_pins = set([])
        pins = set(self.pins)
        while pins != prev_pins:

            # Add the nets attached to any unvisited pins.
            for pin in pins - prev_pins:
                # No use visiting a pin that is not connected to a net.
                if pin.is_connected():
                    nets |= set(pin.get_nets())

            # Update the set of previously visited pins.
            prev_pins = copy(pins)

            # Add the pins attached to any unvisited nets.
            for net in nets - prev_nets:
                pins |= set(net.pins)

            # Update the set of previously visited nets.
            prev_nets = copy(nets)

        # Remove any phantom pins that may have existed for tieing nets together.
        pins = set([p for p in pins if not isinstance(p, PhantomPin)])

        traversal = collections.namedtuple('Traversal', ['nets', 'pins'])
        traversal.nets = list(nets)
        traversal.pins = list(pins)
        return traversal

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
            return pin_net_bus in self.get_nets()
        if isinstance(pin_net_bus, Pin):
            return pin_net_bus.is_attached(self)
        if isinstance(pin_net_bus, Bus):
            for net in pin_net_bus[:]:
                if self.is_attached(net):
                    return True
            return False
        logger.error("Nets can't be attached to {}!".format(type(pin_net_bus)))
        raise Exception

    def is_movable(self):
        """
        Return true if the net is movable to another circuit.

        A net is movable if it's not part of a Circuit or if there are no pins
        attached to it.
        """

        from .Circuit import Circuit

        return not isinstance(self.circuit, Circuit) or not self.pins

    def copy(self, num_copies=1, circuit=None, **attribs):
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

        num_copies = max(num_copies, find_num_copies(**attribs))

        # Check that a valid number of copies is requested.
        if not isinstance(num_copies, int):
            logger.error(
                "Can't make a non-integer number ({}) of copies of a net!".
                format(num_copies))
            raise Exception
        if num_copies < 0:
            logger.error(
                "Can't make a negative number ({}) of copies of a net!".format(
                    num_copies))
            raise Exception

        # Can't make a distinct copy of a net which already has pins on it
        # because what happens if a pin is connected to the copy? Then we have
        # to search for all the other copies to add the pin to those.
        # And what's the value of that?
        if self.pins:
            logger.error(
                "Can't make copies of a net that already has pins attached to it!"
            )
            raise Exception

        # Create a list of copies of this net.
        copies = []
        for i in range(num_copies):
            # Create a deep copy of the net.
            cpy = deepcopy(self)

            # Place the copy into either the passed-in circuit, the circuit of
            # the source net, or the default circuit.
            cpy.circuit = None
            if circuit:
                circuit += cpy
            elif self.circuit:
                self.circuit += cpy
            else:
                builtins.default_circuit += cpy

            # Add other attributes to the net copy.
            for k, v in attribs.items():
                if isinstance(v, (list, tuple)):
                    try:
                        v = v[i]
                    except IndexError:
                        logger.error(
                            "{} copies of net {} were requested, but too few elements in attribute {}!".
                            format(num_copies, self.name, k))
                        raise Exception
                setattr(cpy, k, v)

            # Place the copy into the list of copies.
            copies.append(cpy)

        return list_or_scalar(copies)

    # Make copies with the multiplication operator or by calling the object.
    __mul__ = copy
    __rmul__ = copy
    __call__ = copy

    def is_implicit(self, net_name=None):
        """Return true if the net name is implicit."""

        from .defines import NET_PREFIX

        self.test_validity()
        if net_name:
            return re.match(re.escape(NET_PREFIX), net_name)
        if self.name:
            return re.match(re.escape(NET_PREFIX), self.name)
        return True

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

        from .Pin import Pin, PhantomPin

        def merge(net):
            """
            Merge pins on net with self and then delete net.

            Args:
                net: The net to merge with self.
            """

            if isinstance(self, NCNet):
                logger.error("Can't merge with a no-connect net {}!".format(
                    self.name))
                raise Exception

            if isinstance(net, NCNet):
                logger.error("Can't merge with a no-connect net {}!".format(
                    net.name))
                raise Exception

            # No need to do anything if merging a net with itself.
            if self == net:
                return

            # If this net has pins, just attach the other net to one of them.
            if self.pins:
                self.pins[0].nets.append(net)
                net.pins.append(self.pins[0])
            # If the other net has pins, attach this net to a pin on the other net.
            elif net.pins:
                net.pins[0].nets.append(self)
                self.pins.append(net.pins[0])
            # If neither net has any pins, then attach a phantom pin to one net
            # and then connect the nets together.
            else:
                p = PhantomPin()
                connect_pin(p)
                self.pins[0].nets.append(net)
                net.pins.append(self.pins[0])

            # Update the drive of the merged nets.
            self.drive = net.drive
            net.drive = self.drive

        def connect_pin(pin):
            """Connect a pin to this net."""
            if pin not in self.pins:
                if not pin.is_connected():
                    # Remove the pin from the no-connect net if it is attached to it.
                    pin.disconnect()
                self.pins.append(pin)
                pin.nets.append(self)
            return

        self.test_validity()

        # Go through all the pins and/or nets and connect them to this net.
        for pn in expand_buses(flatten(pins_nets_buses)):
            if isinstance(pn, Net):
                if pn.circuit == self.circuit:
                    merge(pn)
                else:
                    logger.error(
                        "Can't attach nets in different circuits ({}, {})!".
                        format(pn.circuit.name, self.circuit.name))
                    raise Exception
            elif isinstance(pn, Pin):
                if not pn.part or pn.part.circuit == self.circuit:
                    if not pn.part:
                        logger.warning(
                            "Attaching non-part Pin {} to a Net {}.".format(
                                pn.name, self.name))
                    connect_pin(pn)
                else:
                    logger.error(
                        "Can't attach a part to a net in different circuits ({}, {})!".
                        format(pn.part.circuit.name, self.circuit.name))
                    raise Exception
            else:
                logger.error(
                    'Cannot attach non-Pin/non-Net {} to Net {}.'.format(
                        type(pn), self.name))
                raise Exception

        def select_name(nets):
            """Return the net with the best name among a list of nets."""

            if len(nets) == 0:
                return None  # No nets, return None.
            if len(nets) == 1:
                return nets[0]  # One net, return it.
            if len(nets) == 2:
                # Two nets, return the best of them.
                name0 = getattr(nets[0], 'name')
                name1 = getattr(nets[1], 'name')
                if not name1:
                    return nets[0]
                if not name0:
                    return nets[1]
                if self.is_implicit(name1):
                    return nets[0]
                if self.is_implicit(name0):
                    return nets[1]
                logger.warning(
                    'Merging two named nets ({name0} and {name1}) into {name0}.'.
                    format(**locals()))
                return nets[0]

            # More than two nets, so bisect the list into two smaller lists and
            # recursively find the best name from each list and then return the
            # best name of those two.
            mid_point = len(nets) // 2
            return select_name([
                select_name(nets[0:mid_point]),
                select_name(nets[mid_point:])
            ])

        # Assign the same name to all the nets that are connected to this net.
        nets = self._traverse().nets
        selected_name = getattr(select_name(self._traverse().nets), 'name')
        for net in nets:
            # Assign the name directly to each net. Using the name property
            # would cause the names to be changed so they were unique.
            net._name = selected_name  # pylint: disable=protected-access

        # Add the net to the global netlist. (It won't be added again
        # if it's already there.)
        self.circuit += self

        # Set the flag to indicate this result came from the += operator.
        self.iadd_flag = True

        return self

    # Use += to connect to nets.
    __iadd__ = connect

    def disconnect(self, pin):
        """Remove the pin from this net but not any other nets it's attached to."""
        try:
            self.pins.remove(pin)
        except ValueError:
            pass

    def generate_netlist_net(self, tool=None):
        """
        Generate the net information for inclusion in a netlist.

        Args:
            tool: The format for the netlist file (e.g., KICAD).
        """

        import skidl

        if tool is None:
            tool = skidl.get_default_tool()

        self.test_validity()

        # Don't add anything to the netlist if no pins are on this net.
        if not self.get_pins():
            return

        try:
            gen_func = getattr(self, '_gen_netlist_net_{}'.format(tool))
            return gen_func()
        except AttributeError:
            logger.error(
                "Can't generate netlist in an unknown ECAD tool format ({}).".
                format(tool))
            raise Exception

    def _gen_netlist_net_kicad(self):
        code = add_quotes(self.code)  # pylint: disable=unused-variable
        name = add_quotes(self.name)  # pylint: disable=unused-variable
        txt = '    (net (code {code}) (name {name})'.format(**locals())
        for p in sorted(self.get_pins(), key=str):
            part_ref = add_quotes(p.part.ref)  # pylint: disable=unused-variable
            pin_num = add_quotes(p.num)  # pylint: disable=unused-variable
            txt += '\n      (node (ref {part_ref}) (pin {pin_num}))'.format(
                **locals())
        txt += ')'
        return txt

    def generate_xml_net(self, tool=None):
        """
        Generate the net information for inclusion in an XML file.

        Args:
            tool: The format for the XML file (e.g., KICAD).
        """

        import skidl

        if tool is None:
            tool = skidl.get_default_tool()

        self.test_validity()

        # Don't add anything to the XML if no pins are on this net.
        if not self.get_pins():
            return

        try:
            gen_func = getattr(self, '_gen_xml_net_{}'.format(tool))
            return gen_func()
        except AttributeError:
            logger.error(
                "Can't generate XML in an unknown ECAD tool format ({}).".
                format(tool))
            raise Exception

    def _gen_xml_net_kicad(self):
        code = self.code  # pylint: disable=unused-variable
        name = self.name  # pylint: disable=unused-variable
        txt = '    <net code="{code}" name="{name}">'.format(**locals())
        for p in self.get_pins():
            part_ref = p.part.ref  # pylint: disable=unused-variable
            pin_num = p.num  # pylint: disable=unused-variable
            txt += '\n      <node ref="{part_ref}" pin="{pin_num}"/>'.format(
                **locals())
        txt += '\n    </net>'
        return txt

    def erc(self):
        """
        Do electrical rules check on a net in the schematic.
        """

        from .Pin import Pin
        from .Circuit import Circuit

        def pin_conflict_chk(pin1, pin2):
            """
            Check for conflict/contention between two pins on the same net.
            """

            if not pin1.do_erc or not pin2.do_erc:
                return

            erc_result = self.circuit.erc_pin_to_pin_chk(pin1, pin2)

            # Return if the pins are compatible.
            if erc_result == Circuit.OK:
                return

            # Otherwise, generate an error or warning message.
            msg = 'Pin conflict on net {n}: {p1} <==> {p2}'.format(
                n=pin1.net.name, p1=pin1.erc_desc(), p2=pin2.erc_desc())
            if erc_result == Circuit.WARNING:
                erc_logger.warning(msg)
            else:
                erc_logger.error(msg)

        def net_drive_chk():
            """
            Check the drive level on the net to see if it is within bounds.
            """

            # Find the maximum signal driver on this net.
            net_drive = self.drive  # Start with user-set drive level.
            pins = self.get_pins()
            for p in pins:
                net_drive = max(net_drive, Pin.pin_info[p.func]['drive'])

            if net_drive <= Pin.NO_DRIVE:
                erc_logger.warning(
                    'No drivers for net {n}'.format(n=self.name))
            for p in pins:
                if Pin.pin_info[p.func]['min_rcv'] > net_drive:
                    erc_logger.warning(
                        'Insufficient drive current on net {n} for pin {p}'.
                        format(n=self.name, p=p.erc_desc()))

        self.test_validity()

        # Skip ERC check on this net if flag is cleared.
        if not self.do_erc:
            return

        # Check the number of pins attached to the net.
        pins = self.get_pins()
        num_pins = len(pins)
        if num_pins == 0:
            erc_logger.warning(
                'No pins attached to net {n}.'.format(n=self.name))
        elif num_pins == 1:
            erc_logger.warning(
                'Only one pin ({p}) attached to net {n}.'.format(
                    p=pins[0].erc_desc(), n=self.name))
        else:
            for i in range(num_pins):
                for j in range(i + 1, num_pins):
                    pin_conflict_chk(pins[i], pins[j])

        # Check to see if the net has sufficient drive.
        net_drive_chk()

    def __str__(self):
        """Return a list of the pins on this net as a string."""
        self.test_validity()
        pins = self.get_pins()
        return self.name + ': ' + ', '.join(
            [p.__str__() for p in sorted(pins, key=str)])

    __repr__ = __str__

    def __len__(self):
        """Return the number of pins attached to this net."""
        self.test_validity()
        pins = self.get_pins()
        return len(pins)

    @property
    def name(self):
        """
        Get, set and delete the name of this net.

        When setting the net name, if another net with the same name
        is found, the name for this net is adjusted to make it unique.
        """
        return self._name

    @name.setter
    def name(self, name):
        from .defines import NET_PREFIX

        self.test_validity()
        # Remove the existing name so it doesn't cause a collision if the
        # object is renamed with its existing name.
        self._name = None

        # Now name the object with the given name or some variation
        # of it that doesn't collide with anything else in the list.
        self._name = get_unique_name(self.circuit.nets, 'name', NET_PREFIX,
                                     name)

    @name.deleter
    def name(self):
        self.test_validity()
        del self._name

    @property
    def drive(self):
        """
        Get, set and delete the drive strength of this net.

        The drive strength cannot be set to a value less than its current
        value. So as pins are added to a net, the drive strength reflects the
        maximum drive value of the pins currently on the net.
        """
        self.test_validity()
        return self._drive

    @drive.setter
    def drive(self, drive):
        self.test_validity()
        self._drive = max(drive, self._drive)

    @drive.deleter
    def drive(self):
        self.test_validity()
        del self._drive

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
        logger.error('Net {} is no longer valid. Do not use it!'.format(
            self.name))
        raise Exception


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
        from .Pin import Pin

        super(NCNet, self).__init__(
            name=name, circuit=circuit, *pins_nets_buses, **attribs)
        self._drive = Pin.NOCONNECT_DRIVE

    def generate_netlist_net(self, tool=None):
        """NO_CONNECT nets don't generate anything for netlists."""

        import skidl

        if tool is None:
            tool = skidl.get_default_tool()

        return ''

    def erc(self):
        """No need to check NO_CONNECT nets."""
        pass

    @property
    def drive(self):
        """
        Get the drive strength of this net.

        The drive strength is always NOCONNECT_DRIVE. It can't be changed.
        The drive strength cannot be deleted.
        """
        return self._drive
