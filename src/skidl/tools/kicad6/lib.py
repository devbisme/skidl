# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Parsing of Kicad libraries.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import os.path
from builtins import int
from collections import OrderedDict

import sexpdata

from future import standard_library

from skidl.part import LIBRARY
from skidl.utilities import export_to_all, find_and_open_file, num_to_chars, to_list

standard_library.install_aliases()

__all__ = ["lib_suffix"]


lib_suffix = [".kicad_sym"]


@export_to_all
def get_kicad_lib_tbl_dir():
    """Get the path to where the global fp-lib-table file is found."""

    paths = (
        "$HOME/.config/kicad",
        "~/.config/kicad",
        "%APPDATA%/kicad",
        "$HOME/Library/Preferences/kicad",
        "~/Library/Preferences/kicad",
    )

    for path in paths:
        path = os.path.normpath(os.path.expanduser(os.path.expandvars(path)))
        if os.path.lexists(path):
            return path
    return ""


@export_to_all
def load_sch_lib(lib, filename=None, lib_search_paths_=None, lib_section=None):
    """
    Load the parts from a KiCad schematic library file.

    Args:
        lib (SchLib): SKiDL library object.
        filename (str): The name of the KiCad schematic library file.
        lib_search_paths_ (list): List of paths with KiCad symbol libraries.
        lib_section: Only used for SPICE simulations.
    """

    from skidl import Part, KICAD6
    from skidl.tools import lib_suffixes

    # Try to open the file using allowable suffixes for the versions of KiCAD.
    suffixes = lib_suffixes[KICAD6]
    base, suffix = os.path.splitext(filename)
    if suffix:
        # If an explicit file extension was given, use it instead of tool lib default extensions.
        suffixes = [suffix]
    for suffix in suffixes:
        # Allow file open failure so multiple suffixes can be tried without error messages.
        f, _ = find_and_open_file(
            filename, lib_search_paths_, suffix, allow_failure=True
        )
        if f:
            # Break from the loop once a library file is successfully opened.
            break
    if not f:
        raise FileNotFoundError(
            "Unable to open KiCad Schematic Library File {}".format(filename)
        )

    # Parse the library and return a nested list of library parts.
    lib_txt = f.read()
    try:
        lib_txt = lib_txt.decode("latin_1")
    except AttributeError:
        # File contents were already decoded.
        pass

    # Convert S-expression library into a list of symbols.
    lib_list = sexpdata.loads(lib_txt)

    # Skip over the 'kicad_symbol_lib' label and extract symbols into a dictionary with
    # symbol names as keys. Use an ordered dictionary to keep parts in the same order as
    # they appeared in the library file because in KiCad V6 library symbols can "extend"
    # previous symbols which should be processed before those that extend them.
    symbols = OrderedDict(
        [
            (item[1], item[2:])
            for item in lib_list[1:]
            if item[0].value().lower() == "symbol"
        ]
    )

    # Create Part objects for each symbol in the library.
    for part_name, part_defn in symbols.items():
        properties = {}

        # See if this symbol extends a previous parent symbol.
        for item in part_defn:
            if item[0].value().lower() == "extends":
                # Get the properties from the parent symbol.
                parent_part = lib[item[1]]
                if parent_part.part_defn:
                    properties.update(
                        {
                            item[1].lower(): item[2]
                            for item in parent_part.part_defn
                            if item[0].value().lower() == "property"
                        }
                    )
                else:
                    properties["ki_keywords"] = parent_part.keywords
                    properties["ki_description"] = parent_part.description
                    properties["datasheet"] = parent_part.datasheet

        # Get symbol properties, primarily to get the reference id.
        properties.update(
            {
                item[1].lower(): item[2]
                for item in part_defn
                if item[0].value().lower() == "property"
            }
        )

        # Get part properties.
        keywords = properties.get("ki_keywords", "")
        datasheet = properties.get("datasheet", "")
        description = properties.get("ki_description", "")

        # Join the various text pieces by newlines so the ^ and $ special characters
        # can be used to detect the start and end of a piece of text during RE searches.
        search_text = "\n".join([filename, part_name, description, keywords])

        # Create a Part object and add it to the library object.
        lib.add_parts(
            Part(
                part_defn=part_defn,
                tool=KICAD6,
                dest=LIBRARY,
                filename=filename,
                name=part_name,
                aliases=list(),  # No aliases in KiCad V6?
                keywords=keywords,
                datasheet=datasheet,
                description=description,
                search_text=search_text,
            )
        )


