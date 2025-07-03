# -*- coding: utf-8 -*-
from skidl import *

@subcircuit
def USB(_p_5V, D_p, D_n, GND):
    # Local nets
    Net__P1_CC_ = Net('Net-(P1-CC)')

    # Components
    C4 = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric', ref='C4', fields={'Sheetname': 'USB', 'Sheetfile': 'usb.kicad_sch', 'ki_keywords': 'cap capacitor', 'ki_fp_filters': 'C_*'})
    P1 = Part('Connector', 'USB_C_Plug_USB2.0', value='USB_C_Plug_USB2.0', footprint='Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal', ref='P1', fields={'Sheetname': 'USB', 'Sheetfile': 'usb.kicad_sch', 'ki_keywords': 'usb universal serial bus type-C USB2.0', 'ki_fp_filters': 'USB*C*Plug*'})
    R1 = Part('Device', 'R', value='5.1K', footprint='Resistor_SMD:R_0603_1608Metric', ref='R1', fields={'Sheetname': 'USB', 'Sheetfile': 'usb.kicad_sch', 'ki_keywords': 'R res resistor', 'ki_fp_filters': 'R_*'})


    # Connections
    _p_5V += C4['1'], P1['A4'], P1['A9'], P1['B4'], P1['B9']
    D_p += P1['A6']
    D_n += P1['A7']
    GND += C4['2'], P1['A1'], P1['A12'], P1['B1'], P1['B12'], P1['S1'], R1['2']
    Net__P1_CC_ += P1['A5'], R1['1']
    return
