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

from __future__ import absolute_import, division, print_function, unicode_literals

import os.path
from builtins import dict, int, object, range, str, zip

from future import standard_library

from ..common import *
from ..defines import *
from ..logger import logger
from ..net import Net
from ..part import Part
from ..pin import Pin, PinList
from ..utilities import *

standard_library.install_aliases()


# PySpice may not be installed, particularly under Python 2.
try:
    from PySpice.Spice.Library import SpiceLibrary
    from PySpice.Spice.Netlist import (
        Circuit as PySpiceCircuit,
    )  # Avoid clash with Circuit class below.
except ImportError:
    pass

tool_name = SPICE
lib_suffix = ".lib"


def _load_sch_lib_(self, filename=None, lib_search_paths_=None):
    """
    Load the .subckt I/O from a SPICE library file.

    Args:
        filename: The name of the SPICE library file.
        lib_search_paths_ : List of directories to search for the file.
    """

    from ..skidl import lib_suffixes
    from ..part import Part
    from ..pin import Pin

    # Try to open the file. Add a .lib extension if needed. If the file
    # doesn't open, then try looking in the KiCad library directory.
    try:
        f, filepath = find_and_open_file(
            filename,
            lib_search_paths_,
            lib_suffixes[SPICE],
            allow_failure=False,
            exclude_binary=True,
            descend=-1,
        )
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "Unable to open SPICE Library File {} ({})".format(filename, str(e))
        )

    # Read the definition of each part line-by-line and then create
    # a Part object that gets stored in the part list.
    for line in f:

        # Skip over comments.
        if line.startswith("*"):
            pass

        # Look for the start of a part definition.
        elif line.lower().startswith(".subckt"):
            # Part definition is the 1st line plus any continuation lines.
            while line.endswith("+"):
                line = line[:-1]  # Remove '+' at end of current line.
                line += " " + f.readline()  # Append the next line.

            # Create the part with the part definition.
            part = _mk_subckt_part(line)  # Create un-filled part template.

            # Flesh-out the part.
            part.filename = filepath  # Store filename where this part came from.

            # Parse the part definition.
            pieces = part.part_defn.split()
            try:
                # part defn: .subckt part_name pin1, pin2, ... pinN.
                part.name = pieces[1]
                part.pins = [Pin(num=p, name=p) for p in pieces[2:]]
                part.associate_pins()
            except IndexError:
                logger.warn("Misformatted SPICE subcircuit: {}".format(part.part_defn))
            else:
                # Now find a symbol file for the part to assign names to the pins.
                # First, check for LTSpice symbol file.
                sym_file, _ = find_and_open_file(
                    part.name,
                    lib_search_paths_,
                    ".asy",
                    allow_failure=True,
                    exclude_binary=True,
                    descend=-1,
                )
                if sym_file:
                    pin_names = []
                    pin_indices = []
                    for sym_line in sym_file:
                        if sym_line.lower().startswith("pinattr pinname"):
                            pin_names.append(sym_line.split()[2])
                        elif sym_line.lower().startswith("pinattr spiceorder"):
                            pin_indices.append(sym_line.split()[2])
                        elif sym_line.lower().startswith("symattr description"):
                            part.description = " ".join(sym_line.split()[2:])
                    # Pin names and indices should be matched by the order they
                    # appeared in the symbol file. Each index should match the
                    # order of the pins in the .subckt file.
                    for index, name in zip(pin_indices, pin_names):
                        part.pins[int(index) - 1].name = name
                else:
                    # No LTSpice symbol file, so check for PSPICE symbol file.
                    sym_file, diag = find_and_open_file(
                        filename,
                        lib_search_paths_,
                        ".slb",
                        allow_failure=True,
                        exclude_binary=True,
                        descend=-1,
                    )
                    if sym_file:
                        pin_names = []
                        active = False
                        for sym_line in sym_file:
                            line_parts = sym_line.lower().split()
                            if line_parts[0] == "*symbol":
                                active = line_parts[1] == part.name.lower()
                            if active:
                                if line_parts[0] == "p":
                                    pin_names.append(line_parts[6])
                                elif line_parts[0] == "d":
                                    part.description = " ".join(line_parts[1:])
                        pin_indices = list(range(len(pin_names)))
                        for pin, name in zip(part.pins, pin_names):
                            pin.name = name

            # Remove the part definition string since we're done parsing it.
            self.part_defn = None

            self.add_parts(part)


