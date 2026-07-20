"""Nested hierarchical subcircuits with a mix of stub nets and routed nets, so
both stub labels (VIN2) and wire/NetTerminal labels (VIN1) are emitted.  Both
kinds of label should extend away from their pin.  (Adapted from Dave's
hier_test.test_interface_12.)

    python nested_interface.py
"""

from skidl import *

r = Part("Device", "R", dest=TEMPLATE)
c = Part("Device", "C", dest=TEMPLATE)


@subcircuit
def sub1():
    my_vin, my_gnd = Net(), Net()
    r1 = r(tag="r1")
    c1 = c(tag="c1")
    my_vin & r1 & c1 & my_gnd
    return Interface(my_vin=my_vin, my_gnd=my_gnd)


@subcircuit
def sub2(my_vin1, my_vin2, my_gnd):
    s1 = sub1(tag="s1")
    s2 = sub1(tag="s2")
    s1.my_vin += my_vin1
    my_vin2 += s2.my_vin
    my_gnd += s1.my_gnd
    s2.my_gnd += my_gnd


vin1, vin2, gnd, vdd = Net("VIN1"), Net("VIN2", stub=True), Net("GND"), Net("VDD")
sub = sub2(vin1, vin2, gnd, tag="sub")
r1 = r()
vdd & r1 & gnd

generate_schematic(title="Nested interface", flatness=1, filepath=".")
