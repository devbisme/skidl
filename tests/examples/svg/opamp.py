
import svg_setup
from skidl import *

opamp = Part(lib="Amplifier_Operational", name="AD8676xR", symtx="H")
opamp.uA.p2 += Net("IN1")
opamp.uA.p3 += Net("IN2")
opamp.uA.p1 += Net("OUT")
# opamp.uB.symtx = 'L'
generate_svg()

