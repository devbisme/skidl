import pytest
from skidl import *
from .setup_teardown import *

def test_connect_1():
    vreg = Part(get_filename('xess.lib'),
                '1117',
                footprint='null')
    vreg.value = 'NCV1117'
    gnd = Net('GND')
    vin = Net('Vin')
    vout = Net('Vout')
    gnd += vreg[1]
    vin += vreg[2]
    vout += vreg[3]
    assert vreg._is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vout) == 1


def test_connect_2():
    vreg1 = Part(get_filename('xess.lib'),
                 '1117',
                 footprint='null')
    vreg1.value = 'NCV1117'
    vreg2 = 1 * vreg1
    gnd = Net('GND')
    vin = Net('Vin')
    vout = Net('Vout')
    gnd += vreg1[1]
    vin += vreg1[2]
    vout += vreg1[3]
    vreg2[1, 2, 3] += gnd, vin, vout
    assert vreg1._is_connected() == True
    assert vreg2._is_connected() == True
    assert len(gnd) == 2
    assert len(vin) == 2
    assert len(vout) == 2


def test_connect_3():
    vreg1 = Part(get_filename('xess.lib'),
                 '1117',
                 footprint='null')
    vreg1.value = 'NCV1117'
    vreg2 = 1 * vreg1
    gnd = Net('GND')
    vin = Net('Vin')
    vout = Net('Vout')
    gnd += vreg1[1], vreg2[1]
    vin += vreg1[2], vreg2[2]
    vout += vreg1[3], vreg2[3]
    assert vreg1._is_connected() == True
    assert vreg2._is_connected() == True
    assert len(gnd) == 2
    assert len(vin) == 2
    assert len(vout) == 2


def test_connect_4():
    vreg1 = Part(get_filename('xess.lib'),
                 '1117',
                 footprint='null')
    vreg1.value = 'NCV1117'
    vreg2 = 1 * vreg1
    gnd = Net('GND')
    vin = Net('Vin')
    vout = Net('Vout')
    Bus('TMP', gnd, vin, vout)[:] += vreg1[1:3]
    Bus('TMP', gnd, vin, vout)[1:2] += vreg2[(2, 3)]
    assert vreg1._is_connected() == True
    assert vreg2._is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 2
    assert len(vout) == 2


def test_connect_5():
    vreg1 = Part(get_filename('xess.lib'),
                 '1117',
                 footprint='null')
    gnd = Net('GND')
    vin = Net('Vin')
    vreg1['GND', 'IN'] += gnd, vin
    vreg1['HS'] += vreg1['OUT']
    vreg1['OUT'] += vreg1['HS']
    assert vreg1._is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vreg1['IN'].net) == 1
    assert len(vreg1['HS'].net) == 2


def test_connect_6():
    gnd = Net('GND')
    vin = Net('Vin')
    vreg1 = Part(get_filename('xess.lib'),
                 '1117',
                 footprint='null',
                 connections={'GND': gnd,
                              'IN': vin})
    vreg2 = Part(get_filename('xess.lib'),
                 '1117',
                 footprint='null',
                 connections={'GND': gnd,
                              'IN': vin})
    vreg1['HS'] += vreg1['OUT']
    vregs = 2 * vreg1
    vregs = vreg1.copy(2)
    assert vreg1._is_connected() == True
    assert len(gnd) == 6
    assert len(vin) == 6
    assert len(vreg1['IN'].net) == 6
    assert len(vreg1['HS'].net) == 10


def test_connect_7():
    n1, n2 = 2 * Net()
    p1, p2, p3 = 3 * Pin()
    p1 += n1
    n2 += p2, p3
    p1 += p2, p3
    assert len(p1.net) == 3
    assert len(p1.net) == len(p2.net) == len(p3.net)
    assert len(n1) == 3
    assert len(n2) == 3
    assert n2._is_attached(n1)
