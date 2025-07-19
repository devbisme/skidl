# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import glob
import inspect
import itertools
import os
import os.path
import sys

import pytest

from skidl import (
    ERC,
    POWER,
    TEMPLATE,
    Bus,
    Group,
    Net,
    Part,
    PartTmplt,
    SubCircuit,
    generate_graph,
    generate_netlist,
    generate_pcb,
    generate_svg,
    generate_xml,
    subcircuit,
)


@subcircuit
def flat_circuit():
    """Create a flat circuit."""
    # Define parts.
    try:
        q = Part(
            lib="Device",
            name="Q_PNP_CBE",
            footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
            dest=TEMPLATE,
            symtx="V",
            value="Q_PNP_CBE",
        )
    except ValueError:
        # If the part is not found, use another library.
        q = Part(
            lib="Transistor_BJT",
            name="Q_PNP_CBE",
            footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
            dest=TEMPLATE,
            symtx="V",
            value="Q_PNP_CBE",
        )
    r = Part(
        "Device", "R", footprint="Resistor_SMD:R_0805_2012Metric", dest=TEMPLATE
    )
    gndt = Part("power", "GND", footprint="TestPoint:TestPoint_Pad_D4.0mm")
    vcct = Part("power", "VCC", footprint="TestPoint:TestPoint_Pad_D4.0mm")

    # Define nets.
    gnd = Net("GND")
    vcc = Net("VCC")
    gnd & gndt
    vcc & vcct
    a = Net("A", netio="i")
    b = Net("B", netio="i")
    a_and_b = Net("A_AND_B", netio="o")

    # Instantiate parts.
    q1 = q()
    q1.E.symio = "i"
    q1.B.symio = "i"
    q1.C.symio = "o"
    q2 = q()
    q2.E.symio = "i"
    q2.B.symio = "i"
    q2.C.symio = "o"
    r1, r2, r3, r4, r5 = r(5, value="10K")

    # Connect parts using nets.
    a & r1 & q1["B", "C"] & r4 & q2["B", "C"] & a_and_b & r5 & gnd
    b & r2 & q1["B"]
    q1["C"] & r3 & gnd
    vcc & q1["E"]
    vcc & q2["E"]

def test_gen_flat_svg():
    """Test generating SVG for flat circuit."""
    flat_circuit()
    # Test to see if generating the SVG twice produces the same result.
    svg1 = generate_svg()
    svg2 = generate_svg()
    assert svg1 == svg2

def test_gen_flat_netlist():
    """Test generating netlist for flat circuit."""
    flat_circuit()
    # Test to see if generating the netlist twice produces the same result.
    ntlst1 = generate_netlist()
    ntlst2 = generate_netlist()
    assert ntlst1 == ntlst2

def test_gen_flat_xml():
    """Test generating XML for flat circuit."""
    flat_circuit()
    # Test to see if generating the XML twice produces the same result.
    xml1 = generate_xml()
    xml2 = generate_xml()
    assert xml1 == xml2

def test_gen_flat_graph():
    """Test generating graph for flat circuit."""
    flat_circuit()
    # Test to see if generating the DOT graph twice produces the same result.
    grph1 = generate_graph()
    grph2 = generate_graph()
    assert grph1.source == grph2.source

@subcircuit
def hier_circuit():
    """Create a hierarchical circuit."""
    # Define parts.
    try:
        q = Part(
            lib="Device",
            name="Q_PNP_CBE",
            footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
            dest=TEMPLATE,
            # symtx="V",
        )
    except ValueError:
        q = Part(
            lib="Transistor_BJT",
            name="Q_PNP_CBE",
            footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
            dest=TEMPLATE,
            # symtx="V",
        )
    r = Part(
        "Device", "R", footprint="Resistor_SMD:R_0805_2012Metric", dest=TEMPLATE
    )
    vcc = Net("VCC")
    gnd = Net("GND")

    # Create groups of parts and nets.
    for _ in range(3):
        with Group("G:"):
            a = Net("A")
            b = Net("B")
            o = Net("O")
            q1 = q()
            q2 = q()
            r1, r2, r3 = r(3, value="10K")
            a & r1 & (q1["c,e"] | q2["c,e"]) & r3 & o
            b & r2 & (q1["b"] | q2["b"])

    with Group("B:"):
        n = 5
        qs = []
        rs = []
        for i in range(n):
            qs.append(q())
            rs.append(r())
            vcc & rs[-1] & qs[-1]["c,e"]
            if i:
                qs[-2].E & qs[-1].B
        Net("A") & r() & qs[0].B
        qs[-1].E & gnd
        qs[-1].C & Net("O")

def test_gen_hier_svg():
    """Test generating SVG for hierarchical circuit."""
    hier_circuit()
    # Test to see if generating the SVG twice produces the same result.
    svg1 = generate_svg()
    svg2 = generate_svg()
    assert svg1 == svg2

def test_gen_hier_netlist():
    """Test generating netlist for hierarchical circuit."""
    hier_circuit()
    # Test to see if generating the netlist twice produces the same result.
    ntlst1 = generate_netlist()
    ntlst2 = generate_netlist()
    assert ntlst1 == ntlst2

def test_gen_hier_xml():
    """Test generating XML for hierarchical circuit."""
    hier_circuit()
    # Test to see if generating the XML twice produces the same result.
    xml1 = generate_xml()
    xml2 = generate_xml()
    assert xml1 == xml2

def test_gen_hier_graph():
    """Test generating graph for hierarchical circuit."""
    hier_circuit()
    # Test to see if generating the DOT graph twice produces the same result.
    grph1 = generate_graph()
    grph2 = generate_graph()
    assert grph1.source == grph2.source

def test_gen_pcb():
    """Test generating PCB."""
    esp32 = Part('RF_Module','ESP32-WROOM-32', footprint='RF_Module:ESP32-WROOM-32')
    generate_pcb()

def test_global_net_names():
    RR = Part('Device', 'R', dest=TEMPLATE)
    RR1 = RR(value='1M')
    RR2 = RR(value='2M')
    RR3 = RR(value='3M')

    (RR1 & RR2) | RR3 # results in `N$2` and `N$3`
    RR1[1] += Net('net1')
    RR2[2] += Net('net2')
    #(RR1 & RR2) | RR3 # results in `net1` and `net2`

    generate_netlist()

    assert RR1[1].net.name == 'net1'
    assert RR2[2].net.name == 'net2'

