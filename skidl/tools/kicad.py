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

standard_library.install_aliases()


tool_name = KICAD
lib_suffix = ".lib"


def _load_sch_lib_(self, filename=None, lib_search_paths_=None):
    """
    Load the parts from a KiCad schematic library file.

    Args:
        filename: The name of the KiCad schematic library file.
    """

    from ..skidl import lib_suffixes
    from ..part import Part

    # Try to open the file. Add a .lib extension if needed. If the file
    # doesn't open, then try looking in the KiCad library directory.
    try:
        f, _ = find_and_open_file(filename, lib_search_paths_, lib_suffixes[KICAD])
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "Unable to open KiCad Schematic Library File {} ({})".format(
                filename, str(e)
            )
        )

    # Check the file header to make sure it's a KiCad library.
    header = []
    header = [f.readline()]
    if header and "EESchema-LIBRARY" not in header[0]:
        raise RuntimeError(
            "The file {} is not a KiCad Schematic Library File.\n".format(filename)
        )

    # Read the definition of each part line-by-line and then create
    # a Part object that gets stored in the part list.
    part_defn = []
    for line in f:

        # Skip over comments.
        if line.startswith("#"):
            pass

        # Look for the start of a part definition.
        elif line.startswith("DEF"):
            # Initialize the part definition with the first line.
            # This will also signal that succeeding lines should be added.
            part_defn = [line]
            part_name = line.split()[1]  # Get the part name.
            part_aliases = []

        # If gathering the part definition has begun, then continue adding lines.
        elif part_defn:
            part_defn.append(line)

            # Get aliases to add to search text.
            if line.startswith("ALIAS"):
                part_aliases = line.split()[1:]

            # If the current line ends this part definition, then create
            # the Part object and add it to the part list. Be sure to
            # indicate that the Part object is being added to a library
            # and not to a schematic netlist.
            # Also, add null attributes in case a DCM file is not
            # available for this part.
            if line.startswith("ENDDEF"):
                self.add_parts(
                    Part(
                        part_defn=part_defn,
                        tool=KICAD,
                        dest=LIBRARY,
                        filename=filename,
                        name=part_name,
                        aliases=part_aliases,
                        keywords="",
                        datasheet="",
                        description="",
                        search_text="",
                    )
                )

                # Clear the part definition in preparation for the next one.
                part_defn = []

    # Now add information from any associated DCM file.
    base_fn = os.path.splitext(filename)[0]  # Strip any extension.
    f, _ = find_and_open_file(base_fn, lib_search_paths_, ".dcm", allow_failure=True)
    if f:
        part_desc = {}
        for line in f:

            # Skip over comments.
            if line.startswith("#"):
                pass

            # Look for the start of a part description.
            elif line.startswith("$CMP"):
                part_desc["name"] = line.split()[-1]

            # If gathering the part definition has begun, then continue adding lines.
            elif part_desc:
                if line.startswith("D"):
                    part_desc["description"] = " ".join(line.split()[1:])
                elif line.startswith("K"):
                    part_desc["keywords"] = " ".join(line.split()[1:])
                elif line.startswith("F"):
                    part_desc["datasheet"] = " ".join(line.split()[1:])
                elif line.startswith("$ENDCMP"):
                    try:
                        part = self.get_part_by_name(
                            re.escape(part_desc["name"]),
                            silent=True,
                            get_name_only=True,
                        )
                    except Exception as e:
                        pass
                    else:
                        part.description = part_desc.get("description", "")
                        part.keywords = part_desc.get("keywords", "")
                        part.datasheet = part_desc.get("datasheet", "")
                    part_desc = {}
                else:
                    pass

    # Create text string to be used when searching for parts.
    for part in self.parts:
        search_text_pieces = [part.filename, part.name, part.description, part.keywords]
        search_text_pieces.extend(part.aliases)
        # Join the various text pieces by newlines so the ^ and $ special characters
        # can be used to detect the start and end of a piece of text during RE searches.
        part.search_text = "\n".join(search_text_pieces)


# Named tuples for part DRAW primitives.

DrawArc = namedtuple(
    "DrawArc",
    [
        "cx",
        "cy",
        "radius",
        "start_angle",
        "end_angle",
        "unit",
        "dmg",
        "thickness",
        "fill",
        "startx",
        "starty",
        "endx",
        "endy",
    ],
)

