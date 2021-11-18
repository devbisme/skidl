# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    # If matplotlib is not found, it's probably because SPICE tests
    # are not being run anyway. So just eat the exception.
    pass

from skidl import SKIDL, SPICE, TEMPLATE, Part, generate_netlist

from .setup_teardown import setup_function, teardown_function

from skidl.pyspice import *  # isort:skip


@pytest.mark.spice
def test_lib_import_1():
    lib_search_paths[SPICE].append(r"./SpiceLib/lib")
    lib = SchLib("lt1083", tool=SPICE)
    assert len(lib) > 0
    for p in lib.get_parts():
        print(p)


@pytest.mark.spice
def test_lib_import_2():
    with pytest.raises(FileNotFoundError):
        lib = SchLib("lt1074", tool=SPICE)


@pytest.mark.spice
def test_lib_export_1():
    set_default_tool(SPICE)
    lib = SchLib("lt1083", tool=SPICE)
    lib.export("my_lt1083", tool=SKIDL)
    # Doesn't work because of "pyspice={...}" placed in exported library.
    # my_lib = SchLib('my_lt1083', tool=SKIDL)
    # assert len(lib) == len(my_lib)


@pytest.mark.spice
def test_xspice_1():
    set_default_tool(SPICE)
    # Component declarations showing various XSPICE styles.
    vin = sinev(offset=1.65 @ u_V, amplitude=1.65 @ u_V, frequency=100e6)
    adc = Part(
        "pyspice",
        "A",
        io="anlg_in[],dig_out[]",
        model=XspiceModel(
            "adc",
            "adc_bridge",
            in_low=0.05 @ u_V,
            in_high=0.1 @ u_V,
            rise_delay=1e-9 @ u_s,
            fall_delay=1e-9 @ u_s,
        ),
        tool=SKIDL,
    )

    buf_tmp = A(
        io=["buf_in, buf_out"],
        model=XspiceModel(
            "buf",
            "d_buffer",
            rise_delay=1e-9 @ u_s,
            fall_delay=1e-9 @ u_s,
            input_load=1e-12 @ u_s,
        ),
        dest=TEMPLATE,
    )
    buf = buf_tmp()

    dac = A(
        io=["dig_in[]", "anlg_out[]"],
        model=XspiceModel("dac", "dac_bridge", out_low=1.0 @ u_V, out_high=3.3 @ u_V),
    )

    r = R(value=1 @ u_kOhm)

    # Create a part with no connections to test NULL SPICE connections.
    # buf2 = buf_tmp()
    # buf2["buf_in"] += NC

    # Connections: sine wave -> ADC -> buffer -> DAC.
    # Attach to first pin in ADC anlg_in vector of pins.
    vin["p, n"] += adc["anlg_in"][0], gnd
    # Attach first pin of ADC dig_out vector to buffer.
    adc["dig_out"][0] += buf["buf_in"]
    # Attach buffer output to first pin of DAC dig_in vector of pins.
    buf["buf_out"] += dac["dig_in"][0]
    # Attach first pin of DAC anlg_out vector to load resistor.
    r["p,n"] += dac["anlg_out"][0], gnd

    circ = generate_netlist()
    print(circ)
    sim = circ.simulator()
    waveforms = sim.transient(step_time=0.1 @ u_ns, end_time=50 @ u_ns)
    time = waveforms.time
    vin = waveforms[node(vin["p"])]
    vout = waveforms[node(r["p"])]

    print("{:^7s}{:^7s}".format("vin", "vout"))
    print("=" * 15)
    for v1, v2 in zip(vin.as_ndarray(), vout.as_ndarray()):
        print("{:6.2f} {:6.2f}".format(v1, v2))


@pytest.mark.spice
def test_part_convert_for_spice():

    set_default_tool(KICAD)

    vcc = Part("Device", "Battery", value=5 @ u_V)
    r1 = Part("Device", "R", value=1 @ u_kOhm)
    r2 = Part("Device", "R", value=2 @ u_kOhm)

    vcc.convert_for_spice(V, {1: "p", 2: "n"})
    r1.convert_for_spice(R, {1: "p", 2: "n"})
    r2.convert_for_spice(R, {1: "p", 2: "n"})

    vin, vout, gnd = Net("Vin"), Net("Vout"), Net("GND")
    vin.netio = "i"
    vout.netio = "o"
    gnd.netio = "o"

    gnd & vcc["n p"] & vin & r1 & vout & r2 & gnd

    generate_svg()

    set_default_tool(SPICE)
    circ = generate_netlist()
    print(circ)
    sim = circ.simulator()
    analysis = sim.dc(V1=slice(0, 5, 0.5))

    dc_vin = analysis.Vin
    dc_vout = analysis.Vout

    print("{:^7s}{:^7s}".format("Vin (V)", " Vout (V)"))
    print("=" * 15)
    for v, i in zip(dc_vin.as_ndarray(), dc_vout.as_ndarray()):
        print("{:6.2f} {:6.2f}".format(v, i))


