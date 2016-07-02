# -*- coding: utf-8 -*-

# MIT license
# 
# Copyright (C) 2016 by XESS Corp.
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

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import sys
import os
import re
import logging
from copy import deepcopy
from pprint import pprint
import pdb

logger = logging.getLogger('schdl')

USING_PYTHON2 = (sys.version_info.major == 2)
USING_PYTHON3 = not USING_PYTHON2

DEBUG_OVERVIEW = logging.DEBUG
DEBUG_DETAILED = logging.DEBUG - 1
DEBUG_OBSESSIVE = logging.DEBUG - 2

#
# This code was taken from https://github.com/KiCad/kicad-library-utils/tree/master/schlib.
# It's covered by GPL3.
#

from builtins import str
from builtins import zip
from builtins import range
from builtins import object

import sys
import shlex
import os.path
import re


def to_list(x):
    '''
    Return x if it is already a list, or return a list if x is a scalar.
    '''
    if isinstance(x, (list, tuple)):
        return x  # Already a list, so just return it.
    return [x]  # Wasn't a list, so make it into one.


def list_to_scalar(lst):
    '''
    '''
    if isinstance(lst, (list, tuple)):
        if len(lst) > 1:
            return lst  # Multi-element list, so return it unchanged.
        if len(lst) == 1:
            return lst[0]  # Single-element list, so return the scalar element.
        return None  # Empty list, so return None.
    return lst  # Must have been a scalar, so return that.


def filter(lst, **kwargs):
    '''
    Return a list of objects extracted from a list whose attributes match a 
    set of criteria. The match is done using regular expressions.
    Example: filter(pins, name='io[0-9]+', direction='bidir') will
    return all the bidirectional pins of the component that have pin names
    starting with 'io' followed by a number (e.g., 'IO45').
    '''
    extract = []
    for item in lst:
        for k, v in kwargs.items():
            # Break out of the loop if any of the item's given attributes doesn't match.
            if not re.fullmatch(v, getattr(item, k), flags=re.IGNORECASE):
                break
        else:
            # If we get here, then all the item attributes matched and the
            # for loop didn't break, so add this item to the list.
            extract.append(item)
    return extract


class SchLib(object):
    """
    A class to parse schematic library files into a list of Parts.
    """

    def __init__(self, filename=None, tool='kicad'):
        self.load_kicad_sch_lib(filename)

    def load_kicad_sch_lib(self, filename=None):
        self.filename = filename
        self.parts = []

        try:
            f = open(filename)
        except (FileNotFoundError, TypeError):
            sys.stderr.write('Error opening file: {}\n'.format(filename))
            return

        header = []
        header = [f.readline()]
        if header and 'EESchema-LIBRARY' not in header[0]:
            sys.stderr.write(
                'The file is not a KiCad Schematic Library File\n')
            return

        part_data = []
        for line in f.readlines():

            if line.startswith('#'):
                pass

            elif line.startswith('DEF'):
                part_data = [line]

            elif len(part_data) > 0:
                part_data.append(line)
                if line.startswith('ENDDEF'):
                    self.parts.append(Part(data=part_data, tool='kicad'))
                    part_data = []

    def get_parts(self, **kwargs):
        '''
        Return a list of parts that match a list of criteria.
        Return a Part object if only a single match is found.
        '''
        return list_to_scalar(filter(self.parts, **kwargs))

    def get_part_by_name(self, name):
        return self.get_parts(name=name)

    def __getitem__(self, name):
        return self.get_part_by_name(name)


class Pin(object):
    def __init__(self):
        self.net = None

    def __add__(self, net):
        if self.net and self.net != net:
            raise Exception("Can't assign multiple nets ({} and {}) to pin {}-{} of part {}-{}!".format(self.net.name, net.name, self.num, self.name, self.part.ref, self.part.name))
        self.net = net
        net += self
        return self


