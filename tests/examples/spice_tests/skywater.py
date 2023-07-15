import matplotlib.pyplot as plt

from skidl.pyspice import *

lib_search_paths[SPICE].append("")

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
print(circ)
print("Creating simulator...")
sim = circ.simulator()
print("Running simulation...")
dc_vals = sim.dc(VS=slice(0, 10, 0.1))

# Get the voltage applied to the resistor and the current coming out of the voltage source.
voltage = dc_vals[
    node(vs["p"])
]  # Get the voltage applied by the positive terminal of the source.
current = -dc_vals[
    "VS"
]  # Get the current coming out of the positive terminal of the voltage source.

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
plt.plot(
    voltage, current * 1000
)  # Plot X=voltage and Y=current (in milliamps, so multiply it by 1000).
plt.show()
