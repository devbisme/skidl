import sys

from skidl import *

q = Part(lib="Device.lib", name="Q_PNP_CBE", dest=TEMPLATE, symtx="V")
r = Part("Device", "R", dest=TEMPLATE)
gndt = Part("power", "GND")
vcct = Part("power", "VCC")

gnd = Net("GND")
vcc = Net("VCC")
gnd & gndt
vcc & vcct
a = Net("A", netio="i")
b = Net("B", netio="i")
a_and_b = Net("A_AND_B", netio="o")
q1 = q()
q1.E.symio = "i"
q1.B.symio = "i"
q1.C.symio = "o"
q2 = q()
q2.E.symio = "i"
q2.B.symio = "i"
q2.C.symio = "o"
r1, r2, r3, r4, r5 = r(5, value="10K")
a & r1 & q1["B", "C"] & r4 & q2["B", "C"] & a_and_b & r5 & gnd
b & r2 & q1["B"]
q1["C"] & r3 & gnd
vcc & q1["E"]
vcc & q2["E"]

# q1.xy = (1,1)
# q2.xy = (2,1)
# r1.xy = (0,0)
# r2.xy = (0,1)
# r3.xy = (1,2)
# r4.xy = (2,1)
# r5.xy = (2,2)
# vcct.xy = (2,0)
# gndt.xy = (1,2)
# gndt.fix = True

generate_svg()
generate_netlist()
sys.exit()

arr = best_arr = Arranger(default_circuit, 3, 3)
# best_arr.prearranged()
best_arr.arrange_randomly()
best_cost = best_arr.cost()
# print(f"starting cost = {best_cost}")
# import sys
# sys.exit()

for _ in range(50):
    arr.arrange_randomly()
    arr.arrange_kl()
    cost = arr.cost()
    if cost < best_cost:
        best_arr = arr
        best_cost = cost
        print(f"///// Best arrangement cost = {best_cost:2.2f} /////")
        arr = Arranger(default_circuit, 3, 3)

best_arr.apply()
for part in default_circuit.parts:
    print(f"{part.ref:5s} {part.region.x} {part.region.y}")
print(f"cost = {best_arr.cost()}")

best_arr.expand_grid(3, 3)
arr = best_arr
for _ in range(50):
    arr.arrange_randomly()
    arr.arrange_kl()
    cost = arr.cost()
    if cost < best_cost:
        best_arr = arr
        best_cost = cost
        print(f"///// Best arrangement cost = {best_cost:2.2f} /////")
        arr = Arranger(default_circuit, 3, 3)

best_arr.apply()
for part in default_circuit.parts:
    print(f"{part.ref:5s} {part.region.x} {part.region.y}")
print(f"cost = {best_arr.cost()}")