def _parse_lib_part_(self, get_name_only=False):  # pylint: disable=unused-argument
    """
    Create a Part using a part definition from a SPICE library.
    """

    # Parts in a SPICE library are already parsed and ready for use,
    # so just return the part.
    return self


def _mk_subckt_part(defn="XXX"):
    part = Part(part_defn=defn, tool=SPICE, dest=LIBRARY)
    part.part_defn = defn
    part.fplist = []
    part.aliases = []
    part.num_units = 1
    part.ref_prefix = "X"
    part._ref = None
    part.filename = ""
    part.name = ""
    part.pins = []
    part.pyspice = {"name": "X", "add": add_subcircuit_to_circuit}
    return part


# Classes for device and xspice models.


class XspiceModel(object):
    """
    Object to hold the parameters for an XSPICE model.
    """

    def __init__(self, *args, **kwargs):
        self.name = args[0]  # The name to reference the model by.
        self.args = args
        self.kwargs = kwargs


# DeviceModel and XspiceModel are the same.
# WARNING: DeviceModel overlaps a class in PySpice!
DeviceModel = XspiceModel


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
    title = kwargs.pop("title", "")  # Get title and remove it from kwargs.
    circuit = PySpiceCircuit(title)

    # Initialize set of libraries to include in the PySpice circuit.
    includes = set()

    # Add any models used by the parts.
    models = set([getattr(part, "model", None) for part in self.parts])
    models.discard(None)
    lib_dirs = set(flatten([kwargs.get("libs", None)]))
    lib_dirs.discard(None)
    spice_libs = [SpiceLibrary(dir) for dir in lib_dirs]
    for model in models:
        if isinstance(model, (XspiceModel, DeviceModel)):
            circuit.model(*model.args, **model.kwargs)
        else:
            for spice_lib in spice_libs:
                try:
                    includes.add(spice_lib[model])
                except KeyError:
                    pass
                else:
                    break
            else:
                logger.error("Unknown SPICE model: {}".format(model))

    # Add any subckt libraries used by the parts.
    part_names = set(
        [
            getattr(part, "name", None)
            for part in self.parts
            if getattr(part, "filename", None)
        ]
    )
    lib_files = set([getattr(part, "filename", None) for part in self.parts])
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
            logger.error("Unknown SPICE subckt: {}".format(part_name))

    # Add the models and subckt libraries to the PySpice circuit.
    for inc in includes:
        circuit.include(inc)

    # Add each part in the SKiDL circuit to the PySpice circuit.
    for part in sorted(self.parts, key=lambda p: str(p.ref)):
        # Add each part using its add function which will be either
        # add_part_to_circuit() or add_subcircuit_to_circuit().
        try:
            add_func = part.pyspice["add"]
        except (AttributeError, KeyError):
            logger.error("Part has no SPICE model: {}".format(part))
        else:
            add_func(part, circuit)

    return circuit


def node(net_or_pin):
    if isinstance(net_or_pin, Net):
        return net_or_pin.name
    if isinstance(net_or_pin, Pin):
        return net_or_pin.net.name


def _xspice_node(net_or_pin):
    print(net_or_pin, net_or_pin.is_connected())
    if isinstance(net_or_pin, Net):
        return net_or_pin.name
    if isinstance(net_or_pin, Pin):
        if net_or_pin.is_connected():
            return net_or_pin.net.name
        else:
            # For XSPICE parts, unconnected pins are connected to NULL node.
            return "NULL"


