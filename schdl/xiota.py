from pprint import pprint
from schdl import *
import pdb

xess_lib = SchLib('C:/xesscorp/KiCad/libraries/xess.lib')

psoc = Part('C:/xesscorp/KiCad/libraries/Cypress_cy8c5xlp.lib', 'CY8C52LP-QFN68')
psoc.val = 'CY8C52LP-QFN68'
psoc.ref = 'UPSOC1'
psoc_u = (psoc.unit(i) for i in range(1,1+int(psoc.definition['unit_count'])))
psoc_u = psoc.unit(6,slice(6,8))
for p in psoc_u.pins:
    print(p.unit, p.name, p.num, p.part.name, p.part.ref)


def circuit(circuit_func):
    def wrapper(*args, **kwargs):
        upper_circuit_nets = circuit_nets
        circuit_nets = []
        upper_circuit_parts = circuit_parts
        circuit_parts = []
        circuit_name = upper_circuit_name + '.' + 'kdnj'
        results = circuit_func(*args, **kwargs)
        merge(upper_nets, circuit_nets)
        merge(upper_parts, circuit_parts)
        circuit_parts = upper_circuit_parts
        circuit_nets = upper_circuit_nets
        return results

    return wrapper

@circuit
res_divider(in1, out1):
    r1 = Part('C:/xesscorp/KiCad/Libraries/xess.lib', 'R')
    r2 = r1.copy()
    r1.val = '1K6'
    r2.val = '500K3'
    r1[1] = in1
    out1 += r1[2], r2[1]
    r2[2] = gnd

a = Net('A')
b = Net('B')
c = Net('C')
res_divider(a,b)
res_divider(b,c)

    

psoc_uu = []
for u in psoc_u:
    psoc_uu.append(u)

psoc_u1 = psoc_u1 * 10

bypass_caps = 10 * Part(xess_lib,'C-NONPOL', val='1uF')
bypass_caps[3].val = '0.1uF'
bypass_caps[4].val = '0.1uF'
bypass_caps[7].val = '0.1uF'

ferr_bead = Part(xess_lib,'.*FERRITE.*')
ferr_bead.val = '10uH'

vreg = Part(xess_lib,'1117')
usb_pwr_jumper, v33_pwr_jumper = [Part(xess_lib,'JUMPER') for i in range(2)]
usb_pwr_jumper_shrt, v33_pwr_jumper_shrt = [Part(xess_lib,'JSHORTNORMAL') for i in range(2)]

v_5 = Net('+5V')
v_5_usb = Net('+5V-USB')
v_3_3 = Net('+3.3V')
v_3_3_a = Net('+3.3V-A')
gnd = Net('GND')

v_3_3 += psoc_u[0]['VDDD'], bypass_caps[3][1], bypass_caps[4][1], bypass_caps[5][1]
v_3_3_a += psoc_u[0]['VDDA'], bypass_caps[6][1], bypass_caps[7][1]
n = Net()
n += psoc_u[0]['VCCD.*'], bypass_caps[0][1], bypass_caps[1][1]
n = Net()
n += psoc_u[0]['VCCA'], bypass_caps[2][1]
psoc_u[0]['VSS.*'] = gnd

vreg['GND'] = gnd
v_5 += vreg['IN'], bypass_caps[8][1]
v_5_usb += usb_pwr_jumper[1], usb_pwr_jumper_shrt[1]
usb_pwr_jumper[1,2] = v_5_usb, v_5
usb_pwr_jumper_shrt[1,2] = v_5_usb, v_5
#vreg['OUT'].net = bypass_caps[9][1], v33_pwr_jumper[1], v33_pwr_jumper_shrt[1]
v33_pwr_jumper.ref = 'V33'
v33_pwr_jumper[1,2] = vreg['OUT'].net, v_3_3
v33_pwr_jumper_shrt[1,2] = vreg['OUT'].net, v_3_3

ferr_bead[1,2] = v_3_3, v_3_3_a

v_3_3 += bypass_caps[3][1], bypass_caps[4][1], bypass_caps[5][1]
v_3_3_a += bypass_caps[6][1], bypass_caps[7][1]

for c in bypass_caps:
    gnd += c[2]
