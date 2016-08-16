# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2016 by XESS Corp.
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

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import sys
import os
import os.path
import re
import logging
import shlex
import inspect
from copy import deepcopy, copy
from pprint import pprint
import time
import pdb
from builtins import str
from builtins import zip
from builtins import range
from builtins import object

from .__init__ import __version__

# Supported ECAD tools.
# KICAD, EAGLE = ['kicad', 'eagle']
KICAD, = ['kicad',]

# Places where parts can be stored.
#   NETLIST: The part will become part of a circuit netlist.
#   LIBRARY: The part will be placed in the part list for a library.
#   TEMPLATE: The part will be used as a template to be copied from.
NETLIST, LIBRARY, TEMPLATE = ['NETLIST', 'LIBRARY', 'TEMPLATE']

# Prefixes for anonymous nets and buses.
NET_PREFIX = 'N$'
BUS_PREFIX = 'B$'

# Separator for strings containing multiple indices.
INDEX_SEPARATOR = ','


def _scriptinfo():
    """
    Returns a dictionary with information about the running top level Python
    script:
    ---------------------------------------------------------------------------
    dir:    directory containing script or compiled executable
    name:   name of script or executable
    source: name of source code file
    ---------------------------------------------------------------------------
    "name" and "source" are identical if and only if running interpreted code.
    When running code compiled by py2exe or cx_freeze, "source" contains
    the name of the originating Python script.
    If compiled by PyInstaller, "source" contains no meaningful information.

    Downloaded from:
    http://code.activestate.com/recipes/579018-python-determine-name-and-directory-of-the-top-lev/
    """

    #---------------------------------------------------------------------------
    # scan through call stack for caller information
    #---------------------------------------------------------------------------
    for teil in inspect.stack():
        # skip system calls
        if teil[1].startswith("<"):
            continue
        if teil[1].upper().startswith(sys.exec_prefix.upper()):
            continue
        trc = teil[1]

    # trc contains highest level calling script name
    # check if we have been compiled
    if getattr(sys, 'frozen', False):
        scriptdir, scriptname = os.path.split(sys.executable)
        return {"dir": scriptdir, "name": scriptname, "source": trc}

    # from here on, we are in the interpreted case
    scriptdir, trc = os.path.split(trc)
    # if trc did not contain directory information,
    # the current working directory is what we need
    if not scriptdir:
        scriptdir = os.getcwd()

    scr_dict = {"name": trc, "source": trc, "dir": scriptdir}
    return scr_dict


def _get_script_name():
    """Return the name of the top-level script."""
    return os.path.splitext(_scriptinfo()['name'])[0]


class _CountCalls(object):
    """
    Decorator for counting the number of times a function is called.

    This is used for counting errors and warnings passed to logging functions,
    making it easy to track if and how many errors/warnings were issued.
    """

    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)

# Set up logging.
logger = logging.getLogger('skidl')

# Errors always appear on the terminal.
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.WARNING)
handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(handler)

# Errors and warnings are stored in a log file with the top-level script's name.
scr_name = _get_script_name()
handler = logging.StreamHandler(open(scr_name + '.log', 'w'))
handler.setLevel(logging.WARNING)
handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(handler)

logger.setLevel(logging.INFO)
logger.error = _CountCalls(logger.error)
logger.warning = _CountCalls(logger.warning)


def _to_list(x):
    """
    Return x if it is already a list, or return a list if x is a scalar.
    """
    if isinstance(x, (list, tuple)):
        return x  # Already a list, so just return it.
    return [x]  # Wasn't a list, so make it into one.


def _list_or_scalar(lst):
    """
    Return a list if passed a multi-element list, otherwise return a single scalar.

    Args:
        lst: Either a list or a scalar.

    Returns:
        * A list if passed a multi-element list.
        * The list element if passed a single-element list.
        * None if passed an empty list.
        * A scalar if passed a scalar.
    """
    if isinstance(lst, (list, tuple)):
        if len(lst) > 1:
            return lst  # Multi-element list, so return it unchanged.
        if len(lst) == 1:
            return lst[0]  # Single-element list, so return the only element.
        return None  # Empty list, so return None.
    return lst  # Must have been a scalar, so return that.


def _flatten(nested_list):
    """
    Return a flattened list of items from a nested list.
    """
    lst = []
    for item in nested_list:
        if isinstance(item, (list, tuple)):
            lst.extend(_flatten(item))
        else:
            lst.append(item)
    return lst


def _expand_buses(pins_nets_buses):
    """
    Take list of pins, nets, and buses and return a list of only pins and nets.
    """
    pins_nets = []
    for pnb in pins_nets_buses:
        if isinstance(pnb, Bus):
            pins_nets.extend(pnb._get_nets())
        else:
            pins_nets.append(pnb)
    return pins_nets


def _get_unique_name(lst, attrib, prefix, initial=None):
    """
    Return a name that doesn't collide with another in a list.

    This subroutine is used to generate unique part references (e.g., "R12")
    or unique net names (e.g., "N$5").

    Args:
        lst: The list of objects containing names.
        attrib: The attribute in each object containing the name.
        prefix: The prefix attached to each name.
        initial: The initial setting of the name (can be None or empty string).

    Returns:
        A string containing the unique name.
    """

    # If the initial name is None, then create a name based on the prefix
    # and the smallest unused number that's available for that prefix.
    if not initial:

        # Get list entries with the prefix followed by a number, e.g.: C55
        filter_dict = {attrib: re.escape(prefix) + r'\d+'}
        sub_list = _filter(lst, **filter_dict)

        # If entries were found, then find the smallest available number.
        if sub_list:
            # Get the list of names.
            names = [getattr(item, attrib) for item in sub_list]
            # Remove the prefix from each name, leaving only the numbers.
            l = len(prefix)
            nums = set([int(n[l:]) for n in names])
            stop = max(nums) + 1
            # Generate a list of the unused numbers in the range [1,stop]
            # and select the minimum value.
            n = min(set(range(1, stop + 1)) - nums)

        # If no entries were found, start counting from 1.
        else:
            n = 1

        # The initial name is the prefix plus the number.
        initial = prefix + str(n)

    # If the initial name is just a number, then prepend the prefix to it.
    elif isinstance(initial, int):
        initial = prefix + str(initial)

    # Now determine if there are any items in the list with the same name.
    filter_dict = {attrib: re.escape(initial)}
    sub_list = _filter(lst, **filter_dict)

    # If the name is unique, then return it.
    if not sub_list:
        return initial

    # Otherwise, determine how many copies of the name are in the list and
    # append a number to make this name unique.
    filter_dict = {attrib: re.escape(initial) + r'_\d+'}
    n = len(_filter(lst, **filter_dict))
    initial = initial + '_' + str(n + 1)

    # Recursively call this routine using the newly-generated name to
    # make sure it's unique. Eventually, a unique name will be returned.
    return _get_unique_name(lst, attrib, prefix, initial)


def _filter(lst, **criteria):
    """
    Return a list of objects whose attributes match a set of criteria.

    Return a list of objects extracted from a list whose attributes match a
    set of criteria. The match is done using regular expressions.
    Example: _filter(pins, name='io[0-9]+', direction='bidir') will
    return all the bidirectional pins of the component that have pin names
    starting with 'io' followed by a number (e.g., 'IO45').

    If an attribute of the lst object is a list or tuple, each entry in the
    list/tuple will be checked for a match. Only one entry needs to match to
    consider the entire attribute a match. This feature is useful when
    searching for objects that contain a list of aliases, such as Part objects.

    Args:
        lst: The list from which objects will be extracted.

    Keywords Args:
        criteria: Keyword-argument pairs. The keyword specifies the attribute
            name while the argument contains the desired value of the attribute.
            Regardless of what type the argument is, it is always compared as if
            it was a string. The argument can also be a regular expression that
            must match the entire string created from the attribute of the list
            object.

    Returns:
        A list of objects whose attributes match *all* the criteria.
    """

    # Place any matching objects from the list in here.
    extract = []

    for item in lst:
        # Compare an item's attributes to each of the criteria.
        # Break out of the criteria loop and don't add the item to the extract
        # list if *any* of the item's attributes *does not* match.
        for k, v in criteria.items():

            try:
                attr_val = getattr(item, k)
            except AttributeError:
                # If the attribute doesn't exist, then that's a non-match.
                break

            if isinstance(v, (int, type(''))):
                # Check integer or string attributes.

                if isinstance(attr_val, (list, tuple)):
                    # If the attribute value from the item is a list or tuple,
                    # loop through the list of attribute values. If at least one
                    # value matches the current criterium, then break from the
                    # criteria loop and extract this item.
                    for val in attr_val:
                        if re.fullmatch(str(v), str(val), flags=re.IGNORECASE):
                            # One of the list of values matched, so break from this
                            # loop and do not execute the break in the
                            # loop's else clause.
                            break
                    else:
                        # If we got here, then none of the values in the attribute
                        # list matched the current criterium. Therefore, break out
                        # of the criteria loop and don't add this list item to
                        # the extract list.
                        break
                else:
                    # If the attribute value from the item in the list is a scalar,
                    # see if the value matches the current criterium. If it doesn't,
                    # then break from the criteria loop and don't extract this item.
                    if not re.fullmatch(
                            str(v), str(attr_val),
                            flags=re.IGNORECASE):
                        break

            else:
                # Check non-integer, non-string attributes.
                if isinstance(attr_val, (list, tuple)):
                    if v not in attr_val:
                        break
                elif v != attr_val:
                    break

        else:
            # If we get here, then all the item attributes matched and the
            # for criteria loop didn't break, so add this item to the
            # extract list.
            extract.append(item)

    return extract


