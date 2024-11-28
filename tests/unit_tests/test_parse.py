# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from skidl import Part, netlist_to_skidl, generate_netlist, TEMPLATE
from skidl.utilities import find_and_read_file


def test_parser_1():
    """Test the parser with a simple netlist."""

    # Create resistor and capacitor parts as templates.
    r = Part("Device", "R", dest=TEMPLATE)
    c = Part("Device", "C", dest=TEMPLATE)

    # Create a simple circuit with two parallel branches in series.
    (r(value=0.001) | c(value=0.001)) & (r(value=0.002) | c(value=0.002))

    # Generate a netlist file from the circuit.
    generate_netlist(file_="test_parser_1.net")

    # Convert the netlist back to SKiDL code.
    skidl_code = netlist_to_skidl(find_and_read_file("test_parser_1.net")[0])
