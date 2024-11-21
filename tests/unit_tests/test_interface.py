# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import copy

import pytest

from skidl import TEMPLATE, Bus, Circuit, Interface, Net, Part, Pin, subcircuit

from .setup_teardown import setup_function, teardown_function


def test_interface_1():
    """Test interface."""

    @subcircuit
    def resdiv(gnd, vin, vout):
        """Create resistor divider."""
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

    # Create interface with nets
    intfc = Interface(
        gnd=Net("GND"),
        vin=Net("VI"),
        vout=Net("VO"),
    )

    # Add aliases to the ground net
    intfc.gnd.aliases += "GND"
    intfc.gnd.aliases += "GNDA"

    # Instantiate the resistor divider subcircuit
    resdiv(**intfc)
    resdiv(gnd=intfc.gnd, vin=intfc.vin, vout=intfc.vout)

    # Assertions to verify the circuit
    assert len(default_circuit.parts) == 8
    assert len(default_circuit.get_nets()) == 3
    assert len(default_circuit.buses) == 2

    assert len(Net.fetch("GND")) == 4
    assert len(Net.fetch("VI")) == 4
    assert len(Net.fetch("VO")) == 8

    assert len(intfc.gnd) == 4
    assert len(intfc.vin) == 4
    assert len(intfc.vout) == 8

    assert len(intfc["gnd"]) == 4
    assert len(intfc["vin"]) == 4
    assert len(intfc["vout"]) == 8

    # Add pins to the interface nets
    intfc.gnd += Pin()
    intfc["vin"] += Pin()

    # Assertions to verify the updated circuit
    assert len(Net.fetch("GND")) == 5
    assert len(Net.fetch("VI")) == 5
    assert len(Net.fetch("VO")) == 8

    assert len(intfc.gnd) == 5
    assert len(intfc.vin) == 5
    assert len(intfc.vout) == 8

    assert len(intfc["gnd"]) == 5
    assert len(intfc["vin"]) == 5
    assert len(intfc["vout"]) == 8

    assert len(intfc["GND"]) == 5
    assert len(intfc["GNDA"]) == 5


def test_interface_2():
    """Test interface with memory part."""
    mem = Part("Memory_RAM", "AS4C4M16SA")
    intf = Interface(a=mem["A[0:9]"], d=mem["DQ[0:15]"])
    assert len(intf.a) == 10
    assert len(intf["a"]) == 10
    assert len(intf.a[0:9]) == 10
    assert len(intf["a[0:9]"]) == 10
    assert len(intf["a d"]) == len(intf.a) + len(intf.d)
    intf["a d"] += Net()
    intf.a += Net()
    c = Net()
    c += intf["a d"]
    intf["a d"] += Bus(5), Net(), Bus(10), Net(), Net(), Bus(8)
    intf["a[3:7] d[4:1]"] += Bus(5), Net(), Net(), Bus(1), Net()
    d = Bus(6)
    d += intf["d[4:5] a[7:4]"]


def test_interface_3():
    """Test package replication and interconnection."""

    @subcircuit
    def resdiv():
        """Create resistor divider."""
        gnd, vin, vout = Net(), Net(), Net()
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

        return Interface(vin=vin, vout=vout, gnd=gnd)

    # Instantiate two resistor divider subcircuits
    resdiv1 = resdiv()
    resdiv2 = resdiv()

    # Create nets
    vin, vout, gnd = Net("VI"), Net("VO"), Net("GND")

    # Connect the subcircuits to the nets
    resdiv1.gnd += gnd
    resdiv1.vin += vin
    resdiv1.vout += vout

    resdiv2["gnd"] += gnd
    resdiv2["vin"] += vin
    resdiv2["vout"] += vout

    # Add pins to the nets
    gnd += Pin()
    vin += Pin()

    # Assertions to verify the circuit
    assert len(Net.fetch("GND")) == 5
    assert len(Net.fetch("VI")) == 5
    assert len(Net.fetch("VO")) == 8

    assert len(resdiv1.gnd) == 5
    assert len(resdiv1.vin) == 5
    assert len(resdiv1.vout) == 8

    assert len(resdiv2["gnd"]) == 5
    assert len(resdiv2["vin"]) == 5
    assert len(resdiv2["vout"]) == 8


