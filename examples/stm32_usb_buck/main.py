import os
from skidl import *
import subcircuits as sc


for file in os.listdir("."):
    if file.endswith("sklib.py"):
        os.remove(file)



_5v_usb = Net('+3V3')#, stub=True)
_3v3 = Net('+3V3')#, stub=True)
gnd = Net('GND')#, stub=True)

sc.stm32f405r(_3v3, gnd, _5v_usb)
sc.board_enable(_3v3, gnd)
# sc.stm32f405r(_3v3, gnd)
# sc.board_enable(_3v3, gnd)



schematic_path = "/home/cdsfsmattner/Desktop/skidl/examples/stm32_usb_buck/stm32/stm32.sch"
netlist_path = "/home/cdsfsmattner/Desktop/skidl/examples/stm32_usb_buck/stm32/netlist.net"


generate_schematic(file_ = schematic_path)
# generate_netlist(file_ = netlist_path)