def _expand_indices(slice_min, slice_max, *indices):
    """
    Expand a list of indices into a list of integers and strings.

    This function takes the indices used to select pins of parts and 
    lines of buses and returns a flat list of numbers and strings.
    String and integer indices are put in the list unchanged, but
    slices are expanded into a list of integers before entering the
    final list.

    Args:
        slice_min: The minimum possible index.
        slice_max: The maximum possible index (used for slice indices).
        indices: A list of indices made up of numbers, slices, text strings.
            The list can also be nested.

    Returns:
        A linear list of all the indices made up only of numbers and strings.
    """

    def expand_slice(slc):
        """Expand slice notation."""

        # Get bounds for slice.
        start, stop, step = slc.indices(slice_max)
        start = min(max(start, slice_min), slice_max)
        stop = min(max(stop, slice_min), slice_max)

        # Do this if it's a downward slice (e.g., [7:0]).
        if start > stop:
            if slc.start and slc.start > slice_max:
                logger.error('Index out of range ({} > {})!'.format(slc.start,
                                                                    slice_max))
                raise Exception
            # Count down from start to stop.
            stop = stop - step
            step = -step

        # Do this if it's a normal (i.e., upward) slice (e.g., [0:7]).
        else:
            if slc.stop and slc.stop > slice_max:
                logger.error('Index out of range ({} > {})!'.format(slc.stop,
                                                                    slice_max))
                raise Exception
            # Count up from start to stop
            stop += step

        # Create the sequence of indices.
        return range(start, stop, step)

    # Expand each index and add it to the list.
    ids = []
    for indx in _flatten(indices):
        if isinstance(indx, slice):
            ids.extend(expand_slice(indx))
        elif isinstance(indx, int):
            ids.append(indx)
        elif isinstance(indx, type('')):
            # String might contain multiple indices with a separator.
            for id in indx.split(INDEX_SEPARATOR):
                ids.append(id.strip())
        else:
            logger.error('Unknown type in index: {}'.format(type(indx)))
            raise Exception

    # Return the completely expanded list of indices.
    return ids


def _find_num_copies(**attribs):
    """
    Return the number of copies to make from the length of attribute values.

    Keyword Args:
        attribs: Dict of Keyword/Value pairs for setting object attributes.
            If the value is a scalar, then the number of copies is one.
            If the value is a list/tuple, the number of copies is the
            length of the list/tuple.

    Returns:
        The length of the longest value in the dict of attributes.

    Raises:
        Exception if there are two or more list/tuple values with different
        lengths that are greater than 1. (All attribute values must be scalars
        or lists/tuples of the same length.)
    """
    num_copies = set()
    for k, v in attribs.items():
        if isinstance(v, (list, tuple)):
            num_copies.add(len(v))
        else:
            num_copies.add(1)

    num_copies = list(num_copies)
    if len(num_copies) > 2:
        logger.error("Mismatched lengths of attributes: {}!".format(
            num_copies))
        raise Exception
    elif len(num_copies) > 1 and min(num_copies) > 1:
        logger.error("Mismatched lengths of attributes: {}!".format(
            num_copies))
        raise Exception

    try:
        return max(num_copies)
    except ValueError:
        return 0  # If the list if empty.

##############################################################################


class _SchLib(object):
    """
    A class for storing parts from a schematic component library file.

    Attributes:
        filename: The name of the file from which the parts were read.
        parts: The list of parts (composed of Part objects).

    Args:
        filename: The name of the library file.
        tool: The format of the library file (e.g., KICAD).

    Keyword Args:
        attribs: Key/value pairs of attributes to add to the library.
    """

    # Keep a dict of filenames and their associated SchLib object
    # for fast loading of libraries.
    _cache = {}

    def __init__(self, filename=None, tool=KICAD, **attribs):
        """
        Load the parts from a library file.
        """

        self.filename = filename
        self.parts = []

        # Load this SchLib with an existing SchLib object if the file name
        # matches one in the cache.
        if filename in self._cache:
            self.__dict__.update(self._cache[filename].__dict__)

        # Otherwise, load from a schematic library file.
        else:
            try:
                # Use the tool name to find the function for loading the library.
                func_name = '_load_sch_lib_{}'.format(tool)
                load_func = self.__class__.__dict__[func_name]
                load_func(self, filename)
                # Cache a reference to the library.
                self._cache[filename] = self
            except KeyError:
                # OK, that didn't work so well...
                logger.error('Unsupported ECAD tool library: {}'.format(tool))
                raise Exception

        # Attach additional attributes to the library.
        for k, v in attribs.items():
            setattr(self, k, v)

    def _load_sch_lib_kicad(self, filename=None):
        """
        Load the parts from a KiCad schematic library file.

        Args:
            filename: The name of the KiCad schematic library file.
        """

        # Try to open the file. Add a .lib extension if needed. If the file
        # doesn't open, then try looking in the KiCad library directory.
        try:
            _, ext = os.path.splitext(filename)
            if ext.lower() != '.lib':
                filename += '.lib'
            f = open(filename)
        except FileNotFoundError:
            filename = os.path.join(os.environ['KISYSMOD'], '..', 'library',
                                    filename)
            try:
                f = open(filename)
            except FileNotFoundError:
                logger.error("Can't open file: {}\n".format(filename))
                return
        except TypeError:
            logger.error("Can't open file: {}\n".format(filename))
            return

        # Check the file header to make sure it's a KiCad library.
        header = []
        header = [f.readline()]
        if header and 'EESchema-LIBRARY' not in header[0]:
            logger.error(
                'The file {} is not a KiCad Schematic Library File\n'.format(
                    filename))
            return

        # Read the definition of each part line-by-line and then create
        # a Part object that gets stored in the part list.
        part_defn = []
        for line in f.readlines():

            # Skip over comments.
            if line.startswith('#'):
                pass

            # Look for the start of a part definition.
            elif line.startswith('DEF'):
                # Initialize the part definition with the first line.
                # This will also signal that succeeding lines should be added.
                part_defn = [line]

            # If gathering the part definition has begun, then continue adding lines.
            elif part_defn:
                part_defn.append(line)

                # If the current line ends this part definition, then create
                # the Part object and add it to the part list. Be sure to
                # indicate that the Part object is being added to a library
                # and not to a schematic netlist.
                if line.startswith('ENDDEF'):
                    self.parts.append(Part(part_defn=part_defn,
                                           tool=KICAD,
                                           dest=LIBRARY))

                    # Clear the part definition in preparation for the next one.
                    part_defn = []

    def get_parts(self, **criteria):
        """
        Return parts from a library that match *all* the given criteria.

        Keyword Args:
            criteria: One or more keyword-argument pairs. The keyword specifies
                the attribute name while the argument contains the desired value
                of the attribute.

        Returns:
            A single Part or a list of Parts that match all the criteria.        """
        return _list_or_scalar(_filter(self.parts, **criteria))

    def get_part_by_name(self, name, allow_multiples=False):
        """
        Return a Part with the given name or alias from the part list.

        Args:
            name: The part name or alias to search for in the library.
            allow_multiples: If true, return a list of parts matching the name.
                If false, return only the first matching part and issue
                a warning if there were more than one.

        Returns:
            A single Part or a list of Parts that match all the criteria.
        """

        # First check to see if there is a part or parts with a matching name.
        parts = self.get_parts(name=name)

        # No part with that name, so check for an alias that matches.
        if not parts:
            parts = self.get_parts(aliases=name)

            # No part with that alias either, so signal an error.
            if not parts:
                logger.error('Unable to find part {} in library {}.'.format(
                    name, self.filename))
                raise Exception

        # Multiple parts with that name or alias exists, so return the list
        # of parts or just the first part on the list.
        if isinstance(parts, (list, tuple)):

            # Return the entire list if multiples are allowed.
            if allow_multiples:
                parts = [p.parse() for p in parts]

            # Just return the first part from the list if multiples are not
            # allowed and issue a warning.
            else:
                logger.warning(
                    'Found multiple parts matching {}. Selecting {}.'.format(
                        name, parts[0].name))
                parts = parts[0]
                parts._parse()

        # Only a single matching part was found, so return that.
        else:
            parts._parse()

        # Return the library part or parts that were found.
        return parts

    """Get part by name or alias using []'s."""
    __getitem__ = get_part_by_name

    def __str__(self):
        """Return a list of the part names in this library as a string."""
        return '\n'.join([p.name for p in self.parts])

    __repr__ = __str__

    def __len__(self):
        """
        Return number of parts in library.
        """
        return len(self.parts)

##############################################################################