DrawCircle = namedtuple(
    "DrawCircle", ["cx", "cy", "radius", "unit", "dmg", "thickness", "fill"]
)

DrawPoly = namedtuple(
    "DrawPoly", ["point_count", "unit", "dmg", "thickness", "points", "fill"]
)

DrawRect = namedtuple(
    "DrawRect", ["x1", "y1", "x2", "y2", "unit", "dmg", "thickness", "fill",],
)

DrawText = namedtuple(
    "DrawText",
    [
        "angle",
        "x",
        "y",
        "size",
        "hidden",
        "unit",
        "dmg",
        "text",
        "italic",
        "bold",
        "halign",
        "valign",
    ],
)

DrawPin = namedtuple(
    "DrawPin",
    [
        "name",
        "num",
        "x",
        "y",
        "length",
        "orientation",
        "num_size",
        "name_size",
        "unit",
        "dmg",
        "electrical_type",
        "shape",
    ],
)


def _parse_lib_part_(self, get_name_only=False):
    """
    Create a Part using a part definition from a KiCad schematic library.

    This method was written based on the code from
    https://github.com/KiCad/kicad-library-utils/tree/master/schlib.
    It's covered by GPL3.

    Args:
        part_defn: A list of strings that define the part (usually read from a
            schematic library file). Can also be None.
        get_name_only: If true, scan the part definition until the
            name and aliases are found. The rest of the definition
            will be parsed if the part is actually used.
    """

    from ..pin import Pin

    _DEF_KEYS = [
        "name",
        "reference",
        "unused",
        "text_offset",
        "draw_pinnumber",
        "draw_pinname",
        "unit_count",
        "units_locked",
        "option_flag",
    ]
    _F0_KEYS = [
        "reference",
        "posx",
        "posy",
        "text_size",
        "text_orient",
        "visibility",
        "htext_justify",
        "vtext_justify",
    ]
    _FN_KEYS = [
        "name",
        "posx",
        "posy",
        "text_size",
        "text_orient",
        "visibility",
        "htext_justify",
        "vtext_justify",
        "fieldname",
    ]
    _ARC_KEYS = [
        "posx",
        "posy",
        "radius",
        "start_angle",
        "end_angle",
        "unit",
        "convert",
        "thickness",
        "fill",
        "startx",
        "starty",
        "endx",
        "endy",
    ]
    _CIRCLE_KEYS = ["posx", "posy", "radius", "unit", "convert", "thickness", "fill"]
    _POLY_KEYS = ["point_count", "unit", "convert", "thickness", "points", "fill"]
    _RECT_KEYS = [
        "startx",
        "starty",
        "endx",
        "endy",
        "unit",
        "convert",
        "thickness",
        "fill",
    ]
    _TEXT_KEYS = [
        "direction",
        "posx",
        "posy",
        "text_size",
        "text_type",
        "unit",
        "convert",
        "text",
        "italic",
        "bold",
        "hjustify",
        "vjustify",
    ]
    _PIN_KEYS = [
        "name",
        "num",
        "posx",
        "posy",
        "length",
        "direction",
        "name_text_size",
        "num_text_size",
        "unit",
        "convert",
        "electrical_type",
        "pin_type",
    ]
    _DRAW_KEYS = {
        "arcs": _ARC_KEYS,
        "circles": _CIRCLE_KEYS,
        "polylines": _POLY_KEYS,
        "rectangles": _RECT_KEYS,
        "texts": _TEXT_KEYS,
        "pins": _PIN_KEYS,
    }
    _DRAW_ELEMS = {
        "arcs": "A",
        "circles": "C",
        "polylines": "P",
        "rectangles": "S",
        "texts": "T",
        "pins": "X",
    }
    _KEYS = {
        "DEF": _DEF_KEYS,
        "F0": _F0_KEYS,
        "F": _FN_KEYS,
        "A": _ARC_KEYS,
        "C": _CIRCLE_KEYS,
        "P": _POLY_KEYS,
        "S": _RECT_KEYS,
        "T": _TEXT_KEYS,
        "X": _PIN_KEYS,
    }

    # Return if there's nothing to do (i.e., part has already been parsed).
    if not self.part_defn:
        return

    self.aliases = []  # Part aliases.
    self.fplist = []  # Footprint list.
    self.draw = []  # Drawing commands for symbol, including pins.

    building_fplist = False  # True when working on footprint list in defn.
    building_draw = False  # True when gathering part drawing from defn.

    pins = {}  # Dict of symbol pins to check for duplicates.

    # Regular expression for non-quoted and quoted text pieces.
    unqu = r'[^\s"]+'  # Word without spaces or double-quotes.
    qu = r'(?<!\\)".*?(?<!\\)"'  # Quoted string, possibly with escaped quotes.
    srch = "|".join([unqu + qu, qu, unqu])
    srch = re.compile(srch)

    # Go through the part definition line-by-line.
    for line in self.part_defn:

        # Split the line into words.
        line = line.replace("\n", "")

        # Extract all the non-quoted and quoted text pieces, accounting for escaped quotes.
        line = re.findall(srch, line)  # Replace line with list of pieces of line.

        # The first word indicates the type of part definition data that will follow.
        if line[0] in _KEYS:
            # Get the keywords for the current part definition data.
            key_list = _KEYS[line[0]]
            # Make a list of the values in the part data associated with each key.
            # Use an empty string for any missing values so every key will be
            # associated with something.
            values = line[1:] + ["" for _ in range(len(key_list) - len(line[1:]))]
            values = [rmv_quotes(v) for v in values]  # Remove any quotes from values.

        # Create a dictionary of part definition keywords and values.
        if line[0] == "DEF":
            self.definition = dict(list(zip(_DEF_KEYS, values)))
            self.name = self.definition["name"]

            # To handle libraries quickly, just get the name and
            # aliases and parse the rest of the part definition later.
            if get_name_only:
                if self.aliases:
                    # Name found, aliases already found so we're done.
                    return
                # Name found so scan defn to see if aliases are present.
                # (The majority of parts don't have aliases.)
                for ln in self.part_defn:
                    if re.match(r"^\s*ALIAS\s", ln):
                        # Found aliases, so store them.
                        self.aliases = re.findall(srch, ln)[1:]
                        return
                return

        # End the parsing of the part definition.
        elif line[0] == "ENDDEF":
            break

        # Create a dictionary of F0 part field keywords and values.
        elif line[0] == "F0":
            field_dict = dict(list(zip(_F0_KEYS, values)))
            # Add the field name and its value as an attribute to the part.
            self.fields["F0"] = field_dict["reference"]

        # Create a dictionary of the other part field keywords and values.
        elif line[0][0] == "F":
            # Make a list of field values with empty strings for missing fields.
            values = line[1:] + ["" for _ in range(len(_FN_KEYS) - len(line[1:]))]
            values = [rmv_quotes(v) for v in values]  # Remove any quotes from values.
            field_dict = dict(list(zip(_FN_KEYS, values)))
            # If no field name at end of line, use the field identifier F1, F2, ...
            field_dict["fieldname"] = field_dict["fieldname"] or line[0]
            # Add the field name and its value as an attribute to the part.
            self.fields[field_dict["fieldname"]] = field_dict["name"]

        # Create a list of part aliases.
        elif line[0] == "ALIAS":
            self.aliases = line[1:]

        # Start the list of part footprints.
        elif line[0] == "$FPLIST":
            building_fplist = True

        # End the list of part footprints.
        elif line[0] == "$ENDFPLIST":
            building_fplist = False

        # Start gathering the drawing primitives for the part symbol.
        elif line[0] == "DRAW":
            building_draw = True

        # End the gathering of drawing primitives.
        elif line[0] == "ENDDRAW":
            building_draw = False

        # Every other line is either a footprint or a drawing primitive.
        else:
            # If the footprint list is being built, then add this line to it.
            if building_fplist:
                self.fplist.append(
                    line[0].strip().rstrip()
                )  # Remove begin & end whitespace.

            # Else if the drawing primitives are being gathered, process the
            # current line to see what type of primitive is in play.
            elif building_draw:

                def numberize(v):
                    try:
                        return int(v)
                    except ValueError:
                        try:
                            return float(v)
                        except ValueError:
                            pass
                    return v

                values = [numberize(v) for v in values]

                # Gather arcs.
                if line[0] == "A":
                    self.draw.append(DrawArc(*values))

                # Gather circles.
                elif line[0] == "C":
                    self.draw.append(DrawCircle(*values))

                # Gather polygons.
                elif line[0] == "P":
                    n_points = values[0]
                    points = values[4 : 4 + (2 * n_points)]
                    values = values[0:4] + [points]
                    if len(line) > (5 + len(points)):
                        values += [line[-1]]
                    else:
                        values += [""]
                    self.draw.append(DrawPoly(*values))

                # Gather rectangles.
                elif line[0] == "S":
                    self.draw.append(DrawRect(*values))

                # Gather text.
                elif line[0] == "T":
                    self.draw.append(DrawText(*values))

                # Gather the pin symbols. This is what we really want since
                # this defines the names, numbers and attributes of the
                # pins associated with the part.
                elif line[0] == "X":
                    # Get the information for this pin.
                    values[0:2] = line[
                        1:3
                    ]  # Restore pin num & name in case they were made into integers.
                    pin = DrawPin(*values)
                    try:
                        # See if the pin number already exists for this part.
                        rpt_pin = pins[pin.num]
                    except KeyError:
                        # No, this pin number is unique (so far), so store it
                        # using the pin number as the dict key.
                        self.draw.append(pin)
                        pins[pin.num] = pin
                    else:
                        # Uh, oh: Repeated pin number! Check to see if the
                        # duplicated pins have the same I/O type and unit num.
                        if (
                            pin.electrical_type != rpt_pin.electrical_type
                            or pin.unit != rpt_pin.unit
                        ):
                            logger.warning(
                                "Non-identical pins with the same number ({}) in symbol drawing {}".format(
                                    pin.num, self.name
                                )
                            )

                # Found something unknown in the drawing section.
                else:
                    msg = "Found something strange in {} symbol drawing: {}.".format(
                        self.name, line
                    )
                    logger.warning(msg)

            # Found something unknown outside the footprint list or drawing section.
            else:
                msg = "Found something strange in {} symbol definition: {}.".format(
                    self.name, line
                )
                logger.warning(msg)

    # Define some shortcuts to part information.
    self.num_units = int(self.definition["unit_count"])  # # of units within the part.
    self.name = self.definition["name"]  # Part name (e.g., 'LM324').
    self.ref_prefix = self.definition["reference"]  # Part ref prefix (e.g., 'R').

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
        p.__dict__.update(kicad_pin._asdict())

        pin_type_translation = {
            "I": Pin.types.INPUT,
            "O": Pin.types.OUTPUT,
            "B": Pin.types.BIDIR,
            "T": Pin.types.TRISTATE,
            "P": Pin.types.PASSIVE,
            "U": Pin.types.UNSPEC,
            "W": Pin.types.PWRIN,
            "w": Pin.types.PWROUT,
            "C": Pin.types.OPENCOLL,
            "E": Pin.types.OPENEMIT,
            "N": Pin.types.NOCONNECT,
        }
        p.func = pin_type_translation[p.electrical_type]

        return p

    self.pins = [kicad_pin_to_pin(p) for p in pins.values()]

    # Make sure all the pins have a valid reference to this part.
    self.associate_pins()

    # Create part units if there are more than 1.
    if self.num_units > 1:
        for i in range(1, self.num_units + 1):
            self.make_unit("u" + num_to_chars(i), **{"unit": i})

    # Part definition has been parsed, so clear it out. This prevents a
    # part from being parsed more than once.
    self.part_defn = None


