# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import TEMPLATE, Net, Network, Part, tee

from .setup_teardown import setup_function, teardown_function


def test_ntwk_1():
    """A common-emitter amplifier."""
    r1, r2 = Part("Device", "R", dest=TEMPLATE) * 2
    q1 = Part("Device", "Q_NPN_EBC")
    Net("5V") & r1 & Net("OUTPUT") & q1["C,E"] & Net("GND")
    Net.fetch("5V") & r2 & q1.B & Net("INPUT")
    assert len(default_circuit.get_nets()) == 4
    assert len(q1.C.get_nets()[0]) == 2
    assert len(q1.B.get_nets()[0]) == 2
    assert len(q1.E.get_nets()[0]) == 1
    assert len(Net.fetch("5V")) == 2
    assert len(Net.fetch("GND")) == 1


def test_ntwk_2():
    """A resistor + diode in parallel with another resistor."""
    r1, r2 = Part("Device", "R", dest=TEMPLATE) * 2
    d1 = Part("Device", "D")
    Net("5V") & ((r1 & d1["A,K"]) | r2) & Net("GND")
    assert len(default_circuit.get_nets()) == 3
    assert len(d1.A.get_nets()[0]) == 2
    assert len(d1.K.get_nets()[0]) == 2
    assert len(r1.p2.get_nets()[0]) == 2
    assert len(Net.fetch("5V")) == 2
    assert len(Net.fetch("GND")) == 2


def test_ntwk_3():
    """Cascaded resistor dividers."""

    def r_div():
        r1, r2 = Part("Device", "R", dest=TEMPLATE) * 2
        return r1 & (r2 & Net.fetch("GND"))[0]

    Net("inp") & r_div() & r_div() & r_div() & Net("outp")
    assert len(default_circuit.get_nets()) == 5
    assert len(Net.fetch("inp")) == 1
    assert len(Net.fetch("outp")) == 2


def test_ntwk_4():
    """Test limit on network length."""
    q1 = Part("Device", "Q_NPN_EBC")
    with pytest.raises(ValueError):
        Network(q1)


def test_ntwk_5():
    """Test limit on network length."""
    q1 = Part("Device", "Q_NPN_EBC")
    with pytest.raises(ValueError):
        Network(q1[:])


def test_ntwk_6():
    """Test limit on network length."""
    r1, r2 = Part("Device", "R", dest=TEMPLATE) * 2
    q1 = Part("Device", "Q_NPN_EBC")
    with pytest.raises(ValueError):
        (r1 | r2) & q1


def test_ntwk_7():
    """Test tee() function."""
    r1, r2, r3, r4, r5 = Part("Device", "R", dest=TEMPLATE) * 5
    vi, gnd = Net("VI"), Net("GND")
    ntwk = vi & r1 & r2 & tee(r3 & r4 & gnd) & r5 & gnd
    assert len(r3[1].get_nets()[0]) == 3
    assert len(r2[2].get_nets()[0]) == 3
    assert len(r5[1].get_nets()[0]) == 3
    assert len(gnd.get_pins()) == 2
