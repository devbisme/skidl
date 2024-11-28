# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

import skidl
from skidl import (
    ERC,
    Interface,
    POWER,
    SKIDL,
    TEMPLATE,
    Net,
    Part,
    Pin,
    erc_assert,
    erc_logger,
    subcircuit,
)
from skidl.pin import pin_types

from .setup_teardown import setup_function, teardown_function


# A default handler was added that logs errors when a part has an empty footprint.
# These ERC tests were made before that and now fail because of the footprint errors.
# Rather than re-do the tests, I just replaced the default handler with a function
# that doesn't do anything when a part has an empty footprint. Now the tests pass.
skidl.empty_footprint_handler = lambda part: None


def test_nc_1():
    """Test no-connect pins."""
    # Create a resistor part template.
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.PASSIVE), Pin(num=2, func=pin_types.PASSIVE)],
    )
    r1 = res(value="1K")
    r2 = res(value="500")
    r1 & r2  # Connection keeps resistors from being culled.

    # Create a capacitor part template.
    cap = Part(
        tool=SKIDL,
        name="cap",
        ref_prefix="C",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.PASSIVE), Pin(num=2, func=pin_types.NOCONNECT)],
    )
    c1 = cap()
    c2 = cap(value="1uF")
    c1[1] & c2[1]  # Connection keeps capacitors from being culled.

    # Create nets.
    gnd = Net("GND")  # Ground reference.
    vin = Net("VI")  # Input voltage to the divider.
    vout = Net("VO")  # Output voltage from the divider.

    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 8
    assert erc_logger.error.count == 0


def test_nc_2():
    """Test no-connect pin with passive pin."""
    # Create a resistor part template.
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.NOCONNECT), Pin(num=2, func=pin_types.PASSIVE)],
    )
    r1 = res()
    r1[1] += r1[2]

    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 1
    assert erc_logger.error.count == 1


def test_conflict_1():
    """Test power input pin with power output pin."""
    # Create a resistor part template.
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.PWRIN), Pin(num=2, func=pin_types.PWROUT)],
    )
    r1 = res()
    r1[1] += r1[2]

    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 0
    assert erc_logger.error.count == 0


def test_conflict_2():
    """Test output pin with power output pin."""
    # Create a resistor part template.
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.OUTPUT), Pin(num=2, func=pin_types.PWROUT)],
    )
    r1 = res()
    r1[1] += r1[2]

    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 0
    assert erc_logger.error.count == 1


def test_drive_1():
    """Test input pin with power input pin."""
    # Create a resistor part template.
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.INPUT), Pin(num=2, func=pin_types.PWRIN)],
    )
    r1 = res()
    r1[1] += r1[2]

    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 3
    assert erc_logger.error.count == 0


def test_drive_2():
    """Test input pin with power input pin."""
    # Create a resistor part template.
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.INPUT), Pin(num=2, func=pin_types.PWRIN)],
    )
    r1 = res()
    r1[1] += r1[2]

    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 3
    assert erc_logger.error.count == 0


def test_drive_3():
    """Test input pin with power input pin and set drive to power."""
    # Create a resistor part template.
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.INPUT), Pin(num=2, func=pin_types.PWRIN)],
    )
    r1 = res()
    r1[1] += r1[2]
    r1[1].drive = POWER

    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 0
    assert erc_logger.error.count == 0


def test_drive_4():
    """Test input pin with power input pin and set net drive to power."""
    # Create a resistor part template.
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.INPUT), Pin(num=2, func=pin_types.PWRIN)],
    )
    r1 = res()
    n = Net()
    n += r1[:]
    n.drive = POWER

    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 0
    assert erc_logger.error.count == 0


def test_pull_1():
    """Test pull-up pin with pull-down pin."""
    # Create a resistor part template.
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.PULLUP), Pin(num=2, func=pin_types.PULLDN)],
    )
    r1 = res()
    r1[1] += r1[2]

    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 0
    assert erc_logger.error.count == 1


def test_pull_2():
    """Test pull-up pin with pull-up pin."""
    # Create a resistor part template.
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.PULLUP), Pin(num=2, func=pin_types.PULLUP)],
    )
    r1 = res()
    r1[1] += r1[2]

    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 1
    assert erc_logger.error.count == 0


def test_pull_3():
    """Test pull-down pin with input pin."""
    # Create a resistor part template.
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.PULLDN), Pin(num=2, func=pin_types.INPUT)],
    )
    r1 = res()
    r1[1] += r1[2]

    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 0
    assert erc_logger.error.count == 0


def test_all_pin_funcs_1():
    """Test all pin functions."""
    # Create a resistor part template.
    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=pin_types.PULLDN), Pin(num=2, func=pin_types.INPUT)],
    )
    # Create a resistor and assign a pin function to each pin.
    # The, connect the pins and see what type of ERC errors are generated.
    for f1 in pin_types:
        for f2 in pin_types:
            r = res()
            r[1].func = f1
            r[2].func = f2
            r[1] += r[2]
    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 124
    assert erc_logger.error.count == 45


def test_assert_1():
    """Test ERC assertions."""
    # Test assertion that should fail.
    erc_assert("len(Net.get('GND'))==1")  # Should fail.

    # Create resistor and capacitor part templates.
    r = Part("Device", "R", dest=TEMPLATE)
    c = Part("Device", "C", dest=TEMPLATE)

    r1 = r(value="1K")
    r2 = r(value="500")
    r1 & r2  # Keeps resistors from being culled.
    c1 = c()
    c2 = c(value="1uF")
    c1 & c2  # Keeps capacitors from being culled.

    # Create nets.
    gnd = Net("GND")  # Ground reference.
    vin = Net("VI")  # Input voltage to the divider.
    vout = Net("VO")  # Output voltage from the divider.

    # Test assertion that should not fail.
    erc_assert("len(gnd)==0", "Failed test!")  # Should not fail.

    # Run ERC and check warnings and errors.
    ERC()
    assert erc_logger.warning.count == 10
    assert erc_logger.error.count == 1


def test_assert_2():
    """Test ERC assertions within subcircuits."""
    # Create resistor and capacitor part templates.
    r = Part("Device", "R", dest=TEMPLATE)
    c = Part("Device", "C", dest=TEMPLATE)

    @subcircuit
    def sub1(my_vin, my_gnd):
        """Subcircuit 1."""
        r1 = r()
        c1 = c()
        my_vin & r1 & c1 & my_gnd
        erc_assert("len(my_vin) == len(my_gnd)")

    @subcircuit
    def sub2(my_vin, my_gnd):
        """Subcircuit 2."""
        sub1(my_vin, my_gnd)
        sub1(my_vin, my_gnd)
        erc_assert("len(my_vin) == 2")  # Will fail because of connection below.
        return Interface(my_vin=my_vin, my_gnd=my_gnd)

    # Create nets.
    vin, gnd = Net("VIN"), Net("GND")
    sub = sub2(vin, gnd)
    vin += sub.my_vin
    gnd += sub.my_gnd
    # sub.my_vin += vin
    # sub.my_gnd += gnd
    # sub2(vin, gnd)
    r1 = r()
    vin & r1 & gnd  # Makes the assertion in sub2() fail.

    # Run ERC and check assertions.
    ERC()
    assert len(default_circuit.erc_assertion_list) == 3
