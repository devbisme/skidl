# Import the skidl library.
from skidl import *

set_default_tool(KICAD8)

# Create input & output voltages and ground reference.
vin, vout, gnd = Net('VI'), Net('VO'), Net('GND')

# Create two resistors.
r1, r2 = 2 * Part("Device", 'R', TEMPLATE, footprint="Resistor_SMD:R_0603_1608Metric")
r1.value = '1K'   # Set upper resistor value.
r2.value = '500'  # Set lower resistor value.

c1 = Part("Device", 'C', footprint="Capacitor_SMD:C_0603_1608Metric")
c1.value = '1u'   # Set capacitor value.

d1 = Part('Device', 'D', footprint='Diode_SMD:D_0603')

# Connect the nets and resistors.
vin & r1 & vout & (r2 | c1[1,2] | d1['K,A']) & gnd

# Output the netlist to a file.
generate_netlist()


######## Now do a SPICE simulation. ########

from skidl.pyspice import *
set_default_tool(SPICE)
lib_search_paths[SPICE]=['../spice-libraries']

# map from skidl to pyspice. 1 is the skidl pin number, p is the pyspice pin number
r1.convert_for_spice(R, {1: "p", 2: "n"})
r2.convert_for_spice(R, {1: "p", 2: "n"})
c1.convert_for_spice(C, {1: "p", 2: "n"})  

# d1.model = '1N4148'
d1.fields['pin_map'] = {'A': 1, 'K': 2}  # pin map is based on the order in the spice model
d1.name = '1N4148'
spice_part = Part("1N4148", '1N4148', dest=TEMPLATE)
ref = d1.ref
d1.convert_for_spice(spice_part, {'A': 1, 'K': 2})

from InSpice import Simulator
from InSpice.Unit import *

circuit = generate_netlist()
print(circuit)

# The rest would be similar to the example from the PySpice documentation:
# https://pyspice.fabrice-salvaire.fr/releases/v1.6/

circuit.V('VI', vin.name, gnd.name, 5@u_V)
try:
    simulator = Simulator.factory()
    simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)
except:
    simulation = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulation.operating_point()

for node in analysis.nodes.values():
    print('Node {}: {:5.2f} V'.format(str(node), float(node[0]))) # Fixme: format value + unit