# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Bus, Net, Part, Pin

from .setup_teardown import setup_function, teardown_function


def test_connect_1():
    LED = Part("Device", "LED_ARBG", footprint="null")
    LED.value = "RBG_LED"
    gnd = Net("GND")
    vin = Net("Vin")
    vout = Net("Vout")
    gnd += LED[1]
    vin += LED[2]
    vout += LED[3]
    assert LED.is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vout) == 1


def test_connect_2():
    LED1 = Part("Device", "LED_ARBG", footprint="null")
    LED1.value = "RBG_LED"
    LED2 = LED1.copy(1)[0]
    gnd = Net("GND")
    vin = Net("Vin")
    vout = Net("Vout")
    gnd += LED1[1]
    vin += LED1.p2
    vout += LED1.BK, LED1.GK
    LED2[1, 2, 3, "GK"] += gnd, vin, vout, vout
    assert LED1.is_connected() == True
    assert LED2.is_connected() == True
    assert len(gnd) == 2
    assert len(vin) == 2
    assert len(vout) == 4


def test_connect_3():
    LED1 = Part("Device", "LED_ARBG", footprint="null")
    LED1.value = "RBG_LED"
    LED2 = LED1.copy(1)[0]
    gnd = Net("GND")
    vin = Net("Vin")
    vout = Net("Vout")
    gnd += LED1[1], LED2[1]
    vin += LED1[2], LED2[2]
    vout += LED1[3], LED2[3]
    assert LED1.is_connected() == True
    assert LED2.is_connected() == True
    assert len(gnd) == 2
    assert len(vin) == 2
    assert len(vout) == 2


def test_connect_4():
    LED1 = Part("Device", "LED_ARBG", footprint="null")
    LED1.value = "RBG_LED"
    LED2 = LED1()
    gnd = Net("GND")
    vin = Net("Vin")
    vout = Net("Vout")
    Bus("TMP", gnd, vin, vout)[:] += LED1[1:3]
    Bus("TMP", gnd, vin, vout)[1:2] += LED2[(2, 3)]
    assert LED1.is_connected() == True
    assert LED2.is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 2
    assert len(vout) == 2


def test_connect_5():
    LED = Part("Device", "LED_ARBG", footprint="null")
    gnd = Net("GND")
    vin = Net("Vin")
    LED["A", "RK"] += gnd, vin
    LED["BK"] += LED["GK"]
    LED["GK"] += LED["BK"]
    assert LED.is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(LED["A"].net) == 1
    assert len(LED["RK"].net) == 1
    assert len(LED["BK"].net) == 2
    assert len(LED["GK"].net) == 2


def test_connect_6():
    gnd = Net("GND")
    vin = Net("Vin")
    LED1 = Part("Device", "LED_ARBG", footprint="null", connections={"A": gnd, "RK": vin})
    LED2 = Part("Device", "LED_ARBG", footprint="null", connections={"A": gnd, "RK": vin})
    LED1["GK"] += LED1["BK"]
    LEDS = 2 * LED1
    LEDS = LED1.copy(2)
    assert LED1.is_connected() == True
    assert len(gnd) == 6
    assert len(vin) == 6
    assert len(LED1["A"].net) == 6
    assert len(LED1["RK"].net) == 6
    assert len(LED1["BK"].net) == 10
    assert len(LED1["GK"].net) == 10


def test_connect_7():
    n1, n2 = 2 * Net()
    p1, p2, p3 = Pin(), Pin(), Pin()
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
    p1, p2, p3 = Pin(), Pin(), Pin()
    n1[0] += p1, p2, p3
    assert len(n1) == 3


def test_connect_9():
    n1 = Net()
    p1, p2, p3 = Pin(), Pin(), Pin()
    n1[:] += p1, p2, p3
    assert len(n1) == 3


def test_connect_10():
    n1 = Net()
    p1, p2, p3 = Pin(), Pin(), Pin()
    with pytest.raises(ValueError):
        n1[1] += p1, p2, p3


def test_connect_11():
    n1 = Net()
    p1, p2, p3 = Pin(), Pin(), Pin()
    n1[:] += p1, p2, p3[:]
    assert len(n1) == 3
