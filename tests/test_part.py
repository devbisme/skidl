import pytest
from skidl import *
from .setup_teardown import *
import logging

def test_part_1():
    vreg = Part('xess.lib', '1117')
    n = Net()
    # Connect all the part pins to a net...
    for pin in vreg:
        n += pin
    # Then see if the number of pins on the net equals the number of part pins.
    assert(len(n) == len(vreg))
