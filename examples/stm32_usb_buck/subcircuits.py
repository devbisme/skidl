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
    l_5v = Net('+5v5',stub=True, netclass='Power')
    v_5v += l_5v
    # MCU
    u = Part("MCU_ST_STM32F4", 'STM32F405RGTx', footprint='LQFP-64_10x10mm_P0.5mm')

    l_vdd += u.p1, u.p19, u.p32, u.p48, u.p64, u.p13
    u.p31.label = 'vcap1'
    u.p47.label = 'vcap2'
    u.p8.label = 'HB' #heartbeat
    u.p43.label = 'USB_P'
    u.p44.label = 'USB_M'
    u.p60.label = 'BOOT0'
    u.p35.label = 'BD_SEL'

    vcap1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric')
    vcap1.p1 += u.p31

    vcap2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric')
    vcap2.p1 += u.p47

    led_indicator(u.p8, l_gnd, 'blue', '5.6k')
    usb(l_5v, l_gnd, u.p43, u.p44, True)
    board_enable(vdd, l_gnd, u.p35)
    l_gnd += vcap1.p2, vcap2.p2, u.p12, u.p18, u.p63


# Micro-B USB connector with protection and optional pull-up impedance matching resistors
# TODO: Get the impedance match resistor logic to work
@SubCircuit
def usb(v_5v, gnd, dp, dm, imp_match):
    l_gnd = Net('GND', stub=True, netclass='Power')
    gnd += l_gnd
    l_5v = Net('+5v5',stub=True, netclass='Power')
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
def led_indicator(inp, outp, color, resistance):
    d = d0603()
    # d.color = color
    r = Part("Device", 'R', footprint='R_0603_1608Metric', value=resistance)
    inp & r & d & outp

@SubCircuit
def board_enable(vcc, gnd, brd_sel):

    l_gnd = Net('GND', stub=True, netclass='Power')
    gnd += l_gnd
    l_vcc = Net('+3v3',stub=True, netclass='Power')
    vcc += l_vcc

    # TODO: actual IC is SN74LVC1G86DCKR
    xor_ic = Part('74xGxx', '74AUC1G66', footprint='SOT-353_SC-70-5')
    
    r1 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    r2 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    c1 = Part("Device", 'C', footprint='C_0603_1608Metric', value='0.1uF')


    c1.fields['voltage']='100v'
    c1.fields['temp_coeff']='X7R'
    c1.p1 += l_vcc
    c1.p2 += l_gnd

    brd_sel += xor_ic.p1, r1.p1
    xor_ic.p1.label = 'BD_EN'
    r1.p1.label = 'BD_EN'
    # led_indicator(xor_ic.p1,l_gnd, 'green', '5.6k')
    xor_ic.p2 += r2.p1
    xor_ic.p3 += l_gnd
    # xor_ic.p4 += enabled
    xor_ic.p5 += l_vcc
    r1.p2 += l_gnd
    r2.p2 += l_vcc
    