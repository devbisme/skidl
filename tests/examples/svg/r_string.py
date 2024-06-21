import svg_setup
from skidl import *
import sys

# q = Part(lib='Device.lib', name='Q_PNP_CBE', dest=TEMPLATE, symtx='V')
r = Part("Device", "R", dest=TEMPLATE)
gndt = Part("power", "GND")
vcct = Part("power", "VCC")

gnd = Net("GND")
vcc = Net("VCC")
(
    gnd
    & gndt
    & r()
    & r()
    & (r(symtx="l") | r(symtx="R"))
    & r()
    & r()
    & r()
    & r()
    & r()
    & r()
    & r()
    & vcct
    & vcc
)

generate_svg()
sys.exit()
generate_netlist()

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
