from skidl import *

# Create nets.
e, b, c = Net("ENET"), Net("BNET"), Net("CNET")
e.stub, b.stub, c.stub = True, True, True

# Create part templates.
qt = Part(lib="Transistor_BJT", name="Q_PNP_CBE", dest=TEMPLATE)

# Instantiate parts having various rotations & mirroring.
for q, tx in zip(qt(8), ["", "H", "V", "R", "L", "VL", "HR", "LV"]):
    q["E B C"] += e, b, c
    q.ref = "Q_" + tx
    q.symtx = tx

generate_svg()