@pytest.mark.spice
def test_subcircuit_1():
    from skidl.pyspice import gnd

    set_default_tool(SPICE)

    lib_search_paths[SPICE].append("SpiceLib")

    vin = V(ref="VIN", dc_value=8 @ u_V)  # Input power supply.
    vreg = Part("NCP1117", "ncp1117_33-x")  # Voltage regulator from ON Semi part lib.
    print(vreg)  # Print vreg pin names.
    r = R(value=470 @ u_Ohm)  # Load resistor on regulator output.
    # Connect vreg input to vin and output to load resistor.
    vreg["IN", "OUT"] += vin["p"], r[1]
    gnd += vin["n"], r[2], vreg["GND"]  # Ground connections for everybody.

    # Simulate the voltage regulator subcircuit.
    # circ = generate_netlist(libs='SpiceLib') # Pass-in the library where the voltage regulator subcircuit is stored.
    # Pass-in the library where the voltage regulator subcircuit is stored.
    circ = generate_netlist()
    print(circ)
    sim = circ.simulator()
    # Ramp vin from 0->10V and observe regulator output voltage.
    dc_vals = sim.dc(VIN=slice(0, 10, 0.1))

    # Get the input and output voltages.
    inp = dc_vals[node(vin["p"])]
    outp = dc_vals[node(vreg["OUT"])]

    # Plot the regulator output voltage vs. the input supply voltage. Note that the regulator
    # starts to operate once the input exceeds 4V and the output voltage clamps at 3.3V.
    figure = plt.figure(1)
    plt.title("NCP1117-3.3 Regulator Output Voltage vs. Input Voltage")
    plt.xlabel("Input Voltage (V)")
    plt.ylabel("Output Voltage (V)")
    plt.plot(inp, outp)
    plt.show()


@pytest.mark.spice
def test_model_1():
    reset()
    set_default_tool(SPICE)

    # Create a power supply for all the following circuitry.
    pwr = V(dc_value=5 @ u_V)
    pwr["n"] += gnd
    vcc = pwr["p"]

    # Create a logic inverter using a transistor and a few resistors.
    @subcircuit
    def inverter(inp, outp):
        """When inp is driven high, outp is pulled low by transistor. When inp is driven low, outp is pulled high by resistor."""
        q = BJT(model="2n2222a")  # NPN transistor.
        # Resistor attached between transistor collector and VCC.
        rc = R(value=1 @ u_kOhm)
        rc[1, 2] += vcc, q["c"]
        # Resistor attached between transistor base and input.
        rb = R(value=10 @ u_kOhm)
        rb[1, 2] += inp, q["b"]
        # Transistor emitter attached to ground.
        q["e"] += gnd
        # Inverted output comes from junction of the transistor collector and collector resistor.
        outp += q["c"]

    # Create a pulsed voltage source to drive the input of the inverters. I set the rise and fall times to make
    # it easier to distinguish the input and output waveforms in the plot.
    vs = PULSEV(
        initial_value=0,
        pulsed_value=5 @ u_V,
        pulse_width=0.8 @ u_ms,
        period=2 @ u_ms,
        rise_time=0.2 @ u_ms,
        fall_time=0.2 @ u_ms,
    )  # 1ms ON, 1ms OFF pulses.
    vs["n"] += gnd

    # Create three inverters and cascade the output of one to the input of the next.
    outp = Net() * 3  # Create three nets to attach to the outputs of each inverter.
    inverter(vs["p"], outp[0])  # First inverter is driven by the pulsed voltage source.
    inverter(outp[0], outp[1])  # Second inverter is driven by the output of the first.
    inverter(outp[1], outp[2])  # Third inverter is driven by the output of the second.

    # Simulate the cascaded inverters.
    circ = (
        generate_netlist()
    )  # Pass-in the library where the transistor model is stored.
    sim = circ.simulator()
    waveforms = sim.transient(step_time=0.01 @ u_ms, end_time=5 @ u_ms)

    # Get the waveforms for the input and output.
    time = waveforms.time
    inp = waveforms[node(vs["p"])]
    outp = waveforms[
        node(outp[2])
    ]  # Get the output waveform for the final inverter in the cascade.

    # Plot the input and output waveforms. The output will be the inverse of the input since it passed
    # through three inverters.
    figure = plt.figure(1)
    plt.title("Output Voltage vs. Input Voltage")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (V)")
    plt.plot(time * 1000, inp)
    plt.plot(time * 1000, outp)
    plt.legend(("Input Voltage", "Output Voltage"), loc=(1.1, 0.5))
    plt.show()