def test_interface_4():
    """Test nested subcircuits."""

    @subcircuit
    def rc_rc():
        """Create two-stage RC filter."""
        gnd, vin, vout = Net(), Net(), Net()

        @subcircuit
        def rc():
            """Create RC filter stage."""
            gnd, vin, vout = Net(), Net(), Net()
            r = Part("Device", "R")
            c = Part("Device", "C")
            vin & r & vout & c & gnd
            return Interface(gnd=gnd, vin=vin, vout=vout)

        # Instantiate two RC filter stages
        stage1 = rc()
        stage2 = rc()

        # Connect the stages
        stage1.vin += vin
        stage1.vout += Net()
        stage2.vin += stage1.vout
        stage2.vout += vout
        stage1.gnd += gnd
        stage2.gnd += gnd

        return Interface(gnd=gnd, vin=vin, vout=vout)

    # Instantiate two two-stage RC filters
    rc_rc_1 = rc_rc()
    rc_rc_2 = rc_rc()

    # Connect the filters to nets
    rc_rc_1.vin += Net("VI")
    rc_rc_1.vout += Net()
    rc_rc_2.vin += rc_rc_1.vout
    rc_rc_2.vout += Net("VO")
    rc_rc_1.gnd += Net("GND")
    rc_rc_2.gnd += rc_rc_1.gnd

    # Assertions to verify the circuit
    assert len(Net.fetch("GND")) == 4
    assert len(Net.fetch("VI")) == 1
    assert len(Net.fetch("VO")) == 2

    assert len(rc_rc_1.gnd) == 4
    assert len(rc_rc_1.vin) == 1
    assert len(rc_rc_1.vout) == 3

    assert len(rc_rc_2["gnd"]) == 4
    assert len(rc_rc_2["vin"]) == 3
    assert len(rc_rc_2["vout"]) == 2


def test_interface_5():
    """Test interface with bus."""

    @subcircuit
    def f():
        """Create interface with two nets."""
        a, b = Net(), Net()
        return Interface(a=a, b=b)

    # Instantiate the subcircuit
    ff = f()
    b = Bus("B", 2)
    b += Pin(), Pin()
    b += ff["a,b"]
    b[0] += Pin()

    # Assertions to verify the interface
    assert len(ff.a) == 2
    assert len(ff.b) == 1
    assert len(ff["a"]) == 2
    assert len(ff["b"]) == 1


def test_interface_6():
    """Test interface with bus and nets."""

    @subcircuit
    def f():
        """Create interface with two nets."""
        a, b = Net(), Net()
        return Interface(a=a, b=b)

    # Instantiate the subcircuit
    ff = f()
    b = Bus("B", 2)
    b += Pin(), Pin()
    ff["a,b"] += b
    b[0] += Pin()

    # Assertions to verify the interface
    assert len(ff.a) == 2
    assert len(ff.b) == 1
    assert len(ff["a"]) == 2
    assert len(ff["b"]) == 1


def test_interface_7():
    """Test interface with three nets."""

    @subcircuit
    def f():
        """Create interface with three nets."""
        a, b, c = Net(), Net(), Net()
        return Interface(a=a, b=b, c=c)

    # Instantiate the subcircuit
    ff = f()
    b = Bus("B", 2)
    b += Pin(), Pin()
    ff["a,b"] += b
    b[0] += Pin()

    # Assertions to verify the interface
    assert len(ff.a) == 2
    assert len(ff.b) == 1
    assert len(ff.c) == 0
    assert len(ff["a"]) == 2
    assert len(ff["b"]) == 1
    assert len(ff["c"]) == 0


