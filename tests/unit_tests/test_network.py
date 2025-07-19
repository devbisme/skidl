# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import TEMPLATE, Net, Network, Part, tee


def test_ntwk_1():
    """Test a common-emitter amplifier."""
    # Create two resistors and a transistor.
    r1, r2 = Part("Device", "R", dest=TEMPLATE) * 2
    try:
        q1 = Part("Device", "Q_NPN_EBC")
    except ValueError:
        q1 = Part("Transistor_BJT", "Q_NPN_EBC")

    # Connect the components to form the amplifier circuit.
    Net("5V") & r1 & Net("OUTPUT") & q1["C,E"] & Net("GND")
    Net.fetch("5V") & r2 & q1.B & Net("INPUT")
    
    # Perform assertions to verify the circuit.
    assert len(default_circuit.get_nets()) == 4
    assert len(q1.C.nets[0]) == 2
    assert len(q1.B.nets[0]) == 2
    assert len(q1.E.nets[0]) == 1
    assert len(Net.fetch("5V")) == 2
    assert len(Net.fetch("GND")) == 1


def test_ntwk_2():
    """Test a resistor and diode in parallel with another resistor."""
    # Create two resistors and a diode.
    r1, r2 = Part("Device", "R", dest=TEMPLATE) * 2
    d1 = Part("Device", "D")
    
    # Connect the components to form the parallel circuit.
    Net("5V") & ((r1 & d1["A,K"]) | r2) & Net("GND")
    
    # Perform assertions to verify the circuit.
    assert len(default_circuit.get_nets()) == 3
    assert len(d1.A.nets[0]) == 2
    assert len(d1.K.nets[0]) == 2
    assert len(r1.p2.nets[0]) == 2
    assert len(Net.fetch("5V")) == 2
    assert len(Net.fetch("GND")) == 2


def test_ntwk_3():
    """Test cascaded resistor dividers."""
    def r_div():
        """Create a resistor divider."""
        r1, r2 = Part("Device", "R", dest=TEMPLATE) * 2
        return r1 & (r2 & Net.fetch("GND"))[0]

    # Connect multiple resistor dividers in cascade.
    Net("inp") & r_div() & r_div() & r_div() & Net("outp")
    
    # Perform assertions to verify the circuit.
    assert len(default_circuit.get_nets()) == 5
    assert len(Net.fetch("inp")) == 1
    assert len(Net.fetch("outp")) == 2


def test_ntwk_4():
    """Test limit on network length with a single transistor."""
    # Create a transistor.
    try:
        q1 = Part("Device", "Q_NPN_EBC")
    except ValueError:
        q1 = Part("Transistor_BJT", "Q_NPN_EBC")

    # Expect a ValueError when creating a network with the transistor.
    with pytest.raises(ValueError):
        Network(q1)


def test_ntwk_5():
    """Test limit on network length with a sliced transistor."""
    # Create a transistor.
    try:
        q1 = Part("Device", "Q_NPN_EBC")
    except ValueError:
        q1 = Part("Transistor_BJT", "Q_NPN_EBC")

    # Expect a ValueError when creating a network with a sliced transistor.
    with pytest.raises(ValueError):
        Network(q1[:])


def test_ntwk_6():
    """Test limit on network length with resistors and a transistor."""
    # Create two resistors and a transistor.
    r1, r2 = Part("Device", "R", dest=TEMPLATE) * 2
    try:
        q1 = Part("Device", "Q_NPN_EBC")
    except ValueError:
        q1 = Part("Transistor_BJT", "Q_NPN_EBC")

    # Expect a ValueError when creating a network with the components.
    with pytest.raises(ValueError):
        (r1 | r2) & q1


def test_ntwk_7():
    """Test the tee() function."""
    # Create five resistors.
    r1, r2, r3, r4, r5 = Part("Device", "R", dest=TEMPLATE) * 5
    
    # Create two nets.
    vi, gnd = Net("VI"), Net("GND")
    
    # Connect the components using the tee() function.
    ntwk = vi & r1 & r2 & tee(r3 & r4 & gnd) & r5 & gnd
    
    # Perform assertions to verify the circuit.
    assert len(r3[1].nets[0]) == 3
    assert len(r2[2].nets[0]) == 3
    assert len(r5[1].nets[0]) == 3
    assert len(gnd.pins) == 2