class Pin(object):
    """
    A class for storing data about pins for a part.

    Args:
        attribs: Key/value pairs of attributes to add to the library.

    Attributes:
        nets: The electrical nets this pin is connected to (can be >1).
        part: Link to the Part object this pin belongs to.
        do_erc: When false, the pin is not checked for ERC violations.
    """

    # Various types of pins.
    INPUT, OUTPUT, BIDIR, TRISTATE, PASSIVE, UNSPEC, PWRIN,\
    PWROUT, OPENCOLL, OPENEMIT, NOCONNECT = range(11)

    # Various drive levels a pin can output:
    #   NOCONNECT_DRIVE: NC pin drive.
    #   NO_DRIVE: No drive capability (like an input pin).
    #   PASSIVE_DRIVE: Small drive capability, such as a pullup.
    #   ONESIDE_DRIVE: Can pull high (open-emitter) or low (open-collector).
    #   TRISTATE_DRIVE: Can pull high/low and be in high-impedance state.
    #   PUSHPULL_DRIVE: Can actively drive high or low.
    #   POWER_DRIVE: A power supply or ground line.
    NOCONNECT_DRIVE, NO_DRIVE, PASSIVE_DRIVE, ONESIDE_DRIVE,\
    TRISTATE_DRIVE, PUSHPULL_DRIVE, POWER_DRIVE = range(7)

    # Information about the various types of pins:
    #   function: A string describing the pin's function.
    #   drive: The drive capability of the pin.
    #   rcv_min: The minimum amount of drive the pin must receive to function.
    #   rcv_max: The maximum amount of drive the pin can receive and still function.
    pin_info = {
        INPUT: {'function': 'INPUT',
                'drive': NO_DRIVE,
                'max_rcv': POWER_DRIVE,
                'min_rcv': PASSIVE_DRIVE, },
        OUTPUT: {'function': 'OUTPUT',
                 'drive': PUSHPULL_DRIVE,
                 'max_rcv': PASSIVE_DRIVE,
                 'min_rcv': NO_DRIVE, },
        BIDIR: {'function': 'BIDIRECTIONAL',
                'drive': TRISTATE_DRIVE,
                'max_rcv': POWER_DRIVE,
                'min_rcv': NO_DRIVE, },
        TRISTATE: {'function': 'TRISTATE',
                   'drive': TRISTATE_DRIVE,
                   'max_rcv': TRISTATE_DRIVE,
                   'min_rcv': NO_DRIVE, },
        PASSIVE: {'function': 'PASSIVE',
                  'drive': PASSIVE_DRIVE,
                  'max_rcv': POWER_DRIVE,
                  'min_rcv': NO_DRIVE, },
        UNSPEC: {'function': 'UNSPECIFIED',
                 'drive': NO_DRIVE,
                 'max_rcv': POWER_DRIVE,
                 'min_rcv': NO_DRIVE, },
        PWRIN: {'function': 'POWER-IN',
                'drive': NO_DRIVE,
                'max_rcv': POWER_DRIVE,
                'min_rcv': POWER_DRIVE, },
        PWROUT: {'function': 'POWER-OUT',
                 'drive': POWER_DRIVE,
                 'max_rcv': PASSIVE_DRIVE,
                 'min_rcv': NO_DRIVE, },
        OPENCOLL: {'function': 'OPEN-COLLECTOR',
                   'drive': ONESIDE_DRIVE,
                   'max_rcv': TRISTATE_DRIVE,
                   'min_rcv': NO_DRIVE, },
        OPENEMIT: {'function': 'OPEN-EMITTER',
                   'drive': ONESIDE_DRIVE,
                   'max_rcv': TRISTATE_DRIVE,
                   'min_rcv': NO_DRIVE, },
        NOCONNECT: {'function': 'NO-CONNECT',
                    'drive': NOCONNECT_DRIVE,
                    'max_rcv': NOCONNECT_DRIVE,
                    'min_rcv': NOCONNECT_DRIVE, },
    }

    def __init__(self, **attribs):
        self.nets = []
        self.part = None
        self.do_erc = True

        # Attach additional attributes to the pin.
        for k, v in attribs.items():
            setattr(self, k, v)

    def copy(self, num_copies=1, **attribs):
        """
        Return copy or list of copies of a pin including any net connection.

        Args:
            num_copies: Number of copies to make of pin.

        Keyword Args:
            attribs: Name/value pairs for setting attributes for the pin.

        Notes:
            An instance of a pin can be copied just by calling it like so::

                p = Pin()     # Create a pin.
                p_copy = p()  # This is a copy of the pin.
        """

        # Check that a valid number of copies is requested.
        if not isinstance(num_copies, int):
            logger.error(
                "Can't make a non-integer number ({}) of copies of a pin!".format(
                    num_copies))
            raise Exception
        if num_copies < 0:
            logger.error(
                "Can't make a negative number ({}) of copies of a pin!".format(
                    num_copies))
            raise Exception

        copies = []
        for _ in range(num_copies):

            # Make a shallow copy of the pin.
            cpy = copy(self)

            # The copy is not on a net, yet.
            cpy.nets = []

            # Connect the new pin to the same net as the original.
            if self.nets:
                self.nets[0] += cpy

            # Attach additional attributes to the pin.
            for k, v in attribs.items():
                setattr(cpy, k, v)

            copies.append(cpy)

        return _list_or_scalar(copies)

    """Make copies with the multiplication operator or by calling the object."""
    __mul__ = copy
    __rmul__ = copy
    __call__ = copy

    def _is_connected(self):
        """
        Return true if a pin is connected to a net (but not a no-connect net).
        """
        if not self.nets:
            # This pin is not connected to any nets.
            return False

        # Get the types of things this pin is connected to.
        net_types = set([type(n) for n in self.nets])

        if set([_NCNet]) == net_types:
            # This pin is only connected to no-connect nets.
            return False
        if set([Net]) == net_types:
            # This pin is only connected to normal nets.
            return True
        if set([Net,_NCNet]) == net_types:
            # Can't be connected to both normal and no-connect nets!
            logger.error('{} is connected to both normal and no-connect nets!'.format(self._erc_desc()))
            raise Exception
        # This is just strange...
        logger.error("{} is connected to something strange: {}".format(
            self._erc_desc(), nets))
        raise Exception

    def _is_attached(pin_net_bus):
        """Return true if this pin is attached to the given pin, net or bus."""
        if not self._is_connected():
            return False
        if isinstance(pin_net_bus, Pin):
            if pin_net_bus._is_connected():
                return pin_net_bus.net._is_attached(self.net)
            else:
                return False
        if isinstance(pin_net_bus, Net):
            return pin_net_bus._is_attached(self.net)
        if isinstance(pin_net_bus, Bus):
            for net in pin_net_bus[:]:
                if self.net._is_attached(net):
                    return True
            return False
        logger.error("Pins can't be attached to {}!".format(type(pin_net_bus)))
        raise Exception

    def connect(self, *pins_nets_buses):
        """
        Return the pin after connecting it to one or more nets or pins.

        Args:
            pins_nets_buses: One or more Pin, Net or Bus objects or
                lists/tuples of them.

        Returns:
            The updated pin with the new connections.

        Notes:
            You can connect nets or pins to a pin like so::

                p = Pin()     # Create a pin.
                n = Net()     # Create a net.
                p += net      # Connect the net to the pin.
        """

        # Go through all the pins and/or nets and connect them to this pin.
        for pn in _expand_buses(_flatten(pins_nets_buses)):
            if isinstance(pn, Pin):
                # Connecting pin-to-pin.
                if self._is_connected():
                    # If self is already connected to a net, then add the
                    # other pin to the same net.
                    self.nets[0] += pn
                elif pn._is_connected():
                    # If self is unconnected but the other pin is, then
                    # connect self to the other pin's net.
                    pn.nets[0] += self
                else:
                    # Neither pin is connected to a net, so create a net
                    # and attach both to it.
                    Net().connect(self, pn)
            elif isinstance(pn, Net):
                # Connecting pin-to-net, so just connect the pin to the net.
                pn += self
            else:
                logger.error('Cannot attach non-Pin/non-Net {} to {}.'.format(
                    type(pn), self._erc_desc()))
                raise Exception

        # Set the flag to indicate this result came from the += operator.
        self.iadd_flag = True

        return self

    """Connect a net to a pin using the += operator."""
    __iadd__ = connect

    def _disconnect(self):
        """Disconnect this pin from all nets."""
        if not self.net:
            return
        for n in self.nets:
            n._disconnect(self)
        self.nets = []

    def _get_nets(self):
        """Return a list containing the Net objects connected to this pin."""
        return self.nets

    def _get_pins(self):
        """Return a list containing this pin."""
        return _to_list(self)

    def _erc_desc(self):
        """Return a string describing this pin for ERC."""
        desc = "{func} pin {num}/{name} of {part}".format(
            part=self.part._erc_desc(),
            num=self.num,
            name=self.name,
            func=Pin.pin_info[self.func]['function'])
        return desc

    def __str__(self):
        """Return a description of this pin as a string."""
        part_ref = getattr(self.part, 'ref', '???')
        pin_num = getattr(self, 'num', '???')
        pin_name = getattr(self, 'name', '???')
        pin_func = getattr(self, 'func', Pin.UNSPEC)
        pin_func_str = Pin.pin_info[pin_func]['function']
        return 'Pin {ref}/{num}/{name}/{func}'.format(
            ref = part_ref,
            num=pin_num,
            name=pin_name,
            func=pin_func_str)

    @property
    def net(self):
        """Return one of the nets the pin is connected to."""
        if self.nets:
            return self.nets[0]
        return None

    __repr__ = __str__

##############################################################################


class Alias(object):
    """
    An alias can be added to another object to give it another name.
    Since an object might have several aliases, each alias can be tagged
    with an identifier to discriminate between them.

    Args:
        name: The alias name.
        id_tag: The identifier tag.
    """

    def __init__(self, name, id_tag=None):
        self.name = name
        self.id = id_tag

    def __eq__(self, search):
        """
        Return true if one alias is equal to another.

        The aliases are equal if the following conditions are both true::

            1. The ids must match or one or both ids must be something
                that evaluates to False (i.e., None, empty string or list, etc.).

            2. The names must match based on using one name as a
                regular expression to compare to the other.

        Args:
            search: The Alias object which self will be compared to.
        """
        return (not self.id or not search.id or search.id == self.id) and \
            (re.fullmatch(str(search.name), str(self.name), flags=re.IGNORECASE) or
             re.fullmatch(str(self.name), str(search.name), flags=re.IGNORECASE))

