# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import Pin


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
    assert Pin(num="a001") < Pin(num="a1")
