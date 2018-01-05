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

"""
SKiDL: A Python-Based Schematic Design Language

This module extends Python with the ability to design electronic
circuits. It provides classes for working with **1)** electronic parts (``Part``),
**2)** collections of part terminals (``Pin``) connected via wires (``Net``), and
**3)** groups of related nets (``Bus``). Using these classes, you can
concisely describe the interconnection of components using a linear
and/or hierarchical structure. It also provides the capability to
check the resulting circuitry for the violation of electrical rules.
The output of a SKiDL-enabled Python script is a netlist that can be
imported into a PCB layout tool.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import super  # pylint: disable=redefined-builtin
from builtins import open  # pylint: disable=redefined-builtin
from builtins import int  # pylint: disable=redefined-builtin
from builtins import dict  # pylint: disable=redefined-builtin
from builtins import str  # pylint: disable=redefined-builtin
from builtins import zip  # pylint: disable=redefined-builtin
from builtins import range  # pylint: disable=redefined-builtin
from builtins import object  # pylint: disable=redefined-builtin
from future import standard_library
standard_library.install_aliases()

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

import sys
import os
import os.path
import re
import collections
import shlex
import inspect
from copy import deepcopy, copy
import time
import graphviz

from .pckg_info import __version__
from .py_2_3 import *  # pylint: disable=wildcard-import
from .utilities import *  # pylint: disable=wildcard-import


# Places where parts can be stored.
#   NETLIST: The part will become part of a circuit netlist.
#   LIBRARY: The part will be placed in the part list for a library.
#   TEMPLATE: The part will be used as a template to be copied from.
NETLIST, LIBRARY, TEMPLATE = ['NETLIST', 'LIBRARY', 'TEMPLATE']

# Prefixes for implicit nets and buses.
NET_PREFIX = 'N$'
BUS_PREFIX = 'B$'

# Supported ECAD tools.
KICAD, SKIDL = ['kicad', 'skidl']
DEFAULT_TOOL = KICAD


##############################################################################

# These are the paths to search for part libraries of the ECAD tools.
# Start off with a path that allows absolute file names, and then searches
# within the current directory.
lib_search_paths = {
    KICAD: ['', '.'],
    SKIDL: ['', '.']
}

# Add the location of the default KiCad schematic part libs to the search path.
try:
    lib_search_paths[KICAD].append(os.path.join(os.environ['KISYSMOD'], '..', 'library'))
except KeyError:
    logging.warning("KISYSMOD environment variable is missing, so default KiCad libraries won't be searched.")

# Add the location of the default SKiDL part libraries.
import skidl.libs
lib_search_paths[SKIDL].append( skidl.libs.__path__[0])

lib_suffixes = {
    KICAD: '.lib',
    SKIDL: '_sklib.py'
}


##############################################################################


# Definitions for backup library of circuit parts.
BACKUP_LIB_NAME = get_script_name() + '_lib'
BACKUP_LIB_FILE_NAME = BACKUP_LIB_NAME + lib_suffixes[SKIDL]
QUERY_BACKUP_LIB = True
CREATE_BACKUP_LIB = True
backup_lib = None


# Set up logging.
logger = create_logger('skidl')


def _expand_buses(pins_nets_buses):
    """
    Take list of pins, nets, and buses and return a list of only pins and nets.
    """
    pins_nets = []
    for pnb in pins_nets_buses:
        if isinstance(pnb, Bus):
            pins_nets.extend(pnb.get_nets())
        else:
            pins_nets.append(pnb)
    return pins_nets


##############################################################################


class SchLib(object):
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

    def __init__(self, filename=None, tool=None, **attribs):
        """
        Load the parts from a library file.
        """

        if tool is None:
            tool = DEFAULT_TOOL

        # Library starts off empty of parts.
        self.parts = []

        # Attach attributes to the library.
        for k, v in attribs.items():
            setattr(self, k, v)

        # If no filename, create an empty library.
        if not filename:
            pass

        # Load this SchLib with an existing SchLib object if the file name
        # matches one in the cache.
        elif filename in self._cache:
            self.__dict__.update(self._cache[filename].__dict__)

        # Otherwise, load from a schematic library file.
        else:
            try:
                # Use the tool name to find the function for loading the library.
                load_func = getattr(self, '_load_sch_lib_{}'.format(tool))
                load_func(filename, lib_search_paths[tool])
                self.filename = filename
                # Cache a reference to the library.
                self._cache[filename] = self
            except AttributeError:
                # OK, that didn't work so well...
                logger.error('Unsupported ECAD tool library: {}.'.format(tool))
                raise Exception

    @classmethod
    def _reset(cls):
        cls._cache = {}

    def _load_sch_lib_kicad(self, filename=None, lib_search_paths_=None):
        """
        Load the parts from a KiCad schematic library file.

        Args:
            filename: The name of the KiCad schematic library file.
        """

        # Try to open the file. Add a .lib extension if needed. If the file
        # doesn't open, then try looking in the KiCad library directory.
        f = find_and_open_file(filename, lib_search_paths_, lib_suffixes[KICAD], allow_failure=True)
        if not f:
            logger.warning('Unable to open KiCad Schematic Library File {}.\n'.format(filename))
            return

        # Check the file header to make sure it's a KiCad library.
        header = []
        header = [f.readline()]
        if header and 'EESchema-LIBRARY' not in header[0]:
            logger.error(
                'The file {} is not a KiCad Schematic Library File.\n'.format(
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
                    self.add_parts(Part(part_defn=part_defn, tool=KICAD, dest=LIBRARY))

                    # Clear the part definition in preparation for the next one.
                    part_defn = []

        # Now add information from any associated DCM file.
        filename = os.path.splitext(filename)[0] # Strip any extension.
        f = find_and_open_file(filename, lib_search_paths_, '.dcm', allow_failure=True)
        if not f:
            return

        part_desc = {}
        for line in f.readlines():

            # Skip over comments.
            if line.startswith('#'):
                pass

            # Look for the start of a part description.
            elif line.startswith('$CMP'):
                part_desc['name'] = line.split()[-1]

            # If gathering the part definition has begun, then continue adding lines.
            elif part_desc:
                if line.startswith('D'):
                    part_desc['description'] = ' '.join(line.split()[1:])
                elif line.startswith('K'):
                    part_desc['keywords'] = ' '.join(line.split()[1:])
                elif line.startswith('$ENDCMP'):
                    try:
                        part = self.get_part_by_name(part_desc['name'], silent=True)
                    except Exception:
                        pass
                    else:
                        part.description = part_desc.get('description', '')
                        part.keywords = part_desc.get('keywords', '')
                    part_desc = {}
                else:
                    pass

    def _load_sch_lib_skidl(self, filename=None, lib_search_paths_=None):
        """
        Load the parts from a SKiDL schematic library file.

        Args:
            filename: The name of the SKiDL schematic library file.
        """

        f = find_and_open_file(filename, lib_search_paths_, lib_suffixes[SKIDL], allow_failure=True)
        if not f:
            logger.warning('Unable to open SKiDL Schematic Library File {}.\n'.format(filename))
            return
        try:
            # The SKiDL library is stored as a Python module that's executed to
            # recreate the library object.
            vars_ = {}  # Empty dictionary for storing library object.
            exec(f.read(), vars_)  # Execute and store library in dict.

            # Now look through the dict to find the library object.
            for val in vars_.values():
                if isinstance(val, SchLib):
                    # Overwrite self with the new library.
                    self.__dict__.update(val.__dict__)
                    return

            # Oops! No library object. Something went wrong.
            raise Exception('No SchLib object found in {}'.format(filename))

        except Exception as e:
            logger.error('Problem with {}'.format(f))
            logger.error(e)
            raise Exception

    def add_parts(self, *parts):
        """Add one or more parts to a library."""
        for part in flatten(parts):
            # Parts with the same name are not allowed in the library.
            # Also, do not check the backup library to see if the parts
            # are in there because that's probably a different library.
            if not self.get_parts(use_backup_lib=False, name=re.escape(part.name)):
                self.parts.append(part.copy(dest=TEMPLATE))
        return self

    __iadd__ = add_parts

    def get_parts(self, use_backup_lib=True, **criteria):
        """
        Return parts from a library that match *all* the given criteria.

        Keyword Args:
            criteria: One or more keyword-argument pairs. The keyword specifies
                the attribute name while the argument contains the desired value
                of the attribute.

        Returns:
            A single Part or a list of Parts that match all the criteria.
        """
        parts = list_or_scalar(filter_list(self.parts, **criteria))
        if not parts and use_backup_lib and QUERY_BACKUP_LIB:
            try:
                backup_lib_ = load_backup_lib()
                parts = backup_lib_.get_parts(use_backup_lib=False, **criteria)
            except AttributeError:
                pass
        return parts

    def get_part_by_name(self, name, allow_multiples=False, silent=False):
        """
        Return a Part with the given name or alias from the part list.

        Args:
            name: The part name or alias to search for in the library.
            allow_multiples: If true, return a list of parts matching the name.
                If false, return only the first matching part and issue
                a warning if there were more than one.
            silent: If true, don't issue errors or warnings.

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
                if not silent:
                    logger.error('Unable to find part {} in library {}.'.format(
                        name, getattr(self, 'filename', 'UNKNOWN')))
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
                if not silent:
                    logger.warning(
                        'Found multiple parts matching {}. Selecting {}.'.format(
                            name, parts[0].name))
                parts = parts[0]
                parts.parse()

        # Only a single matching part was found, so return that.
        else:
            parts.parse()

        # Return the library part or parts that were found.
        return parts

    # Get part by name or alias using []'s.
    __getitem__ = get_part_by_name

    def __str__(self):
        """Return a list of the part names in this library as a string."""
        return '\n'.join(['{}: {}'.format(p.name, p.description) for p in self.parts])

    __repr__ = __str__

    def export(self, libname, file=None, tool=None):
        """
        Export a library into a file.

        Args:
            libname: A string containing the name of the library.
            file: The file the library will be exported to. It can either
                be a file object or a string or None. If None, the file
                will be the same as the library name with the library
                suffix appended.
            tool: The CAD tool library format to be used. Currently, this can
                only be SKIDL.
        """

        def prettify(s):
            """Breakup and indent library export string."""
            s = re.sub(r'(Part\()', r'\n        \1', s)
            s = re.sub(r'(Pin\()', r'\n            \1', s)
            return s

        if tool is None:
            tool = SKIDL

        if not file:
            file = libname + lib_suffixes[tool]

        export_str = 'from skidl import Pin, Part, SchLib, SKIDL, TEMPLATE\n\n'
        export_str += "SKIDL_lib_version = '0.0.1'\n\n"
        part_export_str = ','.join([p.export() for p in self.parts])
        export_str += '{} = SchLib(tool=SKIDL).add_parts(*[{}])'.format(
                        cnvt_to_var_name(libname), part_export_str)
        export_str = prettify(export_str)
        try:
            file.write(export_str)
        except AttributeError:
            with open(file, 'w') as f:
                f.write(export_str)

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
                'func_str': 'INPUT',
                'drive': NO_DRIVE,
                'max_rcv': POWER_DRIVE,
                'min_rcv': PASSIVE_DRIVE, },
        OUTPUT: {'function': 'OUTPUT',
                 'func_str': 'OUTPUT',
                 'drive': PUSHPULL_DRIVE,
                 'max_rcv': PASSIVE_DRIVE,
                 'min_rcv': NO_DRIVE, },
        BIDIR: {'function': 'BIDIRECTIONAL',
                'func_str': 'BIDIR',
                'drive': TRISTATE_DRIVE,
                'max_rcv': POWER_DRIVE,
                'min_rcv': NO_DRIVE, },
        TRISTATE: {'function': 'TRISTATE',
                   'func_str': 'TRISTATE',
                   'drive': TRISTATE_DRIVE,
                   'max_rcv': TRISTATE_DRIVE,
                   'min_rcv': NO_DRIVE, },
        PASSIVE: {'function': 'PASSIVE',
                  'func_str': 'PASSIVE',
                  'drive': PASSIVE_DRIVE,
                  'max_rcv': POWER_DRIVE,
                  'min_rcv': NO_DRIVE, },
        UNSPEC: {'function': 'UNSPECIFIED',
                 'func_str': 'UNSPEC',
                 'drive': NO_DRIVE,
                 'max_rcv': POWER_DRIVE,
                 'min_rcv': NO_DRIVE, },
        PWRIN: {'function': 'POWER-IN',
                'func_str': 'PWRIN',
                'drive': NO_DRIVE,
                'max_rcv': POWER_DRIVE,
                'min_rcv': POWER_DRIVE, },
        PWROUT: {'function': 'POWER-OUT',
                 'func_str': 'PWROUT',
                 'drive': POWER_DRIVE,
                 'max_rcv': PASSIVE_DRIVE,
                 'min_rcv': NO_DRIVE, },
        OPENCOLL: {'function': 'OPEN-COLLECTOR',
                   'func_str': 'OPENCOLL',
                   'drive': ONESIDE_DRIVE,
                   'max_rcv': TRISTATE_DRIVE,
                   'min_rcv': NO_DRIVE, },
        OPENEMIT: {'function': 'OPEN-EMITTER',
                   'func_str': 'OPENEMIT',
                   'drive': ONESIDE_DRIVE,
                   'max_rcv': TRISTATE_DRIVE,
                   'min_rcv': NO_DRIVE, },
        NOCONNECT: {'function': 'NO-CONNECT',
                    'func_str': 'NOCONNECT',
                    'drive': NOCONNECT_DRIVE,
                    'max_rcv': NOCONNECT_DRIVE,
                    'min_rcv': NOCONNECT_DRIVE, },
    }

    def __init__(self, **attribs):
        self.nets = []
        self.part = None
        self.name = ''
        self.num = ''
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

        return list_or_scalar(copies)

    # Make copies with the multiplication operator or by calling the object.
    __mul__ = copy
    __rmul__ = copy
    __call__ = copy

    def is_connected(self):
        """Return true if a pin is connected to a net (but not a no-connect net)."""
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
        if set([Net, _NCNet]) == net_types:
            # Can't be connected to both normal and no-connect nets!
            logger.error('{} is connected to both normal and no-connect nets!'.format(self._erc_desc()))
            raise Exception
        # This is just strange...
        logger.error("{} is connected to something strange: {}.".format(
            self._erc_desc(), self.nets))
        raise Exception

    def is_attached(self, pin_net_bus):
        """Return true if this pin is attached to the given pin, net or bus."""
        if not self.is_connected():
            return False
        if isinstance(pin_net_bus, Pin):
            if pin_net_bus.is_connected():
                return pin_net_bus.net.is_attached(self.net)
            else:
                return False
        if isinstance(pin_net_bus, Net):
            return pin_net_bus.is_attached(self.net)
        if isinstance(pin_net_bus, Bus):
            for net in pin_net_bus[:]:
                if self.net.is_attached(net):
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
        for pn in _expand_buses(flatten(pins_nets_buses)):
            if isinstance(pn, Pin):
                # Connecting pin-to-pin.
                if self.is_connected():
                    # If self is already connected to a net, then add the
                    # other pin to the same net.
                    self.nets[0] += pn
                elif pn.is_connected():
                    # If self is unconnected but the other pin is, then
                    # connect self to the other pin's net.
                    pn.nets[0] += self
                else:
                    # Neither pin is connected to a net, so create a net
                    # in the same circuit as the pin and attach both to it.
                    Net(circuit=self.part.circuit).connect(self, pn)
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

    # Connect a net to a pin using the += operator.
    __iadd__ = connect

    def _disconnect(self):
        """Disconnect this pin from all nets."""
        if not self.net:
            return
        for n in self.nets:
            n._disconnect(self)
        self.nets = []

    def get_nets(self):
        """Return a list containing the Net objects connected to this pin."""
        return self.nets

    def _get_pins(self):
        """Return a list containing this pin."""
        return to_list(self)

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
            ref=part_ref,
            num=pin_num,
            name=pin_name,
            func=pin_func_str)

    __repr__ = __str__

    def export(self):
        """Return a string to recreate a Pin object."""
        attribs = []
        for k in ['num', 'name', 'func', 'do_erc']:
            v = getattr(self, k, None)
            if v:
                if k == 'func':
                    # Assign the pin function using the actual name of the
                    # function, not its numerical value (in case that changes
                    # in the future if more pin functions are added).
                    v = 'Pin.' + Pin.pin_info[v]['func_str']
                else:
                    v = repr(v)
                attribs.append('{}={}'.format(k, v))
        return 'Pin({})'.format(','.join(attribs))

    @property
    def net(self):
        """Return one of the nets the pin is connected to."""
        if self.nets:
            return self.nets[0]
        return None

