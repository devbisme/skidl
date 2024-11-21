# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Bus, Net, Part, Pin
from skidl.bus import BUS_PREFIX
from skidl.net import NET_PREFIX

from .setup_teardown import setup_function, teardown_function


def test_name_1():
    """Test naming of parts, buses, and nets."""
    # Create a resistor part and check its reference.
    r1 = Part("Device", "R")
    assert r1.ref == "R1"
    r1.ref = "R1"
    assert r1.ref == "R1"
    
    # Create a bus and check its name.
    bus1 = Bus(None)
    assert bus1.name == BUS_PREFIX + "1"
    bus1 = Bus("T1")
    assert bus1.name == "T1"
    bus1.name = "T1"
    assert bus1.name == "T1"
    
    # Create a net and check its name.
    net1 = Net(None)
    assert net1.name == NET_PREFIX + "1"
    net1 = Net("N1")
    assert net1.name == "N1"
    net1.name = "N1"
    assert net1.name == "N1"


def test_name_2():
    """Test unique naming of nets in a bus."""
    # Create a bus with 2 nets and add a pin to each net.
    b = Bus("A", 2)
    for n in b:
        n += Pin()
    
    # Create a net with the same name as one in the bus and add a pin to it.
    n = Net("A0")
    n += Pin()
    
    # Check that all net names are unique.
    net_names = [n.name for n in default_circuit.nets]
    unique_net_names = set(net_names)
    assert len(unique_net_names) == len(net_names)


def test_name_3():
    """Test unique naming of nets when mixed with bus and individual nets."""
    # Create a net and add a pin to it.
    n = Net("A0")
    n += Pin()
    
    # Create a bus with 2 nets and add a pin to each net.
    b = Bus("A", 2)
    for n in b:
        n += Pin()
    
    # Check that all net names are unique.
    net_names = [n.name for n in default_circuit.nets]
    unique_net_names = set(net_names)
    assert len(unique_net_names) == len(net_names)


def test_name_4():
    """Test the number of nets created."""
    # Create 30 nets.
    l = 30
    for _ in range(l):
        n = Net()
    
    # Check that the number of nets is 31 (including the NC net).
    assert len(default_circuit.nets) == l + 1  # Account for NC net.


def test_name_5():
    """Test the number of nets created with random names."""
    from random import shuffle

    # Create a list of 100 numbers and shuffle it.
    l = 30
    lst = list(range(100))
    k = 10
    shuffle(lst)
    
    # Create 10 nets with random names.
    for i in lst[:k]:
        n = Net(i)
    
    # Create 30 nets.
    for _ in range(l):
        n = Net()
    
    # Check that the number of nets is 41 (including the NC net).
    assert len(default_circuit.nets) == l + k + 1  # Account for NC net.


def test_name_6():
    """Test that net and part naming don't affect each other."""
    # Create a net with the name "R1".
    net_r1 = Net("R1")
    
    # Create two resistor parts.
    r1 = Part("Device", "R")
    r2 = Part("Device", "R")
    
    # Check the names of the net and parts.
    assert net_r1.name == "R1"
    assert r1.ref == "R1"
    assert r2.ref == "R2"
    
    # Create another resistor part with the same reference as an existing part.
    r3 = Part("Device", "R", ref="R2")
    assert r3.ref == "R2_1"
    
    # Create another net with the same name as an existing net.
    net_r2 = Net("R1")
    assert net_r2.name == "R1_1"
