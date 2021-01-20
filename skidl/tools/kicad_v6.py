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
Handler for reading Kicad libraries and generating netlists.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os.path
import re
import time
from builtins import dict, int, range, str, zip
from collections import namedtuple
from random import randint

from future import standard_library

from ..common import *
from ..coord import *
from ..defines import *
from ..logger import logger
from ..pckg_info import __version__
from ..scriptinfo import scriptinfo
from ..utilities import *

from .common_sexpr import parse_sexp

standard_library.install_aliases()


# These aren't used here, but they are used in modules
# that include this module.
tool_name = KICAD_V6
lib_suffix = ".kicad_sym"


def _load_sch_lib_(self, filename=None, lib_search_paths_=None, lib_section=None):
    """
    Load the parts from a KiCad schematic library file.

    Args:
        filename: The name of the KiCad schematic library file.
    """

    from ..skidl import lib_suffixes
    from ..part import Part

    # Try to open the file. Add a library file extension if needed. If the file
    # doesn't open, then try looking in the KiCad library directory.
    try:
        f, _ = find_and_open_file(filename, lib_search_paths_, lib_suffixes[tool_name])
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "Unable to open KiCad V6 Schematic Library File {} ({})".format(
                filename, str(e)
            )
        )

    # Parse the library and return a nested list of library parts.
    lib_sexp = ''.join(f.readlines())
    try:
        lib_list = parse_sexp(lib_sexp)
    except RunTimeError:
        raise RuntimeError(
            "The file {} is not a KiCad V6 Schematic Library File.\n".format(filename)
        )

    # Extract a list of parts.
    parts = [item for item in lib_list if item[0] == 'symbol']

    # Create Part objects for each part in library.
    for part in parts:
        # Remove any preceding library name from the part name.
        part_name = part[1].split(':', maxsplit=1)[-1]

        # Get part properties.
        properties = {item[1]: item[2] for item in part if item[0]=="property"}
        keywords=properties.get("ki_keywords", "")
        datasheet=properties.get("Datasheet", "")
        description=properties.get("ki_description", "")

        # Join the various text pieces by newlines so the ^ and $ special characters
        # can be used to detect the start and end of a piece of text during RE searches.
        search_text = "\n".join([filename, part_name, description, keywords])
        
        # Create a Part object and add it to the library object.
        self.add_parts(
            Part(
                part_defn = part,
                tool = tool_name,
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


def _parse_lib_part_(self, get_name_only=False):
    """
    Create a Part using a part definition from a KiCad V6 schematic library.

    Args:
        get_name_only: If true, scan the part definition until the
            name and aliases are found. The rest of the definition
            will be parsed if the part is actually used.
    """

    # For info on part library format, look at:
    # https://docs.google.com/document/d/1lyL_8FWZRouMkwqLiIt84rd2Htg4v1vz8_2MzRKHRkc/edit
    # https://gitlab.com/kicad/code/kicad/-/blob/master/eeschema/sch_plugins/kicad/sch_sexpr_parser.cpp

    from ..pin import Pin

    def numberize(v):
        """If possible, convert a string into a number."""
        try:
            return int(v)
        except ValueError:
            try:
                return float(v)
            except ValueError:
                pass
        return v  # Unable to convert to number. Return string.

    # Return if there's nothing to do (i.e., part has already been parsed).
    if not self.part_defn:
        return

    # If a part def already exists, the name has already been set, so exit.
    if get_name_only:
        return

    self.aliases = []  # Part aliases.
    self.fplist = []  # Footprint list.
    self.draw = []  # Drawing commands for symbol, including pins.

    for item in self.part_defn:
        if to_list(item)[0] == "extends":
            # Populate this part (child) from another part (parent) it is extended from.

            # Make a copy of the parent part from the library.
            parent_part_name = item[1]
            parent_part = self.lib[parent_part_name].copy(dest=TEMPLATE)

            # Remove parent attributes that we don't want to overwrite in the child.
            parent_part_dict = parent_part.__dict__
            for key in ("part_defn", "name", "aliases", "description", "datasheet", "keywords", "search_text"):
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
                cmd = to_list(item)[0]
                if cmd == 'del':
                    self.rmv_pins(item[1])
                elif cmd == 'swap':
                    self.swap_pins(item[1], item[2])
                elif cmd == 'renum':
                    self.renumber_pin(item[1], item[2])
                elif cmd == 'rename':
                    self.rename_pin(item[1], item[2])
                elif cmd == 'property_del':
                    del self.fields[item[1]]
                elif cmd == 'alternate':
                    pass

            break

    # Populate part fields from symbol properties.
    properties = {item[1]: item[2:] for item in self.part_defn if to_list(item)[0]=="property"}
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
        "unconnected": Pin.types.NOCONNECT,
    }

    # Find all the units within a symbol. Skip the first item which is the
    # 'symbol' marking the start of the entire part definition.
    units = [item for item in self.part_defn[1:] if to_list(item)[0] == 'symbol']
    self.num_units = len(units)

    # Get pins and assign them to each unit as well as the entire part.
    for unit in units:

        # Extract the part name, unit number, and conversion flag.
        unit_name = unit[1]
        symbol_name, unit_id, conversion_flag = unit_name.split("_")
        assert symbol_name == self.name
        unit_id = int(unit_id)
        conversion_flag = int(conversion_flag)

        # Don't add this unit to the part if the conversion flag is 0.
        if not conversion_flag:
            continue

        # Process the pins for the current unit.
        unit_pins = [item for item in unit if to_list(item)[0]=="pin"]
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
            self.add_pins(Pin(name=pin_name, num=pin_number, func=pin_func, unit=unit_id))

        # Create the unit within the part.
        unit_label = "u" + num_to_chars(unit_id)
        unit = self.make_unit(unit_label, unit=unit_id)

    # Clear the part reference field directly. Don't use the setter function
    # since it will try to generate and assign a unique part reference if
    # passed a value of None.
    self._ref = None

    # Make sure all the pins have a valid reference to this part.
    self.associate_pins()

    # Part definition has been parsed, so clear it out. This prevents a
    # part from being parsed more than once.
    self.part_defn = None


def _gen_netlist_(self):
    scr_dict = scriptinfo()
    src_file = os.path.join(scr_dict["dir"], scr_dict["source"])
    date = time.strftime("%m/%d/%Y %I:%M %p")
    tool = "SKiDL (" + __version__ + ")"
    template = (
        "(export (version D)\n"
        + "  (design\n"
        + '    (source "{src_file}")\n'
        + '    (date "{date}")\n'
        + '    (tool "{tool}"))\n'
    )
    netlist = template.format(**locals())
    netlist += "  (components"
    for p in sorted(self.parts, key=lambda p: str(p.ref)):
        netlist += "\n" + p.generate_netlist_component(KICAD)
    netlist += ")\n"
    netlist += "  (nets"
    for code, n in enumerate(sorted(self.get_nets(), key=lambda n: str(n.name))):
        n.code = code
        netlist += "\n" + n.generate_netlist_net(KICAD)
    netlist += ")\n)\n"
    return netlist


def _gen_netlist_comp_(self):
    ref = add_quotes(self.ref)

    value = add_quotes(self.value_str)

    try:
        footprint = self.footprint
    except AttributeError:
        logger.error("No footprint for {part}/{ref}.".format(part=self.name, ref=ref))
        footprint = "No Footprint"
    footprint = add_quotes(footprint)

    lib = add_quotes(getattr(self, "lib", "NO_LIB"))
    name = add_quotes(self.name)

    # Embed the hierarchy along with a random integer into the sheetpath for each component.
    # This enables hierarchical selection in pcbnew.
    hierarchy = add_quotes(
        "/"
        + getattr(self, "hierarchy", ".").replace(".", "/")
        + "/"
        + str(randint(0, 2 ** 64 - 1))
    )
    tstamps = hierarchy

    fields = ""
    for fld_name, fld_value in self.fields.items():
        fld_value = add_quotes(fld_value)
        if fld_value:
            fld_name = add_quotes(fld_name)
            fields += "\n        (field (name {fld_name}) {fld_value})".format(
                **locals()
            )
    if fields:
        fields = "      (fields" + fields
        fields += ")\n"

    template = (
        "    (comp (ref {ref})\n"
        + "      (value {value})\n"
        + "      (footprint {footprint})\n"
        + "{fields}"
        + "      (libsource (lib {lib}) (part {name}))\n"
        + "      (sheetpath (names {hierarchy}) (tstamps {tstamps})))"
    )
    txt = template.format(**locals())
    return txt


def _gen_netlist_net_(self):
    code = add_quotes(self.code)
    name = add_quotes(self.name)
    txt = "    (net (code {code}) (name {name})".format(**locals())
    for p in sorted(self.get_pins(), key=str):
        part_ref = add_quotes(p.part.ref)
        pin_num = add_quotes(p.num)
        txt += "\n      (node (ref {part_ref}) (pin {pin_num}))".format(**locals())
    txt += ")"
    return txt


def _gen_xml_(self):
    scr_dict = scriptinfo()
    src_file = os.path.join(scr_dict["dir"], scr_dict["source"])
    date = time.strftime("%m/%d/%Y %I:%M %p")
    tool = "SKiDL (" + __version__ + ")"
    template = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + '<export version="D">\n'
        + "  <design>\n"
        + "    <source>{src_file}</source>\n"
        + "    <date>{date}</date>\n"
        + "    <tool>{tool}</tool>\n"
        + "  </design>\n"
    )
    netlist = template.format(**locals())
    netlist += "  <components>"
    for p in self.parts:
        netlist += "\n" + p.generate_xml_component(KICAD)
    netlist += "\n  </components>\n"
    netlist += "  <nets>"
    for code, n in enumerate(self.get_nets()):
        n.code = code
        netlist += "\n" + n.generate_xml_net(KICAD)
    netlist += "\n  </nets>\n"
    netlist += "</export>\n"
    return netlist


