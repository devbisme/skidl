"""Eight PNP transistors in every rotation/mirror, each pin carrying a stub net
label.  Exercises net-label orientation across all symbol transforms: every
label should extend AWAY from the body (horizontal labels reach to the side,
vertical labels run clear above/below), in all four KiCad backends.

    python transistor_rotations.py           # default tool (KiCad 9)
    SKIDL_TOOL=KICAD8 python transistor_rotations.py
"""
from skidl import *

e, b, c = Net("ENET"), Net("BNET"), Net("CNET")
b.netio = "i"
e.stub, b.stub, c.stub = True, True, True

qt = Part(lib="Transistor_BJT", name="Q_PNP_CBE", dest=TEMPLATE)
for q, tx in zip(qt(8), ["", "H", "V", "R", "L", "VL", "HR", "LV"]):
    q["E B C"] += e, b, c
    q.ref = "Q_" + tx
    q.symtx = tx

generate_schematic(filepath=".", flatness=1.0)
