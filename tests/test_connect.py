# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import Part, Net, Bus, Pin

from .setup_teardown import setup_function, teardown_function


def test_connect_1():
    vreg = Part("xess.lib", "1117", footprint="null")
    vreg.value = "NCV1117"
    gnd = Net("GND")
    vin = Net("Vin")
    vout = Net("Vout")
    gnd += vreg[1]
    vin += vreg[2]
    vout += vreg[3]
    assert vreg.is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vout) == 1


def test_connect_2():
    vreg1 = Part("xess.lib", "1117", footprint="null")
    vreg1.value = "NCV1117"
    vreg2 = vreg1.copy(1)[0]
    gnd = Net("GND")
    vin = Net("Vin")
    vout = Net("Vout")
    gnd += vreg1[1]
    vin += vreg1.p2
    vout += vreg1.IN, vreg1.HS
    vreg2[1, 2, 3, "HS"] += gnd, vin, vout, vout
    assert vreg1.is_connected() == True
    assert vreg2.is_connected() == True
    assert len(gnd) == 2
    assert len(vin) == 2
    assert len(vout) == 4


def test_connect_3():
    vreg1 = Part("xess.lib", "1117", footprint="null")
    vreg1.value = "NCV1117"
    vreg2 = vreg1.copy()
    gnd = Net("GND")
    vin = Net("Vin")
    vout = Net("Vout")
    gnd += vreg1[1], vreg2[1]
    vin += vreg1[2], vreg2[2]
    vout += vreg1[3], vreg2[3]
    assert vreg1.is_connected() == True
    assert vreg2.is_connected() == True
    assert len(gnd) == 2
    assert len(vin) == 2
    assert len(vout) == 2


def test_connect_4():
    vreg1 = Part("xess.lib", "1117", footprint="null")
    vreg1.value = "NCV1117"
    vreg2 = vreg1()
    gnd = Net("GND")
    vin = Net("Vin")
    vout = Net("Vout")
    Bus("TMP", gnd, vin, vout)[:] += vreg1[1:3]
    Bus("TMP", gnd, vin, vout)[1:2] += vreg2[(2, 3)]
    assert vreg1.is_connected() == True
    assert vreg2.is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 2
    assert len(vout) == 2


def test_connect_5():
    vreg1 = Part("xess.lib", "1117", footprint="null")
    gnd = Net("GND")
    vin = Net("Vin")
    vreg1["GND", "IN"] += gnd, vin
    vreg1["HS"] += vreg1["OUT"]
    vreg1["OUT"] += vreg1["HS"]
    assert vreg1.is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vreg1["IN"].net) == 1
    assert len(vreg1["HS"].net) == 2


def test_connect_6():
    gnd = Net("GND")
    vin = Net("Vin")
    vreg1 = Part(
        "xess.lib", "1117", footprint="null", connections={"GND": gnd, "IN": vin}
    )
    vreg2 = Part(
        "xess.lib", "1117", footprint="null", connections={"GND": gnd, "IN": vin}
    )
    vreg1["HS"] += vreg1["OUT"]
    vregs = 2 * vreg1
    vregs = vreg1.copy(2)
    assert vreg1.is_connected() == True
    assert len(gnd) == 6
    assert len(vin) == 6
    assert len(vreg1["IN"].net) == 6
    assert len(vreg1["HS"].net) == 10


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
    assert n2.is_attached(n1)


def test_connect_8():
    n1 = Net()
    p1, p2, p3 = 3 * Pin()
    n1[0] += p1, p2, p3
    assert len(n1) == 3


def test_connect_9():
    n1 = Net()
    p1, p2, p3 = 3 * Pin()
    n1[:] += p1, p2, p3
    assert len(n1) == 3


def test_connect_10():
    n1 = Net()
    p1, p2, p3 = 3 * Pin()
    with pytest.raises(ValueError):
        n1[1] += p1, p2, p3


def test_connect_11():
    n1 = Net()
    p1, p2, p3 = 3 * Pin()
    n1[:] += p1, p2, p3[:]
    assert len(n1) == 3
