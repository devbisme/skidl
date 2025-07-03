import matplotlib.pyplot as plt

from skidl.pyspice import *

lib_search_paths[SPICE] = ["../../test_data/SpiceLib"]


###############################################################################
# Resistor-capacitor driven by pulses.
###############################################################################

reset()

# Create a pulsed voltage source, a 1KOhm resistor, and a 1uF capacitor.
# Pulsed voltage: 1ms ON, 1ms OFF pulses.
vs = PULSEV(
    initial_value=0, pulsed_value=5 @ u_V, pulse_width=1 @ u_ms, period=2 @ u_ms
)
r = R(value=1 @ u_kOhm)
c = C(value=1 @ u_uF)

# Connect the resistor between the positive source terminal and one of the capacitor terminals.
r["+", "-"] += vs["p"], c[1]

# Connect the negative battery terminal and the other capacitor terminal to ground.
gnd += vs["n"], c[2]

# Simulate the circuit.
circ = generate_netlist()  # Create the PySpice Circuit object from the SKiDL code.
sim = Simulator.factory().simulation(circ)
# Run a transient simulation from 0 to 10 msec.
waveforms = sim.transient(step_time=0.01 @ u_ms, end_time=10 @ u_ms)

# Get the simulation data.
# Time values for each point on the waveforms.
time = waveforms.time
# Voltage on the positive terminal of the pulsed voltage source.
pulses = waveforms[node(vs["p"])]
# Voltage on the capacitor.
cap_voltage = waveforms[node(c[1])]

# Plot the pulsed source and capacitor voltage values versus time.
figure = plt.figure(1)
plt.title("Capacitor Voltage vs. Source Pulses")
plt.xlabel("Time (ms)")
plt.ylabel("Voltage (V)")
plt.plot(time * 1000, pulses)  # Plot pulsed source waveform.
plt.plot(time * 1000, cap_voltage)  # Plot capacitor charging waveform.
plt.legend(("Source Pulses", "Capacitor Voltage"), loc=(1.1, 0.5))
plt.show()
