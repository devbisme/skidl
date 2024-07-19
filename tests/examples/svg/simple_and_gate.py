from skidl import *

# Create part templates.
q = Part("Device", "Q_PNP_CBE", dest=TEMPLATE)
r = Part("Device", "R", dest=TEMPLATE)

# Create nets.
gnd, vcc = Net("GND"), Net("VCC")
a, b, a_and_b = Net("A"), Net("B"), Net("A_AND_B")

# Instantiate parts.
gndt = Part("power", "GND")             # Ground terminal.
vcct = Part("power", "VCC")             # Power terminal.
q1, q2 = q(2)                           # Two transistors.
r1, r2, r3, r4, r5 = r(5, value="10K")  # Five 10K resistors.

# Make connections between parts.
a & r1 & q1["B C"] & r4 & q2["B C"] & a_and_b & r5 & gnd
b & r2 & q1["B"]
q1["C"] & r3 & gnd
vcc += q1["E"], q2["E"], vcct
gnd += gndt

generate_netlist(tool=KICAD8) # Create KICAD version 8 netlist.

layout_options = """
org.eclipse.elk.algorithm="random"
"""
# org.eclipse.elk.layered.spacing.nodeNodeBetweenLayers="5"
# org.eclipse.elk.layered.compaction.postCompaction.strategy="4"
# org.eclipse.elk.spacing.nodeNode="50"
# org.eclipse.elk.direction="DOWN"

generate_svg(layout_options=layout_options)