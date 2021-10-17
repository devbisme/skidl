# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import TEMPLATE, Net, Part, generate_pcb

from .setup_teardown import setup_function, teardown_function


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