def test_interface_8():
    """Test adjustable voltage regulator."""

    @subcircuit
    def reg_adj(bom, output_voltage):
        """Create voltage regulator with adjustable output."""
        VI, VO, GND = 3 * Net()

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

        return Interface(VI=VI, VO=VO, GND=GND)

    @subcircuit
    def vreg(vin, vout, gnd, bom):
        """Create voltage regulator with filtering caps."""
        # Create regulator and attach to input, output and ground.
        reg = bom["reg"]
        reg["VI, VO, GND"] += vin, vout, gnd

        # Attach filtering capacitors on input and output.
        cin, cout = bom["c"](2)
        vin & cin & gnd
        vout & cout & gnd

    @subcircuit
    def vreg_adj(bom, output_voltage=3.0):
        """Create adjustable voltage regulator with filtering caps."""
        vin, vout, gnd = 3 * Net()

        bom2 = copy.copy(bom)
        bom2["reg"] = reg_adj(bom=bom, output_voltage=output_voltage)
        vreg(vin=vin, vout=vout, gnd=gnd, bom=bom2)

        return Interface(vin=vin, vout=vout, gnd=gnd)

    # Create nets and parts
    vin, vout, gnd = Net("VIN"), Net("VOUT"), Net("GND")
    reg = Part("Regulator_Linear", "AP1117-ADJ", dest=TEMPLATE)
    bom = {
        "r": Part("Device", "R", dest=TEMPLATE),
        "c": Part("Device", "C", dest=TEMPLATE),
        "reg": reg,
    }

    # Instantiate the adjustable voltage regulator subcircuit
    vr = vreg_adj(bom=bom)
    vr["vin, vout, gnd"] += vin, vout, gnd

    # Assertions to verify the circuit
    assert len(vin) == 2
    assert len(gnd) == 3
    assert len(vout) == 3

# def test_interface_9():
#     """Test multiple packages for independence."""

#     @package
#     def reg_adj(VI, VO, GND, bom, output_voltage):
#         """Create voltage regulator with adjustable output."""

#         # Create adjustable regulator chip and connect to input and output.
#         reg = bom["reg"]()
#         reg["VI"] += VI
#         reg["VO"] += VO

#         # Create resistor divider and attach between output, adjust pin and ground.
#         rh = bom["r"]()
#         rl = bom["r"]()
#         r_total = 1000
#         rl.value = (1.25 / output_voltage) * r_total
#         rh.value = r_total - float(rl.value)
#         VO & rh & reg["ADJ"] & rl & GND

#     @package
#     def vreg(vin, vout, gnd, bom):
#         """Create voltage regulator with filtering caps."""

#         # Create regulator and attach to input, output and ground.
#         reg = bom["reg"]()
#         reg["VI, VO, GND"] += vin, vout, gnd

#         # Attach filtering capacitors on input and output.
#         cin, cout = bom["c"](2)
#         vin & cin & gnd
#         vout & cout & gnd

#     @package
#     def vreg_adj(vin, vout, gnd, bom, output_voltage=3.0):
#         """Create adjustable voltage regulator with filtering caps."""
#         bom2 = copy.copy(bom)
#         bom2["reg"] = reg_adj(bom=bom, output_voltage=output_voltage, dest=TEMPLATE)
#         vreg(vin=vin, vout=vout, gnd=gnd, bom=bom2)

#     vin, vout1, vout2, gnd = Net("VIN"), Net("VOUT1"), Net("VOUT2"), Net("GND")
#     reg = Part("xess.lib", "1117", dest=TEMPLATE)
#     reg.GND.aliases += "ADJ"
#     reg.IN.aliases += "VI"
#     reg.OUT.aliases += "VO"
#     bom = {
#         "r": Part("Device", "R", dest=TEMPLATE),
#         "c": Part("Device", "C", dest=TEMPLATE),
#         "reg": reg,
#     }
#     vr1 = vreg_adj(bom=bom)
#     vr2 = vreg_adj(bom=bom)
#     vr1["vin, vout, gnd"] += vin, vout1, gnd
#     vr2["vin, vout, gnd"] += vin, vout2, gnd
#     default_circuit.instantiate_packages()
#     u1 = Part.get("U1")
#     u2 = Part.get("U2")
#     u1.F2 = "U1-F2"
#     u2.F2 = "U2-F2"
#     assert u1.F2 == "U1-F2"
#     assert u2.F2 == "U2-F2"
#     assert len(default_circuit.parts) == 10
#     assert len(vout1.pins) == 3
#     assert len(vout2.pins) == 3
#     assert len(vin.pins) == 4
#     assert len(gnd.pins) == 6
#     # check decorator has not messed up docstring for subcircuits
#     assert vreg_adj.subcircuit.__name__ == "vreg_adj"
#     assert (
#         vreg_adj.subcircuit.__doc__
#         == "Create adjustable voltage regulator with filtering caps."
#     )
#     assert vreg.subcircuit.__name__ == "vreg"
#     assert vreg.subcircuit.__doc__ == "Create voltage regulator with filtering caps."
#     assert reg_adj.subcircuit.__name__ == "reg_adj"
#     assert (
#         reg_adj.subcircuit.__doc__ == "Create voltage regulator with adjustable output."
#     )


