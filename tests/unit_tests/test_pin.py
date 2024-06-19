# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Part, Pin

from .setup_teardown import setup_function, teardown_function


def test_pin_names_1():
    mem = Part("Memory_RAM", "AS4C4M16SA")
    assert mem["DQ15"] == mem.n["DQ15"]
    assert mem[1:4] == mem.p[1:4]


def test_pin_names_2():
    mem = Part("Memory_RAM", "AS4C4M16SA")
    mem[4].name = "X1"
    mem[8].name = "X2"
    mem[8].num = "X1"
    assert mem[4] is mem.n["X1"]
    assert mem.p[4] is mem.n["X1"]
    assert mem[4] is mem.p[4]
    assert mem.p["X1"] is mem.n["X2"]
    assert mem["X1"] is mem.n["X2"]
    assert mem["X1"] is mem.p["X1"]


def test_numerical_pin_order():
    mem = Part("Memory_RAM", "AS4C4M16SA")
    p = mem.pins.pop(13)
    mem.pins.append(p)
    assert [int(x.num) for x in mem.pins] != list(range(1, len(mem.pins) + 1))
    assert [int(x.num) for x in mem.ordered_pins] == list(
        range(1, len(mem.pins) + 1)
    )


def test_alphanumeric_pin_order():
    mem = Part("Memory_RAM", "AS4C4M16SA")
    mem[3].num = "A1"
    mem[5].num = "B1"
    assert [p.num for p in mem.ordered_pins[-6:]] == [
        "51",
        "52",
        "53",
        "54",
        "A1",
        "B1",
    ]


def test_eq():
    p1 = Pin(num=1)
    p2 = Pin(num=1)
    assert p1 == p2
    assert p1 is not p2
    p2.part = "new part"
    assert p1 != p2


def test_numeric_sorts():
    assert Pin(num=1) < Pin(num=2)
    assert Pin(num=9) < Pin(num=10) < Pin(num=11)
    assert Pin(num="1") < Pin(num="2")
    assert Pin(num="9") < Pin(num="10") < Pin(num="11")
    assert Pin(num="1") < Pin(num=2)
    assert Pin(num="9") < Pin(num=10) < Pin(num="11")
    with pytest.raises(ValueError):
        Pin(num=1) < Pin(num=2, part="newpart")


def test_alphanum_sorts():
    assert Pin(num=1) < Pin(num="a1")
    assert Pin(num="a1") < Pin(num="a2")
    assert Pin(num="a100") < Pin(num="b1")
    assert Pin(num="a001") == Pin(num="a1")
    assert Pin(num="AA100") > Pin(num="A1000")


def test_pin_search_1():
    mem = Part("Memory_RAM", "AS4C4M16SA")
    bidir = mem.get_pins(func=Pin.BIDIR)
    input = mem.get_pins(func=Pin.INPUT)
    passive = mem.get_pins(func=Pin.PASSIVE)
    nc = mem.get_pins(func=Pin.NOCONNECT)
    pwrin = mem.get_pins(func=Pin.PWRIN)
    assert len(bidir) == 16
    assert len(pwrin) == 4
    assert len(bidir) + len(pwrin) + len(input) + len(passive) + len(nc) == len(mem)
