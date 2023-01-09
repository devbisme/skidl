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
from collections import OrderedDict

import sexpdata
from future import standard_library

from ...logger import active_logger

from ...utilities import num_to_chars, export_to_all

standard_library.install_aliases()


@export_to_all
def load_sch_lib(self, f, filename, lib_search_paths_):
    """
    Load the parts from a KiCad schematic library file.

    Args:
        filename: The name of the KiCad schematic library file.
    """

    from ...part import LIBRARY, Part
    from .. import KICAD

    # Parse the library and return a nested list of library parts.
    lib_txt = f.read()
    try:
        lib_txt = lib_txt.decode("latin_1")
    except AttributeError:
        # File contents were already decoded.
        pass

    lib_list = sexpdata.loads(lib_txt)

    # Skip over the 'kicad_symbol_lib' label and extract symbols into a dictionary with
    # symbol names as keys. Use an ordered dictionary to keep parts in the same order as
    # they appeared in the library file because in KiCad V6 library symbols can "extend"
    # previous symbols which should be processed before those that extend them.
    parts = OrderedDict(
        [
            (item[1], item[2:])
            for item in lib_list[1:]
            if item[0].value().lower() == "symbol"
        ]
    )

    # Create Part objects for each part in library.
    for part_name, part_defn in parts.items():

        properties = {}

        # See if this symbol extends a previous parent symbol.
        for item in part_defn:
            if item[0].value().lower() == "extends":
                # Get the properties from the parent symbol.
                parent_part = self[item[1]]
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
        self.add_parts(
            Part(
                part_defn=part_defn,
                tool=KICAD,
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


@export_to_all
def parse_lib_part(self, partial_parse):
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

    from ...part import TEMPLATE
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

    for item in self.part_defn:
        if item[0].value().lower() == "extends":
            # Populate this part (child) from another part (parent) it is extended from.

            # Make a copy of the parent part from the library.
            parent_part = self.lib[item[1]].copy(dest=TEMPLATE)

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
            for item in self.part_defn:
                cmd = item[0].value().lower()
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
        item[1]: item[2:]
        for item in self.part_defn
        if item[0].value().lower() == "property"
    }
    for name, data in properties.items():
        value = data[0]
        for item in data[1:]:
            if item[0].value().lower() == "id":
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
    units = {
        item[1]: item[2:]
        for item in self.part_defn[1:]
        if item[0].value().lower() == "symbol"
    }
    self.num_units = len(units)

    # Get pins and assign them to each unit as well as the entire part.
    unit_nums = []  # Stores unit numbers for units with pins.
    for unit_name, unit_data in units.items():

        # Extract the part name, unit number, and conversion flag.
        unit_name_pieces = unit_name.split("_")  # unit name follows 'symbol'
        symbol_name = "_".join(unit_name_pieces[:-2])
        assert symbol_name == self.name
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
                if item[0].value().lower() == "name":
                    pin_name = item[1]
                elif item[0].value().lower() == "number":
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


@export_to_all
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
