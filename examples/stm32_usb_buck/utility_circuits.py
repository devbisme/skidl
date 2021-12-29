from skidl import *


def led(inp, outp, color, resistance):
    d = Part("Device", 'D', footprint='D_0603_1608Metric', value = color)
    r = Part("Device", 'R', footprint='R_0603_1608Metric', value=resistance)
    inp & r & d['a k'] & outp
