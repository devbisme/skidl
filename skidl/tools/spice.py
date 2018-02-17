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
Handler for reading SPICE libraries.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from builtins import str
from builtins import int
from builtins import range
from builtins import dict
from builtins import zip
from future import standard_library
standard_library.install_aliases()

import os.path
from ..py_2_3 import *
from ..defines import *
from ..utilities import *
from ..Part import Part
from ..Net import Net
from ..Pin import Pin

if USING_PYTHON3:
    from PySpice.Spice.Library import SpiceLibrary
    from PySpice.Spice.Netlist import Circuit as PySpiceCircuit # Avoid clash with Circuit class below.

tool_name = SPICE
lib_suffix = '.lib'


def _load_sch_lib_(self, filename=None, lib_search_paths_=None):
    """
    Load the .subckt I/O from a SPICE library file.

    Args:
        filename: The name of the SPICE library file.
    """

    from ..skidl import lib_suffixes
    from ..Part import Part
    from ..Pin import Pin

    # Try to open the file. Add a .lib extension if needed. If the file
    # doesn't open, then try looking in the KiCad library directory.
    try:
        f, filename = find_and_open_file(
            filename,
            lib_search_paths_,
            lib_suffixes[SPICE],
            exclude_binary=True,
            descend=-1)
    except Exception as e:
        raise Exception('Unable to open SPICE Library File {} ({})'.format(
            filename, str(e)))

    # Read the definition of each part line-by-line and then create
    # a Part object that gets stored in the part list.
    for line in f:

        # Skip over comments.
        if line.startswith('*'):
            pass

        # Look for the start of a part definition.
        elif line.lower().startswith('.subckt'):
            # Part definition is the 1st line plus any continuation lines.
            while line.endswith('+'):
                line = line[:-1]  # Remove '+' at end of current line.
                line += ' ' + f.readline()  # Append the next line.

            # Create the part with the part definition.
            part = _mk_subckt_part(line)  # Create un-filled part template.

            # Flesh-out the part.
            part.filename = filename  # Store filename where this part came from.

            # Parse the part definition.
            pieces = part.part_defn.split()
            try:
                # part defn: .subckt part_name pin1, pin2, ... pinN.
                part.name = pieces[1]
                part.pins = [Pin(num=p, name=p) for p in pieces[2:]]
                part.associate_pins()
            except IndexError:
                logger.warn('Misformatted SPICE subcircuit: {}'.format(
                    part.part_defn))
            else:
                # Now find a symbol file for the part to assign names to the pins.
                sym_file, _ = find_and_open_file(
                    part.name,
                    lib_search_paths_,
                    '.asy',
                    allow_failure=True,
                    exclude_binary=True,
                    descend=-1)
                if sym_file:
                    pin_names = []
                    pin_indices = []
                    for sym_line in sym_file:
                        if sym_line.lower().startswith('pinattr pinname'):
                            pin_names.append(sym_line.split()[2])
                        elif sym_line.lower().startswith('pinattr spiceorder'):
                            pin_indices.append(sym_line.split()[2])
                        elif sym_line.lower().startswith(
                                'symattr description'):
                            part.description = ' '.join(sym_line.split()[2:])
                    # Pin names and indices should be matched by the order they
                    # appeared in the symbol file. Each index should match the
                    # order of the pins in the .subckt file.
                    for index, name in zip(pin_indices, pin_names):
                        part.pins[int(index) - 1].name = name

            # Remove the part definition string since we're done parsing it.
            self.part_defn = None

            self.add_parts(part)

def _parse_lib_part_(self, just_get_name=False):  # pylint: disable=unused-argument
    """
    Create a Part using a part definition from a SPICE library.
    """

    # Parts in a SPICE library are already parsed and ready for use,
    # so just return the part.
    return self


def _mk_subckt_part(defn='XXX'):
    part = Part(part_defn=defn, tool=SPICE, dest=LIBRARY)
    part.part_defn = defn
    part.fplist = []
    part.aliases = []
    part.num_units = 1
    part.ref_prefix = 'X'
    part._ref = None
    part.filename = ''
    part.name = ''
    part.pins = []
    part.pyspice = {'name': 'X', 'add': add_subcircuit_to_circuit}
    return part

