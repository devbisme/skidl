from skidl.pyspice import *

lib_search_paths[SKIDL].append("../../../src/skidl/tools/skidl/libs")

# Component declarations showing various XSPICE styles.
vin = sinev(offset=1.65 @ u_V, amplitude=1.65 @ u_V, frequency=1e4)

adc = Part(
    "pyspice",
    "A",
    io="anlg_in[],dig_out[]",
    model=XspiceModel(
        "adc",
        "adc_bridge",
        in_low=1.65 @ u_V,
        in_high=1.65 @ u_V,
        rise_delay=1e-9 @ u_s,
        fall_delay=1e-9 @ u_s,
    ),
    tool=SKIDL,
)

buf_tmp = A(
    # io=["buf_in, buf_out"],
    io=["buf_in", "buf_out"],
    # io=["buf_in[]","buf_out[]"],
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
    model=XspiceModel("dac", "dac_bridge", out_low=0 @ u_V, out_high=3.3 @ u_V),
)

r = R(value=1 @ u_kOhm)

# Create an unconnected buffer to test NULL connections.
# buf2 = buf_tmp()
# buf2.buf_in += NC

# Connections: sine wave -> ADC -> buffer -> DAC.
# Attach to first pin in ADC anlg_in vector of pins.
vin["p, n"] += adc["anlg_in"][0], gnd
# Attach first pin of ADC dig_out vector to buffer.
adc["dig_out"][0] += buf["buf_in"]
# Attach buffer output to first pin of DAC dig_in vector of pins.
buf["buf_out"] += dac["dig_in"][0]
# Attach first pin of DAC anlg_out vector to load resistor.
r["p,n"] += dac["anlg_out"][0], gnd

circ = generate_netlist(file_="xspice.cir", libs="SpiceLib")
print(circ)
sim = Simulator.factory().simulation(circ)
waveforms = sim.transient(step_time=1 @ u_us, end_time=2 @ u_ms)
time = waveforms.time
vin = waveforms[node(vin["p"])]
vout = waveforms[node(r["p"])]

print("{:^7s}{:^7s}".format("vin", "vout"))
print("=" * 15)
for v1, v2 in zip(vin.as_ndarray(), vout.as_ndarray()):
    print(f"{v1:6.2f} {v2:6.2f}")