class Part(object):
    """
    Schematic part class.
    """

    def __init__(self, lib=None, name=None, data=None, tool='kicad', connections=None, **kwargs):
        if lib:
            self.load(lib, name, tool)
        elif data:
            self.create_part_from_kicad(data, tool)
        else:
            raise Exception(
                "Can't make a part without a library & part name or some part data.")
        if isinstance(connections, type({})):
            for pin, net in connections.items():
                net += self[pin]
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def copy(self, num_copies):
        copies = []
        if not isinstance(num_copies,int):
            raise Exception("Can't make a non-integer number ({}) of copies of a part!".format(num_copies))
        for i in range(num_copies):
            cpy = deepcopy(self)
            for i, pin in enumerate(cpy.pins):
                pin.part = cpy
                pin.net = None
                original_net = self.pins[i].net
                if original_net:
                    original_net += pin
            copies.append(cpy)
        return copies

    def __mul__(self, num_copies):
        return self.copy(num_copies)

    def __rmul__(self, num_copies):
        return self.copy(num_copies)

    def load(self, lib, name, tool):
        if isinstance(lib, type('')):
            lib = SchLib(filename=lib, tool=tool)
        part = deepcopy(lib.get_part_by_name(name))
        self.__dict__.update(part.__dict__)  # Overwrite self with the new part.
        # Update the reference in each pin to point to the copied part.
        for p in self.pins:
            p.part = self

    def create_part_from_kicad(self, data, tool):
        _DEF_KEYS = ['name', 'reference', 'unused', 'text_offset',
                     'draw_pinnumber', 'draw_pinname', 'unit_count',
                     'units_locked', 'option_flag']
        _F0_KEYS = ['reference', 'posx', 'posy', 'text_size', 'text_orient',
                    'visibility', 'htext_justify', 'vtext_justify']
        _FN_KEYS = ['name', 'posx', 'posy', 'text_size', 'text_orient',
                    'visibility', 'htext_justify', 'vtext_justify',
                    'fieldname']
        _ARC_KEYS = ['posx', 'posy', 'radius', 'start_angle', 'end_angle',
                     'unit', 'convert', 'thickness', 'fill', 'startx',
                     'starty', 'endx', 'endy']
        _CIRCLE_KEYS = ['posx', 'posy', 'radius', 'unit', 'convert',
                        'thickness', 'fill']
        _POLY_KEYS = ['point_count', 'unit', 'convert', 'thickness', 'points',
                      'fill']
        _RECT_KEYS = ['startx', 'starty', 'endx', 'endy', 'unit', 'convert',
                      'thickness', 'fill']
        _TEXT_KEYS = ['direction', 'posx', 'posy', 'text_size', 'text_type',
                      'unit', 'convert', 'text', 'italic', 'bold', 'hjustify',
                      'vjustify']
        _PIN_KEYS = ['name', 'num', 'posx', 'posy', 'length', 'direction',
                     'name_text_size', 'num_text_size', 'unit', 'convert',
                     'electrical_type', 'pin_type']
        _DRAW_KEYS = {'arcs': _ARC_KEYS,
                      'circles': _CIRCLE_KEYS,
                      'polylines': _POLY_KEYS,
                      'rectangles': _RECT_KEYS,
                      'texts': _TEXT_KEYS,
                      'pins': _PIN_KEYS}
        _DRAW_ELEMS = {'arcs': 'A',
                       'circles': 'C',
                       'polylines': 'P',
                       'rectangles': 'S',
                       'texts': 'T',
                       'pins': 'X'}
        _KEYS = {'DEF': _DEF_KEYS,
                 'F0': _F0_KEYS,
                 'F': _FN_KEYS,
                 'A': _ARC_KEYS,
                 'C': _CIRCLE_KEYS,
                 'P': _POLY_KEYS,
                 'S': _RECT_KEYS,
                 'T': _TEXT_KEYS,
                 'X': _PIN_KEYS}

        self.fplist = []
        self.aliases = []
        building_fplist = False
        building_draw = False
        for line in data:
            line = line.replace('\n', '')
            s = shlex.shlex(line)
            s.whitespace_split = True
            s.commenters = ''
            s.quotes = '"'
            line = list(s)

            if line[0] in _KEYS:
                key_list = _KEYS[line[0]]
                values = line[1:] + [
                    '' for n in range(len(key_list) - len(line[1:]))
                ]

            if line[0] == 'DEF':
                self.definition = dict(list(zip(_DEF_KEYS, values)))

            elif line[0] == 'F0':
                self.fields = []
                self.fields.append(dict(list(zip(_F0_KEYS, values))))

            elif line[0][0] == 'F':
                values = line[1:] + [
                    '' for n in range(len(_FN_KEYS) - len(line[1:]))
                ]
                self.fields.append(dict(list(zip(_FN_KEYS, values))))

            elif line[0] == 'ALIAS':
                self.aliases = [alias for alias in line[1:]]

            elif line[0] == '$FPLIST':
                building_fplist = True
                self.fplist = []

            elif line[0] == '$ENDFPLIST':
                building_fplist = False

            elif line[0] == 'DRAW':
                building_draw = True
                self.draw = {
                    'arcs': [],
                    'circles': [],
                    'polylines': [],
                    'rectangles': [],
                    'texts': [],
                    'pins': []
                }

            elif line[0] == 'ENDDRAW':
                building_draw = False

            else:
                if building_fplist:
                    self.fplist.append(line[0])

                elif building_draw:
                    if line[0] == 'A':
                        self.draw['arcs'].append(dict(list(zip(_ARC_KEYS,
                                                               values))))
                    if line[0] == 'C':
                        self.draw['circles'].append(dict(list(zip(_CIRCLE_KEYS,
                                                                  values))))
                    if line[0] == 'P':
                        n_points = int(line[1])
                        points = line[5:5 + (2 * n_points)]
                        values = line[1:5] + [points]
                        if len(line) > (5 + len(points)):
                            values += [line[-1]]
                        else:
                            values += ['']
                        self.draw['polylines'].append(dict(list(zip(_POLY_KEYS,
                                                                    values))))
                    if line[0] == 'S':
                        self.draw['rectangles'].append(dict(list(zip(
                            _RECT_KEYS, values))))
                    if line[0] == 'T':
                        self.draw['texts'].append(dict(list(zip(_TEXT_KEYS,
                                                                values))))
                    if line[0] == 'X':
                        self.draw['pins'].append(dict(list(zip(_PIN_KEYS,
                                                               values))))

        # define some shortcuts
        self.num_units = int(self.definition['unit_count'])
        self.name = self.definition['name']
        self.ref_prefix = self.definition['reference']
        self.ref = '???'

        def kicad_pin_to_pin(kpin):
            p = Pin()
            p.__dict__.update(kpin)
            # the reference to the containing part needs to be updated when
            # the part is copied!!!
            p.part = self  # This lets the pin find the part that contains it.
            return p

        self.pins = [kicad_pin_to_pin(p) for p in self.draw['pins']]

    def __getitem__(self, *pin_ids):
        '''
        Return list of part pins selected by pin numbers or names.
        '''
        pins = []
        for p_id in pin_ids:
            if isinstance(p_id, int):
                pins.extend(to_list(self.filter_pins(num=str(p_id))))
            elif isinstance(p_id, (list, tuple)):
                for p in p_id:
                    pins.extend(to_list(self[p]))
            elif isinstance(p_id, slice):
                if p_id.start is None or p_id.stop is None:
                    pin_nums = [int(p.num) for p in self.pins]
                start = p_id.start or min(pin_nums)
                stop = p_id.stop or (max(pin_nums) + 1)
                step = p_id.step or 1
                for pin_num in range(start, stop, step):
                    pins.extend(to_list(self[pin_num]))
            else:
                tmp_pins = self.filter_pins(num=p_id)
                if tmp_pins:
                    pins.extend(to_list(tmp_pins))
                else:
                    pins.extend(to_list(self.filter_pins(name=p_id)))
        return list_to_scalar(pins)

    def filter_pins(self, **kwargs):
        '''
        Return a list of component pins that match a list of criteria.
        Possible criteria are 'name', 'direction', 'electrical_type', etc.
        The match is done using regular expressions.
        Example: comp.filter_pins(name='io[0-9]+', direction='bidir') will
        return all the bidirectional pins of the component that have pin names
        starting with 'io' followed by a number (e.g., 'IO45').
        '''
        return filter(self.pins, **kwargs)

    def __setitem__(self, pin_ids, nets):
        '''
        Attach nets or pins of other parts to the specified pins of this part.
        '''
        pins = self[pin_ids]
        if isinstance(pins, Pin):
            pins = [pins]
        if pins is None or len(pins) == 0:
            raise Exception("No pins to attach to!")
        if isinstance(nets, Net):
            nets = [nets]
        if len(nets) == 1:
            nets = nets * len(pins)
        if len(nets) == len(pins):
            for pin, net in zip(pins, nets):
                net += pin
        else:
            raise Exception("Can't attach differing numbers of pins and nets!")

    @property
    def ref(self):
        '''Return the part reference.'''
        return self._ref

    @ref.setter
    def ref(self, id):
        '''Set the part reference.'''
        if isinstance(id, int):
            self._ref = self.ref_prefix + str(id)
        elif isinstance(id, type('')):
            self._ref = id
        else:
            raise Exception("Illegal part reference: {}".format(id))

    @ref.deleter
    def ref(self):
        '''Delete the part reference.'''
        del sel._ref

    @property
    def val(self):
        '''Return the part value.'''
        return self._val

    @val.setter
    def val(self, value):
        '''Set the part value.'''
        self._val = str(value)

    @val.deleter
    def val(self):
        '''Delete the part value.'''
        del sel._val

    @property
    def foot(self):
        '''Return the part footprint.'''
        return self._foot

    @foot.setter
    def foot(self, footprint):
        '''Set the part footprint.'''
        self._foot = str(footprint)

    @foot.deleter
    def foot(self):
        '''Delete the part footprint.'''
        del sel._foot

    def unit(self, *unit_ids):
        '''Return a subunit of this part.'''
        return PartUnit(self, *unit_ids)


