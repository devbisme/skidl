# -*- coding: utf-8 -*-
from skidl import *

@subcircuit
def _3v3_regulator(_p_3V3, _p_5V, _3v3_monitor, _5v_monitor, GND):
    # Components
    C2 = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric', ref='C2', fields={'Sheetname': '3v3_regulator', 'Sheetfile': 'power2.kicad_sch', 'ki_keywords': 'cap capacitor', 'ki_fp_filters': 'C_*'})
    C3 = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric', ref='C3', fields={'Sheetname': '3v3_regulator', 'Sheetfile': 'power2.kicad_sch', 'ki_keywords': 'cap capacitor', 'ki_fp_filters': 'C_*'})
    C5 = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0603_1608Metric', ref='C5', fields={'Sheetname': '3v3_regulator', 'Sheetfile': 'power2.kicad_sch', 'ki_keywords': 'cap capacitor', 'ki_fp_filters': 'C_*'})
    C9 = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0603_1608Metric', ref='C9', fields={'Sheetname': '3v3_regulator', 'Sheetfile': 'power2.kicad_sch', 'ki_keywords': 'cap capacitor', 'ki_fp_filters': 'C_*'})
    R2 = Part('Device', 'R', value='2k', footprint='Resistor_SMD:R_0603_1608Metric', ref='R2', fields={'Sheetname': '3v3_regulator', 'Sheetfile': 'power2.kicad_sch', 'ki_keywords': 'R res resistor', 'ki_fp_filters': 'R_*'})
    R3 = Part('Device', 'R', value='1k', footprint='Resistor_SMD:R_0603_1608Metric', ref='R3', fields={'Sheetname': '3v3_regulator', 'Sheetfile': 'power2.kicad_sch', 'ki_keywords': 'R res resistor', 'ki_fp_filters': 'R_*'})
    R7 = Part('Device', 'R', value='1k', footprint='Resistor_SMD:R_0603_1608Metric', ref='R7', fields={'Sheetname': '3v3_regulator', 'Sheetfile': 'power2.kicad_sch', 'ki_keywords': 'R res resistor', 'ki_fp_filters': 'R_*'})
    R8 = Part('Device', 'R', value='2k', footprint='Resistor_SMD:R_0603_1608Metric', ref='R8', fields={'Sheetname': '3v3_regulator', 'Sheetfile': 'power2.kicad_sch', 'ki_keywords': 'R res resistor', 'ki_fp_filters': 'R_*'})
    U1 = Part('Regulator_Linear', 'NCP1117-3.3_SOT223', value='NCP1117-3.3_SOT223', footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2', ref='U1', fields={'Sheetname': '3v3_regulator', 'Sheetfile': 'power2.kicad_sch', 'ki_keywords': 'REGULATOR LDO 3.3V', 'ki_fp_filters': 'SOT?223*TabPin2*'})


    # Connections
    _p_3V3 += C2['1'], R8['1'], U1['2']
    _p_5V += C3['1'], R2['1'], U1['3']
    _3v3_monitor += C5['1'], R3['1'], R8['2']
    _5v_monitor += C9['1'], R2['2'], R7['1']
    GND += C2['2'], C3['2'], C5['2'], C9['2'], R3['2'], R7['2'], U1['1']
    return