@pytest.mark.spice
def test_skywater_1():

    reset()
    set_default_tool(SPICE)

    sky_lib = SchLib(
        "/home/devb/tmp/skywater-pdk/libraries/sky130_fd_pr/latest/models/sky130.lib.spice",
        recurse=True,
        lib_section="tt",
    )

    nfet_wl = Parameters(W=1.26, L=0.15)
    pfet_wl = Parameters(W=1.26, L=0.15)

    pfet = Part(sky_lib, "sky130_fd_pr__pfet_01v8", params=pfet_wl, dest=TEMPLATE)
    nfet = Part(sky_lib, "sky130_fd_pr__nfet_01v8", params=nfet_wl, dest=TEMPLATE)

    def oscope(waveforms, *nets, ymin=-0.4, ymax=2.4):

        fig, axes = plt.subplots(
            nrows=len(nets),
            sharex=True,
            squeeze=False,
            subplot_kw={"ylim": (ymin, ymax)},
            gridspec_kw=None,
        )
        traces = axes[:, 0]

        num_traces = len(traces)
        trace_hgt = 1.0 / num_traces
        trace_lbl_position = dict(
            rotation=0, horizontalalignment="right", verticalalignment="center", x=-0.01
        )

        for i, (net, trace) in enumerate(zip(nets, traces), 1):
            trace.set_ylabel(net.name, trace_lbl_position)
            trace.set_position([0.1, (num_traces - i) * trace_hgt, 0.8, trace_hgt])
            trace.plot(waveforms.time, waveforms[node(net)])

        plt.show()

    def counter(*bits, time_step=1.0 @ u_ns, vmin=0.0 @ u_V, vmax=1.8 @ u_V):
        for bit in bits:
            pulse = PULSEV(
                initial_value=vmax,
                pulsed_value=vmin,
                pulse_width=time_step,
                period=2 * time_step,
            )
            pulse["p, n"] += bit, gnd
            time_step = 2 * time_step

    def pwr(dc_value=1.8 @ u_V):
        vdd_ps = V(ref="Vdd_ps", dc_value=dc_value)
        vdd_ps["p, n"] += Net("Vdd"), gnd
        return vdd_ps["p"]

    @package
    def inverter(a=Net(), out=Net()):
        qp = pfet()
        qn = nfet()

        gnd & qn.b
        vdd & qp.b
        vdd & qp["s,d"] & out & qn["d,s"] & gnd
        a & qn.g & qp.g

    @package
    def nand(a=Net(), b=Net(), out=Net()):
        q1, q2 = 2 * pfet
        q3, q4 = 2 * nfet

        vdd & q1.b & q2.b
        gnd & q3.b & q4.b
        vdd & (q1["s,d"] | q2["s,d"]) & out & q3["d,s"] & q4["d,s"] & gnd
        a & q1.g & q3.g
        b & q2.g & q4.g

    @package
    def xor(a=Net(), b=Net(), out=Net()):
        a_inv, b_inv = inverter(), inverter()
        a_inv.a += a
        b_inv.a += b

        an, abn, bn, bbn = 4 * nfet
        ap, abp, bp, bbp = 4 * pfet

        vdd & abp["s,d"] & bp["s,d"] & out & an["d,s"] & bn["d,s"] & gnd
        vdd & ap["s,d"] & bbp["s,d"] & out & abn["d,s"] & bbn["d,s"] & gnd

        a & ap.g & an.g
        a_inv.out & abp.g & abn.g
        b & bp.g & bn.g
        b_inv.out & bbp.g & bbn.g

        vdd & ap.b & abp.b & bp.b & bbp.b
        gnd & an.b & abn.b & bn.b & bbn.b

    @package
    def full_adder(a=Net(), b=Net(), cin=Net(), s=Net(), cout=Net()):
        ab_sum = Net()
        xor()["a,b,out"] += a, b, ab_sum
        xor()["a,b,out"] += ab_sum, cin, s

        nand1, nand2, nand3 = nand(), nand(), nand()
        nand1["a,b"] += ab_sum, cin
        nand2["a,b"] += a, b
        nand3["a,b,out"] += nand1.out, nand2.out, cout

    @subcircuit
    def adder(a, b, cin, s, cout):
        width = len(s)
        fadds = [full_adder() for _ in range(width)]
        for i in range(width):
            fadds[i]["a, b, s"] += a[i], b[i], s[i]
            if i == 0:
                fadds[i].cin += cin
            else:
                fadds[i].cin += fadds[i - 1].cout
        cout += fadds[-1].cout

    def integerize(waveforms, *nets, threshold=0.9 @ u_V):
        def binarize():
            binary_vals = []
            for net in nets:
                binary_vals.append([v > threshold for v in waveforms[node(net)]])
            return binary_vals

        int_vals = []
        for bin_vector in zip(*reversed(binarize())):
            int_vals.append(int(bytes([ord("0") + b for b in bin_vector]), base=2))
        return int_vals

    def sample(sample_times, times, *int_vals):
        sample_vals = [[] for _ in int_vals]
        sample_times = list(reversed(sample_times))
        sample_time = sample_times.pop()
        for time, *int_vec in zip(times, *int_vals):
            if sample_time < float(time):
                for i, v in enumerate(int_vec):
                    sample_vals[i].append(v)
                try:
                    sample_time = sample_times.pop()
                except IndexError:
                    break
        return sample_vals

    @package
    def weak_inverter(a=Net(), out=Net()):
        weak_nfet_wl = Parameters(W=1.0, L=8.0)
        weak_pfet_wl = Parameters(W=1.0, L=8.0)
        qp = Part(sky_lib, "sky130_fd_pr__pfet_01v8", params=weak_pfet_wl)
        qn = Part(sky_lib, "sky130_fd_pr__nfet_01v8", params=weak_nfet_wl)

        gnd & qn.b
        vdd & qp.b
        vdd & qp["s,d"] & out & qn["d,s"] & gnd
        a & qn.g & qp.g

    @package
    def sram_bit(wr=Net(), in_=Net(), out=Net()):
        in_inv = inverter()
        inv12, inv34 = weak_inverter(), weak_inverter()
        m5, m6 = nfet(), nfet()

        inv12["a, out"] += inv34["out, a"]
        m5.s & out & inv12.out
        m6.s & inv34.out
        in_ & m5.d
        in_ & in_inv["a, out"] & m6.d
        wr & m5.g & m6.g
        gnd & m5.b & m6.b

    @package
    def latch_bit(wr=Net(), in_=Net(), out=Net()):
        inv_in, inv_out, inv_wr = inverter(), inverter(), inverter()
        q_in, q_latch = nfet(), nfet()
        in_ & q_in["s,d"] & inv_in["a, out"] & inv_out["a, out"] & out
        inv_in.a & q_latch["s,d"] & out
        q_in.g & wr
        q_in.b & gnd
        wr & inv_wr.a
        q_latch.g & inv_wr.out
        q_latch.b & gnd

    @package
    def reg_bit(wr=Net(), in_=Net(), out=Net()):
        master, slave = latch_bit(), latch_bit()
        wr_inv = inverter()
        wr_inv.a += wr
        in_ & master["in_, out"] & slave["in_, out"] & out
        wr_inv.out & master.wr
        wr & slave.wr

    @subcircuit
    def register(wr, in_, out):
        width = len(out)
        reg_bits = [reg_bit() for _ in range(width)]
        for i, rb in enumerate(reg_bits):
            rb["wr, in_, out"] += wr, in_[i], out[i]

    @subcircuit
    def cntr(clk, out):
        global gnd
        width = len(out)
        zero = Bus(width)
        gnd += zero
        nxt = Bus(width)
        adder(out, zero, vdd, nxt, Net())
        register(clk, nxt, out)

    reset()

    vdd = pwr()
    clk = Net("clk")
    cnt = Bus("CNT", 3)
    counter(clk)
    cntr(clk, cnt)

    waveforms = (
        generate_netlist()
        .simulator()
        .transient(step_time=0.01 @ u_ns, end_time=30 @ u_ns)
    )
    oscope(waveforms, clk, *cnt)


