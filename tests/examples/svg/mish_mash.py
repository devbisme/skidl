import svg_setup
from skidl import *

l1 = Part("Device", "L")
r1, r2 = Part("Device", "R", dest=TEMPLATE, value="200.0") * 2
q1 = Part("Device", "Q_NPN_CBE")
c1 = Part("Device", "C", value="10pF")
r3 = r2(value="1K")
vcc, vin, vout, gnd = Net("VCC"), Net("VIN"), Net("VOUT"), Net("GND")
vcc & r1 & vin & r2 & gnd
vcc & r3 & vout & q1["C,E"] & gnd
q1["B"] += vin
vout & (l1 | c1) & gnd
rly = Part("Relay", "TE_PCH-1xxx2M")
rly[1, 2, 3, 5] += gnd
led = Part("Device", "LED_ARGB", symtx="RH")
r, g, b = Net("R"), Net("G"), Net("B")
led["A,RK,GK,BK"] += vcc, r, g, b
Part(lib="MCU_Microchip_PIC10", name="PIC10F200-IMC")
generate_svg()
