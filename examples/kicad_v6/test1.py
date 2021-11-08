from skidl import *

# Place the location of the KiCad-nightly libraries first in the search path.
lib_search_paths[KICAD].insert(0, "/usr/lib/kicad-nightly/share/kicad/library")

gnd = Net('GND')

# Create a few parts...
j1 = Part(lib='Device', name='Jumper', footprint='TestPoint:TestPoint_2Pads_Pitch2.54mm_Drill0.8mm')
r1 = Part(lib='Device', name='R', footprint='Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder')
c1 = Part(lib='Device', name='C', footprint='Capacitor_SMD:CP_Elec_10x10')
rn1 = Part(lib='Device', name='R_Pack04', footprint='Resistor_SMD:R_Array_Convex_4x1206')

# Connect the parts.
j1[1] & r1 & rn1['r1.1, r1.2'] & rn1['r2.2, r2.1'] & rn1['r3.1, r3.2'] & rn1['r4.2, r4.1'] & c1 & j1[2] & gnd

generate_netlist()