##############################################################################


class PhantomPin(Pin):
    """
    A pin type that exists solely to tie two pinless nets together.
    It will not participate in generating any netlists.
    """

    def __init__(self, **attribs):
        super(PhantomPin, self).__init__(**attribs)
        self.nets = []
        self.part = None
        self.do_erc = False


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
            (fullmatch(str(search.name), str(self.name), flags=re.IGNORECASE) or
             fullmatch(str(self.name), str(search.name), flags=re.IGNORECASE))

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

        if tool is None:
            tool = DEFAULT_TOOL

        # Setup some part attributes that might be overwritten later on.
        self.do_erc = True # Allow part to be included in ERC.
        self.unit = {} # Dictionary for storing subunits of the part, if desired.
        self.pins = [] # Start with no pins, but a place to store them.
        self.name = name # Assign initial part name. (Must come after circuit is assigned.)
        self.description = '' # Make sure there is a description, even if empty.
        self._ref = '' # Provide a member for holding a reference.
        self.ref_prefix = '' # Provide a member for holding the part reference prefix.
        self.tool = tool # Initial type of part (SKIDL, KICAD, etc.)
        self.circuit = None # Part starts off unassociated with any circuit.

        # Create a Part from a library entry.
        if lib:
            # If the lib argument is a string, then create a library using the
            # string as the library file name.
            if isinstance(lib, basestring):
                lib = SchLib(filename=lib, tool=tool)

            # Make a copy of the part from the library but don't add it to the netlist.
            part = lib[name].copy(1, TEMPLATE)

            # Overwrite self with the new part.
            self.__dict__.update(part.__dict__)

            # Make sure all the pins have a valid reference to this part.
            self._associate_pins()

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
                "Can't make a part without a library & part name or a part definition.")
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
            parse_func = getattr(self, 'parse_{}'.format(self.tool))
            parse_func(just_get_name)
        except AttributeError:
            logger.error(
                "Can't create a part with an unknown ECAD tool file format: {}.".format(
                    self.tool))
            raise Exception

    def parse_kicad(self, just_get_name=False):
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

        # Always make sure there are drawing & footprint sections, even if the part doesn't have them.
        self.draw = {
            'arcs': [],
            'circles': [],
            'polylines': [],
            'rectangles': [],
            'texts': [],
            'pins': []
        }
        self.fplist = []

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

            # End the parsing of the part definition.
            elif line[0] == 'ENDDEF':
                break

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

            # End the list of part footprints.
            elif line[0] == '$ENDFPLIST':
                building_fplist = False

            # Start gathering the drawing primitives for the part symbol.
            elif line[0] == 'DRAW':
                building_draw = True

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
                    elif line[0] == 'C':
                        self.draw['circles'].append(dict(list(zip(_CIRCLE_KEYS,
                                                                  values))))

                    # Gather polygons.
                    elif line[0] == 'P':
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
                    elif line[0] == 'S':
                        self.draw['rectangles'].append(dict(list(zip(
                            _RECT_KEYS, values))))

                    # Gather text.
                    elif line[0] == 'T':
                        self.draw['texts'].append(dict(list(zip(_TEXT_KEYS,
                                                                values))))

                    # Gather the pin symbols. This is what we really want since
                    # this defines the names, numbers and attributes of the
                    # pins associated with the part.
                    elif line[0] == 'X':
                        self.draw['pins'].append(dict(list(zip(_PIN_KEYS,
                                                               values))))

                    # Found something unknown in the drawing section.
                    else:
                        msg = 'Found something strange in {} symbol drawing: {}.'.format(self.name, line)
                        logger.warning(msg)

                # Found something unknown outside the footprint list or drawing section.
                else:
                    msg = 'Found something strange in {} symbol definition: {}.'.format(self.name, line)
                    logger.warning(msg)

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
            p = Pin()  # Create a blank pin.

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
            p.func = pin_type_translation[p.electrical_type]  # pylint: disable=no-member

            return p

        self.pins = [kicad_pin_to_pin(p) for p in self.draw['pins']]

        # Make sure all the pins have a valid reference to this part.
        self._associate_pins()

        # Part definition has been parsed, so clear it out. This prevents a
        # part from being parsed more than once.
        self.part_defn = None

    def parse_skidl(self, just_get_name=False):
        """
        Create a Part using a part definition from a SKiDL library.
        """

        # Parts in a SKiDL library are already parsed and ready for use,
        # so just return the part.
        return self


    def _associate_pins(self):
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

        num_copies = max(num_copies, find_num_copies(**attribs))

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
            cpy.pins = []
            for p in getattr(self, 'pins', None):
                cpy.pins.append(p.copy())

            # Make sure all the pins have a reference to this new part copy.
            cpy._associate_pins()

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
                            "{} copies of part {} were requested, but too few elements in attribute {}!".format(
                                num_copies, self.name, k))
                        raise Exception
                setattr(cpy, k, v)

            # Add the part copy to the list of copies.
            copies.append(cpy)

        return list_or_scalar(copies)

    """Make copies with the multiplication operator or by calling the object."""
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

        # If no pin identifiers were given, then use a wildcard that will
        # select all pins.
        if not pin_ids:
            pin_ids = ['.*']

        # Determine the minimum and maximum pin ids if they don't already exist.
        if 'min_pin' not in dir(self) or 'max_pin' not in dir(self):
            self.min_pin, self.max_pin = self._find_min_max_pins()

        # Go through the list of pin IDs one-by-one.
        pins = _NetPinList()
        for p_id in expand_indices(self.min_pin, self.max_pin, *pin_ids):

            # Does pin ID (either integer or string) match a pin number...
            tmp_pins = filter_list(self.pins, num=str(p_id), **criteria)
            if tmp_pins:
                pins.extend(tmp_pins)
                continue

            # OK, pin ID is not a pin number. Does it match a substring
            # within a pin name or alias?
            loose_p_id = ''.join(['.*', p_id, '.*'])
            pins.extend(filter_list(self.pins, name=loose_p_id, **criteria))
            loose_pin_alias = Alias(loose_p_id, id(self))
            pins.extend(filter_list(self.pins, alias=loose_pin_alias, **criteria))

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

    def _is_movable(self):
        """
        Return T/F if the part can be moved from one circuit into another.

        This method returns true if:
            1) the part is not in a circuit, or
            2) the part has pins but none of them are connected to nets, or
            3) the part has no pins (which can be the case for mechanical parts,
               silkscreen logos, or other non-electrical schematic elements).
        """
        return not isinstance(self.circuit, Circuit) or not self.is_connected() or not self.pins

    def set_pin_alias(self, alias, *pin_ids, **criteria):
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
            logger.warning("Using a label ({}) for a unit of {} that matches one or more of it's pin names ({})!".format(label, self._erc_desc(), collisions))
        self.unit[label] = PartUnit(self, *pin_ids, **criteria)
        return self.unit[label]

    def _get_fields(self):
        """
        Return a list of component field names.
        """

        # Get all the component attributes and subtract all the ones that
        # should not appear under "fields" in the netlist or XML.
        fields = set(self.__dict__.keys())
        non_fields = set(['name', 'min_pin', 'max_pin', 'hierarchy', '_value',
                      '_ref', 'ref_prefix', 'unit', 'num_units', 'part_defn',
                      'definition', 'fields', 'draw', 'lib', 'fplist',
                      'do_erc', 'aliases', 'tool', 'pins', 'footprint', 'circuit'])
        return list(fields-non_fields)

    def _generate_netlist_component(self, tool=None):
        """
        Generate the part information for inclusion in a netlist.

        Args:
            tool: The format for the netlist file (e.g., KICAD).
        """

        if tool is None:
            tool = DEFAULT_TOOL

        try:
            gen_func = getattr(self, '_gen_netlist_comp_{}'.format(tool))
            return gen_func()
        except AttributeError:
            logger.error(
                "Can't generate netlist in an unknown ECAD tool format ({}).".format(
                    tool))
            raise Exception

    def _gen_netlist_comp_kicad(self):
        ref = add_quotes(self.ref)

        try:
            value = self.value
            if not value:
                value = self.name
        except AttributeError:
            try:
                value = self.name
            except AttributeError:
                value = self.ref_prefix
        value = add_quotes(value)

        try:
            footprint = self.footprint
        except AttributeError:
            logger.error('No footprint for {part}/{ref}.'.format(
                part=self.name, ref=ref))
            footprint = 'No Footprint'
        footprint = add_quotes(footprint)

        lib = add_quotes(getattr(self, 'lib', 'NO_LIB'))
        name = add_quotes(self.name)

        fields = ''
        for fld_name in self._get_fields():
            fld_value = add_quotes(self.__dict__[fld_name])
            if fld_value:
                fld_name = add_quotes(fld_name)
                fields += '\n        (field (name {fld_name}) {fld_value})'.format(**locals())
        if fields:
            fields = '      (fields' + fields
            fields += ')\n'

        template = '    (comp (ref {ref})\n' + \
                   '      (value {value})\n' + \
                   '      (footprint {footprint})\n' + \
                   '{fields}' + \
                   '      (libsource (lib {lib}) (part {name})))'
        txt = template.format(**locals())
        return txt

    def _generate_xml_component(self, tool=None):
        """
        Generate the part information for inclusion in an XML file.

        Args:
            tool: The format for the XML file (e.g., KICAD).
        """

        if tool is None:
            tool = DEFAULT_TOOL

        try:
            gen_func = getattr(self, '_gen_xml_comp_{}'.format(tool))
            return gen_func()
        except AttributeError:
            logger.error(
                "Can't generate XML in an unknown ECAD tool format ({}).".format(tool))
            raise Exception

    def _gen_xml_comp_kicad(self):
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

        lib = add_quotes(getattr(self, 'lib', 'NO_LIB'))
        name = self.name

        fields = ''
        for fld_name in self._get_fields():
            fld_value = self.__dict__[fld_name]
            if fld_value:
                fields += '\n        <field name="{fld_name}">{fld_value}</field>'.format(**locals())
        if fields:
            fields = '      <fields>' + fields
            fields += '\n      </fields>\n'

        template = '    <comp ref="{ref}">\n' + \
                   '      <value>{value}</value>\n' + \
                   '      <footprint>{footprint}</footprint>\n' + \
                   '{fields}' + \
                   '      <libsource lib="{lib}" part="{name}"/>\n' + \
                   '    </comp>'
        txt = template.format(**locals())
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
        return '\n' + self.name + ': ' + self.description + '\n    ' + '\n    '.join(
            [p.__str__() for p in self.pins])

    __repr__ = __str__

    def export(self):
        """Return a string to recreate a Part object."""
        keys = self._get_fields()
        keys.extend(('ref_prefix', 'num_units', 'fplist', 'do_erc', 'aliases', 'pin', 'footprint'))
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
        return 'Part({})'.format(','.join(attribs))


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
        self._ref = get_unique_name(self.circuit.parts, 'ref', self.ref_prefix, r)
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
        except AttributeError:
            # If part has no value, return its part name as the value. This is
            # done in KiCad where a resistor value is set to 'R' if no
            # explicit value was set.
            return self.name

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


