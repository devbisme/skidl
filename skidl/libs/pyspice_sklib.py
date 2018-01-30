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
    return part.ref


def _get_net_names(part):
    '''Return a list of net names attached to the pins of a part.'''
    return [pin.nets[0].name for pin in part.pins if pin.is_connected()]


def _get_pos_args(part, pos_arg_names):
    '''Return the values for positional arguments to PySpice element constructor.'''
    pos_arg_values = []
    for name in pos_arg_names:
        try:
            pos_arg_values.append(getattr(part, name))
        except AttributeError:
            pass
    return pos_arg_values


def _get_kwargs(part, keys):
    '''Return a dict of keyword arguments to PySpice element constructor.'''
    kwargs = {}
    for key in keys:
        try:
            kwargs.update({key: getattr(part, key)})
        except AttributeError:
            pass
    return kwargs


def _add_part_to_circuit(part, circuit, pos, keys):
    '''
    Add a part to a PySpice Circuit object.
    '''

    # Positional arguments start with the device name.
    args = [_get_spice_ref(part)]
    # Then add the net connections to the device.
    args.extend(_get_net_names(part))
    # Then add any additional positional arguments.
    args.extend(_get_pos_args(part, pos))
    # Get keyword arguments.
    kwargs = _get_kwargs(part, keys)
    # Add the part to the PySpice circuit.
    getattr(circuit, part.pyspice_name)(*args, **kwargs)


def add_spice_subcircuit(part, circuit):
    # How to add the SKiDL-part pins to the subcircuit in the correct order?
    # The SKiDL-part must have a parameter dict to pass to the subcircuit.
    logger.error(
        "add_spice_subcircuit not implemented for {} - {}.".format(
            part.name, part.ref))


# The following functions add a specific type of SPICE element to a PySpice circuit.


def _add_capacitor_to_circuit(part, circuit):
    pos = ('value', )
    kw = ('model', 'multiplier', 'm', 'scale', 'temperature', 'temp',
          'device_temperature', 'dtemp', 'ic')
    _add_part_to_circuit(part, circuit, pos, kw)


def _add_diode_to_circuit(part, circuit):
    pos = ('value', )
    kw = ('model', 'area', 'multiplier', 'm', 'pj', 'off', 'ic', 'temperature',
          'temp', 'device_temperature', 'dtemp')
    _add_part_to_circuit(part, circuit, pos, kw)


def _add_inductor_to_circuit(part, circuit):
    pos = ('value', )
    kw = ('value', 'nt', 'multiplier', 'm', 'scale', 'temperature', 'temp',
          'device_temperature', 'dtemp', 'ic')
    _add_part_to_circuit(part, circuit, pos, kw)


def _add_resistor_to_circuit(part, circuit):
    pos = ('value', )
    kw = ('ac', 'multiplier', 'm', 'scale', 'temperature', 'temp',
          'device_temperature', 'dtemp', 'noisy')
    _add_part_to_circuit(part, circuit, pos, kw)


def _add_vcvs_to_circuit(part, circuit):
    logger.error(
        "VCVS not implemented for {} - {}.".format(
            part.name, part.ref))


def _add_vccs_to_circuit(part, circuit):
    logger.error(
        "VCCS not implemented for {} - {}.".format(
            part.name, part.ref))


def _add_vcsw_to_circuit(part, circuit):
    logger.error(
        "VCSW not implemented for {} - {}.".format(
            part.name, part.ref))


def _add_cccs_to_circuit(part, circuit):
    logger.error(
        "CCCS not implemented for {} - {}.".format(
            part.name, part.ref))


def _add_ccvs_to_circuit(part, circuit):
    logger.error(
        "CCVS not implemented for {} - {}.".format(
            part.name, part.ref))


def _add_ccsw_to_circuit(part, circuit):
    logger.error(
        "CCSW not implemented for {} - {}.".format(
            part.name, part.ref))


def _add_cs_to_circuit(part, circuit):
    logger.error(
        "Current source not implemented for {} - {}.".format(
            part.name, part.ref))


def _add_bjt_to_circuit(part, circuit):
    pos = []
    kw = ('model', 'area', 'areac', 'areab'
          'multiplier', 'm', 'off', 'ic', 'temperature', 'temp',
          'device_temperature', 'dtemp')
    _add_part_to_circuit(part, circuit, pos, kw)


def _add_jfet_to_circuit(part, circuit):
    pos = []
    kw = ('model', 'area', 'off', 'ic', 'temperature', 'temp')
    _add_part_to_circuit(part, circuit, pos, kw)


def _add_mesfet_to_circuit(part, circuit):
    pos = []
    kw = ('model', 'area', 'off', 'ic', 'temperature', 'temp')
    _add_part_to_circuit(part, circuit, pos, kw)


def _add_mosfet_to_circuit(part, circuit):
    pos = []
    kw = ('model', 'mltiplier', 'm', 'length', 'l', 'width', 'w',
          'drain_area', 'ad', 'source_area', 'as', 'drain_perimeter', 'pd',
          'source_perimeter', 'ps', 'drain_number', 'nrd',
          'source_number_square', 'nrs', 'off', 'ic', 'temperature', 'temp')
    _add_part_to_circuit(part, circuit, pos, kw)


def _add_coupled_inductor_to_circuit(part, circuit):
    logger.error(
        "Coupled inductor not implemented for {} - {}.".format(
            part.name, part.ref))


def _add_coupled_multiconductor_line_to_circuit(part, circuit):
    logger.error(
        "Coupled multiconductor line not implemented for {} - {}.".format(
            part.name, part.ref))


