import pytest

from skidl import *

from .setup_teardown import *


def test_pin_search_1():
    codec = Part("xess.lib", "ak4520a")
    bidir = codec.get_pins(func=Pin.BIDIR)
    pwrin = codec.get_pins(func=Pin.PWRIN)
    assert len(bidir) == 24
    assert len(pwrin) == 4
    assert len(bidir) + len(pwrin) == len(codec['.*'])