class SkidlPart(Part):
    """
    A class for storing a SKiDL definition of a schematic part. It's identical
    to its Part superclass except:
        *) The tool defaults to SKIDL.
        *) The destination defaults to TEMPLATE so that it's easier to start
           a part and then add pins to it without it being added to the netlist.
    """

    def __init__(self,
                 lib=None,
                 name=None,
                 dest=TEMPLATE,
                 tool=SKIDL,
                 connections=None,
                 **attribs):
        super(SkidlPart, self).__init__(lib, name, dest, tool, connections, attribs)


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

##############################################################################


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
        self._valid = True # Make net valid before doing anything else.
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

    def _get_pins(self):
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

    def _is_movable(self):
        """
        Return true if the net is movable to another circuit.

        A net is movable if it's not part of a Circuit or if there are no pins
        attached to it.
        """
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
                            "{} copies of net {} were requested, but too few elements in attribute {}!".format(
                                num_copies, self.name, k))
                        raise Exception
                setattr(cpy, k, v)

            # Place the copy into the list of copies.
            copies.append(cpy)

        return list_or_scalar(copies)

    """Make copies with the multiplication operator or by calling the object."""
    __mul__ = copy
    __rmul__ = copy
    __call__ = copy

    def _is_implicit(self, net_name=None):
        """Return true if the net name is implicit."""
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
                    pin._disconnect()
                self.pins.append(pin)
                pin.nets.append(self)
            return

        self.test_validity()

        # Go through all the pins and/or nets and connect them to this net.
        for pn in _expand_buses(flatten(pins_nets_buses)):
            if isinstance(pn, Net):
                if pn.circuit == self.circuit:
                    merge(pn)
                else:
                    logger.error("Can't attach nets in different circuits ({}, {})!".format(pn.circuit.name, self.circuit.name))
                    raise Exception
            elif isinstance(pn, Pin):
                if not pn.part or pn.part.circuit == self.circuit:
                    if not pn.part:
                        logger.warning("Attaching non-part Pin {} to a Net {}.".format(pn.name, self.name))
                    connect_pin(pn)
                else:
                    logger.error("Can't attach a part to a net in different circuits ({}, {})!".format(pn.part.circuit.name, self.circuit.name))
                    raise Exception
            else:
                logger.error(
                    'Cannot attach non-Pin/non-Net {} to Net {}.'.format(type(pn), self.name))
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
                if self._is_implicit(name1):
                    return nets[0]
                if self._is_implicit(name0):
                    return nets[1]
                logger.warning('Merging two named nets ({name0} and {name1}) into {name0}.'.format(**locals()))
                return nets[0]

            # More than two nets, so bisect the list into two smaller lists and
            # recursively find the best name from each list and then return the
            # best name of those two.
            mid_point = len(nets) // 2
            return select_name([select_name(nets[0:mid_point]), select_name(nets[mid_point:])])

        # Assign the same name to all the nets that are connected to this net.
        nets = self._traverse().nets
        selected_name = getattr(select_name(self._traverse().nets), 'name')
        for net in nets:
            # Assign the name directly to each net. Using the name property
            # would cause the names to be changed so they were unique.
            net._name = selected_name

        # Add the net to the global netlist. (It won't be added again
        # if it's already there.)
        self.circuit += self

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

    def _generate_netlist_net(self, tool=None):
        """
        Generate the net information for inclusion in a netlist.

        Args:
            tool: The format for the netlist file (e.g., KICAD).
        """

        if tool is None:
            tool = DEFAULT_TOOL

        self.test_validity()

        # Don't add anything to the netlist if no pins are on this net.
        if not self._get_pins():
            return

        try:
            gen_func = getattr(self, '_gen_netlist_net_{}'.format(tool))
            return gen_func()
        except AttributeError:
            logger.error(
                "Can't generate netlist in an unknown ECAD tool format ({}).".format(
                    tool))
            raise Exception

    def _gen_netlist_net_kicad(self):
        code = add_quotes(self.code)
        name = add_quotes(self.name)
        txt = '    (net (code {code}) (name {name})'.format(**locals())
        for p in sorted(self._get_pins(), key=lambda p: str(p)):
            part_ref = add_quotes(p.part.ref)
            pin_num = add_quotes(p.num)
            txt += '\n      (node (ref {part_ref}) (pin {pin_num}))'.format(**locals())
        txt += ')'
        return txt

    def _generate_xml_net(self, tool=None):
        """
        Generate the net information for inclusion in an XML file.

        Args:
            tool: The format for the XML file (e.g., KICAD).
        """

        if tool is None:
            tool = DEFAULT_TOOL

        self.test_validity()

        # Don't add anything to the XML if no pins are on this net.
        if not self._get_pins():
            return

        try:
            gen_func = getattr(self, '_gen_xml_net_{}'.format(tool))
            return gen_func()
        except AttributeError:
            logger.error(
                "Can't generate XML in an unknown ECAD tool format ({}).".format(
                    tool))
            raise Exception

    def _gen_xml_net_kicad(self):
        code = self.code
        name = self.name
        txt = '    <net code="{code}" name="{name}">'.format(**locals())
        for p in self._get_pins():
            part_ref = p.part.ref
            pin_num = p.num
            txt += '\n      <node ref="{part_ref}" pin="{pin_num}"/>'.format(**locals())
        txt += '\n    </net>'
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

            erc_result = self.circuit._erc_pin_to_pin_chk(pin1, pin2)

            # Return if the pins are compatible.
            if erc_result == Circuit.OK:
                return

            # Otherwise, generate an error or warning message.
            msg = 'Pin conflict on net {n}: {p1} <==> {p2}'.format(
                n=pin1.net.name,
                p1=pin1._erc_desc(),
                p2=pin2._erc_desc())
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
        return self.name + ': ' + ', '.join([p.__str__() for p in sorted(pins, key=lambda p: str(p))])

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
        self._name = get_unique_name(self.circuit.nets, 'name', NET_PREFIX, name)

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

    def __init__(self, name=None, circuit=None, *pins_nets_buses, **attribs):
        super(_NCNet, self).__init__(name=name, circuit=circuit, *pins_nets_buses, **attribs)
        self._drive = Pin.NOCONNECT_DRIVE

    def _generate_netlist_net(self, tool=None):
        """NO_CONNECT nets don't generate anything for netlists."""

        if tool is None:
            tool = DEFAULT_TOOL

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

        # Define the member storing the nets so it's present, but it starts empty.
        self.nets = []

        # For Bus objects, the circuit object the bus is a member of is passed
        # in with all the other attributes. If a circuit object isn't provided,
        # then the default circuit object is added to the attributes.
        attribs['circuit'] = attribs.get('circuit', default_circuit)  # pylint: disable=undefined-variable

        # Attach additional attributes to the bus. (The Circuit object also gets
        # set here.)
        for k, v in attribs.items():
            setattr(self, k, v)

        # The bus name is set after the circuit is assigned so the name can be
        # checked against the other bus names already in that circuit.
        self.name = name

        # Add the bus to the circuit.
        self.circuit = None  # Bus won't get added if it's already seen as part of circuit.
        attribs['circuit'] += self  # Add bus to circuit. This also sets self.circuit again.

        # Build the bus from net widths, existing nets, nets of pins, other buses.
        self.extend(args)

    def extend(self, *objects):
        """Extend bus by appending objects to the end (MSB)."""
        self.insert(len(self.nets), objects)

    def insert(self, index, *objects):
        """Insert objects into bus starting at indexed position."""
        for obj in flatten(objects):
            if isinstance(obj, int):
                # Add a number of new nets to the bus.
                for _ in range(obj):
                    self.nets.insert(index, Net())
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
                    # so create a new net, add it to the bus, and
                    # connect the pin to it.
                    n = Net()
                    n += obj
                    self.nets.insert(index, n)
                index += 1
            elif isinstance(obj, Bus):
                # Add an existing bus to this bus.
                for n in reversed(obj.nets):
                    self.nets.insert(index, n)
                index += len(obj)
            else:
                logger.error('Adding illegal type of object ({}) to Bus {}.'.format(type(obj), self.name))
                raise Exception

        # Assign names to all the unnamed nets in the bus.
        for i, net in enumerate(self.nets):
            if net._is_implicit():
                # Net names are the bus name with the index appended.
                net.name = self.name + str(i)

    def get_nets(self):
        """Return the list of nets contained in this bus."""
        return to_list(self.nets)

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

            cpy = Bus(self.name, self)

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

        return list_or_scalar(copies)

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
        for ident in expand_indices(0, len(self) - 1, ids):
            if isinstance(ident, int):
                nets.append(self.nets[ident])
            elif isinstance(ident, basestring):
                nets.extend(filter_list(self.nets, name=ident))
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

    def _is_movable(self):
        """
        Return true if the bus is movable to another circuit.

        A bus  is movable if all the nets in it are movable.
        """
        for n in self.nets:
            if not n._is_movable():
                # One net not movable means the entire Bus is not movable.
                return False
        return True # All the nets were movable.

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
        self._name = get_unique_name(self.circuit.buses, 'name', BUS_PREFIX, name)

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
        for item in _expand_buses(flatten(nets_pins_buses)):
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


