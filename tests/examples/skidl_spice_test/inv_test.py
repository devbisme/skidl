import matplotlib.pyplot as plt

# from skidl import SKIDL, SPICE, TEMPLATE, Part, generate_netlist
from skidl.pyspice import *  # isort:skip


def test_inverters():

    sky_lib = SchLib(
        "/home/devb/tmp/skywater-pdk/libraries/sky130_fd_pr/latest/models/sky130.lib.spice",
        recurse=True,
        lib_section="tt",
    )

    nfet_wl = Parameters(W=1.26, L=0.15)
    pfet_wl = Parameters(W=1.26, L=0.15)

    pfet = Part(sky_lib, "sky130_fd_pr__pfet_01v8", params=pfet_wl, dest=TEMPLATE)
    nfet = Part(sky_lib, "sky130_fd_pr__nfet_01v8", params=nfet_wl, dest=TEMPLATE)

    disp_vmin, disp_vmax = -0.4 @ u_V, 2.4 @ u_V
    disp_imin, disp_imax = -10 @ u_mA, 10 @ u_mA

    def oscope(waveforms, *nets_or_parts):
        """
        Plot selected waveforms as a stack of individual traces.

        Args:
            waveforms: Complete set of waveform data from ngspice simulation.
            nets_or_parts: SKiDL Net or Part objects that correspond to individual waveforms.
            vmin, vmax: Minimum/maximum voltage limits for each waveform trace.
            imin, imax: Minimum/maximum current limits for each waveform trace.
        """
        # Determine if this is a time-series plot, or something else.
        try:
            x = waveforms.time  # Sample times are used for the data x coord.
        except AttributeError:
            # Use the first Net or Part data to supply the x coord.
            nets_or_parts = list(nets_or_parts)
            x_node = nets_or_parts.pop(0)
            x = waveforms[node(x_node)]

        # Create separate plot traces for each selected waveform.
        num_traces = len(nets_or_parts)
        trace_hgt = 1.0 / num_traces
        fig, axes = plt.subplots(
            nrows=num_traces,
            sharex=True,
            squeeze=False,
            subplot_kw=None,
            gridspec_kw=None,
        )
        traces = axes[:, 0]

        # Set the X axis label on the bottom-most trace.
        if isinstance(x.unit, SiUnits.Second):
            xlabel = "Time (S)"
        elif isinstance(x.unit, SiUnits.Volt):
            xlabel = x_node.name + " (V)"
        elif isinstance(x.unit, SiUnits.Ampere):
            xlabel = x_node.ref + " (A)"
        traces[-1].set_xlabel(xlabel)

        # Set the Y axis label position for each plot trace.
        trace_ylbl_position = dict(
            rotation=0, horizontalalignment="right", verticalalignment="center", x=-0.01
        )

        # Plot each Net/Part waveform in its own trace.
        for i, (net_or_part, trace) in enumerate(zip(nets_or_parts, traces), 1):

            y = waveforms[node(net_or_part)]  # Extract the waveform data

            # Set the Y axis label depending upon whether data is voltage or current.
            if isinstance(y.unit, SiUnits.Volt):
                trace.set_ylim(float(disp_vmin), float(disp_vmax))
                trace.set_ylabel(net_or_part.name + " (V)", trace_ylbl_position)
            elif isinstance(y.unit, SiUnits.Ampere):
                trace.set_ylim(float(disp_imin), float(disp_imax))
                trace.set_ylabel(net_or_part.ref + " (A)", trace_ylbl_position)

            # Set position of trace within stacked traces.
            trace.set_position([0.1, (num_traces - i) * trace_hgt, 0.8, trace_hgt])

            # Place grid on X axis.
            trace.grid(axis="x", color="orange", alpha=1.0)

            # Plot the waveform data.
            trace.plot(x, y)

        plt.show()

    default_freq = (
        500 @ u_MHz
    )  # Specify a default frequency so it doesn't need to be set every time.

    def cntgen(*bits, freq=default_freq):
        """
        Generate one or more square waves varying in frequency by a factor of two.

        Args:
            bits: One or more Net objects, each of which will carry a square wave.
        """
        bit_period = 1.0 / freq
        for bit in bits:

            # Create a square-wave pulse generator with the current period.
            pulse = PULSEV(
                initial_value=vdd_voltage,
                pulsed_value=0.0 @ u_V,
                pulse_width=bit_period / 2,
                period=bit_period,
            )

            # Attach the pulse generator between ground and the net that carries the square wave.
            gnd & pulse["n, p"] & bit

            # Double the period (halve the frequency) for each successive bit.
            bit_period = 2 * bit_period

    default_voltage = 1.8 @ u_V  # Specify a default supply voltage.

    def pwr(voltage=default_voltage):
        """
        Create a global power supply and voltage rail.
        """
        # Clear any pre-existing circuitry. (Start with a clear slate.)
        reset()

        # Global variables for the power supply and voltage rail.
        global vdd_ps, vdd, vdd_voltage, gnd
        GND = gnd = Net("0")  # Instantiate the default ground net for SPICE.
        gnd.fixed_name = (
            True  # Make sure ground keeps it's name of "0" during net merges.
        )

        # Create a power supply and attach it between the Vdd rail and ground.
        vdd_voltage = voltage
        vdd_ps = V(ref="VDD_SUPPLY", dc_value=vdd_voltage)
        vdd = Net("Vdd")
        vdd & vdd_ps["p, n"] & gnd

    get_sim = (
        lambda: generate_netlist().simulator()
    )  # Compile netlist & create simulator.
    do_dc = lambda **kwargs: get_sim().dc(**kwargs)  # Run a DC-level analysis.
    do_trans = lambda **kwargs: get_sim().transient(
        **kwargs
    )  # Run a transient analysis.

    def how_big(circuit=default_circuit):
        from collections import defaultdict

        parts = defaultdict(lambda: 0)
        for p in circuit.parts:
            parts[p.name] += 1
        for part_name, num_parts in parts.items():
            print(f"{part_name}: {num_parts}")

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

    #############################################################################
    pwr()  # Apply power to the circuitry.

    inv = inverter()  # Create an inverter.

    # Attach a voltage source between ground and the inverter's input.
    # Then attach the output to a net.
    (
        gnd
        & V(ref="VIN", dc_value=0.0 @ u_V)["n, p"]
        & Net("VIN")
        & inv["a, out"]
        & Net("VOUT")
    )

    # Do a DC-level simulation while ramping the voltage source from 0 to Vdd.
    generate_netlist()
    vio = do_dc(VIN=slice(0, vdd_voltage, 0.01))

    # Plot the inverter's output against its input.
    oscope(vio, inv.a, inv.out)

    #############################################################################
    pwr()

    a = Net("A")
    cntgen(a)

    # Create a list of 30 inverters.
    invs = [inverter() for _ in range(30)]

    # Attach the square wave to the first inverter in the list.
    a & invs[0].a

    # Go through the list, attaching the input of each inverter to the output of the previous one.
    for i in range(1, len(invs)):
        invs[i - 1].out & invs[i].a

    # Attach the output of the last inverter to the output net.
    invs[-1].out & Net("A_DELAY")

    print(generate_netlist())

    # Do a transient analysis.
    waveforms = do_trans(step_time=0.01 @ u_ns, end_time=3.5 @ u_ns)
    oscope(waveforms, a, invs[-1].out)


if __name__ == "__main__":
    test_inverters()
