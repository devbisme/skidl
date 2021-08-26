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

from __future__ import absolute_import, division, print_function, unicode_literals

import re
from builtins import dict, int, object, range, str, super, zip
from copy import copy
from random import randint

from future import standard_library

from .common import *
from .defines import *
from .erc import dflt_part_erc
from .logger import logger
from .skidlbaseobj import SkidlBaseObject
from .utilities import *

import time

standard_library.install_aliases()


try:
    from PySpice.Unit.Unit import UnitValue
except ImportError:
    # PySpice is not supported in Python 2, so need to make a dummy class
    # to replicate a class from PySpice.
    class UnitValue(object):
        pass


class PinNumberSearch(object):
    """
    A class for restricting part pin indexing to only pin numbers
    while ignoring pin names.
    """

    def __init__(self, part):
        # Store the part this object belongs to.
        self.part = part

    def get_pins(self, *pin_ids, **criteria):
        # Add criteria that restricts pin searching to only numbers.
        criteria["only_search_numbers"] = True

        # Now search the part for pin numbers matching the pin_ids.
        return self.part.get_pins(*pin_ids, **criteria)

    # Get pin numbers from a part using brackets, e.g. [1,5:9].
    __getitem__ = get_pins

    def __setitem__(self, ids, *pins_nets_buses):
        self.part.__setitem__(ids, *pins_nets_buses)


class PinNameSearch(object):
    """
    A class for restricting part pin indexing to only pin names
    while ignoring pin numbers.
    """

    def __init__(self, part):
        self.part = part

    def get_pins(self, *pin_ids, **criteria):
        # Add criteria that restricts pin searching to only names.
        criteria["only_search_names"] = True

        # Now search the part for pin names matching the pin_ids.
        return self.part.get_pins(*pin_ids, **criteria)

    # Get pin names from a part using brackets, e.g. ['A1, A2, A3'].
    __getitem__ = get_pins

    def __setitem__(self, ids, *pins_nets_buses):
        self.part.__setitem__(ids, *pins_nets_buses)


