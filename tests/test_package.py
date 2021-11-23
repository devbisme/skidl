# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import copy

import pytest

from skidl import TEMPLATE, Bus, Circuit, Net, Part, Pin, package, subcircuit

from .setup_teardown import setup_function, teardown_function


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

    assert len(rc_rc_2.gnd) == 4
    assert len(rc_rc_2.vin) == 3
    assert len(rc_rc_2.vout) == 2

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

    default_circuit.instantiate_packages()

    assert len(b[0]) == 2
    assert len(b[1]) == 1
    assert len(ff["a"]) == 2
    assert len(ff["b"]) == 1
    assert len(ff.a) == 2
    assert len(ff.b) == 1


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


def test_package_6():
    @package
    def reg_adj(VI, VO, GND, bom, output_voltage):
        """Create voltage regulator with adjustable output."""

        # Create adjustable regulator chip and connect to input and output.
        reg = bom["reg"]()
        reg["VI"] += VI
        reg["VO"] += VO

        # Create resistor divider and attach between output, adjust pin and ground.
        rh = bom["r"]()
        rl = bom["r"]()
        r_total = 1000
        rl.value = (1.25 / output_voltage) * r_total
        rh.value = r_total - float(rl.value)
        VO & rh & reg["ADJ"] & rl & GND

    @package
    def vreg(vin, vout, gnd, bom):
        """Create voltage regulator with filtering caps."""

        # Create regulator and attach to input, output and ground.
        reg = bom["reg"]()
        reg["VI, VO, GND"] += vin, vout, gnd

        # Attach filtering capacitors on input and output.
        cin, cout = bom["c"](2)
        vin & cin & gnd
        vout & cout & gnd

    @package
    def vreg_adj(vin, vout, gnd, bom, output_voltage=3.0):
        """Create adjustable voltage regulator with filtering caps."""
        bom2 = copy.copy(bom)
        bom2["reg"] = reg_adj(bom=bom, output_voltage=output_voltage, dest=TEMPLATE)
        vreg(vin=vin, vout=vout, gnd=gnd, bom=bom2)

    vin, vout, gnd = Net("VIN"), Net("VOUT"), Net("GND")
    reg = Part("xess.lib", "1117", dest=TEMPLATE)
    reg.GND.aliases += "ADJ"
    reg.IN.aliases += "VI"
    reg.OUT.aliases += "VO"
    bom = {
        "r": Part("Device", "R", dest=TEMPLATE),
        "c": Part("Device", "C", dest=TEMPLATE),
        "reg": reg,
    }
    vr = vreg_adj(bom=bom)
    vr["vin, vout, gnd"] += vin, vout, gnd

    default_circuit.instantiate_packages()

    assert len(vin) == 2
    assert len(gnd) == 3
    assert len(vout) == 3


def test_package_7():
    """Test multiple packages for independence."""

    @package
    def reg_adj(VI, VO, GND, bom, output_voltage):
        """Create voltage regulator with adjustable output."""

        # Create adjustable regulator chip and connect to input and output.
        reg = bom["reg"]()
        reg["VI"] += VI
        reg["VO"] += VO

        # Create resistor divider and attach between output, adjust pin and ground.
        rh = bom["r"]()
        rl = bom["r"]()
        r_total = 1000
        rl.value = (1.25 / output_voltage) * r_total
        rh.value = r_total - float(rl.value)
        VO & rh & reg["ADJ"] & rl & GND

    @package
    def vreg(vin, vout, gnd, bom):
        """Create voltage regulator with filtering caps."""

        # Create regulator and attach to input, output and ground.
        reg = bom["reg"]()
        reg["VI, VO, GND"] += vin, vout, gnd

        # Attach filtering capacitors on input and output.
        cin, cout = bom["c"](2)
        vin & cin & gnd
        vout & cout & gnd

    @package
    def vreg_adj(vin, vout, gnd, bom, output_voltage=3.0):
        """Create adjustable voltage regulator with filtering caps."""
        bom2 = copy.copy(bom)
        bom2["reg"] = reg_adj(bom=bom, output_voltage=output_voltage, dest=TEMPLATE)
        vreg(vin=vin, vout=vout, gnd=gnd, bom=bom2)

    vin, vout1, vout2, gnd = Net("VIN"), Net("VOUT1"), Net("VOUT2"), Net("GND")
    reg = Part("xess.lib", "1117", dest=TEMPLATE)
    reg.GND.aliases += "ADJ"
    reg.IN.aliases += "VI"
    reg.OUT.aliases += "VO"
    bom = {
        "r": Part("Device", "R", dest=TEMPLATE),
        "c": Part("Device", "C", dest=TEMPLATE),
        "reg": reg,
    }
    vr1 = vreg_adj(bom=bom)
    vr2 = vreg_adj(bom=bom)
    vr1["vin, vout, gnd"] += vin, vout1, gnd
    vr2["vin, vout, gnd"] += vin, vout2, gnd

    default_circuit.instantiate_packages()

    u1 = Part.get("U1")
    u2 = Part.get("U2")
    u1.F2 = "U1-F2"
    u2.F2 = "U2-F2"
    assert u1.F2 == "U1-F2"
    assert u2.F2 == "U2-F2"
    assert len(default_circuit.parts) == 10
    assert len(vout1.pins) == 3
    assert len(vout2.pins) == 3
    assert len(vin.pins) == 4
    assert len(gnd.pins) == 6
    # check decorator has not messed up docstring for subcircuits
    assert vreg_adj.subcircuit.__name__ == "vreg_adj"
    assert (
        vreg_adj.subcircuit.__doc__
        == "Create adjustable voltage regulator with filtering caps."
    )
    assert vreg.subcircuit.__name__ == "vreg"
    assert vreg.subcircuit.__doc__ == "Create voltage regulator with filtering caps."
    assert reg_adj.subcircuit.__name__ == "reg_adj"
    assert (
        reg_adj.subcircuit.__doc__ == "Create voltage regulator with adjustable output."
    )


