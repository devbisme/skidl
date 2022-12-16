from skidl import *

# Connectors, terminal blocks, etc


# @SubCircuit
# def headers(i2c_sda, i2c_scl, uart_tx, uart_rx, vdd, gnd):
    

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



# 2-pin screw terminal
@SubCircuit
def screw_term_2(in1, in2):
    t = Part("Connector", "Screw_Terminal_01x02", footprint = "TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal")
    t.p1 += in1
    t.p2 += in2