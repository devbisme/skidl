from skidl import *

rt = Part('device', 'R', dest=TEMPLATE, footprint='null')
r1 = rt()
resistors = rt(5)
generate_netlist()
