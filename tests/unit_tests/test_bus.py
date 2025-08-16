# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Bus, Net, Pin, NetClass, Part, SubCircuit


def test_bus_1():
    # Test creating a bus with a specified range.
    bus = Bus("BB", 11, 5)
    # Check if the bus length is correct.
    assert len(bus) == 16


def test_bus_2():
    # Test creating a bus from individual nets.
    gnd = Net("GND")
    a = Net("A")
    b = Net("B")
    c = Net()
    bus = Bus("BB", a, b, c)
    # Check if the bus length is correct.
    assert len(bus) == 3
    # Ensure no nets are added to the default circuit.
    assert len(default_circuit.get_nets()) == 0


def test_bus_3():
    # Test creating a bus from a mix of integers and nets.
    gnd = Net("GND")
    a = Net("A")
    b = Net("B")
    c = Net()
    bus = Bus("BB", a, 5, b, c)
    # Check if the bus length is correct.
    assert len(bus) == 8
    # Ensure no nets are added to the default circuit.
    assert len(default_circuit.get_nets()) == 0


def test_bus_4():
    # Test creating a bus from integers, nets, and other buses.
    gnd = Net("GND")
    a = Net("A")
    b = Net("B")
    c = Net()
    bus1 = Bus("AA", a, c, 2)
    # Check if the bus length is correct.
    assert len(bus1) == 4
    bus1.name = "AA"
    # Verify the bus name.
    assert bus1.name == "AA"
    bus2 = Bus("BB", b, bus1, 3)
    # Check if the bus length is correct.
    assert len(bus2) == len(bus1) + 4
    # Ensure no nets are added to the default circuit.
    assert len(default_circuit.get_nets()) == 0


def test_bus_5():
    # Test connecting a pin to a bus line.
    gnd = Net("GND")
    a = Net("A")
    b = Net("B")
    c = Net()
    bus = Bus("AA", a, a, 2)
    # Check if the bus length is correct.
    assert len(bus) == 4
    p = Pin()
    a += p
    # Verify the bus element type.
    assert isinstance(bus[0], Net)
    bus[0] += p
    # Check the net length.
    assert len(a) == 1
    # Check the bus line length.
    assert len(bus[0]) == 1
    # Check the bus line length.
    assert len(bus[1]) == 1
    # Ensure one net is added to the default circuit.
    assert len(default_circuit.get_nets()) == 1


def test_bus_6():
    # Test bus line names.
    bus_prefix = "AA"
    net = Net()
    pin = Pin()
    bus = Bus(bus_prefix, 4, net, 3, pin, 4)
    # Check if the bus length is correct.
    assert len(bus) == 13
    for i, n in enumerate(bus.nets):
        # Verify the bus line names.
        assert bus_prefix + str(i) == n.name
    net.name = "a"
    for i, n in enumerate(bus.nets):
        if i == 4:
            # Verify the net name.
            assert net.name == n.name
        else:
            # Verify the bus line names.
            assert bus_prefix + str(i) == n.name


def test_bus_7():
    # Test bus connections.
    net = Net()
    pin = Pin()
    bus = Bus("AA", 2)
    net += pin
    net += bus[1]
    # Check the #pins on the net.
    assert len(net) == 1
    # Check the #pins on the bus line.
    assert len(bus[1]) == 1


def test_bus_8():
    # Test adding nets to a bus.
    bus1 = Bus("A", 8)
    # Verify the bus type.
    assert isinstance(bus1, Bus)
    nets = [Net() for _ in bus1.nets]
    for n in nets:
        n += Pin()
    bus1 += nets
    # Verify the bus type.
    assert isinstance(bus1, Bus)
    bus2 = Bus("B", 8)
    # Verify the bus type.
    assert isinstance(bus2, Bus)
    bus1 += bus2
    # Ensure the correct number of nets are added to the default circuit.
    assert len(default_circuit.get_nets()) == len(bus1)


def test_bus_9():
    # Test adding reversed bus to another bus.
    bus1 = Bus("A", 8)
    bus2 = Bus("B", 8)
    bus2 += 8 * Pin()
    bus1 += bus2[7:0]
    # Ensure the correct number of nets are added to the default circuit.
    assert len(default_circuit.get_nets()) == len(bus1)


def test_bus_10():
    # Test adding buses of different lengths.
    bus1 = Bus("A", 8)
    bus2 = Bus("B", 9)
    # Ensure ValueError is raised when adding buses of different lengths.
    with pytest.raises(ValueError):
        bus1 += bus2


def test_bus_11():
    # Test adding buses of different lengths in reverse order.
    bus1 = Bus("A", 8)
    bus2 = Bus("B", 9)
    # Ensure ValueError is raised when adding buses of different lengths.
    with pytest.raises(ValueError):
        bus2 += bus1


