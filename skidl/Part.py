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
Handles parts.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from builtins import super
from builtins import str
from builtins import int
from builtins import range
from builtins import dict
from builtins import zip
from future import standard_library
standard_library.install_aliases()

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

from copy import copy

# PySpice is not supported in Python 2, so need to make a dummy class to replicate
# a class from PySpice.
from .py_2_3 import *
if USING_PYTHON3:
    from PySpice.Unit.Unit import UnitValue
else:
    class UnitValue:
        pass

from .defines import *
from .utilities import *


class Part(object):
    """
    A class for storing a definition of a schematic part.

    Attributes:
        ref: String storing the reference of a part within a schematic (e.g., 'R5').
        value: String storing the part value (e.g., '3K3').
        footprint: String storing the PCB footprint associated with a part (e.g., SOIC-8).
        pins: List of Pin objects for this part.

    Args:
        lib: Either a SchLib object or a schematic part library file name.
        name: A string with name of the part to find in the library, or to assign to
            the part defined by the part definition.
        dest: String that indicates where the part is destined for (e.g., LIBRARY).
        tool: The format for the library file or part definition (e.g., KICAD).
        connections: A dictionary with part pin names/numbers as keys and the
            names of nets to which they will be connected as values. For example:
            { 'IN-':'a_in', 'IN+':'GND', '1':'AMPED_OUTPUT', '14':'VCC', '7':'GND' }
        part_defn: A list of strings that define the part (usually read from a
            schematic library file).
        circuit: The Circuit object this Part belongs to.

    Keyword Args:
        attribs: Name/value pairs for setting attributes for the part.
            For example, manf_num='LM4808MP-8' would create an attribute
            named 'manf_num' for the part and assign it the value 'LM4808MP-8'.

    Raises:
        * Exception if the part library and definition are both missing.
        * Exception if an unknown file format is requested.
    """

    def __init__(self,
                 lib=None,
                 name=None,
                 dest=NETLIST,
                 tool=None,
                 connections=None,
                 part_defn=None,
                 circuit=None,
                 **attribs):

        import skidl
        from .SchLib import SchLib
        from .defines import TEMPLATE, NETLIST, LIBRARY, SKIDL

        if tool is None:
            tool = skidl.get_default_tool()

        # Setup some part attributes that might be overwritten later on.
        self.do_erc = True  # Allow part to be included in ERC.
        self.unit = {
        }  # Dictionary for storing subunits of the part, if desired.
        self.pins = []  # Start with no pins, but a place to store them.
        self.name = name  # Assign initial part name. (Must come after circuit is assigned.)
        self.description = ''  # Make sure there is a description, even if empty.
        self._ref = ''  # Provide a member for holding a reference.
        self.ref_prefix = ''  # Provide a member for holding the part reference prefix.
        self.tool = tool  # Initial type of part (SKIDL, KICAD, etc.)
        self.circuit = None  # Part starts off unassociated with any circuit.

        # Create a Part from a library entry.
        if lib:
            # If the lib argument is a string, then create a library using the
            # string as the library file name.
            if isinstance(lib, basestring):
                try:
                    libname = lib
                    lib = SchLib(filename=libname, tool=tool)
                except Exception as e:
                    if skidl.QUERY_BACKUP_LIB:
                        logger.warning(
                            'Could not load KiCad schematic library "{}", falling back to backup library.'
                            .format(libname))
                        lib = skidl.load_backup_lib()
                        if not lib:
                            raise e
                    else:
                        raise e

            # Make a copy of the part from the library but don't add it to the netlist.
            part = lib[name].copy(1, TEMPLATE)

            # Overwrite self with the new part.
            self.__dict__.update(part.__dict__)

            # Make sure all the pins have a valid reference to this part.
            self.associate_pins()

            # Store the library name of this part.
            self.lib = getattr(lib, 'filename', None)

        # Otherwise, create a Part from a part definition. If the part is
        # destined for a library, then just get its name. If it's going into
        # a netlist, then parse the entire part definition.
        elif part_defn:
            self.part_defn = part_defn
            self.parse(just_get_name=(dest != NETLIST))

        # If the part is destined for a SKiDL library, then it will be defined
        # by the additional attribute values that are passed.
        elif tool == SKIDL and name:
            pass

        else:
            logger.error(
                "Can't make a part without a library & part name or a part definition."
            )
            raise Exception

        # If the part is going to be an element in a circuit, then add it to the
        # the circuit and make any indicated pin/net connections.
        if dest != LIBRARY:
            if dest == NETLIST:
                # If no Circuit object is given, then use the default Circuit that always exists.
                # Always set circuit first because naming the part requires a lookup
                # of existing names in the circuit.
                if not circuit:
                    circuit = default_circuit  # pylint: disable=undefined-variable
                circuit += self
            elif dest == TEMPLATE:
                # If this is just a part template, don't add the part to the circuit.
                # Just place the reference to the Circuit object in the template.
                if not circuit:
                    self.circuit = default_circuit  # pylint: disable=undefined-variable
                self.circuit = circuit

            # Add any net/pin connections to this part that were passed as arguments.
            if isinstance(connections, dict):
                for pin, net in connections.items():
                    net += self[pin]

            # Add any other passed-in attributes to the part.
            for k, v in attribs.items():
                setattr(self, k, v)

    def _find_min_max_pins(self):
        """ Return the minimum and maximum pin numbers for the part. """
        pin_nums = []
        try:
            for p in self.pins:
                try:
                    pin_nums.append(int(p.num))
                except ValueError:
                    pass
        except AttributeError:
            # This happens if the part has no pins.
            pass
        try:
            return min(pin_nums), max(pin_nums)
        except ValueError:
            # This happens if the part has no integer-labeled pins.
            return 0, 0

    def parse(self, just_get_name=False):
        """
        Create a part from its stored part definition.

        Args:
            just_get_name: When true, just get the name and aliases for the
                part. Leave the rest unparsed.
        """

        try:
            parse_func = getattr(self, '_parse_lib_part_{}'.format(self.tool))
            parse_func(just_get_name)
        except AttributeError:
            logger.error(
                "Can't create a part with an unknown ECAD tool file format: {}.".
                format(self.tool))
            raise Exception

    def associate_pins(self):
        """
        Make sure all the pins in a part have valid references to the part.
        """
        for p in self.pins:
            p.part = self

    def copy(self, num_copies=1, dest=NETLIST, circuit=None, **attribs):
        """
        Make zero or more copies of this part while maintaining all pin/net
        connections.

        Args:
            num_copies: Number of copies to make of this part.
            dest: Indicates where the copy is destined for (e.g., NETLIST).

        Keyword Args:
            attribs: Name/value pairs for setting attributes for the copy.

        Returns:
            A list of Part copies or a single Part if num_copies==1.

        Raises:
            Exception if the requested number of copies is a non-integer or negative.

        Notes:
            An instance of a part can be copied just by calling it like so::

                res = Part('device','R')    # Get a resistor.
                res_copy = res(value='1K')  # Copy the resistor and set resistance value.

            You can also use the multiplication operator to make copies::

                cap = Part('device', 'C')   # Get a capacitor
                caps = 10 * cap             # Make an array with 10 copies of it.
        """

        from .defines import NETLIST
        from .Circuit import Circuit

        num_copies = max(num_copies, find_num_copies(**attribs))

        # Check that a valid number of copies is requested.
        if not isinstance(num_copies, int):
            logger.error(
                "Can't make a non-integer number ({}) of copies of a part!".
                format(num_copies))
            raise Exception
        if num_copies < 0:
            logger.error(
                "Can't make a negative number ({}) of copies of a part!".
                format(num_copies))
            raise Exception

        # Now make copies of the part one-by-one.
        copies = []
        for i in range(num_copies):

            # Make a shallow copy of the part.
            cpy = copy(self)

            # The shallow copy will just put references to the pins of the
            # original into the copy, so create independent copies of the pins.
            cpy.pins = []
            for p in getattr(self, 'pins', None):
                cpy.pins.append(p.copy())

            # Make sure all the pins have a reference to this new part copy.
            cpy.associate_pins()

            # Clear the part reference of the copied part so a unique reference
            # can be assigned when the part is added to the circuit.
            # (This is not strictly necessary since the part reference will be
            # adjusted to be unique if needed during the addition process.)
            cpy._ref = None

            # Copied part starts off not being in any circuit.
            cpy.circuit = None

            # If copy is destined for a netlist, then add it to the Circuit its
            # source came from or else add it to the default Circuit object.
            if dest == NETLIST:
                # Place the copied part in the explicitly-stated circuit,
                # or else into the same circuit as the source part,
                # or else into the default circuit.
                if circuit:
                    circuit += cpy
                elif isinstance(self.circuit, Circuit):
                    self.circuit += cpy
                else:
                    builtins.default_circuit += cpy

            # Enter any new attributes.
            for k, v in attribs.items():
                if isinstance(v, (list, tuple)):
                    try:
                        v = v[i]
                    except IndexError:
                        logger.error(
                            "{} copies of part {} were requested, but too few elements in attribute {}!".
                            format(num_copies, self.name, k))
                        raise Exception
                setattr(cpy, k, v)

            # Add the part copy to the list of copies.
            copies.append(cpy)

        return list_or_scalar(copies)

    # Make copies with the multiplication operator or by calling the object.
    __mul__ = copy
    __rmul__ = copy
    __call__ = copy

    def add_pins(self, *pins):
        """Add one or more pins to a part."""
        for pin in flatten(pins):
            pin.part = self
            self.pins.append(pin)
        return self

    __iadd__ = add_pins

    def get_pins(self, *pin_ids, **criteria):
        """
        Return list of part pins selected by pin numbers or names.

        Args:
            pin_ids: A list of strings containing pin names, numbers,
                regular expressions, slices, lists or tuples. If empty,
                then it will select all pins.

        Keyword Args:
            criteria: Key/value pairs that specify attribute values the
                pins must have in order to be selected.

        Returns:
            A list of pins matching the given IDs and satisfying all the criteria,
            or just a single Pin object if only a single match was found.
            Or None if no match was found.

        Notes:
            Pins can be selected from a part by using brackets like so::

                atmega = Part('atmel', 'ATMEGA16U2')
                net = Net()
                atmega[1] += net  # Connects pin 1 of chip to the net.
                net += atmega['.*RESET.*']  # Connects reset pin to the net.
        """

        from .NetPinList import NetPinList
        from .Alias import Alias

        # If no pin identifiers were given, then use a wildcard that will
        # select all pins.
        if not pin_ids:
            pin_ids = ['.*']

        # Determine the minimum and maximum pin ids if they don't already exist.
        if 'min_pin' not in dir(self) or 'max_pin' not in dir(self):
            self.min_pin, self.max_pin = self._find_min_max_pins()

        # Go through the list of pin IDs one-by-one.
        pins = NetPinList()
        for p_id in expand_indices(self.min_pin, self.max_pin, *pin_ids):

            # Does pin ID (either integer or string) match a pin number...
            tmp_pins = filter_list(self.pins, num=re.escape(str(p_id)), **criteria)
            if tmp_pins:
                pins.extend(tmp_pins)
                continue

            # OK, assume it's not a pin number but a pin name. Look for an
            # exact match.
            name = '^' + re.escape(p_id) + '$'
            tmp_pins = filter_list(self.pins, name=name, **criteria)
            if tmp_pins:
                pins.extend(tmp_pins)
                continue

            # OK, now check pin aliases for an exact match.
            tmp_pins = filter_list(self.pins, alias=name, **criteria)
            if tmp_pins:
                pins.extend(tmp_pins)
                continue

            # OK, pin ID is not a pin number and doesn't exactly match a pin
            # name. Does it match a substring within a pin name or alias?
            loose_p_id = ''.join(['.*', p_id, '.*'])
            pins.extend(filter_list(self.pins, name=loose_p_id, **criteria))
            loose_pin_alias = Alias(loose_p_id, id(self))
            pins.extend(
                filter_list(self.pins, alias=loose_pin_alias, **criteria))

        return list_or_scalar(pins)

    # Get pins from a part using brackets, e.g. [1,5:9,'A[0-9]+'].
    __getitem__ = get_pins

    def __setitem__(self, ids, *pins_nets_buses):
        """
        You can't assign to the pins of parts. You must use the += operator.

        This method is a work-around that allows the use of the += for making
        connections to pins while prohibiting direct assignment. Python
        processes something like my_part['GND'] += gnd as follows::

            1. Part.__getitem__ is called with 'GND' as the index. This
               returns a single Pin or a NetPinList.
            2. The Pin.__iadd__ or NetPinList.__iadd__ method is passed
               the thing to connect to the pin (gnd in this case). This method
               makes the actual connection to the part pin or pins. Then it
               creates an iadd_flag attribute in the object it returns.
            3. Finally, Part.__setitem__ is called. If the iadd_flag attribute
               is true in the passed argument, then __setitem__ was entered
               as part of processing the += operator. If there is no
               iadd_flag attribute, then __setitem__ was entered as a result
               of using a direct assignment, which is not allowed.
        """

        # If the iadd_flag is set, then it's OK that we got
        # here and don't issue an error. Also, delete the flag.
        if getattr(pins_nets_buses[0], 'iadd_flag', False):
            del pins_nets_buses[0].iadd_flag
            return

        # No iadd_flag or it wasn't set. This means a direct assignment
        # was made to the pin, which is not allowed.
        logger.error("Can't assign to a part! Use the += operator.")
        raise Exception

    def is_connected(self):
        """
        Return T/F depending upon whether a part is connected in a netlist.

        If a part has pins but none of them are connected to nets, then
        this method will return False. Otherwise, it will return True even if
        the part has no pins (which can be the case for mechanical parts,
        silkscreen logos, or other non-electrical schematic elements).
        """

        # Assume parts without pins (like mech. holes) are always connected.
        if len(self.pins) == 0:
            return True

        # If any pin is found to be connected to a net, return True.
        for p in self.pins:
            if p.is_connected():
                return True

        # No net connections found, so return False.
        return False

    def is_movable(self):
        """
        Return T/F if the part can be moved from one circuit into another.

        This method returns true if:
            1) the part is not in a circuit, or
            2) the part has pins but none of them are connected to nets, or
            3) the part has no pins (which can be the case for mechanical parts,
               silkscreen logos, or other non-electrical schematic elements).
        """

        from .Circuit import Circuit

        return not isinstance(
            self.circuit,
            Circuit) or not self.is_connected() or not self.pins

    def set_pin_alias(self, alias, *pin_ids, **criteria):
        from .Alias import Alias

        pins = to_list(self.get_pins(*pin_ids, **criteria))
        if not pins:
            logger.error("Trying to alias a non-existent pin.")
        if len(pins) > 1:
            logger.error("Trying to give more than one pin the same alias.")
            raise Exception
        for pin in pins:
            pin.alias = Alias(alias, id(self))

    def make_unit(self, label, *pin_ids, **criteria):
        """
        Create a PartUnit from a set of pins in a Part object.

        Parts can be organized into smaller pieces called PartUnits. A PartUnit
        acts like a Part but contains only a subset of the pins of the Part.

        Args:
            label: The label used to identify the PartUnit.
            pin_ids: A list of strings containing pin names, numbers,
                regular expressions, slices, lists or tuples.

        Keyword Args:
            criteria: Key/value pairs that specify attribute values the
                pin must have in order to be selected.

        Returns:
            The PartUnit.
        """

        collisions = self.get_pins(label)
        if collisions:
            logger.warning(
                "Using a label ({}) for a unit of {} that matches one or more of it's pin names ({})!".
                format(label, self.erc_desc(), collisions))
        self.unit[label] = PartUnit(self, *pin_ids, **criteria)
        return self.unit[label]

    def _get_fields(self):
        """
        Return a list of component field names.
        """

        # Get all the component attributes and subtract all the ones that
        # should not appear under "fields" in the netlist or XML.
        fields = set(self.__dict__.keys())
        non_fields = set([
            'name', 'min_pin', 'max_pin', 'hierarchy', '_value', '_ref',
            'ref_prefix', 'unit', 'num_units', 'part_defn', 'definition',
            'fields', 'draw', 'lib', 'fplist', 'do_erc', 'aliases', 'tool',
            'pins', 'footprint', 'circuit'
        ])
        return list(fields - non_fields)

    def generate_netlist_component(self, tool=None):
        """
        Generate the part information for inclusion in a netlist.

        Args:
            tool: The format for the netlist file (e.g., KICAD).
        """

        import skidl

        if tool is None:
            tool = skidl.get_default_tool()

        try:
            gen_func = getattr(self, '_gen_netlist_comp_{}'.format(tool))
            return gen_func()
        except AttributeError:
            logger.error(
                "Can't generate netlist in an unknown ECAD tool format ({}).".
                format(tool))
            raise Exception

    def generate_xml_component(self, tool=None):
        """
        Generate the part information for inclusion in an XML file.

        Args:
            tool: The format for the XML file (e.g., KICAD).
        """

        import skidl

        if tool is None:
            tool = skidl.get_default_tool()

        try:
            gen_func = getattr(self, '_gen_xml_comp_{}'.format(tool))
            return gen_func()
        except AttributeError:
            logger.error(
                "Can't generate XML in an unknown ECAD tool format ({}).".
                format(tool))
            raise Exception

    def erc(self):
        """
        Do electrical rules check on a part in the schematic.
        """

        from .Pin import Pin

        # Don't check this part if the flag is not true.
        if not self.do_erc:
            return

        # Check each pin of the part.
        for p in self.pins:

            # Skip this pin if the flag is false.
            if not p.do_erc:
                continue

            # Error if a pin is unconnected but not of type NOCONNECT.
            if p.net is None:
                if p.func != Pin.NOCONNECT:
                    erc_logger.warning(
                        'Unconnected pin: {p}.'.format(p=p.erc_desc()))

            # Error if a no-connect pin is connected to a net.
            elif p.net.drive != Pin.NOCONNECT_DRIVE:
                if p.func == Pin.NOCONNECT:
                    erc_logger.warning(
                        'Incorrectly connected pin: {p} should not be connected to a net ({n}).'.
                        format(p=p.erc_desc(), n=p.net.name))

    def erc_desc(self):
        """Create description of part for ERC and other error reporting."""
        return "{p.name}/{p.ref}".format(p=self)

    def __str__(self):
        """Return a description of the pins on this part as a string."""
        return '\n {name} ({aliases}): {desc}\n    {pins}'.format(
            name=self.name, 
            aliases=', '.join(getattr(self, 'aliases','')), 
            desc=self.description, 
            pins='\n    '.join([p.__str__() for p in self.pins])
            )

    __repr__ = __str__

    def export(self):
        """Return a string to recreate a Part object."""
        keys = self._get_fields()
        keys.extend(('ref_prefix', 'num_units', 'fplist', 'do_erc', 'aliases',
                     'pin', 'footprint'))
        attribs = []
        attribs.append('{}={}'.format('name', repr(self.name)))
        attribs.append('dest=TEMPLATE')
        attribs.append('tool=SKIDL')
        for k in keys:
            v = getattr(self, k, None)
            if v:
                attribs.append('{}={}'.format(k, repr(v)))
        if self.pins:
            pin_strs = [p.export() for p in self.pins]
            attribs.append('pins=[{}]'.format(','.join(pin_strs)))

        # Return the string after removing all the non-ascii stuff (like ohm symbols).
        return 'Part({})'.format(','.join(attribs)).encode('ascii', 'ignore').decode('utf-8')

    @property
    def ref(self):
        """
        Get, set and delete the part reference.

        When setting the part reference, if another part with the same
        reference is found, the reference for this part is adjusted to make
        it unique.
        """
        return self._ref

    @ref.setter
    def ref(self, r):
        # Remove the existing reference so it doesn't cause a collision if the
        # object is renamed with its existing name.
        self._ref = None

        # Now name the object with the given reference or some variation
        # of it that doesn't collide with anything else in the list.
        self._ref = get_unique_name(self.circuit.parts, 'ref', self.ref_prefix,
                                    r)
        return

    @ref.deleter
    def ref(self):
        """Delete the part reference."""
        self._ref = None

    @property
    def value(self):
        """Get, set and delete the part value."""
        try:
            if isinstance(self._value, UnitValue):
                return self._value
            else:
                return str(self._value)
        except AttributeError:
            # If part has no value, return its part name as the value. This is
            # done in KiCad where a resistor value is set to 'R' if no
            # explicit value was set.
            return self.name

    @value.setter
    def value(self, value):
        """Set the part value."""
        self._value = value

    @value.deleter
    def value(self):
        """Delete the part value."""
        del self._value

    @property
    def foot(self):
        """Get, set and delete the part footprint."""
        return self._foot

    @foot.setter
    def foot(self, footprint):
        """Set the part footprint."""
        self._foot = str(footprint)

    @foot.deleter
    def foot(self):
        """Delete the part footprint."""
        del self._foot


