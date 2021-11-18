from skidl import *

mosfet = Part("pspice", "MPMOS")
mosfet.symtx = "HR"
mosfet.symtx = "HL"
pmos = Part("pspice", "MPMOS")
# pmos = Part("DeviceSteffen","PMOS_GSD")
n01 = Net("n01")
mosfet[1] += mosfet[2]
n01 += mosfet[3]
pmos[3] += mosfet[3]

generate_svg()