class Circuit(object):
    """
    Class object that holds the entire netlist of parts and nets.

    Attributes:
        parts: List of all the schematic parts as Part objects.
        nets: List of all the schematic nets as Net objects.
        buses: List of all the buses as Bus objects.
        hierarchy: A '.'-separated concatenation of the names of nested
            SubCircuits at the current time it is read.
        level: The current level in the schematic hierarchy.
        context: Stack of contexts for each level in the hierarchy.
    """

    OK, WARNING, ERROR = range(3)

    def __init__(self, **kwargs):
        """Initialize the Circuit object."""
        self.reset()

        # Set passed-in attributes for the circuit.
        for k, v in kwargs.items():
            setattr(self, k, v)

    def reset(self):
        """Clear any circuitry and cached part libraries and start over."""

        # Create this member here to prevent pylint error later in mini_reset().
        self.NC = None

        # Clear circuitry.
        self.mini_reset()

        # Also clear any cached libraries.
        SchLib._reset()
        global backup_lib
        backup_lib = None

    def mini_reset(self):
        """Clear any circuitry but don't erase any loaded part libraries."""
        self.name = ''
        self.parts = []
        self.nets = []
        self.buses = []
        self.hierarchy = 'top'
        self.level = 0
        self.context = [('top', )]

        # Clear out the no-connect net and set the global no-connect if it's
        # tied to this circuit.
        if getattr(self, 'NC', False) and NC and NC is self.NC:  # pylint: disable=undefined-variable
            self.NC = _NCNet(name='__NOCONNECT', circuit=self)  # Net for storing no-connects for parts in this circuit.
            builtins.NC = self.NC
        else:
            self.NC = _NCNet(name='__NOCONNECT', circuit=self)  # Net for storing no-connects for parts in this circuit.

    def add_parts(self, *parts):
        """Add some Part objects to the circuit."""
        for part in parts:
            # Add the part to this circuit if the part is movable and
            # it's not already in this circuit.
            if part.circuit != self:
                if part._is_movable():

                    # Remove the part from the circuit it's already in.
                    if isinstance(part.circuit, Circuit):
                        part.circuit -= part

                    # Add the part to this circuit.
                    part.circuit = self  # Record the Circuit object the part belongs to.
                    part.ref = part.ref  # This adjusts the part reference if necessary.
                    part.hierarchy = self.hierarchy  # Tag the part with its hierarchy position.

                    # To determine where this part was created, trace the function
                    # calls that led to this part and place into a field
                    # but strip off all the calls to internal SKiDL functions.
                    call_stack = inspect.stack()  # Get function call stack.
                    # Use the function at the top of the stack to
                    # determine the location of the SKiDL library functions.
                    try:
                        skidl_dir, _ = os.path.split(call_stack[0].filename)
                    except AttributeError:
                        skidl_dir, _ = os.path.split(call_stack[0][1])
                    # Record file_name#line_num starting from the bottom of the stack
                    # and terminate as soon as a function is found that's in the
                    # SKiDL library (no use recording internal calls).
                    skidl_trace = []
                    for frame in reversed(call_stack):
                        try:
                            filename = frame.filename
                            lineno = frame.lineno
                        except AttributeError:
                            filename = frame[1]
                            lineno = frame[2]
                        if os.path.split(filename)[0] == skidl_dir:
                            # Found function in SKiDL library, so trace is complete.
                            break
                        # Get the absolute path to the file containing the function
                        # and the line number of the call in the file. Append these
                        # to the trace.
                        filepath = os.path.abspath(filename)
                        skidl_trace.append('#'.join((filepath, str(lineno))))
                    # Store the function call trace into a part field.
                    if skidl_trace:
                        part.skidl_trace = ';'.join(skidl_trace)

                    self.parts.append(part)

                else:
                    logger.error("Can't add unmovable part {} to this circuit.".format(part.ref))
                    raise Exception

    def rmv_parts(self, *parts):
        """Remove some Part objects from the circuit."""
        for part in parts:
            if part._is_movable():
                if part.circuit == self and part in self.parts:
                    part.circuit = None
                    part.hierarchy = None
                    self.parts.remove(part)
                else:
                    logger.warning("Removing non-existent part {} from this circuit.".format(part.ref))
            else:
                logger.error("Can't remove part {} from this circuit.".format(part.ref))
                raise Exception

    def add_nets(self, *nets):
        """Add some Net objects to the circuit. Assign a net name if necessary."""
        for net in nets:
            # Add the net to this circuit if the net is movable and
            # it's not already in this circuit.
            if net.circuit != self:
                if net._is_movable():

                    # Remove the net from the circuit it's already in.
                    if isinstance(net.circuit, Circuit):
                        net.circuit -= net

                    # Add the net to this circuit.
                    net.circuit = self  # Record the Circuit object the net belongs to.
                    net.name = net.name
                    net.hierarchy = self.hierarchy  # Tag the net with its hierarchy position.
                    self.nets.append(net)

                else:
                    logger.error("Can't add unmovable net {} to this circuit.".format(net.name))
                    raise Exception

    def rmv_nets(self, *nets):
        """Remove some Net objects from the circuit."""
        for net in nets:
            if net._is_movable():
                if net.circuit == self and net in self.nets:
                    net.circuit = None
                    net.hierarchy = None
                    self.nets.remove(net)
                else:
                    logger.warning("Removing non-existent net {} from this circuit.".format(net.name))
            else:
                logger.error("Can't remove unmovable net {} from this circuit.".format(net.name))
                raise Exception

    def add_buses(self, *buses):
        """Add some Bus objects to the circuit. Assign a bus name if necessary."""
        for bus in buses:
            # Add the bus to this circuit if the bus is movable and
            # it's not already in this circuit.
            if bus.circuit != self:
                if bus._is_movable():

                    # Remove the bus from the circuit it's already in, but skip
                    # this if the bus isn't already in a Circuit.
                    if isinstance(bus.circuit, Circuit):
                        bus.circuit -= bus

                    # Add the bus to this circuit.
                    bus.circuit = self
                    bus.name = bus.name
                    bus.hierarchy = self.hierarchy  # Tag the bus with its hierarchy position.
                    self.buses.append(bus)
                    for net in bus.nets:
                        self += net

    def rmv_buses(self, *buses):
        """Remove some buses from the circuit."""
        for bus in buses:
            if bus._is_movable():
                if bus.circuit == self and bus in self.buses:
                    bus.circuit = None
                    bus.hierarchy = None
                    self.buses.remove(bus)
                    for net in bus.nets:
                        self.nets.remove(net)
                else:
                    logger.warning("Removing non-existent bus {} from this circuit.".format(bus.name))
            else:
                logger.error("Can't remove unmovable bus {} from this circuit.".format(bus.name))
                raise Exception

    def add_parts_nets_buses(self, *parts_nets_buses):
        """Add Parts, Nets and Buses to the circuit."""
        for pnb in flatten(parts_nets_buses):
            if isinstance(pnb, Part):
                self.add_parts(pnb)
            elif isinstance(pnb, Net):
                self.add_nets(pnb)
            elif isinstance(pnb, Bus):
                self.add_buses(pnb)
            else:
                logger.error("Can't add a {} to a Circuit object.".format(type(pnb)))
                raise Exception
        return self

    def rmv_parts_nets_buses(self, *parts_nets_buses):
        """Add Parts, Nets and Buses to the circuit."""
        for pnb in flatten(parts_nets_buses):
            if isinstance(pnb, Part):
                self.rmv_parts(pnb)
            elif isinstance(pnb, Net):
                self.rmv_nets(pnb)
            elif isinstance(pnb, Bus):
                self.rmv_buses(pnb)
            else:
                logger.error("Can't remove a {} from a Circuit object.".format(type(pnb)))
                raise Exception
        return self

    __iadd__ = add_parts_nets_buses
    __isub__ = rmv_parts_nets_buses

    def get_nets(self):
        """Get all the distinct nets for the circuit."""
        distinct_nets = []
        for net in self.nets:
            if net is self.NC:
                # Exclude no-connect net.
                continue
            if not net._get_pins():
                # Exclude empty nets with no attached pins.
                continue
            for n in distinct_nets:
                # Exclude net if its already attached to a previously selected net.
                if net.is_attached(n):
                    break
            else:
                # This net is not attached to any of the other distinct nets,
                # so it is also distinct.
                distinct_nets.append(net)
        return distinct_nets

    def _erc_setup(self):
        """
        Initialize the electrical rules checker.
        """

        # Initialize the pin contention matrix.
        self._erc_matrix = [[self.OK for c in range(11)] for r in range(11)]
        self._erc_matrix[Pin.OUTPUT][Pin.OUTPUT] = self.ERROR
        self._erc_matrix[Pin.TRISTATE][Pin.OUTPUT] = self.WARNING
        self._erc_matrix[Pin.UNSPEC][Pin.INPUT] = self.WARNING
        self._erc_matrix[Pin.UNSPEC][Pin.OUTPUT] = self.WARNING
        self._erc_matrix[Pin.UNSPEC][Pin.BIDIR] = self.WARNING
        self._erc_matrix[Pin.UNSPEC][Pin.TRISTATE] = self.WARNING
        self._erc_matrix[Pin.UNSPEC][Pin.PASSIVE] = self.WARNING
        self._erc_matrix[Pin.UNSPEC][Pin.UNSPEC] = self.WARNING
        self._erc_matrix[Pin.PWRIN][Pin.TRISTATE] = self.WARNING
        self._erc_matrix[Pin.PWRIN][Pin.UNSPEC] = self.WARNING
        self._erc_matrix[Pin.PWROUT][Pin.OUTPUT] = self.ERROR
        self._erc_matrix[Pin.PWROUT][Pin.BIDIR] = self.WARNING
        self._erc_matrix[Pin.PWROUT][Pin.TRISTATE] = self.ERROR
        self._erc_matrix[Pin.PWROUT][Pin.UNSPEC] = self.WARNING
        self._erc_matrix[Pin.PWROUT][Pin.PWROUT] = self.ERROR
        self._erc_matrix[Pin.OPENCOLL][Pin.OUTPUT] = self.ERROR
        self._erc_matrix[Pin.OPENCOLL][Pin.TRISTATE] = self.ERROR
        self._erc_matrix[Pin.OPENCOLL][Pin.UNSPEC] = self.WARNING
        self._erc_matrix[Pin.OPENCOLL][Pin.PWROUT] = self.ERROR
        self._erc_matrix[Pin.OPENEMIT][Pin.OUTPUT] = self.ERROR
        self._erc_matrix[Pin.OPENEMIT][Pin.BIDIR] = self.WARNING
        self._erc_matrix[Pin.OPENEMIT][Pin.TRISTATE] = self.WARNING
        self._erc_matrix[Pin.OPENEMIT][Pin.UNSPEC] = self.WARNING
        self._erc_matrix[Pin.OPENEMIT][Pin.PWROUT] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.INPUT] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.OUTPUT] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.BIDIR] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.TRISTATE] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.PASSIVE] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.UNSPEC] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.PWRIN] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.PWROUT] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.OPENCOLL] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.OPENEMIT] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.NOCONNECT] = self.ERROR

        # Fill-in the other half of the symmetrical matrix.
        for c in range(1, 11):
            for r in range(c):
                self._erc_matrix[r][c] = self._erc_matrix[c][r]

        # Setup the error/warning logger.
        global erc_logger
        erc_logger = create_logger('ERC_Logger', 'ERC ', '.erc')

    def set_pin_conflict_rule(self, pin1_func, pin2_func, conflict_level):
        """
        Set the level of conflict for two types of pins on the same net.

        Args:
            pin1_func: The function of the first pin (e.g., Pin.OUTPUT).
            pin2_func: The function of the second pin (e.g., Pin.TRISTATE).
            conflict_level: Severity of conflict (e.g., self.OK, self.WARNING, self.ERROR).
        """

        # Place the conflict level into the symmetrical ERC matrix.
        self._erc_matrix[pin1_func][pin2_func] = conflict_level
        self._erc_matrix[pin2_func][pin1_func] = conflict_level

    def _erc_pin_to_pin_chk(self, pin1, pin2):
        """Check for conflict between two pins on a net."""

        # Use the functions of the two pins to index into the ERC table
        # and see if the pins are compatible (e.g., an input and an output)
        # or incompatible (e.g., a conflict because both are outputs).
        return self._erc_matrix[pin1.func][pin2.func]

    def ERC(self):
        """
        Do an electrical rules check on the circuit.
        """

        self._erc_setup()

        # Check the nets for errors.
        for net in self.nets:
            net._erc()

        # Check the parts for errors.
        for part in self.parts:
            part._erc()

        if (erc_logger.error.count, erc_logger.warning.count) == (0, 0):
            sys.stderr.write('\nNo ERC errors or warnings found.\n\n')
        else:
            sys.stderr.write('\n{} warnings found during ERC.\n'.format(
                erc_logger.warning.count))
            sys.stderr.write('{} errors found during ERC.\n\n'.format(
                erc_logger.error.count))

    def generate_netlist(self, file=None, tool=None):
        """
        Return a netlist as a string and also write it to a file/stream.

        Args:
            file: Either a file object that can be written to, or a string
                containing a file name, or None.

        Returns:
            A string containing the netlist.
        """

        if tool is None:
            tool = DEFAULT_TOOL

        try:
            gen_func = getattr(self, '_gen_netlist_{}'.format(tool))
            netlist = gen_func()
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
                with open(get_script_name() + '.net', 'w') as f:
                    f.write(netlist)

        if CREATE_BACKUP_LIB:
            self.backup_parts()  # Create a new backup lib for the circuit parts.
            global backup_lib    # Clear out any old backup lib so the new one
            backup_lib = None    #   will get reloaded when it's needed.

        return netlist

    def _gen_netlist_kicad(self):
        scr_dict = scriptinfo()
        src_file = os.path.join(scr_dict['dir'], scr_dict['source'])
        date = time.strftime('%m/%d/%Y %I:%M %p')
        tool = 'SKiDL (' + __version__ + ')'
        template = '(export (version D)\n' + \
                   '  (design\n' + \
                   '    (source "{src_file}")\n' + \
                   '    (date "{date}")\n' + \
                   '    (tool "{tool}"))\n'
        netlist = template.format(**locals())
        netlist += "  (components"
        for p in sorted(self.parts, key=lambda p: str(p.ref)):
            netlist += '\n' + p._generate_netlist_component(KICAD)
        netlist += ")\n"
        netlist += "  (nets"
        for code, n in enumerate(sorted(self.get_nets(), key=lambda n: str(n.name))):
            n.code = code
            netlist += '\n' + n._generate_netlist_net(KICAD)
        netlist += ")\n)\n"
        return netlist

    def generate_xml(self, file=None, tool=None):
        """
        Return netlist as an XML string and also write it to a file/stream.

        Args:
            file: Either a file object that can be written to, or a string
                containing a file name, or None.

        Returns:
            A string containing the netlist.
        """

        if tool is None:
            tool = DEFAULT_TOOL

        try:
            gen_func = getattr(self, '_gen_xml_{}'.format(tool))
            netlist = gen_func()
        except KeyError:
            logger.error(
                "Can't generate XML in an unknown ECAD tool format ({}).".format(
                    tool))
            raise Exception

        if (logger.error.count, logger.warning.count) == (0, 0):
            sys.stderr.write(
                '\nNo errors or warnings found during XML generation.\n\n')
        else:
            sys.stderr.write(
                '\n{} warnings found during XML generation.\n'.format(
                    logger.warning.count))
            sys.stderr.write(
                '{} errors found during XML generation.\n\n'.format(
                    logger.error.count))

        try:
            with file as f:
                f.write(netlist)
        except AttributeError:
            try:
                with open(file, 'w') as f:
                    f.write(netlist)
            except (FileNotFoundError, TypeError):
                with open(get_script_name() + '.xml', 'w') as f:
                    f.write(netlist)
        return netlist

    def _gen_xml_kicad(self):
        scr_dict = scriptinfo()
        src_file = os.path.join(scr_dict['dir'], scr_dict['source'])
        date = time.strftime('%m/%d/%Y %I:%M %p')
        tool = 'SKiDL (' + __version__ + ')'
        template = '<?xml version="1.0" encoding="UTF-8"?>\n' + \
                   '<export version="D">\n' + \
                   '  <design>\n' + \
                   '    <source>{src_file}</source>\n' + \
                   '    <date>{date}</date>\n' + \
                   '    <tool>{tool}</tool>\n' + \
                   '  </design>\n'
        netlist = template.format(**locals())
        netlist += '  <components>'
        for p in self.parts:
            netlist += '\n' + p._generate_xml_component(KICAD)
        netlist += '\n  </components>\n'
        netlist += '  <nets>'
        for code, n in enumerate(self.get_nets()):
            n.code = code
            netlist += '\n' + n._generate_xml_net(KICAD)
        netlist += '\n  </nets>\n'
        netlist += '</export>\n'
        return netlist

    def _gen_xml_skidl(self):
        logger.error("Can't generate XML in SKiDL format!")

    def generate_graph(self, file=None, engine='neato', rankdir='LR',
                       part_shape='rectangle', net_shape='point',
                       splines=None, show_values=True, show_anon=False):
        """
        Returns a graphviz graph as graphviz object and can also write it to a file/stream.
        When used in ipython the graphviz object will drawn as an SVG in the output.

        See https://graphviz.readthedocs.io/en/stable/ and http://graphviz.org/doc/info/attrs.html

        Args:
            file: A string containing a file name, or None.
            engine: See graphviz documentation
            rankdir: See graphviz documentation
            part_shape: Shape of the part nodes
            net_shape: Shape of the net nodes
            splines: Style for the edges, try 'ortho' for a schematic like feel
            show_values: Show values as external labels on part nodes
            show_anon: Show anonymous net names

        Returns:
            graphviz.Digraph
        """
        dot = graphviz.Digraph(engine=engine)
        dot.attr(rankdir=rankdir, splines=splines)

        nets = self.get_nets()

        # try and keep things in the same order
        nets.sort(key=lambda n: n.name.lower())

        for n in nets:
            xlabel = n.name
            if not show_anon and n._is_implicit():
                xlabel = None
            dot.node(n.name, shape=net_shape, xlabel=xlabel)
            for pin in n.pins:
                dot.edge(pin.part.ref, n.name, arrowhead='none')

        for p in sorted(self.parts, key=lambda p: p.ref.lower()):
            xlabel = None
            if show_values:
                xlabel = p.value
            dot.node(p.ref, shape=part_shape, xlabel=xlabel)

        if file is not None:
            dot.save(file)
        return dot



    def backup_parts(self, file=None):
        """
        Saves parts in circuit as a SKiDL library in a file.

        Args:
            file: Either a file object that can be written to, or a string
                containing a file name, or None. If None, a standard library
                file will be used.

        Returns:
            Nothing.
        """

        lib = SchLib(tool=SKIDL)  # Create empty library.
        for p in self.parts:
            lib += p
        if not file:
            file = BACKUP_LIB_FILE_NAME
        lib.export(libname=BACKUP_LIB_NAME, file=file)

