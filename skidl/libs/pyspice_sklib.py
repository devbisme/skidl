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
An interface from SKiDL to PySpice.
"""

from skidl import Pin, Part, SchLib, SKIDL, TEMPLATE, logger


def _get_spice_ref(part):
    '''Return a SPICE reference ID for the part.'''
    if part.ref.startswith(part.ref_prefix):
        return part.ref[len(part.ref_prefix):]
    return part.ref


def _get_net_names(part):
    '''Return a list of net names attached to the pins of a part.'''
    return [pin.net.name for pin in part.pins if pin.is_connected()]


def _get_pos_args(part, pos_arg_names):
    '''Return the values for positional arguments to PySpice element constructor.'''
    pos_arg_values = []
    for name in pos_arg_names:
        try:
            pos_arg_values.append(getattr(part, name))
        except AttributeError:
            pass
    return pos_arg_values


def _get_kwargs(part, kw):
    '''Return a dict of keyword arguments to PySpice element constructor.'''
    kwargs = {}
    for key in kw:
        try:
            kwargs.update({key: getattr(part, key)})
        except AttributeError:
            pass
    return kwargs


def _add_part_to_circuit(part, circuit):
    '''
    Add a part to a PySpice Circuit object.
    '''

    pos = part.pyspice['pos']
    kw = part.pyspice['kw']

    # Positional arguments start with the device name.
    args = [_get_spice_ref(part)]
    # Then add the net connections to the device.
    args.extend(_get_net_names(part))
    # Then add any additional positional arguments.
    args.extend(_get_pos_args(part, pos))
    # Get keyword arguments.
    kwargs = _get_kwargs(part, kw)
    # Add the part to the PySpice circuit.
    getattr(circuit, part.pyspice['name'])(*args, **kwargs)


def add_spice_subcircuit(part, circuit):
    # How to add the SKiDL-part pins to the subcircuit in the correct order?
    # The SKiDL-part must have a parameter dict to pass to the subcircuit.
    logger.error(
        "add_spice_subcircuit not implemented for {} - {}.".format(
            part.name, part.ref))


def _not_implemented(part, circuit):
    logger.error("Function not implemented for {} - {}.".format(
        part.name, part.ref))


# Create a SKiDL library of SPICE elements.

pyspice = SchLib(tool=SKIDL).add_parts(*[
    Part(
        name='A',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='XSPICE',
        description='XSPICE code module',
        ref_prefix='A',
        pyspice={
            'prefix': 'A',
            'name': 'XSpiceElement',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[]),
    Part(
        name='B',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='Behavioral source',
        description='Behavioral (arbitrary) source',
        ref_prefix='B',
        pyspice={
            'prefix': 'B',
            'name': 'BehavioralSource',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='C',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='cap capacitor',
        description='Capacitor',
        ref_prefix='C',
        pyspice={
            'prefix': 'C',
            'name': 'C',
            'pos': ('value', ),
            'kw': ('model', 'multiplier', 'm', 'scale', 'temperature', 'temp',
                   'device_temperature', 'dtemp', 'ic'),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='D',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='diode rectifier',
        description='Diode',
        ref_prefix='D',
        pyspice={
            'prefix': 'D',
            'name': 'D',
            'pos': ('value', ),
            'kw': ('model', 'area', 'multiplier', 'm', 'pj', 'off', 'ic', 'temperature',
                   'temp', 'device_temperature', 'dtemp'),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='E',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='voltage-controlled voltage source',
        description='Voltage-controlled voltage source',
        ref_prefix='E',
        pyspice={
            'prefix': 'E',
            'name': 'VoltageControlledVoltageSource',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='ip', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='in', func=Pin.PASSIVE, do_erc=True),
            Pin(num='3', name='op', func=Pin.PASSIVE, do_erc=True),
            Pin(num='4', name='on', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='F',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='current-controlled current source',
        description='Current-controlled current source',
        ref_prefix='F',
        pyspice={
            'prefix': 'F',
            'name': 'CurrentControlledCurrentSource',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='G',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='voltage-controlled current source',
        description='Voltage-controlled current source',
        ref_prefix='G',
        pyspice={
            'prefix': 'G',
            'name': 'VoltageControlledCurrentSource',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='ip', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='in', func=Pin.PASSIVE, do_erc=True),
            Pin(num='3', name='op', func=Pin.PASSIVE, do_erc=True),
            Pin(num='4', name='on', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='H',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='current-controlled voltage source',
        description='Current-controlled voltage source',
        ref_prefix='H',
        pyspice={
            'prefix': 'H',
            'name': 'CurrentControlledCurrentSource',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='I',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='current source',
        description='Current source',
        ref_prefix='I',
        pyspice={
            'prefix': 'I',
            'name': 'CurrentSource',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='J',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='junction field-effect transistor JFET',
        description='Junction field-effect transistor',
        ref_prefix='J',
        pyspice={
            'prefix': 'J',
            'name': 'JFET',
            'pos': [],
            'kw': ('model', 'area', 'off', 'ic', 'temperature', 'temp'),
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='D', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='G', func=Pin.PASSIVE, do_erc=True),
            Pin(num='3', name='S', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='K',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='coupled mutual inductors',
        description='Coupled (mutual) inductors',
        ref_prefix='K',
        pyspice={
            'prefix': 'K',
            'name': 'CoupledInductor',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        coupled_parts=[],
        pins=[]),
    Part(
        name='L',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='inductor choke coil reactor magnetic',
        description='Inductor',
        ref_prefix='L',
        pyspice={
            'prefix': 'L',
            'name': 'L',
            'pos': ('value', ),
            'kw': ('value', 'nt', 'multiplier', 'm', 'scale', 'temperature', 'temp',
                   'device_temperature', 'dtemp', 'ic'),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='M',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='metal-oxide field-effect transistor MOSFET',
        description='Metal-oxide field-effect transistor',
        ref_prefix='M',
        pyspice={
            'prefix': 'M',
            'name': 'Mosfet',
            'pos': [],
            'kw': ('model', 'mltiplier', 'm', 'length', 'l', 'width', 'w',
                   'drain_area', 'ad', 'source_area', 'as', 'drain_perimeter', 'pd',
                   'source_perimeter', 'ps', 'drain_number', 'nrd',
                   'source_number_square', 'nrs', 'off', 'ic', 'temperature', 'temp'),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='D', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='G', func=Pin.PASSIVE, do_erc=True),
            Pin(num='3', name='S', func=Pin.PASSIVE, do_erc=True),
            Pin(num='4', name='T', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='N',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='numerical device GSS',
        description='Numerical device for GSS',
        ref_prefix='N',
        pyspice={
            'prefix': 'N',
            'name': 'GSSElement',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[]),
    Part(
        name='O',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='lossy transmission line',
        description='Lossy transmission line',
        ref_prefix='O',
        pyspice={
            'prefix': 'O',
            'name': 'LossyTransmission',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='ip', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='in', func=Pin.PASSIVE, do_erc=True),
            Pin(num='3', name='op', func=Pin.PASSIVE, do_erc=True),
            Pin(num='4', name='on', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='P',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='coupled multiconductor line',
        description='Coupled multiconductor line',
        ref_prefix='P',
        pyspice={
            'prefix': 'P',
            'name': 'CoupledMulticonductorLine',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        #model=
        pins=[]),
    Part(
        name='Q',
        aliases=('BJT','NPN'),
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='bipolar transistor npn pnp',
        description='Bipolar Junction Transistor',
        ref_prefix='Q',
        pyspice={
            'prefix': 'Q',
            'name': 'BJT',
            'pos': [],
            'kw': ('model', 'area', 'areac', 'areab'
                   'multiplier', 'm', 'off', 'ic', 'temperature', 'temp',
                   'device_temperature', 'dtemp'),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='C', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='B', func=Pin.PASSIVE, do_erc=True),
            Pin(num='3', name='E', func=Pin.PASSIVE, do_erc=True),
            Pin(num='4', name='T', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='R',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='res resistor',
        description='Resistor',
        ref_prefix='R',
        pyspice={
            'prefix': 'R',
            'name': 'R',
            'pos': ('value', ),
            'kw': ('ac', 'multiplier', 'm', 'scale', 'temperature', 'temp',
                   'device_temperature', 'dtemp', 'noisy'),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='S',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='voltage-controlled switch',
        description='Voltage-controlled switch',
        ref_prefix='S',
        pyspice={
            'prefix': 'S',
            'name': 'VoltageControlledSwitch',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='ip', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='in', func=Pin.PASSIVE, do_erc=True),
            Pin(num='3', name='op', func=Pin.PASSIVE, do_erc=True),
            Pin(num='4', name='on', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='T',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='transmission line',
        description='transmission line',
        ref_prefix='T',
        pyspice={
            'prefix': '',
            'name': 'TransmissionLine',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='ip', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='in', func=Pin.PASSIVE, do_erc=True),
            Pin(num='3', name='op', func=Pin.PASSIVE, do_erc=True),
            Pin(num='4', name='on', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='U',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='uniformly-distributed RC line',
        description='Uniformly-distributed RC line',
        ref_prefix='U',
        pyspice={
            'prefix': 'U',
            'name': 'UniformDistributedRCLine',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[]),
    Part(
        name='V',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='voltage source',
        description='Voltage source',
        ref_prefix='V',
        pyspice={
            'prefix': 'V',
            'name': 'V',
            'pos': [],
            'kw': ('dc_value', ),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='W',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='current-controlled switch',
        description='Current-controlled switch',
        ref_prefix='W',
        pyspice={
            'prefix': 'W',
            'name': 'CurrentControlledSwitch',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    # Don't put X subcircuit in this list! It's handled separately.
    Part(
        name='Y',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='single lossy transmission line',
        description='Single lossy transmission line',
        ref_prefix='Y',
        pyspice={
            'prefix': 'Y',
            'name': 'SingleLossyTransmissionLine',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        #model=
        pins=[]),
    Part(
        name='Z',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='metal-semiconductor field-effect transistor MOSFET',
        description='Metal-semiconductor field-effect transistor',
        ref_prefix='Z',
        pyspice={
            'prefix': 'Z',
            'name': 'Mesfet',
            'pos': [],
            'kw': ('model', 'area', 'off', 'ic', 'temperature', 'temp'),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='D', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='G', func=Pin.PASSIVE, do_erc=True),
            Pin(num='3', name='S', func=Pin.PASSIVE, do_erc=True),
        ]),
])


# Place all the PySpice parts into the namespace so they can bb instantiated easily.
this_module = __import__(__name__)
for p in pyspice.get_parts():
    # Add the part name to the module namespace.
    setattr(this_module, p.name, p)
    # Add all the part aliases to the module namespace.
    try:
        for alias in p.aliases:
            setattr(this_module, alias, p)
    except AttributeError:
        pass
