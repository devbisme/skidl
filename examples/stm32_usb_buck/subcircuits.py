from skidl import *


# LED indicator circuit
# c = central coordinates for the subcircuit
@SubCircuit
def stm32f405r(c,vdd, gnd):
    x = c[0]
    y = c[1]
    # MCU
    u = Part("MCU_ST_STM32F4", 'STM32F405RGTx', footprint='LQFP-64_10x10mm_P0.5mm')
    u.fields['loc']=[x,y]
    

    # VACP's
    
    
    
    vcap1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric')
    vcap1.fields['loc']=[x-1000, y-1100]
    vc1 = Net('vcap1')
    vc1 += u.p31
    vcap2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric')
    vcap2.fields['loc']=[x-900,y-1000]
    vc2 = Net('vcap2')
    vc2 += u.p47


############################################################################

# LED indicator circuit
@SubCircuit
def led_indicator(c, inp, outp, color, resistance):
    x = c[0]
    y = c[1]

    # create parts
    d = Part("Device", 'D', footprint='D_0603_1608Metric')
    d.fields['color'] = color
    d.fields['loc']=[x, y]
    # d.fields['subcircuit']="stm32f405r"
    r = Part("Device", 'R', footprint='R_0603_1608Metric', value=resistance)
    r.fields['loc']=[x, y+250]
    # r.fields['subcircuit']="stm32f405r"
    # connect parts and nets
    inp & r & d & outp

    

@SubCircuit
def board_enable(c,bd_sel_ls, enabled, vcc, gnd_):
    x = c[0]
    y = c[1]
    # TODO: actual IC is SN74LVC1G86DCKR
    xor_ic = Part('74xGxx', '74AUC1G66', footprint='SOT-353_SC-70-5')
    
    r1 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    r2 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    c1 = Part("Device", 'C', footprint='C_0603_1608Metric', value='0.1uF')
    c1.fields['voltage']='100v'
    c1.fields['temp_coeff']='X7R'

    # Place parts
    xor_ic.fields['loc']=[x, y]
    r1.fields['loc']=[x+300, y+300]
    r2.fields['loc']=[x-300, y-300]
    c1.fields['loc']=[x+500, y+500]

    xor_ic.p1 += bd_sel_ls
    xor_ic.p2 += r2.p1
    xor_ic.p3 += gnd_
    xor_ic.p4 += enabled
    xor_ic.p5 += vcc
    r1.p1 += bd_sel_ls
    r1.p2 += gnd_
    r2.p2 += gnd_
    
    # led_indicator(c*2, vcc, enabled, 'green', '5.6k')


@SubCircuit
def ADC_16bit_spi(fl_n, mosi_iso, miso_iso, sclk_iso, cs_iso, rst, _5v_iso, _3v3_iso, iso_gnd):
    # create parts
    ic = Part('Analog_ADC','ADS1220xPW', footprint='SSOP-16_3.9x4.9mm_P0.635mm')

    r1 = Part("Device", 'R', footprint='R_0603_1608Metric', value='200')
    r1.fields['power']='0.25w'
    r1.fields['tolerance']='0.1'
    r2 = Part("Device", 'R', footprint='R_0603_1608Metric', value='47')
    r3 = Part("Device", 'R', footprint='R_0603_1608Metric', value='22')
    r3.fields['tolerance']='1'
    r4 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    r5 = Part("Device", 'R', footprint='R_0603_1608Metric', value='20.5k')

    c1 = Part("Device", 'C', footprint='C_0603_1608Metric', value='10uF')
    c1.fields['voltage']='25v'
    c1.fields['temp_coeff']='X5R'
    c2 = Part("Device", 'C', footprint='C_0603_1608Metric', value='22uF')
    c2.fields['voltage']='16v'
    c2.fields['temp_coeff']='X5R'
    c3 = Part("Device", 'C', footprint='C_0603_1608Metric', value='1uF')
    c3.fields['voltage']='16v'
    c3.fields['temp_coeff']='X7R'
    c4 = Part("Device", 'C', footprint='C_0603_1608Metric', value='1uF')
    c4.fields['voltage']='50v'
    c4.fields['temp_coeff']='X5R'
    c5 = Part("Device", 'C', footprint='C_0603_1608Metric', value='1uF')
    c5.fields['voltage']='50v'
    c5.fields['temp_coeff']='X5R'

    # Place components
    ic.loc = (0,0)
    r1.loc = (0,0)
    r2.loc = (0,0)
    r3.loc = (0,0)
    r4.loc = (0,0)
    r5.loc = (0,0)
    c1.loc = (0,0)
    c2.loc = (0,0)
    c3.loc = (0,0)
    c4.loc = (0,0)
    c5.loc = (0,0)

    # Connect parts
    ic.p1 += iso_gnd
    ic.p3 += iso_gnd
    ic.p5 += iso_gnd
    ic.p8 += iso_gnd
    ic.p16 += _3v3_iso
    ic.p2 += _5v_iso
    
    ic.p4 += r2.p2
    ic.p6 += r3.p2
    ic.p7 += fl_n
    ic.p9 += rst

    ic.p10 += mosi_iso
    ic.p11 += cs_iso
    ic.p12 += sclk_iso
    ic.p13 += miso_iso
    # ic.p14
    # ic.p15
    

    r1.p1 += fl_n
    r1.p2 += iso_gnd
    r2.p1 += c1.p1
    c1.p2 += iso_gnd
    c2.p1 += r3.p1
    c2.p2 += iso_gnd
    c3.p1 += r3.p1
    c3.p2 += iso_gnd


    c4.p1 += _5v_iso
    c4.p2 += iso_gnd
    c5.p1 += _3v3_iso
    c5.p2 += iso_gnd

    r4.p1 += ic.p9
    r4.p2 += _3v3_iso

    r5.p1 += ic.p13
    r5.p2 += iso_gnd