def SubCircuit(f):
    """
    A @SubCircuit decorator is used to create hierarchical circuits.

    Args:
        f: The function containing SKiDL statements that represents a subcircuit.
    """
    def sub_f(*args, **kwargs):
        # Upon entry, save the reference to the default Circuit object.
        save_default_circuit = default_circuit  # pylint: disable=undefined-variable

        # If the subcircuit has no 'circuit' argument, then all the SKiDL
        # statements in the subcircuit function will reference the default Circuit
        # object.
        if 'circuit' not in kwargs:
            circuit = default_circuit  # pylint: disable=undefined-variable

        # But if the subcircuit function has a 'circuit' argument, then set the default
        # Circuit object to that. Then all SKiDL statements in the function will
        # make changes (i.e., add parts, nets, buses) to that.
        else:
            circuit = kwargs['circuit']
            del kwargs['circuit'] # Don't pass the circuit parameter down to the f function.
            builtins.default_circuit = circuit

        # Setup some globals needed in the subcircuit.
        builtins.NC = default_circuit.NC  # pylint: disable=undefined-variable

        # Invoking the subcircuit function creates circuitry at a level one
        # greater than the current level. (The top level is zero.)
        circuit.level += 1

        # Create a name for this subcircuit from the concatenated names of all
        # the nested subcircuit functions that were called on all the preceding levels
        # that led to this one.
        circuit.hierarchy = circuit.context[-1][0] + '.' + f.__name__

        # Store the context so it can be used if this subcircuit function
        # invokes another subcircuit function within itself to add more
        # levels of hierarchy.
        circuit.context.append((circuit.hierarchy, ))

        # Call the function to create whatever circuitry it handles.
        # The arguments to the function are usually nets to be connected to the
        # parts instantiated in the function, but they may also be user-specific
        # and have no effect on the mechanics of adding parts or nets although
        # they may direct the function as to what parts and nets get created.
        # Store any results it returns as a list. These results are user-specific
        # and have no effect on the mechanics of adding parts or nets.
        results = f(*args, **kwargs)

        # Restore the context that existed before the subcircuitry was
        # created. This does not remove the circuitry since it has already been
        # added to the parts and nets lists.
        circuit.context.pop()

        # Restore the hierarchy label and level.
        circuit.hierarchy = circuit.context[-1][0]
        circuit.level -= 1

        # Restore the default circuit and globals.
        builtins.default_circuit = save_default_circuit
        builtins.NC = default_circuit.NC  # pylint: disable=undefined-variable

        return results

    return sub_f

