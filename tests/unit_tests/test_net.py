# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Net, NetClass, Part, Pin


def test_nets_1():
    """Test basic net operations."""
    gnd = Net("GND")
    a = Net("A")
    b = Net("B")
    c = Net()
    p = Pin()
    assert len(default_circuit.get_nets()) == 0  # No nets initially.
    assert len(a) == 0  # Net 'a' is empty.
    assert len(b) == 0  # Net 'b' is empty.
    assert len(c) == 0  # Net 'c' is empty.
    a += p  # Add pin to net 'a'.
    assert len(default_circuit.get_nets()) == 1  # One net in the circuit.
    assert len(a) == 1  # Net 'a' has one pin.
    assert len(b) == 0  # Net 'b' is still empty.
    assert len(c) == 0  # Net 'c' is still empty.


def test_net_get_pull_1():
    """Test getting and fetching nets."""
    net1 = Net.get("test_net")
    assert net1 is None  # Net 'test_net' does not exist.
    net2 = Net.fetch("test_net")
    assert isinstance(net2, Net)  # Net 'test_net' is created.
    assert len(default_circuit.nets) == 2  # NOCONNECT net is always there.
    net3 = Net.get("test_net")
    assert id(net3) == id(net2)  # Same net object.
    assert len(default_circuit.nets) == 2  # No new net should have been created.


def test_net_fixed_name_1():
    """Test net with fixed name."""
    net_fixed = Net("A", fixed_name=True)
    net_merged = Net()
    net_merged += net_fixed  # Merge fixed name net.
    for _ in range(5):
        net_merged += Net()  # Merge additional nets.
    default_circuit.merge_net_names()
    assert net_merged.name == "A"  # Name should remain 'A'.


def test_netclass_1():
    """Test assigning netclass to a net."""
    led = Part("Device", "LED_ARBG")
    n1 = Net()
    n1 += led[1, 2, 3, 4]  # Add LED pins to net.
    n1.netclass = NetClass("my_net", a=1, b=2, c=3, priority=1)  # Assign netclass.


def test_netclass_2():
    """Test reassigning netclass to a net."""
    led = Part("Device", "LED_ARBG")
    n1 = Net()
    n1 += led[1, 2, 3, 4]  # Add pins to net.
    n1.netclass = NetClass("my_net", a=1, b=2, c=3, priority=2)  # Assign netclass.
    with pytest.raises(KeyError):
        n1.netclass = NetClass("my_net", a=5, b=6, c=7, priority=1)  # Reassign netclass should raise error.


def test_netclass_3():
    """Test merging nets with different netclasses."""
    n1, n2 = Net("a"), Net("b")
    n1.netclass = NetClass("class1", priority=1)  # Assign netclass to n1.
    n2.netclass = NetClass("class2", priority=2)  # Assign netclass to n2.
    n1 += n2  # Merge nets.
    assert n1.netclass == n2.netclass  # Netclass should be the same after merging.
    assert len(n1.netclass) == 2
    nt_cls_names = list(default_circuit.netclasses)
    assert "class1" in nt_cls_names  # Netclass 'class1' should be present.
    assert "class2" in nt_cls_names  # Netclass 'class2' should also be present.


def test_netclass_4():
    """Test netclass propagation after merging nets."""
    n1, n2 = Net("a"), Net("b")
    n1 += n2  # Merge nets.
    n1.netclass = NetClass("class1", priority=1)  # Assign netclass to merged net.
    assert n2.netclass[0].name == "class1"  # Netclass should propagate.
    n2.netclass = NetClass("class2", priority=2)  # Adding another netclass.
    assert len(n2.netclass) == 2  # Netclass list should contain both netclasses.
    assert len(n1.netclass) == 2  # Netclass list should propagate to connected net.
    nt_cls_names = list(default_circuit.netclasses)
    assert "class1" in nt_cls_names  # Netclass 'class1' should be present.
    assert "class2" in nt_cls_names  # Netclass 'class2' should also be present.


def test_netclass_5():
    """Test netclass priority sorting."""
    n1, n2 = Net("a"), Net("b")
    n1 += n2  # Merge nets.
    n1.netclass = NetClass("class1", priority=1)  # Assign netclass to merged net.
    assert n2.netclass[0].name == "class1"  # Netclass should propagate.
    n2.netclass = NetClass("class2", priority=2)  # Adding another netclass.
    prioritized_names = n2.netclass.by_priority()  # Sort netclasses by priority.
    assert prioritized_names[-1] == "class2"  # Last netclass should be 'class2'.
    assert prioritized_names[-2] == "class1"  # First netclass should be 'class1'.
    netclasses = n1.circuit.netclasses[prioritized_names]
    assert netclasses[-1].priority == 2
    assert netclasses[-2].priority == 1


def test_netclass_6():
    """Test netclass single and multiple indexing."""
    n1 = Net("a")
    n1.netclass = NetClass("class1", priority=1)  # Assign netclass to merged net.
    n1.netclass = NetClass("class2", priority=2)  # Adding another netclass.
    netclass = n1.circuit.netclasses["class1"]
    assert netclass.priority == 1
    netclasses = n1.circuit.netclasses["class1", "class2"]
    assert netclasses[0].priority == 1
    assert netclasses[1].priority == 2


def test_netclass_7():
    """Test netclass duplication."""
    n1 = Net("a")
    ntcls1 = NetClass("class1", priority=1)
    NetClass("class1", priority=1)  # Netclass with same name and same attributes doesn't raise error.
    n1.netclass = ntcls1
    n1.netclass = ntcls1  # Reassigning should be ignored and not raise error.
    with pytest.raises(KeyError):
        NetClass("class1", priority=2)  # Netclass with same name but different attributes should raise error.


def test_drive_1():
    """Test drive strength propagation after merging nets."""
    n1, n2 = Net("a"), Net("b")
    n1.drive = 5  # Set drive strength.
    n2.drive = 6  # Set different drive strength.
    n1 += n2  # Merge nets.
    assert n1.drive == n2.drive  # Drive strength should be the same.
    assert n1.drive == 6  # Drive strength should be the higher value.


def test_drive_2():
    """Test drive strength update after merging nets."""
    n1, n2 = Net("a"), Net("b")
    n1.drive = 5  # Set drive strength.
    n1 += n2  # Merge nets.
    assert n1.drive == n2.drive  # Drive strength should be the same.
    assert n2.drive == 5  # Drive strength should be 5.
    n1.drive = 7  # Update drive strength.
    assert n2.drive == 7  # Drive strength should be updated.