class PartUnit(Part):
    def __init__(self, part, *unit_ids):
        for k, v in part.__dict__.items():
            self.__dict__[k] = v
        unique_pins = set()
        for unit_id in unit_ids:
            if isinstance(unit_id,int):
                unique_pins |= set(part.filter_pins(unit=str(unit_id)))
            elif isinstance(unit_id,slice):
                max_index = part.num_units
                for id in range(*unit_id.indices(max_index)):
                    unique_pins |= set(part.filter_pins(unit=str(id)))
        self.pins = [p for p in unique_pins]
        print('# pins in unit = {}'.format(len(self.pins)))
        print(self.name, self.pins[0].part.name)
        print(self.ref, self.pins[0].part.ref)


class SubCircuit(object):
    pass


class Net(object):
    def __init__(self, name=None, *pins):
        self.name = name
        self.pins = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name or 'Default'

    @name.deleter
    def name(self):
        del self._name

    def add_pins(self, *pins):
        for pin in pins:
            if isinstance(pin, Pin):
                if pin not in self.pins:
                    # Pin is not already in the net, so add it to the net.
                    self.pins.append(pin)  # This must come 1st to prevent infinite recursion!
                    pin += self  # Let the pin know the net it's connected to.
            elif isinstance(pin, (list, tuple)):
                for p in pin:
                    self += p
            else:
                raise Exception('Cannot attach a non-Pin {} to Net {}.'.format(
                    type(pin), self.name))
        return self

    def __add__(self, *pins):
        return self.add_pins(*pins)