@pytest.mark.spice
def test_skywater_2():

    reset()
    set_default_tool(SPICE)
    # lib_search_paths[SPICE].append("")

    vs = V(ref="VS", dc_value=1 @ u_V)
    r = R(value=0 @ u_Ohm)
    splib = SchLib(
        "/media/devb/Main/TEMP/skywater-pdk/libraries/sky130_fd_pr/latest/models/sky130.lib.spice",
        recurse=True,
        lib_section="tt",
    )

    nfet = Part(splib, "sky130_fd_pr__nfet_01v8", params=Parameters(L=8, W=0.55))
    vs["p"] & r & nfet["d, s"] & gnd & vs["n"]
    nfet.g & nfet.d
    nfet.b & nfet.s

    circ = generate_netlist()
    sim = circ.simulator()
    dc_vals = sim.dc(VS=slice(0, 10, 0.1))

    # Get the voltage applied to the resistor and the current coming out of the voltage source.
    # Get the voltage applied by the positive terminal of the source.
    voltage = dc_vals[node(vs["p"])]
    # Get the current coming out of the positive terminal of the voltage source.
    current = -dc_vals["VS"]

    # Print a table showing the current through the resistor for the various applied voltages.
    print("{:^7s}{:^7s}".format("V", " I (mA)"))
    print("=" * 15)
    for v, i in zip(voltage.as_ndarray(), current.as_ndarray() * 1000):
        print("{:6.2f} {:6.2f}".format(v, i))

    # Create a plot of the current (Y coord) versus the applied voltage (X coord).
    figure = plt.figure(1)
    plt.title("Resistor Current vs. Applied Voltage")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (mA)")
    # Plot X=voltage and Y=current (in milliamps, so multiply it by 1000).
    plt.plot(voltage, current * 1000)
    plt.show()