# The decorator can also be called as "@subcircuit".
subcircuit = SubCircuit


@norecurse
def load_backup_lib():
    """Load a backup library that stores the parts used in the circuit."""

    global backup_lib

    # Don't keep reloading the backup library once it's loaded.
    if not backup_lib:
        try:
            # The backup library is a SKiDL lib stored as a Python module.
            exec(open(BACKUP_LIB_FILE_NAME).read())
            # Copy the backup library in the local storage to the global storage.
            backup_lib = locals()[BACKUP_LIB_NAME]

        except (FileNotFoundError, ImportError, NameError, IOError):
            pass

    return backup_lib


def search(term, tool=None):
    """
    Print a list of components with the regex term within their name, alias, description or keywords.
    """

    def search_libraries(term, tool):
        """Search for a regex term in part libraries."""

        parts = set() # Set of parts and their containing libraries found with the term.

        for lib_dir in lib_search_paths[tool]:
            print('lib_dir = {}'.format(lib_dir))
            # Get all the library files in the search path.
            try:
                lib_files = os.listdir(lib_dir)
            except OSError:
                continue
            lib_files = [l for l in lib_files if l.endswith(lib_suffixes[tool])]

            for lib_file in lib_files:
                print(' '*79, '\rSearching {} ...'.format(lib_file), end='\r')
                lib = SchLib(os.path.join(lib_dir, lib_file), tool=tool) # Open the library file.

                def mk_list(l):
                    """Make a list out of whatever is given."""
                    if isinstance(l, (list, tuple)):
                        return l
                    if not l:
                        return []
                    return [l]

                # Search the current library for parts with the given term in 
                # each of the these categories.
                for category in ['name', 'alias', 'description', 'keywords']:
                    for part in mk_list(lib.get_parts(**{category:term})):
                        part.parse() # Parse the part to instantiate the complete object.
                        parts.add((lib_file, part)) # Store the library name and part object.
                print(' '*79, end='\r')

        return list(parts) # Return the list of parts and their containing libraries.

    if tool is None:
        tool = DEFAULT_TOOL

    term = '.*' + term + '.*' # Use the given term as a substring.
    parts = search_libraries(term, tool)  # Search for parts with that substring.

    # Print each part name sorted by the library where it was found.
    for lib_file, p in sorted(parts, key=lambda p: p[0]):
        try:
            print('{}:'.format(lib_file), end=" ")
        except Exception:
            pass
        try:
            print(p.name, end=" ")
        except Exception:
            pass
        try:
            print('({})'.format(p.description))
        except Exception:
            print(' ')


