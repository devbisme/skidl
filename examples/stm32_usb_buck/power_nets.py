
from skidl import *


v_12v = Net('+12V', stub=True, netclass='Power')
v_5v = Net('+5V', stub=True, netclass='Power')
v_3v3 = Net('+3V3', stub=True, netclass='Power')
gnd = Net('GND', stub=True, netclass='Power')
vdda = Net('+3.3VA', stub=True, netclass='Power')