def _gen_netlist_(self):
    scr_dict = scriptinfo()
    src_file = os.path.join(
        scr_dict["dir"], scr_dict["source"]
    )  # pylint: disable=unused-variable
    date = time.strftime("%m/%d/%Y %I:%M %p")  # pylint: disable=unused-variable
    tool = "SKiDL (" + __version__ + ")"  # pylint: disable=unused-variable
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

    lib = add_quotes(getattr(self, "lib", "NO_LIB"))  # pylint: disable=unused-variable
    name = add_quotes(self.name)  # pylint: disable=unused-variable

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
    code = add_quotes(self.code)  # pylint: disable=unused-variable
    name = add_quotes(self.name)  # pylint: disable=unused-variable
    txt = "    (net (code {code}) (name {name})".format(**locals())
    for p in sorted(self.get_pins(), key=str):
        part_ref = add_quotes(p.part.ref)  # pylint: disable=unused-variable
        pin_num = add_quotes(p.num)  # pylint: disable=unused-variable
        txt += "\n      (node (ref {part_ref}) (pin {pin_num}))".format(**locals())
    txt += ")"
    return txt


def _gen_xml_(self):
    scr_dict = scriptinfo()
    src_file = os.path.join(
        scr_dict["dir"], scr_dict["source"]
    )  # pylint: disable=unused-variable
    date = time.strftime("%m/%d/%Y %I:%M %p")  # pylint: disable=unused-variable
    tool = "SKiDL (" + __version__ + ")"  # pylint: disable=unused-variable
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
        footprint = self.footprint  # pylint: disable=unused-variable
    except AttributeError:
        logger.error("No footprint for {part}/{ref}.".format(part=self.name, ref=ref))
        footprint = "No Footprint"

    lib = add_quotes(getattr(self, "lib", "NO_LIB"))  # pylint: disable=unused-variable
    name = self.name  # pylint: disable=unused-variable

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
    code = self.code  # pylint: disable=unused-variable
    name = self.name  # pylint: disable=unused-variable
    txt = '    <net code="{code}" name="{name}">'.format(**locals())
    for p in self.get_pins():
        part_ref = p.part.ref  # pylint: disable=unused-variable
        pin_num = p.num  # pylint: disable=unused-variable
        txt += '\n      <node ref="{part_ref}" pin="{pin_num}"/>'.format(**locals())
    txt += "\n    </net>"
    return txt


