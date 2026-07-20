#!/usr/bin/env python3
"""Example: ESP32-S3 audio board with auto_stub and subcircuits.

Demonstrates how to structure a real-world PCB design using SKiDL's
auto_stub feature and @subcircuit grouping for clean schematic output.

Circuit: ESP32-S3 + LiPo charger + I2S amplifier + speaker
- USB-C input with TP4056 battery charging
- AP2112K-3.3 LDO for 3.3V rail
- MAX98357A I2S DAC/amplifier driving a speaker
- Status LED and user button

Key patterns shown:
1. @subcircuit groups related parts → hierarchical sheets
2. Power nets with .drive = POWER → KiCad power symbols
3. auto_stub handles routing complexity automatically
4. Smaller subcircuits (5-15 parts) route better than one big flat circuit
"""

import os, sys

# Ensure KICAD9_SYMBOL_DIR is set to your KiCad 9 symbol library path.
# e.g.: export KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols

from skidl import *

set_default_tool(KICAD9)


# ── Subcircuit: USB-C + TP4056 LiPo Charger ──────────────────────────────


@subcircuit
def usb_charger(vbus, vbat, gnd, usb_dp, usb_dm):
    """USB-C connector with CC resistors and TP4056 battery charger."""

    # USB-C receptacle (full pinout, USB 2.0 data only)
    usb = Part("Connector", "USB_C_Receptacle")
    # Power and ground pins
    for p in ["A1", "A12", "B1", "B12"]:
        usb[p] += gnd
    for p in ["A4", "A9", "B4", "B9"]:
        usb[p] += vbus
    usb["S1"] += gnd  # Shield

    # CC pull-downs for sink/UFP role
    for cc_pin in ["A5", "B5"]:
        cc = Net()
        usb[cc_pin] += cc
        r = Part("Device", "R", value="5.1K")
        r[1] += cc
        r[2] += gnd

    # USB 2.0 data (tie A/B together)
    usb["A6"] += usb_dp
    usb["B6"] += usb_dp
    usb["A7"] += usb_dm
    usb["B7"] += usb_dm

    # Unused high-speed pins
    for p in ["A2", "A3", "A8", "A10", "A11", "B2", "B3", "B8", "B10", "B11"]:
        usb[p] += Net(f"USB_{p}_NC")

    # TP4056 LiPo charger
    # Pins: 1=TEMP 2=PROG 3=GND 4=VCC 5=BAT 6=~STDBY 7=~CHRG 8=CE 9=EPAD
    tp = Part("Battery_Management", "TP4056-42-ESOP8")
    tp[4] += vbus
    tp[3] += gnd
    tp[9] += gnd
    tp[5] += vbat
    tp[8] += vbus  # CE always enabled

    # TEMP: resistor to GND disables temp sensing
    r_temp = Part("Device", "R", value="10K")
    r_temp[1] += tp[1]
    r_temp[2] += gnd

    # PROG: sets charge current (2K = 500mA)
    r_prog = Part("Device", "R", value="2K")
    r_prog[1] += tp[2]
    r_prog[2] += gnd

    # Charge status LEDs (active-low open drain)
    for pin_num in [7, 6]:  # ~CHRG, ~STDBY
        status = Net()
        tp[pin_num] += status
        r = Part("Device", "R", value="1K")
        led = Part("Device", "LED")
        r[1] += vbus
        r[2] += led[1]
        led[2] += status

    # Input decoupling
    c = Part("Device", "C", value="10uF")
    c[1] += vbus
    c[2] += gnd


# ── Subcircuit: 3.3V LDO + Battery Connector ─────────────────────────────


@subcircuit
def power_supply(vbat, vcc, gnd):
    """AP2112K LDO regulator with battery connector and decoupling."""

    bat = Part("Connector", "Conn_01x02_Pin")
    bat[1] += vbat
    bat[2] += gnd

    c_bat = Part("Device", "C", value="10uF")
    c_bat[1] += vbat
    c_bat[2] += gnd

    # AP2112K-3.3: 1=VIN 2=GND 3=EN 5=VOUT
    ldo = Part("Regulator_Linear", "AP2112K-3.3")
    ldo[1] += vbat
    ldo[2] += gnd
    ldo[3] += vbat
    ldo[5] += vcc

    c_in = Part("Device", "C", value="1uF")
    c_in[1] += vbat
    c_in[2] += gnd
    c_out = Part("Device", "C", value="1uF")
    c_out[1] += vcc
    c_out[2] += gnd


# ── Subcircuit: ESP32-S3 MCU ─────────────────────────────────────────────


