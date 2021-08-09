import os
from skidl import *
import subcircuits as sc


for file in os.listdir("."):
    if file.endswith("sklib.py"):
        os.remove(file)

_3v3 = Net('+3V3')
gnd = Net('GND')

sc.stm32f405r(_3v3, gnd,[1000,1000])

schematic_path = "/home/cdsfsmattner/Desktop/skidl/examples/stm32_usb_buck/stm32/stm32.sch"

generate_schematic(schematic_path, x_start=3000, y_start=1500, comp_spacing = 700, ncols=10)