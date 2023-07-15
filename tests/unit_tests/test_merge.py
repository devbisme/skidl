# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import Net, Pin

from .setup_teardown import setup_function, teardown_function


def test_net_merge_1():
    a = Net("A")
    b = Net("B")
    a += Pin(), Pin(), Pin(), Pin(), Pin()
    assert len(a) == 5
    b += Pin(), Pin(), Pin()
    assert len(b) == 3
    a += b
    assert len(a) == 8
