from skidl import *
import power_nets as pn
import utility_circuits as uc
import subcircuits as sc

# STM32 circuit, includes all subcircuitry needed
@SubCircuit
def stm32f405r():
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
    # buck(pn.v_12v, pn.v_3v3, pn.v_5v, pn.gnd)
    sc.usb(pn.v_5v, pn.gnd, u.p43, u.p44, imp_match = True)
    sc.boot_sw(pn.v_3v3, pn.gnd)
    uc.led(u.p8, pn.gnd, 'blue', '5.6k')
    # anlg_flt(pn.vdda, pn.gnd, pn.vdda)
    sc.oscillator(pn.v_3v3, pn.gnd, u.p5, u.p6)
    sc.screw_term_2(pn.v_12v, pn.gnd)
    sc.debug_header(u.p7, u.p49, u.p46, u.p55, pn.v_3v3, pn.gnd)
    sc.header_4pin(pn.v_3v3, pu_scl.p2, pu_sda.p2, pn.gnd) # i2c header
    sc.header_4pin(pn.v_3v3, u.p16, u.p17, pn.gnd) # uart header
    sc.mounting_holes(pn.gnd)

    # Connect pins
    vcap2.p2 += u.p47
    vcap1.p2 += u.p31
    pn.v_3v3 += u.p1, u.p19, u.p32, u.p48, u.p64, bcap.p1, fcap1.p1, fcap2.p1, fcap3.p1, fcap4.p1, fcap5.p1, pu_sda.p1, pu_scl.p1
    pn.gnd += vcap1.p1, vcap2.p1, u.p12, u.p18, u.p63, bcap.p2, fcap1.p2, fcap2.p2, fcap3.p2, fcap4.p2, fcap5.p2
