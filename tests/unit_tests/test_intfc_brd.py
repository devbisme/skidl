# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import ERC, POWER, TEMPLATE, Bus, Net, Part, generate_netlist


def test_intfc_brd():
    # Create a simple interface board for a microcontroller.
    # It's intended to show how to create a schematic using SKiDL.

    return # TODO: Create a similar example using KiCad default libraries.

    # Libraries.
    xess_lib = r"xess.lib"
    pic32_lib = r"pic32.lib"
    pickit3_lib = r"pickit3.lib"

    # Global nets.
    gnd = Net("GND")
    gnd.drive = POWER
    vusb = Net("VUSB")
    vusb.drive = POWER
    vdd = Net("+3.3V")

    # Some common parts used as templates.
    cap = Part(
        "Device", "C", footprint="Capacitor_SMD:C_0603_1608Metric", dest=TEMPLATE
    )
    res = Part("Device", "R", footprint="Resistor_SMD:R_0603_1608Metric", dest=TEMPLATE)
    # Regulate +5V VUSB down to +3.3V for VDD.
    vreg = Part(xess_lib, "TPS793XX", footprint="Package_TO_SOT_SMD:SOT-23-5")
    noise_cap = cap(value="0.01uf")
    vreg["IN, EN"] += vusb
    vreg["GND"] += gnd
    vreg["OUT"] += vdd
    vreg["NR"] += noise_cap[1]
    noise_cap[2] += gnd

    # Microcontroller.
    pic32 = Part(
        pic32_lib,
        "PIC32MX2\*0F\*\*\*B-QFN28",
        footprint="Package_DFN_QFN:QFN-28-1EP_6x6mm_P0.65mm_EP4.25x4.25mm",
    )
    pic32.split_pin_names("/")
    pic32["VSS"] += gnd
    pic32["VDD"] += vdd  # Main CPU power.
    pic32["VUSB3V3"] += vdd  # Power to USB transceiver.
    pic32["VBUS"] += vusb  # Monitor power pin of USB connector.
    pic32["PAD"] += gnd  # Power pad on bottom attached to ground.

    # Bypass capacitors for microcontroller.
    bypass = cap(3, value="0.1uf")
    bypass[0][1, 2] += vdd, gnd
    bypass[1][1, 2] += vdd, gnd
    bypass[2][1, 2] += pic32["VCAP"], gnd

    # Microcontroller MCLR circuitry:
    #   Pull-up resistor to VDD.
    #   Filter capacitor to delay exit of reset or eliminate glitches.
    #   Series resistor to isolate capacitor from device programmer.
    r_pullup = res(value="10K")
    r_series = res(value="1K")
    filter_cap = cap(value="0.1uf")
    r_series[1, 2] += r_pullup[1], pic32["~MCLR"]
    r_pullup[2] += vdd
    filter_cap[1, 2] += r_series[1], gnd

    # USB connector.
    usb_conn = Part(xess_lib, "USB-MicroB", footprint="XESS:USB-microB-1")
    usb_conn["D+, D-, VBUS, GND, NC"] += pic32["D+, D-"], vusb, gnd, NC
    # Noise filtering/isolation on the USB connector shield.
    shld_cap = cap(value="4.7nf")
    shld_res = res(value="1M")
    shld_cap[1] += usb_conn["shield"]
    shld_res[1] += usb_conn["shield"]
    gnd += shld_cap[2], shld_res[2]

    # LED with current-limiting resistor driven by microcontroller pin.
    led = Part("Device", "LED", footprint="LED_SMD:LED_0603_1608Metric")
    led_curr_limit = res(value="1K")
    led_curr_limit[1, 2] += pic32["RB4"], led["A"]
    led["K"] += gnd

    # Crystal and trim capacitors.
    xtal = Part(xess_lib, "XTAL4", footprint="XESS:32x25-4")
    xtal[2, 4] += gnd
    pic32["OSC1, OSC2"] += xtal[3, 1]
    trim_cap = cap(2, value="10pf")
    trim_cap[0][1, 2] += xtal[1], gnd
    trim_cap[1][1, 2] += xtal[3], gnd

    # Port for attachment of device programmer.
    prg_hdr = Part(
        pickit3_lib,
        "pickit3_hdr",
        footprint="Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Horizontal",
    )
    prg_hdr.ref = "PRG"
    prg_hdr["~MCLR"] += pic32["~MCLR"]
    prg_hdr["VDD"] += vdd
    prg_hdr["GND"] += gnd
    prg_hdr["PGC"] += pic32["PGEC1"]
    prg_hdr["PGD"] += pic32["PGED1"]

    # Port for attachment of FPGA programming pins.
    port = Part(
        "Conn",
        "CONN_01x06",
        footprint="Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Horizontal",
    )
    port.ref = "JTAG"
    port[1, 2] += vusb, gnd
    port[3] += pic32["SCK1"]  # SCK1 output.
    port[5] += pic32["RB5"]  # PPS: SDI1 input.
    port[4] += pic32["RB15"]  # PPS: SS1 output.
    port[6] += pic32["RA4"]  # PPS: SDO1 output.

    ERC()
    generate_netlist()