def _gen_svg_comp_(self):
    def draw_text(text, size, justify, origin, rotation, offset):
        return "<text font-size='{size}' class='text' text-anchor='{justify}' x='{origin.x}' y='{origin.y}' transform='rotate({rotation} {origin.x} {origin.y}) translate({offset.x} {offset.y})'>{text}</text>".format(
            **locals()
        )

    scale = 0.30

    PinDir = namedtuple(
        "PinDir",
        "direction side angle num_justify name_justify num_offset name_offset",
    )
    h_offset = 50
    pin_dir_tbl = {
        "U": PinDir(
            Point(0, -1), "bottom", -90, "end", "start", Point(-h_offset, -0.3), Point(h_offset, 0.5)
        ),
        "D": PinDir(
            Point(0, 1), "top", -90, "start", "end", Point(h_offset, -0.3), Point(-h_offset, 0.5)
        ),
        "L": PinDir(
            Point(-1, 0), "right", 0, "start", "end", Point(h_offset, -0.3), Point(-h_offset, 0.5)
        ),
        "R": PinDir(
            Point(1, 0), "left", 0, "end", "start", Point(-h_offset, -0.3), Point(h_offset, 0.5)
        ),
    }

    fill_tbl = {
        "F": "#000",  # Black fill.
        "f": "#ffc"   # Light-yellow fill.
    }

    bbox = BBox()
    svg = ['<g s:type="{}">'.format(self.name)]
    svg.append('<s:alias val="{}"/>'.format(self.name))
    for obj in self.draw:
        if isinstance(obj, DrawArc):
            arc = obj
            center = Point(arc.cx, -arc.cy) * scale
            radius = arc.radius * scale
            start = Point(arc.startx, -arc.starty) * scale
            end = Point(arc.endx, -arc.endy) * scale
            start_angle = arc.start_angle / 10
            end_angle = arc.end_angle / 10
            clock_wise = int(end_angle < start_angle)
            large_arc = int(abs(end_angle - start_angle) > 180)
            thickness = max(arc.thickness * scale, 1)
            fill = fill_tbl.get(arc.fill, "")
            radius_pt = Point(radius, radius)
            bbox.add(center - radius_pt)
            bbox.add(center + radius_pt)
            svg.append(
                '<path d="M {start.x} {start.y} A {radius} {radius} 0 {large_arc} {clock_wise} {end.x} {end.y}" style="stroke-width:{thickness}; fill:{fill}" class="$cell_id symbol"/>'.format(
                    **locals()
                )
            )
        elif isinstance(obj, DrawCircle):
            circle = obj
            center = Point(circle.cx, -circle.cy) * scale
            radius = circle.radius * scale
            thickness = max(circle.thickness * scale, 1)
            fill = fill_tbl.get(circle.fill, "")
            radius_pt = Point(radius, radius)
            bbox.add(center - radius_pt)
            bbox.add(center + radius_pt)
            svg.append(
                '<circle cx="{center.x}" cy="{center.y}" r="{radius}" style="stroke-width:{thickness}; fill:{fill}" class="$cell_id symbol"/>'.format(
                    **locals()
                )
            )
        elif isinstance(obj, DrawPoly):
            poly = obj
            pts = [Point(x, -y) for x, y in zip(poly.points[0::2], poly.points[1::2])]
            path = [
                '<path d="',
            ]
            path_op = "M"
            for pt in pts:
                pt = pt * scale
                bbox.add(pt)
                path.append("{path_op} {pt.x} {pt.y} ".format(**locals()))
                path_op = "L"
            path.append('" ')
            thickness = max(poly.thickness * scale, 1)
            fill = fill_tbl.get(poly.fill, "")
            path.append(
                'style="stroke-width:{thickness}; fill:{fill}" class="$cell_id symbol"'.format(**locals())
            )
            path.append("/>")
            svg.append("".join(path))
        elif isinstance(obj, DrawRect):
            rect = obj
            start = Point(rect.x1, -rect.y1)
            start = start * scale
            end = Point(rect.x2, -rect.y2)
            end = end * scale
            bbox.add(start)
            bbox.add(end)
            rect_bbox = BBox()
            rect_bbox.add(start)
            rect_bbox.add(end)
            thickness = max(rect.thickness * scale, 1)
            fill = fill_tbl.get(rect.fill, "")
            svg.append(
                '<rect x="{rect_bbox.min.x}" y="{rect_bbox.min.y}" width="{rect_bbox.w}" height="{rect_bbox.h}" style="stroke-width:{thickness}; fill:{fill}" class="$cell_id symbol"/>'.format(
                    **locals()
                )
            )
        elif isinstance(obj, DrawText):
            text = obj
            origin = Point(text.x, -text.y) * scale
            angle = text.angle
            size = text.size * scale
            style = "font-size: {size} ".format(**locals())
            justify = {"L": "start", "C": "middle", "R": "end"}[text.halign]
            offset = {"T": Point(0, 1), "B": Point(0, 0), "C": Point(0, 0.5)}[
                text.valign
            ] * size * scale
            svg.append(draw_text(text.text, size, justify, origin, angle, offset))
        elif isinstance(obj, DrawPin):
            pin = obj
            try:
                if pin.shape[0] == "N":
                    continue  # Skip invisible pins
            except IndexError:
                pass  # No pin shape given, so it is visible by default.

            # Start pin group.
            start = Point(pin.x, -pin.y) * scale
            side = pin_dir_tbl[pin.orientation].side
            svg.append(
                '<g s:x="{start.x}" s:y="{start.y}" s:pid="{pin.num}" s:position="{side}">'.format(
                    **locals()
                )
            )

            # Create line for pin lead.
            l = pin.length * scale
            dir = pin_dir_tbl[pin.orientation].direction
            end = start + dir * l
            bbox.add(start)
            bbox.add(end)
            # class_ = "$cell_id connect"
            svg.append(
                '<path d="M {start.x} {start.y} L {end.x} {end.y}" class="$cell_id connec"/>'.format(
                    **locals()
                )
            )

            # Create pin number.
            angle = pin_dir_tbl[pin.orientation].angle
            num_justify = pin_dir_tbl[pin.orientation].num_justify
            num_size = pin.num_size * scale
            num_offset = pin_dir_tbl[pin.orientation].num_offset
            num_offset.y = num_offset.y * num_size
            num_offset = num_offset * scale
            svg.append(
                draw_text(str(pin.num), num_size, num_justify, end, angle, num_offset)
            )

            # Create pin name.
            if pin.name != "~":
                name_justify = pin_dir_tbl[pin.orientation].name_justify
                name_size = pin.name_size * scale
                name_offset = pin_dir_tbl[pin.orientation].name_offset
                name_offset.y = name_offset.y * name_size
                name_offset = name_offset * scale
                svg.append(
                    draw_text(
                        str(pin.name), name_size, name_justify, end, angle, name_offset
                    )
                )

            svg.append("</g>")

        else:
            logger.error(
                "Unknown graphical object {} in part symbol {}.".format(
                    type(obj), self.name
                )
            )
    svg.append("</g>")
    svg[
        0
    ] = '<g s:type="{self.name}" s:width="{bbox.w}" s:height="{bbox.h}" transform="translate(0,0)">'.format(
        **locals()
    )
    return "\n".join(svg)