##############################################################################


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
        part_defn: A list of strings that define the part (usually read from a
            schematic library file).
        tool: The format for the library file or part definition (e.g., KICAD).
        dest: String that indicates where the part is destined for (e.g., LIBRARY).
        connections: A dictionary with part pin names/numbers as keys and the
            names of nets to which they will be connected as values. For example:
            { 'IN-':'a_in', 'IN+':'GND', '1':'AMPED_OUTPUT', '14':'VCC', '7':'GND' }

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
                 tool=KICAD,
                 connections=None,
                 part_defn=None,
                 **attribs):

        # Create a Part from a library entry.
        if lib:
            # If the lib argument is a string, then create a library using the
            # string as the library file name.
            if isinstance(lib, type('')):
                lib = _SchLib(filename=lib, tool=tool)

            # Make a copy of the part from the library but don't add it to the netlist.
            part = lib[name].copy(1, TEMPLATE)

            # Overwrite self with the new part.
            self.__dict__.update(part.__dict__)

            # Make sure all the pins have a valid reference to this part.
            self._associate_pins()

        # Otherwise, create a Part from a part definition. If the part is
        # destined for a library, then just get its name. If it's going into
        # a netlist, then parse the entire part definition.
        elif part_defn:
            self.tool = tool
            self.part_defn = part_defn
            self._parse(just_get_name=dest != NETLIST)

        else:
            logger.error(
                "Can't make a part without a library & part name or a part definition.")
            raise Exception

        # Add additional attributes to the part.
        for k, v in attribs.items():
            setattr(self, k, v)

        # Allow part to be included in ERC.
        self.do_erc = True

        # Dictionary for storing subunits of the part, if desired.
        self.unit = {}

        # If the part is going to be an element in a circuit, then add it to the
        # the circuit and make any indicated pin/net connections.
        if dest != LIBRARY:
            if dest == NETLIST:
                SubCircuit._add_part(self)
            if isinstance(connections, dict):
                for pin, net in connections.items():
                    net += self[pin]

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

    def _parse(self, just_get_name=False):
        """
        Create a part from its stored part definition.

        Args:
            just_get_name: When true, just get the name and aliases for the
                part. Leave the rest unparsed.
        """

        try:
            parse_func = self.__class__.__dict__['_parse_{}'.format(self.tool)]
            parse_func(self, just_get_name)
        except KeyError:
            logger.error(
                "Can't create a part with an unknown ECAD tool file format: {}.".format(
                    self.tool))
            raise Exception

        # Find the minimum and maximum pin numbers for the part after parsing.
        self.min_pin, self.max_pin = self._find_min_max_pins()

    def _parse_kicad(self, just_get_name=False):
        """
        Create a Part using a part definition from a KiCad schematic library.

        This method was written based on the code from
        https://github.com/KiCad/kicad-library-utils/tree/master/schlib.
        It's covered by GPL3.

        Args:
            part_defn: A list of strings that define the part (usually read from a
                schematic library file). Can also be None.
            just_get_name: If true, scan the part definition until the
                name and aliases are found. The rest of the definition
                will be parsed if the part is actually used.
        """

        _DEF_KEYS = ['name', 'reference', 'unused', 'text_offset',
                     'draw_pinnumber', 'draw_pinname', 'unit_count',
                     'units_locked', 'option_flag']
        _F0_KEYS = ['reference', 'posx', 'posy', 'text_size', 'text_orient',
                    'visibility', 'htext_justify', 'vtext_justify']
        _FN_KEYS = ['name', 'posx', 'posy', 'text_size', 'text_orient',
                    'visibility', 'htext_justify', 'vtext_justify',
                    'fieldname']
        _ARC_KEYS = ['posx', 'posy', 'radius', 'start_angle', 'end_angle',
                     'unit', 'convert', 'thickness', 'fill', 'startx',
                     'starty', 'endx', 'endy']
        _CIRCLE_KEYS = ['posx', 'posy', 'radius', 'unit', 'convert',
                        'thickness', 'fill']
        _POLY_KEYS = ['point_count', 'unit', 'convert', 'thickness', 'points',
                      'fill']
        _RECT_KEYS = ['startx', 'starty', 'endx', 'endy', 'unit', 'convert',
                      'thickness', 'fill']
        _TEXT_KEYS = ['direction', 'posx', 'posy', 'text_size', 'text_type',
                      'unit', 'convert', 'text', 'italic', 'bold', 'hjustify',
                      'vjustify']
        _PIN_KEYS = ['name', 'num', 'posx', 'posy', 'length', 'direction',
                     'name_text_size', 'num_text_size', 'unit', 'convert',
                     'electrical_type', 'pin_type']
        _DRAW_KEYS = {'arcs': _ARC_KEYS,
                      'circles': _CIRCLE_KEYS,
                      'polylines': _POLY_KEYS,
                      'rectangles': _RECT_KEYS,
                      'texts': _TEXT_KEYS,
                      'pins': _PIN_KEYS}
        _DRAW_ELEMS = {'arcs': 'A',
                       'circles': 'C',
                       'polylines': 'P',
                       'rectangles': 'S',
                       'texts': 'T',
                       'pins': 'X'}
        _KEYS = {'DEF': _DEF_KEYS,
                 'F0': _F0_KEYS,
                 'F': _FN_KEYS,
                 'A': _ARC_KEYS,
                 'C': _CIRCLE_KEYS,
                 'P': _POLY_KEYS,
                 'S': _RECT_KEYS,
                 'T': _TEXT_KEYS,
                 'X': _PIN_KEYS}

        # Return if there's nothing to do (i.e., part has already been parsed).
        if not self.part_defn:
            return

        self.fplist = []  # Footprint list.
        self.aliases = []  # Part aliases.
        building_fplist = False  # True when working on footprint list in defn.
        building_draw = False  # True when gathering part drawing from defn.

        # Go through the part definition line-by-line.
        for line in self.part_defn:

            # Split the line into words.
            line = line.replace('\n', '')
            s = shlex.shlex(line)
            s.whitespace_split = True
            s.commenters = ''
            s.quotes = '"'
            line = list(s)  # Place the words in a list.

            # The first word indicates the type of part definition data that will follow.
            if line[0] in _KEYS:
                # Get the keywords for the current part definition data.
                key_list = _KEYS[line[0]]
                # Make a list of the values in the part data associated with each key.
                # Use an empty string for any missing values so every key will be
                # associated with something.
                values = line[1:] + [
                    '' for n in range(len(key_list) - len(line[1:]))
                ]

            # Create a dictionary of part definition keywords and values.
            if line[0] == 'DEF':
                self.definition = dict(list(zip(_DEF_KEYS, values)))
                self.name = self.definition['name']

                # To handle libraries quickly, just get the name and
                # aliases and only parse the rest of the part definition later.
                if just_get_name:
                    if self.aliases:
                        # Name found, aliases already found so we're done.
                        return
                    # Name found so scan defn to see if aliases are present.
                    # (The majority of parts don't have aliases.)
                    for line in self.part_defn:
                        if re.match(r'^\s*ALIAS\s', line):
                            # Break and keep parsing defn if aliases are present.
                            break
                    else:
                        # No aliases found, so part name is all that's needed.
                        return

            # Create a dictionary of F0 part field keywords and values.
            elif line[0] == 'F0':
                self.fields = []
                self.fields.append(dict(list(zip(_F0_KEYS, values))))

            # Create a dictionary of the other part field keywords and values.
            elif line[0][0] == 'F':
                # Make a list of field values with empty strings for missing fields.
                values = line[1:] + [
                    '' for n in range(len(_FN_KEYS) - len(line[1:]))
                ]
                self.fields.append(dict(list(zip(_FN_KEYS, values))))

            # Create a list of part aliases.
            elif line[0] == 'ALIAS':
                self.aliases = [alias for alias in line[1:]]
                if just_get_name and self.name:
                    # Aliases found, name already found so we're done.
                    return

            # Start the list of part footprints.
            elif line[0] == '$FPLIST':
                building_fplist = True
                self.fplist = []

            # End the list of part footprints.
            elif line[0] == '$ENDFPLIST':
                building_fplist = False

            # Start gathering the drawing primitives for the part symbol.
            elif line[0] == 'DRAW':
                building_draw = True
                self.draw = {
                    'arcs': [],
                    'circles': [],
                    'polylines': [],
                    'rectangles': [],
                    'texts': [],
                    'pins': []
                }

            # End the gathering of drawing primitives.
            elif line[0] == 'ENDDRAW':
                building_draw = False

            # Every other line is either a footprint or a drawing primitive.
            else:
                # If the footprint list is being built, then add this line to it.
                if building_fplist:
                    self.fplist.append(line[0])

                # Else if the drawing primitives are being gathered, process the
                # current line to see what type of primitive is in play.
                elif building_draw:

                    # Gather arcs.
                    if line[0] == 'A':
                        self.draw['arcs'].append(dict(list(zip(_ARC_KEYS,
                                                               values))))

                    # Gather circles.
                    if line[0] == 'C':
                        self.draw['circles'].append(dict(list(zip(_CIRCLE_KEYS,
                                                                  values))))

                    # Gather polygons.
                    if line[0] == 'P':
                        n_points = int(line[1])
                        points = line[5:5 + (2 * n_points)]
                        values = line[1:5] + [points]
                        if len(line) > (5 + len(points)):
                            values += [line[-1]]
                        else:
                            values += ['']
                        self.draw['polylines'].append(dict(list(zip(_POLY_KEYS,
                                                                    values))))

                    # Gather rectangles.
                    if line[0] == 'S':
                        self.draw['rectangles'].append(dict(list(zip(
                            _RECT_KEYS, values))))

                    # Gather text.
                    if line[0] == 'T':
                        self.draw['texts'].append(dict(list(zip(_TEXT_KEYS,
                                                                values))))

                    # Gather the pin symbols. This is what we really want since
                    # this defines the names, numbers and attributes of the
                    # pins associated with the part.
                    if line[0] == 'X':
                        self.draw['pins'].append(dict(list(zip(_PIN_KEYS,
                                                               values))))

        # Define some shortcuts to part information.
        self.num_units = int(
            self.definition['unit_count'])  # # of units within the part.
        self.name = self.definition['name']  # Part name (e.g., 'LM324').
        self.ref_prefix = self.definition[
            'reference']  # Part ref prefix (e.g., 'R').

        # Clear the part reference field directly. Don't use the setter function
        # since it will try to generate and assign a unique part reference if
        # passed a value of None.
        self._ref = None

        # Make a Pin object from the information in the KiCad pin data fields.
        def kicad_pin_to_pin(kicad_pin):
            p = Pin()
            # Replicate the KiCad pin fields as attributes in the Pin object.
            # Note that this update will not give the pins valid references
            # to the current part, but we'll fix that soon.
            p.__dict__.update(kicad_pin)

            pin_type_translation = {'I': Pin.INPUT,
                                    'O': Pin.OUTPUT,
                                    'B': Pin.BIDIR,
                                    'T': Pin.TRISTATE,
                                    'P': Pin.PASSIVE,
                                    'U': Pin.UNSPEC,
                                    'W': Pin.PWRIN,
                                    'w': Pin.PWROUT,
                                    'C': Pin.OPENCOLL,
                                    'E': Pin.OPENEMIT,
                                    'N': Pin.NOCONNECT}
            p.func = pin_type_translation[p.electrical_type]

            return p

        self.pins = [kicad_pin_to_pin(p) for p in self.draw['pins']]

        # Make sure all the pins have a valid reference to this part.
        self._associate_pins()

        # Part definition has been parsed, so clear it out. This prevents a
        # part from being parsed more than once.
        self.part_defn = None

    def _associate_pins(self):
        """
        Make sure all the pins in a part have valid references to the part.
        """
        for p in self.pins:
            p.part = self

    def copy(self, num_copies=1, dest=NETLIST, **attribs):
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

        num_copies = max(num_copies, _find_num_copies(**attribs))

        # Check that a valid number of copies is requested.
        if not isinstance(num_copies, int):
            logger.error(
                "Can't make a non-integer number ({}) of copies of a part!".format(
                    num_copies))
            raise Exception
        if num_copies < 0:
            logger.error(
                "Can't make a negative number ({}) of copies of a part!".format(
                    num_copies))
            raise Exception

        # Now make copies of the part one-by-one.
        copies = []
        for i in range(num_copies):

            # Make a shallow copy of the part.
            cpy = copy(self)

            # The shallow copy will just put references to the pins of the
            # original into the copy, so create independent copies of the pins.
            pin_copies = []
            for p in self.pins:
                pin_copies.append(p.copy())
            self.pins = pin_copies

            # Make sure all the pins have a reference to this new part copy.
            cpy._associate_pins()

            # Clear the part reference of the copied part so a unique reference
            # can be assigned when the part is added to the circuit.
            # (This is not strictly necessary since the part reference will be
            # adjusted to be unique if needed during the addition process.)
            cpy._ref = None

            # Enter any new attributes.
            for k, v in attribs.items():
                if isinstance(v, (list, tuple)):
                    try:
                        v = v[i]
                    except IndexError:
                        logger.error(
                            "{} copies of part {} were requested, but too few elements in attribute {}!".format(
                                num_copies, self.name, k))
                        raise Exception
                setattr(cpy, k, v)

            # Add the part copy to the list of copies and then add the
            # part to the circuit netlist (if requested).
            copies.append(cpy)
            if dest == NETLIST:
                SubCircuit._add_part(cpy)

        return _list_or_scalar(copies)

    """Make copies with the multiplication operator or by calling the object."""
    __mul__ = copy
    __rmul__ = copy
    __call__ = copy

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

        # If no pin identifiers were given, then use a wildcard that will
        # select all pins.
        if not pin_ids:
            pin_ids = ['.*']

        # Go through the list of pin IDs one-by-one.
        pins = _NetPinList()
        for p_id in _expand_indices(self.min_pin, self.max_pin, *pin_ids):

            # Pin ID is an integer.
            if isinstance(p_id, int):
                pins.extend(_filter(self.pins, num=str(p_id), **criteria))

            # Pin ID is a string containing a number or name.
            else:
                # First try to get pins using the string as a number.
                tmp_pins = _filter(self.pins, num=p_id, **criteria)
                if tmp_pins:
                    pins.extend(tmp_pins)
                else:
                    # If that didn't work, try using the string as a pin name.
                    tmp_pins = _filter(self.pins, name=p_id, **criteria)
                    if tmp_pins:
                        pins.extend(tmp_pins)
                    else:
                        # If that didn't work, look for pin aliases.
                        alias = Alias(p_id, id(self))
                        pins.extend(_filter(self.pins,
                                            alias=alias,
                                            **criteria))

        return _list_or_scalar(pins)

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

    def _is_connected(self):
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
            if p._is_connected():
                return True

        # No net connections found, so return False.
        return False

    def set_pin_alias(self, alias, *pin_ids, **criteria):
        pins = _to_list(self.get_pins(*pin_ids, **criteria))
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
            logger.warning("Using a label ({}) for a unit of {} that matches one or more of it's pin names ({})!".format(label, self._erc_desc(), collisions))
        self.unit[label] = PartUnit(self, *pin_ids, **criteria)
        return self.unit[label]

    def _generate_netlist_component(self, tool=KICAD):
        """
        Generate the part information for inclusion in a netlist.

        Args:
            tool: The format for the netlist file (e.g., KICAD).
        """

        try:
            gen_func = self.__class__.__dict__['_gen_netlist_comp_{}'.format(
                tool)]
            return gen_func(self)
        except KeyError:
            logger.error(
                "Can't generate netlist in an unknown ECAD tool format ({}).".format(
                    format))
            raise Exception

    def _gen_netlist_comp_kicad(self):
        ref = self.ref
        try:
            value = self.value
            if not value:
                value = self.name
        except AttributeError:
            try:
                value = self.name
            except AttributeError:
                value = self.ref_prefix
        try:
            footprint = self.footprint
        except AttributeError:
            logger.error('No footprint for {part}/{ref}.'.format(
                part=self.name, ref=ref))
            footprint = 'No Footprint'

        txt = '    (comp (ref {ref})\n      (value {value})\n      (footprint {footprint}))'.format(
            ref=ref, value=value, footprint=footprint)
        return txt

    def _erc(self):
        """
        Do electrical rules check on a part in the schematic.
        """

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
                    erc_logger.warning('Unconnected pin: {p}.'.format(
                        p=p._erc_desc()))

            # Error if a no-connect pin is connected to a net.
            elif p.net.drive != Pin.NOCONNECT_DRIVE:
                if p.func == Pin.NOCONNECT:
                    erc_logger.warning(
                        'Incorrectly connected pin: {p} should not be connected to a net ({n}).'.format(
                            p=p._erc_desc(), n=p.net.name))

    def _erc_desc(self):
        """Create description of part for ERC and other error reporting."""
        return "{p.name}/{p.ref}".format(p=self)

    def __str__(self):
        """Return a description of the pins on this part as a string."""
        return self.name + ':\n\t' + '\n\t'.join(
            [p.__str__() for p in self.pins])

    __repr__ = __str__

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
        self._ref = _get_unique_name(SubCircuit.parts, 'ref', self.ref_prefix,
                                     r)
        return

    @ref.deleter
    def ref(self):
        """Delete the part reference."""
        self._ref = None

    @property
    def value(self):
        """Get, set and delete the part value."""
        return self._value

    @value.setter
    def value(self, value):
        """Set the part value."""
        self._value = str(value)

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
        unique_pins |= set(_to_list(self.parent.get_pins(*pin_ids, **
                                                         criteria)))
        self.pins = list(unique_pins)

