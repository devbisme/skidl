import os

import power_circuits as pc
import stm32_circuit as stm32

from skidl import *

# Delete sklib file or we get errors
for file in os.listdir("."):
    if file.endswith("sklib.py"):
        os.remove(file)

v_12v = Net("+12V", stub=True, netclass="Power")
v_5v = Net("+5V", stub=True, netclass="Power")
v_3v3 = Net("+3V3", stub=True, netclass="Power")
gnd = Net("GND", stub=True, netclass="Power")
vdda = Net("+3.3VA", stub=True, netclass="Power")

with Group("STM"):
    u = Part("MCU_ST_STM32F4", "STM32F405RGTx", footprint="LQFP-64_10x10mm_P0.5mm")
    u.p5 += Net("OSC_IN", stub=True)
    u.p6 += Net("OSC_OUT", stub=True)
    u.p7 += Net("NRST", stub=True)
    u.p8 += Net("HB", stub=True)
    u.p16 += Net("USART2_TX", stub=True)
    u.p17 += Net("USART2_TX", stub=True)
    u.p31 += Net("vcap1", stub=False)
    u.p47 += Net("vcap2", stub=True)
    u.p45 += Net("USB_P", stub=True)
    u.p44 += Net("USB_M", stub=True)
    u.p46 += Net("SWDIO", stub=True)
    u.p49 += Net("SWCLK", stub=True)
    u.p55 += Net("SWO", stub=True)
    u.p58 += Net("I2C1_SCL", stub=True)
    u.p59 += Net("I2C1_SDA", stub=True)
    u.p60 += Net("BOOT0", stub=True)

    # Bulking cap
    bcap = Part("Device", "C_Small", footprint="C_0603_1608Metric", value="4.7uF")
    # Decoupling caps
    fcap1 = Part("Device", "C_Small", footprint="C_0603_1608Metric", value="100nF")
    fcap2 = Part("Device", "C_Small", footprint="C_0603_1608Metric", value="100nF")
    fcap3 = Part("Device", "C_Small", footprint="C_0603_1608Metric", value="100nF")
    fcap4 = Part("Device", "C_Small", footprint="C_0603_1608Metric", value="100nF")
    fcap5 = Part("Device", "C_Small", footprint="C_0603_1608Metric", value="100nF")

    # VCaps recommended by ST
    vcap1 = Part("Device", "C_Small", footprint="C_0603_1608Metric", value="2.2uF")
    vcap2 = Part("Device", "C_Small", footprint="C_0603_1608Metric", value="2.2uF")

    # I2C pull-ups
    pu_scl = Part("Device", "R", footprint="R_0603_1608Metric", value="2.2k")
    pu_sda = Part("Device", "R", footprint="R_0603_1608Metric", value="2.2k")
    pu_scl.p2 += u.p58
    pu_sda.p2 += u.p59

    # Connect pins
    vcap2.p2 += u.p47
    vcap1.p2 += u.p31
    v_3v3 += (
        u.p1,
        u.p19,
        u.p32,
        u.p48,
        u.p64,
        bcap.p1,
        fcap1.p1,
        fcap2.p1,
        fcap3.p1,
        fcap4.p1,
        fcap5.p1,
        pu_sda.p1,
        pu_scl.p1,
    )
    gnd += (
        vcap1.p1,
        vcap2.p1,
        u.p12,
        u.p18,
        u.p63,
        bcap.p2,
        fcap1.p2,
        fcap2.p2,
        fcap3.p2,
        fcap4.p2,
        fcap5.p2,
    )

with Group("Boot_SW"):
    # Create parts
    sw = Part("Switch", "SW_SPDT", footprint="SW_SPDT_CK-JS102011SAQN")
    r1 = Part("Device", "R", footprint="R_0603_1608Metric", value="10k")

    # Connect parts
    sw.p1 += v_5v
    sw.p2 += r1.p1
    u.p60 += r1.p2
    sw.p3 += gnd

# Generate schematic
schematic_path = "./stm32.sch"
generate_schematic(file_=schematic_path, _title="SKiDL generated schematic")
