# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from builtins import super

import pytest

from skidl import (
    ERC,
    SKIDL,
    TEMPLATE,
    Bus,
    Circuit,
    Net,
    Part,
    Pin,
    generate_netlist,
    generate_xml,
    subcircuit,
)


def test_subcircuit_1():
    """Test subcircuit creation and connection."""
    class Resistor(Part):
        def __init__(self, value, ref=None, footprint="Resistors_SMD:R_0805"):
            super().__init__("Device", "R", value=value, ref=ref, footprint=footprint)

    @subcircuit
    def resdiv():
        """Create a resistor divider subcircuit."""
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

    # Create multiple circuits and add the subcircuit to them.
    circuit1 = Circuit()
    circuit2 = Circuit()
    resdiv(circuit=circuit2)
    resdiv()
    resdiv(circuit=circuit1)
    resdiv(circuit=circuit1)
    resdiv(circuit=circuit2)
    resdiv(circuit=circuit2)

    # Assert the number of parts, nets, and buses in each circuit.
    assert len(default_circuit.parts) == 4
    assert len(default_circuit.get_nets()) == 3
    assert len(default_circuit.buses) == 1

    assert len(circuit1.parts) == 8
    assert len(circuit1.get_nets()) == 6
    assert len(circuit1.buses) == 2

    assert len(circuit2.parts) == 12
    assert len(circuit2.get_nets()) == 9
    assert len(circuit2.buses) == 3

    # Perform ERC and generate netlist and XML for each circuit.
    ERC()
    generate_netlist()
    generate_xml()

    circuit1.ERC()
    circuit1.generate_netlist()
    circuit1.generate_xml()

    circuit2.ERC()
    circuit2.generate_netlist()
    circuit2.generate_xml()


def test_subcircuit_2():
    """Test nested subcircuit creation and connection."""
    class Resistor(Part):
        def __init__(self, value, ref=None, footprint="Resistors_SMD:R_0805"):
            super().__init__("Device", "R", value=value, ref=ref, footprint=footprint)

    @subcircuit
    def resdiv_1():
        """Create a resistor divider subcircuit with capacitors."""
        gnd = Net("GND")  # Ground reference.
        vin = Net("VI")  # Input voltage to the divider.
        vout = Net("VO")  # Output voltage from the divider.

        r1 = Resistor("1k")
        r2 = Resistor("500")

        cap = Part("Device", "C", dest=TEMPLATE)
        c1 = cap()
        c2 = cap(value="1uF")
        c1[1] += NC
        c2[1, 2] += NC

        bus1 = Bus("BB", 10)

        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    @subcircuit
    def resdiv_2():
        """Create a nested resistor divider subcircuit."""
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

    # Create multiple circuits and add the nested subcircuit to them.
    default_circuit.name = "DEFAULT"
    circuit1 = Circuit(name="CIRCUIT1")
    circuit2 = Circuit(name="CIRCUIT2")
    resdiv_2(circuit=circuit2)
    resdiv_2()
    resdiv_2(circuit=circuit1)
    resdiv_2(circuit=circuit1)
    resdiv_2(circuit=circuit2)
    resdiv_2(circuit=circuit2)

    # Assert the number of parts, nets, buses, and NC pins in each circuit.
    assert len(default_circuit.parts) == 12
    assert len(default_circuit.get_nets()) == 9
    assert len(default_circuit.buses) == 3
    assert len(NC.pins) == 6

    assert len(circuit1.parts) == 24
    assert len(circuit1.get_nets()) == 18
    assert len(circuit1.buses) == 6
    assert len(circuit1.NC.pins) == 12

    assert len(circuit2.parts) == 36
    assert len(circuit2.get_nets()) == 27
    assert len(circuit2.buses) == 9
    assert len(circuit2.NC.pins) == 18

    # Perform ERC and generate netlist and XML for each circuit.
    ERC()
    generate_netlist()
    generate_xml()

    circuit1.ERC()
    circuit1.generate_netlist()
    circuit1.generate_xml()

    circuit2.ERC()
    circuit2.generate_netlist()
    circuit2.generate_xml()


def test_circuit_add_rmv_1():
    """Test adding and removing parts and nets between circuits."""
    circuit1 = Circuit()
    circuit2 = Circuit()
    r1 = Part("Device", "R")
    n1 = Net("N1")
    circuit1 += r1
    circuit1 += n1
    assert len(circuit1.parts) == 1
    assert len(circuit2.parts) == 0
    assert len(circuit1.nets) == 2  # Add 1 for NC
    assert len(circuit2.nets) == 1  # Add 1 for NC
    circuit2 += r1
    circuit2 += n1
    assert len(circuit1.parts) == 0
    assert len(circuit2.parts) == 1
    assert len(circuit1.nets) == 1  # Add 1 for NC
    assert len(circuit2.nets) == 2  # Add 1 for NC
    n1 += r1[1]
    with pytest.raises(ValueError):
        circuit1 += r1


def test_circuit_add_rmv_2():
    """Test adding and removing buses between circuits."""
    circuit1 = Circuit()
    circuit2 = Circuit()
    r1 = Part("Device", "R")
    bus = Bus("B", 8)
    circuit1 += bus
    assert len(circuit1.nets) == len(bus) + 1  # Add 1 for NC
    assert len(circuit2.nets) == 1  # Add 1 for NC
    circuit2 += bus
    assert len(circuit1.nets) == 1  # Add 1 for NC
    assert len(circuit2.nets) == len(bus) + 1  # Add 1 for NC


def test_circuit_add_rmv_3():
    """Test adding and removing multiple parts, nets, and buses."""
    circuit = Circuit()
    r = Part("Device", "R")
    c = Part("Device", "C")
    n = Net("N")
    bus = Bus("B", 8)
    circuit += r, c, bus, n
    circuit += (
        r,
        c,
        bus,
        n,
    )  # Shouldn't do anything since these are already in the circuit.
    assert len(circuit.nets) == len(bus) + 1 + 1  # Add 1 for NC
    assert len(circuit.parts) == 2
    assert len(circuit.buses) == 1


def test_circuit_connect_btwn_circuits_1():
    """Test connecting parts between different circuits."""
    circuit1 = Circuit()
    circuit2 = Circuit()
    r1 = Part(tool=SKIDL, name="R")
    r1 += Pin(num=1), Pin(num=2)
    n1 = Net("N1")
    circuit1 += r1
    circuit2 += n1
    with pytest.raises(ValueError):
        n1 += r1[1]


def test_circuit_NC_1():
    """Test handling of NC (not connected) pins."""
    circuit1 = Circuit()
    circuit2 = Circuit()
    res = Part(tool=SKIDL, name="res", dest=TEMPLATE, pins=[Pin(num=1), Pin(num=2)])
    r1 = res()
    r2 = res(circuit=circuit1)
    r3 = res()
    circuit2 += r3
    r2[1, 2] += circuit1.NC
    r3[1] += circuit2.NC
    assert len(NC.pins) == 0
    assert len(circuit1.NC.pins) == 2
    assert len(circuit2.NC.pins) == 1


def test_circuit_context_1():
    """Test using circuits as context managers."""
    circuit1 = Circuit()
    circuit2 = Circuit()
    res = Part(tool=SKIDL, name="res", dest=TEMPLATE, pins=[Pin(num=1), Pin(num=2)])
    with circuit1:
        for _ in range(3):
            res()
    with circuit2:
        for _ in range(10):
            res()
    assert len(circuit1.parts) == 3
    assert len(circuit2.parts) == 10