def _gen_netlist_(self, **kwargs):
    """
    Return a PySpice Circuit generated from a SKiDL circuit.

    Args:
        title: String containing the title for the PySpice circuit.
        libs: String or list of strings containing the paths to directories
            containing SPICE models.
    """

    if USING_PYTHON2:
        return None

    # Create an empty PySpice circuit.
    title = kwargs.pop('title', '') # Get title and remove it from kwargs.
    circuit = PySpiceCircuit(title)

    # Initialize set of libraries to include in the PySpice circuit.
    includes = set()

    # Add any models used by the parts.
    models = set([getattr(part, 'model', None) for part in self.parts])
    models.discard(None)
    lib_dirs = set(flatten([kwargs.get('libs', None)]))
    lib_dirs.discard(None)
    spice_libs = [SpiceLibrary(dir) for dir in lib_dirs]
    for model in models:
        for spice_lib in spice_libs:
            try:
                includes.add(spice_lib[model])
            except KeyError:
                pass
            else:
                break
        else:
            logger.error('Unknown SPICE model: {}'.format(model))

    # Add any subckt libraries used by the parts.
    part_names = set([getattr(part, 'name', None) for part in self.parts if getattr(part, 'filename', None)])
    lib_files = set([getattr(part, 'filename', None) for part in self.parts])
    lib_files.discard(None)
    lib_dirs = [os.path.dirname(f) for f in lib_files]
    spice_libs = [SpiceLibrary(dir) for dir in lib_dirs]
    for part_name in part_names:
        for spice_lib in spice_libs:
            try:
                includes.add(spice_lib[part_name])
            except KeyError:
                pass
            else:
                break
        else:
            logger.error('Unknown SPICE subckt: {}'.format(part_name))

    # Add the models and subckt libraries to the PySpice circuit.
    for inc in includes:
        circuit.include(inc)

    # Add each part in the SKiDL circuit to the PySpice circuit.
    for part in sorted(self.parts, key=lambda p: str(p.ref)):
        # Add each part. All PySpice parts have an add_to_spice attribute
        # and can be added directly. Other parts are added as subcircuits.
        try:
            add_func = part.pyspice['add']
        except (AttributeError, KeyError):
            logger.error('Part has no SPICE model: {}'.format(part))
        else:
            add_func(part, circuit)
                    
    return circuit


def node(net_or_pin):
    if isinstance(net_or_pin, Net):
        return net_or_pin.name
    if isinstance(net_or_pin, Pin):
        return net_or_pin.net.name

def _get_spice_ref(part):
    '''Return a SPICE reference ID for the part.'''
    if part.ref.startswith(part.ref_prefix):
        return part.ref[len(part.ref_prefix):]
    return part.ref


def _get_net_names(part):
    '''Return a list of net names attached to the pins of a part.'''
    return [node(pin) for pin in part.pins if pin.is_connected()]


def _get_pos_args(part, pos_arg_names):
    '''Return the values for positional arguments to PySpice element constructor.'''
    pos_arg_values = []
    for name in pos_arg_names:
        try:
            # If the positional argument is a Part, then substitute the part
            # reference because it's probably a control current for something
            # like a current-controlled source or switch. Otherwise, just use
            # the positional argument as-is.
            value = getattr(part, name)
            if isinstance(value, Part):
                value = value.ref
            pos_arg_values.append(value)
        except AttributeError:
            pass
    return pos_arg_values


def _get_kwargs(part, kw):
    '''Return a dict of keyword arguments to PySpice element constructor.'''
    kwargs = {}
    for key in kw:
        try:
            # If the keyword argument is a Part, then substitute the part
            # reference because it's probably a control current for something
            # like a current-controlled source or switch. Otherwise, just use
            # the keyword argument as-is.
            value = getattr(part, key)
            if isinstance(value, Part):
                value = value.ref
            elif isinstance(value, Net):
                value = value.name
            kwargs.update({key: value})
        except AttributeError:
            pass
    return kwargs


def _get_optional_pin_nets(part, optional_pins):
    pins = {}
    for pin in part.pins:
        if pin.is_connected():
            try:
                pin_key = optional_pins[pin.name]
                pins[pin_key] = node(pin)
            except KeyError:
                logger.error('Part {}-{} has no {} pin: {}'.format(part.ref, part.name, pin.name, part))
    return pins


def add_part_to_circuit(part, circuit):
    '''
    Add a part to a PySpice Circuit object.

    Args:
        part: SKiDL Part object.
        circuit: PySpice Circuit object.
    '''

    pos = part.pyspice['pos']
    kw = part.pyspice['kw']
    optional_pins = part.pyspice.get('optional_pins', None)

    # Positional arguments start with the device name.
    args = [_get_spice_ref(part)]

    # Then add the net connections to the device unless it has optional pins
    # like the substrate connection of a MOSFET. In that case, they'll get
    # added as keyword arguments below.
    if not optional_pins:
        args.extend(_get_net_names(part))

    # Then add any additional positional arguments.
    args.extend(_get_pos_args(part, pos))
    # Get keyword arguments.
    kwargs = _get_kwargs(part, kw)

    # If the device has optional pins, add all pins as keyword arguments.
    if optional_pins:
        kwargs.update(_get_optional_pin_nets(part, optional_pins))

    # Add the part to the PySpice circuit.
    print('Adding {}-{} to PySpice Circuit object.'.format(part.name, part.ref))
    print('args:', args)
    print('kwargs:', kwargs)
    getattr(circuit, part.pyspice['name'])(*args, **kwargs)


def add_subcircuit_to_circuit(part, circuit):
    '''
    Add a .SUBCKT part to a PySpice Circuit object.

    Args:
        part: SKiDL Part object.
        circuit: PySpice Circuit object.
    '''

    args = [_get_spice_ref(part)]
    args.append(part.name)
    args.extend(_get_net_names(part))
    getattr(circuit, part.pyspice['name'])(*args)


def not_implemented(part, circuit):
    logger.error("Function not implemented for {} - {}.".format(
        part.name, part.ref))
