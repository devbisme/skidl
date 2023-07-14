from skidl import *

r = Part("Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric", dest=TEMPLATE)
q = Part(
    lib="Device.lib",
    name="Q_PNP_CBE",
    footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
    dest=TEMPLATE,
    symtx="V",
)

a = Net("A")
b = Net("B")
o = Net("O")

for _ in range(3):
    with Group("A:"):
        q1 = q()
        q2 = q()
        r1, r2, r3 = r(3, value="10K")
        a & r1 & (q1["c,e"] | q2["c,e"]) & r3 & o
        b & r2 & (q1["b"] | q2["b"])

generate_schematic(filepath=".", flatness=1.0)