@pytest.mark.spice
def test_all_parts():

    lib_search_paths[SPICE].append("SpiceLib")

    ###############################################################################
    # NCP1117 voltage regulator.
    ###############################################################################

    reset()
    set_default_tool(SPICE)
    gnd = Net("0")
    lib_search_paths[SPICE].append("SpiceLib")
    vin = V(dc_value=8 @ u_V)  # Input power supply
    splib = SchLib("NCP1117")
    vreg = Part(splib, "ncp1117_33-x")  # Voltage regulator.
    r = R(value=470 @ u_Ohm)
    print(vreg)
    vreg["IN", "OUT"] += vin["p"], r[1]
    gnd += vin["n"], r[2], vreg["GND"]
    print(gnd)
    print(vreg["IN"].net)
    print(vreg["OUT"].net)
    print(node(vreg["IN"]))
    print(node(vin["p"]))

    # Simulate the voltage regulator subcircuit.
    # Pass-in the library where the voltage regulator subcircuit is stored.
    circ = generate_netlist(libs="SpiceLib")
    sim = circ.simulator()
    dc_vals = sim.dc(**{vin.ref: slice(0, 10, 0.1)})

    # Get the input and output voltages.
    inp = dc_vals[node(vin["p"])]
    outp = dc_vals[node(vreg["OUT"])]

    # Plot the input and output waveforms. The output will be the inverse of the input since it passed
    # through three inverters.
    figure = plt.figure(1)
    plt.title("Output Voltage vs. Input Voltage")
    plt.xlabel("Input Voltage (V)")
    plt.ylabel("Output Voltage (V)")
    plt.plot(inp, outp)
    plt.show()

    ###############################################################################
    # Current-controlled switch.
    ###############################################################################

    reset()  # Clear out the existing circuitry from the previous example.

    # Create a switch, power supply, drain resistor, and an input pulse source.
    # sw = CCS(model='CCS1')
    vdc = V(dc_value=10 @ u_V)  # 10V power supply.
    rl = R(value=4.7 @ u_kOhm)  # load resistor in series with power supply.
    isrc = PULSEI(
        initial_value=0 @ u_mA,
        pulsed_value=2 @ u_mA,
        pulse_width=1 @ u_ms,
        period=2 @ u_ms,
    )  # 1ms ON, 1ms OFF pulses.
    vsrc = V(dc_value=0 @ u_V)
    vdc["p", "n"] += rl[1], gnd  # Connect power supply to load resistor and ground.
    # Connect negative terminal of pulse source to ground.
    isrc["p", "n"] += vsrc["n"], gnd
    vsrc["p"] += gnd
    sw = CCS(source=vsrc, model="CCS1", initial_state="OFF")
    sw["p", "n"] += rl[2], gnd

    # Simulate the transistor amplifier. This requires a SPICE library containing a model of the 2N2222A transistor.
    # Pass the directory to the SPICE model library when creating circuit.
    circ = generate_netlist(libs="SpiceLib")
    sim = circ.simulator()
    waveforms = sim.transient(step_time=0.01 @ u_ms, end_time=5 @ u_ms)

    # Get the input source and amplified output waveforms.
    time = waveforms.time
    vout = waveforms[node(sw["p"])]  # Voltage at drain of the MOSFET.

    # Plot the input and output waveforms.
    figure = plt.figure(1)
    plt.title("Current-Controlled Switch Inverter Output Vs. Input Voltage")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (V)")
    # plt.plot(time*1000, vin)
    plt.plot(time * 1000, vout)
    plt.legend(("Input Voltage", "Output Voltage"), loc=(1.1, 0.5))
    plt.show()

    ###############################################################################
    # Voltage-controlled switch.
    ###############################################################################

    reset()  # Clear out the existing circuitry from the previous example.

    # Create a switch, power supply, drain resistor, and an input pulse source.
    # sw = VCS(model='VCS1', initial_state='OFF')
    sw = VCS(model="VCS1")
    vdc = V(dc_value=10 @ u_V)  # 10V power supply.
    rl = R(value=4.7 @ u_kOhm)  # load resistor in series with power supply.
    vs = PULSEV(
        initial_value=0 @ u_V,
        pulsed_value=2 @ u_V,
        pulse_width=1 @ u_ms,
        period=2 @ u_ms,
    )  # 1ms ON, 1ms OFF pulses.
    vdc["p", "n"] += rl[2], gnd  # Connect power supply to load resistor and ground.
    vs["n"] += gnd  # Connect negative terminal of pulse source to ground.
    sw["ip", "in"] += vs["p"], gnd
    sw["op", "on"] += rl[1], gnd

    # Simulate the transistor amplifier. This requires a SPICE library containing a model of the 2N2222A transistor.
    # Pass the directory to the SPICE model library when creating circuit.
    circ = generate_netlist(libs="SpiceLib")
    sim = circ.simulator()
    waveforms = sim.transient(step_time=0.01 @ u_ms, end_time=5 @ u_ms)

    # Get the input source and amplified output waveforms.
    time = waveforms.time
    vin = waveforms[node(vs["p"])]  # Input source voltage.
    vout = waveforms[node(sw["op"])]  # Voltage at drain of the MOSFET.

    # Plot the input and output waveforms.
    figure = plt.figure(1)
    plt.title("Voltage-Controlled Switch Inverter Output Vs. Input Voltage")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (V)")
    plt.plot(time * 1000, vin)
    plt.plot(time * 1000, vout)
    plt.legend(("Input Voltage", "Output Voltage"), loc=(1.1, 0.5))
    plt.show()

    ###############################################################################
    # MOSFET switch.
    ###############################################################################

    reset()  # Clear out the existing circuitry from the previous example.

    # Create a transistor, power supply, drain resistor, and an input pulse source.
    q = M(
        model="MOD1"
    )  # N-channel MOSFET. The model is stored in a directory of SPICE .lib files.
    vdc = V(dc_value=10 @ u_V)  # 10V power supply.
    rd = R(value=4.7 @ u_kOhm)  # Drain resistor in series with power supply.
    vs = PULSEV(
        initial_value=0 @ u_V,
        pulsed_value=5 @ u_V,
        pulse_width=1 @ u_ms,
        period=2 @ u_ms,
    )  # 1ms ON, 1ms OFF pulses.
    # Connect MOSFET pins to ground, drain resistor and pulse source.
    q["s", "d", "g", "b"] += gnd, rd[1], vs["p"], gnd
    vdc["p", "n"] += rd[2], gnd  # Connect power supply to drain resistor and ground.
    vs["n"] += gnd  # Connect negative terminal of pulse source to ground.

    # Simulate the transistor amplifier. This requires a SPICE library containing a model of the 2N2222A transistor.
    # Pass the directory to the SPICE model library when creating circuit.
    circ = generate_netlist(libs="SpiceLib")
    print(circ)
    sim = circ.simulator()
    waveforms = sim.transient(step_time=0.01 @ u_ms, end_time=5 @ u_ms)

    # Get the input source and amplified output waveforms.
    time = waveforms.time
    vin = waveforms[node(q["g"])]  # Input source voltage.
    vout = waveforms[node(q["d"])]  # Voltage at drain of the MOSFET.

    # Plot the input and output waveforms.
    figure = plt.figure(1)
    plt.title("MOSFET Inverter Output Vs. Input Voltage")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (V)")
    plt.plot(time * 1000, vin)
    plt.plot(time * 1000, vout)
    plt.legend(("Input Voltage", "Output Voltage"), loc=(1.1, 0.5))
    plt.show()

    ###############################################################################
    # Transistor amplifier.
    ###############################################################################

    reset()  # Clear out the existing circuitry from the previous example.

    # Create a transistor, power supply, bias resistors, collector resistor, and an input sine wave source.
    # 2N2222A NPN transistor. The model is stored in a directory of SPICE .lib files.
    q = BJT(model="2n2222a")
    vdc = V(dc_value=5 @ u_V)  # 5V power supply.
    rs = R(value=5 @ u_kOhm)  # Source resistor in series with sine wave input voltage.
    rb = R(value=25 @ u_kOhm)  # Bias resistor from 5V to base of transistor.
    rc = R(value=1 @ u_kOhm)  # Load resistor connected to collector of transistor.
    # 1 KHz sine wave input source.
    vs = SINEV(amplitude=0.01 @ u_V, frequency=1 @ u_kHz)
    # Connect transistor CBE pins to load & bias resistors and ground.
    q["c", "b", "e"] += rc[1], rb[1], gnd
    # Connect other end of load and bias resistors to power supply's positive terminal.
    vdc["p"] += rc[2], rb[2]
    vdc["n"] += gnd  # Connect negative terminal of power supply to ground.
    # Connect source resistor from input source to base of transistor.
    rs[1, 2] += vs["p"], q["b"]
    vs["n"] += gnd  # Connect negative terminal of input source to ground.

    # Simulate the transistor amplifier. This requires a SPICE library containing a model of the 2N2222A transistor.
    # Pass the directory to the SPICE model library when creating circuit.
    circ = generate_netlist(libs="SpiceLib")
    print(circ)
    sim = circ.simulator()
    waveforms = sim.transient(step_time=0.01 @ u_ms, end_time=5 @ u_ms)

    # Get the input source and amplified output waveforms.
    time = waveforms.time
    vin = waveforms[node(vs["p"])]  # Input source voltage.
    # Amplified output voltage at collector of the transistor.
    vout = waveforms[node(q["c"])]

    # Plot the input and output waveforms.
    figure = plt.figure(1)
    plt.title("Transistor Amplifier Output Voltage vs. Input Voltage")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (V)")
    plt.plot(time * 1000, vin)
    plt.plot(time * 1000, vout)
    plt.legend(("Input Voltage", "Output Voltage"), loc=(1.1, 0.5))
    plt.show()

    ###############################################################################
    # Resistor-Diode driven by pulses.
    ###############################################################################

    reset()

    # Create a pulsed voltage source, a resistor, and a capacitor.
    vs = PULSEV(
        initial_value=-5 @ u_V,
        pulsed_value=5 @ u_V,
        pulse_width=1 @ u_ms,
        period=2 @ u_ms,
    )  # 1ms ON, 1ms OFF pulses.
    r = R(value=100 @ u_Ohm)  # 1 Kohm resistor.
    d = D(model="DI_BAV21W")  # Diode.
    # Connect the diode between the positive source terminal and one of the resistor terminals.
    d["p", "n"] += vs["p"], r[1]
    # Connect the negative battery terminal and the other resistor terminal to ground.
    gnd += vs["n"], r[2]

    # Simulate the circuit.
    circ = generate_netlist()  # Create the PySpice Circuit object from the SKiDL code.
    print(circ)
    sim = circ.simulator()  # Get a simulator for the Circuit object.
    # Run a transient simulation from 0 to 10 msec.
    waveforms = sim.transient(step_time=0.01 @ u_ms, end_time=10 @ u_ms)

    # Get the simulation data.
    time = waveforms.time  # Time values for each point on the waveforms.
    # Voltage on the positive terminal of the pulsed voltage source.
    pulses = waveforms[node(vs["p"])]
    res_voltage = waveforms[node(r[1])]  # Voltage on the resistor.

    # Plot the pulsed source and capacitor voltage values versus time.
    figure = plt.figure(1)
    plt.title("Resistor Voltage Vs. Input Voltage Passed Through Diode")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (V)")
    plt.plot(time * 1000, pulses)  # Plot pulsed source waveform.
    plt.plot(time * 1000, res_voltage)  # Plot resistor charging waveform.
    plt.legend(("Source Pulses", "Resistor Voltage"), loc=(1.1, 0.5))
    plt.show()

    ###############################################################################
    # Current through resistor.
    ###############################################################################

    reset()  # This will clear any previously defined circuitry.

    # Create and interconnect the components.
    # Create a voltage source named "VS" with an initial value of 1 volt.
    vs = V(ref="VS", dc_value=1 @ u_V)
    r1 = R(value=1 @ u_kOhm)  # Create a 1 Kohm resistor.
    # Connect one end of the resistor to the positive terminal of the voltage source.
    vs["p"] += r1[1]
    # Connect the other end of the resistor and the negative terminal of the source to ground.
    gnd += vs["n"], r1[2]

    # Simulate the circuit.
    circ = (
        generate_netlist()
    )  # Translate the SKiDL code into a PyCircuit Circuit object.
    sim = circ.simulator()  # Create a simulator for the Circuit object.
    # Run a DC simulation where the voltage ramps from 0 to 1V by 0.1V increments.
    dc_vals = sim.dc(VS=slice(0, 1, 0.1))

    # Get the voltage applied to the resistor and the current coming out of the voltage source.
    # Get the voltage applied by the positive terminal of the source.
    voltage = dc_vals[node(vs["p"])]
    # Get the current coming out of the positive terminal of the voltage source.
    current = -dc_vals["VS"]

    # Print a table showing the current through the resistor for the various applied voltages.
    print("{:^7s}{:^7s}".format("V", " I (mA)"))
    print("=" * 15)
    for v, i in zip(voltage.as_ndarray(), current.as_ndarray() * 1000):
        print("{:6.2f} {:6.2f}".format(v, i))

    # Create a plot of the current (Y coord) versus the applied voltage (X coord).
    figure = plt.figure(1)
    plt.title("Resistor Current vs. Applied Voltage")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (mA)")
    # Plot X=voltage and Y=current (in milliamps, so multiply it by 1000).
    plt.plot(voltage, current * 1000)
    plt.show()

    ###############################################################################
    # Resistor-capacitor driven by pulses.
    ###############################################################################

    reset()

    # Create a pulsed voltage source, a resistor, and a capacitor.
    # 1ms ON, 1ms OFF pulses.
    vs = PULSEV(
        initial_value=0, pulsed_value=5 @ u_V, pulse_width=1 @ u_ms, period=2 @ u_ms
    )
    r = R(value=1 @ u_kOhm)  # 1 Kohm resistor.
    c = C(value=1 @ u_uF)  # 1 uF capacitor.
    # Connect the resistor between the positive source terminal and one of the capacitor terminals.
    r["+", "-"] += vs["p"], c[1]
    # Connect the negative battery terminal and the other capacitor terminal to ground.
    gnd += vs["n"], c[2]

    # Simulate the circuit.
    circ = generate_netlist()  # Create the PySpice Circuit object from the SKiDL code.
    sim = circ.simulator()  # Get a simulator for the Circuit object.
    # Run a transient simulation from 0 to 10 msec.
    waveforms = sim.transient(step_time=0.01 @ u_ms, end_time=10 @ u_ms)

    # Get the simulation data.
    time = waveforms.time  # Time values for each point on the waveforms.
    # Voltage on the positive terminal of the pulsed voltage source.
    pulses = waveforms[node(vs["p"])]
    cap_voltage = waveforms[node(c[1])]  # Voltage on the capacitor.

    # Plot the pulsed source and capacitor voltage values versus time.
    figure = plt.figure(1)
    plt.title("Capacitor Voltage vs. Source Pulses")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (V)")
    plt.plot(time * 1000, pulses)  # Plot pulsed source waveform.
    plt.plot(time * 1000, cap_voltage)  # Plot capacitor charging waveform.
    plt.legend(("Source Pulses", "Capacitor Voltage"), loc=(1.1, 0.5))
    plt.show()

    ###############################################################################
    # Resistor-inductor driven by pulses.
    ###############################################################################

    reset()

    # Create a pulsed voltage source, a resistor, and a capacitor.
    # 1ms ON, 1ms OFF pulses.
    vs = PULSEV(
        initial_value=0, pulsed_value=5 @ u_V, pulse_width=1 @ u_ms, period=2 @ u_ms
    )
    r = R(value=10 @ u_Ohm)  # 1 Kohm resistor.
    l = L(value=10 @ u_mH)  # 1 uF inductor.
    # Connect the resistor between the positive source terminal and one of the inductor terminals.
    r[1, 2] += vs["p"], l[1]
    # Connect the negative battery terminal and the other capacitor terminal to ground.
    gnd += vs["n"], l[2]

    # Simulate the circuit.
    circ = generate_netlist()  # Create the PySpice Circuit object from the SKiDL code.
    sim = circ.simulator()  # Get a simulator for the Circuit object.
    # Run a transient simulation from 0 to 10 msec.
    waveforms = sim.transient(step_time=0.01 @ u_ms, end_time=10 @ u_ms)

    # Get the simulation data.
    time = waveforms.time  # Time values for each point on the waveforms.
    # Voltage on the positive terminal of the pulsed voltage source.
    pulses = waveforms[node(vs["p"])]
    ind_voltage = waveforms[node(l[1])]  # Voltage on the capacitor.

    # Plot the pulsed source and capacitor voltage values versus time.
    figure = plt.figure(1)
    plt.title("Inductor Voltage vs. Source Pulses")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (V)")
    plt.plot(time * 1000, pulses)  # Plot pulsed source waveform.
    plt.plot(time * 1000, ind_voltage)  # Plot capacitor charging waveform.
    plt.legend(("Source Pulses", "Inductor Voltage"), loc=(1.1, 0.5))
    plt.show()


