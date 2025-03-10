import os

# Import the skidl library.
from skidl import *
from skidl import KICAD8
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
d1.model = '1N4148'
d1.fields['pin_map'] = {'A': 1, 'K': 2}  # pin map is based on the order in the spice model

# Connect the nets and resistors.
vin += r1[1]      # Connect the input to the upper resistor.
gnd += r2[2]      # Connect the lower resistor to ground.
vout += r1[2], r2[1] # Output comes from the connection of the two resistors.
vout += c1[1]
gnd += c1[2]
vout += d1['K']
gnd += d1['A']


# Output the netlist to a file.
generate_netlist()

# generate_schematic()
# generate_pcb()

####################################################################################################
set_default_tool(SPICE)
from skidl.pyspice import *
# map from skidl to pyspice. 1 is the skidl pin number, p is the pyspice pin number
r1.convert_for_spice(R, {1: "p", 2: "n"})
r2.convert_for_spice(R, {1: "p", 2: "n"})
c1.convert_for_spice(C, {1: "p", 2: "n"})  

d1.name = '1N4148'
spice_part = Part("1N4148", '1N4148', dest=TEMPLATE)
ref = d1.ref
d1.convert_for_spice(spice_part, {'A': 1, 'K': 2})

from PySpice.Doc.ExampleTools import find_libraries
from PySpice import SpiceLibrary, Circuit, Simulator
from PySpice.Unit import *

# libraries_path = find_libraries()
libraries_path = './tests/examples/spice-libraries/'
lib_search_paths[SPICE]=[libraries_path]

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