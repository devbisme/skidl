import matplotlib.pyplot as plt

from skidl.pyspice import *
from skidl import Interface

sky_lib = SchLib(
    "/home/asepahvand/repos/skywater-pdk/libraries/sky130_fd_pr/latest/models/sky130.lib_custom.spice",
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

@subcircuit
def inverter(a=None, out=None):
    a = a or Net()
    out = out or Net()
    qp = pfet()
    qn = nfet()

    gnd & qn.b
    vdd & qp.b
    vdd & qp["s,d"] & out & qn["d,s"] & gnd
    a & qn.g & qp.g
    return Interface(a=a, out=out)

@subcircuit
def nand(a=None, b=None, out=None):
    a = a or Net()
    b = b or Net()
    out = out or Net()
    q1, q2 = 2 * pfet
    q3, q4 = 2 * nfet

    vdd & q1.b & q2.b
    gnd & q3.b & q4.b
    vdd & (q1["s,d"] | q2["s,d"]) & out & q3["d,s"] & q4["d,s"] & gnd
    a & q1.g & q3.g
    b & q2.g & q4.g
    return Interface(a=a, b=b, out=out)

@subcircuit
def xor(a=None, b=None, out=None):
    a = a or Net()
    b = b or Net()
    out = out or Net()
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

    return Interface(a=a, b=b, out=out)

@subcircuit
def full_adder(a=None, b=None, cin=None, s=None, cout=None):
    a = a or Net()
    b = b or Net()
    cin = cin or Net()
    s = s or Net()
    cout = cout or Net()
    ab_sum = Net()
    xor()["a,b,out"] += a, b, ab_sum
    xor()["a,b,out"] += ab_sum, cin, s

    nand1, nand2, nand3 = nand(), nand(), nand()
    nand1["a,b"] += ab_sum, cin
    nand2["a,b"] += a, b
    nand3["a,b,out"] += nand1.out, nand2.out, cout
    return Interface(a=a, b=b, cin=cin, s=s, cout=cout)

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

@subcircuit
def weak_inverter(a=None, out=None):
    a = a or Net()
    out = out or Net()
    weak_nfet_wl = Parameters(W=1.0, L=8.0)
    weak_pfet_wl = Parameters(W=1.0, L=8.0)
    qp = Part(sky_lib, "sky130_fd_pr__pfet_01v8", params=weak_pfet_wl)
    qn = Part(sky_lib, "sky130_fd_pr__nfet_01v8", params=weak_nfet_wl)

    gnd & qn.b
    vdd & qp.b
    vdd & qp["s,d"] & out & qn["d,s"] & gnd
    a & qn.g & qp.g
    
    return Interface(a=a, out=out)

@subcircuit
def sram_bit(wr=None, in_=None, out=None):
    wr = wr or Net()
    in_ = in_ or Net()
    out = out or Net()
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

    return Interface(wr=wr, in_=in_, out=out)

@subcircuit
def latch_bit(wr=None, in_=None, out=None):
    wr = wr or Net()
    in_ = in_ or Net()
    out = out or Net()
    inv_in, inv_out, inv_wr = inverter(), inverter(), inverter()
    q_in, q_latch = nfet(), nfet()
    in_ & q_in["s,d"] & inv_in["a, out"] & inv_out["a, out"] & out
    inv_in.a & q_latch["s,d"] & out
    q_in.g & wr
    q_in.b & gnd
    wr & inv_wr.a
    q_latch.g & inv_wr.out
    q_latch.b & gnd

    return Interface(wr=wr, in_=in_, out=out)

@subcircuit
def reg_bit(wr=None, in_=None, out=None):
    wr = wr or Net()
    in_ = in_ or Net()
    out = out or Net()
    master, slave = latch_bit(), latch_bit()
    wr_inv = inverter()
    wr_inv.a += wr
    in_ & master["in_, out"] & slave["in_, out"] & out
    wr_inv.out & master.wr
    wr & slave.wr

    return Interface(wr=wr, in_=in_, out=out)

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

# waveforms = (
#     generate_netlist()
#     .simulator()
#     .transient(step_time=0.01 @ u_ns, end_time=30 @ u_ns)
# )

circ = generate_netlist()
print(circ)
try:
    sim = Simulator.factory()
    sim = sim.simulation(circ)
except:
    sim = circ.simulator()
waveforms = sim.transient(step_time=0.01 @ u_ns, end_time=30 @ u_ns)

oscope(waveforms, clk, *cnt)