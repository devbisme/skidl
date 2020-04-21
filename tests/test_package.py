import pytest

from skidl import *

from .setup_teardown import *


def test_package_1():
    """Test package replication and interconnection."""

    @package
    def resdiv(gnd, vin, vout):
        res = Part("Device", "R", dest=TEMPLATE)
        r1 = res(value="1k")
        r2 = res(value="500")

        cap = Part("Device", "C", dest=TEMPLATE)
        c1 = cap()
        c2 = cap(value="1uF")

        bus1 = Bus("BB", 10)

        vin += r1[1], c1[1]  # Connect the input to the first resistor.
        gnd += r2[2], c2[2]  # Connect the second resistor to ground.
        vout += (
            r1[2],
            c1[2],
            r2[1],
            c2[1],
        )  # Output comes from the connection of the two resistors.

    resdiv1 = resdiv()
    resdiv2 = resdiv()

    vin, vout, gnd = Net("VI"), Net("VO"), Net("GND")

    resdiv1.gnd += gnd
    resdiv1.vin += vin
    resdiv1.vout += vout

    resdiv2["gnd"] += gnd
    resdiv2["vin"] += vin
    resdiv2["vout"] += vout

    gnd += Pin()
    vin += Pin()

    default_circuit.instantiate_packages()

    assert len(Net.fetch("GND")) == 5
    assert len(Net.fetch("VI")) == 5
    assert len(Net.fetch("VO")) == 8

    assert len(resdiv1.gnd) == 5
    assert len(resdiv1.vin) == 5
    assert len(resdiv1.vout) == 8

    assert len(resdiv2["gnd"]) == 5
    assert len(resdiv2["vin"]) == 5
    assert len(resdiv2["vout"]) == 8


def test_package_2():
    """Test nested packages and interconnection."""

    @package
    def rc_rc(gnd, vin, vout):
        @package
        def rc(gnd, vin, vout):
            r = Part("Device", "R")
            c = Part("Device", "C")
            vin & r & vout & c & gnd

        stage1 = rc()
        stage2 = rc()

        stage1.vin += vin
        stage1.vout += Net()
        stage2.vin += stage1.vout
        stage2.vout += vout
        stage1.gnd += gnd
        stage2.gnd += gnd

    rc_rc_1 = rc_rc()
    rc_rc_2 = rc_rc()

    rc_rc_1.vin += Net("VI")
    rc_rc_1.vout += Net()
    rc_rc_2.vin += rc_rc_1.vout
    rc_rc_2.vout += Net("VO")
    rc_rc_1.gnd += Net("GND")
    rc_rc_2.gnd += rc_rc_1.gnd

    default_circuit.instantiate_packages()

    assert len(Net.fetch("GND")) == 4
    assert len(Net.fetch("VI")) == 1
    assert len(Net.fetch("VO")) == 2

    assert len(rc_rc_1.gnd) == 4
    assert len(rc_rc_1.vin) == 1
    assert len(rc_rc_1.vout) == 3

    assert len(rc_rc_2["gnd"]) == 4
    assert len(rc_rc_2["vin"]) == 3
    assert len(rc_rc_2["vout"]) == 2


def test_package_3():
    @package
    def f(a, b):
        pass

    ff = f()
    b = Bus("B", 2)
    b += Pin(), Pin()
    b += ff["a,b"]
    b[0] += Pin()
    assert len(ff.a) == 2
    assert len(ff.b) == 1
    assert len(ff["a"]) == 2
    assert len(ff["b"]) == 1


def test_package_4():
    @package
    def f(a, b):
        pass

    ff = f()
    b = Bus("B", 2)
    b += Pin(), Pin()
    ff["a,b"] += b
    b[0] += Pin()
    assert len(ff.a) == 2
    assert len(ff.b) == 1
    assert len(ff["a"]) == 2
    assert len(ff["b"]) == 1


def test_package_5():
    @package
    def f(a, b, c):
        pass

    ff = f()
    b = Bus("B", 2)
    b += Pin(), Pin()
    ff["a,b"] += b
    b[0] += Pin()
    assert len(ff.a) == 2
    assert len(ff.b) == 1
    assert len(ff.c) == 0
    assert len(ff["a"]) == 2
    assert len(ff["b"]) == 1
    assert len(ff["c"]) == 0
