# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2022 Dave Vandenbout.

"""
Functions for handling KiCad 6 files.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from builtins import int

from future import standard_library

from ...logger import active_logger
from ...utilities import *

standard_library.install_aliases()


def _split_into_symbols(libstr):
    """Split a KiCad V6 library and return a list of symbol strings."""

    # Split using "(symbol" as delimiter and discard any preamble.
    libstr = libstr.replace("( ", "(")
    delimiter = "(symbol "
    pieces = libstr.split(delimiter)[1:]

    symbol_name = "_"  # Name of current symbol being assembled.
    symbols = {}  # Symbols indexed by their names.

    # Go through the pieces and assemble each symbol.
    for piece in pieces:

        # Get the symbol name immediately following the delimiter.
        name = piece.split(None, 1)[0]
        name = name.replace('"', "")  # Remove quotes around name.
        name1 = "_".join(name.split("_")[:-2])  # Remove '_#_#' from subsymbols.

        if name1 == symbol_name:
            # if name.startswith(symbol_name):
            # If the name starts with the same string as the
            # current symbol, then this is a unit of the symbol.
            # Therefore, just append the unit to the symbol.
            symbols[symbol_name] += delimiter + piece
        else:
            # Otherwise, this is the start of a new symbol.
            # Remove the library name preceding the symbol name.
            symbol_name = name.split(":", 1)[-1]
            symbols[symbol_name] = delimiter + piece

    return symbols


def load_sch_lib(self, f, filename, lib_search_paths_):
    """
    Load the parts from a KiCad schematic library file.

    Args:
        filename: The name of the KiCad schematic library file.
    """

    from ...part import Part

    # Parse the library and return a nested list of library parts.
    lib_sexp = "".join(f.readlines())

    parts = _split_into_symbols(lib_sexp)

    def extract_quoted_string(part, property_type):
        """Extract quoted string from a property in a part symbol definition."""
        try:
            # Quoted string follows the property type id.
            value = part.split(property_type)[1]
        except IndexError:
            # Property didn't exist, so return empty string.
            return ""
        # Remove quotes and return the string.
        return re.findall(r'"(.*?)(?<!\\)"', value)[0]

    # Create Part objects for each part in library.
    for part_name, part_defn in parts.items():

        # Get part properties.
        keywords = extract_quoted_string(part_defn, "ki_keywords")
        datasheet = extract_quoted_string(part_defn, "Datasheet")
        description = extract_quoted_string(part_defn, "ki_description")

        # Join the various text pieces by newlines so the ^ and $ special characters
        # can be used to detect the start and end of a piece of text during RE searches.
        search_text = "\n".join([filename, part_name, description, keywords])

        # Create a Part object and add it to the library object.
        self.add_parts(
            Part(
                part_defn=part_defn,
                tool=tool_name,
                dest=LIBRARY,
                filename=filename,
                name=part_name,
                aliases=list(),  # No aliases in KiCad V6?
                keywords=keywords,
                datasheet=datasheet,
                description=description,
                search_text=search_text,
                tool_version="kicad_v6",
            )
        )


def parse_lib_part(self, partial_parse):
    """
    Create a Part using a part definition from a KiCad V6 schematic library.

    Args:
        partial_parse: If true, scan the part definition until the
            name and aliases are found. The rest of the definition
            will be parsed if the part is actually used.
    """

    # For info on part library format, look at:
    # https://docs.google.com/document/d/1lyL_8FWZRouMkwqLiIt84rd2Htg4v1vz8_2MzRKHRkc/edit
    # https://gitlab.com/kicad/code/kicad/-/blob/master/eeschema/sch_plugins/kicad/sch_sexpr_parser.cpp

    from ...pin import Pin

    # Return if there's nothing to do (i.e., part has already been parsed).
    if not self.part_defn:
        return

    # If a part def already exists, the name has already been set, so exit.
    if partial_parse:
        return

    self.aliases = []  # Part aliases.
    self.fplist = []  # Footprint list.
    self.draw = []  # Drawing commands for symbol, including pins.

    part_defn = parse_sexp(self.part_defn, allow_underflow=True)

    for item in part_defn:
        if to_list(item)[0] == "extends":
            # Populate this part (child) from another part (parent) it is extended from.

            # Make a copy of the parent part from the library.
            parent_part_name = item[1]
            parent_part = self.lib[parent_part_name].copy(dest=TEMPLATE)

            # Remove parent attributes that we don't want to overwrite in the child.
            parent_part_dict = parent_part.__dict__
            for key in (
                "part_defn",
                "name",
                "aliases",
                "description",
                "datasheet",
                "keywords",
                "search_text",
            ):
                try:
                    del parent_part_dict[key]
                except KeyError:
                    pass

            # Overwrite child with the parent part.
            self.__dict__.update(parent_part_dict)

            # Make sure all the pins have a valid reference to the child.
            self.associate_pins()

            # Copy part units so all the pin and part references stay valid.
            self.copy_units(parent_part)

            # Perform some operations on the child part.
            for item in part_defn:
                cmd = to_list(item)[0]
                if cmd == "del":
                    self.rmv_pins(item[1])
                elif cmd == "swap":
                    self.swap_pins(item[1], item[2])
                elif cmd == "renum":
                    self.renumber_pin(item[1], item[2])
                elif cmd == "rename":
                    self.rename_pin(item[1], item[2])
                elif cmd == "property_del":
                    del self.fields[item[1]]
                elif cmd == "alternate":
                    pass

            break

    # Populate part fields from symbol properties.
    properties = {
        item[1]: item[2:] for item in part_defn if to_list(item)[0] == "property"
    }
    for name, data in properties.items():
        value = data[0]
        for item in data[1:]:
            if to_list(item)[0] == "id":
                self.fields["F" + str(item[1])] = value
                break
        self.fields[name] = value

    self.ref_prefix = self.fields["F0"]  # Part ref prefix (e.g., 'R').

    # Association between KiCad and SKiDL pin types.
    pin_io_type_translation = {
        "input": Pin.types.INPUT,
        "output": Pin.types.OUTPUT,
        "bidirectional": Pin.types.BIDIR,
        "tri_state": Pin.types.TRISTATE,
        "passive": Pin.types.PASSIVE,
        "unspecified": Pin.types.UNSPEC,
        "power_in": Pin.types.PWRIN,
        "power_out": Pin.types.PWROUT,
        "open_collector": Pin.types.OPENCOLL,
        "open_emitter": Pin.types.OPENEMIT,
        "no_connect": Pin.types.NOCONNECT,
    }

    # Find all the units within a symbol. Skip the first item which is the
    # 'symbol' marking the start of the entire part definition.
    units = [item for item in part_defn[1:] if to_list(item)[0] == "symbol"]
    self.num_units = len(units)

    # Get pins and assign them to each unit as well as the entire part.
    unit_nums = []  # Stores unit numbers for units with pins.
    for unit in units:

        # Extract the part name, unit number, and conversion flag.
        unit_name_pieces = unit[1].split("_")  # unit name follows 'symbol'
        symbol_name = "_".join(unit_name_pieces[:-2])
        assert symbol_name == self.name
        unit_num = int(unit_name_pieces[-2])
        conversion_flag = int(unit_name_pieces[-1])

        # Don't add this unit to the part if the conversion flag is 0.
        if not conversion_flag:
            continue

        # Get the pins for this unit.
        unit_pins = [item for item in unit if to_list(item)[0] == "pin"]

        # Save unit number if the unit has pins. Use this to create units
        #  after the entire part is created.
        if unit_pins:
            unit_nums.append(unit_num)

        # Process the pins for the current unit.
        for pin in unit_pins:

            # Pin electrical type immediately follows the "pin" tag.
            pin_func = pin_io_type_translation[pin[1]]

            # Find the pin name and number starting somewhere after the pin function and shape.
            pin_name = ""
            pin_number = None
            for item in pin[3:]:
                item = to_list(item)
                if item[0] == "name":
                    pin_name = item[1]
                elif item[0] == "number":
                    pin_number = item[1]

            # Add the pins that were found to the total part. Include the unit identifier
            # in the pin so we can find it later when the part unit is created.
            self.add_pins(
                Pin(name=pin_name, num=pin_number, func=pin_func, unit=unit_num)
            )

    # Clear the part reference field directly. Don't use the setter function
    # since it will try to generate and assign a unique part reference if
    # passed a value of None.
    self._ref = None

    # Make sure all the pins have a valid reference to this part.
    self.associate_pins()

    # Create the units now that all the part pins have been added.
    if len(unit_nums) > 1:
        for unit_num in unit_nums:
            unit_label = "u" + num_to_chars(unit_num)
            self.make_unit(unit_label, unit=unit_num)

    # Part definition has been parsed, so clear it out. This prevents a
    # part from being parsed more than once.
    self.part_defn = None


def gen_svg_comp(part, symtx, net_stubs=None):
    """
    Generate SVG for this component.

    Args:
        part: Part object for which an SVG symbol will be created.
        net_stubs: List of Net objects whose names will be connected to
            part symbol pins as connection stubs.
        symtx: String such as "HR" that indicates symbol mirroring/rotation.

    Returns: SVG for the part symbol.
    """
    raise NotImplementedError
