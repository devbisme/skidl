from skidl.pyspice import *

set_default_tool(KICAD)

vcc = Part("Device", "Battery", value=5 @ u_V)
r1 = Part("Device", "R", value=1 @ u_kOhm)
r2 = Part("Device", "R", value=2 @ u_kOhm)

vcc.convert_for_spice(V, {1: "p", 2: "n"})
r1.convert_for_spice(R, {1: "p", 2: "n"})
r2.convert_for_spice(R, {1: "p", 2: "n"})

vin, vout, gnd = Net("Vin"), Net("Vout"), Net("GND")
vin.netio = "i"
vout.netio = "o"
gnd.netio = "o"

gnd & vcc["n p"] & vin & r1 & vout & r2 & gnd

generate_svg()

set_default_tool(SPICE)
circ = generate_netlist()
print(circ)
sim = circ.simulator()
analysis = sim.dc(V1=slice(0, 5, 0.5))

dc_vin = analysis.Vin
dc_vout = analysis.Vout

print("{:^7s}{:^7s}".format("Vin (V)", " Vout (V)"))
print("=" * 15)
for v, i in zip(dc_vin.as_ndarray(), dc_vout.as_ndarray()):
    print("{:6.2f} {:6.2f}".format(v, i))
