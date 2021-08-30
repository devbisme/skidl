from skidl import *



r0603 = Part("Device", 'R', footprint='R_0603_1608Metric', value='1.5k')
c0603 = Part("Device", 'C_Small', footprint='C_0603_1608Metric')
d0603 = Part("Device", 'D', footprint='D_0603_1608Metric')
# LED indicator circuit
# c = central coordinates for the subcircuit
@package
def stm32f405r(v_12v, v_5v, vdd, gnd):
    l12v = Net('+12V',stub=True, netclass='Power')
    v_12v += l12v
    l_5v = Net('+5V',stub=True, netclass='Power')
    v_5v += l_5v
    l_vdd = Net('+3V3', stub=True, netclass='Power')
    vdd += l_vdd
    l_gnd = Net('GND', stub=True, netclass='Power')
    gnd += l_gnd

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

    # Subcircuits
    buck(l12v, l_vdd, l_gnd)
    usb(l_5v, l_gnd, u.p43, u.p44, imp_match = True)
    boot_sw(l_vdd, l_gnd)
    led(u.p8, l_gnd, 'blue', '5.6k')
    anlg_flt(l_vdd, l_gnd, u.p13)
    oscillator(l_vdd, l_gnd, u.p5, u.p6)

    # Connect pins
    vcap2.p2 += u.p47
    vcap1.p2 += u.p31
    l_vdd += u.p1, u.p19, u.p32, u.p48, u.p64, bcap.p1, fcap1.p1, fcap2.p1, fcap3.p1, fcap4.p1, fcap5.p1
    l_gnd += vcap1.p1, vcap2.p1, u.p12, u.p18, u.p63, bcap.p2, fcap1.p2, fcap2.p2, fcap3.p2, fcap4.p2, fcap5.p2


# analog supply filter circuit
@SubCircuit
def anlg_flt(vdd, gnd, vdda):
    # Redeclare power nets, TODO: possible bug
    l_vdd = Net('+3V3', stub=True, netclass='Power')
    vdd += l_vdd
    l_gnd = Net('GND', stub=True, netclass='Power')
    gnd += l_gnd
    l_vdda = Net('+3.3VA', stub=True, netclass='Power')
    vdda += l_vdda

    # Create parts
    c1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='1uF')
    c2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='10nF')
    l1 = Part("Device", 'L_Small', footprint='L_0603_1608Metric', value='29nH')

    # Connect pins
    l_vdda += c1.p1, c2.p1, l1.p2
    l_vdd += l1.p1
    l_gnd += c1.p2, c2.p2


@SubCircuit
def vin_protection(vin, vout, gnd):
    # Redeclare power nets, TODO: possible bug
    lvin = Net('+12V', stub=True, netclass='Power')
    vin += lvin
    lgnd = Net('GND', stub=True, netclass='Power')
    gnd += lgnd
    lvout = Net('+3V3', stub=True, netclass='Power')
    vout += lvout

    fuse = Part('Device', 'Polyfuse_Small', footprint='Fuse_Bourns_MF-RG300') # resetable fuse
    pmos = Part('Device', 'Q_PMOS_DGS', footprint='SOT-23') # reverse polarity protection
    fb = Part('Device', 'Ferrite_Bead', footprint='L_Murata_DEM35xxC') # ferrite bead

    lvin += fuse.p1
    fuse.p2 += pmos.p1
    pmos.p2 += lgnd
    pmos.p3 += fb.p1
    fb.p2 += lvout

@SubCircuit
def buck(vin, vout, gnd):
    
    # Redeclare power nets, TODO: possible bug
    lvin = Net('+12V', stub=True, netclass='Power')
    vin += lvin
    lgnd = Net('GND', stub=True, netclass='Power')
    gnd += lgnd
    lvout = Net('+3V3', stub=True, netclass='Power')
    vout += lvout

    vprotected = Net('v12_fused')
    vin_protection(lvin, vprotected, lgnd)


    reg = Part('Regulator_Linear', 'AP1117-15', footprint='SOT-223-3_TabPin2')
    c1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='10uF')
    c2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric', value='10uF')


    vprotected += reg.p3, c1.p1
    lvout += reg.p2, c2.p1
    lgnd += reg.p1, c1.p2, c2.p2

@SubCircuit
def oscillator(vdd, gnd, osc_in, osc_out):
    # Redeclare power nets, TODO: possible bug
    l_vdd = Net('+3V3', stub=True, netclass='Power')
    vdd += l_vdd
    l_gnd = Net('GND', stub=True, netclass='Power')
    gnd += l_gnd

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
    l_gnd += osc.p2, osc.p4, c1.p2, c2.p2


@SubCircuit
def boot_sw(vdd, gnd):
    # Redeclare power nets, TODO: possible bug
    l_vdd = Net('+3V3', stub=True, netclass='Power')
    vdd += l_vdd
    l_gnd = Net('GND', stub=True, netclass='Power')
    gnd += l_gnd
    # Create parts
    sw = Part('Switch', 'SW_SPDT', footprint='SW_SPDT_CK-JS102011SAQN')
    r1 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    r1.p2.label = 'BOOT0'
    
    # Connect parts
    sw.p1 += l_vdd
    sw.p2 += r1.p1
    sw.p3 += l_gnd
    

    
# Micro-B USB connector with protection and optional pull-up impedance matching resistors
@SubCircuit
def usb(v_5v, gnd, dp, dm, imp_match):
    # Redeclare power nets, TODO: possible bug
    l_gnd = Net('GND', stub=True, netclass='Power')
    gnd += l_gnd
    l_5v = Net('+5V',stub=True, netclass='Power')
    v_5v += l_5v

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
        l_5v += rp.p2, rn.p2

    # Connect pins and nets
    usb_protection.p1 += dp
    usb_protection.p3 += usb_connector.p3
    usb_protection.p4 += dm        
    usb_protection.p6 += usb_connector.p2

    l_5v += usb_connector.p1, usb_protection.p5
    l_gnd += usb_connector.p5, usb_connector.p6, usb_protection.p2
    
# LED indicator circuit
@SubCircuit
def led(inp, outp, color, resistance):
    d = Part("Device", 'D', footprint='D_0603_1608Metric', value = color)
    r = Part("Device", 'R', footprint='R_0603_1608Metric', value=resistance)
    inp & r & d & outp