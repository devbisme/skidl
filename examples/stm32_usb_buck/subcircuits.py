from skidl import *
import power_nets as pn

# Generates STM32 chip with peripherals including:
#   * 
@package
def stm32f405r():
    # MCU
    u = Part("MCU_ST_STM32F4", 'STM32F405RGTx', footprint='LQFP-64_10x10mm_P0.5mm')
    # Label signal pins
    u.p5.label = 'OSC_IN'
    u.p6.label = 'OSC_OUT'
    u.p7.label = 'NRST'
    u.p8.label = 'HB' #heartbeat
    u.p16.label = 'USART2_TX'
    u.p17.label = 'USART2_TX'
    u.p31.label = 'vcap1'
    u.p47.label = 'vcap2'
    u.p45.label = 'USB_P'
    u.p44.label = 'USB_M'
    u.p46.label = 'SWDIO'
    u.p49.label = 'SWCLK'
    u.p55.label = 'SWO'
    u.p58.label = 'I2C1_SCL'
    u.p59.label = 'I2C1_SDA'
    u.p60.label = 'BOOT0'

    # Bulking cap
    bcap = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='4.7uF')
    # Decoupling caps
    fcap1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='100nF')
    fcap2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='100nF')
    fcap3 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='100nF')
    fcap4 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='100nF')
    fcap5 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='100nF')

    #VCaps recommended by ST
    vcap1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='2.2uF')
    vcap2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='2.2uF')

    # I2C pull-ups
    pu_scl = Part("Device", 'R', footprint='R_0603_1608Metric', value="2.2k")
    pu_sda = Part("Device", 'R', footprint='R_0603_1608Metric', value="2.2k")
    pu_scl.p2 += u.p58
    pu_sda.p2 += u.p59

    # Subcircuits
    buck(pn.v_12v, pn.v_3v3, pn.v_5v, pn.gnd)
    usb(pn.v_5v, pn.gnd, u.p43, u.p44, imp_match = True)
    boot_sw(pn.v_3v3, pn.gnd)
    led(u.p8, pn.gnd, 'blue', '5.6k')
    anlg_flt(pn.vdda, pn.gnd, pn.vdda)
    oscillator(pn.v_3v3, pn.gnd, u.p5, u.p6)
    screw_term_2(pn.v_12v, pn.gnd)
    debug_header(u.p7, u.p49, u.p46, u.p55, pn.v_3v3, pn.gnd)
    header_4pin(pn.v_3v3, pu_scl.p2, pu_sda.p2, pn.gnd) # i2c header
    header_4pin(pn.v_3v3, u.p16, u.p17, pn.gnd) # uart header
    mounting_holes(pn.gnd)

    # Connect pins
    vcap2.p2 += u.p47
    vcap1.p2 += u.p31
    pn.v_3v3 += u.p1, u.p19, u.p32, u.p48, u.p64, bcap.p1, fcap1.p1, fcap2.p1, fcap3.p1, fcap4.p1, fcap5.p1, pu_sda.p1, pu_scl.p1
    pn.gnd += vcap1.p1, vcap2.p1, u.p12, u.p18, u.p63, bcap.p2, fcap1.p2, fcap2.p2, fcap3.p2, fcap4.p2, fcap5.p2

# analog supply filter circuit
@SubCircuit
def anlg_flt(vdd, gnd, vdda):
    # Create parts
    c1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='1uF')
    c2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='10nF')
    l1 = Part("Device", 'L_Small', footprint='L_0603_1608Metric', value='29nH')

    # Connect pins
    vdda += c1.p1, c2.p1, l1.p2
    vdd += l1.p1
    gnd += c1.p2, c2.p2


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
    
@SubCircuit
def buck(vin, v_usb, vout, gnd):

    vprotected = Net('v12_fused')
    vin_protection(vin, vprotected, gnd)


    reg = Part('Regulator_Linear', 'AP1117-15', footprint='SOT-223-3_TabPin2')
    reg.p3.label = "v12_fused"
    c1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='10uF')
    c2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='10uF')
    d = Part("Device", "D_Zener_Small", footprint="D_0201_0603Metric")
    d.p1 += v_usb
    

    led(vout, gnd, 'red', '5.6k')

    vprotected += reg.p3, c1.p1, d.p2
    vout += reg.p2, c2.p1
    gnd += reg.p1, c1.p2, c2.p2

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

@SubCircuit
def header_4pin(in1, in2, in3, in4):
    h = Part("Connector_Generic", "Conn_01x04", footprint = "PinHeader_1x04_P2.54mm_Vertical")
    h.p1 += in1
    h.p2 += in2
    h.p3 += in3
    h.p4 += in4

# LED indicator circuit
# @SubCircuit
def led(inp, outp, color, resistance):
    d = Part("Device", 'D', footprint='D_0603_1608Metric', value = color)
    r = Part("Device", 'R', footprint='R_0603_1608Metric', value=resistance)
    inp & r & d & outp

@SubCircuit
def mounting_holes(gnd):
    h1 = Part("Mechanical", "MountingHole_Pad", footprint = "MountingHole_5mm")
    h2 = Part("Mechanical", "MountingHole_Pad", footprint = "MountingHole_5mm")
    h3 = Part("Mechanical", "MountingHole_Pad", footprint = "MountingHole_5mm")
    h4 = Part("Mechanical", "MountingHole_Pad", footprint = "MountingHole_5mm")

    gnd += h1.p1, h2.p1, h3.p1, h4.p1


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
    # Do we need impedance matching pull-ups?
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
  

@SubCircuit
def vin_protection(vin, vout, gnd):
    pmos = Part('Device', 'Q_PMOS_DGS', footprint='SOT-23') # reverse polarity protection
    fuse = Part('Device', 'Polyfuse_Small', footprint='Fuse_Bourns_MF-RG300') # resetable fuse
    fb = Part('Device', 'Ferrite_Bead', footprint='L_Murata_DEM35xxC') # ferrite bead

    vin += fuse.p1
    fuse.p2 += pmos.p1
    pmos.p2 += gnd
    pmos.p3 += fb.p1
    fb.p2 += vout
