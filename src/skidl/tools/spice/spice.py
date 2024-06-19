# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Handler for reading SPICE libraries.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import os.path
import re
import sys
from builtins import dict, int, object, range, str, zip

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from skidl import Alias, Net, LIBRARY, Part, Pin
from skidl.logger import active_logger
from skidl.utilities import (
    INDEX_SEPARATOR,
    export_to_all,
    find_and_open_file,
    find_and_read_file,
)


__all__ = ["lib_suffix", "DeviceModel", "XspiceModel", "Parameters"]


# PySpice may not be installed, particularly under Python 2.
try:
    from PySpice.Spice.Library import SpiceLibrary
    from PySpice.Spice.Netlist import (
        Circuit as PySpiceCircuit,  # Avoid clash with Circuit class below.
    )
except ImportError:
    pass

# These aren't used here, but they are used in modules
# that include this module.
lib_suffix = [".lib", ".spice"]


@export_to_all
def default_lib_paths():
    """Return default list of directories to search for part libraries."""

    # Start search for part libraries in the current directory.
    paths = ["."]

    return paths


@export_to_all
def get_fp_lib_tbl_dir():
    """Get the path to where the global fp-lib-table file is found."""

    return "" # No global fp-lib-table file for SPICE.


def _gather_statement(file):
    """Return list of words in a complete statement read from a SPICE file."""

    statement = ""  # Holds complete SPICE statement consisting of one or more lines.
    for line in file:
        line = line.strip()

        if not line:
            continue  # Ignore blank lines.
        if line.startswith("*"):
            continue  # Ignore comments.

        if line.startswith("+"):
            # Continuation lines are appended to the statement.
            statement += " " + line[1:]
        else:
            # If the current line is not a continuation, then
            # return the statement accumulated from the previous lines.
            if statement:
                yield statement.lower().split()
            # The current line becomes the start of the next statement.
            statement = line[:]

    # Return any statement that was in-process when the file ended.
    if statement != "":
        yield statement.lower().split()


