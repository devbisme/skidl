# -*- coding: utf-8 -*-
from skidl import *
from resistor_divider1 import resistor_divider1

@subcircuit
def esp32s3mini1(_p_3V3, _3v3_monitor, _5v_monitor, D_p, D_n, esp32s3mini1_HW_VER, GND):
    # Components
    C1 = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric', tag='C1', Sheetname='esp32s3mini1', Sheetfile='esp32s3mini1.kicad_sch', ki_keywords='cap capacitor', ki_fp_filters='C_*')
    J1 = Part('Connector_Generic', 'Conn_02x03_Odd_Even', value='Conn_02x03_Odd_Even', footprint='Connector_IDC:IDC-Header_2x03_P2.54mm_Vertical', tag='J1', Sheetname='esp32s3mini1', Sheetfile='esp32s3mini1.kicad_sch', ki_keywords='connector', ki_fp_filters='Connector*:*_2x??_*')
    U3 = Part('RF_Module', 'ESP32-S3-MINI-1', value='ESP32-S3-MINI-1', footprint='RF_Module:ESP32-S2-MINI-1', tag='U3', Sheetname='esp32s3mini1', Sheetfile='esp32s3mini1.kicad_sch', ki_keywords='RF Radio BT ESP ESP32-S3 Espressif', ki_fp_filters='ESP32?S*MINI?1')

    # Local nets
    esp32s3mini1_EN = Net('esp32s3mini1/EN')
    esp32s3mini1_IO0 = Net('esp32s3mini1/IO0')
    esp32s3mini1_RX = Net('esp32s3mini1/RX')
    esp32s3mini1_TX = Net('esp32s3mini1/TX')


    # Hierarchical subcircuits
    resistor_divider1(_p_3V3, esp32s3mini1_HW_VER, GND)

    # Connections
    _p_3V3 += C1['1'], J1['2'], U3['3']
    _3v3_monitor += U3['6']
    _5v_monitor += U3['7']
    D_p += U3['24']
    D_n += U3['23']
    esp32s3mini1_EN += J1['1'], U3['45']
    esp32s3mini1_HW_VER += U3['5']
    esp32s3mini1_IO0 += J1['6'], U3['4']
    esp32s3mini1_RX += J1['5'], U3['40']
    esp32s3mini1_TX += J1['3'], U3['39']
    GND += C1['2'], J1['4'], U3['1'], U3['2'], U3['42'], U3['43'], U3['46'], U3['47'], U3['48'], U3['49'], U3['50'], U3['51'], U3['52'], U3['53'], U3['54'], U3['55'], U3['56'], U3['57'], U3['58'], U3['59'], U3['60'], U3['61'], U3['62'], U3['63'], U3['64'], U3['65']
