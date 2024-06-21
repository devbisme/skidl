import svg_setup
from skidl import *

mosfet = Part("Device", "Q_NMOS_DGS")
mosfet.symtx = "HR"
mosfet.symtx = "HL"
pmos = Part("Device", "Q_PMOS_DGS")
n01 = Net("n01")
mosfet[1] += mosfet[2]
n01 += mosfet[3]
pmos[3] += mosfet[3]

generate_svg()