##############################################################################


class SkidlPart(Part):
    """
    A class for storing a SKiDL definition of a schematic part. It's identical
    to its Part superclass except:
        *) The tool defaults to SKIDL.
        *) The destination defaults to TEMPLATE so that it's easier to start
           a part and then add pins to it without it being added to the netlist.
    """

    from .defines import SKIDL, TEMPLATE

    def __init__(self,
                 lib=None,
                 name=None,
                 dest=TEMPLATE,
                 tool=SKIDL,
                 connections=None,
                 **attribs):
        super(SkidlPart, self).__init__(lib, name, dest, tool, connections,
                                        attribs)


##############################################################################


class PartUnit(Part):
    """
    Create a PartUnit from a set of pins in a Part object.

    Parts can be organized into smaller pieces called PartUnits. A PartUnit
    acts like a Part but contains only a subset of the pins of the Part.

    Args:
        part: This is the parent Part whose pins the PartUnit is built from.
        pin_ids: A list of strings containing pin names, numbers,
            regular expressions, slices, lists or tuples.

    Keyword Args:
        criteria: Key/value pairs that specify attribute values the
            pin must have in order to be selected.

    Examples:
        This will return unit 1 from a part::

            lm358 = Part('linear','lm358')
            lm358a = PartUnit(lm358, unit=1)

        Or you can specify the pins directly::

            lm358a = PartUnit(lm358, 1, 2, 3)
    """

    def __init__(self, part, *pin_ids, **criteria):
        # Remember the part that this unit belongs to.
        self.parent = part

        # Give the PartUnit the same information as the Part it is generated
        # from so it can act the same way, just with fewer pins.
        for k, v in part.__dict__.items():
            self.__dict__[k] = v

        # Remove the pins copied from the parent and replace them with
        # pins selected from the parent.
        self.pins = []
        self._add_pins(*pin_ids, **criteria)

    def _add_pins(self, *pin_ids, **criteria):
        """
        Add selected pins from the parent to the part unit.
        """
        try:
            unique_pins = set(self.pins)
        except (AttributeError, TypeError):
            unique_pins = set()
        unique_pins |= set(to_list(self.parent.get_pins(*pin_ids, **criteria)))
        self.pins = list(unique_pins)
