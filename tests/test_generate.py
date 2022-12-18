# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import os
import os.path
import pytest
import shutil
import sys

from skidl import (
    TEMPLATE,
    Net,
    Part,
    Group,
    subcircuit,
    generate_netlist,
    generate_svg,
    generate_xml,
    generate_graph,
    generate_schematic,
    generate_pcb,
)

from .setup_teardown import setup_function, teardown_function


def create_output_dir(leaf_dir_name):
    output_file_root = "schematic_output"
    python_version = ".".join([str(n) for n in sys.version_info[0:3]])
    output_dir = os.path.join(".", output_file_root, python_version, leaf_dir_name)
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir)
    return output_dir


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
    generate_schematic(filepath=create_output_dir("generate_1"), flatness=1.0)
    generate_pcb()


def test_pcb_1():
    """Test PCB generation."""

    l1 = Part(
        "Device.lib",
        "L",
        footprint="Inductor_SMD:L_0805_2012Metric_Pad1.15x1.40mm_HandSolder",
    )
    r1, r2 = (
        Part(
            "Device.lib",
            "R",
            dest=TEMPLATE,
            value="200.0",
            footprint="Resistor_SMD:R_0805_2012Metric",
        )
        * 2
    )
    q1 = Part(
        "Device.lib", "Q_NPN_CBE", footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2"
    )
    c1 = Part(
        "Device.lib",
        "C",
        value="10pF",
        footprint="Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder",
    )
    r3 = r2(value="1K", footprint="Resistor_SMD:R_0805_2012Metric")
    vcc, vin, vout, gnd = Net("VCC"), Net("VIN"), Net("VOUT"), Net("GND")
    vcc & r1 & vin & r2 & gnd
    vcc & r3 & vout & q1["C,E"] & gnd
    q1["B"] += vin
    vout & (l1 | c1) & gnd
    rly = Part("Relay", "TE_PCH-1xxx2M", footprint="Relay_THT:Relay_SPST_TE_PCH-1xxx2M")
    rly[1, 2, 3, 5] += gnd
    led = Part("Device.lib", "LED_ARGB", symtx="RH", footprint="LED_SMD:LED_RGB_1210")
    r, g, b = Net("R"), Net("G"), Net("B")
    led["A,RK,GK,BK"] += vcc, r, g, b
    Part(
        lib="MCU_Microchip_PIC10.lib",
        name="PIC10F200-IMC",
        footprint="Package_DFN_QFN:DFN-8-1EP_2x3mm_P0.5mm_EP0.61x2.2mm",
    )

    generate_pcb()


def test_schematic_gen_place():
    @subcircuit
    def test():
        q = Part(lib="Device.lib", name="Q_PNP_CBE", footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2", dest=TEMPLATE, symtx="V")
        r = Part("Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric",dest=TEMPLATE)
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
                a & r1 & (q1['c,e'] | q2['c,e']) & r3 & o
                b & r2 & (q1['b'] | q2['b'])

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

    test()
    generate_schematic(filepath=create_output_dir("place"), flatness=0.5)

def test_schematic_gen_simple():
    q = Part(lib="Device.lib", name="Q_PNP_CBE", footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2", dest=TEMPLATE, symtx="V")
    qs = q(15)
    ns = [Net() for p in qs[0].pins]
    for q in qs:
        for p, n in zip(q.pins, ns):
            n += p
    generate_schematic(filepath=create_output_dir("simple"), flatness=1.0)

def test_schematic_gen_units():
    @subcircuit
    def test():
        q = Part(lib="Device.lib", name="Q_PNP_CBE", footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2", dest=TEMPLATE, symtx="V")
        # r = Part("Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric",dest=TEMPLATE)
        rn = Part("Device", "R_Pack05_Split", footprint=":")
        gndt = Part("power", "GND", footprint='TestPoint:TestPoint_Pad_D4.0mm')
        vcct = Part("power", "VCC", footprint='TestPoint:TestPoint_Pad_D4.0mm')

        gnd = Net("GND", stub=True, netclass='Power')
        vcc = Net("VCC", stub=True, netclass='Power')
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
        # r1, r2, r3, r4, r5 = r(5, value="10K")
        r1, r2, r3, r4, r5 = rn.unit.values()
        a & r1 & q1["B", "C"] & r4 & q2["B", "C"] & a_and_b & r5 & gnd
        b & r2 & q1["B"]
        q1["C"] & r3 & gnd
        vcc & q1["E"]
        vcc & q2["E"]

    with Group("A"):
        q = Part(lib="Device.lib", name="Q_PNP_CBE", footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2", dest=TEMPLATE, symtx="V")
        q()
        test()

    generate_schematic(filepath=create_output_dir("units"), flatness=1.0)

def test_schematic_gen_hier():
    with Group("A"):
        with Group("B"):
            q = Part(lib="Device.lib", name="Q_PNP_CBE", footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2", dest=TEMPLATE, symtx="V")
            r = Part("Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric",dest=TEMPLATE)
            gndt = Part("power", "GND", footprint='TestPoint:TestPoint_Pad_D4.0mm')
            vcct = Part("power", "VCC", footprint='TestPoint:TestPoint_Pad_D4.0mm')

            gnd = Net("GND", stub=True, netclass='Power')
            vcc = Net("VCC", stub=True, netclass='Power')
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

    generate_schematic(filepath=create_output_dir("hier"), flatness=0.0)

def test_schematic_hier_connections():

    r = Part("Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric",dest=TEMPLATE)
    q = Part(lib="Device.lib", name="Q_PNP_CBE", footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2", dest=TEMPLATE, symtx="V")

    a = Net("A")
    b = Net("B")
    o = Net("O")

    for _ in range(3):
        with Group("A:"):
            q1 = q()
            q2 = q()
            r1, r2, r3 = r(3, value="10K")
            a & r1 & (q1['c,e'] | q2['c,e']) & r3 & o
            b & r2 & (q1['b'] | q2['b'])

    generate_schematic(filepath=create_output_dir("hier_connections"), flatness=1.0)

def test_schematic_part_tx():
    q = Part(lib="Device.lib", name="Q_PNP_CBE", footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2", dest=TEMPLATE)
    q1 = q(symtx="")
    q2 = q(symtx="R")
    q3 = q(symtx="L")
    q4 = q(symtx="H")
    q5 = q(symtx="V")
    generate_schematic(filepath=create_output_dir("part_tx"), flatness=1.0)