def _get_spice_ref(part):
    """Return a SPICE reference ID for the part."""
    if part.ref.startswith(part.ref_prefix):
        return part.ref[len(part.ref_prefix) :]
    return part.ref


def _get_kwargs(part, kw):
    """Return a dict of keyword arguments to PySpice element constructor."""
    kwargs = {}

    for key, param_name in kw.items():
        try:
            # The key indicates some attribute of the part.
            part_attr = getattr(part, key)
        except AttributeError:
            pass
        else:
            # If the keyword argument is a Part, then substitute the part
            # reference because it's probably a control current for something
            # like a current-controlled source or switch.
            if isinstance(part_attr, Part):
                kwargs.update({param_name: part_attr.ref})
            # If the keyword argument is a Net, substitute the net name.
            elif isinstance(part_attr, Net):
                kwargs.update({param_name: node(part_attr)})
            # If the keyword argument is a Pin, skip it. It gets handled below.
            elif isinstance(part_attr, Pin):
                continue
            else:
                kwargs.update({param_name: part_attr})

    for pin in part.pins:
        if pin.is_connected():
            try:
                param_name = kw[pin.name]
                kwargs.update({param_name: node(pin)})
            except KeyError:
                logger.error(
                    "Part {}-{} has no {} pin: {}".format(
                        part.ref, part.name, pin.name, part
                    )
                )

    return kwargs


def not_implemented(part, circuit):
    """Unable to add a particular SPICE part to a circuit."""
    logger.error("Function not implemented for {} - {}.".format(part.name, part.ref))


def add_part_to_circuit(part, circuit):
    """
    Add a part to a PySpice Circuit object.

    Args:
        part: SKiDL Part object.
        circuit: PySpice Circuit object.
    """

    # The device reference is always the first positional argument.
    args = [_get_spice_ref(part)]

    # Get keyword arguments.
    kwargs = _get_kwargs(part, part.pyspice["kw"])

    # Convert model argument if it exists and it's not a string.
    try:
        kwargs["model"] = part.model.name
    except (KeyError, AttributeError):
        # Don't change model kw param if it doesn't exist or is a string.
        pass

    # Add the part to the PySpice circuit.
    getattr(circuit, part.pyspice["name"])(*args, **kwargs)


def _get_net_names(part):
    """Return a list of net names attached to the pins of a part."""
    return [node(pin) for pin in part.pins if pin.is_connected()]


def add_subcircuit_to_circuit(part, circuit):
    """
    Add a .SUBCKT part to a PySpice Circuit object.

    Args:
        part: SKiDL Part object.
        circuit: PySpice Circuit object.
    """

    # The device reference is always the first positional argument.
    args = [_get_spice_ref(part)]

    args.append(part.name)
    args.extend(_get_net_names(part))

    # Add the part to the PySpice circuit.
    getattr(circuit, part.pyspice["name"])(*args)


def add_xspice_to_circuit(part, circuit):
    """
    Add an XSPICE part to a PySpice Circuit object.

    Args:
        part: SKiDL Part object.
        circuit: PySpice Circuit object.
    """

    # The device reference is always the first positional argument.
    args = [_get_spice_ref(part)]

    # Add the pins to the argument list.
    for pin in part.pins:
        if isinstance(pin, Pin):
            # Add a non-vector pin. Use _xspice_node() in case pin is unconnected.
            args.append(_xspice_node(pin))
        elif isinstance(pin, PinList):
            # Add pins from a pin vector.
            args.append("[" + " ".join([node(p) for p in pin]) + "]")
        else:
            logger.error("Illegal XSPICE argument: {}".format(pin))

    # The XSPICE model name should be the only keyword argument.
    kwargs = {"model": part.model.name}

    # Add the part to the PySpice circuit.
    getattr(circuit, part.pyspice["name"])(*args, **kwargs)
