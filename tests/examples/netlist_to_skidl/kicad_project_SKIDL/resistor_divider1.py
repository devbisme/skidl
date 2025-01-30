# -*- coding: utf-8 -*-
from skidl import *

@subcircuit
def resistor_divider1(_p_3V3, esp32s3mini1_HW_VER, GND):
    # Components
    C10 = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0603_1608Metric', ref='C10', Sheetname='resistor_divider1', Sheetfile='resistor_divider.kicad_sch', ki_keywords='cap capacitor', ki_fp_filters='C_*')
    R10 = Part('Device', 'R', value='1k', footprint='Resistor_SMD:R_0603_1608Metric', ref='R10', Sheetname='resistor_divider1', Sheetfile='resistor_divider.kicad_sch', ki_keywords='R res resistor', ki_fp_filters='R_*')
    R9 = Part('Device', 'R', value='2k', footprint='Resistor_SMD:R_0603_1608Metric', ref='R9', Sheetname='resistor_divider1', Sheetfile='resistor_divider.kicad_sch', ki_keywords='R res resistor', ki_fp_filters='R_*')


    # Connections
    _p_3V3 += R9['1']
    esp32s3mini1_HW_VER += C10['1'], R10['1'], R9['2']
    GND += C10['2'], R10['2']
