from skidl import *

set_default_tool(KICAD6)

def my_empty_footprint_handler(part):
    part.fields["footprint"] = ":"
    part.footprint = ":"

import skidl
skidl.empty_footprint_handler = my_empty_footprint_handler

# Create part templates.
q = PartTmplt(lib="Device", name="Q_PNP_CBE", symtx="V")
r = PartTmplt("Device", "R")

# Create nets.
gnd, vcc = Net("GND"), Net("VCC")
a, b, a_and_b = Net("A"), Net("B"), Net("A_AND_B")

# Instantiate parts.
gndt = Part("power", "GND")  # Ground terminal.
vcct = Part("power", "VCC")  # Power terminal.
q1, q2 = q(2)
r1, r2, r3, r4, r5 = r(5, value="10K")
r4.symtx = "L"

# Make connections between parts.
a & r1 & q1["B", "C"] & r4 & q2["B", "C"] & a_and_b & r5 & gnd
b & r2 & q1["B"]
q1["C"] & r3 & gnd
vcc += q1["E"], q2["E"], vcct
gnd += gndt

generate_svg()
# generate_schematic(draw=True, fanout_attenuation=True)
