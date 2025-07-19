# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from builtins import super

from skidl import (
    ERC,
    TEMPLATE,
    Bus,
    Group,
    Net,
    Part,
    generate_netlist,
    generate_xml,
    subcircuit,
)
from skidl.skidlbaseobj import HIER_SEP


def test_group_1():
    """Test the grouping of parts in a circuit."""
    
    class Resistor(Part):
        """Define a resistor part."""
        def __init__(self, value, ref=None, footprint="Resistors_SMD:R_0805"):
            # Initialize the resistor with given value, reference, and footprint.
            super().__init__("Device", "R", value=value, ref=ref, footprint=footprint)

    @subcircuit
    def resdiv():
        """Create a resistor divider subcircuit."""
        gnd = Net("GND")  # Ground reference.
        vin = Net("VI")  # Input voltage to the divider.
        vout = Net("VO")  # Output voltage from the divider.

        r1 = Resistor("1k")  # First resistor.
        r2 = Resistor("500")  # Second resistor.

        with Group("Caps"):
            # Create a group for capacitors.
            cap = Part("Device", "C", dest=TEMPLATE)
            c1 = cap()  # First capacitor.
            c2 = cap(value="1uF")  # Second capacitor with value 1uF.
            with Group("Resistors"):
                # Create a subgroup for resistors.
                r3 = Resistor("5k")  # Third resistor.
                r4 = Resistor("10k")  # Fourth resistor.
                vin & (r3 | c1) & (r4 | c2) & gnd  # Connect components in series and parallel.

        bus1 = Bus("BB", 10)  # Create a bus with 10 lines.

        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    with Group("Resistor_Divider"):
        # Create a group for the resistor divider subcircuits.
        resdiv()  # Add the first resistor divider.
        resdiv()  # Add the second resistor divider.

    assert len(default_circuit.parts) == 12  # Check the number of parts.
    assert len(default_circuit.get_nets()) == 8  # Check the number of nets.
    assert len(default_circuit.buses) == 2  # Check the number of buses.

    depth = 0
    for part in default_circuit.parts:
        # Calculate the maximum depth of hierarchical names.
        depth = max(depth, part.hierarchical_name.count(HIER_SEP))
    assert depth == 5  # Check the maximum depth.

    ERC()  # Run electrical rules check.
    generate_netlist()  # Generate the netlist.
    generate_xml()  # Generate the XML output.