##############################################################################


class Net(object):
    """
    Lists of connected pins are stored as nets using this class.

    Args:
        name: A string with the name of the net. If None or '', then
            a unique net name will be assigned.
        *pins_nets_buses: One or more Pin, Net, or Bus objects or
            lists/tuples of them to be connected to this net.

    Keyword Args:
        attribs: A dictionary of attributes and values to attach to
            the Net object.
    """

    def __init__(self, name=None, *pins_nets_buses, **attribs):
        self._valid = True # Make net valid before doing anything else.
        self._name = None
        if name:
            self.name = name
        self.do_erc = True
        self._drive = Pin.NO_DRIVE
        self.pins = []

        # Attach whatever pins were given.
        self.connect(pins_nets_buses)
        del self.iadd_flag # Remove the += flag inserted by connect().

        # Attach additional attributes to the net.
        for k, v in attribs.items():
            setattr(self, k, v)

    def _traverse(self):
        """Return all the nets and pins attached to this net, including itself."""
        self.test_validity()
        prev_nets = set([self])
        nets = set([self])
        prev_pins = set([])
        pins = set(self.pins)
        while pins != prev_pins:

            # Add the nets attached to any unvisited pins.
            for pin in pins - prev_pins:
                # No use visiting a pin that is not connected to a net.
                if pin._is_connected():
                    nets |= set(pin._get_nets())

            # Update the set of previously visited pins.
            prev_pins = copy(pins)

            # Add the pins attached to any unvisited nets.
            for net in nets - prev_nets:
                pins |= set(net.pins)

            # Update the set of previously visited nets.
            prev_nets = copy(nets)

        return list(nets), list(pins)

    def _get_pins(self):
        """Return a list of pins attached to this net."""
        self.test_validity()
        return self._traverse()[1]

    def _get_nets(self):
        """Return a list of nets attached to this net, including this net."""
        self.test_validity()
        return self._traverse()[0]

    def _is_attached(self, pin_net_bus):
        """Return true if the net is attached to this one."""
        if isinstance(pin_net_bus, Net):
            return pin_net_bus in self._get_nets()
        if isinstance(pin_net_bus, Pin):
            return pin_net_bus._is_attached(self)
        if isinstance(pin_net_bus, Bus):
            for net in pin_net_bus[:]:
                if self._is_attached(net):
                    return True
            return False
        logger.error("Nets can't be attached to {}!".format(type(pin_net_bus)))
        raise Exception

    def copy(self, num_copies=1, **attribs):
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

        num_copies = max(num_copies, _find_num_copies(**attribs))

        # Check that a valid number of copies is requested.
        if not isinstance(num_copies, int):
            logger.error(
                "Can't make a non-integer number ({}) of copies of a net!".format(
                    num_copies))
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
                "Can't make copies of a net that already has pins attached to it!")
            raise Exception

        # Now make copies of the net one-by-one.
        copies = [deepcopy(self) for i in range(num_copies)]

        # Enter new attributes into each copy.
        for i, cpy in enumerate(copies):
            for k, v in attribs.items():
                if isinstance(v, (list, tuple)):
                    try:
                        v = v[i]
                    except IndexError:
                        logger.error(
                            "{} copies of net {} were requested, but too few elements in attribute {}!".format(
                                num_copies, self.name, k))
                        raise Exception
                setattr(cpy, k, v)

        return _list_or_scalar(copies)

    """Make copies with the multiplication operator or by calling the object."""
    __mul__ = copy
    __rmul__ = copy
    __call__ = copy

    def _is_anonymous(self, net_name=None):
        """Return true if the net name is anonymous."""
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

        def merge(net):
            """
            Merge pins on net with self and then delete net.

            Args:
                net: The net to merge with self.
            """

            if isinstance(self, _NCNet):
                logger.error("Can't merge with a no-connect net {}!".format(
                    self.name))
                raise Exception

            if isinstance(net, _NCNet):
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

            # Update the drive of the merged nets.
            self.drive = net.drive
            net.drive = self.drive

            def select_name(name1, name2):
                """Select one name or the other for the merged net."""
                if not name2:
                    return name1
                if not name1:
                    return name2
                if self._is_anonymous(name2):
                    return name1
                if self._is_anonymous(name1):
                    return name2
                logger.warning(
                    'Merging two named nets ({a} and {b}) into {a}.'.format(
                        a=name1, b=name2))
                return name1

            # Give the merged net the name of one of the nets.
            # Bypass the unique naming function because all the
            # net names should already have unique names.
            name = select_name(self.name, net.name)
            self._name = name
            net._name = name

        def connect_pin(pin):
            """Connect a pin to this net."""
            if pin not in self.pins:
                if not pin._is_connected():
                    # Remove the pin from the no-connect net if it is attached to it.
                    pin._disconnect()
                self.pins.append(pin)
                pin.nets.append(self)
            return

        self.test_validity()

        # Go through all the pins and/or nets and connect them to this net.
        for pn in _expand_buses(_flatten(pins_nets_buses)):
            if isinstance(pn, Net):
                merge(pn)
            elif isinstance(pn, Pin):
                connect_pin(pn)
            else:
                logger.error(
                    'Cannot attach non-Pin/non-Net {} to Net {}.'.format(
                        type(pn), self.name))
                raise Exception

        # Add the net to the global netlist. (It won't be added again
        # if it's already there.)
        SubCircuit._add_net(self)

        # Set the flag to indicate this result came from the += operator.
        self.iadd_flag = True

        return self

    # Use += to connect to nets.
    __iadd__ = connect

    def _disconnect(self, pin):
        """Remove the pin from this net but not any other nets it's attached to."""
        try:
            self.pins.remove(pin)
        except ValueError:
            pass

    def _generate_netlist_net(self, tool=KICAD):
        """
        Generate the net information for inclusion in a netlist.

        Args:
            tool: The format for the netlist file (e.g., KICAD).
        """
        self.test_validity()

        try:
            gen_func = self.__class__.__dict__['_gen_netlist_net_{}'.format(
                tool)]
            return gen_func(self)
        except KeyError:
            logger.error(
                "Can't generate netlist in an unknown ECAD tool format ({}).".format(
                    format))
            raise Exception

    def _gen_netlist_net_kicad(self):
        txt = '    (net (code {code}) (name "{name}")'.format(code=self.code,
                                                              name=self.name)
        for p in self._get_pins():
            txt += '\n      (node (ref {part_ref}) (pin {pin_num}))'.format(
                part_ref=p.part.ref, pin_num=p.num)
        txt += (')')
        return txt

    def _erc(self):
        """
        Do electrical rules check on a net in the schematic.
        """

        def pin_conflict_chk(pin1, pin2):
            """
            Check for conflict/contention between two pins on the same net.
            """

            if not pin1.do_erc or not pin2.do_erc:
                return

            erc_result = SubCircuit._erc_pin_to_pin_chk(pin1, pin2)

            # Return if the pins are compatible.
            if erc_result == SubCircuit.OK:
                return

            # Otherwise, generate an error or warning message.
            msg = 'Pin conflict on net {n}: {p1} <==> {p2}'.format(
                n=pin1.net.name,
                p1=pin1._erc_desc(),
                p2=pin2._erc_desc())
            if erc_result == SubCircuit.WARNING:
                erc_logger.warning(msg)
            else:
                erc_logger.error(msg)

        def net_drive_chk():
            """
            Check the drive level on the net to see if it is within bounds.
            """

            # Find the maximum signal driver on this net.
            net_drive = self.drive  # Start with user-set drive level.
            pins = self._get_pins()
            for p in pins:
                net_drive = max(net_drive, Pin.pin_info[p.func]['drive'])

            if net_drive <= Pin.NO_DRIVE:
                erc_logger.warning('No drivers for net {n}'.format(
                    n=self.name))
            for p in pins:
                if Pin.pin_info[p.func]['min_rcv'] > net_drive:
                    erc_logger.warning(
                        'Insufficient drive current on net {n} for pin {p}'.format(
                            n=self.name, p=p._erc_desc()))

        self.test_validity()

        # Skip ERC check on this net if flag is cleared.
        if not self.do_erc:
            return

        # Check the number of pins attached to the net.
        pins = self._get_pins()
        num_pins = len(pins)
        if num_pins == 0:
            erc_logger.warning('No pins attached to net {n}.'.format(
                n=self.name))
        elif num_pins == 1:
            erc_logger.warning(
                'Only one pin ({p}) attached to net {n}.'.format(p=pins[
                    0]._erc_desc(), n=self.name))
        else:
            for i in range(num_pins):
                for j in range(i + 1, num_pins):
                    pin_conflict_chk(pins[i], pins[j])

        # Check to see if the net has sufficient drive.
        net_drive_chk()

    def __str__(self):
        """Return a list of the pins on this net as a string."""
        self.test_validity()
        pins = self._get_pins()
        return self.name + ': ' + ', '.join([p.__str__() for p in pins])

    __repr__ = __str__

    def __len__(self):
        """Return the number of pins attached to this net."""
        self.test_validity()
        pins = self._get_pins()
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
        self.test_validity()
        # Remove the existing name so it doesn't cause a collision if the
        # object is renamed with its existing name.
        self._name = None

        # Now name the object with the given name or some variation
        # of it that doesn't collide with anything else in the list.
        self._name = _get_unique_name(SubCircuit.nets, 'name', NET_PREFIX,
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
        logger.error('Net {} is no longer valid. Do not use it!'.format(self.name))
        raise Exception

##############################################################################


class _NCNet(Net):
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

    def __init__(self, name=None, *pins_nets_buses, **attribs):
        super(_NCNet, self).__init__(name, *pins_nets_buses, **attribs)
        self._drive = Pin.NOCONNECT_DRIVE

    def _generate_netlist_net(self, tool=KICAD):
        """NO_CONNECT nets don't generate anything for netlists."""
        return ''

    def _erc(self):
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

##############################################################################


class Bus(object):
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
            led1 = Part('device', 'LED')
            b = Bus('B', 8, n, led1['K'])
    """

    def __init__(self, name, *args, **attribs):
        self.name = name

        # Build the bus from net widths, existing nets, nets of pins, other buses.
        self.nets = []
        for arg in _flatten(args):
            if isinstance(arg, int):
                # Add a number of new nets to the bus.
                self.nets.extend(arg * Net())
            elif isinstance(arg, Net):
                # Add an existing net to the bus.
                self.nets.append(arg)
            elif isinstance(arg, Pin):
                # Add a pin to the bus.
                try:
                    # Add the pin's net to the bus.
                    self.nets.append(arg._get_nets()[0])
                except IndexError:
                    # OK, the pin wasn't already connected to a net,
                    # so create a new net, add it to the bus, and
                    # connect the pin to it.
                    n = Net()
                    n += arg
                    self.nets.append(n)
            elif isinstance(arg, Bus):
                # Add an existing bus to this bus.
                self.nets.extend(arg.nets)

        # Assign names to all the unnamed nets in the bus.
        for i, net in enumerate(self.nets):
            if net._is_anonymous():
                # Net names are the bus name with the index appended.
                net.name = self.name + str(i)

        # Attach additional attributes to the bus.
        for k, v in attribs.items():
            setattr(self, k, v)

    def _get_nets(self):
        """Return the list of nets contained in this bus."""
        return _to_list(self.nets)

    def _get_pins(self):
        """It's an error to get the list of pins attached to all bus lines."""
        logger.error("Can't get the list of pins on a bus!")
        raise Exception

    def copy(self, num_copies=1, **attribs):
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

        # Check that a valid number of copies is requested.
        if not isinstance(num_copies, int):
            logger.error(
                "Can't make a non-integer number ({}) of copies of a bus!".format(
                    num_copies))
            raise Exception
        if num_copies < 0:
            logger.error(
                "Can't make a negative number ({}) of copies of a bus!".format(
                    num_copies))
            raise Exception

        copies = []
        for i in range(num_copies):

            cpy = Bus(self)

            # Attach additional attributes to the bus.
            for k, v in attribs.items():
                if isinstance(v, (list, tuple)):
                    try:
                        v = v[i]
                    except IndexError:
                        logger.error(
                            "{} copies of bus {} were requested, but too few elements in attribute {}!".format(
                                num_copies, self.name, k))
                        raise Exception
                setattr(cpy, k, v)

            copies.append(cpy)

        return _list_or_scalar(copies)

    """Make copies with the multiplication operator or by calling the object."""
    __mul__ = copy
    __rmul__ = copy
    __call__ = copy

    def __getitem__(self, *ids):
        """
        Return a bus made up of the nets at the given indices.

        Args:
            ids: A list of indices of bus lines. These can be individual
                numbers, net names, nested lists, or slices.

        Returns:
            A bus if the indices are valid, otherwise None.
        """

        # Use the indices to get the nets from the bus.
        nets = []
        for ident in _expand_indices(0, len(self) - 1, ids):
            if isinstance(ident, int):
                nets.append(self.nets[ident])
            elif isinstance(ident, type('')):
                nets.extend(_filter(self.nets, name=ident))
            else:
                logger.error("Can't index bus with a {}.".format(type(ident)))
                raise Exception

        if len(nets) == 0:
            # No nets were selected from the bus, so return None.
            return None
        if len(nets) == 1:
            # Just one net selected, so return the Net object.
            return nets[0]
        else:
            # Multiple nets selected, so return them as a NetPinList list.
            return _NetPinList(nets)

    def __setitem__(self, ids, *pins_nets_buses):
        """
        You can't assign to bus lines. You must use the += operator.
        
        This method is a work-around that allows the use of the += for making
        connections to bus lines while prohibiting direct assignment. Python
        processes something like my_bus[7:0] += 8 * Pin() as follows::

            1. Part.__getitem__ is called with '7:0' as the index. This 
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
        if getattr(pins_nets_buses[0], 'iadd_flag', False):
            del pins_nets_buses[0].iadd_flag
            return

        # No iadd_flag or it wasn't set. This means a direct assignment
        # was made to the pin, which is not allowed.
        logger.error("Can't assign to a bus! Use the += operator.")
        raise Exception

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
        nets = _NetPinList(self.nets)
        nets += pins_nets_buses
        return self

    __iadd__ = connect

    @property
    def name(self):
        """
        Get, set and delete the name of the bus.

        When setting the bus name, if another bus with the same name
        is found, the name for this bus is adjusted to make it unique.
        """
        return self._name

    @name.setter
    def name(self, name):
        # Remove the existing name so it doesn't cause a collision if the
        # object is renamed with its existing name.
        self._name = None

        # Now name the object with the given name or some variation
        # of it that doesn't collide with anything else in the list.
        self._name = _get_unique_name(SubCircuit.buses, 'name', BUS_PREFIX,
                                      name)

    @name.deleter
    def name(self):
        """Delete the bus name."""
        del self._name

    def __str__(self):
        """Return a list of the nets in this bus as a string."""
        return self.name + ':\n\t' + '\n\t'.join([n.__str__() for n in self.nets])

    __repr__ = __str__

    def __len__(self):
        """Return the number of nets in this bus."""
        return len(self.nets)

##############################################################################

class _NetPinList(list):

    def __iadd__(self, *nets_pins_buses):

        nets_pins = []
        for item in _expand_buses(_flatten(nets_pins_buses)):
            if isinstance(item, (Pin, Net)):
                nets_pins.append(item)
            else:
                logger.error("Can't make connections to a {} ({}).".format(
                    type(id), item.__name__))
                raise Exception

        if len(nets_pins) != len(self):
            if Net in [type(item) for item in self] or len(nets_pins) > 1:
                logger.error(
                    "Connection mismatch {} != {}!".format(
                        len(self), len(nets_pins)))
                raise Exception

            # If just a single net is to be connected, make a list out of it that's
            # just as long as the list of pins to connect to. This will connect
            # multiple pins to the same net.
            if len(nets_pins) == 1:
                nets_pins = [nets_pins[0] for _ in range(len(self))]

        # Connect the nets to the nets in the bus.
        for i, np in enumerate(nets_pins):
            self[i] += np

        # Set the flag to indicate this result came from the += operator.
        self.iadd_flag = True

        return self


##############################################################################


class SubCircuit(object):
    """
    Class object that holds the entire netlist of parts and nets. This is
    initialized once when the module is first imported and then all parts
    and nets are added to its static members.

    Attributes:
        parts: List of all the schematic parts as Part objects.
        nets: List of all the schematic nets as Net objects.
        hierarchy: A '.'-separated concatenation of the names of nested
            SubCircuits at the current time it is read.
        level: The current level in the schematic hierarchy.
        context: Stack of contexts for each level in the hierarchy.
        circuit_func: The function that creates a given subcircuit.
    """

    OK, WARNING, ERROR = range(3)

    parts = []
    nets = []
    buses = []
    hierarchy = 'top'
    level = 0
    context = [('top', )]

    @classmethod
    def _reset(cls):
        """Clear any circuitry and start over."""
        cls.parts = []
        cls.nets = []
        cls.hierarchy = 'top'
        cls.level = 0
        cls.context = [('top', )]

    @classmethod
    def _add_part(cls, part):
        """Add a Part object to the circuit"""
        part.ref = part.ref  # This adjusts the part reference if necessary.
        part.hierarchy = cls.hierarchy  # Tag the part with its hierarchy position.
        cls.parts.append(part)

    @classmethod
    def _add_net(cls, net):
        """Add a Net object to the circuit. Assign a net name if necessary."""
        if net in cls.nets or len(net.pins) == 0:
            return
        net.name = net.name
        net.hierarchy = cls.hierarchy  # Tag the net with its hierarchy position.
        cls.nets.append(net)

    @classmethod
    def _get_nets(cls):
        """Get all the distinct nets for the circuit."""
        distinct_nets = []
        for net in cls.nets:
            for n in distinct_nets:
                # Exclude net if its already attached to a previously selected net.
                if net._is_attached(n):
                    break
            else:
                # This net is not attached to any of the other distinct nets,
                # so it is also distinct.
                distinct_nets.append(net)
        return distinct_nets

    @classmethod
    def _delete_net(cls, net):
        """Delete net from circuit."""
        if net in cls.nets:
            cls.nets.remove(net)
        del net

    @classmethod
    def _add_bus(cls, bus):
        """Add a Bus object to the circuit. Assign a bus name if necessary."""
        bus.name = bus.name
        bus.hierarchy = cls.hierarchy  # Tag the bus with its hierarchy position.
        cls.buses.append(bus)

    def __init__(self, circuit_func):
        """
        When you place the @SubCircuit decorator before a function, this method
        stores the reference to the subroutine into the SubCircuit object.
        """

        self.circuit_func = circuit_func

    def __call__(self, *args, **kwargs):
        """
        This method is called when you invoke the SubCircuit object to create
        some schematic circuitry.
        """

        # Invoking the SubCircuit object creates circuitry at a level one
        # greater than the current level. (The top level is zero.)
        self.level += 1

        # Create a name for this SubCircuit from the concatenated names of all
        # the SubCircuit functions that were called on all the preceding levels
        # that led to this one.
        self.__class__.hierarchy = self.context[-1][
            0] + '.' + self.circuit_func.__name__

        # Store the context so it can be used if this SubCircuit object
        # invokes another SubCircuit object within itself to add more
        # levels of hierarchy.
        self.context.append((self.__class__.hierarchy, ))

        # Call the SubCircuit object function to create whatever circuitry it handles.
        # The arguments to the function are usually nets to be connected to the
        # parts instantiated in the function, but they may also be user-specific
        # and have no effect on the mechanics of adding parts or nets although
        # they may direct the function as to what parts and nets get created.
        # Store any results it returns as a list. These results are user-specific
        # and have no effect on the mechanics of adding parts or nets.
        try:
            results = _list_or_scalar(self.circuit_func(*args, **kwargs))
        except Exception:
            logger.exception("Serious error! Can't continue.")

        # Restore the context that existed before the SubCircuit circuitry was
        # created. This does not remove the circuitry since it has already been
        # added to the parts and nets lists.
        self.context.pop()

        return results

    @classmethod
    def _erc_setup(cls):
        """
        Initialize the electrical rules checker.
        """

        # Initialize the pin contention matrix.
        cls._erc_matrix = [[cls.OK for c in range(11)] for r in range(11)]
        cls._erc_matrix[Pin.OUTPUT][Pin.OUTPUT] = cls.ERROR
        cls._erc_matrix[Pin.TRISTATE][Pin.OUTPUT] = cls.WARNING
        cls._erc_matrix[Pin.UNSPEC][Pin.INPUT] = cls.WARNING
        cls._erc_matrix[Pin.UNSPEC][Pin.OUTPUT] = cls.WARNING
        cls._erc_matrix[Pin.UNSPEC][Pin.BIDIR] = cls.WARNING
        cls._erc_matrix[Pin.UNSPEC][Pin.TRISTATE] = cls.WARNING
        cls._erc_matrix[Pin.UNSPEC][Pin.PASSIVE] = cls.WARNING
        cls._erc_matrix[Pin.UNSPEC][Pin.UNSPEC] = cls.WARNING
        cls._erc_matrix[Pin.PWRIN][Pin.TRISTATE] = cls.WARNING
        cls._erc_matrix[Pin.PWRIN][Pin.UNSPEC] = cls.WARNING
        cls._erc_matrix[Pin.PWROUT][Pin.OUTPUT] = cls.ERROR
        cls._erc_matrix[Pin.PWROUT][Pin.BIDIR] = cls.WARNING
        cls._erc_matrix[Pin.PWROUT][Pin.TRISTATE] = cls.ERROR
        cls._erc_matrix[Pin.PWROUT][Pin.UNSPEC] = cls.WARNING
        cls._erc_matrix[Pin.PWROUT][Pin.PWROUT] = cls.ERROR
        cls._erc_matrix[Pin.OPENCOLL][Pin.OUTPUT] = cls.ERROR
        cls._erc_matrix[Pin.OPENCOLL][Pin.TRISTATE] = cls.ERROR
        cls._erc_matrix[Pin.OPENCOLL][Pin.UNSPEC] = cls.WARNING
        cls._erc_matrix[Pin.OPENCOLL][Pin.PWROUT] = cls.ERROR
        cls._erc_matrix[Pin.OPENEMIT][Pin.OUTPUT] = cls.ERROR
        cls._erc_matrix[Pin.OPENEMIT][Pin.BIDIR] = cls.WARNING
        cls._erc_matrix[Pin.OPENEMIT][Pin.TRISTATE] = cls.WARNING
        cls._erc_matrix[Pin.OPENEMIT][Pin.UNSPEC] = cls.WARNING
        cls._erc_matrix[Pin.OPENEMIT][Pin.PWROUT] = cls.ERROR
        cls._erc_matrix[Pin.NOCONNECT][Pin.INPUT] = cls.ERROR
        cls._erc_matrix[Pin.NOCONNECT][Pin.OUTPUT] = cls.ERROR
        cls._erc_matrix[Pin.NOCONNECT][Pin.BIDIR] = cls.ERROR
        cls._erc_matrix[Pin.NOCONNECT][Pin.TRISTATE] = cls.ERROR
        cls._erc_matrix[Pin.NOCONNECT][Pin.PASSIVE] = cls.ERROR
        cls._erc_matrix[Pin.NOCONNECT][Pin.UNSPEC] = cls.ERROR
        cls._erc_matrix[Pin.NOCONNECT][Pin.PWRIN] = cls.ERROR
        cls._erc_matrix[Pin.NOCONNECT][Pin.PWROUT] = cls.ERROR
        cls._erc_matrix[Pin.NOCONNECT][Pin.OPENCOLL] = cls.ERROR
        cls._erc_matrix[Pin.NOCONNECT][Pin.OPENEMIT] = cls.ERROR
        cls._erc_matrix[Pin.NOCONNECT][Pin.NOCONNECT] = cls.ERROR

        # Fill-in the other half of the symmetrical matrix.
        for c in range(1, 11):
            for r in range(c):
                cls._erc_matrix[r][c] = cls._erc_matrix[c][r]

        # Setup the error/warning logger.
        global erc_logger
        erc_logger = logging.getLogger('ERC_Logger')
        log_level = logging.WARNING

        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.WARNING)
        handler.setFormatter(logging.Formatter(
            'ERC %(levelname)s: %(message)s'))
        erc_logger.addHandler(handler)

        scr_name = _get_script_name()
        handler = logging.StreamHandler(open(scr_name + '.erc', 'w'))
        handler.setLevel(log_level)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        erc_logger.addHandler(handler)

        erc_logger.setLevel(log_level)
        erc_logger.error = _CountCalls(erc_logger.error)
        erc_logger.warning = _CountCalls(erc_logger.warning)

    @classmethod
    def set_pin_conflict_rule(cls, pin1_func, pin2_func, conflict_level):
        """
        Set the level of conflict for two types of pins on the same net.

        Args:
            pin1_func: The function of the first pin (e.g., Pin.OUTPUT).
            pin2_func: The function of the second pin (e.g., Pin.TRISTATE).
            conflict_level: Severity of conflict (e.g., cls.OK, cls.WARNING, cls.ERROR).
        """

        # Place the conflict level into the symmetrical ERC matrix.
        cls._erc_matrix[pin1_func][pin2_func] = conflict_level
        cls._erc_matrix[pin2_func][pin1_func] = conflict_level

    @classmethod
    def _erc_pin_to_pin_chk(cls, pin1, pin2):
        """Check for conflict between two pins on a net."""

        # Use the functions of the two pins to index into the ERC table
        # and see if the pins are compatible (e.g., an input and an output)
        # or incompatible (e.g., a conflict because both are outputs).
        return cls._erc_matrix[pin1.func][pin2.func]

    @classmethod
    def _ERC(cls):
        """
        Do an electrical rules check on the circuit.
        """

        cls._erc_setup()

        # Check the nets for errors.
        for net in cls.nets:
            net._erc()

        # Check the parts for errors.
        for part in cls.parts:
            part._erc()

        if (erc_logger.error.count, erc_logger.warning.count) == (0, 0):
            sys.stderr.write('\nNo ERC errors or warnings found.\n\n')
        else:
            sys.stderr.write('\n{} warnings found during ERC.\n'.format(
                erc_logger.warning.count))
            sys.stderr.write('{} errors found during ERC.\n\n'.format(
                erc_logger.error.count))

    @classmethod
    def _generate_netlist(cls, file=None, tool=KICAD):
        """
        Return a netlist as a string and also write it to a file/stream.

        Args:
            file: Either a file object that can be written to, or a string
                containing a file name, or None.

        Returns:
            A string containing the netlist.
        """
        try:
            gen_func = cls.__dict__['_gen_netlist_{}'.format(tool)]
            netlist = gen_func(cls)
        except KeyError:
            logger.error(
                "Can't generate netlist in an unknown ECAD tool format ({}).".format(
                    tool))
            raise Exception

        if (logger.error.count, logger.warning.count) == (0, 0):
            sys.stderr.write(
                '\nNo errors or warnings found during netlist generation.\n\n')
        else:
            sys.stderr.write(
                '\n{} warnings found during netlist generation.\n'.format(
                    logger.warning.count))
            sys.stderr.write(
                '{} errors found during netlist generation.\n\n'.format(
                    logger.error.count))

        try:
            with file as f:
                f.write(netlist)
        except AttributeError:
            try:
                with open(file, 'w') as f:
                    f.write(netlist)
            except (FileNotFoundError, TypeError):
                with open(_get_script_name() + '.net', 'w') as f:
                    f.write(netlist)
        return netlist

    def _gen_netlist_kicad(self):
        scr_dict = _scriptinfo()
        src_file = os.path.join(scr_dict['dir'], scr_dict['source'])
        date = time.strftime('%m/%d/%Y %I:%M %p')
        tool = 'SKiDL (' + __version__ + ')'
        netlist = ('''(export (version D)
  (design
    (source "{src_file}")
    (date "{date}")
    (tool "{tool}"))\n'''.format(src_file=src_file,
                                 date=date,
                                 tool=tool))
        netlist += "  (components"
        for p in SubCircuit.parts:
            comp_txt = p._generate_netlist_component(KICAD)
            netlist += '\n' + comp_txt
        netlist += ")\n"
        netlist += "  (nets"
        for code, n in enumerate(SubCircuit._get_nets()):
            n.code = code
            netlist += '\n' + n._generate_netlist_net(KICAD)
        netlist += ")\n)\n"
        return netlist


def search(name):
    lib_dir = os.path.join(os.environ['KISYSMOD'], '..', 'library')
    lib_files = os.listdir(lib_dir)
    lib_files.extend(os.listdir('.'))
    lib_files = [l for l in lib_files if l.endswith('.lib')]
    parts = []
    for lib_file in lib_files:
        lib = _SchLib(lib_file)

        def mk_list(l):
            if isinstance(l, (list, tuple)):
                return l
            if not l:
                return []
            return [l]

        for p in mk_list(lib.get_parts(name=name)):
            p._parse()
            parts.append((lib_file, p))
        for p in mk_list(lib.get_parts(alias=name)):
            p._parse()
            parts.append((lib_file, p))
    for lib_file, p in parts:
        print('{}: {}'.format(lib_file, p.name))


def show(lib_file, name):
    print(Part(lib_file, name))


Circuit = SubCircuit

ERC = SubCircuit._ERC
generate_netlist = SubCircuit._generate_netlist

POWER = Pin.POWER_DRIVE

# This is a NOCONNECT net for attaching to pins which are intentionally left open.
NC = _NCNet('NOCONNECT')