def _gen_xml_comp_(self):
    ref = self.ref
    value = self.value_str

    try:
        footprint = self.footprint
    except AttributeError:
        logger.error("No footprint for {part}/{ref}.".format(part=self.name, ref=ref))
        footprint = "No Footprint"

    lib = add_quotes(getattr(self, "lib", "NO_LIB"))
    name = self.name

    fields = ""
    for fld_name, fld_value in self.fields.items():
        fld_value = add_quotes(fld_value)
        if fld_value:
            fld_name = add_quotes(fld_name)
            fields += "\n        (field (name {fld_name}) {fld_value})".format(
                **locals()
            )
    if fields:
        fields = "      <fields>" + fields
        fields += "\n      </fields>\n"

    template = (
        '    <comp ref="{ref}">\n'
        + "      <value>{value}</value>\n"
        + "      <footprint>{footprint}</footprint>\n"
        + "{fields}"
        + '      <libsource lib="{lib}" part="{name}"/>\n'
        + "    </comp>"
    )
    txt = template.format(**locals())
    return txt


def _gen_xml_net_(self):
    code = self.code
    name = self.name
    txt = '    <net code="{code}" name="{name}">'.format(**locals())
    for p in self.get_pins():
        part_ref = p.part.ref
        pin_num = p.num
        txt += '\n      <node ref="{part_ref}" pin="{pin_num}"/>'.format(**locals())
    txt += "\n    </net>"
    return txt


def _gen_svg_comp_(self, symtx, net_stubs=None):
    pass


def _gen_pinboxes_(self):
    """ Generate bounding box and I/O pin positions for each unit in a part. """
    pass


def _gen_schematic_(self, route):
    pass
