from skidl import *
import sys
import gc


xess_lib = SchLib('C:/xesscorp/KiCad/libraries/xess.lib')

@SubCircuit
def res_divider(in1, out1):
    r1, r2 = 2 * Part('C:/xesscorp/KiCad/libraries/xess.lib', 'R', footprint='Resistors_SMD:R_0805')
    r1.value = '1K6'
    r2.value = '500K3'
    r1[1] += in1
    out1 += r1[2], r2[1]
    r2[2] = gnd
    vreg = Part('C:/xesscorp/KiCad/libraries/xess.lib', 'NCV1117', footprint='XESS:SOT-223')
    vreg.value = 'NCV1117'
    vreg[1,2,3] = gnd, out1, in1
    #vreg[2] = out1
    #vreg[1] = gnd
    #vreg[3] = in1
    vreg2 = Part('C:/xesscorp/KiCad/libraries/xess.lib', '1117', footprint='XESS:SOT-223')
    vreg2.value = 'NCV1117'
    vreg2[2] = out1
    vreg2[1] = gnd
    vreg2[3] = in1
    print('.',r1.hierarchy)
    print(r1[1].electrical_type, r1[1].func)
    print(gnd.hierarchy)

    @SubCircuit
    def cap_divider():
        c1, c2 = 2 * Part('C:/xesscorp/KiCad/libraries/xess.lib', 'C-NONPOL', footprint='Capacitors_SMD:C_0805')
        c1.value = '1uF'
        c2.value = '2uF'
        c1[1] = in1
        out1.add_pins(c1[2], c2[1])
        #out1 += c1[2], c2[1]
        c2[2] = gnd
        print(':',c2.hierarchy)
        print(gnd.hierarchy)

    cap_divider()

gnd = Net('GND')
# multi_gnds = 10 * gnd
# cs = 10* Part('C:/xesscorp/KiCad/libraries/xess.lib', 'C-NONPOL', footprint='Capacitors_SMD:C_0805')
# for c,g in zip(cs,multi_gnds):
    # c[1] = g
a = Net('A')
b = Net('B')
c = Net()
bus = Bus('BB', a, b, c)
# a = bus[0]
# b = bus[1]
# c = bus[2]

res_divider(a,b)
res_divider(b,c)
#r = Part('C:/xesscorp/KiCad/libraries/xess.lib', 'R', footprint='Resistors_SMD:R_0603', connections={1:bus[0], 2:bus[1]})
r = Part('C:/xesscorp/KiCad/libraries/xess.lib', 'R', footprint='Resistors_SMD:R_0603')
#r[1,2] = bus[0,1]
#r[1,2] = bus[0:2]
r[1,2] = bus[0],bus[1]
r['.*'] = bus[0:2]
# r[1] += bus[0]
# r[2] += bus[1]
ra = 10 * Part('C:/xesscorp/KiCad/libraries/xess.lib', 'R', footprint='Resistors_SMD:R_0603')
gnd += [r[1] for r in ra]
a += [r[2] for r in ra]


def print_pin(p):
    print('Pin:', p.name, p.num, p.part.name, p.part.ref, p.part.value, p.part.name)

def print_net(n):
    print('Net:', n.name)
    for p in n.pins:
        print_pin(p)

def print_part(p):
    print('Part:', p.name, p.ref)

# for p in SubCircuit.circuit_parts:
    # print_part(p)
    # print('# referers:', sys.getrefcount(p), len(gc.get_referrers(p)), p.is_connected())
    # # for r in gc.get_referrers(p):
        # # print('Referrer:', r)
# for n in SubCircuit.circuit_nets:
    # print_net(n)

SubCircuit.ERC()
SubCircuit.generate_netlist('file.net')