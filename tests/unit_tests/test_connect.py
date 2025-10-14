# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Bus, Net, Part, Pin


def test_connect_1():
    """
    Test connecting a single LED to nets
    """
    # Create an LED part
    LED = Part("Device", "LED_ARBG", footprint="null")
    LED.value = "RBG_LED"
    # Create nets
    gnd = Net("GND")
    vin = Net("Vin")
    vout = Net("Vout")
    # Connect LED pins to nets
    gnd += LED[1]
    vin += LED[2]
    vout += LED[3]
    # Check connections
    assert LED.is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vout) == 1

def test_connect_2():
    """
    Test connecting two LEDs to nets using copy
    """
    # Create an LED part and copy it
    LED1 = Part("Device", "LED_ARBG", footprint="null")
    LED1.value = "RBG_LED"
    LED2 = LED1.copy(1)[0]
    # Create nets
    gnd = Net("GND")
    vin = Net("Vin")
    vout = Net("Vout")
    # Connect LED1 pins to nets
    gnd += LED1[1]
    vin += LED1.p2
    vout += LED1.BK, LED1.GK
    # Connect LED2 pins to nets
    LED2[1, 2, 3, "GK"] += gnd, vin, vout, vout
    # Check connections
    assert LED1.is_connected() == True
    assert LED2.is_connected() == True
    assert len(gnd) == 2
    assert len(vin) == 2
    assert len(vout) == 4

def test_connect_3():
    """
    Test connecting two LEDs to nets directly
    """
    # Create an LED part and copy it
    LED1 = Part("Device", "LED_ARBG", footprint="null")
    LED1.value = "RBG_LED"
    LED2 = LED1.copy(1)[0]
    # Create nets
    gnd = Net("GND")
    vin = Net("Vin")
    vout = Net("Vout")
    # Connect LED1 and LED2 pins to nets
    gnd += LED1[1], LED2[1]
    vin += LED1[2], LED2[2]
    vout += LED1[3], LED2[3]
    # Check connections
    assert LED1.is_connected() == True
    assert LED2.is_connected() == True
    assert len(gnd) == 2
    assert len(vin) == 2
    assert len(vout) == 2

def test_connect_4():
    """
    Test connecting two LEDs to nets using Bus
    """
    # Create an LED part and copy it
    LED1 = Part("Device", "LED_ARBG", footprint="null")
    LED1.value = "RBG_LED"
    LED2 = LED1()
    # Create nets
    gnd = Net("GND")
    vin = Net("Vin")
    vout = Net("Vout")
    # Connect LED1 and LED2 pins to nets using Bus
    Bus("TMP", gnd, vin, vout)[:] += LED1[1:3]
    Bus("TMP", gnd, vin, vout)[1:2] += LED2[(2, 3)]
    # Check connections
    assert LED1.is_connected() == True
    assert LED2.is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 2
    assert len(vout) == 2

def test_connect_5():
    """
    Test connecting LED pins to nets and interconnecting LED pins
    """
    # Create an LED part
    LED = Part("Device", "LED_ARBG", footprint="null")
    # Create nets
    gnd = Net("GND")
    vin = Net("Vin")
    # Connect LED pins to nets
    LED["A", "RK"] += gnd, vin
    # Interconnect LED pins
    LED["BK"] += LED["GK"]
    LED["GK"] += LED["BK"]
    # Check connections
    assert LED.is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(LED["A"].net) == 1
    assert len(LED["RK"].net) == 1
    assert len(LED["BK"].net) == 2
    assert len(LED["GK"].net) == 2

def test_connect_6():
    """
    Test connecting multiple LEDs to nets using connections parameter
    """
    # Create nets
    gnd = Net("GND")
    vin = Net("Vin")
    # Create LED parts with connections
    LED1 = Part("Device", "LED_ARBG", footprint="null", connections={"A": gnd, "RK": vin})
    LED2 = Part("Device", "LED_ARBG", footprint="null", connections={"A": gnd, "RK": vin})
    # Interconnect LED pins
    LED1["GK"] += LED1["BK"]
    # Copy LED1
    LEDS = 2 * LED1
    LEDS = LED1.copy(2)
    # Check connections
    assert LED1.is_connected() == True
    assert len(gnd) == 6
    assert len(vin) == 6
    assert len(LED1["A"].net) == 6
    assert len(LED1["RK"].net) == 6
    assert len(LED1["BK"].net) == 10
    assert len(LED1["GK"].net) == 10

def test_connect_7():
    """
    Test connecting pins to nets and checking net lengths
    """
    # Create nets
    n1, n2 = 2 * Net()
    # Create pins
    p1, p2, p3 = Pin(), Pin(), Pin()
    # Connect pins to nets
    p1 += n1
    n2 += p2, p3
    p1 += p2, p3
    # Check net lengths
    assert len(p1.net) == 3
    assert len(p1.net) == len(p2.net) == len(p3.net)
    assert len(n1) == 3
    assert len(n2) == 3
    assert n2.is_attached(n1)

def test_connect_8():
    """
    Test connecting multiple pins to a net using indexing
    """
    # Create a net
    n1 = Net()
    # Create pins
    p1, p2, p3 = Pin(), Pin(), Pin()
    # Connect pins to net using indexing
    n1[0] += p1, p2, p3
    # Check net length
    assert len(n1) == 3

def test_connect_9():
    """
    Test connecting multiple pins to a net using slicing
    """
    # Create a net
    n1 = Net()
    # Create pins
    p1, p2, p3 = Pin(), Pin(), Pin()
    # Connect pins to net using slicing
    n1[:] += p1, p2, p3
    # Check net length
    assert len(n1) == 3

def test_connect_10():
    """
    Test raising ValueError when using invalid index for net connection
    """
    # Create a net
    n1 = Net()
    # Create pins
    p1, p2, p3 = Pin(), Pin(), Pin()
    # Check for ValueError when using invalid index
    with pytest.raises(ValueError):
        n1[1] += p1, p2, p3

def test_connect_11():
    """
    Test connecting multiple pins to a net using slicing and pin slicing
    """
    # Create a net
    n1 = Net()
    # Create pins
    p1, p2, p3 = Pin(), Pin(), Pin()
    # Connect pins to net using slicing and pin slicing
    n1[:] += p1, p2, p3[:]
    # Check net length
    assert len(n1) == 3

def test_connect_12():
    """
    Test connecting multiple pins to nets and selecting one pin from multiple matching alternate names.
    """
    mcu = Part('MCU_ST_STM32F1','STM32F100C_4-6_Tx')
    # Create nets
    vss = Net("VSS")
    vdd = Net("VDD")
    sck = Net("SCK")
    # Connect MCU pins to nets.
    # Test multiple connections of VDD and VSS pins.
    mcu["VDD"] += vdd
    vss += mcu["VSS"]
    # Test different ways of connecting a pin with an alternate name that matches multiple pins.
    sck += mcu["SPI1_SCK"][39]
    sck += mcu["SPI1_SCK"]["PB3"]
    mcu["SPI1_SCK"].p39 += sck
    # Check connections
    assert mcu.is_connected() == True
    assert len(vss) == 3
    assert len(vdd) == 3
    # Connecting the same pin in multiple ways should still result in just one connection.
    assert len(sck) == 1
