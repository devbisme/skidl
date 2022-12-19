# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

from builtins import super

from skidl import (
    ERC,
    TEMPLATE,
    Bus,
    Net,
    Part,
    generate_netlist,
    generate_xml,
    subcircuit,
)

from .setup_teardown import setup_function, teardown_function


def test_subcircuit_1():
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

        cap = Part("Device", "C", dest=TEMPLATE)
        c1 = cap()
        c2 = cap(value="1uF")

        bus1 = Bus("BB", 10)

        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    resdiv()
    resdiv()

    assert len(default_circuit.parts) == 8
    assert len(default_circuit.get_nets()) == 6
    assert len(default_circuit.buses) == 2

    ERC()
    generate_netlist()
    generate_xml()


def test_subcircuit_2():
    class Resistor(Part):
        def __init__(self, value, ref=None, footprint="Resistors_SMD:R_0805"):
            super().__init__("Device", "R", value=value, ref=ref, footprint=footprint)

    @subcircuit
    def resdiv_1():
        gnd = Net("GND")  # Ground reference.
        vin = Net("VI")  # Input voltage to the divider.
        vout = Net("VO")  # Output voltage from the divider.

        r1 = Resistor("1k")
        r2 = Resistor("500")

        cap = Part("Device", "C", dest=TEMPLATE)
        c1 = cap()
        c2 = cap(value="1uF")

        bus1 = Bus("BB", 10)

        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    @subcircuit
    def resdiv_2():
        resdiv_1()
        resdiv_1()

        a = Net("GND")  # Ground reference.
        b = Net("VI")  # Input voltage to the divider.
        c = Net("VO")  # Output voltage from the divider.

        r1 = Resistor("1k")
        r2 = Resistor("500")

        cap = Part("Device", "C", dest=TEMPLATE)
        c1 = cap()
        c2 = cap(value="1uF")

        bus1 = Bus("BB", 10)

        r1[1] += a  # Connect the input to the first resistor.
        r2[2] += b  # Connect the second resistor to ground.
        c += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    resdiv_2()

    assert len(default_circuit.parts) == 12
    assert len(default_circuit.get_nets()) == 9
    assert len(default_circuit.buses) == 3

    ERC()
    generate_netlist()
    generate_xml()


class Resistor(Part):
    def __init__(
        self, value, ref=None, footprint="Resistors_SMD:R_0805", tag=None, **kwargs
    ):
        super().__init__(
            "Device", "R", value=value, ref=ref, footprint=footprint, tag=tag, **kwargs
        )


def test_hierarchical_names_1():
    r1s = []
    r2s = []

    @subcircuit
    def resdiv():
        gnd = Net("GND")  # Ground reference.
        vin = Net("VI")  # Input voltage to the divider.
        vout = Net("VO")  # Output voltage from the divider.

        r1 = Resistor("1k")
        r1.tag = "resistor1"
        r1s.append(r1)
        r2 = Resistor("500", tag="resistor2")
        r2s.append(r2)

        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    resdiv()
    resdiv(tag="divider1")

    assert len(default_circuit.parts) == 4
    assert len(default_circuit.get_nets()) == 6

    assert r1s[0].hierarchical_name == "top.resdiv0.resistor1"
    assert r1s[1].hierarchical_name == "top.resdivdivider1.resistor1"
    assert r2s[0].hierarchical_name == "top.resdiv0.resistor2"
    assert r2s[1].hierarchical_name == "top.resdivdivider1.resistor2"

    ERC()
    generate_netlist()
    generate_xml()


def test_hierarchical_names_2():
    @subcircuit
    def circuit_for_test():
        pass

    circuit_for_test(tag="1")
    try:
        circuit_for_test(tag="1")
        assert False, "subcircuit should throw with duplicate hierarchical name"
    except Exception:
        pass


def test_hierarchical_names_3():
    r1 = Resistor("1k")
    r1.tag = "resistor1"

    try:
        r1 = Resistor("1k", tag="resistor1")
        assert False, "part should throw with duplicate hierarchical name"
    except Exception:
        pass
