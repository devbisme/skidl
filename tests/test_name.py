# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import BUS_PREFIX, NET_PREFIX, Bus, Net, Part, Pin

from .setup_teardown import setup_function, teardown_function


def test_name_1():
    vreg1 = Part("xess.lib", "1117")
    assert vreg1.ref == "U1"
    vreg1.ref = "U1"
    assert vreg1.ref == "U1"
    bus1 = Bus(None)
    assert bus1.name == BUS_PREFIX + "1"
    bus1 = Bus("T1")
    assert bus1.name == "T1"
    bus1.name = "T1"
    assert bus1.name == "T1"
    net1 = Net(None)
    assert net1.name == NET_PREFIX + "1"
    net1 = Net("N1")
    assert net1.name == "N1"
    net1.name = "N1"
    assert net1.name == "N1"


def test_name_2():
    b = Bus("A", 2)
    for n in b:
        n += Pin()
    n = Net("A0")
    n += Pin()
    net_names = [n.name for n in default_circuit.nets]
    unique_net_names = set(net_names)
    assert len(unique_net_names) == len(net_names)


def test_name_3():
    n = Net("A0")
    n += Pin()
    b = Bus("A", 2)
    for n in b:
        n += Pin()
    net_names = [n.name for n in default_circuit.nets]
    unique_net_names = set(net_names)
    assert len(unique_net_names) == len(net_names)


def test_name_4():
    l = 30
    for _ in range(l):
        n = Net()
    assert len(default_circuit.nets) == l + 1  # Account for NC net.


def test_name_5():
    from random import shuffle

    l = 30
    lst = list(range(100))
    k = 10
    shuffle(lst)
    for i in lst[:k]:
        n = Net(i)
    for _ in range(l):
        n = Net()
    assert len(default_circuit.nets) == l + k + 1  # Account for NC net.


def test_name_6():
    # Test that net and part naming don't affect each other.
    net_r1 = Net("R1")
    r1 = Part("Device", "R")
    r2 = Part("Device", "R")
    assert net_r1.name == "R1"
    assert r1.ref == "R1"
    assert r2.ref == "R2"
    r3 = Part("Device", "R", ref="R2")
    assert r3.ref == "R2_1"
    net_r2 = Net("R1")
    assert net_r2.name == "R1_1"
