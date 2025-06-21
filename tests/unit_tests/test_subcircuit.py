# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from builtins import super

import pytest

from skidl import (
    ERC,
    TEMPLATE,
    Bus,
    Net,
    Part,
    generate_netlist,
    generate_xml,
    generate_svg,
    subcircuit,
)

from .setup_teardown import setup_function, teardown_function

def test_subcircuit_1():
    """Test a simple resistor divider subcircuit."""
    class Resistor(Part):
        def __init__(self, value, ref=None, footprint="Resistors_SMD:R_0805"):
            super().__init__("Device", "R", value=value, ref=ref, footprint=footprint)

    @subcircuit
    def resdiv():
        """Define a resistor divider subcircuit."""
        gnd = Net("GND")  # Ground reference.
        vin = Net("VI")  # Input voltage to the divider.
        vout = Net("VO")  # Output voltage from the divider.

        r1 = Resistor("1k")  # First resistor.
        r2 = Resistor("500")  # Second resistor.

        cap = Part("Device", "C", dest=TEMPLATE)  # Capacitor template.
        c1 = cap()  # First capacitor instance.
        c2 = cap(value="1uF")  # Second capacitor instance with value.

        bus1 = Bus("BB", 10)  # Bus with 10 lines.

        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    resdiv()  # Instantiate the resistor divider subcircuit.
    resdiv()  # Instantiate another resistor divider subcircuit.

    assert len(default_circuit.parts) == 8  # Check the number of parts.
    assert len(default_circuit.get_nets()) == 6  # Check the number of nets.
    assert len(default_circuit.buses) == 2  # Check the number of buses.

    ERC()  # Run electrical rules check.
    generate_netlist()  # Generate the netlist.
    generate_xml()  # Generate the XML.

    # Test to make sure generating netlists and xml do not change the circuit.
    ntlst1 = generate_netlist()
    ntlst2 = generate_netlist()
    assert ntlst1==ntlst2
    xml1 = generate_xml()
    xml2 = generate_xml()
    assert xml1==xml2
    svg1 = generate_svg()
    svg2 = generate_svg()
    assert svg1==svg2


def test_subcircuit_2():
    """Test a nested resistor divider subcircuit."""
    class Resistor(Part):
        def __init__(self, value, ref=None, footprint="Resistors_SMD:R_0805"):
            super().__init__("Device", "R", value=value, ref=ref, footprint=footprint)

    @subcircuit
    def resdiv_1():
        """Define the first level of the resistor divider subcircuit."""
        gnd = Net("GND")  # Ground reference.
        vin = Net("VI")  # Input voltage to the divider.
        vout = Net("VO")  # Output voltage from the divider.

        r1 = Resistor("1k")  # First resistor.
        r2 = Resistor("500")  # Second resistor.

        cap = Part("Device", "C", dest=TEMPLATE)  # Capacitor template.
        c1 = cap()  # First capacitor instance.
        c2 = cap(value="1uF")  # Second capacitor instance with value.

        bus1 = Bus("BB", 10)  # Bus with 10 lines.

        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    @subcircuit
    def resdiv_2():
        """Define the second level of the resistor divider subcircuit."""
        resdiv_1()  # Instantiate the first level subcircuit.
        resdiv_1()  # Instantiate another first level subcircuit.

        a = Net("GND")  # Ground reference.
        b = Net("VI")  # Input voltage to the divider.
        c = Net("VO")  # Output voltage from the divider.

        r1 = Resistor("1k")  # First resistor.
        r2 = Resistor("500")  # Second resistor.

        cap = Part("Device", "C", dest=TEMPLATE)  # Capacitor template.
        c1 = cap()  # First capacitor instance.
        c2 = cap(value="1uF")  # Second capacitor instance with value.

        bus1 = Bus("BB", 10)  # Bus with 10 lines.

        r1[1] += a  # Connect the input to the first resistor.
        r2[2] += b  # Connect the second resistor to ground.
        c += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    resdiv_2()  # Instantiate the second level subcircuit.

    assert len(default_circuit.parts) == 12  # Check the number of parts.
    assert len(default_circuit.get_nets()) == 9  # Check the number of nets.
    assert len(default_circuit.buses) == 3  # Check the number of buses.

    ERC()  # Run electrical rules check.
    generate_netlist()  # Generate the netlist.
    generate_xml()  # Generate the XML.

    # Test to make sure generating netlists and xml do not change the circuit.
    ntlst1 = generate_netlist()
    ntlst2 = generate_netlist()
    assert ntlst1==ntlst2
    xml1 = generate_xml()
    xml2 = generate_xml()
    assert xml1==xml2
    svg1 = generate_svg()
    svg2 = generate_svg()
    assert svg1==svg2


