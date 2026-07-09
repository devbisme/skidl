# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Part, netlist_to_skidl, generate_netlist, TEMPLATE, Net, subcircuit


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

    default_circuit.mini_reset()

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


def test_parser_missing_root_sheet():
    """Hierarchy whose root sheet is not enumerated must still convert.

    Some exporters (cs-native netlists) list only the leaf sheets, so a net
    spanning two subsheets has a lowest-common-ancestor sheet ('/') that is
    absent from the design/sheet block. The converter must synthesize the
    missing ancestor instead of raising ``KeyError: '/'`` in analyze_nets.
    """
    netlist = """
(export (version "E")
  (design
    (sheet (number "1") (name "/sub_a/") (tstamps "/a/"))
    (sheet (number "2") (name "/sub_b/") (tstamps "/b/")))
  (components
    (comp (ref "R1") (value "1k")
      (libsource (lib "Device") (part "R"))
      (sheetpath (names "/sub_a/") (tstamps "/a/")))
    (comp (ref "R2") (value "2k")
      (libsource (lib "Device") (part "R"))
      (sheetpath (names "/sub_b/") (tstamps "/b/"))))
  (nets
    (net (code "1") (name "/SHARED")
      (node (ref "R1") (pin "2"))
      (node (ref "R2") (pin "1")))
    (net (code "2") (name "/sub_a/A")
      (node (ref "R1") (pin "1")))
    (net (code "3") (name "/sub_b/B")
      (node (ref "R2") (pin "2")))))
"""
    import tempfile
    import os

    out_dir = tempfile.mkdtemp()
    # Must not raise KeyError: '/'.
    netlist_to_skidl(netlist, output_dir=out_dir)

    files = set(os.listdir(out_dir))
    # One @subcircuit file per leaf sheet, plus a synthesized top and a main.
    assert {"main.py", "top.py", "sub_a.py", "sub_b.py"} <= files
    top = open(os.path.join(out_dir, "top.py")).read()
    # The shared net is passed from the synthesized root into both subsheets.
    assert "sub_a(" in top and "sub_b(" in top
    assert "SHARED" in top