def _add_single_lossy_transmission_line_to_circuit(part, circuit):
    logger.error(
        "Single lossy transmission line not implemented for {} - {}.".format(
            part.name, part.ref))


def _add_transmission_line_to_circuit(part, circuit):
    logger.error("Transmission line not implemented for {} - {}.".format(
        part.name, part.ref))


def _add_lossy_transmission_line_to_circuit(part, circuit):
    logger.error("Lossy transmission line not implemented for {} - {}.".format(
        part.name, part.ref))


def _add_uniform_distributed_rc_line_to_circuit(part, circuit):
    logger.error("Uniform distributed RC line not implemented for {} - {}.".format(
        part.name, part.ref))


def _add_vs_to_circuit(part, circuit):
    pos = []
    kw = ('dc_value', )
    _add_part_to_circuit(part, circuit, pos, kw)


def _not_implemented(part, circuit):
    logger.error("Function not implemented for {} - {}.".format(
        part.name, part.ref))


# Create a SKiDL library of SPICE elements.

spice = SchLib(tool=SKIDL).add_parts(*[
    Part(
        name='A',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='XSPICE',
        description='XSPICE code module',
        ref_prefix='A',
        spice_prefix='A',
        pyspice_name='XSpiceElement',
        num_units=1,
        do_erc=True,
        add_to_spice=_not_implemented,
        pins=[]),
    Part(
        name='B',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='Behavioral source',
        description='Behavioral (arbitrary) source',
        ref_prefix='B',
        spice_prefix='B',
        pyspice_name='BehavioralSource',
        num_units=1,
        do_erc=True,
        add_to_spice=_not_implemented,
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
        spice_prefix='C',
        pyspice_name='C',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_capacitor_to_circuit,
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
        spice_prefix='D',
        pyspice_name='D',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_diode_to_circuit,
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
        spice_prefix='E',
        pyspice_name='VoltageControlledVoltageSource',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_vcvs_to_circuit,
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
        spice_prefix='F',
        pyspice_name='CurrentControlledCurrentSource',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_cccs_to_circuit,
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
        spice_prefix='G',
        pyspice_name='VoltageControlledCurrentSource',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_vccs_to_circuit,
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
        spice_prefix='H',
        pyspice_name='CurrentControlledCurrentSource',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_ccvs_to_circuit,
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
        spice_prefix='I',
        pyspice_name='CurrentSource',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_cs_to_circuit,
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
        spice_prefix='J',
        pyspice_name='JFET',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_jfet_to_circuit,
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
        spice_prefix='K',
        pyspice_name='CoupledInductor',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_coupled_inductor_to_circuit,
        coupled_parts=[],
        pins=[]),
    Part(
        name='L',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='inductor choke coil reactor magnetic',
        description='Inductor',
        ref_prefix='L',
        spice_prefix='L',
        pyspice_name='L',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_inductor_to_circuit,
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
        spice_prefix='M',
        pyspice_name='Mosfet',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_mosfet_to_circuit,
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
        spice_prefix='N',
        pyspice_name='GSSElement',
        num_units=1,
        do_erc=True,
        add_to_spice=_not_implemented,
        pins=[]),
    Part(
        name='O',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='lossy transmission line',
        description='Lossy transmission line',
        ref_prefix='O',
        spice_prefix='O',
        pyspice_name='LossyTransmission',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_lossy_transmission_line_to_circuit,
        #model=
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
        spice_prefix='P',
        pyspice_name='CoupledMulticonductorLine',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_coupled_multiconductor_line_to_circuit,
        #model=
        pins=[]),
    Part(
        name='Q',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='bipolar transistor npn pnp',
        description='Bipolar Junction Transistor',
        ref_prefix='Q',
        spice_prefix='Q',
        pyspice_name='BJT',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_bjt_to_circuit,
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
        spice_prefix='R',
        pyspice_name='R',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_resistor_to_circuit,
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
        spice_prefix='S',
        pyspice_name='VoltageControlledSwitch',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_vcsw_to_circuit,
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
        spice_prefix='T',
        pyspice_name='TransmissionLine',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_transmission_line_to_circuit,
        #model=
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
        spice_prefix='U',
        pyspice_name='UniformDistributedRCLine',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_uniform_distributed_rc_line_to_circuit,
        #model=
        pins=[]),
    Part(
        name='V',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='voltage source',
        description='Voltage source',
        ref_prefix='V',
        spice_prefix='V',
        pyspice_name='V',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_vs_to_circuit,
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
        spice_prefix='W',
        pyspice_name='CurrentControlledSwitch',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_ccsw_to_circuit,
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
        spice_prefix='Y',
        pyspice_name='SingleLossyTransmissionLine',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_single_lossy_transmission_line_to_circuit,
        #model=
        pins=[]),
    Part(
        name='Z',
        dest=TEMPLATE,
        tool=SKIDL,
        keywords='metal-semiconductor field-effect transistor MOSFET',
        description='Metal-semiconductor field-effect transistor',
        ref_prefix='Z',
        spice_prefix='Z',
        pyspice_name='Mesfet',
        num_units=1,
        do_erc=True,
        add_to_spice=_add_mesfet_to_circuit,
        pins=[
            Pin(num='1', name='D', func=Pin.PASSIVE, do_erc=True),
            Pin(num='2', name='G', func=Pin.PASSIVE, do_erc=True),
            Pin(num='3', name='S', func=Pin.PASSIVE, do_erc=True),
        ]),
])
