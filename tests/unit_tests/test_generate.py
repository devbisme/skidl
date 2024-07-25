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

from .setup_teardown import setup_function, teardown_function

@subcircuit
def flat_circuit():
    q = Part(
        lib="Device",
        name="Q_PNP_CBE",
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
        dest=TEMPLATE,
        symtx="V",
        value="Q_NPN_CBE",
    )
    r = Part(
        "Device", "R", footprint="Resistor_SMD:R_0805_2012Metric", dest=TEMPLATE
    )
    gndt = Part("power", "GND", footprint="TestPoint:TestPoint_Pad_D4.0mm")
    vcct = Part("power", "VCC", footprint="TestPoint:TestPoint_Pad_D4.0mm")

    gnd = Net("GND")
    vcc = Net("VCC")
    gnd & gndt
    vcc & vcct
    a = Net("A", netio="i")
    b = Net("B", netio="i")
    a_and_b = Net("A_AND_B", netio="o")
    q1 = q()
    q1.E.symio = "i"
    q1.B.symio = "i"
    q1.C.symio = "o"
    q2 = q()
    q2.E.symio = "i"
    q2.B.symio = "i"
    q2.C.symio = "o"
    r1, r2, r3, r4, r5 = r(5, value="10K")
    a & r1 & q1["B", "C"] & r4 & q2["B", "C"] & a_and_b & r5 & gnd
    b & r2 & q1["B"]
    q1["C"] & r3 & gnd
    vcc & q1["E"]
    vcc & q2["E"]

def test_gen_flat_svg():
    flat_circuit()
    generate_svg()

def test_gen_flat_netlist():
    flat_circuit()
    generate_netlist()

def test_gen_flat_xml():
    flat_circuit()
    generate_xml()

def test_gen_flat_graph():
    flat_circuit()
    generate_graph()

@subcircuit
def hier_circuit():
    q = Part(
        lib="Device",
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
    hier_circuit()
    generate_svg()

def test_gen_hier_netlist():
    hier_circuit()
    generate_netlist()

def test_gen_hier_xml():
    hier_circuit()
    generate_xml()

def test_gen_hier_graph():
    hier_circuit()
    generate_graph()

def test_gen_pcb():
    esp32 = Part('RF_Module','ESP32-WROOM-32', footprint='RF_Module:ESP32-WROOM-32')
    generate_pcb()
    
