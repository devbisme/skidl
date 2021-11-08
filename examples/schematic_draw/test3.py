from skidl import *

gnd = Part("power", "GND")
vcc = Part("power", "VCC")

opamp = Part(lib="Amplifier_Operational.lib", name="AD8676xR", symtx="V")

for part in default_circuit.parts:
    part.validate()

vcc[1] += opamp[8]
gnd[1] += opamp[4]

r = Part("Device", "R_US", dest=TEMPLATE, tx_ops="L")

(
    Net("IN")
    & r(value="4K7", symtx="L")
    & opamp.uA[2]
    & r(value="4K7", symtx="L")
    & opamp.uA[1]
)
gnd[1] += opamp.uA[3]

opamp.uA[1] & r(value="10K") & gnd[1]

for part in default_circuit.parts:
    part.validate()

generate_svg()
generate_schematic()
generate_netlist()

for part in default_circuit.parts:
    part.validate()

w, h = 5, 5
arr = best_arr = Arranger(default_circuit, w, h)
# best_arr.prearranged()
best_arr.arrange_randomly()
best_cost = best_arr.cost()
# print(f"starting cost = {best_cost}")
# import sys
# sys.exit()

for _ in range(1):
    arr.arrange_randomly()
    arr.arrange_kl()
    cost = arr.cost()
    if cost < best_cost:
        best_arr = arr
        best_cost = cost
        print(f"///// Best arrangement cost = {best_cost:2.2f} /////")
        arr = Arranger(default_circuit, w, h)

best_arr.apply()
for part in best_arr.parts:
    print(f"{part.ref:5s} {part.region.x} {part.region.y}")
print(f"cost = {best_arr.cost()}")
