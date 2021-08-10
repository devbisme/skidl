import os
from skidl import *
import subcircuits as sc


for file in os.listdir("."):
    if file.endswith("sklib.py"):
        os.remove(file)



brd_sel = Net('brd_sel')
brd_en = Net('brd_en')
_3v3 = Net('+3V3')
gnd = Net('GND')

sc.stm32f405r([0,0], _3v3, gnd)
sc.board_enable([2000, 2000], brd_sel, brd_en, _3v3, gnd)



schematic_path = "/home/cdsfsmattner/Desktop/skidl/examples/stm32_usb_buck/stm32/stm32.sch"


generate_schematic(schematic_path)