#
# Can't get this one to work.
#
# def test_555():
#     # Load the package for drawing graphs.
#     import matplotlib.pyplot as plt

#     # Omit the following line if you're not using a Jupyter notebook.
#     # %matplotlib inline
#     # from skidl.pyspice import gnd

#     lib_search_paths[SPICE].append(
#         "/media/devb/Main/TEMP/ngspice-33/examples/p-to-n-examples"
#     )

#     reset()  # Clear out the existing circuitry from the previous example.
#     set_default_tool(SPICE)
#     gnd = Net("0")
#     # Create a pulsed voltage source, a resistor, and a capacitor.
#     v2 = V(ref="V2", dc_value=5 @ u_V)
#     vreset = PULSEV(
#         ref="VRESET",
#         initial_value=0,
#         pulsed_value=5 @ u_V,
#         delay_time=1 @ u_us,
#         rise_time=1 @ u_us,
#         fall_time=1 @ u_us,
#         pulse_width=30 @ u_ms,
#         period=50 @ u_ms,
#     )
#     ra = R(ref="RA", value=1 @ u_kOhm)
#     rb = R(ref="RB", value=5 @ u_kOhm)
#     c = C(ref="C", value=0.5 @ u_uF)
#     ccont = C(ref="Ccont", value=0.5 @ u_uF)
#     rl = R(ref="RL", value=1 @ u_kOhm)
#     ra["+", "-"] += v2["p"], rb["+"]
#     rl["+"] += v2["p"]
#     c["+"] += rb["-"]
#     x1 = Part("TLC555.LIB", "TLC555")
#     # x1 = Part('NE555','NE555')
#     c["+"] += x1["THRES"], x1["TRIG"]
#     x1["RESET"] += vreset["p"]
#     x1["OUT"] += rl["-"]
#     x1["DISC"] += rb["+"]

