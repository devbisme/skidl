from skidl import *
import power_nets as pn
import utility_circuits as uc


# Boot switch circuit
@SubCircuit
def boot_sw(vdd, gnd):
    # Create parts
    sw = Part('Switch', 'SW_SPDT', footprint='SW_SPDT_CK-JS102011SAQN')
    r1 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    r1.p2.label = 'BOOT0'
    
    # Connect parts
    sw.p1 += vdd
    sw.p2 += r1.p1
    sw.p3 += gnd
    
# Debug header circuit
@SubCircuit
def debug_header(reset, swdclk, swdio, swo, vref, gnd):
    t = Part("Connector", "Conn_ARM_JTAG_SWD_10", footprint = "PinSocket_2x05_P2.54mm_Vertical_SMD")
    t.p1 += vref
    t.p2 += swdio
    t.p3 += gnd
    t.p4 += swdclk
    # t.p5 += 
    t.p6 += swo
    # t.p7 +=
    # t.p8 += 
    t.p9 += gnd
    t.p10 += reset

# 4-pin header
@SubCircuit
def header_4pin(in1, in2, in3, in4):
    h = Part("Connector_Generic", "Conn_01x04", footprint = "PinHeader_1x04_P2.54mm_Vertical")
    h.p1 += in1
    h.p2 += in2
    h.p3 += in3
    h.p4 += in4

# PCB mounting holes
@SubCircuit
def mounting_holes(gnd):
    h1 = Part("Mechanical", "MountingHole_Pad", footprint = "MountingHole_5mm")
    h2 = Part("Mechanical", "MountingHole_Pad", footprint = "MountingHole_5mm")
    h3 = Part("Mechanical", "MountingHole_Pad", footprint = "MountingHole_5mm")
    h4 = Part("Mechanical", "MountingHole_Pad", footprint = "MountingHole_5mm")

    gnd += h1.p1, h2.p1, h3.p1, h4.p1

# Oscillator circuit
@SubCircuit
def oscillator(vdd, gnd, osc_in, osc_out):
    # Create parts
    osc = Part('Device', 'Crystal_GND24_Small', footprint = 'Oscillator_SMD_Fordahl_DFAS2-4Pin_7.3x5.1mm')
    c1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='12pF')
    c2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='12pF')
    r1 = Part("Device", 'R', footprint='R_0603_1608Metric', value='47R')

    # Connect parts
    osc.p1 += osc_in, c1.p1
    osc.p3 += c2.p1
    r1.p1 += osc_out
    r1.p2 +=c2.p1
    gnd += osc.p2, osc.p4, c1.p2, c2.p2

# 2-pin screw terminal
@SubCircuit
def screw_term_2(in1, in2):
    t = Part("Connector", "Screw_Terminal_01x02", footprint = "TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal")
    t.p1 += in1
    t.p2 += in2

# Micro-B USB connector with protection and optional pull-up impedance matching resistors
@SubCircuit
def usb(v_5v, gnd, dp, dm, imp_match):

    # Create parts
    usb_protection = Part("Power_Protection", 'USBLC6-4SC6', footprint='SOT-23-6')
    usb_protection.p1.label = 'USB_P'
    usb_protection.p3.label = 'C_USB_P' # connector USB+
    usb_protection.p4.label = 'USB_M'
    usb_protection.p6.label = 'C_USB_M' # connector USB-

    usb_connector = Part("Connector", 'USB_B_Mini', footprint='USB_Micro-B_Molex-105017-0001')
    # Check if we should add impedance matching pull-ups
    if imp_match:
        rp = Part("Device", 'R', footprint='R_0603_1608Metric', value='1.5k')
        rn = Part("Device", 'R', footprint='R_0603_1608Metric', value='1.5k')
        rp.p1 += usb_connector.p2
        rn.p1 += usb_connector.p3
        v_5v += rp.p2, rn.p2

    # Connect pins and nets
    usb_protection.p1 += dp
    usb_protection.p3 += usb_connector.p3
    usb_protection.p4 += dm        
    usb_protection.p6 += usb_connector.p2

    v_5v += usb_connector.p1, usb_protection.p5
    gnd += usb_connector.p5, usb_connector.p6, usb_protection.p2
  
