from skidl import *

# Create input & output voltages and ground reference.
vin, vout, gnd = Net("VI"), Net("VO"), Net("GND")

# Create two resistors.
r1, r2 = 2 * Part("device", "R", TEMPLATE, footprint="Resistors_SMD:R_0805")
r1.value = "1K"  # Set upper resistor value.
r2.value = "500"  # Set lower resistor value.

# Connect the nets and resistors.
vin += r1[1]  # Connect the input to the upper resistor.
gnd += r2[2]  # Connect the lower resistor to ground.
vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

print(generate_netlist())
