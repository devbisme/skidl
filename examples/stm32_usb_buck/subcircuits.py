from skidl import *


# LED indicator circuit
# c = central coordinates for the subcircuit
@SubCircuit
def stm32f405r(c,vdd, gnd):
    x = c[0]
    y = c[1]
    # MCU
    u = Part("MCU_ST_STM32F4", 'STM32F405RGTx', footprint='LQFP-64_10x10mm_P0.5mm')
    u.sch_loc=[x,y]
    
    # VACP's
    vcap1 = Part("Device", 'C_Small', footprint='C_0603_1608Metric')
    vcap1.sch_loc=[x, y]
    vc1 = Net('vcap1')
    vc1 += u.p31, vcap1.p1

    vcap2 = Part("Device", 'C_Small', footprint='C_0603_1608Metric')
    vcap2.sch_loc=[x,y]
    vc2 = Net('vcap2')
    vc2 += u.p47, vcap2.p1

    led_indicator([x,y],u.p50,gnd,'green','5.6k')


############################################################################

# LED indicator circuit
@SubCircuit
def led_indicator(c, inp, outp, color, resistance):
    x = c[0]
    y = c[1]

    # create parts
    d = Part("Device", 'D', footprint='D_0603_1608Metric')
    d.fields['color'] = color
    d.sch_loc=[x+1400, y+200]
    r = Part("Device", 'R', footprint='R_0603_1608Metric', value=resistance)
    r.sch_loc=[x, y]
    # r.fields['subcircuit']="stm32f405r"
    # connect parts and nets
    inp & r & d & outp

    

@SubCircuit
def board_enable(c, vcc, gnd_):
    x = c[0]
    y = c[1]

    bd_sel_ls = Net('GND')
    n1 = Net('icp2_r2p1')

    # TODO: actual IC is SN74LVC1G86DCKR
    xor_ic = Part('74xGxx', '74AUC1G66', footprint='SOT-353_SC-70-5')
    
    r1 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    r2 = Part("Device", 'R', footprint='R_0603_1608Metric', value='10k')
    c1 = Part("Device", 'C', footprint='C_0603_1608Metric', value='0.1uF')

    d = Part("Device", 'D', footprint='D_0603_1608Metric')
    d.fields['color'] = 'green'
    
    # d.fields['subcircuit']="stm32f405r"
    r_d = Part("Device", 'R', footprint='R_0603_1608Metric', value="5.6k")
    
    xor_ic.p4 += d.p2 
    r_d.p1 += vcc
    r_d.p2 += d.p1
     

    c1.fields['voltage']='100v'
    c1.fields['temp_coeff']='X7R'

    # Place parts
    xor_ic.sch_loc=[x, y]
    # r_d.sch_loc=[x-600, y+500]
    # d.sch_loc=[x-400, y+650]
    # r1.sch_loc=[x-450, y+150]
    # r2.sch_loc=[x+350, y+150]
    # c1.sch_loc=[x, y-400]
    r_d.sch_loc=[x, y]
    d.sch_loc=[x, y]
    r1.sch_loc=[x, y]
    r2.sch_loc=[x, y]
    c1.sch_loc=[x, y-400]


    bd_sel_ls += xor_ic.p1, r1.p1
    n1 += xor_ic.p2, r2.p1
    xor_ic.p3 += gnd_
    # xor_ic.p4 += enabled
    xor_ic.p5 += vcc
    r1.p2 += gnd_
    r2.p2 += vcc
    
    # led_indicator(c*2, vcc, enabled, 'green', '5.6k')