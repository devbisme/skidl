import matplotlib.pyplot as plt

from skidl.pyspice import *

lib_search_paths[SPICE].append("../SpiceLib")

vin = V(ref="VIN", dc_value=8 @ u_V)  # Input power supply.
vreg = Part("NCP1117", "ncp1117_33-x")  # Voltage regulator from ON Semi part lib.
print(vreg)  # Print vreg pin names.
r = R(value=470 @ u_Ohm)  # Load resistor on regulator output.
vreg["IN", "OUT"] += (
    vin["p"],
    r[1],
)  # Connect vreg input to vin and output to load resistor.
gnd += vin["n"], r[2], vreg["GND"]  # Ground connections for everybody.

# Simulate the voltage regulator subcircuit.
# circ = generate_netlist(libs='SpiceLib') # Pass-in the library where the voltage regulator subcircuit is stored.
circ = (
    generate_netlist()
)  # Pass-in the library where the voltage regulator subcircuit is stored.
print(circ)
sim = circ.simulator()
dc_vals = sim.dc(
    VIN=slice(0, 10, 0.1)
)  # Ramp vin from 0->10V and observe regulator output voltage.

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
