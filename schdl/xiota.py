from pprint import pprint
from schdl import *
import pdb

xess_lib = SchLib('C:/xesscorp/KiCad/libraries/xess.lib')

psoc = Part('C:/xesscorp/KiCad/libraries/Cypress_cy8c5xlp.lib', 'CY8C52LP-QFN68')
psoc.val = 'CY8C52LP-QFN68'
psoc_u = [PartUnit(psoc,i) for i in range(1,1+int(psoc.definition['unit_count']))]

bypass_caps = [Part(xess_lib,'C-NONPOL') for i in range(10)]
for c in bypass_caps:
    c.val = '1uF'
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

caps = [Part(xess_lib,'C-NONPOL', connections={1:v_5, 2:gnd}, value='1.0uF',tolerance='10%') for i in range(10)]
for c in caps:
    print(c[1].net.name, c[2].net.name)

v_3_3 += psoc_u[0]['VDDD'], bypass_caps[3][1], bypass_caps[4][1], bypass_caps[5][1]
v_3_3_a += psoc_u[0]['VDDA'], bypass_caps[6][1], bypass_caps[7][1]
n = Net()
n += psoc_u[0]['VCCD.*'], bypass_caps[0][1], bypass_caps[1][1]
n = Net()
n += psoc_u[0]['VCCA'], bypass_caps[2][1]
psoc_u[0]['VSS.*'] = gnd

for p in vreg['.*']:
    try:
        print(p.name, p.net.name)
    except:
        pass
print('*'*20)
vreg['GND'] = gnd
v_5 += vreg['IN'], bypass_caps[8][1]
v_5_usb += usb_pwr_jumper[1], usb_pwr_jumper_shrt[1]
for p in vreg['.*']:
    try:
        print(p.name, p.net.name)
    except:
        pass
print('*'*20)
usb_pwr_jumper[1,2] = v_5_usb, v_5
usb_pwr_jumper_shrt[1,2] = v_5_usb, v_5
for p in vreg['.*']:
    try:
        print(p.name, p.net.name)
    except:
        pass
print('*'*20)
#vreg['OUT'].net = bypass_caps[9][1], v33_pwr_jumper[1], v33_pwr_jumper_shrt[1]
v33_pwr_jumper.ref = 'V33'
v33_pwr_jumper[1,2] = vreg['OUT'].net, v_3_3
v33_pwr_jumper_shrt[1,2] = vreg['OUT'].net, v_3_3

ferr_bead[1,2] = v_3_3, v_3_3_a

v_3_3 += bypass_caps[3][1], bypass_caps[4][1], bypass_caps[5][1]
v_3_3_a += bypass_caps[6][1], bypass_caps[7][1]

for c in bypass_caps:
    gnd += c[2]