#     x1["VCC"] += v2["p"]
#     x1["CONT"] += ccont["+"]
#     x1["GND"] += gnd
#     gnd += v2["n"], c["-"], vreset["n"], ccont["-"]
#     # Simulate the circuit.
#     circ = generate_netlist()  # Create the PySpice Circuit object from the SKiDL code.
#     sim = circ.simulator()  # Get a simulator for the Circuit object.
#     # Run a transient simulation from 0 to 100 msec.
#     waveforms = sim.transient(step_time=0.01 @ u_ms, end_time=100 @ u_ms)
#     # Get the simulation data.
#     time = waveforms.time  # Time values for each point on the waveforms.
#     # TLC 555 pin names below
#     # Voltage on the positive terminal of the pulsed voltage source.
#     thres = waveforms[node(x1["THRES"])]
#     out = waveforms[node(x1["OUT"])]
#     disc = waveforms[node(x1["DISC"])]
#     figure = plt.figure(1)
#     plt.title("555 Timer output vs threshold vs. discharge")
#     plt.xlabel("Time (ms)")
#     plt.ylabel("Voltage (V)")
#     plt.plot(time * 1000, thres)
#     plt.plot(time * 1000, out)
#     plt.plot(time * 1000, disc)
#     plt.legend(("Threshold", "Output Voltage", "Discharge"), loc=(1.1, 0.5))
#     plt.show()
