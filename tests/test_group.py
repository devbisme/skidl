# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

from builtins import super

from skidl import (
    ERC,
    HIER_SEP,
    TEMPLATE,
    Bus,
    Group,
    Net,
    Part,
    generate_netlist,
    generate_xml,
    subcircuit,
)

from .setup_teardown import setup_function, teardown_function


def test_group_1():
    class Resistor(Part):
        def __init__(self, value, ref=None, footprint="Resistors_SMD:R_0805"):
            super().__init__("Device", "R", value=value, ref=ref, footprint=footprint)

    @subcircuit
    def resdiv():
        gnd = Net("GND")  # Ground reference.
        vin = Net("VI")  # Input voltage to the divider.
        vout = Net("VO")  # Output voltage from the divider.

        r1 = Resistor("1k")
        r2 = Resistor("500")

        with Group("Caps"):
            cap = Part("Device", "C", dest=TEMPLATE)
            c1 = cap()
            c2 = cap(value="1uF")
            with Group("Resistors"):
                r3 = Resistor("5k")
                r4 = Resistor("10k")
                vin & (r3 | c1) & (r4 | c2) & gnd

        bus1 = Bus("BB", 10)

        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    with Group("Resistor_Divider"):
        resdiv()
        resdiv()

    assert len(default_circuit.parts) == 12
    assert len(default_circuit.get_nets()) == 8
    assert len(default_circuit.buses) == 2

    depth = 0
    for part in default_circuit.parts:
        depth = max(depth, part.hierarchical_name.count(HIER_SEP))
    assert depth == 5

    ERC()
    generate_netlist()
    generate_xml()
