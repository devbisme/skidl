import pytest
from skidl import *
from .setup_teardown import *

def test_bus_1():
    # Make a bus.
    bus = Bus('BB', 11, 5)
    assert len(bus) == 16


def test_bus_2():
    # Make a bus from nets.
    gnd = Net('GND')
    a = Net('A')
    b = Net('B')
    c = Net()
    bus = Bus('BB', a, b, c)
    assert len(bus) == 3
    assert len(default_circuit.nets) == 0


def test_bus_3():
    # Make a bus from ints and nets.
    gnd = Net('GND')
    a = Net('A')
    b = Net('B')
    c = Net()
    bus = Bus('BB', a, 5, b, c)
    assert len(bus) == 8
    assert len(default_circuit.nets) == 0


def test_bus_4():
    # Make a bus from ints, nets and buses.
    gnd = Net('GND')
    a = Net('A')
    b = Net('B')
    c = Net()
    bus1 = Bus('AA', a, c, 2)
    assert len(bus1) == 4
    bus1.name = 'AA'
    assert bus1.name == 'AA'
    bus2 = Bus('BB', b, bus1, 3)
    assert len(bus2) == len(bus1) + 4
    assert len(default_circuit.nets) == 0


def test_bus_5():
    # Connect a pin to a bus line.
    gnd = Net('GND')
    a = Net('A')
    b = Net('B')
    c = Net()
    bus = Bus('AA', a, a, 2)
    assert len(bus) == 4
    p = Pin()
    a += p
    assert isinstance(bus[0], Net)
    bus[0] += p
    assert len(a) == 1
    assert len(bus[0]) == 1
    assert len(bus[1]) == 1
    assert len(default_circuit.nets) == 1


def test_bus_6():
    # Check bus line names.
    bus_prefix = 'AA'
    net = Net()
    pin = Pin()
    bus = Bus(bus_prefix, 4, net, 3, pin, 4)
    assert len(bus) == 13
    for i, n in enumerate(bus._get_nets()):
        assert bus_prefix + str(i) == n.name
    net.name = 'a'
    for i, n in enumerate(bus._get_nets()):
        if i == 4:
            assert net.name == n.name
        else:
            assert bus_prefix + str(i) == n.name


def test_bus_7():
    # Test bus connections.
    net = Net()
    pin = Pin()
    bus = Bus('AA', 2)
    net += pin
    net += bus[1]
    assert len(net) == 1


def test_bus_8():
    bus1 = Bus('A', 8)
    assert isinstance(bus1, Bus)
    nets = [Net() for _ in bus1.nets]
    for n in nets:
        n += Pin()
    bus1 += nets
    assert isinstance(bus1, Bus)
    bus2 = Bus('B', 8)
    assert isinstance(bus2, Bus)
    bus1 += bus2
    assert len(default_circuit._get_nets()) == len(bus1)


def test_bus_9():
    bus1 = Bus('A', 8)
    bus2 = Bus('B', 8)
    bus2 += 8 * Pin()
    bus1 += bus2[7:0]
    assert len(default_circuit._get_nets()) == len(bus1)


def test_bus_10():
    bus1 = Bus('A', 8)
    bus2 = Bus('B', 9)
    with pytest.raises(Exception):
        bus1 += bus2


def test_bus_11():
    bus1 = Bus('A', 8)
    bus2 = Bus('B', 9)
    with pytest.raises(Exception):
        bus2 += bus1


def test_bus_12():
    bus1 = Bus('A', 8)
    with pytest.raises(Exception):
        bus1[5:0] = 6 * Pin()


def test_bus_13():
    bus1 = Bus('A', 8)
    bus1 += 8 * Pin()
    with pytest.raises(Exception):
        bus1[5:0] = 6 * Pin()

def test_bus_14():
    bus1 = Bus('A',8)
    p1, p2 = 2 * Pin()
    p2 += bus1[5]
    p1 += p2
    p3 = Pin()
    bus1[5] += p3

def test_bus_15():
    bus1 = Bus('A', 8)
    nets = bus1[:][::-1]
    for n, i in zip(nets, range(8)[::-1]):
        assert 'A'+str(i) == n.name
