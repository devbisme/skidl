# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import Part

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
    codec.pins[3].num = "A1"
    codec.pins[5].num = "B1"
    for _ in codec.pins[6:]:
        codec.pins.pop()
    assert [x.num for x in codec.ordered_pins] == ["1", "2", "3", "5", "A1", "B1"]
    assert codec.pins != codec.ordered_pins