@export_to_all
def parse_lib_part(part, partial_parse):
    """
    Create a Part using a part definition from a KiCad V6 schematic library.

    Args:
        partial_parse: If true, scan the part definition until the
            name and aliases are found. The rest of the definition
            will be parsed if the part is actually used.
    """

    # For info on part library format, look at:
    # https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/
    # https://docs.google.com/document/d/1lyL_8FWZRouMkwqLiIt84rd2Htg4v1vz8_2MzRKHRkc/edit
    # https://gitlab.com/kicad/code/kicad/-/blob/master/eeschema/sch_plugins/kicad/sch_sexpr_parser.cpp

    from skidl import TEMPLATE, Pin

    # Return if there's nothing to do (i.e., part has already been parsed).
    if not part.part_defn:
        return

    # If a part def already exists, the name has already been set, so exit.
    if partial_parse:
        return

    part.aliases = []  # Part aliases.
    part.fplist = []  # Footprint list.
    part.draw = []  # Drawing commands for symbol, including pins.

    for item in part.part_defn:
        if item[0].value().lower() == "extends":
            # Populate this part (child) from another part (parent) it is extended from.

            # Make a copy of the parent part from the library.
            parent_part = part.lib[item[1]].copy(dest=TEMPLATE)

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
            part.__dict__.update(parent_part_dict)

            # Make sure all the pins have a valid reference to the child.
            part.associate_pins()

            # Copy part units so all the pin and part references stay valid.
            part.copy_units(parent_part)

            # Perform some operations on the child part.
            for item in part.part_defn:
                cmd = item[0].value().lower()
                if cmd == "del":
                    part.rmv_pins(item[1])
                elif cmd == "swap":
                    part.swap_pins(item[1], item[2])
                elif cmd == "renum":
                    part.renumber_pin(item[1], item[2])
                elif cmd == "rename":
                    part.rename_pin(item[1], item[2])
                elif cmd == "property_del":
                    del part.fields[item[1]]
                elif cmd == "alternate":
                    pass

            break

    # Populate part fields from symbol properties.
    properties = {
        item[1]: item[2:]
        for item in part.part_defn
        if item[0].value().lower() == "property"
    }
    for name, data in properties.items():
        value = data[0]
        for item in data[1:]:
            if item[0].value().lower() == "id":
                part.fields["F" + str(item[1])] = value
                break
        part.fields[name] = value

    part.ref_prefix = part.fields["F0"]  # Part ref prefix (e.g., 'R').

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
    units = {
        item[1]: item[2:]
        for item in part.part_defn[1:]
        if item[0].value().lower() == "symbol"
    }
    part.num_units = len(units)

    # Get pins and assign them to each unit as well as the entire part.
    unit_nums = []  # Stores unit numbers for units with pins.
    for unit_name, unit_data in units.items():
        # Extract the part name, unit number, and conversion flag.
        unit_name_pieces = unit_name.split("_")  # unit name follows 'symbol'
        symbol_name = "_".join(unit_name_pieces[:-2])
        assert symbol_name == part.name
        unit_num = int(unit_name_pieces[-2])
        conversion_flag = int(unit_name_pieces[-1])

        # Don't add this unit to the part if the conversion flag is 0.
        if not conversion_flag:
            continue

        # Get the pins for this unit.
        unit_pins = [item for item in unit_data if item[0].value().lower() == "pin"]

        # Save unit number if the unit has pins. Use this to create units
        # after the entire part is created.
        if unit_pins:
            unit_nums.append(unit_num)

        # Process the pins for the current unit.
        for pin in unit_pins:
            # Pin electrical type immediately follows the "pin" tag.
            pin_func = pin_io_type_translation[pin[1].value().lower()]

            # Find the pin name and number starting somewhere after the pin function and shape.
            pin_name = ""
            pin_number = None
            for item in pin[3:]:
                item = to_list(item)
                if item[0].value().lower() == "name":
                    pin_name = item[1]
                elif item[0].value().lower() == "number":
                    pin_number = item[1]

            # Add the pins that were found to the total part. Include the unit identifier
            # in the pin so we can find it later when the part unit is created.
            part.add_pins(
                Pin(name=pin_name, num=pin_number, func=pin_func, unit=unit_num)
            )

    # Clear the part reference field directly. Don't use the setter function
    # since it will try to generate and assign a unique part reference if
    # passed a value of None.
    part._ref = None

    # Make sure all the pins have a valid reference to this part.
    part.associate_pins()

    # Create the units now that all the part pins have been added.
    if len(unit_nums) > 1:
        for unit_num in unit_nums:
            unit_label = "u" + num_to_chars(unit_num)
            part.make_unit(unit_label, unit=unit_num)

    # Part definition has been parsed, so clear it out. This prevents a
    # part from being parsed more than once.
    part.part_defn = None
