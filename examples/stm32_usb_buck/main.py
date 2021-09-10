import os
from skidl import *
import subcircuits as sc


# Delete sklib file or we get errors
for file in os.listdir("."):
    if file.endswith("sklib.py"):
        os.remove(file)

# clear the console so we can see the print statements easier
clear = lambda: os.system('clear')
clear()


# Declare power nets
v_12v = Net('+12V', stub=True, netclass='Power')
v_5v = Net('+5V', stub=True, netclass='Power')
v_3v3 = Net('+3V3', stub=True, netclass='Power')
gnd = Net('GND', stub=True, netclass='Power')

# Generate STM32 circuit
sc.stm32f405r(v_12v, v_5v, v_3v3, gnd)

# Generate netlist
netlist_path = "/home/cdsfsmattner/Desktop/skidl/examples/stm32_usb_buck/stm32/netlist.net"
generate_netlist(file_ = netlist_path)

# Generate schematic
schematic_path = "/home/cdsfsmattner/Desktop/skidl/examples/stm32_usb_buck/stm32/stm32.sch"
generate_schematic(file_ = schematic_path, sch_size='A2')



