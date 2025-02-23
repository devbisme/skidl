# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from skidl import Part, netlist_to_skidl, generate_netlist, TEMPLATE, Net, subcircuit
from skidl.utilities import find_and_read_file


def test_parser_1():
    """Test the parser with a simple netlist."""

    @subcircuit
    def sub1(n1, n2):
        # Create resistor and capacitor parts as templates.
        r = Part("Device", "R", dest=TEMPLATE)
        c = Part("Device", "C", dest=TEMPLATE)

        # Create a simple circuit with two parallel branches in series.
        n1 & (r(value=0.001) | c(value=0.001)) & (r(value=0.002) | c(value=0.002)) & n2

    @subcircuit
    def main():
        # Create global nets
        i, o = Net(), Net()

        # Create subcircuits
        sub1(i, o)
        sub1(i, o)

    main()

    # Generate a netlist file and string from the circuit.
    netlist = generate_netlist(file_="test_parser_1.net")

    # Get comparison tuple for the original circuit.
    original_tuple = default_circuit.to_tuple()

    # Convert the netlist back to SKiDL code.
    netlist_to_skidl(netlist, output_dir="./test_parser_1")

    # Create __init__.py file in the output directory so import will work.
    with open("./test_parser_1/__init__.py", "w") as f:
        f.write("import main\n")

    default_circuit.reset()

    # Import and execute the generated SKiDL code.
    import sys
    import os
    sys.path.insert(0, os.path.abspath("./test_parser_1"))
    import test_parser_1

    # Get the default circuit created by the generated SKiDL code.
    new_circuit = test_parser_1.__builtins__['default_circuit']

    # Get comparison tuple for the reconstructed circuit.
    new_tuple =  new_circuit.to_tuple()

    # Check that the original and new circuits are the same.
    assert original_tuple == new_tuple
