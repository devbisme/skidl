from skidl import *

q = Part(lib="Transistor_BJT", name="Q_PNP_CBE")
r = Part("Device", "R")
gnd = Part("power", "GND")
vcc = Part("power", "VCC")

generate_schematic()
