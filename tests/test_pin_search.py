# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import Part, Pin

from .setup_teardown import setup_function, teardown_function


def test_pin_search_1():
    codec = Part("xess.lib", "ak4520a")
    bidir = codec.get_pins(func=Pin.BIDIR)
    pwrin = codec.get_pins(func=Pin.PWRIN)
    assert len(bidir) == 24
    assert len(pwrin) == 4
    assert len(bidir) + len(pwrin) == len(codec)
