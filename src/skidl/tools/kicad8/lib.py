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

import os

# import os.path
from builtins import int
from collections import defaultdict, OrderedDict

import sexpdata

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from skidl import Alias
from skidl.logger import active_logger
from skidl.part import LIBRARY
from skidl.schematics.geometry import mils_per_mm, BBox
from skidl.utilities import export_to_all, find_and_open_file, num_to_chars, to_list, add_unique_attr


__all__ = ["lib_suffix"]


lib_suffix = [".kicad_sym"]


@export_to_all
def default_lib_paths():
    """Return default list of directories to search for part libraries."""

    # Start search for part libraries in the current directory.
    paths = ["."]

    # Add the location of the default KiCad part libraries.
    try:
        paths.append(os.environ["KICAD8_SYMBOL_DIR"])
    except KeyError:
        active_logger.warning(
            "KICAD8_SYMBOL_DIR environment variable is missing, so the default KiCad symbol libraries won't be searched."
        )

    return paths


@export_to_all
def get_fp_lib_tbl_dir():
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

    from skidl import Part, KICAD8
    from skidl.tools import lib_suffixes

    # Try to open the file using allowable suffixes for the versions of KiCAD.
    suffixes = lib_suffixes[KICAD8]
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
    try:
        lib_list = sexpdata.loads(lib_txt)
    except:
        active_logger.raise_(
            RuntimeError,
            "The file {} is not a KiCad Schematic Library File.\n".format(filename),
        )

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
                    # Properties are stored as lists: ["property", name, value].
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

                break # At most one extends clause in part def.

        # Get symbol properties, primarily to get the reference id.
        # Properties are stored as lists: ["property", name, value].
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
                part_defn=part_defn, # A list of lists that define the part.
                tool=KICAD8,
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

    part.aliases = Alias()  # Part aliases.
    part.fplist = []  # Footprint list.
    part.draw_cmds = defaultdict(list)  # Drawing commands for the part and any units, including pins.

    # Search for a parent that this part inherits from.
    for item in part.part_defn:
        if item[0].value().lower() == "extends":

            # Make a copy of the parent part from the library.
            parent_part = part.lib[item[1]].copy(dest=TEMPLATE)

            # Remove parent attributes that we don't want to overwrite in the child.
            parent_part_dict = parent_part.__dict__
            for property_key in (
                "part_defn",
                "_name",
                "_aliases",
                "description",
                "datasheet",
                "keywords",
                "search_text",
            ):
                try:
                    del parent_part_dict[property_key]
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

    def parse_pins(symbol, unit):
        '''Parse the pins within a symbol and add them to the Part object.'''

        # Association between KiCad : SKiDL pin types.
        pin_io_type_translation = {
            "input": Pin.types.INPUT,
            "output": Pin.types.OUTPUT,
            "bidirectional": Pin.types.BIDIR,
            "tri_state": Pin.types.TRISTATE,
            "passive": Pin.types.PASSIVE,
            "free": Pin.types.FREE,
            "unspecified": Pin.types.UNSPEC,
            "power_in": Pin.types.PWRIN,
            "power_out": Pin.types.PWROUT,
            "open_collector": Pin.types.OPENCOLL,
            "open_emitter": Pin.types.OPENEMIT,
            "no_connect": Pin.types.NOCONNECT,
        }

        # Get the pins for this symbol.
        symbol_pins = [item for item in symbol if item[0].value().lower() == "pin"]

        # Process the pins for the symbol.
        for pin in symbol_pins:
            # Pin electrical type immediately follows the "pin" tag.
            pin_func = pin_io_type_translation[pin[1].value().lower()]

            # Find the pin name, number, and X/Y position.
            pin_name = ""
            pin_number = None
            for item in pin:
                item = to_list(item)
                token_name = item[0].value().lower()
                if token_name == "name":
                    pin_name = item[1]
                elif token_name == "number":
                    pin_number = item[1]
                elif token_name == "at":
                    pin_x, pin_y, pin_angle = item[1:4]
                    # TODO: Convert these units from mm to mils?
                    # pin_x = round(pin_x * mils_per_mm)
                    # pin_y = round(pin_y * mils_per_mm)
                    pin_side = {0: "R", 90: "D", 180: "L", 270: "U"}[pin_angle]
                elif token_name == "length":
                    pin_length = item[1]
                    # pin_length = round(mils_per_mm * pin_length)

            # Add the pins that were found to the total part. Include the unit identifier
            # in the pin so we can find it later when the part unit is created.
            part.add_pins(
                Pin(
                    name=pin_name,
                    num=pin_number,
                    func=pin_func,
                    unit=unit,
                    x=pin_x,
                    y=pin_y,
                    length=pin_length,
                    rotation=pin_angle,
                    orientation=pin_angle,
                )
            )

        # Return true if the symbol had pins.
        return bool(symbol_pins)
    
    def parse_draw_cmds(symbol):
        '''Return a list of graphic drawing commands contained in the symbol.'''
        return [
            item
            for item in symbol
            if item[0].value().lower()
            in ("arc", "bezier", "circle", "pin", "polyline", "rectangle", "text")
        ]
    
    # Parse top-level pins. (Any units with pins are parsed later.)
    top_has_pins = parse_pins(part.part_defn, unit=1)

    # Find all the units within a symbol. Skip the first item which is the
    # 'symbol' marking the start of the entire part definition.
    units = {
        item[1]: item[2:]
        for item in part.part_defn[1:]
        if item[0].value().lower() == "symbol"
    }

    # I'm assuming a part will not have both pins at the top level and units with pins.
    # The bool(units) will test for units within this part, while bool(part.unit)
    # will test for units in the part this part is extending.
    # This assertion will check that assumption.
    assert top_has_pins ^ (bool(units) or bool(part.unit)), "Top-level pins must be present if and only if there are no units."

    # If there are pins in the top-level part, then the part shouldn't have any units.
    # Therefore, make the part a unit of itself.
    if top_has_pins:
        part.make_unit("uA", unit=1)

    # Parse any graphics commands in the top-level part definition.
    part.draw_cmds[1].extend(parse_draw_cmds(part.part_defn))

    # Get pins and assign them to each unit as well as the entire part.
    # Also assign any graphic objects to each unit.
    unit_nums = []  # Stores unit numbers for units with pins.
    for unit_name, unit_data in units.items():
        # Extract the major and minor unit numbers from the last two numbers in the name.
        # A major number of 0 means the unit contains global stuff for all the other units,
        # but it isn't an actual usable unit itself. A non-global unit with a minor number
        # greater than 1 indicates a DeMorgan-equivalent unit.
        major, minor = [int(n) for n in unit_name.split("_")[-2:]]

        # Skip DeMorgan equivalent units.
        if major != 0 and minor > 1:
            continue

        # Get any graphic drawing commands for this unit.
        part.draw_cmds[major].extend(parse_draw_cmds(unit_data))

        # Save unit number if the unit has pins. Use this to create units
        # after the entire part is created.
        unit_has_pins = parse_pins(unit_data, unit=major)
        if major != 0 and unit_has_pins:
            unit_nums.append(major)

    # Copy drawing objects from the global unit with major id 0 to all the other units.
    if unit_nums:
        for unit_major, unit_draw_cmds in part.draw_cmds.items():
            if unit_major != 0:
                # Update non-global units with the global unit drawing commands.
                unit_draw_cmds.extend(part.draw_cmds.get(0, []))

    # Clear the part reference field directly. Don't use the setter function
    # since it will try to generate and assign a unique part reference if
    # passed a value of None.
    part._ref = None

    # Make sure all the pins have a valid reference to this part.
    part.associate_pins()

    # Create any units now that all the part pins have been added.
    for unit_num in unit_nums:
        unit_label = "u" + num_to_chars(unit_num)
        # Create a unit using pins with the same unit number.
        u = part.make_unit(unit_label, unit=unit_num)

    if len(part.unit) == 1:
        # If there's only one unit, that unit is the part itself.
        # Replace the PartUnit object with the parent Part object.
        unit_label = list(part.unit.keys())[0]
        part.rmv_unit(unit_label)
        part.unit[unit_label] = part
        part.num = 1
        add_unique_attr(part, unit_label, part)

    # Populate part fields from symbol properties. Properties will also be included below in drawing commands.
    props = {
        prop[1].lower(): prop for prop in part.part_defn if prop[0].value().lower() == "property"
    }
    part.ref_prefix = props["reference"][2]
    part.value = props["value"][2]
    part.fplist.append(props["footprint"][2])
    part.datasheet = props["datasheet"][2]
    part.draw_cmds[1].extend([props["reference"], props["value"]])

    # Construct the rest of the part attribute space, avoid part attributes that are already defined.
    part_dict = {
        k.replace(" ", "_").replace("/", "_"): v[2]
        for k, v in props.items()
        if k not in vars(part).keys()
    }
    for k, v in part_dict.items():
        setattr(part, k, v)

    # Part definition has been parsed, so clear it out to prevent parsing it again.
    part.part_defn = None
