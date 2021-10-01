# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import Part, Net, Bus

from .setup_teardown import setup_function, teardown_function


def test_iters_1():
    """Test bus iterator."""
    b_size = 4
    b = Bus("chplx", b_size)
    for hi in b:
        for lo in b:
            if hi != lo:
                led = Part("Device", "LED")
                hi += led["A"]
                lo += led["K"]
    for l in b:
        assert len(l) == 2 * (b_size - 1)


def test_iters_2():
    """Test pin iterator."""
    q = Part("Device", "Q_NPN_CEB")
    s = 0
    for p1 in q:
        for p2 in q:
            if p1 != p2:
                s += 1
    assert s == len(q) * (len(q) - 1)


def test_iters_3():
    """Test net iterator."""
    b = Net()
    for hi in b:
        for lo in b:
            if hi != lo:
                led = Part("Device", "LED")
                hi += led["A"]
                lo += led["K"]
    for l in b:
        assert len(l) == 0
