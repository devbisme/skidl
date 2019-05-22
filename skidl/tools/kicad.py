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
import time
from random import randint

from ..py_2_3 import *
from ..defines import *
from ..utilities import *
from ..pckg_info import __version__

tool_name = KICAD
lib_suffix = '.lib'


def _load_sch_lib_(self, filename=None, lib_search_paths_=None):
    """
    Load the parts from a KiCad schematic library file.

    Args:
        filename: The name of the KiCad schematic library file.
    """

    from ..skidl import lib_suffixes
    from ..Part import Part

    # Try to open the file. Add a .lib extension if needed. If the file
    # doesn't open, then try looking in the KiCad library directory.
    try:
        f, _ = find_and_open_file(filename, lib_search_paths_, lib_suffixes[KICAD])
    except Exception as e:
        raise Exception(
            'Unable to open KiCad Schematic Library File {} ({})'.format(
                filename, str(e)))

    # Check the file header to make sure it's a KiCad library.
    header = []
    header = [f.readline()]
    if header and 'EESchema-LIBRARY' not in header[0]:
        raise Exception(
            'The file {} is not a KiCad Schematic Library File.\n'.format(
                filename))

    # Read the definition of each part line-by-line and then create
    # a Part object that gets stored in the part list.
    part_defn = []
    for line in f:

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
                self.add_parts(
                    Part(part_defn=part_defn, tool=KICAD, dest=LIBRARY))

                # Clear the part definition in preparation for the next one.
                part_defn = []

    # Now add information from any associated DCM file.
    filename = os.path.splitext(filename)[0]  # Strip any extension.
    f, _ = find_and_open_file(
        filename, lib_search_paths_, '.dcm', allow_failure=True)
    if not f:
        return

    part_desc = {}
    for line in f:

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
                    part = self.get_part_by_name(
                        part_desc['name'], silent=True)
                except Exception:
                    pass
                else:
                    part.description = part_desc.get('description', '')
                    part.keywords = part_desc.get('keywords', '')
                part_desc = {}
            else:
                pass

