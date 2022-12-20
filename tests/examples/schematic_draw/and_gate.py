from skidl import *

# Create part templates.
q = Part(lib="Device.lib", name="Q_PNP_CBE", dest=TEMPLATE, symtx="V")
r = Part("Device", "R", dest=TEMPLATE)

# Create nets.
gnd, vcc = Net("GND"), Net("VCC")
# a, b, a_and_b = Net("A", netio="i"), Net("B", netio="i"), Net("A_AND_B", netio="o")
a, b, a_and_b = Net("A"), Net("B"), Net("A_AND_B")

# Instantiate parts.
gndt = Part("power", "GND")  # Ground terminal.
vcct = Part("power", "VCC")  # Power terminal.
q1, q2 = q(2)
r1, r2, r3, r4, r5 = r(5, value="10K")

# Make connections between parts.
a & r1 & q1["B", "C"] & r4 & q2["B", "C"] & a_and_b & r5 & gnd
b & r2 & q1["B"]
q1["C"] & r3 & gnd
vcc += q1["E"], q2["E"], vcct
gnd += gndt

a.netio = "i"  # Input terminal.
b.netio = "i"  # Input terminal.
a_and_b.netio = "o"  # Output terminal.

q1.E.symio = "i"  # Signal enters Q1 on E and B terminals.
q1.B.symio = "i"
q1.C.symio = "o"  # Signal exits Q1 on C terminal.
q2.E.symio = "i"  # Signal enters Q2 on E and B terminals.
q2.B.symio = "i"
q2.C.symio = "o"  # Signal exits Q2 on C terminal.

q1.symtx = "L"
q2.symtx = "L"
vcc.stub = True

generate_svg()
generate_graph(file_="and_gate.dot")