def test_bus_12():
    # Test assigning pins to a bus slice.
    bus1 = Bus("A", 8)
    # Ensure TypeError is raised when assigning pins to a bus slice.
    with pytest.raises(TypeError):
        bus1[5:0] = 6 * Pin()


def test_bus_13():
    # Test assigning pins to a bus slice after adding pins.
    bus1 = Bus("A", 8)
    bus1 += 8 * Pin()
    # Ensure TypeError is raised when assigning pins to a bus slice.
    with pytest.raises(TypeError):
        bus1[5:0] = 6 * Pin()


def test_bus_14():
    # Test connecting pins to a bus line.
    bus1 = Bus("A", 8)
    p1, p2 = 2 * Pin()
    p2 += bus1[5]
    p1 += p2
    p3 = Pin()
    bus1[5] += p3


def test_bus_15():
    # Test reversing a bus.
    bus1 = Bus("A", 8)
    nets = bus1[:][::-1]
    for n, i in zip(nets, range(8)[::-1]):
        # Verify the bus line names after reversing.
        assert "A" + str(i) == n.name


def test_bus_copy_1():
    # Test copying a bus.
    bus1 = Bus("A", 8)
    bus2 = bus1()
    # Check if the bus length is correct after copying.
    assert len(bus1) == len(bus2)


def test_bus_get_pull_1():
    # Test getting and fetching a bus.
    bus1 = Bus.get("test_bus")
    # Ensure the bus is not found initially.
    assert bus1 is None
    bus2 = Bus.fetch("test_bus")
    # Verify the bus type.
    assert isinstance(bus2, Bus)
    # Ensure one bus is added to the default circuit.
    assert len(default_circuit.buses) == 1
    bus3 = Bus.get("test_bus")
    # Ensure the fetched bus is the same as the created bus.
    assert id(bus3) == id(bus2)
    # Ensure no additional buses are added to the default circuit.
    assert len(default_circuit.buses) == 1


def test_bus_netclass_1():
    """Test assigning netclass to a bus."""
    led = Part("Device", "LED_ARBG")
    b1 = Bus(4)
    b1 += led[1, 2, 3, 4]  # Attach LED pins to the bus.
    b1.netclasses = NetClass("my_net", a=1, b=2, c=3, priority=1)  # Assign netclass.
    assert "my_net" in b1.netclasses
    for n in b1:
        assert "my_net" in n.netclasses

def test_bus_netclass_2():
    """Test reassigning netclass to a bus."""
    led = Part("Device", "LED_ARBG")
    b1 = Bus(4)
    b1 += led[1, 2, 3, 4]  # Attach LED pins to the bus.
    b1.netclasses = NetClass("my_net", a=1, b=2, c=3, priority=1)  # Assign netclass.
    with pytest.raises(ValueError):
        b1.netclasses = NetClass("my_net", a=5, b=6, c=7, priority=1)  # Reassign netclass should raise error.

def test_bus_netclass_3():
    """Test merging buses with different netclasses."""
    b1, b2 = Bus("a", 4), Bus("b", 4)
    b1.netclasses = NetClass("class1", priority=1)  # Assign netclass to n1.
    b2.netclasses = NetClass("class2", priority=2)  # Assign netclass to n2.
    b1 += b2  # Merge nets.
    for n in b1:
        assert set(n.netclasses) == {"class1", "class2"}
    for n in b2:
        assert set(n.netclasses) == {"class1", "class2"}
    assert b1.netclasses == b2.netclasses  # Netclass should be the same after merging.
    assert {"class1", "class2"} == set(b1.netclasses)
    assert {"class1", "class2"} == set(b2.netclasses)

def test_bus_netclass_4():
    """Test netclass multiple assignment."""
    b1 = Bus("b", 4)
    b1.netclasses = NetClass("class1", priority=1), NetClass("class2", priority=2)
    assert set(b1.netclasses) == {"class1", "class2"}

def test_bus_netclass_5():
    """Test netclass for bus surrounded by hierarchical net classes."""
    # Create a hierarchical net class.
    default_circuit.root.netclasses = NetClass("class0", priority=0)
    with SubCircuit("lvl0", netclasses=NetClass("class1",priority=1)):
        outer_bus = Bus("outer", 4)
        with SubCircuit("lvl1"):
            with SubCircuit("lvl2", netclasses=NetClass("class3",priority=3)):
                inner_bus = Bus("inner", 4)
                inner_bus.netclasses = NetClass("class2", priority=2)
                netclasses = inner_bus.netclasses.by_priority()
                assert netclasses == ["class0", "class1", "class2", "class3"]
        netclasses = outer_bus.netclasses.by_priority()
        assert netclasses == ["class0", "class1"]
    assert set(default_circuit.netclasses) == {"class0", "class1", "class2", "class3"}
