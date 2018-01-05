import pytest
from skidl import *
from .setup_teardown import *

def test_name_1():
    vreg1 = Part('xess.lib', '1117')
    assert vreg1.ref == 'U1'
    vreg1.ref = 'U1'
    assert vreg1.ref == 'U1'
    bus1 = Bus(None)
    assert bus1.name == 'B$1'
    bus1 = Bus('B1')
    assert bus1.name == 'B1'
    bus1.name = 'B1'
    assert bus1.name == 'B1'

def test_name_2():
    b = Bus('A',2)
    for n in b:
        n += Pin()
    n = Net('A0')
    n += Pin()
    net_names = [n.name for n in default_circuit.nets]
    unique_net_names = set(net_names)
    assert len(unique_net_names) == len(net_names)

def test_name_3():
    n = Net('A0')
    n += Pin()
    b = Bus('A',2)
    for n in b:
        n += Pin()
    net_names = [n.name for n in default_circuit.nets]
    unique_net_names = set(net_names)
    assert len(unique_net_names) == len(net_names)
