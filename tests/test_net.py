import pytest
from skidl import *
from .setup_teardown import *

def test_nets_1():
    gnd = Net('GND')
    a = Net('A')
    b = Net('B')
    c = Net()
    p = Pin()
    assert len(default_circuit.get_nets()) == 0
    assert len(a) == 0
    assert len(b) == 0
    assert len(c) == 0
    a += p
    assert len(default_circuit.get_nets()) == 1
    assert len(a) == 1
    assert len(b) == 0
    assert len(c) == 0

def test_net_get_pull_1():
    net1 = Net.get('test_net')
    assert net1 is None
    net2 = Net.pull('test_net')
    assert isinstance(net2, Net)
    assert len(default_circuit.nets) == 2  # NOCONNECT net is always there.
    net3 = Net.get('test_net')
    assert id(net3) == id(net2)
    assert len(default_circuit.nets) == 2  # No new net should have been created.

