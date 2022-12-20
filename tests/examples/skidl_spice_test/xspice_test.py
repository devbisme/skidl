from skidl.pyspice import *

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

# Create an unconnected buffer to test NULL connections.
buf2 = buf_tmp()
buf2.buf_in += NC

# Connections: sine wave -> ADC -> buffer -> DAC.
vin["p, n"] += adc["anlg_in"][0], gnd  # Attach to first pin in ADC anlg_in vector of pins.
adc["dig_out"][0] += buf["buf_in"]  # Attach first pin of ADC dig_out vector to buffer.
buf["buf_out"] += dac["dig_in"][0]  # Attach buffer output to first pin of DAC dig_in vector of pins.
r["p,n"] += dac["anlg_out"][0], gnd  # Attach first pin of DAC anlg_out vector to load resistor.

circ = generate_netlist(libs="SpiceLib")
print(circ)
sim = circ.simulator()
waveforms = sim.transient(step_time=0.1 @ u_ns, end_time=50 @ u_ns)
time = waveforms.time
vin = waveforms[node(vin["p"])]
vout = waveforms[node(r["p"])]

import sys
sys.exit()

print('{:^7s}{:^7s}'.format('vin', 'vout'))
print('='*15)
for v1, v2 in zip(vin.as_ndarray(), vout.as_ndarray()):
    print('{:6.2f} {:6.2f}'.format(v1, v2))