def show(lib, part_name, tool=None):
    """
    Print the I/O pins for a given part in a library.

    Args:
        lib: Either a SchLib object or the name of a library.
        part_name: The name of the part in the library.
        tool: The ECAD tool format for the library.

    Returns:
        A Part object.
    """

    if tool is None:
        tool = DEFAULT_TOOL
    try:
        return Part(lib, re.escape(part_name), tool=tool, dest=TEMPLATE)
    except Exception:
        return None


def set_default_tool(tool):
    """Set the ECAD tool that will be used by default."""
    global DEFAULT_TOOL
    DEFAULT_TOOL = tool


# Create the default Circuit object that will be used unless another is explicitly created.
builtins.default_circuit = Circuit()
# NOCONNECT net for attaching pins that are intentionally left open.
builtins.NC = default_circuit.NC  # pylint: disable=undefined-variable

# Create calls to functions on whichever Circuit object is the current default.
ERC = default_circuit.ERC                            # pylint: disable=undefined-variable
generate_netlist = default_circuit.generate_netlist  # pylint: disable=undefined-variable
generate_xml = default_circuit.generate_xml          # pylint: disable=undefined-variable
generate_graph = default_circuit.generate_graph      # pylint: disable=undefined-variable
backup_parts = default_circuit.backup_parts          # pylint: disable=undefined-variable

# Define a tag for nets that convey power (e.g., VCC or GND).
POWER = Pin.POWER_DRIVE
