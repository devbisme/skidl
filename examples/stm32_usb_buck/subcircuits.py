from skidl import *


# LED indicator circuit
# c = central coordinates for the subcircuit
@SubCircuit
def stm32f405r(vdd, gnd, _5v):
    # MCU
    u = Part("MCU_ST_STM32F4", 'STM32F405RGTx', footprint='LQFP-64_10x10mm_P0.5mm')
    vdd += u.p1, u.p19, u.p32, u.p48, u.p64, u.p13

    # VACP's
    vcap1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric')
    vc1 = Net('vcap1')
    vc1 += u.p31, vcap1.p1

    vcap2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric')
    vc2 = Net('vcap2')
    vc2 += u.p47, vcap2.p1

    led_indicator(u.p8,gnd, 'blue', '5.6k')
    usb(_5v, gnd, u.p43, u.p44, False)
    
    gnd += vcap1.p2, vcap2.p2


# Micro-B USB connector with protection and optional pull-up impedance matching resistors
# TODO: Get the impedance match resistor logic to work
def usb(_5v, gnd, dp, dm, imp_match):
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
        rp = Part("Device", 'R', footprint='R_0603_1608Metric', value='1.5k')
        rn = Part("Device", 'R', footprint='R_0603_1608Metric', value='1.5k')
        rp.p1 += usb_connector.p2
        rp.p2 += _5v
        rn.p1 += usb_connector.p3
        rn.p2 += _5v


############################################################################

# LED indicator circuit
def led_indicator(inp, outp, color, resistance):
    # create parts
    d = Part("Device", 'D', footprint='D_0603_1608Metric')
    d.fields['color'] = color
    r = Part("Device", 'R', footprint='R_0603_1608Metric', value=resistance)
    # r.fields['subcircuit']="stm32f405r"
    # connect parts and nets
    inp & r & d & outp

    

@SubCircuit
def board_enable(vcc, gnd_):
    bd_sel_ls = Net('GND')
    n1 = Net('icp2_r2p1')

    # TODO: actual IC is SN74LVC1G86DCKR
    xor_ic = Part('74xGxx', '74AUC1G66', footprint='SOT-353_SC-70-5')
    
    r1 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    r2 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    c1 = Part("Device", 'C', footprint='C_0603_1608Metric', value='0.1uF')

    d = Part("Device", 'D', footprint='D_0603_1608Metric')
    d.fields['color'] = 'green'
    
    r_d = Part("Device", 'R', footprint='R_0603_1608Metric', value="5.6k")
    
    xor_ic.p4 += d.p2 
    r_d.p1 += vcc
    r_d.p2 += d.p1
     

    c1.fields['voltage']='100v'
    c1.fields['temp_coeff']='X7R'

    bd_sel_ls += xor_ic.p1, r1.p1
    n1 += xor_ic.p2, r2.p1
    xor_ic.p3 += gnd_
    # xor_ic.p4 += enabled
    xor_ic.p5 += vcc
    r1.p2 += gnd_
    r2.p2 += vcc
    