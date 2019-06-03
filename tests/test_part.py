import logging

import pytest

from skidl import *

from .setup_teardown import *


def test_part_1():
    vreg = Part("xess.lib", "1117")
    n = Net()
    # Connect all the part pins to a net...
    for pin in vreg:
        n += pin
    # Then see if the number of pins on the net equals the number of part pins.
    assert len(n) == len(vreg)


def test_part_2():
    vreg = Part("xess.lib", "1117")
    codec = Part("xess.lib", "ak4520a")
    parts = Part.get("u1")
    assert len(parts) == 1
    parts = Part.get("ak4520a")
    assert len(parts) == 1
    parts = Part.get(".*")
    assert len(parts) == 2
