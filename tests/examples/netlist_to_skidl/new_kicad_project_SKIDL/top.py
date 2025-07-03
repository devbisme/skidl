# -*- coding: utf-8 -*-
from skidl import *
from esp32s3mini1 import esp32s3mini1
from _3v3_regulator import _3v3_regulator
from USB import USB

@subcircuit
def top():
    # Local nets
    _p_3V3 = Net('+3V3')
    _p_5V = Net('+5V')
    _3v3_monitor = Net('/3v3_monitor')
    _5v_monitor = Net('/5v_monitor')
    D_p = Net('/D+')
    D_n = Net('/D-')
    GND = Net('GND')

    # Hierarchical subcircuits
    esp32s3mini1(_p_3V3, _3v3_monitor, _5v_monitor, D_p, D_n, GND)
    _3v3_regulator(_p_3V3, _p_5V, _3v3_monitor, _5v_monitor, GND)
    USB(_p_5V, D_p, D_n, GND)
    return
