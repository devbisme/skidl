import pytest
from skidl import *
from .setup_teardown import *

def test_string_indices_1():
    vreg1 = Part(get_filename('xess.lib'),
                 '1117',
                 footprint='null')
    gnd = Net('GND')
    vin = Net('Vin')
    vreg1['GND, IN, OUT'] += gnd, vin, vreg1['HS']
    assert vreg1._is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vreg1['IN'].net) == 1
    assert len(vreg1['HS'].net) == 2
    assert len(vreg1['OUT'].net) == 2
    assert vreg1['OUT'].net._is_attached(vreg1['HS'].net)
