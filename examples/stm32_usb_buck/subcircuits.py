from skidl import *



r0603 = Part("Device", 'R', footprint='R_0603_1608Metric', value='1.5k')
c0603 = Part("Device", 'C_Small', footprint='C_0603_1608Metric')
d0603 = Part("Device", 'D', footprint='D_0603_1608Metric')
# LED indicator circuit
# c = central coordinates for the subcircuit
@package
def stm32f405r(vdd, gnd, v_5v):
    vdd.netclass = "Power"
    gnd.netclass = "Power"
    v_5v.netclass = "Power"
    # MCU
    u = Part("MCU_ST_STM32F4", 'STM32F405RGTx', footprint='LQFP-64_10x10mm_P0.5mm')

    vdd += u.p1, u.p19, u.p32, u.p48, u.p64, u.p13
    u.p31.label = 'vcap1'
    u.p47.label = 'vcap2'
    u.p8.label = 'HB' #heartbeat
    u.p43.label = 'USB_P'
    u.p44.label = 'USB_M'
    u.p60.label = 'BOOT0'

    vcap1 = c0603()
    vcap1.p1 += u.p31

    vcap2 = c0603()
    vcap2.p1 += u.p47

    led_indicator(u.p8, gnd, 'blue', '5.6k')
    usb(v_5v, gnd, u.p43, u.p44, False)
    
    gnd += vcap1.p2, vcap2.p2, u.p12, u.p18, u.p63

    # board_enable(vdd, gnd)

# Micro-B USB connector with protection and optional pull-up impedance matching resistors
# TODO: Get the impedance match resistor logic to work
def usb(_5v, gnd, dp, dm, imp_match):
    _5v.netclass = "Power"
    gnd.netclass = "Power"
    usb_protection = Part("Power_Protection", 'USBLC6-4SC6', footprint='SOT-23-6')
    usb_protection.p1 += dp
    usb_protection.p2 += gnd
    # usb_protection.p3 += 
    usb_protection.p4 += dm
    usb_protection.p5 += _5v
    # usb_protection.p6 += 


    usb_connector = Part("Connector", 'USB_B_Mini', footprint='USB_Micro-B_Molex-105017-0001')
    usb_connector.p1 += _5v
    usb_connector.p2 += usb_protection.p6
    usb_connector.p3 += usb_protection.p3
    # usb_connector.p4 += usb_protection.p6
    usb_connector.p5 += gnd
    usb_connector.p6 += gnd
    
    if imp_match:
        rp = r0603(value='1.5k')
        rn = r0603(value='1.5k')
        rp.p1 += usb_connector.p2
        rp.p2 += _5v
        rn.p1 += usb_connector.p3
        rn.p2 += _5v
    
# LED indicator circuit
def led_indicator(inp, outp, color, resistance):
    inp.netclass = "Power"
    outp.netclass = "Power"
    d = d0603()
    # d.color = color
    r = r0603(value=resistance)
    inp & r & d & outp

@SubCircuit
def board_enable(vcc, gnd_):
    bd_sel_ls = Net('bd_sel_ls')
    n1 = Net('icp2_r2p1')

    # TODO: actual IC is SN74LVC1G86DCKR
    xor_ic = Part('74xGxx', '74AUC1G66', footprint='SOT-353_SC-70-5')
    
    r1 = r0603(value='10k')
    r2 = r0603(value='10k')
    c1 = Part("Device", 'C', footprint='C_0603_1608Metric', value='0.1uF')

    d = Part("Device", 'D', footprint='D_0603_1608Metric')
    d.fields['color'] = 'green'
    
    r_d = Part("Device", 'R', footprint='R_0603_1608Metric', value="5.6k")
    
    xor_ic.p4 += d.p2 
    r_d.p1 += vcc
    r_d.p2 += d.p1
     

    c1.fields['voltage']='100v'
    c1.fields['temp_coeff']='X7R'
    c1.p1 += vcc
    c1.p2 += gnd_

    bd_sel_ls += xor_ic.p1, r1.p1
    # led_indicator(xor_ic.p1,gnd_, 'green', '5.6k')
    n1 += xor_ic.p2, r2.p1
    xor_ic.p3 += gnd_
    # xor_ic.p4 += enabled
    xor_ic.p5 += vcc
    r1.p2 += gnd_
    r2.p2 += vcc
    