@subcircuit
def mcu_esp32s3(vcc, gnd, usb_dp, usb_dm, i2s_bclk, i2s_lrclk, i2s_dout, gpio_btn):
    """ESP32-S3-WROOM-1 with boot circuit and decoupling."""

    esp = Part("RF_Module", "ESP32-S3-WROOM-1")
    esp[2] += vcc  # 3V3
    esp[1] += gnd  # GND
    esp[40] += gnd
    esp[41] += gnd

    # EN: pull-up + filter cap for clean reset
    r_en = Part("Device", "R", value="10K")
    r_en[1] += vcc
    r_en[2] += esp[3]
    c_en = Part("Device", "C", value="100nF")
    c_en[1] += esp[3]
    c_en[2] += gnd

    # Native USB
    esp[14] += usb_dp
    esp[13] += usb_dm

    # I2S output (GPIO7=BCLK, GPIO8=LRCLK, GPIO9=DOUT)
    esp[7] += i2s_bclk
    esp[12] += i2s_lrclk
    esp[17] += i2s_dout

    # User button on GPIO0 (doubles as boot select)
    esp[27] += gpio_btn

    # Decoupling: 2x 100nF + 1x 10uF
    for _ in range(2):
        c = Part("Device", "C", value="100nF")
        c[1] += vcc
        c[2] += gnd
    c_bulk = Part("Device", "C", value="10uF")
    c_bulk[1] += vcc
    c_bulk[2] += gnd


# ── Subcircuit: I2S Amplifier + Speaker ───────────────────────────────────


@subcircuit
def audio_output(vbat, vcc, gnd, i2s_bclk, i2s_lrclk, i2s_dout):
    """MAX98357A I2S amp with speaker connector."""

    # Pins: 1=DIN 2=GAIN_SLOT 3=GND 4=~SD_MODE 7-8=VDD
    #       9=OUTP 10=OUTN 11=GND 14=LRCLK 15=GND 16=BCLK 17=PAD
    amp = Part("Audio", "MAX98357A")
    amp[7] += vbat
    amp[8] += vbat  # VDD from battery for headroom
    amp[3] += gnd
    amp[11] += gnd
    amp[15] += gnd
    amp[17] += gnd

    amp[16] += i2s_bclk
    amp[14] += i2s_lrclk
    amp[1] += i2s_dout

    # SD_MODE: pull high to enable
    sd = Net("AMP_SD")
    amp[4] += sd
    r = Part("Device", "R", value="100K")
    r[1] += vcc
    r[2] += sd

    # GAIN: float for 9dB default
    amp[2] += Net("AMP_GAIN_NC")

    # Decoupling
    c1 = Part("Device", "C", value="10uF")
    c1[1] += vbat
    c1[2] += gnd
    c2 = Part("Device", "C", value="100nF")
    c2[1] += vbat
    c2[2] += gnd

    # Speaker connector
    spk = Part("Connector", "Conn_01x02_Pin")
    spk[1] += amp[9]
    spk[2] += amp[10]


# ── Subcircuit: Button + LED ─────────────────────────────────────────────


@subcircuit
def user_interface(vcc, gnd, gpio_btn):
    """Tactile button with pull-up and status LED."""

    sw = Part("Switch", "SW_Push")
    sw[1] += gpio_btn
    sw[2] += gnd
    r = Part("Device", "R", value="10K")
    r[1] += vcc
    r[2] += gpio_btn

    led = Part("LED", "WS2812B")
    led[1] += vcc
    led[3] += gnd
    led[4] += Net("LED_DIN")  # Connect to an ESP32 GPIO as needed
    led[2] += Net("LED_DOUT_NC")

    c = Part("Device", "C", value="100nF")
    c[1] += vcc
    c[2] += gnd


# ═══════════════════════════════════════════════════════════════════════════
# Top level: define nets and instantiate subcircuits
# ═══════════════════════════════════════════════════════════════════════════

# Power rails — .drive = POWER makes them emit KiCad power symbols
vbus = Net("VBUS")
vbat = Net("VBAT")
vcc = Net("VCC")
vcc.drive = POWER
gnd = Net("GND")
gnd.drive = POWER

# Inter-block signals
usb_dp = Net("USB_DP")
usb_dm = Net("USB_DM")
i2s_bclk = Net("I2S_BCLK")
i2s_lrclk = Net("I2S_LRCLK")
i2s_dout = Net("I2S_DOUT")
btn = Net("BTN")

# Build the circuit from subcircuits
usb_charger(vbus, vbat, gnd, usb_dp, usb_dm)
power_supply(vbat, vcc, gnd)
mcu_esp32s3(vcc, gnd, usb_dp, usb_dm, i2s_bclk, i2s_lrclk, i2s_dout, btn)
audio_output(vbat, vcc, gnd, i2s_bclk, i2s_lrclk, i2s_dout)
user_interface(vcc, gnd, btn)

# Generate — auto_stub handles routing complexity, subcircuits become sheets
generate_schematic(
    auto_stub=True,
    auto_stub_fanout=3,
    erc_max_iterations=8,
)
