from skidl import *



r0603 = Part("Device", 'R', footprint='R_0603_1608Metric', value='1.5k')
c0603 = Part("Device", 'C_Small', footprint='C_0603_1608Metric')
d0603 = Part("Device", 'D', footprint='D_0603_1608Metric')
# LED indicator circuit
# c = central coordinates for the subcircuit
@package
def stm32f405r(vdd, gnd, v_5v):

    l_vdd = Net('+3V3', stub=True, netclass='Power')
    vdd += l_vdd
    l_gnd = Net('GND', stub=True, netclass='Power')
    gnd += l_gnd
    l_5v = Net('+5V',stub=True, netclass='Power')
    v_5v += l_5v
    # MCU
    u = Part("MCU_ST_STM32F4", 'STM32F405RGTx', footprint='LQFP-64_10x10mm_P0.5mm')

    

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
    u.p58.label = 'I2C1_SCL'
    u.p59.label = 'I2C1_SDA'
    u.p60.label = 'BOOT0'

    bcap = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='4.7uF')
    fcap1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='100nF')
    fcap2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='100nF')
    fcap3 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='100nF')
    fcap4 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='100nF')
    fcap5 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='100nF')

    vcap1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='2.2uF')
    vcap1.p2 += u.p31

    vcap2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='2.2uF')
    vcap2.p2 += u.p47
    usb(l_5v, l_gnd, u.p43, u.p44, True)
    boot_sw(l_vdd, l_gnd)
    led(u.p8, l_gnd, 'blue', '5.6k')
    anlg_flt(l_vdd, l_gnd, u.p13)
    oscillator(l_vdd, l_gnd, u.p5, u.p6)

    l_vdd += u.p1, u.p19, u.p32, u.p48, u.p64, bcap.p1, fcap1.p1, fcap2.p1, fcap3.p1, fcap4.p1, fcap5.p1
    l_gnd += vcap1.p1, vcap2.p1, u.p12, u.p18, u.p63, bcap.p2, fcap1.p2, fcap2.p2, fcap3.p2, fcap4.p2, fcap5.p2


# analog supply filter circuit
@SubCircuit
def anlg_flt(vdd, gnd, vdda):
    c1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='1uF')
    c2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='10nF')
    l1 = Part("Device", 'L_Small', footprint='L_0603_1608Metric', value='29nH')
    l_vdd = Net('+3V3', stub=True, netclass='Power')
    vdd += l_vdd
    l_gnd = Net('GND', stub=True, netclass='Power')
    gnd += l_gnd
    l_vdda = Net('+3.3VA', stub=True, netclass='Power')
    vdda += l_vdda

    l_vdda += c1.p1, c2.p1, l1.p2
    l_vdd += l1.p1
    l_gnd += c1.p2, c2.p2


@SubCircuit
def oscillator(vdd, gnd, osc_in, osc_out):

    l_vdd = Net('+3V3', stub=True, netclass='Power')
    vdd += l_vdd
    l_gnd = Net('GND', stub=True, netclass='Power')
    gnd += l_gnd


    print("oscillator")
    osc = Part('Device', 'Crystal_GND24_Small', footprint = 'Oscillator_SMD_Fordahl_DFAS2-4Pin_7.3x5.1mm')
    c1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='12pF')
    c2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='12pF')
    r1 = Part("Device", 'R', footprint='R_0603_1608Metric', value='47R')

    osc.p1 += osc_in, c1.p1
    l_gnd += osc.p2, osc.p4, c1.p2, c2.p2
    osc.p3 += c2.p1

    r1.p1 += osc_out
    r1.p2 +=c2.p1


@SubCircuit
def boot_sw(vdd, gnd):
    l_vdd = Net('+3V3', stub=True, netclass='Power')
    vdd += l_vdd
    l_gnd = Net('GND', stub=True, netclass='Power')
    gnd += l_gnd
    sw = Part('Switch', 'SW_SPDT', footprint='SW_SPDT_CK-JS102011SAQN')
    r1 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    sw.p1 += l_vdd
    sw.p2 += r1.p1
    sw.p3 += l_gnd
    r1.p2.label = 'BOOT0'

    
# Micro-B USB connector with protection and optional pull-up impedance matching resistors
# TODO: Get the impedance match resistor logic to work
@SubCircuit
def usb(v_5v, gnd, dp, dm, imp_match):
    l_gnd = Net('GND', stub=True, netclass='Power')
    gnd += l_gnd
    l_5v = Net('+5V',stub=True, netclass='Power')
    v_5v += l_5v

    usb_protection = Part("Power_Protection", 'USBLC6-4SC6', footprint='SOT-23-6')
    usb_protection.p1 += dp
    usb_protection.p1.label = 'USB_P'
    usb_protection.p2 += l_gnd
    usb_protection.p3.label = 'CONN_USB_P'
    # usb_protection.p3 += 
    usb_protection.p4 += dm
    usb_protection.p4.label = 'USB_M'
    usb_protection.p5 += l_5v
    usb_protection.p6.label = 'CONN_USB_M'
    # usb_protection.p6 += 


    usb_connector = Part("Connector", 'USB_B_Mini', footprint='USB_Micro-B_Molex-105017-0001')
    usb_connector.p1 += l_5v
    usb_connector.p2 += usb_protection.p6
    # usb_connector.p2.label = 'CONN_USB_P'
    usb_connector.p3 += usb_protection.p3
    # usb_connector.p3.label = 'CONN_USB_M'
    # usb_connector.p4 += usb_protection.p6
    usb_connector.p5 += l_gnd
    usb_connector.p6 += l_gnd

    if imp_match:
        rp = Part("Device", 'R', footprint='R_0603_1608Metric', value='1.5k')
        rn = Part("Device", 'R', footprint='R_0603_1608Metric', value='1.5k')
        rp.p1 += usb_connector.p2
        rp.p2 += l_5v
        rn.p1 += usb_connector.p3
        rn.p2 += l_5v
    
# LED indicator circuit
@SubCircuit
def led(inp, outp, color, resistance):
    d = d0603()
    # d.color = color
    r = Part("Device", 'R', footprint='R_0603_1608Metric', value=resistance)
    inp & r & d & outp