class Bus(object):
    def __init__(self, name=None):
        self.set_name(name)
        self.nets = []

    def set_name(self, name):
        self.name = name

    def __getitem__(self, *ids):
        subset = Bus()
        for id in ids:
            if isinstance(id, slice):
                for i in range(id.start, id.stop, id.step):
                    subset.nets.append(self.nets[i])
            elif isinstance(id, int):
                subset.nets.append(self.nets[id])
            else:
                for n in self.nets:
                    if re.match(id, n.name):
                        subset.nets.append(n)
        if len(subset) == 0:
            return None
        elif len(subset) == 1:
            return subset[0]
        else:
            return subset


if __name__ == '__main__':

    # Libraries.
    xess_lib = SchLib('C:/xesscorp/KiCad/libraries/xess.lib')

    # Components.
    vreg = Part(xess_lib, '1117')  # Also check part aliases!
    vreg.ref = 1

    psoc = Part(xess_lib, 'CY8C52\?\?LTI-LP')
    psoc.ref = 2
    psoc_unit_A = PartUnit(psoc, '2')
    for p in psoc_unit_A.pins:
        print(p.part.ref, p.name, p.num, p.unit)

    cap = [Part(xess_lib, 'C-NONPOL') for i in range(5)]
    for i in range(len(cap)):
        cap[i].ref = i

    bead = Part(xess_lib, 'FERRITE.*')
    bead.ref = 'L1'

    # Power and ground nets.
    gnd = Net(name='GND')
    vcc_5 = Net(name='+5V')
    vcc_33_a = Net(name='+3.3V-A')
    vcc_33 = Net(name='+3.3V')
    dummy = Net(name='dummy')
    psoc_unit_A[27] = vcc_33_a

    # Connect pins to nets.
    #vcc_33 += vreg['OUT']
    vreg['OUT', 'IN'] = vcc_33
    #vcc_5 += vreg['IN']
    gnd += vreg['GND']
    vcc_33_a += bead[2]

    #gnd += psoc['VSS.*']
    psoc['VSS.*'] = gnd

    for c in cap[:3]:
        vcc_33_a += c[1]
        gnd += c[2]
    for c in cap[3:]:
        vcc_33 += c[1]
        gnd += c[2]

    dummy += vreg[4]
    #dummy += 1

    print('GND:')
    for p in gnd.pins:
        print(p.part.ref, p.name, p.num, p.electrical_type)
    print('INPUT POWER:')
    for p in vcc_5.pins:
        print(p.part.ref, p.name, p.num, p.electrical_type)
    print('VCC (analog):')
    for p in vcc_33_a.pins:
        print(p.part.ref, p.name, p.num, p.electrical_type)
    print('VCC (digital):')
    for p in vcc_33.pins:
        print(p.part.ref, p.name, p.num, p.electrical_type)
    print('dummy:')
    for p in dummy.pins:
        print(p.part.ref, p.name, p.num, p.electrical_type)

    sys.exit()

    #lib_file = 'C:/xesscorp/KiCad/libraries/xilinx7.lib'
    #part_name = 'xc7a100tfgg484'
    lib_file = 'C:/xesscorp/KiCad/libraries/Cypress_cy8c5xlp.lib'
    part_name = 'CY8C54LP-.*'
    lib = SchLib(lib_file)
    part_list = lib.get_parts(name=part_name)
    for p in part_list:
        print(p.name)
    part_name = 'CY8C54LP-TQFP100'
    part = Part(lib_file, part_name)
    print(part.name)
    for p in part.pins:
        print(p.part.name, p.name, p.num)
    #gnd.add_pins(*part['gnd.*'])
    gnd += part['vss.*']
    gnd += part[70]
    gnd += part['.*MHZ_XTAL:XO.*']
    for p in gnd.pins:
        print(p.name, p.num, p.electrical_type)
    #pprint(part['gnd.*'])
