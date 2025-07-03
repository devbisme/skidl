from skidl import *

C = Part('Device', 'C', dest=TEMPLATE, footprint='Capacitor_SMD:C_0402_1005Metric')
R = Part('Device', 'R', dest=TEMPLATE, footprint='Resistor_SMD:R_0402_1005Metric')
C1 = C(value='10u', tag='C1')
C2 = C(value='4.7u', tag='C2')
with Group("A"):
    R1 = R(value='10K', tag=1)
    R2 = R(value='1K', tag=2)
generate_netlist(file_="tstamps1.net")


reset()

C = Part('Device', 'C', dest=TEMPLATE, footprint='Capacitor_SMD:C_0402_1005Metric')
R = Part('Device', 'R', dest=TEMPLATE, footprint='Resistor_SMD:R_0402_1005Metric')
C2 = C(value='4.7u', tag='C2')
C1 = C(value='10u', tag='C1')
with Group("A"):
    R2 = R(value='1K', tag=2)
    R1 = R(value='10K', tag=1)
generate_netlist(file_="tstamps2.net")

