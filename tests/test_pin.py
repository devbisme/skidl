# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import Part, Pin

from .setup_teardown import setup_function, teardown_function


def test_pin_names_1():
    codec = Part("xess.lib", "ak4520a")
    assert codec["ain"] == codec.n["ain"]
    assert codec[1:4] == codec.p[1:4]


def test_pin_names_2():
    codec = Part("xess.lib", "ak4520a")
    codec[4].name = "A1"
    codec[8].name = "A2"
    codec[8].num = "A1"
    assert codec[4] is codec.n["A1"]
    assert codec.p[4] is codec.n["A1"]
    assert codec[4] is codec.p[4]
    assert codec.p["A1"] is codec.n["A2"]
    assert codec["A1"] is codec.n["A2"]
    assert codec["A1"] is codec.p["A1"]


def test_numerical_pin_order():
    codec = Part("xess.lib", "ak4520a")
    p = codec.pins.pop(13)
    codec.pins.append(p)
    assert [int(x.num) for x in codec.pins] != list(range(1, len(codec.pins) + 1))
    assert [int(x.num) for x in codec.ordered_pins] == list(
        range(1, len(codec.pins) + 1)
    )


def test_alphanumeric_pin_order():
    codec = Part("xess.lib", "ak4520a")
    codec[3].num = "A1"
    codec[5].num = "B1"
    assert [p.num for p in codec.ordered_pins[-6:]] == ["25", "26", "27", "28", "A1", "B1"]


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
    codec = Part("xess.lib", "ak4520a")
    bidir = codec.get_pins(func=Pin.BIDIR)
    pwrin = codec.get_pins(func=Pin.PWRIN)
    assert len(bidir) == 24
    assert len(pwrin) == 4
    assert len(bidir) + len(pwrin) == len(codec)
