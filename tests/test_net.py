import pytest
from skidl import *
from .setup_teardown import *

def test_nets_1():
    gnd = Net('GND')
    a = Net('A')
    b = Net('B')
    c = Net()
    p = Pin()
    assert len(default_circuit._get_nets()) == 0
    assert len(a) == 0
    assert len(b) == 0
    assert len(c) == 0
    a += p
    assert len(default_circuit._get_nets()) == 1
    assert len(a) == 1
    assert len(b) == 0
    assert len(c) == 0
