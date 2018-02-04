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

from PySpice import *
from PySpice.Unit import *
from skidl import Net, Pin, Part, SchLib, SKIDL, TEMPLATE, logger


def node(net_or_pin):
    if isinstance(net_or_pin, Net):
        return net_or_pin.name
    if isinstance(net_or_pin, Pin):
        return net_or_pin.net.name

def _get_spice_ref(part):
    '''Return a SPICE reference ID for the part.'''
    if part.ref.startswith(part.ref_prefix):
        return part.ref[len(part.ref_prefix):]
    return part.ref


def _get_net_names(part):
    '''Return a list of net names attached to the pins of a part.'''
    return [node(pin) for pin in part.pins if pin.is_connected()]


def _get_pos_args(part, pos_arg_names):
    '''Return the values for positional arguments to PySpice element constructor.'''
    pos_arg_values = []
    for name in pos_arg_names:
        try:
            # If the positional argument is a Part, then substitute the part
            # reference because it's probably a control current for something
            # like a current-controlled source or switch. Otherwise, just use
            # the positional argument as-is.
            value = getattr(part, name)
            if isinstance(value, Part):
                value = value.ref
            pos_arg_values.append(value)
        except AttributeError:
            pass
    return pos_arg_values


def _get_kwargs(part, kw):
    '''Return a dict of keyword arguments to PySpice element constructor.'''
    kwargs = {}
    for key in kw:
        try:
            # If the keyword argument is a Part, then substitute the part
            # reference because it's probably a control current for something
            # like a current-controlled source or switch. Otherwise, just use
            # the keyword argument as-is.
            value = getattr(part, key)
            if isinstance(value, Part):
                value = value.ref
            kwargs.update({key: value})
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
    Part( #####################################################################
        name='A',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='XSPICE',
        description='XSPICE code module',
        ref_prefix='A',
        pyspice={
            'name': 'XSpiceElement',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[]),
    Part(
        name='B',
        aliases=['behavsrc', 'BEHAVSRC', 'behavioralsource', 'BEHAVIORALSOURCE',],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='Behavioral source',
        description='Behavioral (arbitrary) source',
        ref_prefix='B',
        pyspice={
            'name': 'BehavioralSource',
            'pos': ('i_expression', 'v_expression', ),
            'kw': ('tc1', 'tc2', 'temp', 'temperature', 'dtemp', 'device_temperature',),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='C',
        aliases=['cap', 'CAP'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='cap capacitor',
        description='Capacitor',
        ref_prefix='C',
        pyspice={
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
        name='BEHAVCAP',
        aliases=['behavcap', 'behavioralcap', 'BEHAVIORALCAP',],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='behavioral capacitor',
        description='Behavioral capacitor',
        ref_prefix='C',
        pyspice={
            'name': 'BehavioralCapacitor',
            'pos': ('expression', ),
            'kw': ('tc1', 'tc2'),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='SEMICAP',
        aliases=['semicap', 'semiconductorcap', 'SEMICONDUCTORCAP',],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='semiconductor capacitor',
        description='Semiconductor capacitor',
        ref_prefix='C',
        pyspice={
            'name': 'SemiconductorCapacitor',
            'pos': ('value', 'model', ),
            'kw': ('length', 'l', 'width', 'w', 'multiplier', 'm', 'scale', 'temperature', 'temp',
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
        aliases=['diode', 'DIODE'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='diode rectifier',
        description='Diode',
        ref_prefix='D',
        pyspice={
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
        aliases=['VCVS', 'vcvs'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='voltage-controlled voltage source',
        description='Voltage-controlled voltage source',
        ref_prefix='E',
        pyspice={
            'name': 'VCVS',
            'pos': ('gain',),
            'kw': [],
            'add': _add_part_to_circuit,
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
        name='NONLINV',
        aliases=['nonlinv', 'nonlinearvoltagesource', 'NONLINEARVOLTAGESOURCE'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='non-linear voltage source',
        description='Nonlinear voltage source',
        ref_prefix='E',
        pyspice={
            'name': 'NonLinearVoltageSource',
            'pos': [],
            'kw': ('expression', 'table',),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='F',
        aliases=['CCCS', 'cccs'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='current-controlled current source',
        description='Current-controlled current source',
        ref_prefix='F',
        pyspice={
            'name': 'CCCS',
            'pos': ('control', 'gain', ),
            'kw': [],
            'add': _add_part_to_circuit,
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
            'name': 'VCCS',
            'pos': ('transconductance', ),
            'kw': [],
            'add': _add_part_to_circuit,
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
        aliases=['CCVS', 'ccvs'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='current-controlled voltage source',
        description='Current-controlled voltage source',
        ref_prefix='H',
        pyspice={
            'name': 'CCVS',
            'pos': ('control', 'transresistance', ),
            'kw': [],
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='I',
        aliases=['cs', 'CS'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='current source',
        description='Current source',
        ref_prefix='I',
        pyspice={
            'name': 'CurrentSource',
            'pos': ('dc_value', ),
            'kw': [],
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='J',
        aliases=['JFET', 'jfet'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='junction field-effect transistor JFET',
        description='Junction field-effect transistor',
        ref_prefix='J',
        pyspice={
            'name': 'JFET',
            'pos': ('model',),
            'kw': ('area', 'off', 'ic', 'temperature', 'temp'),
            'add': _add_part_to_circuit,
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
            'name': 'CoupledInductor',
            'pos': ('ind1', 'ind2', 'coupling',),
            'kw': [],
            'add': _add_part_to_circuit,
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
        name='BEHAVIND',
        aliases=['behavind', 'behavioralind', 'BEHAVIORALIND',],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='behavioral inductor',
        description='Behavioral inductor',
        ref_prefix='C',
        pyspice={
            'name': 'BehavioralInductor',
            'pos': ('expression', ),
            'kw': ('tc1', 'tc2'),
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
        aliases=['MOSFET', 'mosfet', 'FET', 'fet',],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='metal-oxide field-effect transistor MOSFET',
        description='Metal-oxide field-effect transistor',
        ref_prefix='M',
        pyspice={
            'name': 'Mosfet',
            'pos': ('model',),
            'kw': ('multiplier', 'm', 'length', 'l', 'width', 'w',
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
    Part( #####################################################################
        name='N',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='numerical device GSS',
        description='Numerical device for GSS',
        ref_prefix='N',
        pyspice={
            'name': 'GSSElement',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[]),
    Part( #####################################################################
        name='O',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='lossy transmission line',
        description='Lossy transmission line',
        ref_prefix='O',
        pyspice={
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
    Part( #####################################################################
        name='P',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='coupled multiconductor line',
        description='Coupled multiconductor line',
        ref_prefix='P',
        pyspice={
            'name': 'CoupledMulticonductorLine',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        #model=
        pins=[]),
    Part(
        name='Q',
        aliases=('BJT', 'bjt'),
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='bipolar transistor npn pnp',
        description='Bipolar Junction Transistor',
        ref_prefix='Q',
        pyspice={
            'name': 'BJT',
            'pos': ('model',),
            'kw': ('area', 'areac', 'areab'
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
        name='BEHAVRES',
        aliases=['behavres', 'behavioralresistor', 'BEHAVIORALRESISTOR',],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='behavioral resistor',
        description='Behavioral resistor',
        ref_prefix='R',
        pyspice={
            'name': 'BehavioralResistor',
            'pos': ('expression',),
            'kw': ('tc1', 'tc2'),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='SEMIRES',
        aliases=['semires', 'semiconductorresistor', 'SEMICONDUCTORRESISTOR',],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='semiconductor resistor',
        description='Semiconductor resistor',
        ref_prefix='R',
        pyspice={
            'name': 'SemiconductorResistor',
            'pos': ('value', 'model',),
            'kw': ('ac', 'length', 'l', 'width', 'w', 'multiplier', 'm', 'scale', 'temperature', 'temp',
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
        aliases=['VCS', 'vcs'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='voltage-controlled switch',
        description='Voltage-controlled switch',
        ref_prefix='S',
        pyspice={
            'name': 'VCS',
            'pos': ('model', 'initial_state',),
            'kw': [],
            'add': _add_part_to_circuit,
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
        aliases=['transmissionline', 'TRANSMISSIONLINE'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='transmission line',
        description='Transmission line',
        ref_prefix='T',
        pyspice={
            'name': 'TransmissionLine',
            'add': _add_part_to_circuit,
            'pos': [],
            'kw': ('impedance', 'time_delay', 'frequency', 'normalized_length',),
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='ip', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='in', func=Pin.PASSIVE, do_erc=True),
            Pin(num='3', name='op', func=Pin.PASSIVE, do_erc=True),
            Pin(num='4', name='on', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part( #####################################################################
        name='U',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='uniformly-distributed RC line',
        description='Uniformly-distributed RC line',
        ref_prefix='U',
        pyspice={
            'name': 'UniformDistributedRCLine',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        pins=[]),
    Part(
        name='V',
        aliases=['v', 'AMMETER', 'ammeter',],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='voltage source',
        description='Voltage source',
        ref_prefix='V',
        pyspice={
            'name': 'V',
            'pos': ('dc_value',),
            'kw': [],
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
        aliases=['CCS', 'ccs'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='current-controlled switch',
        description='Current-controlled switch',
        ref_prefix='W',
        pyspice={
            'name': 'CurrentControlledSwitch',
            'pos': ('control', 'model', 'initial_state',),
            'kw': [],
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    # Don't put X subcircuit in this list! It's handled separately.
    Part( #####################################################################
        name='Y',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='single lossy transmission line',
        description='Single lossy transmission line',
        ref_prefix='Y',
        pyspice={
            'name': 'SingleLossyTransmissionLine',
            'add': _not_implemented,
        },
        num_units=1,
        do_erc=True,
        #model=
        pins=[]),
    Part(
        name='Z',
        aliases=['MESFET', 'mesfet'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='metal-semiconductor field-effect transistor MOSFET',
        description='Metal-semiconductor field-effect transistor',
        ref_prefix='Z',
        pyspice={
            'name': 'Mesfet',
            'pos': ('model',),
            'kw': ('area', 'off', 'ic', 'multiplier', 'm'),
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='D', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='G', func=Pin.PASSIVE, do_erc=True),
            Pin(num='3', name='S', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='SINE',
        aliases=['SIN', 'SINUSOIDAL', 'sin', 'sine', 'sinusoidal'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='simusoidal voltage source',
        description='Sinusoidal voltage source',
        ref_prefix='V',
        pyspice={
            'name': 'Sinusoidal',
            'pos': [],
            'kw': ['dc_offset', 'amplitude', 'frequency', 'delay', 'damping_factor'],
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='PULSE',
        aliases=['pulse'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='pulsed voltage source',
        description='Pulsed voltage source',
        ref_prefix='V',
        pyspice={
            'name': 'Pulse',
            'pos': [],
            'kw': ['initial_value', 'pulsed_value', 'delay_time', 'rise_time', 'fall_time', 'pulse_width', 'period'],
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='EXP',
        aliases=['exp', 'exponential', 'EXPONENTIAL'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='exponential voltage source',
        description='Exponential voltage source',
        ref_prefix='V',
        pyspice={
            'name': 'Exponential',
            'pos': [],
            'kw': ['initial_value', 'pulsed_value', 'rise_delay_time', 'rise_time_constant', 'fall_delay_time', 'fall_time_constant'],
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='PWL',
        aliases=['pwl', 'piecewiselinear', 'PIECEWISELINEAR'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='piecewise linear voltage source',
        description='Piecewise linear voltage source',
        ref_prefix='V',
        pyspice={
            'name': 'PieceWiseLinear',
            'pos': [],
            'kw': ['repeate_time', 'delay_time',],
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='FM',
        aliases=['fm', 'SFFM', 'sffm', 'SINGLEFREQUENCYFM', 'singlefrequencyfm'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='single frequency FM modulated voltage source',
        description='Single-frequency FM voltage source',
        ref_prefix='V',
        pyspice={
            'name': 'SingleFrequencyFM',
            'pos': [],
            'kw': ['offset', 'amplitude', 'carrier_frequency', 'modulation_index', 'signal_frequency'],
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='AM',
        aliases=['am', 'AMPLITUDEMODULATED', 'amplitudemodulated'],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='amplitude modulated voltage source',
        description='Amplitude modulated voltage source',
        ref_prefix='V',
        pyspice={
            'name': 'AmplitudeModulated',
            'pos': [],
            'kw': ['offset', 'amplitude', 'carrier_frequency', 'modulating_frequency', 'signal_delay'],
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
        ]),
    Part(
        name='RND',
        aliases=['rnd',],
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='random voltage source',
        description='Random voltage source',
        ref_prefix='V',
        pyspice={
            'name': 'RandomVoltage',
            'pos': [],
            'kw': ['random_type', 'duration', 'time_delay', 'parameter1', 'parameter2'],
            'add': _add_part_to_circuit,
        },
        num_units=1,
        do_erc=True,
        pins=[
            Pin(num='1', name='p', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='n', func=Pin.PASSIVE, do_erc=True),
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
