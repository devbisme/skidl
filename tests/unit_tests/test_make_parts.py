# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

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
from skidl.pin import pin_types


def test_subcircuit_1():
    """Test subcircuit creation and connection."""
    @subcircuit
    def resdiv():
        """Create a resistor divider subcircuit."""
        gnd = Net("GND")  # Ground reference.
        vin = Net("VI")  # Input voltage to the divider.
        vout = Net("VO")  # Output voltage from the divider.

        # Create resistor part template.
        res = Part(
            tool=SKIDL,
            name="res",
            ref_prefix="R",
            dest=TEMPLATE,
            pins=[
                Pin(num=1, func=pin_types.PASSIVE),
                Pin(num=2, func=pin_types.PASSIVE),
            ],
        )
        r1 = res(value="1K")
        r2 = res(value="500")

        # Create capacitor part template.
        cap = Part(
            tool=SKIDL,
            name="cap",
            ref_prefix="C",
            dest=TEMPLATE,
            pins=[
                Pin(num=1, func=pin_types.PASSIVE),
                Pin(num=2, func=pin_types.PASSIVE),
            ],
        )
        c1 = cap()
        c2 = cap(value="1uF")

        bus1 = Bus("BB", 10)  # Create a bus.

        # Connect the components.
        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    # Create circuits and add subcircuits to them.
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

    # Run ERC and generate netlist and XML for each circuit.
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
        """Create a resistor part."""
        def __init__(self, value, ref=None, footprint="Resistors_SMD:R_0805"):
            super().__init__("Device", "R", value=value, ref=ref, footprint=footprint)

    @subcircuit
    def resdiv_1():
        """Create a resistor divider subcircuit."""
        gnd = Net("GND")  # Ground reference.
        vin = Net("VI")  # Input voltage to the divider.
        vout = Net("VO")  # Output voltage from the divider.

        # Create resistor part template.
        res = Part(
            tool=SKIDL,
            name="res",
            ref_prefix="R",
            dest=TEMPLATE,
            pins=[
                Pin(num=1, func=pin_types.PASSIVE),
                Pin(num=2, func=pin_types.PASSIVE),
            ],
        )
        r1 = res(value="1K")
        r2 = res(value="500")

        # Create capacitor part template.
        cap = Part(
            tool=SKIDL,
            name="cap",
            ref_prefix="C",
            dest=TEMPLATE,
            pins=[
                Pin(num=1, func=pin_types.PASSIVE),
                Pin(num=2, func=pin_types.PASSIVE),
            ],
        )
        c1 = cap()
        c2 = cap(value="1uF")

        bus1 = Bus("BB", 10)  # Create a bus.

        # Connect the components.
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

        # Create resistor part template.
        res = Part(
            tool=SKIDL,
            name="res",
            ref_prefix="R",
            dest=TEMPLATE,
            pins=[
                Pin(num=1, func=pin_types.PASSIVE),
                Pin(num=2, func=pin_types.PASSIVE),
            ],
        )
        r1 = res(value="1K")
        r2 = res(value="500")

        # Create capacitor part template.
        cap = Part(
            tool=SKIDL,
            name="cap",
            ref_prefix="C",
            dest=TEMPLATE,
            pins=[
                Pin(num=1, func=pin_types.PASSIVE),
                Pin(num=2, func=pin_types.PASSIVE),
            ],
        )
        c1 = cap()
        c2 = cap(value="1uF")

        bus1 = Bus("BB", 10)  # Create a bus.

        # Connect the components.
        r1[1] += a  # Connect the input to the first resistor.
        r2[2] += b  # Connect the second resistor to ground.
        c += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    # Create circuits and add nested subcircuits to them.
    circuit1 = Circuit()
    circuit2 = Circuit()
    resdiv_2(circuit=circuit2)
    resdiv_2()
    resdiv_2(circuit=circuit1)
    resdiv_2(circuit=circuit1)
    resdiv_2(circuit=circuit2)
    resdiv_2(circuit=circuit2)

    # Assert the number of parts, nets, and buses in each circuit.
    assert len(default_circuit.parts) == 12
    assert len(default_circuit.get_nets()) == 9
    assert len(default_circuit.buses) == 3

    assert len(circuit1.parts) == 24
    assert len(circuit1.get_nets()) == 18
    assert len(circuit1.buses) == 6

    assert len(circuit2.parts) == 36
    assert len(circuit2.get_nets()) == 27
    assert len(circuit2.buses) == 9

    # Run ERC and generate netlist and XML for each circuit.
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
    r1 = Part(tool=SKIDL, name="res", ref_prefix="R", pins=[Pin(num=1), Pin(num=2)])

    n1 = Net("N1")  # Create a net.
    circuit1 += r1  # Add resistor to circuit1.
    circuit1 += n1  # Add net to circuit1.
    assert len(circuit1.parts) == 1
    assert len(circuit2.parts) == 0
    assert len(circuit1.nets) == 2  # Add 1 for NC
    assert len(circuit2.nets) == 1  # Add 1 for NC
    circuit2 += r1  # Move resistor to circuit2.
    circuit2 += n1  # Move net to circuit2.
    assert len(circuit1.parts) == 0
    assert len(circuit2.parts) == 1
    assert len(circuit1.nets) == 1  # Add 1 for NC
    assert len(circuit2.nets) == 2  # Add 1 for NC
    n1 += r1[1]  # Connect net to resistor pin.
    with pytest.raises(ValueError):
        circuit1 += r1  # Attempt to add resistor back to circuit1.


def test_circuit_add_rmv_2():
    """Test adding and removing buses between circuits."""
    circuit1 = Circuit()
    circuit2 = Circuit()
    r1 = Part(tool=SKIDL, name="res", ref_prefix="R", pins=[Pin(num=1), Pin(num=2)])
    bus = Bus("B", 8)  # Create a bus.
    circuit1 += bus  # Add bus to circuit1.
    assert len(circuit1.nets) == len(bus) + 1  # Add 1 for NC
    assert len(circuit2.nets) == 1  # Add 1 for NC
    circuit2 += bus  # Move bus to circuit2.
    assert len(circuit1.nets) == 1  # Add 1 for NC
    assert len(circuit2.nets) == len(bus) + 1  # Add 1 for NC


def test_circuit_connect_btwn_circuits_1():
    """Test connecting parts and nets between different circuits."""
    circuit1 = Circuit()
    circuit2 = Circuit()
    # r1 = Part(tool=SKIDL, name='R', pins=[Pin(num=1), Pin(num=2)])
    r1 = Part(tool=SKIDL, name="res", ref_prefix="R")
    r1 += Pin(num=1), Pin(num=2)  # Add pins to resistor.
    n1 = Net("N1")  # Create a net.
    circuit1 += r1  # Add resistor to circuit1.
    circuit2 += n1  # Add net to circuit2.
    with pytest.raises(ValueError):
        n1 += r1[1]  # Attempt to connect net from circuit2 to resistor in circuit1.
