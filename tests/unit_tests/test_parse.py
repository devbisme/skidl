# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Part, netlist_to_skidl, generate_netlist, TEMPLATE, Net, subcircuit
from skidl.netlist_to_skidl import HierarchicalConverter


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
    new_circuit = test_parser_1.__builtins__["default_circuit"]

    # Get comparison tuple for the reconstructed circuit.
    new_tuple = new_circuit.to_tuple()

    # Check that the original and new circuits are the same.
    assert original_tuple == new_tuple


def test_parser_boolean_property_without_value():
    """Test parsing a netlist with a property that has no value.

    KiCad 10 exports boolean component properties (e.g. exclude_from_bom,
    exclude_from_sim) as `(property (name "..."))` without a `(value ...)`
    child. The parser must treat the missing value as an empty string
    instead of crashing. (Upstream issue: devbisme/skidl PR #317.)
    """

    # Minimal KiCad 10 style netlist with a valueless boolean property.
    netlist = """
(export
    (version "E")
    (design
        (source "test.kicad_sch")
        (date "2026-07-02T16:56:33")
        (tool "Eeschema 10.0.3")
        (sheet
            (number "1")
            (name "/")
            (tstamps "/")))
    (components
        (comp
            (ref "P5")
            (value "MOUNTING_HOLE")
            (footprint "Footprints:MountingHole_3.2mm_M3_DIN965_Pad")
            (libsource
                (lib "ecc83-pp")
                (part "CONN_1")
                (description ""))
            (property
                (name "Sheetname")
                (value ""))
            (property
                (name "exclude_from_bom"))
            (sheetpath
                (names "/")
                (tstamps "/"))
            (tstamps "00000000-0000-0000-0000-000054a5890a")))
    (nets
        (net
            (code "1")
            (name "GND")
            (class "Default")
            (node
                (ref "P5")
                (pin "1")
                (pintype "passive")))))
"""

    # Parsing must not raise and the boolean property value must be "".
    converter = HierarchicalConverter(netlist)
    part = converter.netlist.parts[0]
    prop_values = {prop.name: prop.value for prop in part.properties}
    assert prop_values["exclude_from_bom"] == ""
    assert prop_values["Sheetname"] == ""

    # The full netlist-to-SKiDL conversion must also succeed.
    code = netlist_to_skidl(netlist)
    assert "P5" in code
