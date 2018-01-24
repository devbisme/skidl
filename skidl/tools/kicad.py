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

import os.path
import time
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
        f = find_and_open_file(filename, lib_search_paths_, lib_suffixes[KICAD])
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
    for line in f.readlines():

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
    f = find_and_open_file(
        filename, lib_search_paths_, '.dcm', allow_failure=True)
    if not f:
        return

    part_desc = {}
    for line in f.readlines():

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
