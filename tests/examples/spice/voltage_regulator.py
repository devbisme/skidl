# Import the skidl library.
from skidl import *

set_default_tool(KICAD8)

# Create input & output voltages and ground reference.
vin, vout, gnd = Net('VI'), Net('VO'), Net('GND')

# Create two resistors.
r1, r2 = 2 * Part("Device", 'R', TEMPLATE, footprint="Resistor_SMD:R_0603_1608Metric")
r1.value = '100K'   # Set upper resistor value.
r2.value = '1K'   # Set lower resistor value.

c1 = Part("Device", 'C', footprint="Capacitor_SMD:C_0603_1608Metric")
c1.value = '1u'   # Set capacitor value.

d1 = Part('Regulator_Switching',  'LM5017MR')

# Connect the nets and resistors.
vin & d1.VIN & r1 & d1.RON
d1.FB & r2 & d1.SW & vout & c1 & gnd

# connect the rest of the pins to gnd
d1['RTN ULVO FB VCC BST RTNPAD'] += gnd

####################################################################################################
from skidl.pyspice import *
set_default_tool(SPICE)
lib_search_paths[SPICE] = ["../../test_data/SpiceLib"]

d1.RTN += gnd

# map from skidl to pyspice. 1 is the skidl pin number, p is the pyspice pin number
r1.convert_for_spice(R, {1: "p", 2: "n"})
r2.convert_for_spice(R, {1: "p", 2: "n"})
c1.convert_for_spice(C, {1: "p", 2: "n"})  

spice_part = Part("regulator_models", d1.name, dest=TEMPLATE)
d1.convert_for_spice(spice_part, {'RTN': '1', 'VIN': '2', 'ULVO': '3', 'RON': '4', 'FB': '5', 'VCC': '6', 'BST': '7', 'SW': '8', 'RTNPAD': '9'})

from InSpice import Simulator
from InSpice.Unit import *

circuit = generate_netlist()
circuit.V('VI', vin.name, gnd.name, 20@u_V)
print(circuit)

# The rest would be similar to the example from the PySpice documentation:
# https://pyspice.fabrice-salvaire.fr/releases/v1.6/

try:
    simulator = Simulator.factory()
    simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)
except:
    simulation = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulation.operating_point()

for node in analysis.nodes.values():
    print(f'Node {str(node)}: {float(node[0]):5.2f} V') # Fixme: format value + unit