class Part(SkidlBaseObject):
    """
    A class for storing a definition of a schematic part.

    Args:
        lib: Either a SchLib object or a schematic part library file name.
        name: A string with name of the part to find in the library, or to assign to
            the part defined by the part definition.
        dest: String that indicates where the part is destined for (e.g., LIBRARY).
        tool: The format for the library file or part definition (e.g., KICAD).
        connections: A dictionary with part pin names/numbers as keys and the
            nets to which they will be connected as values. For example:
            { 'IN-':a_in, 'IN+':gnd, '1':AMPED_OUTPUT, '14':vcc, '7':gnd }
        part_defn: A list of strings that define the part (usually read from a
            schematic library file).
        circuit: The Circuit object this Part belongs to.
        ref_prefix: Prefix for part references such as 'U' or 'J'.
        ref: A specific part reference to be assigned.
        tag: A specific tag to tie the part to its footprint in the PCB.
        pin_splitters: String of characters that split long pin names into shorter aliases.
        tool_version: Select between KiCad V5 and V6.

    Keyword Args:
        kwargs: Name/value pairs for setting attributes for the part.
            For example, manf_num='LM4808MP-8' would create an attribute
            named 'manf_num' for the part and assign it the value 'LM4808MP-8'.

    Raises:
        * Exception if the part library and definition are both missing.
        * Exception if an unknown file format is requested.
    """

    # Set the default ERC functions for all Part instances.
    erc_list = [dflt_part_erc]

    def __init__(
        self,
        lib=None,
        name=None,
        dest=NETLIST,
        tool=None,
        connections=None,
        part_defn=None,
        circuit=None,
        ref_prefix='U',
        orientation = [1,0,0,-1],
        ref=None,
        tag=None,
        pin_splitters=None,
        tool_version=None,
        **kwargs
    ):

        import skidl
        from .schlib import SchLib

        super().__init__()

        if tool is None:
            tool = skidl.get_default_tool()

        # Setup some part attributes that might be overwritten later on.
        self.do_erc = True  # Allow part to be included in ERC.
        self.unit = {}  # Dictionary for storing subunits of the part, if desired.
        self.pins = []  # Start with no pins, but a place to store them.
        self.p = PinNumberSearch(self)  # Does pin search using only pin numbers.
        self.n = PinNameSearch(self)  # Does pin search using only pin names.
        self.name = name  # Assign initial part name.
        self.description = ""  # Make sure there is a description, even if empty.
        self._ref = ""  # Provide a member for holding a reference.
        self.ref_prefix = ref_prefix  # Store the part reference prefix.
        self.orientation = [1,0,0,-1]
        self.sch_bb=[0,0,0,0] # Set schematic location to x, y, height, width
        self.tool = tool  # Initial type of part (SKIDL, KICAD, etc.)
        self.circuit = None  # Part starts off unassociated with any circuit.
        self.match_pin_regex = False  # Don't allow regex matches of pin names.

        # Create a Part from a library entry.
        if lib:
            # If the lib argument is a string, then create a library using the
            # string as the library file name.
            if isinstance(lib, basestring):
                libname = lib
                try:
                    lib = SchLib(filename=libname, tool=tool)
                except FileNotFoundError as e:
                    if skidl.QUERY_BACKUP_LIB:
                        logger.warning(
                            'Could not load KiCad schematic library "{}", falling back to backup library.'.format(
                                libname
                            )
                        )
                        lib = skidl.load_backup_lib()
                        if not lib:
                            raise e
                    else:
                        raise e

            # Make a copy of the part from the library but don't add it to the netlist.
            part = lib[name].copy(dest=TEMPLATE)

            # Overwrite self with the new part.
            self.__dict__.update(part.__dict__)

            # Make sure all the pins have a valid reference to this part.
            self.associate_pins()

            # Copy part units so all the pin and part references stay valid.
            self.copy_units(part)

        # Otherwise, create a Part from a part definition. If the part is
        # destined for a library, then just get its name. If it's going into
        # a netlist, then parse the entire part definition.
        elif part_defn:
            self.part_defn = part_defn

            # If given, set the tool version before parsing the part definition.
            # At this time, this is done to support differences between KiCad V5 and V6.
            if tool_version:
                self.tool_version = tool_version

            self.parse(get_name_only=(dest != NETLIST))

        # If the part is destined for a SKiDL library, then it will be defined
        # by the additional attribute values that are passed.
        elif tool == SKIDL and name:
            pass

        else:
            log_and_raise(
                logger,
                ValueError,
                "Can't make a part without a library & part name or a part definition.",
            )

        # Split multi-part pin names into individual pin aliases.
        self.split_pin_names(pin_splitters)

        # Setup the tag for tieing the part to a footprint in a pcb editor.
        # Do this before adding the part to the circuit or an exception will occur
        # because the part can't give its hierarchical name to the circuit.
        self.tag = tag or str(randint(0, 2 ** 64 - 1))

        if dest != LIBRARY:
            if dest == NETLIST:
                # If the part is going to be an element in a circuit, then add it to the
                # the circuit and make any indicated pin/net connections.
                # If no Circuit object is given, then use the default Circuit that always exists.
                circuit = circuit or default_circuit
                circuit += self
            elif dest == TEMPLATE:
                # If this is just a part template, don't add the part to the circuit.
                self.circuit = None

            # Add any net/pin connections to this part that were passed as arguments.
            if isinstance(connections, dict):
                for pin, net in list(connections.items()):
                    net += self[pin]

        # Add any XSPICE I/O as pins. (This only happens with SPICE simulations.)
        self.add_xspice_io(kwargs.pop("io", []))

        # Set the part reference if one was explicitly provided.
        if ref:
            self.ref = ref

        # Add any other passed-in attributes to the part.
        for k, v in list(kwargs.items()):
            setattr(self, k, v)

        # If any pins were added, make sure they're associated with the part.
        self.associate_pins()
        self.sch_bb=[0,0,0,0]

    def add_xspice_io(self, io):
        """
        Add XSPICE I/O to the pins of a part.
        """
        from .pin import Pin, PinList

        if not io:
            return

        # Change a string into a list with a single string element.
        if isinstance(io, basestring):
            io = [io]

        # Join all the pin name arguments into a comma-separated string and then split them into a list.
        ios = re.split(INDEX_SEPARATOR, ",".join(io))

        # Add a pin to the part for each pin name.
        for i, arg in enumerate(ios):
            arg = arg.strip()  # Strip any spaces that may have been between pin names.

            # If [pin_name] or pin_name[], then add a PinList to the part. Don't use
            # part.add_pins() because it will flatten the PinList and add nothing since
            # the PinList is empty.
            if arg[0] + arg[-1] == "[]":
                self.pins.append(PinList(num=i, name=arg[1:-1], part=self))
            elif arg[-2:] == "[]":
                self.pins.append(PinList(num=i, name=arg[0:-2], part=self))
            else:
                # Add a simple, non-vector pin.
                self.add_pins(Pin(num=i, name=arg))

    @classmethod
    def get(cls, text, circuit=None):
        """
        Get the part with the given text from a circuit, or return None.

        Args:
            text: A text string that will be searched for in the list of
                parts.

        Keyword Args:
            circuit: The circuit whose parts will be searched. If set to None,
                then the parts in the default_circuit will be searched.

        Returns:
            A list of parts or a single part that match the text string with
            either their reference, name, alias, or their description.
        """

        from .alias import Alias

        if not circuit:
            circuit = builtins.default_circuit

        search_params = (
            ("ref", text, True),
            ("name", text, True),
            ("aliases", text, True),
            ("description", text, False),
        )

        parts = []
        for attr, name, do_str_match in search_params:
            parts.extend(
                filter_list(circuit.parts, do_str_match=do_str_match, **{attr: name})
            )

        return list_or_scalar(parts)

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

    def parse(self, get_name_only=False):
        """
        Create a part from its stored part definition.

        Args:
            get_name_only: When true, just get the name and aliases for the
                part. Leave the rest unparsed.
        """

        # Get the function to parse the part description.
        try:
            parse_func = getattr(self, "_parse_lib_part_{}".format(self.tool))
        except AttributeError:
            log_and_raise(
                logger,
                ValueError,
                "Can't create a part with an unknown ECAD tool file format: {}.".format(
                    self.tool
                ),
            )

        # Parse the part description.
        parse_func(get_name_only)

    def associate_pins(self):
        """
        Make sure all the pins in a part have valid references to the part.
        """
        for p in self.pins:
            p.part = self

    def copy(self, num_copies=None, dest=NETLIST, circuit=None, io=None, **attribs):
        """
        Make zero or more copies of this part while maintaining all pin/net
        connections.

        Args:
            num_copies: Number of copies to make of this part.
            dest: Indicates where the copy is destined for (e.g., NETLIST).
            circuit: The circuit this part should be added to.
            io: XSPICE I/O names.

        Keyword Args:
            attribs: Name/value pairs for setting attributes for the copy.

        Returns:
            A list of Part copies or a single Part if num_copies==1.

        Raises:
            Exception if the requested number of copies is a non-integer or negative.

        Notes:
            An instance of a part can be copied just by calling it like so::

                res = Part("Device",'R')    # Get a resistor.
                res_copy = res(value='1K')  # Copy the resistor and set resistance value.

            You can also use the multiplication operator to make copies::

                cap = Part("Device", 'C')   # Get a capacitor
                caps = 10 * cap             # Make an array with 10 copies of it.
        """

        from .defines import NETLIST
        from .circuit import Circuit
        from .pin import Pin

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
            log_and_raise(
                logger,
                ValueError,
                "Can't make a non-integer number ({}) of copies of a part!".format(
                    num_copies
                ),
            )
        if num_copies < 0:
            log_and_raise(
                logger,
                ValueError,
                "Can't make a negative number ({}) of copies of a part!".format(
                    num_copies
                ),
            )

        # Now make copies of the part one-by-one.
        copies = []
        for i in range(num_copies):

            # Make a shallow copy of the part.
            cpy = copy(self)

            # Remove any existing Pin and PartUnit attributes so new ones
            # can be made in the copy without generating warning messages.
            rmv_attrs = [
                k
                for k, v in list(cpy.__dict__.items())
                if isinstance(v, (Pin, PartUnit))
            ]
            for attr in rmv_attrs:
                delattr(cpy, attr)

            # The shallow copy will just put references to the pins of the
            # original into the copy, so create independent copies of the pins.
            cpy.pins = []
            cpy += [p.copy() for p in self.pins]  # Add pin and its attribute.
            cpy.pin_aliases_to_attributes()  # Add pin aliases as part attributes.

            # If the part copy is intended as a template, then disconnect its pins
            # from any circuit nets.
            if dest == TEMPLATE:
                for p in cpy.pins:
                    p.disconnect()

            # Make sure all the pins have a reference to this new part copy.
            cpy.associate_pins()

            # Make new objects for searching the copy's pin numbers and names.
            cpy.p = PinNumberSearch(cpy)
            cpy.n = PinNameSearch(cpy)

            # Copy the part fields from the original.
            cpy.fields = {k: v for k, v in self.fields.items()}

            # Copy part units from the original to the copy.
            cpy.copy_units(self)

            # Clear the part reference of the copied part so a unique reference
            # can be assigned when the part is added to the circuit.
            # (This is not strictly necessary since the part reference will be
            # adjusted to be unique if needed during the addition process.)
            cpy._ref = None

            # Copied part starts off not being in any circuit.
            cpy.circuit = None

            # Reset the tag to a random generated one.  We
            # are careful to do this after setting the circuit to
            # None so we don't corrupt the hierarchical name index
            # maintained in circuit.
            del cpy.tag

            # If copy is destined for a netlist, then add it to the Circuit its
            # source came from or else add it to the default Circuit object.
            if dest == NETLIST:
                # Place the copied part in the explicitly-stated circuit,
                # or the same circuit as the original,
                # or else into the default circuit.
                circuit = circuit or self.circuit or builtins.default_circuit
                circuit += cpy

            # Add any XSPICE I/O as pins to the part.
            cpy.add_xspice_io(io)

            # Enter any new attributes.
            for k, v in list(attribs.items()):
                if isinstance(v, (list, tuple)):
                    try:
                        v = v[i]
                    except IndexError:
                        log_and_raise(
                            logger,
                            ValueError,
                            "{} copies of part {} were requested, but too few elements in attribute {}!".format(
                                num_copies, self.name, k
                            ),
                        )
                setattr(cpy, k, v)

            # Add the part copy to the list of copies.
            copies.append(cpy)

        # Return a list of the copies made or just a single copy.
        if return_list:
            return copies
        return copies[0]

    def validate(self):
        """ Check that pins and units reference the correct part that owns them. """
        for pin in self.pins:
            assert pin.part == self
        for unit in self.unit.values():
            unit.validate()

    # Make copies with the multiplication operator or by calling the object.
    __call__ = copy

    def __mul__(self, num_copies):
        if num_copies is None:
            num_copies = 0
        return self.copy(num_copies=num_copies)

    __rmul__ = __mul__

    def copy_units(self, src):
        """ Make copies of the units from the source part. """
        self.unit = {}  # Remove references to any existing units.
        for label, unit in src.unit.items():
            # Get the pin numbers from the unit in the source part.
            pin_nums = [p.num for p in unit.pins]

            # Make a unit in the part copy with the same pin numbers.
            self.make_unit(label, *pin_nums)
            self.unit[label].num = unit.num

    def add_pins(self, *pins):
        """Add one or more pins to a part."""
        for pin in flatten(pins):
            pin.part = self
            self.pins.append(pin)
            # Create attributes so pin can be accessed by name or number such
            # as part.ENBL or part.p5.
            add_unique_attr(self, pin.name, pin)
            add_unique_attr(self, "p" + str(pin.num), pin)
        return self

    __iadd__ = add_pins

    def rmv_pins(self, *pin_ids):
        """Remove one or more pins from a part."""
        pins = self.pins
        for i, pin in enumerate(pins):
            if pin.num in pin_ids or pin.name in pin_ids:
                del pins[i]

    def swap_pins(self, pin_id1, pin_id2):
        """Swap pin name/number between two pins of a part."""
        pins = self.pins
        i1, i2 = None, None
        for i, pin in enumerate(pins):
            pin_num_name = (pin.num, pin.name)
            if pin_id1 in pin_num_name:
                i1 = i
            elif pin_id2 in pin_num_name:
                i2 = i
            if i1 and i2:
                break
        if i1 and i2:
            pins[i1].num, pins[i1].name, pins[i2].num, pins[i2].name = pins[i2].num, pins[i2].name, pins[i1].num, pins[i1].name

    def rename_pin(self, pin_id, new_pin_name):
        """Assign a new name to a pin of a part."""
        for pin in self.pins:
            if pin_id in (pin.num, pin.name):
                pin.name = new_pin_name
                return

    def renumber_pin(self, pin_id, new_pin_num):
        "Assign a new number to a pin of a part."""
        for pin in self.pins:
            if pin_id in (pin.num, pin.name):
                pin.num = new_pin_num
                return

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
                net += atmega['RESET']  # Connects reset pin to the net.
        """

        from .netpinlist import NetPinList
        from .alias import Alias

        # Extract restrictions on searching for only pin names or numbers.
        only_search_numbers = criteria.pop("only_search_numbers", False)
        only_search_names = criteria.pop("only_search_names", False)

        # Extract permission to search for regex matches in pin names/aliases.
        match_regex = criteria.pop("match_regex", False) or self.match_pin_regex

        # If no pin identifiers were given, then use a wildcard that will
        # select all pins.
        if not pin_ids:
            pin_ids = [".*"]
            match_regex = True

        # Determine the minimum and maximum pin ids if they don't already exist.
        if "min_pin" not in dir(self) or "max_pin" not in dir(self):
            self.min_pin, self.max_pin = self._find_min_max_pins()

        # Go through the list of pin IDs one-by-one.
        pins = NetPinList()
        for p_id in expand_indices(self.min_pin, self.max_pin, match_regex, *pin_ids):

            # If only names are being searched, the search of pin numbers is skipped.
            if not only_search_names:
                # Does pin ID (either integer or string) match a pin number...
                tmp_pins = filter_list(
                    self.pins, num=str(p_id), do_str_match=True, **criteria
                )
                if tmp_pins:
                    pins.extend(tmp_pins)
                    continue

            # if only numbers are being searched, then search of pin names is skipped.
            if not only_search_numbers:
                # OK, assume it's not a pin number but a pin name or alias.
                # Look for an exact match.

                # Check pin aliases for an exact match.
                tmp_pins = filter_list(
                    self.pins, aliases=p_id, do_str_match=True, **criteria
                )
                if tmp_pins:
                    pins.extend(tmp_pins)
                    continue

                # Check pin names for an exact match.
                tmp_pins = filter_list(
                    self.pins, name=p_id, do_str_match=True, **criteria
                )
                if tmp_pins:
                    pins.extend(tmp_pins)
                    continue

                # Skip regex matching if not enabled.
                if not match_regex:
                    continue

                # OK, pin ID is not a pin number and doesn't exactly match a pin
                # name or alias. Does it match as a regex?
                p_id_re = p_id

                # Check pin aliases for a regex match.
                tmp_pins = filter_list(self.pins, aliases=Alias(p_id_re), **criteria)
                if tmp_pins:
                    pins.extend(tmp_pins)
                    continue

                # Check the pin names for a regex match.
                tmp_pins = filter_list(self.pins, name=p_id_re, **criteria)
                if tmp_pins:
                    pins.extend(tmp_pins)
                    continue

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
        if getattr(pins_nets_buses[0], "iadd_flag", False):
            del pins_nets_buses[0].iadd_flag
            return

        # No iadd_flag or it wasn't set. This means a direct assignment
        # was made to the pin, which is not allowed.
        log_and_raise(logger, TypeError, "Can't assign to a part! Use the += operator.")

    def __iter__(self):
        """
        Return an iterator for stepping thru individual pins of the part.
        """
        return (p for p in self.pins)  # Return generator expr.

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

    def attached_to(self, nets=None):
        """Return True if any part pin is connected to a net in the list."""
        if not nets:
            return False

        for pin in self.get_pins():
            for net in pin.get_nets():
                if net in nets:
                    return True
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
        from .circuit import Circuit

        return (
            not isinstance(self.circuit, Circuit)
            or not self.is_connected()
            or not self.pins
        )

    def set_pin_alias(self, alias, *pin_ids, **criteria):
        """
        Set the alias for a part pin.

        Args:
            alias: The alias for the pin.
            pin_ids: A list of strings containing pin names, numbers,
                regular expressions, slices, lists or tuples.

        Keyword Args:
            criteria: Key/value pairs that specify attribute values the
                pin must have in order to be selected.

        Returns:
            Nothing.
        """

        from .alias import Alias
        from .pin import Pin

        pin = self.get_pins(*pin_ids, **criteria)
        if isinstance(pin, Pin):
            # Alias the single pin that was found.
            pin.aliases += alias
            # Add the name of the aliased pin as an attribute to the part,
            # so it will act just like a pin for making connections.
            add_unique_attr(self, alias, pin)
        else:
            # Error: either 0 or multiple pins were found.
            log_and_raise(logger, ValueError, "Cannot set alias for {}".format(pin_ids))

    def pin_aliases_to_attributes(self):
        """Make each pin alias into an attribute of the part."""

        for pin in self:
            for alias in pin.aliases:
                add_unique_attr(self, alias, pin)

    def split_pin_names(self, delimiters):
        """Use chars in delimiters to split pin names and add as aliases to each pin."""

        if delimiters:
            for pin in self:
                # Split pin name and add subnames as aliases to the pin.
                pin.split_name(delimiters)

            # Add the pin aliases as attributes to the part.
            self.pin_aliases_to_attributes()

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

        # Warn if the unit label collides with any of the part's pin names.
        collisions = self.get_pins("^" + label + "$")  # Look for exact match.
        if collisions:
            logger.warning(
                "Using a label ({}) for a unit of {} that matches one or more of it's pin names ({})!".format(
                    label, self.erc_desc(), collisions
                )
            )

        # Create the part unit.
        self.unit[label] = PartUnit(self, label, *pin_ids, **criteria)
        add_unique_attr(self, label, self.unit[label])

        return self.unit[label]

    def create_network(self):
        """Create a network from the pins of a part."""
        from .network import Network

        ntwk = Network(self[:])  # An error will occur if part has more than 2 pins.
        return ntwk

    def __and__(self, obj):
        """Attach a part and another part/pin/net in serial."""
        from .network import Network

        return Network(self) & obj

    def __rand__(self, obj):
        """Attach a part and another part/pin/net in serial."""
        from .network import Network

        return obj & Network(self)

    def __or__(self, obj):
        """Attach a part and another part/pin/net in parallel."""
        from .network import Network

        return Network(self) | obj

    def __ror__(self, obj):
        """Attach a part and another part/pin/net in parallel."""
        from .network import Network

        return obj | Network(self)

    def _get_fields(self):
        """
        Return a list of component field names.
        """

        from .pin import Pin

        # Get all the component attributes and subtract all the ones that
        # should not appear under "fields" in the netlist or XML.
        # Also, skip all the Pin and PartUnit attributes.
        fields = set(
            [
                k
                for k, v in list(self.__dict__.items())
                if not isinstance(v, (Pin, PartUnit))
            ]
        )
        non_fields = set(
            [
                "name",
                "min_pin",
                "max_pin",
                "hierarchy",
                "_tag",
                "_value",
                "_ref",
                "ref_prefix",
                "unit",
                "num_units",
                "part_defn",
                "definition",
                "fields",
                "draw",
                "lib",
                "fplist",
                "do_erc",
                "aliases",
                "tool",
                "pins",
                "footprint",
                "circuit",
                "skidl_trace",
                "search_text",
                "filename",
                "p",
                "n",
            ]
        )
        return list(fields - non_fields)

    def _value_to_str(self):
        """Return value of part as a string."""
        value = getattr(self, "value", getattr(self, "name", self.ref_prefix))
        return str(value)

    def generate_netlist_component(self, tool=None):
        """
        Generate the part information for inclusion in a netlist.

        Args:
            tool: The format for the netlist file (e.g., KICAD).
        """

        import skidl

        if tool is None:
            tool = skidl.get_default_tool()

        # Create part value as a string so including it in netlist isn't a problem.
        self.value_str = self._value_to_str()

        try:
            gen_func = getattr(self, "_gen_netlist_comp_{}".format(tool))
        except AttributeError:
            log_and_raise(
                logger,
                ValueError,
                "Can't generate netlist in an unknown ECAD tool format ({}).".format(
                    tool
                ),
            )

        return gen_func()

    def generate_bounding_box(self):
        for p in self.pins:
            len_label = 0
            if len(p.label) > 0:
                len_label = int((len(p.label) +1) * 50)
            if self.sch_bb[2] < (abs(p.x) + len_label):
                self.sch_bb[2] = abs(p.x) + len_label
            if self.sch_bb[3] < (abs(p.y) + len_label):
                self.sch_bb[3] = abs(p.y) + len_label
        
        if self.sch_bb[2] < 100:
            self.sch_bb[2] = 100
        if self.sch_bb[3] < 100:
            self.sch_bb[3] = 100

    def generate_xml_component(self, tool=None):
        """
        Generate the part information for inclusion in an XML file.

        Args:
            tool: The format for the XML file (e.g., KICAD).
        """

        import skidl

        if tool is None:
            tool = skidl.get_default_tool()

        # Create part value as a string so including it in XML isn't a problem.
        self.value_str = self._value_to_str()

        try:
            gen_func = getattr(self, "_gen_xml_comp_{}".format(tool))
        except AttributeError:
            log_and_raise(
                logger,
                ValueError,
                "Can't generate XML in an unknown ECAD tool format ({}).".format(tool),
            )

        return gen_func()

    
    # Move the part by dx/dy, then check to see if it's colliding with 
    #   any other part.  If it is colliding then move the part move towards the 
    #   direction of the pin it was moving towards
    def move_part(self, dx, dy, _parts_list):
        # print(self.ref + " x: " + str(self.sch_bb[0]) + " Y: " + str(self.sch_bb[1]))
        # Determine if the part moved left or right
        move_dir = 'L'
        if dx > 0:
            move_dir = 'R'
            # dy = -dy # TODO: figure out why we need to reverse the y sign when moving right...
        # Move the part
        self.sch_bb[0] += dx
        self.sch_bb[1] -= dy

        # Range through parts in the subcircuit and look for overlaps
        # If we are overlapping then nudge the part 50mil left/right and rerun this function
        for pt in _parts_list:
            if pt.ref == self.ref:
                continue
            x1min = self.sch_bb[0] - self.sch_bb[2]
            x1max = self.sch_bb[0] + self.sch_bb[2]
            
            x2min = pt.sch_bb[0] - pt.sch_bb[2]
            x2max = pt.sch_bb[0] + pt.sch_bb[2]
            
            y1min = self.sch_bb[1] - self.sch_bb[3]
            y1max = self.sch_bb[1] + self.sch_bb[3]
            
            y2min = pt.sch_bb[1] - pt.sch_bb[3]
            y2max = pt.sch_bb[1] + pt.sch_bb[3]
            # Logic to tell whether parts collide
            # Note that the movement direction is opposite of what's intuitive ('R' = move left, 'U' = -50)
            # https://stackoverflow.com/questions/20925818/algorithm-to-check-if-two-boxes-overlap
            if (x1min <= x2max) and (x2min <= x1max) and (y1min <= y2max) and (y2min <= y1max):
                if move_dir == 'R':
                    self.move_part(200, 0, _parts_list)
                else:
                    self.move_part(-200, 0, _parts_list)


    def generate_svg_component(self, symtx="", tool=None, net_stubs=None):
        """
        Generate the SVG for displaying a part in an SVG schematic.
        """

        import skidl

        if tool is None:
            tool = skidl.get_default_tool()

        try:
            gen_func = getattr(self, "_gen_svg_comp_{}".format(tool))
        except AttributeError:
            log_and_raise(
                logger,
                ValueError,
                "Can't generate SVG for a component in an unknown ECAD tool format({}).".format(
                    tool
                ),
            )

        return gen_func(symtx=symtx, net_stubs=net_stubs)

    def generate_pinboxes(self, tool=None):
        """
        Generate the pinboxes for arranging parts in a schematic.
        """

        import skidl

        if tool is None:
            tool = skidl.get_default_tool()

        try:
            gen_func = getattr(self, "_gen_pinboxes_{}".format(tool))
        except AttributeError:
            log_and_raise(
                logger,
                ValueError,
                "Can't generate pinboxes for a component in an unknown ECAD tool format({}).".format(
                    tool
                ),
            )

        return gen_func()
    
    # Generate eeschema code for part from SKiDL part
    # self: SKiDL part
    # c[x,y]: coordinated to place the part
    # https://en.wikibooks.org/wiki/Kicad/file_formats#Schematic_Files_Format
    def gen_part_eeschema(self, c=[0,0]):

        time_hex = hex(int(time.time()))[2:]

        out=["$Comp\n"]
        out.append("L {}:{} {}\n".format(self.lib.filename, self.name, self.ref))
        out.append("U 1 1 {}\n".format(time_hex))    
        out.append("P {} {}\n".format(str(c[0]), str(c[1])))
        # Add part symbols. For now we are only adding the designator
        n_F0 = 1
        for i in range(len(self.draw)):
            if re.search("^DrawF0", str(self.draw[i])):
                n_F0 = i
                break
        out.append('F 0 "{}" {} {} {} {} {} {} {}\n'.format(
                                        self.ref,
                                        self.draw[n_F0].orientation,
                                        str(self.draw[n_F0].x + c[0]),
                                        str(self.draw[n_F0].y + c[1]),
                                        self.draw[n_F0].size,
                                        "000",
                                        self.draw[n_F0].halign,
                                        self.draw[n_F0].valign
        ))
        out.append("   1   {} {}\n".format(str(c[0]), str(c[1])))
        out.append("   {}   {}  {}  {}\n".format(self.orientation[0], self.orientation[1], self.orientation[2], self.orientation[3], ))
        out.append("$EndComp\n") 
        return ("\n" + "".join(out))



    def erc_desc(self):
        """Create description of part for ERC and other error reporting."""
        return "{p.name}/{p.ref}".format(p=self)

    def __str__(self):
        """Return a description of the pins on this part as a string."""
        return "\n {name} ({aliases}): {desc}\n    {pins}".format(
            name=self.name,
            aliases=", ".join(getattr(self, "aliases", "")),
            desc=self.description,
            pins="\n    ".join([p.__str__() for p in self.pins]),
        )

    __repr__ = __str__

    def export(self):
        """Return a string to recreate a Part object."""
        keys = self._get_fields()
        keys.extend(
            (
                "ref_prefix",
                "num_units",
                "fplist",
                "do_erc",
                "aliases",
                "pin",
                "footprint",
            )
        )
        attribs = []
        attribs.append("'{}':{}".format("name", repr(self.name)))
        attribs.append("'dest':TEMPLATE")
        attribs.append("'tool':SKIDL")
        for k in keys:
            v = getattr(self, k, None)
            attribs.append("'{}':{}".format(k, repr(v)))
        if self.pins:
            pin_strs = [p.export() for p in self.pins]
            attribs.append("'pins':[{}]".format(",".join(pin_strs)))

        # Return the string after removing all the non-ascii stuff (like ohm symbols).
        return "Part(**{{ {} }})".format(", ".join(attribs))

    @property
    def hierarchical_name(self):
        return getattr(self, "hierarchy", "") + "." + self._tag

    @property
    def tag(self):
        """Return the part's tag."""
        return self._tag

    @tag.setter
    def tag(self, value):
        """Set the part's tag."""
        # Remove the part's old hierarchical name from the index.
        if self.circuit is not None:
            self.circuit.rmv_hierarchical_name(self.hierarchical_name)

        # Update the part's tag.
        str_tag = str(value)
        if re.compile(r"[^a-zA-Z0-9\-_]").search(str_tag):
            log_and_raise(
                logger,
                ValueError,
                "Can't set part tag to {} it contains disallowed characters.".format(
                    str_tag
                ),
            )
        self._tag = str_tag

        # Add the udpated hierarchical name back to the index.
        if self.circuit is not None:
            self.circuit.add_hierarchical_name(self.hierarchical_name)

    @tag.deleter
    def tag(self):
        """Delete the part tag."""
        # Part's can't have a None tag, so set a new random tag.
        self.tag = randint(0, 2 ** 64 - 1)

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
        self._ref = get_unique_name(self.circuit.parts, "ref", self.ref_prefix, r)
        return

    @ref.deleter
    def ref(self):
        """Delete the part reference."""
        self._ref = None

    @property
    def value(self):
        """Get, set and delete the part value."""
        try:
            return self._value
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

    @property
    def match_pin_regex(self):
        """Get, set and delete the enable/disable of pin regular-expression matching."""
        return self._match_pin_regex

    @match_pin_regex.setter
    def match_pin_regex(self, flag):
        """Set the regex matching flag."""
        self._match_pin_regex = flag

        # Also set flag for units of the part.
        for unit in self.unit.values():
            unit._match_pin_regex = flag

    @match_pin_regex.deleter
    def match_pin_regex(self):
        """Delete the regex matching flag."""
        del self._match_pin_regex

    def __bool__(self):
        """Any valid Part is True"""
        return True

    __nonzero__ = __bool__  # Python 2 compatibility.

    def __len__(self):
        """Return the number of pins in this part."""
        return len(self.pins)


