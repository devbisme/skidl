from skidl import *

q = Part(lib="Device.lib", name="Q_PNP_CBE")
r = Part("Device", "R")
gnd = Part("power", "GND")
vcc = Part("power", "VCC")

generate_schematic()
