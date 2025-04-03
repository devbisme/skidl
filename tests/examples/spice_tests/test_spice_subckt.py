import matplotlib.pyplot as plt

from skidl.pyspice import *

lib_search_paths[SPICE].append("../../test_data/SpiceLib")

vin = V(ref="VIN", dc_value=8 @ u_V)  # Input power supply.

vreg = Part("NCP1117", "ncp1117_33-x")  # Voltage regulator from ON Semi part lib.
vreg[3].aliases += "IN"  # Set pin 3 as IN.
vreg[1].aliases += "OUT"  # Set pin 1 as OUT.
vreg[2].aliases += "GND"  # Set pin 2 as GND.

r = R(value=470 @ u_Ohm)  # Load resistor on regulator output.

vin["p"] & vreg["IN", "OUT"] & r & gnd
gnd += vin["n"], vreg["GND"]  # Ground connections for everybody.

# Simulate the voltage regulator subcircuit.
circ = generate_netlist()
print(circ)

try:
    sim = Simulator.factory()
    sim = sim.simulation(circ)
except:
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