##############################################################################


class SkidlPart(Part):
    """
    A class for storing a SKiDL definition of a schematic part. It's identical
    to its Part superclass except:

    + The tool defaults to SKIDL.
    + The destination defaults to TEMPLATE so that it's easier to start
        a part and then add pins to it without it being added to the netlist.
    """

    from .defines import SKIDL, TEMPLATE

    def __init__(
        self,
        lib=None,
        name=None,
        dest=TEMPLATE,
        tool=SKIDL,
        connections=None,
        **attribs
    ):
        super().__init__(lib, name, dest, tool, connections, attribs)


##############################################################################


class PartUnit(Part):
    """
    Create a PartUnit from a set of pins in a Part object.

    Parts can be organized into smaller pieces called PartUnits. A PartUnit
    acts like a Part but contains only a subset of the pins of the Part.

    Args:
        part: This is the parent Part whose pins the PartUnit is built from.
        pin_ids: A list of strings containing pin names, numbers,
            regular expressions, slices, lists or tuples. If empty, it
            will match *every* pin of the part.

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

    def __init__(self, parent, label, *pin_ids, **criteria):

        # Don't use super() for this.
        SkidlBaseObject.__init__(self)

        # Remember the part that this unit belongs to.
        self.parent = parent

        # Store the part unit label.
        self.label = label

        # Store the part unit number if it's given.
        try:
            self.num = criteria["unit"]
        except KeyError:
            pass

        # Give the PartUnit the same information as the Part it is generated
        # from so it can act the same way, just with fewer pins.
        for k, v in list(parent.__dict__.items()):
            self.__dict__[k] = v

        # Don't associate any units from the parent with this unit itself.
        self.unit = {}

        # Remove the pins copied from the parent and replace them with
        # pins selected from the parent.
        self.pins = []
        self.add_pins_from_parent(*pin_ids, **criteria)

    def add_pins_from_parent(self, *pin_ids, **criteria):
        """
        Add selected pins from the parent to the part unit.
        """

        # Get new pins selected from the parent.
        new_pins = to_list(self.parent.get_pins(*pin_ids, **criteria))

        # Remove None if that's gotten into the list.
        try:
            new_pins.remove(None)
        except ValueError:
            pass

        # Add attributes for accessing the new pins.
        for pin in new_pins:
            add_unique_attr(self, "p" + str(pin.num), pin)
            add_unique_attr(self, pin.name, pin)

        # Add new pins to existing pins of the unit, removing duplicates.
        self.pins = list(set(self.pins + new_pins))

    def validate(self):
        """ Check that unit pins point to the parent part. """
        for pin in self.pins:
            assert id(pin.part) == id(self.parent)

    @property
    def ref(self):
        return ".".join((self.parent.ref, self.label))
