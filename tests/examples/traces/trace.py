from skidl import *

netclass1 = NetClass("netclass1", priority=1)
netclass2 = NetClass("netclass2", priority=2)
netclass3 = NetClass("netclass3", priority=3)

@subcircuit
def rc():
    r = Part("Device","R")
    c = Part("Device","C")
    rc = r | c
    r[1].net.netclass = netclass1
    r[1].net.netclass = netclass2
    return Interface(p1=rc[1], p2=rc[0])

@subcircuit
def rcrl():
    l = Part("Device","L")
    r = Part("Device","R")
    rl = l & r
    l[2].net.netclass = netclass3
    rc_ = rc()
    rl[0] += rc_.p1
    rl[1] += rc_.p2
    return Interface(p1=rl[0], p2=rl[1])

rcrl_ = rcrl()

default_circuit.track_abs_path = True
default_circuit.track_src = True
generate_netlist()
