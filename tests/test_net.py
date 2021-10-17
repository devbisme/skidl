# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import Net, NetClass, Part, Pin

from .setup_teardown import setup_function, teardown_function


def test_nets_1():
    gnd = Net("GND")
    a = Net("A")
    b = Net("B")
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
    net1 = Net.get("test_net")
    assert net1 is None
    net2 = Net.fetch("test_net")
    assert isinstance(net2, Net)
    assert len(default_circuit.nets) == 2  # NOCONNECT net is always there.
    net3 = Net.get("test_net")
    assert id(net3) == id(net2)
    assert len(default_circuit.nets) == 2  # No new net should have been created.


def test_net_fixed_name_1():
    net_fixed = Net("A", fixed_name=True)
    net_merged = Net()
    net_merged += net_fixed
    for _ in range(5):
        net_merged += Net()
    default_circuit._merge_net_names()
    assert net_merged.name == "A"


def test_netclass_1():
    vreg = Part("xess.lib", "1117")
    n1 = Net()
    n1 += vreg[1, 2, 3]
    n1.netclass = NetClass("my_net", a=1, b=2, c=3)


def test_netclass_2():
    vreg = Part("xess.lib", "1117")
    n1 = Net()
    n1 += vreg[1, 2, 3]
    n1.netclass = NetClass("my_net", a=1, b=2, c=3)
    with pytest.raises(ValueError):
        n1.netclass = NetClass("my_net", a=5, b=6, c=7)


def test_netclass_3():
    n1, n2 = Net("a"), Net("b")
    n1.netclass = NetClass("class1")
    n2.netclass = NetClass("class2")
    with pytest.raises(ValueError):
        n1 += n2


def test_netclass_4():
    n1, n2 = Net("a"), Net("b")
    n1 += n2
    n1.netclass = NetClass("class1")
    assert n2.netclass.name == "class1"
    with pytest.raises(ValueError):
        n2.netclass = NetClass("class2")


def test_drive_1():
    n1, n2 = Net("a"), Net("b")
    n1.drive = 5
    n2.drive = 6
    n1 += n2
    assert n1.drive == n2.drive
    assert n1.drive == 6


def test_drive_2():
    n1, n2 = Net("a"), Net("b")
    n1.drive = 5
    n1 += n2
    assert n1.drive == n2.drive
    assert n2.drive == 5
    n1.drive = 7
    assert n2.drive == 7