@SubCircuit
def digital_isolator(mosi_iso, miso_iso, sclk_iso, cs_iso, mosi_l, miso_l, sclk_l, cs_l, _5v,_3v3_iso, iso_gnd, gnd_l):
    # Make parts
    ic = Part('Isolator', 'ISO7763DW', footprint='SOIC-16_W7.5mm')
    c1 = Part("Device", 'C', footprint='C_0603_1608Metric', value='100nF')
    c1.fields['voltage']='50v'
    c1.fields['temp_coeff']='X7R'
    c2 = c1.copy()

    # Place components
    ic.loc = (0,0)
    c1.loc = (0,0)
    c2.loc = (0,0)


    ic.p1 += _5v
    ic.p7 += _5v
    ic.p16 += _3v3_iso
    ic.p10 += _3v3_iso
    ic.p9 += iso_gnd
    ic.p15 += iso_gnd
    ic.p2 += gnd_l
    ic.p8 += gnd_l

    ic.p5 += mosi_l
    ic.p6 += miso_l
    ic.p3 += sclk_l
    ic.p4 += cs_l
    
    ic.p12 += mosi_l
    ic.p11 += miso_iso
    ic.p14 += sclk_iso
    ic.p13 += cs_iso
    


    c1.p1 += _3v3_iso
    c1.p2 += iso_gnd
    c2.p1 += _5v
    c2.p2 += gnd_l
    
@SubCircuit
def address_decode(adr_in, adr_out, enable, cs_ls, _5v, _3v3, gnd_l):
    ic = Part('74xx', '74HC4051', footprint='TSSOP-16_4.4x5mm_P0.65mm')

    r1 = Part('Device', 'R', footprint='R_0603_1608Metric', value='10k') # pull-up on chip-select line
    c1 = Part('Device', 'C', footprint='C_0603_1608Metric', value='0.1uF')
    c1.fields['voltage'] = '100v'
    c1.fields['temp_coeff'] = 'X7R'

    # Place components
    ic.loc = (0,0)
    r1.loc = (0,0)
    c1.loc = (0,0)

    c1.p1 += _5v
    c1.p2 += gnd_l
    r1.p1 += _3v3
    r1.p2 += cs_ls

    ic.p1 += adr_in[0]
    ic.p2 += adr_in[1]
    ic.p3 += adr_in[2]
    ic.p4 += enable
    ic.p5 += cs_ls
    ic.p6 += _5v
    # ic.p7 += adr_out[7]
    ic.p8 += gnd_l
    # ic.p9 += adr_out[6]
    # ic.p10 += adr_out[5]
    # ic.p11 += adr_out[4]
    ic.p12 += adr_out[3]
    ic.p13 += adr_out[2]
    ic.p14 += adr_out[1]
    ic.p15 += adr_out[0]
    ic.p16 += _5v




