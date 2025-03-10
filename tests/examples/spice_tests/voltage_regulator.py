import os

# Import the skidl library.
from skidl import *
from skidl import KICAD8
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
d1.model = d1.value
d1.fields['pin_map'] = {'RTN': '1', 'VIN': '2', 'ULVO': '3', 'RON': '4', 'FB': '5', 'VCC': '6', 'BST': '7', 'SW': '8', 'RTNPAD': '9'}



# Connect the nets and resistors.
vin += r1[1]      # Connect the input to the upper resistor.
d1['RON'] += r1[2] # Output comes from the connection of the two resistors.
vout += c1[1]
gnd += c1[2]
d1['FB'] += r2[1]
vout += r2[2]
vin += d1['VIN']
gnd += d1['RTN']
vout += d1['SW']
# connect the rest of the pins to gnd
for pin in d1.pins:
    if pin.name in ['ULVO', 'FB', 'VCC', 'BST', 'RTNPAD']:
        gnd += d1[pin.name]

# Output the netlist to a file.
# generate_netlist()

# generate_schematic()
# generate_pcb()

####################################################################################################
set_default_tool(SPICE)
# from skidl.pyspice import *
# r1.convert_for_spice(R, {1: "p", 2: "n"})

from PySpice.Doc.ExampleTools import find_libraries
from PySpice import SpiceLibrary, Circuit, Simulator
from PySpice.Unit import *

# libraries_path = find_libraries()
libraries_path = './tests/examples/spice-library/'
lib_search_paths[SPICE]=[libraries_path]

circuit = generate_netlist()
print(circuit)

# The rest would be similar to the example from the PySpice documentation:
# https://pyspice.fabrice-salvaire.fr/releases/v1.6/

circuit.V('VI', vin.name, gnd.name, 20@u_V)
try:
    simulator = Simulator.factory()
    simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)
except:
    simulation = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulation.operating_point()

for node in analysis.nodes.values():
    print('Node {}: {:5.2f} V'.format(str(node), float(node[0]))) # Fixme: format value + unit