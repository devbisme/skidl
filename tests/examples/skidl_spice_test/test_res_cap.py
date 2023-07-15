import matplotlib.pyplot as plt

from skidl.pyspice import *

lib_search_paths[SPICE].append("SpiceLib")


###############################################################################
# Resistor-capacitor driven by pulses.
###############################################################################

reset()

# Create a pulsed voltage source, a resistor, and a capacitor.
vs = PULSEV(
    initial_value=0, pulsed_value=5 @ u_V, pulse_width=1 @ u_ms, period=2 @ u_ms
)  # 1ms ON, 1ms OFF pulses.
r = R(value=1 @ u_kOhm)  # 1 Kohm resistor.
c = C(value=1 @ u_uF)  # 1 uF capacitor.
r["+", "-"] += (
    vs["p"],
    c[1],
)  # Connect the resistor between the positive source terminal and one of the capacitor terminals.
gnd += (
    vs["n"],
    c[2],
)  # Connect the negative battery terminal and the other capacitor terminal to ground.

# Simulate the circuit.
circ = generate_netlist()  # Create the PySpice Circuit object from the SKiDL code.
sim = circ.simulator()  # Get a simulator for the Circuit object.
waveforms = sim.transient(
    step_time=0.01 @ u_ms, end_time=10 @ u_ms
)  # Run a transient simulation from 0 to 10 msec.

# Get the simulation data.
time = waveforms.time  # Time values for each point on the waveforms.
pulses = waveforms[
    node(vs["p"])
]  # Voltage on the positive terminal of the pulsed voltage source.
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
