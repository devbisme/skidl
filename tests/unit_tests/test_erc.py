# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import (
    ERC,
    POWER,
    SKIDL,
    TEMPLATE,
    Net,
    Part,
    Pin,
    erc_assert,
    erc_logger,
    package,
    subcircuit,
)

from .setup_teardown import setup_function, teardown_function


def test_nc_1():

    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.PASSIVE), Pin(num=2, func=Pin.types.PASSIVE)],
    )
    r1 = res(value="1K")
    r2 = res(value="500")
    r1 & r2  # Connection keeps resistors from being culled.

    cap = Part(
        tool=SKIDL,
        name="cap",
        ref_prefix="C",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.PASSIVE), Pin(num=2, func=Pin.types.NOCONNECT)],
    )
    c1 = cap()
    c2 = cap(value="1uF")
    c1[1] & c2[1]  # Connection keeps capacitors from being culled.

    gnd = Net("GND")  # Ground reference.
    vin = Net("VI")  # Input voltage to the divider.
    vout = Net("VO")  # Output voltage from the divider.

    ERC()
    assert erc_logger.warning.count == 8
    assert erc_logger.error.count == 0


def test_nc_2():
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.NOCONNECT), Pin(num=2, func=Pin.types.PASSIVE)],
    )
    r1 = res()
    r1[1] += r1[2]

    ERC()
    assert erc_logger.warning.count == 1
    assert erc_logger.error.count == 1


def test_conflict_1():
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.PWRIN), Pin(num=2, func=Pin.types.PWROUT)],
    )
    r1 = res()
    r1[1] += r1[2]

    ERC()
    assert erc_logger.warning.count == 0
    assert erc_logger.error.count == 0


def test_conflict_2():
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.OUTPUT), Pin(num=2, func=Pin.types.PWROUT)],
    )
    r1 = res()
    r1[1] += r1[2]

    ERC()
    assert erc_logger.warning.count == 0
    assert erc_logger.error.count == 1


def test_drive_1():
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.INPUT), Pin(num=2, func=Pin.types.PWRIN)],
    )
    r1 = res()
    r1[1] += r1[2]

    ERC()
    assert erc_logger.warning.count == 3
    assert erc_logger.error.count == 0


def test_drive_2():
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.INPUT), Pin(num=2, func=Pin.types.PWRIN)],
    )
    r1 = res()
    r1[1] += r1[2]

    ERC()
    assert erc_logger.warning.count == 3
    assert erc_logger.error.count == 0


def test_drive_3():
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.INPUT), Pin(num=2, func=Pin.types.PWRIN)],
    )
    r1 = res()
    r1[1] += r1[2]
    r1[1].drive = POWER

    ERC()
    assert erc_logger.warning.count == 0
    assert erc_logger.error.count == 0


def test_drive_4():
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.INPUT), Pin(num=2, func=Pin.types.PWRIN)],
    )
    r1 = res()
    n = Net()
    n += r1[:]
    n.drive = POWER

    ERC()
    assert erc_logger.warning.count == 0
    assert erc_logger.error.count == 0


def test_pull_1():
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.PULLUP), Pin(num=2, func=Pin.types.PULLDN)],
    )
    r1 = res()
    r1[1] += r1[2]

    ERC()
    assert erc_logger.warning.count == 0
    assert erc_logger.error.count == 1


def test_pull_2():
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.PULLUP), Pin(num=2, func=Pin.types.PULLUP)],
    )
    r1 = res()
    r1[1] += r1[2]

    ERC()
    assert erc_logger.warning.count == 1
    assert erc_logger.error.count == 0


def test_pull_3():
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.PULLDN), Pin(num=2, func=Pin.types.INPUT)],
    )
    r1 = res()
    r1[1] += r1[2]

    ERC()
    assert erc_logger.warning.count == 0
    assert erc_logger.error.count == 0


def test_all_pin_funcs_1():
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.PULLDN), Pin(num=2, func=Pin.types.INPUT)],
    )
    for f1 in Pin.types:
        for f2 in Pin.types:
            r = res()
            r[1].func = f1
            r[2].func = f2
            r[1] += r[2]
    ERC()
    assert erc_logger.warning.count == 109  # 35 from pin conflicts.
    assert erc_logger.error.count == 43  # 43 from pin conflicts.


def test_assert_1():

    erc_assert("len(Net.get('GND'))==1")  # Should fail.

    r = Part("Device", "R", dest=TEMPLATE)
    c = Part("Device", "C", dest=TEMPLATE)

    r1 = r(value="1K")
    r2 = r(value="500")
    r1 & r2  # Keeps resistors from being culled.
    c1 = c()
    c2 = c(value="1uF")
    c1 & c2  # Keeps capacitors from being culled.

    gnd = Net("GND")  # Ground reference.
    vin = Net("VI")  # Input voltage to the divider.
    vout = Net("VO")  # Output voltage from the divider.

    erc_assert("len(gnd)==0", "Failed test!")  # Should not fail.

    ERC()
    assert erc_logger.warning.count == 10
    assert erc_logger.error.count == 1


def test_assert_2():

    r = Part("Device", "R", dest=TEMPLATE)
    c = Part("Device", "C", dest=TEMPLATE)

    @subcircuit
    def sub1(my_vin, my_gnd):
        r1 = r()
        c1 = c()
        my_vin & r1 & c1 & my_gnd
        erc_assert("len(my_vin) == len(my_gnd)")

    @package
    # @subcircuit
    def sub2(my_vin, my_gnd):
        sub1(my_vin, my_gnd)
        sub1(my_vin, my_gnd)
        erc_assert("len(my_vin) == 2")  # Will fail because of connection below.

    vin, gnd = Net("VIN"), Net("GND")
    sub = sub2()
    vin += sub.my_vin
    gnd += sub.my_gnd
    # sub.my_vin += vin
    # sub.my_gnd += gnd
    # sub2(vin, gnd)
    r1 = r()
    vin & r1 & gnd  # Makes the assertion in sub2() fail.

    ERC()

    assert len(default_circuit.erc_assertion_list) == 3