@export_to_all
def load_sch_lib(self, filename=None, lib_search_paths_=None, lib_section=None):
    """
    Load the .subckt I/O from a SPICE library file.

    Args:
        filename: The name of the SPICE library file.
        lib_search_paths_ : List of directories to search for the file.
    """

    from skidl import SPICE
    from skidl.tools import lib_suffixes

    if os.path.isdir(filename):
        # A directory was given, so just use that.
        spice_lib_path = os.path.abspath(filename)
    else:
        # A file name was given, so find the absolute file path in the search paths.
        _, spice_lib_path = find_and_open_file(
            filename=filename,
            paths=lib_search_paths_,
            ext=lib_suffixes[SPICE],
            exclude_binary=True,
            descend=-1,
        )

    # Read the Spice library from the given path.
    spice_lib = SpiceLibrary(
        root_path=spice_lib_path, recurse=True, section=lib_section
    )

    # Get the unique set of files referenced by the subcircuits in the Spice library.
    lib_files = set([str(spice_lib[subcirc]) for subcirc in spice_lib.subcircuits])

    # Go through the files and create a SKiDL Part for each subcircuit.
    for lib_file in lib_files:

        with open(lib_file) as f:
            # Read the definition of each part line-by-line and then create
            # a Part object that gets stored in the part list.
            for statement in _gather_statement(f):

                # Look for the start of a part definition.
                if statement[0] == ".subckt":

                    # Create an un-filled part template.
                    part = Part(part_defn="don't care", tool=SPICE, dest=LIBRARY)
                    part.fplist = []
                    part.aliases = []
                    part.num_units = 1
                    part.ref_prefix = "X"
                    part._ref = None
                    part.filename = ""
                    part.name = ""
                    part.pins = []
                    part.pyspice = {
                        "name": "X",
                        "add": add_subcircuit_to_circuit,
                        "lib": spice_lib,
                        "lib_path": spice_lib_path,
                        "lib_section": lib_section,
                    }

                    # Flesh-out the part.
                    # Parse the part definition.
                    pieces = statement
                    try:
                        # part defn: .subckt part_name pin1, pin2, ... pinN.
                        part.name = pieces[1]
                        part.pins = [Pin(num=p, name=p) for p in pieces[2:]]
                        part.associate_pins()
                    except IndexError:
                        active_logger.warning(
                            "Misformatted SPICE subcircuit: {}".format(part.part_defn)
                        )
                    else:
                        # Now find a symbol file for the part to assign names to the pins.
                        # First, check for LTSpice symbol file.
                        sym_file, _ = find_and_read_file(
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
                            for sym_line in sym_file.split("\n"):
                                if not sym_line:
                                    continue
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
                            sym_file, _ = find_and_read_file(
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
                                for sym_line in sym_file.split("\n"):
                                    sym_line = sym_line.strip()
                                    if not sym_line:
                                        continue
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

                    # Add subcircuit part to the library.
                    self.add_parts(part)


@export_to_all
def parse_lib_part(self, partial_parse=False):  # pylint: disable=unused-argument
    """
    Create a Part using a part definition from a SPICE library.
    """

    # Parts in a SPICE library are already parsed and ready for use,
    # so just return the part.
    return self


# Classes for device and xspice models.


@export_to_all
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


@export_to_all
def gen_netlist(self, **kwargs):
    """
    Return a PySpice Circuit generated from a SKiDL circuit.

    Args:
        title: String containing the title for the PySpice circuit.
        libs: String or list of strings containing the paths to directories
            containing SPICE models.
    """

    from skidl import lib_search_paths, SPICE

    if sys.version_info.major == 2:
        active_logger.raise_(
            NotImplementedError,
            "PySpice does not support Python 2, so a SPICE netlist cannot be generated.",
        )

    # Create an empty PySpice circuit.
    title = kwargs.pop("title", "")  # Get title and remove it from kwargs.
    circuit = PySpiceCircuit(title)

    # Default SPICE libraries will be read-in down below if needed.
    default_libs = []

    # Initialize set of libraries to include in the PySpice circuit.
    model_paths = set()  # Paths to the model files that have been used.
    lib_paths = set()  # Paths to the library files that have been used.
    lib_ids = set()  # A lib_id is a tuple of the path to the lib file and a section.

    for part in self.parts:
        try:
            pyspice = part.pyspice
        except AttributeError:
            continue

        model = getattr(part, "model", None)
        if model:
            if isinstance(model, (XspiceModel, DeviceModel)):
                circuit.model(*model.args, **model.kwargs)
            else:
                try:
                    path = pyspice["lib"][model]
                except KeyError:
                    # The part doesn't contain the library with the model, so look elsewhere.
                    if not default_libs:
                        # Read the default SPICE libraries.
                        for path in lib_search_paths[SPICE]:
                            default_libs.append(
                                SpiceLibrary(root_path=path, recurse=True)
                            )

                    # Search for the model in the default libraries.
                    path = None
                    for lib in default_libs:
                        try:
                            path = lib[model]
                            break
                        except KeyError:
                            pass
                    if path == None:
                        active_logger.error(
                            "Unable to find model {} for part {}".format(
                                model, part.ref
                            )
                        )

                # Include the model file if it hasn't been included yet.
                if path != None and path not in model_paths:
                    circuit.include(path)
                    model_paths.add(path)

        try:
            path, section = pyspice["lib_path"], pyspice["lib_section"]
        except KeyError:
            continue
        if not section:
            # Libraries without a section are added as include files.
            if path not in lib_paths:
                circuit.include(path)
                lib_paths.add(path)
        else:
            lib_id = (path, section)
            if lib_id not in lib_ids:
                circuit.lib(*lib_id)
                lib_ids.add(lib_id)

    # Add each part in the SKiDL circuit to the PySpice circuit.
    # TODO: Make sure self.parts is processed in order that parts were created so ngspice doesn't get references to parts before they exist.
    for part in self.parts:
        # Add each part using its add function which will be either
        # add_part_to_circuit() or add_subcircuit_to_circuit().
        try:
            add_func = part.pyspice["add"]
        except (AttributeError, KeyError):
            active_logger.error("Part has no SPICE model: {}".format(part))
        else:
            add_func(part, circuit)

    return circuit


@export_to_all
def node(net_pin_part):
    if isinstance(net_pin_part, Net):
        # Replace any special chars in a net name because Spice doesn't like them.
        return re.sub(r"\W", "_", net_pin_part.name)
    if isinstance(net_pin_part, Pin):
        # Replace any special chars in a net name because Spice doesn't like them.
        return re.sub(r"\W", "_", net_pin_part.net.name)
    if isinstance(net_pin_part, Part):
        return net_pin_part.ref


def _xspice_node(net_or_pin):
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
                active_logger.error(
                    "Part {}-{} has no {} pin: {}".format(
                        part.ref, part.name, pin.name, part
                    )
                )

    return kwargs


@export_to_all
def not_implemented(part, circuit):
    """Unable to add a particular SPICE part to a circuit."""
    active_logger.error(
        "Function not implemented for {} - {}.".format(part.name, part.ref)
    )


@export_to_all
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


class Parameters(dict):
    """Class for holding Spice subcircuit parameters."""

    def __init__(self, **params):
        super().__init__(**params)

    def __copy__(self):
        return {k: copy(v) for k, v in self}


@export_to_all
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
    from skidl.pyspice import Parameters

    params = {}
    for k, v in part.__dict__.items():
        if isinstance(v, Parameters):
            params = v
    getattr(circuit, part.pyspice["name"])(*args, **params)


@export_to_all
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
        elif isinstance(pin, XspicePinList):
            # Add pins from a pin vector.
            args.append("[" + " ".join([node(p) for p in pin]) + "]")
        else:
            active_logger.error("Illegal XSPICE argument: {}".format(pin))

    # The XSPICE model name should be the only keyword argument.
    kwargs = {"model": part.model.name}

    # Add the part to the PySpice circuit.
    getattr(circuit, part.pyspice["name"])(*args, **kwargs)


@export_to_all
def add_xspice_io(part, io):
    """
    Add XSPICE I/O to the pins of a part.
    """
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
            part.pins.append(XspicePinList(num=i, name=arg[1:-1], part=part))
        elif arg[-2:] == "[]":
            part.pins.append(XspicePinList(num=i, name=arg[0:-2], part=part))
        else:
            # Add a simple, non-vector pin.
            part.add_pins(Pin(num=i, name=arg))


@export_to_all
def convert_for_spice(part, spice_part, pin_map):
    """Convert a Part object for use with SPICE.

    Args:
        part: SKiDL Part object that will be converted for use as a SPICE component.
        spice_part (Part): The type of SPICE Part to be converted to.
        pin_map (dict): Dict with pin numbers/names of part as keys and num/names of spice_part pins as replacement values.
    """

    # Give the part access to the PySpice information from the SPICE part.
    part.pyspice = spice_part.pyspice

    # Give the part the additional aliases from the SPICE part.
    part.aliases += spice_part.aliases

    # Look-up pin names/numbers to create a mapping between actual Pin objects.
    pin_map = [[part[dst], spice_part[src]] for dst, src in pin_map.items()]

    # Pull some info from the SPICE part pins into the part pins.
    for dst_pin, src_pin in pin_map:
        dst_pin.num = src_pin.num
        dst_pin.name = src_pin.name
        dst_pin.aliases += src_pin.aliases


class XspicePinList(list):
    """
    A list of Pin objects that's meant to look something like a Pin to a Part.
    This is used for vector I/O of XSPICE parts.
    """

    def __init__(self, num, name, part):
        super().__init__()
        # The list needs the following attributes to behave like a Pin.
        self.aliases = Alias()
        self.num = num
        self.name = name
        self.part = part

    def __getitem__(self, i):
        """
        Get a Pin from the list. Add Pin objects to the list if they don't exist.
        """
        l = super().__len__()
        if i >= l:
            self.extend([Pin(num=j, part=self.part) for j in range(l, i + 1)])
        return super().__getitem__(i)

    def __iter__(self):
        if super().__len__() == 0:
            tmp = [Pin()]
            return (p for p in tmp)
        return (p for p in super().__iter__())  # Return generator expr.

    def __len__(self):
        l = super().__len__()
        return l or 1

    def copy(self, **attribs):
        """
        Return a copy of a PinList for use when a Part is copied.

        Args:
            attribs(dict): Attributes to apply to copied part pins.
        """
        cpy = self.__class__(self.num, self.name, self.part)
        for pin in self:
            cpy += pin.copy(**attribs)
        return cpy

    def disconnect(self):
        """Disconnect all the pins in the list."""
        for pin in self:
            pin.disconnect()

    def is_connected(self):
        for pin in self:
            if pin.is_connected():
                return True
        return False

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, nm):
        del self.name  # Remove any pre-existing name.
        self.aliases += nm
        self._name = nm

    @name.deleter
    def name(self):
        try:
            self.aliases.discard(self._name)
            self._name = None
        except AttributeError:
            pass
