import pytest

from skidl import *

from .setup_teardown import *


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

    cap = Part(
        tool=SKIDL,
        name="cap",
        ref_prefix="C",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.PASSIVE), Pin(num=2, func=Pin.types.NOCONNECT)],
    )
    c1 = cap()
    c2 = cap(value="1uF")

    gnd = Net("GND")  # Ground reference.
    vin = Net("VI")  # Input voltage to the divider.
    vout = Net("VO")  # Output voltage from the divider.

    ERC()
    assert erc_logger.warning.count == 12
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

    res = Part(
        tool=SKIDL,
        name="res",
        ref_prefix="R",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.PASSIVE), Pin(num=2, func=Pin.types.PASSIVE)],
    )
    r1 = res(value="1K")
    r2 = res(value="500")

    cap = Part(
        tool=SKIDL,
        name="cap",
        ref_prefix="C",
        dest=TEMPLATE,
        pins=[Pin(num=1, func=Pin.types.PASSIVE), Pin(num=2, func=Pin.types.NOCONNECT)],
    )
    c1 = cap()
    c2 = cap(value="1uF")

    gnd = Net("GND")  # Ground reference.
    vin = Net("VI")  # Input voltage to the divider.
    vout = Net("VO")  # Output voltage from the divider.

    # add_erc_assertion(default_circuit, "len(gnd)==1")
    # add_erc_assertion(default_circuit, compile("len(gnd)==0", "<stdin>", "eval"), globals(), locals())
    add_erc_assertion(default_circuit, "len(gnd)==1")

    ERC()
    assert erc_logger.warning.count == 12
    assert erc_logger.error.count == 0