@SubCircuit
def spi_driver(mosi_ls, sclk_ls, mosi_l, sclk_l, enable, _5v, _3v3, gnd_):
    ic = Part('74xx', '74HCT541', footprint='TSSOP-20_4.4x5mm_P0.5mm')
    r1, r2, r3, r4 = 4 * Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    c1 = Part("Device", 'C', footprint='C_0603_1608Metric', value='0.1uF')
    c1.fields['voltage']='100v'
    c1.fields['temp_coeff']='X7R'

    # Place components
    ic.loc = (0,0)
    r1.loc = (0,0)
    r2.loc = (0,0)
    r3.loc = (0,0)
    r4.loc = (0,0)
    c1.loc = (0,0)


    c1.p1 += _5v
    c1.p2 += gnd_

    r1.p1 += _3v3
    r1.p2 += sclk_ls
    r2.p1 += _3v3
    r2.p2 += mosi_ls
    r3.p1 += _3v3
    r3.p2 += sclk_l
    r4.p1 += _3v3
    r4.p2 += mosi_l

    ic.p1 += enable
    ic.p2 += mosi_ls
    ic.p3 += sclk_ls
    ic[4:10] += gnd_
    # ic[11:16]
    ic.p17 += sclk_l
    ic.p18 += mosi_l
    ic.p19 += gnd_
    ic.p20 += _5v



@SubCircuit
def bus_driver(miso_ls, miso_l, enable, _3v3, gnd_l):
    ic = Part('74xGxx', '74LVC1G125', footprint='SOT-353')
    r1 = Part("Device", 'R', footprint='R_0603_1608Metric', value='22')
    r2 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    c1 = Part("Device", 'C', footprint='C_0603_1608Metric', value='0.1uF')
    c1.fields['voltage']='100v'
    c1.fields['temp_coeff']='X7R'


    # Place components
    ic.loc = (0,0)
    r1.loc = (0,0)
    r2.loc = (0,0)
    c1.loc = (0,0)

    c1.p1 += _3v3
    c1.p2 += gnd_l

    r1.p1 += miso_ls
    r1.p2 += ic.p4

    r2.p1 += _3v3
    r2.p2 += miso_ls

    ic.p1 += enable
    ic.p2 += miso_l
    ic.p3 += gnd_l
    ic.p4 += r1.p2
    ic.p5 += _3v3


@SubCircuit
def shift_register(miso_l_bd, miso, adr, enable, _5v, gnd_l):
    ic = Part('74xx', '74LS151', footprint='SOIC-16_W3.90mm')
    c1 = Part("Device", 'C', footprint='C_0603_1608Metric', value='0.1uF')
    c1.fields['voltage']='100v'
    c1.fields['temp_coeff']='X7R'

    c1.p1 += _5v
    c1.p2 += gnd_l

    ic.p1 += miso[3]
    ic.p2 += miso[2]
    ic.p3 += miso[1]
    ic.p4 += miso[0]

    ic.p5 += miso_l_bd
    # ic.p6 +=
    ic.p7 += enable
    ic.p8 += gnd_l
    ic.p9 += adr[2]
    ic.p10 += adr[1]
    ic.p11 += adr[0]
    ic[12:15] += gnd_l
    ic.p16 += _5v


@SubCircuit
def ribbon_cable(mosi_ls, miso_ls, sclk_ls, cs_ls, adr, bd_sel_ls, gnd_l):
    rib = Part('Connector_Generic', 'Conn_01x26', footprint='PinHeader_2x26_P2.54mm_Vertical_SMD')
    r1, r2, r3 = 3 * Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')

    # Place components
    rib.loc = (0,0)
    r1.loc = (0,0)
    r2.loc = (0,0)
    r3.loc = (0,0)


    r1.p1 += adr[0]
    r1.p2 += gnd_l
    r2.p1 += adr[1]
    r2.p2 += gnd_l
    r3.p1 += adr[2]
    r3.p2 += gnd_l


    rib.p1 += gnd_l
    rib.p3 += gnd_l
    rib.p5 += gnd_l
    rib.p7 += gnd_l
    rib.p9 += gnd_l
    rib.p11 += gnd_l
    rib.p13 += gnd_l
    rib.p15 += gnd_l
    rib[17:26] += gnd_l

    rib.p2 += mosi_ls
    rib.p4 += miso_ls
    rib.p6 += sclk_ls
    rib.p8 += cs_ls
    rib.p10 += adr[0]
    rib.p12 += adr[1]
    rib.p14 += adr[2]
    rib.p16 += bd_sel_ls