def _parse_lib_part_(self, just_get_name=False):
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

    from ..Pin import Pin

    _DEF_KEYS = [
        'name', 'reference', 'unused', 'text_offset', 'draw_pinnumber',
        'draw_pinname', 'unit_count', 'units_locked', 'option_flag'
    ]
    _F0_KEYS = [
        'reference', 'posx', 'posy', 'text_size', 'text_orient',
        'visibility', 'htext_justify', 'vtext_justify'
    ]
    _FN_KEYS = [
        'name', 'posx', 'posy', 'text_size', 'text_orient', 'visibility',
        'htext_justify', 'vtext_justify', 'fieldname'
    ]
    _ARC_KEYS = [
        'posx', 'posy', 'radius', 'start_angle', 'end_angle', 'unit',
        'convert', 'thickness', 'fill', 'startx', 'starty', 'endx', 'endy'
    ]
    _CIRCLE_KEYS = [
        'posx', 'posy', 'radius', 'unit', 'convert', 'thickness', 'fill'
    ]
    _POLY_KEYS = [
        'point_count', 'unit', 'convert', 'thickness', 'points', 'fill'
    ]
    _RECT_KEYS = [
        'startx', 'starty', 'endx', 'endy', 'unit', 'convert', 'thickness',
        'fill'
    ]
    _TEXT_KEYS = [
        'direction', 'posx', 'posy', 'text_size', 'text_type', 'unit',
        'convert', 'text', 'italic', 'bold', 'hjustify', 'vjustify'
    ]
    _PIN_KEYS = [
        'name', 'num', 'posx', 'posy', 'length', 'direction',
        'name_text_size', 'num_text_size', 'unit', 'convert',
        'electrical_type', 'pin_type'
    ]
    _DRAW_KEYS = {
        'arcs': _ARC_KEYS,
        'circles': _CIRCLE_KEYS,
        'polylines': _POLY_KEYS,
        'rectangles': _RECT_KEYS,
        'texts': _TEXT_KEYS,
        'pins': _PIN_KEYS
    }
    _DRAW_ELEMS = {
        'arcs': 'A',
        'circles': 'C',
        'polylines': 'P',
        'rectangles': 'S',
        'texts': 'T',
        'pins': 'X'
    }
    _KEYS = {
        'DEF': _DEF_KEYS,
        'F0': _F0_KEYS,
        'F': _FN_KEYS,
        'A': _ARC_KEYS,
        'C': _CIRCLE_KEYS,
        'P': _POLY_KEYS,
        'S': _RECT_KEYS,
        'T': _TEXT_KEYS,
        'X': _PIN_KEYS
    }

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
        'pins': {}  # Use pin number as key to detect duplicates.
    }
    self.fplist = []

    # Go through the part definition line-by-line.
    for line in self.part_defn:

        # Split the line into words.

        line = line.replace('\n', '')

        # Extract all the non-quoted and quoted text pieces, accounting for escaped quotes.
        unqu = r'[^\s"]+'  # Word without spaces or double-quotes.
        qu = r'(?<!\\)".*?(?<!\\)"'  # Quoted string, possibly with escaped quotes.
        srch = '|'.join([unqu + qu, qu, unqu])
        line = re.findall(
            srch, line)  # Replace line with list of pieces of line.

        # The first word indicates the type of part definition data that will follow.
        if line[0] in _KEYS:
            # Get the keywords for the current part definition data.
            key_list = _KEYS[line[0]]
            # Make a list of the values in the part data associated with each key.
            # Use an empty string for any missing values so every key will be
            # associated with something.
            values = line[1:] + [
                '' for _ in range(len(key_list) - len(line[1:]))
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
                for ln in self.part_defn:
                    if re.match(r'^\s*ALIAS\s', ln):
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
                '' for _ in range(len(_FN_KEYS) - len(line[1:]))
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
                    self.draw['arcs'].append(
                        dict(list(zip(_ARC_KEYS, values))))

                # Gather circles.
                elif line[0] == 'C':
                    self.draw['circles'].append(
                        dict(list(zip(_CIRCLE_KEYS, values))))

                # Gather polygons.
                elif line[0] == 'P':
                    n_points = int(line[1])
                    points = line[5:5 + (2 * n_points)]
                    values = line[1:5] + [points]
                    if len(line) > (5 + len(points)):
                        values += [line[-1]]
                    else:
                        values += ['']
                    self.draw['polylines'].append(
                        dict(list(zip(_POLY_KEYS, values))))

                # Gather rectangles.
                elif line[0] == 'S':
                    self.draw['rectangles'].append(
                        dict(list(zip(_RECT_KEYS, values))))

                # Gather text.
                elif line[0] == 'T':
                    self.draw['texts'].append(
                        dict(list(zip(_TEXT_KEYS, values))))

                # Gather the pin symbols. This is what we really want since
                # this defines the names, numbers and attributes of the
                # pins associated with the part.
                elif line[0] == 'X':
                    # Get the information for this pin.
                    pin = dict(list(zip(_PIN_KEYS, values)))
                    try:
                        # See if the pin number already exists for this part.
                        rpt_pin = self.draw['pins'][pin['num']]
                    except KeyError:
                        # No, this pin number is unique (so far), so store it
                        # using the pin number as the dict key.
                        self.draw['pins'][pin['num']] = pin
                    else:
                        # Uh, oh: Repeated pin number! Check to see if the 
                        # duplicated pins have the same I/O type and unit num.
                        if (pin['electrical_type'] != rpt_pin['electrical_type'] or
                            pin['unit'] != rpt_pin['unit']):
                            logger.warning('Non-identical pins with the same number ({}) in symbol drawing {}'.format(pin['num'], self.name))

                # Found something unknown in the drawing section.
                else:
                    msg = 'Found something strange in {} symbol drawing: {}.'.format(
                        self.name, line)
                    logger.warning(msg)

            # Found something unknown outside the footprint list or drawing section.
            else:
                msg = 'Found something strange in {} symbol definition: {}.'.format(
                    self.name, line)
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

        pin_type_translation = {
            'I': Pin.types.INPUT,
            'O': Pin.types.OUTPUT,
            'B': Pin.types.BIDIR,
            'T': Pin.types.TRISTATE,
            'P': Pin.types.PASSIVE,
            'U': Pin.types.UNSPEC,
            'W': Pin.types.PWRIN,
            'w': Pin.types.PWROUT,
            'C': Pin.types.OPENCOLL,
            'E': Pin.types.OPENEMIT,
            'N': Pin.types.NOCONNECT
        }
        p.func = pin_type_translation[p.electrical_type]  # pylint: disable=no-member, attribute-defined-outside-init

        return p

    self.pins = [kicad_pin_to_pin(p) for p in self.draw['pins'].values()]

    # Make sure all the pins have a valid reference to this part.
    self.associate_pins()

    # Create part units if there are more than 1.
    if self.num_units > 1:
        for i in range(1, self.num_units+1):
            self.make_unit('u'+num_to_chars(i), **{'unit': i})

    # Part definition has been parsed, so clear it out. This prevents a
    # part from being parsed more than once.
    self.part_defn = None

def _gen_netlist_(self):
    scr_dict = scriptinfo()
    src_file = os.path.join(scr_dict['dir'], scr_dict['source'])  # pylint: disable=unused-variable
    date = time.strftime('%m/%d/%Y %I:%M %p')  # pylint: disable=unused-variable
    tool = 'SKiDL (' + __version__ + ')'  # pylint: disable=unused-variable
    template = '(export (version D)\n' + \
               '  (design\n' + \
               '    (source "{src_file}")\n' + \
               '    (date "{date}")\n' + \
               '    (tool "{tool}"))\n'
    netlist = template.format(**locals())
    netlist += "  (components"
    for p in sorted(self.parts, key=lambda p: str(p.ref)):
        netlist += '\n' + p.generate_netlist_component(KICAD)
    netlist += ")\n"
    netlist += "  (nets"
    for code, n in enumerate(
            sorted(self.get_nets(), key=lambda n: str(n.name))):
        n.code = code
        netlist += '\n' + n.generate_netlist_net(KICAD)
    netlist += ")\n)\n"
    return netlist

def _gen_netlist_comp_(self):
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

    lib = add_quotes(getattr(self, 'lib', 'NO_LIB'))  # pylint: disable=unused-variable
    name = add_quotes(self.name)  # pylint: disable=unused-variable

    # Embed the hierarchy along with a random integer into the sheetpath for each component.
    # This enables hierarchical selection in pcbnew.
    hierarchy = add_quotes('/'+getattr(self,'hierarchy','.').replace('.','/')+'/'+str(randint(0,2**64-1)))
    tstamps = hierarchy

    fields = ''
    for fld_name in self._get_fields():
        fld_value = add_quotes(self.__dict__[fld_name])
        if fld_value:
            fld_name = add_quotes(fld_name)
            fields += '\n        (field (name {fld_name}) {fld_value})'.format(
                **locals())
    if fields:
        fields = '      (fields' + fields
        fields += ')\n'

    template = '    (comp (ref {ref})\n' + \
               '      (value {value})\n' + \
               '      (footprint {footprint})\n' + \
               '{fields}' + \
               '      (libsource (lib {lib}) (part {name}))\n' + \
               '      (sheetpath (names {hierarchy}) (tstamps {tstamps})))'
    txt = template.format(**locals())
    return txt

def _gen_netlist_net_(self):
    code = add_quotes(self.code)  # pylint: disable=unused-variable
    name = add_quotes(self.name)  # pylint: disable=unused-variable
    txt = '    (net (code {code}) (name {name})'.format(**locals())
    for p in sorted(self.get_pins(), key=str):
        part_ref = add_quotes(p.part.ref)  # pylint: disable=unused-variable
        pin_num = add_quotes(p.num)  # pylint: disable=unused-variable
        txt += '\n      (node (ref {part_ref}) (pin {pin_num}))'.format(
            **locals())
    txt += ')'
    return txt

def _gen_xml_(self):
    scr_dict = scriptinfo()
    src_file = os.path.join(scr_dict['dir'], scr_dict['source'])  # pylint: disable=unused-variable
    date = time.strftime('%m/%d/%Y %I:%M %p')  # pylint: disable=unused-variable
    tool = 'SKiDL (' + __version__ + ')'  # pylint: disable=unused-variable
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
        netlist += '\n' + p.generate_xml_component(KICAD)
    netlist += '\n  </components>\n'
    netlist += '  <nets>'
    for code, n in enumerate(self.get_nets()):
        n.code = code
        netlist += '\n' + n.generate_xml_net(KICAD)
    netlist += '\n  </nets>\n'
    netlist += '</export>\n'
    return netlist

def _gen_xml_comp_(self):
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
        footprint = self.footprint  # pylint: disable=unused-variable
    except AttributeError:
        logger.error('No footprint for {part}/{ref}.'.format(
            part=self.name, ref=ref))
        footprint = 'No Footprint'

    lib = add_quotes(getattr(self, 'lib', 'NO_LIB'))  # pylint: disable=unused-variable
    name = self.name  # pylint: disable=unused-variable

    fields = ''
    for fld_name in self._get_fields():
        fld_value = self.__dict__[fld_name]
        if fld_value:
            fields += '\n        <field name="{fld_name}">{fld_value}</field>'.format(
                **locals())
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

def _gen_xml_net_(self):
    code = self.code  # pylint: disable=unused-variable
    name = self.name  # pylint: disable=unused-variable
    txt = '    <net code="{code}" name="{name}">'.format(**locals())
    for p in self.get_pins():
        part_ref = p.part.ref  # pylint: disable=unused-variable
        pin_num = p.num  # pylint: disable=unused-variable
        txt += '\n      <node ref="{part_ref}" pin="{pin_num}"/>'.format(
            **locals())
    txt += '\n    </net>'
    return txt
