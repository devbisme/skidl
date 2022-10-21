from skidl import *
import power_nets as pn
import utility_circuits as uc
import connection_circuits as c

# STM32 circuit, includes all subcircuitry needed
@SubCircuit
def stm32f405r():
    u = Part("MCU_ST_STM32F4", 'STM32F405RGTx', footprint='LQFP-64_10x10mm_P0.5mm')
    # Label signal pins
    # u.p5.label = 'OSC_IN'
    # u.p6.label = 'OSC_OUT'
    # u.p7.label = 'NRST'
    # u.p8.label = 'HB' #heartbeat
    # u.p16.label = 'USART2_TX'
    # u.p17.label = 'USART2_TX'
    # u.p31.label = 'vcap1'
    # u.p47.label = 'vcap2'
    # u.p45.label = 'USB_P'
    # u.p44.label = 'USB_M'
    # u.p46.label = 'SWDIO'
    # u.p49.label = 'SWCLK'
    # u.p55.label = 'SWO'
    # u.p58.label = 'I2C1_SCL'
    # u.p59.label = 'I2C1_SDA'
    # u.p60.label = 'BOOT0'
    u.p5 += Net('OSC_IN', stub=True)
    u.p6 += Net('OSC_OUT', stub=True)
    u.p7 += Net('NRST', stub=True)
    u.p8 += Net('HB', stub=True)
    u.p16 += Net('USART2_TX', stub=True)
    u.p17 += Net('USART2_TX', stub=True)
    u.p31 += Net('vcap1', stub=True)
    u.p47 += Net('vcap2', stub=True)
    u.p45 += Net('USB_P', stub=True)
    u.p44 += Net('USB_M', stub=True)
    u.p46 += Net('SWDIO', stub=True)
    u.p49 += Net('SWCLK', stub=True)
    u.p55 += Net('SWO', stub=True)
    u.p58 += Net('I2C1_SCL', stub=True)
    u.p59 += Net('I2C1_SDA', stub=True)
    u.p60 += Net('BOOT0', stub=True)

    # Random connection to test routing points.
    u.p11 += u.p34

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
    usb(pn.v_5v, pn.gnd, u.p43, u.p44, imp_match = True)
    boot_sw(pn.v_3v3, pn.gnd, u.p60)
    uc.led(u.p8, pn.gnd, 'blue', '5.6k')
    oscillator(pn.v_3v3, pn.gnd, u.p5, u.p6)
    c.screw_term_2(pn.v_12v, pn.gnd)
    c.debug_header(u.p7, u.p49, u.p46, u.p55, pn.v_3v3, pn.gnd)
    c.header_4pin(pn.v_3v3, pu_scl.p2, pu_sda.p2, pn.gnd) # i2c header
    c.header_4pin(pn.v_3v3, u.p16, u.p17, pn.gnd) # uart header
    c.mounting_holes(pn.gnd)

    # Connect pins
    vcap2.p2 += u.p47
    vcap1.p2 += u.p31
    pn.v_3v3 += u.p1, u.p19, u.p32, u.p48, u.p64, bcap.p1, fcap1.p1, fcap2.p1, fcap3.p1, fcap4.p1, fcap5.p1, pu_sda.p1, pu_scl.p1
    pn.gnd += vcap1.p1, vcap2.p1, u.p12, u.p18, u.p63, bcap.p2, fcap1.p2, fcap2.p2, fcap3.p2, fcap4.p2, fcap5.p2



# Boot switch circuit
@SubCircuit
def boot_sw(vdd, gnd, boot):
    # Create parts
    sw = Part('Switch', 'SW_SPDT', footprint='SW_SPDT_CK-JS102011SAQN')
    r1 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    
    # Connect parts
    sw.p1 += vdd
    sw.p2 += r1.p1
    boot += r1.p2
    sw.p3 += gnd

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

# Micro-B USB connector with protection and optional pull-up impedance matching resistors
@SubCircuit
def usb(v_5v, gnd, dp, dm, imp_match):

    # Create parts
    usb_protection = Part("Power_Protection", 'USBLC6-4SC6', footprint='SOT-23-6')
    usb_protection.p1 += Net.get('USB_P')
    usb_protection.p3 += Net('C_USB_P', stub=True) # connector USB+
    usb_protection.p4 += Net.get('USB_M')
    usb_protection.p6 += Net('C_USB_M', stub=True) # connector USB-

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
  