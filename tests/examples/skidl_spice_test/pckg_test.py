import matplotlib.pyplot as plt
# from skidl import SKIDL, SPICE, TEMPLATE, Part, generate_netlist
from skidl.pyspice import *  # isort:skip

def test_skywater_1():

    sky_lib = SchLib(
        "/home/devb/tmp/skywater-pdk/libraries/sky130_fd_pr/latest/models/sky130.lib.spice",
        recurse=True,
        lib_section="tt",
    )
    print(sky_lib)

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

    circ = generate_netlist()
    print(circ)
    waveforms = (
        circ.simulator().transient(step_time=0.01 @ u_ns, end_time=30 @ u_ns)
    )
    oscope(waveforms, clk, *cnt)



if __name__ == "__main__":
    test_skywater_1()