def test_interface_10():
    """Test resistor subcircuit."""
    r = Part("Device", "R", dest=TEMPLATE)

    @subcircuit
    def r_sub():
        # Create nets
        neta, netb = 2 * Net()
        # Connect resistor between nets
        neta & r() & netb
        return Interface(neta=neta, netb=netb)

    # Instantiate the subcircuit
    rr = r_sub()
    # Create nets
    vcc, gnd = Net("VCC"), Net("GND")
    # Connect the subcircuit to the nets
    rr.neta += vcc
    gnd += rr.netb
    # Assertions to verify the circuit
    assert len(gnd) == 1
    assert len(vcc) == 1


def test_interface_11():
    """Test nested subcircuits with resistors and capacitors."""
    r = Part("Device", "R", dest=TEMPLATE)
    c = Part("Device", "C", dest=TEMPLATE)

    @subcircuit
    def sub1(my_vin, my_gnd):
        # Create resistor and capacitor
        r1 = r()
        c1 = c()
        # Connect resistor and capacitor between input and ground
        my_vin & r1 & c1 & my_gnd

    @subcircuit
    def sub2():
        # Create nets
        my_vin1, my_vin2, my_gnd = 3 * Net()
        # Instantiate subcircuits
        sub1(my_vin1, my_gnd)
        sub1(my_vin2, my_gnd)
        return Interface(my_vin1=my_vin1, my_vin2=my_vin2, my_gnd=my_gnd)

    # Create nets
    vin1, vin2, gnd = Net("VIN1"), Net("VIN2"), Net("GND")
    # Instantiate the subcircuit
    sub = sub2()
    # Connect the subcircuit to the nets
    vin1 += sub.my_vin1
    sub.my_vin2 += vin2
    sub.my_gnd += gnd
    # Create resistor and connect between input and ground
    r1 = r()
    vin1 & r1 & gnd

    # Assertions to verify the circuit
    assert len(gnd) == 3
    assert len(vin1) == 2
    assert len(vin2) == 1


def test_interface_12():
    """Test nested subcircuits with fixed nets."""
    r = Part("Device", "R", dest=TEMPLATE)
    c = Part("Device", "C", dest=TEMPLATE)

    @subcircuit
    def sub1():
        # Create nets
        my_vin, my_gnd = Net(), Net()
        # Create resistor and capacitor
        r1 = r()
        c1 = c()
        # Connect resistor and capacitor between input and ground
        my_vin & r1 & c1 & my_gnd
        return Interface(my_vin=my_vin, my_gnd=my_gnd)

    @subcircuit
    def sub2(my_vin1, my_vin2, my_gnd):
        # Instantiate subcircuits
        s1 = sub1()
        s2 = sub1()
        # Connect the subcircuits to the nets
        s1.my_vin += my_vin1
        my_vin2 += s2.my_vin
        my_gnd += s1.my_gnd
        s2.my_gnd += my_gnd

    # Create nets
    vin1, vin2, gnd = Net("VIN1"), Net("VIN2"), Net("GND")
    # Instantiate the subcircuit
    sub = sub2(vin1, vin2, gnd)
    # Create resistor and connect between input and ground
    r1 = r()
    vin1 & r1 & gnd

    # Assertions to verify the circuit
    assert len(gnd) == 3
    assert len(vin1) == 2
    assert len(vin2) == 1


def test_interface_13():
    """Test analog averaging circuit."""
    @subcircuit
    def analog_average():
        # Create nets
        in1, in2, avg = 3 * Net()
        # Create resistors
        r1, r2 = 2 * Part("Device", "R", value="1K", dest=TEMPLATE)
        # Connect resistors to nets
        r1[1, 2] += in1, avg
        r2[1, 2] += in2, avg
        return Interface(in1=in1, in2=in2, avg=avg)

    # Create circuit
    cct = Circuit(name="My circuit")

    # Instantiate subcircuits
    avg1 = analog_average(circuit=cct)
    avg2 = analog_average(circuit=cct)

    # Create nets
    in1, in2, in3, in4, out1, out2 = Net(circuit=cct) * 6
    # Connect subcircuits to nets
    avg1["in1"] += in1
    avg1.in2 += in2
    avg1["avg"] += out1

    avg2["in1"] += in3
    avg2["in2"] += in4
    avg2.avg += out2

    # Assertions to verify the circuit
    assert len(cct.parts) == 4
    assert len(default_circuit.parts) == 0

    assert len(in1) == 1
    assert len(in2) == 1
    assert len(in3) == 1
    assert len(in4) == 1
    assert len(out1) == 2
    assert len(out2) == 2


