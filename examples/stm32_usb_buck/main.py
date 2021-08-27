import os
from skidl import *
import subcircuits as sc



for file in os.listdir("."):
    if file.endswith("sklib.py"):
        os.remove(file)





v_5v = Net('+5V', stub=True, netclass='Power')
v_3v3 = Net('+3V3', stub=True, netclass='Power')
gnd = Net('GND', stub=True, netclass='Power')

sc.stm32f405r(v_3v3, gnd, v_5v)



schematic_path = "/home/cdsfsmattner/Desktop/skidl/examples/stm32_usb_buck/stm32/stm32.sch"
generate_schematic(file_ = schematic_path, gen_iso_hier_sch=False, sch_size='A3')


# netlist_path = "/home/cdsfsmattner/Desktop/skidl/examples/stm32_usb_buck/stm32/netlist.net"
# generate_netlist(file_ = netlist_path)