class Resistor(Part):
    def __init__(
        self, value, ref=None, footprint="Resistors_SMD:R_0805", tag=None, **kwargs
    ):
        """Initialize a resistor part."""
        super().__init__(
            "Device", "R", value=value, ref=ref, footprint=footprint, tag=tag, **kwargs
        )


def test_hierarchical_names_1():
    """Test hierarchical names in subcircuits."""
    r1s = []
    r2s = []

    @subcircuit
    def resdiv():
        """Define a resistor divider subcircuit with hierarchical names."""
        gnd = Net("GND")  # Ground reference.
        vin = Net("VI")  # Input voltage to the divider.
        vout = Net("VO")  # Output voltage from the divider.

        r1 = Resistor("1k")  # First resistor.
        r1.tag = "resistor1"  # Tag for hierarchical name.
        r1s.append(r1)  # Append to list.
        r2 = Resistor("500", tag="resistor2")  # Second resistor with tag.
        r2s.append(r2)  # Append to list.

        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    resdiv()  # Instantiate the resistor divider subcircuit.
    resdiv(tag="divider1")  # Instantiate another resistor divider with a tag.
    r_top = Resistor("1k", tag="resistor_top")  # Instantiate a resistor on the top level.

    assert len(default_circuit.parts) == 5  # Check the number of parts.
    assert len(default_circuit.get_nets()) == 6  # Check the number of nets.

    assert r1s[0].hierarchical_name == ".resdiv1.resistor1"  # Check hierarchical name.
    assert r1s[1].hierarchical_name == ".resdiv2.resistor1"  # Check hierarchical name.
    assert r2s[0].hierarchical_name == ".resdiv1.resistor2"  # Check hierarchical name.
    assert r2s[1].hierarchical_name == ".resdiv2.resistor2"  # Check hierarchical name.
    assert r_top.hierarchical_name == ".resistor_top"  # Check top-level resistor name.

    ERC()  # Run electrical rules check.
    generate_netlist()  # Generate the netlist.
    generate_xml()  # Generate the XML.

    # Test to make sure generating netlists and xml do not change the circuit.
    ntlst1 = generate_netlist()
    ntlst2 = generate_netlist()
    assert ntlst1==ntlst2
    xml1 = generate_xml()
    xml2 = generate_xml()
    assert xml1==xml2
    svg1 = generate_svg()
    svg2 = generate_svg()
    assert svg1==svg2


def test_hierarchical_names_2():
    """Test for duplicate hierarchical names in subcircuits."""
    @subcircuit
    def circuit_for_test():
        """Define an empty subcircuit for testing."""
        pass

    circuit_for_test(tag="1")  # Instantiate the subcircuit with a tag.
    try:
        circuit_for_test(tag="1")  # Try to instantiate with the same tag.
        assert False, "subcircuit should throw with duplicate hierarchical name"
    except Exception:
        pass  # Expected exception for duplicate hierarchical name.


def test_hierarchical_names_3():
    """Test for duplicate hierarchical names in parts."""
    r1 = Resistor("1k")  # Instantiate a resistor.
    r1.tag = "resistor1"  # Tag for hierarchical name.

    try:
        r1 = Resistor("1k", tag="resistor1")  # Try to instantiate with the same tag.
        assert False, "part should throw with duplicate hierarchical name"
    except Exception:
        pass  # Expected exception for duplicate hierarchical name.