def test_interface_14():
    """Test analog averaging circuit with default circuit."""
    @subcircuit
    def analog_average(circuit=None):
        # Use default circuit if none provided
        circuit = circuit or default_circuit
        with circuit as cct:
            # Create nets
            in1, in2, avg = 3 * Net(circuit=circuit)
            # Create resistors
            r1, r2 = 2 * Part("Device", "R", value="1K", dest=TEMPLATE)
            # Connect resistors to nets
            r1[1, 2] += in1, avg
            r2[1, 2] += in2, avg
            return Interface(in1=in1, in2=in2, avg=avg)

    # Create circuit
    cct = Circuit(name="My circuit")

    # Instantiate subcircuits
    avg1 = analog_average(circuit=cct)
    avg2 = analog_average(circuit=cct)

    # Create nets
    in1, in2, in3, in4, out1, out2 = Net(circuit=cct) * 6
    # Connect subcircuits to nets
    avg1["in1"] += in1
    avg1.in2 += in2
    avg1["avg"] += out1

    avg2["in1"] += in3
    avg2["in2"] += in4
    avg2.avg += out2

    # Assertions to verify the circuit
    assert len(cct.parts) == 4
    assert len(default_circuit.parts) == 0

    assert len(in1) == 1
    assert len(in2) == 1
    assert len(in3) == 1
    assert len(in4) == 1
    assert len(out1) == 2
    assert len(out2) == 2


def test_interface_15():
    """Test analog averaging circuit with explicit circuit."""
    @subcircuit
    def analog_average(cct=None):
        # Create nets
        in1, in2, avg = 3 * Net(circuit=cct)
        # Create resistors
        r1, r2 = 2 * Part("Device", "R", value="1K", dest=TEMPLATE, circuit=cct)
        # Connect resistors to nets
        r1[1, 2] += in1, avg
        r2[1, 2] += in2, avg
        return Interface(in1=in1, in2=in2, avg=avg)

    # Create circuit
    cct = Circuit(name="My circuit")

    # Instantiate subcircuits
    avg1 = analog_average(circuit=cct, cct=cct)
    avg2 = analog_average(circuit=cct, cct=cct)

    # Create nets
    in1, in2, in3, in4, out1, out2 = Net(circuit=cct) * 6

    # Connect subcircuits to nets
    avg1["in1"] += in1
    avg1.in2 += in2
    avg1["avg"] += out1

    avg2["in1"] += in3
    avg2["in2"] += in4
    avg2.avg += out2

    # Assertions to verify the circuit
    assert len(cct.parts) == 4
    assert len(default_circuit.parts) == 0

    assert len(in1) == 1
    assert len(in2) == 1
    assert len(in3) == 1
    assert len(in4) == 1
    assert len(out1) == 2
    assert len(out2) == 2


def test_interface_16():
    """Test analog averaging circuit with gates."""
    @subcircuit
    def analog_average(cct=None):
        # Create nets
        in1, in2, avg = 3 * Net(circuit=cct)
        # Create gates
        g1, g2 = 2 * Part("4xxx", "4001", value="4001", dest=TEMPLATE, circuit=cct)
        # Connect gates to nets
        g1[1, 2] += in1, avg
        g2[1, 2] += in2, avg
        return Interface(in1=in1, in2=in2, avg=avg)

    # Create circuit
    cct = Circuit(name="My circuit")

    # Instantiate subcircuits
    avg1 = analog_average(circuit=cct, cct=cct)
    avg2 = analog_average(circuit=cct, cct=cct)

    # Create nets
    in1, in2, in3, in4, out1, out2 = Net(circuit=cct) * 6

    # Connect subcircuits to nets
    avg1["in1"] += in1
    avg1.in2 += in2
    avg1["avg"] += out1

    avg2["in1"] += in3
    avg2["in2"] += in4
    avg2.avg += out2

    # Assertions to verify the circuit
    assert len(cct.parts) == 4
    assert len(default_circuit.parts) == 0

    assert len(in1) == 1
    assert len(in2) == 1
    assert len(in3) == 1
    assert len(in4) == 1
    assert len(out1) == 2
    assert len(out2) == 2