def test_package_8():
    r = Part("Device", "R", dest=TEMPLATE)

    @package
    def r_sub(neta, netb):
        neta & r() & netb

    rr = r_sub()
    vcc, gnd = Net("VCC"), Net("GND")
    rr.neta += vcc
    gnd += rr.netb

    default_circuit.instantiate_packages()

    assert len(gnd) == 1
    assert len(vcc) == 1


def test_package_9():

    r = Part("Device", "R", dest=TEMPLATE)
    c = Part("Device", "C", dest=TEMPLATE)

    @subcircuit
    def sub1(my_vin, my_gnd):
        r1 = r()
        c1 = c()
        my_vin & r1 & c1 & my_gnd

    @package
    def sub2(my_vin1, my_vin2, my_gnd):
        sub1(my_vin1, my_gnd)
        sub1(my_vin2, my_gnd)

    vin1, vin2, gnd = Net("VIN1"), Net("VIN2"), Net("GND")
    sub = sub2()
    vin1 += sub.my_vin1
    sub.my_vin2 += vin2
    sub.my_gnd += gnd
    r1 = r()
    vin1 & r1 & gnd

    default_circuit.instantiate_packages()

    assert len(gnd) == 3
    assert len(vin1) == 2
    assert len(vin2) == 1


def test_package_10():

    r = Part("Device", "R", dest=TEMPLATE)
    c = Part("Device", "C", dest=TEMPLATE)

    @package
    def sub1(my_vin, my_gnd):
        r1 = r()
        c1 = c()
        my_vin & r1 & c1 & my_gnd

    @subcircuit
    def sub2(my_vin1, my_vin2, my_gnd):
        s1 = sub1()
        s2 = sub1()
        s1.my_vin += my_vin1
        my_vin2 += s2.my_vin
        my_gnd += s1.my_gnd
        s2.my_gnd += my_gnd

    vin1, vin2, gnd = Net("VIN1"), Net("VIN2"), Net("GND")
    sub = sub2(vin1, vin2, gnd)
    r1 = r()
    vin1 & r1 & gnd

    default_circuit.instantiate_packages()

    assert len(gnd) == 3
    assert len(vin1) == 2
    assert len(vin2) == 1


def test_package_11():
    @package
    def analog_average(in1, in2, avg):
        r1, r2 = 2 * Part("Device", "R", value="1K", dest=TEMPLATE)
        r1[1, 2] += in1, avg
        r2[1, 2] += in2, avg

    cct = Circuit(name="My circuit")

    avg1 = analog_average(circuit=cct)
    avg2 = analog_average(circuit=cct)

    in1, in2, in3, in4, out1, out2 = Net(circuit=cct) * 6
    avg1["in1"] += in1
    avg1.in2 += in2
    avg1["avg"] += out1

    avg2["in1"] += in3
    avg2["in2"] += in4
    avg2.avg += out2

    cct.generate_netlist()


def test_package_12():
    @package
    def analog_average(in1, in2, avg, circuit=None):
        r1, r2 = 2 * Part("Device", "R", value="1K", dest=TEMPLATE, circuit=circuit)
        r1[1, 2] += in1, avg
        r2[1, 2] += in2, avg

    cct = Circuit(name="My circuit")

    avg1 = analog_average(circuit=cct)
    avg2 = analog_average(circuit=cct)

    in1, in2, in3, in4, out1, out2 = Net(circuit=cct) * 6
    avg1["in1"] += in1
    avg1.in2 += in2
    avg1["avg"] += out1

    avg2["in1"] += in3
    avg2["in2"] += in4
    avg2.avg += out2

    cct.generate_netlist()


def test_package_13():
    @package
    def analog_average(in1, in2, avg, cct=None):
        r1, r2 = 2 * Part("Device", "R", value="1K", dest=TEMPLATE, circuit=cct)
        r1[1, 2] += in1, avg
        r2[1, 2] += in2, avg

    cct = Circuit(name="My circuit")

    avg1 = analog_average(circuit=cct, cct=cct)
    avg2 = analog_average(circuit=cct, cct=cct)

    in1, in2, in3, in4, out1, out2 = Net(circuit=cct) * 6

    avg1["in1"] += in1
    avg1.in2 += in2
    avg1["avg"] += out1

    avg2["in1"] += in3
    avg2["in2"] += in4
    avg2.avg += out2
    cct.generate_netlist()


def test_package_14():
    global default_circuit

    @package
    def analog_average(in1, in2, avg):
        r1, r2 = 2 * Part("Device", "R", value="1K", dest=TEMPLATE)
        r1[1, 2] += in1, avg
        r2[1, 2] += in2, avg

    cct = Circuit(name="My circuit")

    global default_circuit

    avg1 = analog_average()
    default_circuit -= avg1
    cct += avg1
    avg2 = analog_average()
    default_circuit -= avg2
    cct += avg2

    # in1, in2, in3, in4, out1, out2 = Net(circuit=cct) * 6
    in1, in2, in3, in4, out1, out2 = (
        Net("IN1", circuit=cct),
        Net("IN2", circuit=cct),
        Net("IN3", circuit=cct),
        Net("IN4", circuit=cct),
        Net("OUT1", circuit=cct),
        Net("OUT2", circuit=cct),
    )
    avg1["in1"] += in1
    avg1.in2 += in2
    avg1["avg"] += out1

    avg2["in1"] += in3
    avg2["in2"] += in4
    avg2.avg += out2

    cct.generate_netlist()
