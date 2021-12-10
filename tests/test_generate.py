# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import (
    TEMPLATE,
    Net,
    Part,
    generate_netlist,
    generate_svg,
    generate_xml,
    generate_graph,
    generate_schematic,
    generate_pcb
)

from .setup_teardown import setup_function, teardown_function


def test_generate_1():
    q = Part(lib="Device.lib", name="Q_PNP_CBE", footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2", dest=TEMPLATE, symtx="V")
    r = Part("Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric",dest=TEMPLATE)
    gndt = Part("power", "GND", footprint='TestPoint:TestPoint_Pad_D4.0mm')
    vcct = Part("power", "VCC", footprint='TestPoint:TestPoint_Pad_D4.0mm')

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

    generate_svg()
    generate_netlist()
    generate_xml()
    generate_graph()
    generate_schematic(filepath='test_generate.sch')
    generate_pcb()
