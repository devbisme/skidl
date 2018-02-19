import matplotlib.pyplot as plt
from skidl.pyspice import *

lib_search_paths[SPICE].append('SpiceLib')


###############################################################################
# NCP1117 voltage regulator.
###############################################################################

reset()
gnd = Net('0')
lib_search_paths[SPICE].append('SpiceLib')
vin = V(dc_value=8@u_V)  # Input power supply
splib = SchLib('NCP1117')
vreg = Part(splib, 'ncp1117_33-x')  # Voltage regulator.
r = R(value=470 @ u_Ohm)
print(vreg)
vreg['IN', 'OUT'] += vin['p'], r[1]
gnd += vin['n'], r[2], vreg['GND']
print(gnd)
print(vreg['IN'].net)
print(vreg['OUT'].net)
print(node(vreg['IN']))
print(node(vin['p']))

# Simulate the voltage regulator subcircuit.
circ = generate_netlist(libs='SpiceLib') # Pass-in the library where the voltage regulator subcircuit is stored.
sim = circ.simulator()
dc_vals = sim.dc(**{vin.ref:slice(0,10,0.1)})

# Get the input and output voltages.
inp = dc_vals[node(vin['p'])]
outp = dc_vals[node(vreg['OUT'])]

# Plot the input and output waveforms. The output will be the inverse of the input since it passed
# through three inverters.
figure = plt.figure(1)
plt.title('Output Voltage vs. Input Voltage')
plt.xlabel('Input Voltage (V)')
plt.ylabel('Output Voltage (V)')
plt.plot(inp, outp)
plt.show()

# import sys
# sys.exit()


###############################################################################
# Current-controlled switch.
###############################################################################

reset()  # Clear out the existing circuitry from the previous example.

# Create a switch, power supply, drain resistor, and an input pulse source.
#sw = CCS(model='CCS1')
vdc = V(dc_value=10@u_V)    # 10V power supply.
rl = R(value=4.7@u_kOhm)    # load resistor in series with power supply.
isrc = PULSEI(initial_value=0@u_mA, pulsed_value=2@u_mA, pulse_width=1@u_ms, period=2@u_ms)  # 1ms ON, 1ms OFF pulses.
vsrc = V(dc_value=0@u_V)
vdc['p', 'n'] += rl[1], gnd # Connect power supply to load resistor and ground.
isrc['p', 'n'] += vsrc['n'], gnd              # Connect negative terminal of pulse source to ground.
vsrc['p'] += gnd
sw = CCS(source=vsrc, model='CCS1', initial_state='OFF')
#sw.source = isrc
print(sw)
sw['p', 'n'] += rl[2], gnd

# Simulate the transistor amplifier. This requires a SPICE library containing a model of the 2N2222A transistor.
circ = generate_netlist(libs='SpiceLib')  # Pass the directory to the SPICE model library when creating circuit.
sim = circ.simulator()
print(sim)
waveforms = sim.transient(step_time=0.01@u_ms, end_time=5@u_ms)

# Get the input source and amplified output waveforms.
time = waveforms.time
vout = waveforms[node(sw['p'])]  # Voltage at drain of the MOSFET.

# Plot the input and output waveforms.
figure = plt.figure(1)
plt.title('Current-Controlled Switch Inverter Output Vs. Input Voltage')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
#plt.plot(time*1000, vin)
plt.plot(time*1000, vout)
plt.legend(('Input Voltage', 'Output Voltage'), loc=(1.1, 0.5))
plt.show()

# import sys
# sys.exit()


###############################################################################
# Voltage-controlled switch.
###############################################################################

reset()  # Clear out the existing circuitry from the previous example.

# Create a switch, power supply, drain resistor, and an input pulse source.
#sw = VCS(model='VCS1', initial_state='OFF')
sw = VCS(model='VCS1')
vdc = V(dc_value=10@u_V)    # 10V power supply.
rl = R(value=4.7@u_kOhm)    # load resistor in series with power supply.
vs = PULSEV(initial_value=0@u_V, pulsed_value=2@u_V, pulse_width=1@u_ms, period=2@u_ms)  # 1ms ON, 1ms OFF pulses.
vdc['p', 'n'] += rl[2], gnd # Connect power supply to load resistor and ground.
vs['n'] += gnd              # Connect negative terminal of pulse source to ground.
sw['ip', 'in'] += vs['p'], gnd
sw['op', 'on'] += rl[1], gnd

# Simulate the transistor amplifier. This requires a SPICE library containing a model of the 2N2222A transistor.
circ = generate_netlist(libs='SpiceLib')  # Pass the directory to the SPICE model library when creating circuit.
print(circ)
sim = circ.simulator() 
waveforms = sim.transient(step_time=0.01@u_ms, end_time=5@u_ms)

# Get the input source and amplified output waveforms.
time = waveforms.time
vin = waveforms[node(vs['p'])]  # Input source voltage.
vout = waveforms[node(sw['op'])]  # Voltage at drain of the MOSFET.

# Plot the input and output waveforms.
figure = plt.figure(1)
plt.title('Voltage-Controlled Switch Inverter Output Vs. Input Voltage')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
plt.plot(time*1000, vin)
plt.plot(time*1000, vout)
plt.legend(('Input Voltage', 'Output Voltage'), loc=(1.1, 0.5))
plt.show()

# import sys
# sys.exit()


###############################################################################
# MOSFET switch.
###############################################################################

reset()  # Clear out the existing circuitry from the previous example.

# Create a transistor, power supply, drain resistor, and an input pulse source.
q = M(model='MOD1')         # N-channel MOSFET. The model is stored in a directory of SPICE .lib files.
vdc = V(dc_value=10@u_V)    # 10V power supply.
rd = R(value=4.7@u_kOhm)    # Drain resistor in series with power supply.
vs = PULSEV(initial_value=0@u_V, pulsed_value=5@u_V, pulse_width=1@u_ms, period=2@u_ms)  # 1ms ON, 1ms OFF pulses.
q['s', 'd', 'g', 'b'] += gnd, rd[1], vs['p'], gnd  # Connect MOSFET pins to ground, drain resistor and pulse source.
vdc['p', 'n'] += rd[2], gnd # Connect power supply to drain resistor and ground.
vs['n'] += gnd              # Connect negative terminal of pulse source to ground.

# Simulate the transistor amplifier. This requires a SPICE library containing a model of the 2N2222A transistor.
circ = generate_netlist(libs='SpiceLib')  # Pass the directory to the SPICE model library when creating circuit.
print(circ)
sim = circ.simulator() 
waveforms = sim.transient(step_time=0.01@u_ms, end_time=5@u_ms)

# Get the input source and amplified output waveforms.
time = waveforms.time
vin = waveforms[node(q['g'])]  # Input source voltage.
vout = waveforms[node(q['d'])]  # Voltage at drain of the MOSFET.

# Plot the input and output waveforms.
figure = plt.figure(1)
plt.title('MOSFET Inverter Output Vs. Input Voltage')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
plt.plot(time*1000, vin)
plt.plot(time*1000, vout)
plt.legend(('Input Voltage', 'Output Voltage'), loc=(1.1, 0.5))
plt.show()

# import sys
# sys.exit()


###############################################################################
# Transistor amplifier.
###############################################################################

reset()  # Clear out the existing circuitry from the previous example.

# Create a transistor, power supply, bias resistors, collector resistor, and an input sine wave source.
q = BJT(model='2n2222a')    # 2N2222A NPN transistor. The model is stored in a directory of SPICE .lib files.
vdc = V(dc_value=5@u_V)     # 5V power supply.
rs = R(value=5@u_kOhm)      # Source resistor in series with sine wave input voltage.
rb = R(value=25@u_kOhm)     # Bias resistor from 5V to base of transistor.
rc = R(value=1@u_kOhm)      # Load resistor connected to collector of transistor.
vs = SINEV(amplitude=0.01@u_V, frequency=1@u_kHz)  # 1 KHz sine wave input source.
q['c', 'b', 'e'] += rc[1], rb[1], gnd  # Connect transistor CBE pins to load & bias resistors and ground.
vdc['p'] += rc[2], rb[2]    # Connect other end of load and bias resistors to power supply's positive terminal.
vdc['n'] += gnd             # Connect negative terminal of power supply to ground.
rs[1,2] += vs['p'], q['b']  # Connect source resistor from input source to base of transistor.
vs['n'] += gnd              # Connect negative terminal of input source to ground.

# Simulate the transistor amplifier. This requires a SPICE library containing a model of the 2N2222A transistor.
circ = generate_netlist(libs='SpiceLib')  # Pass the directory to the SPICE model library when creating circuit.
print(circ)
sim = circ.simulator() 
waveforms = sim.transient(step_time=0.01@u_ms, end_time=5@u_ms)

# Get the input source and amplified output waveforms.
time = waveforms.time
vin = waveforms[node(vs['p'])]  # Input source voltage.
vout = waveforms[node(q['c'])]  # Amplified output voltage at collector of the transistor.

# Plot the input and output waveforms.
figure = plt.figure(1)
plt.title('Transistor Amplifier Output Voltage vs. Input Voltage')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
plt.plot(time*1000, vin)
plt.plot(time*1000, vout)
plt.legend(('Input Voltage', 'Output Voltage'), loc=(1.1, 0.5))
plt.show()


###############################################################################
# Resistor-Diode driven by pulses.
###############################################################################

reset()

# Create a pulsed voltage source, a resistor, and a capacitor.
vs = PULSEV(initial_value=-5@u_V, pulsed_value=5@u_V, pulse_width=1@u_ms, period=2@u_ms)  # 1ms ON, 1ms OFF pulses.
r = R(value=100@u_Ohm)    # 1 Kohm resistor.
d = D(model='DI_BAV21W') # Diode.
d['p', 'n'] += vs['p'], r[1]  # Connect the diode between the positive source terminal and one of the resistor terminals.
gnd += vs['n'], r[2]     # Connect the negative battery terminal and the other resistor terminal to ground.

# Simulate the circuit.
circ = generate_netlist()            # Create the PySpice Circuit object from the SKiDL code.
print(circ)
sim = circ.simulator()               # Get a simulator for the Circuit object.
waveforms = sim.transient(step_time=0.01@u_ms, end_time=10@u_ms)  # Run a transient simulation from 0 to 10 msec.

# Get the simulation data.
time = waveforms.time                # Time values for each point on the waveforms.
pulses = waveforms[node(vs['p'])]    # Voltage on the positive terminal of the pulsed voltage source.
res_voltage = waveforms[node(r[1])]  # Voltage on the resistor.

# Plot the pulsed source and capacitor voltage values versus time.
figure = plt.figure(1)
plt.title('Resistor Voltage Vs. Input Voltage Passed Through Diode')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
plt.plot(time*1000, pulses)       # Plot pulsed source waveform.
plt.plot(time*1000, res_voltage)  # Plot resistor charging waveform.
plt.legend(('Source Pulses', 'Resistor Voltage'), loc=(1.1, 0.5))
plt.show()


###############################################################################
# Current through resistor.
###############################################################################

reset()  # This will clear any previously defined circuitry.

# Create and interconnect the components.
vs = V(ref='VS', dc_value = 1 @ u_V)  # Create a voltage source named "VS" with an initial value of 1 volt.
r1 = R(value = 1 @ u_kOhm)            # Create a 1 Kohm resistor.
vs['p'] += r1[1]       # Connect one end of the resistor to the positive terminal of the voltage source.
gnd += vs['n'], r1[2]  # Connect the other end of the resistor and the negative terminal of the source to ground.

# Simulate the circuit.
circ = generate_netlist()              # Translate the SKiDL code into a PyCircuit Circuit object.
sim = circ.simulator()                 # Create a simulator for the Circuit object.
dc_vals = sim.dc(VS=slice(0, 1, 0.1))  # Run a DC simulation where the voltage ramps from 0 to 1V by 0.1V increments.

# Get the voltage applied to the resistor and the current coming out of the voltage source.
voltage = dc_vals[node(vs['p'])]  # Get the voltage applied by the positive terminal of the source.
current = -dc_vals['VS']  # Get the current coming out of the positive terminal of the voltage source.

# Print a table showing the current through the resistor for the various applied voltages.
print('{:^7s}{:^7s}'.format('V', ' I (mA)'))
print('='*15)
for v, i in zip(voltage.as_ndarray(), current.as_ndarray()*1000):
    #print('{:6.2f} {:6.2f}'.format(v, i))
    print('{:6.2f} {:6.2f}'.format(v, i))

# Create a plot of the current (Y coord) versus the applied voltage (X coord).
figure = plt.figure(1)
plt.title('Resistor Current vs. Applied Voltage')
plt.xlabel('Voltage (V)')
plt.ylabel('Current (mA)')
plt.plot(voltage, current*1000) # Plot X=voltage and Y=current (in milliamps, so multiply it by 1000).
plt.show()


###############################################################################
# Resistor-capacitor driven by pulses.
###############################################################################

reset()

# Create a pulsed voltage source, a resistor, and a capacitor.
vs = PULSEV(initial_value=0, pulsed_value=5@u_V, pulse_width=1@u_ms, period=2@u_ms)  # 1ms ON, 1ms OFF pulses.
r = R(value=1@u_kOhm)    # 1 Kohm resistor.
c = C(value=1@u_uF)      # 1 uF capacitor.
r[1,2] += vs['p'], c[1]  # Connect the resistor between the positive source terminal and one of the capacitor terminals.
gnd += vs['n'], c[2]     # Connect the negative battery terminal and the other capacitor terminal to ground.

# Simulate the circuit.
circ = generate_netlist()            # Create the PySpice Circuit object from the SKiDL code.
sim = circ.simulator()               # Get a simulator for the Circuit object.
waveforms = sim.transient(step_time=0.01@u_ms, end_time=10@u_ms)  # Run a transient simulation from 0 to 10 msec.

# Get the simulation data.
time = waveforms.time                # Time values for each point on the waveforms.
pulses = waveforms[node(vs['p'])]    # Voltage on the positive terminal of the pulsed voltage source.
cap_voltage = waveforms[node(c[1])]  # Voltage on the capacitor.

# Plot the pulsed source and capacitor voltage values versus time.
figure = plt.figure(1)
plt.title('Capacitor Voltage vs. Source Pulses')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
plt.plot(time*1000, pulses)       # Plot pulsed source waveform.
plt.plot(time*1000, cap_voltage)  # Plot capacitor charging waveform.
plt.legend(('Source Pulses', 'Capacitor Voltage'), loc=(1.1, 0.5))
plt.show()


###############################################################################
# Resistor-inductor driven by pulses.
###############################################################################

reset()

# Create a pulsed voltage source, a resistor, and a capacitor.
vs = PULSEV(initial_value=0, pulsed_value=5@u_V, pulse_width=1@u_ms, period=2@u_ms)  # 1ms ON, 1ms OFF pulses.
r = R(value=10@u_Ohm)    # 1 Kohm resistor.
l = L(value=10@u_mH)     # 1 uF inductor.
r[1,2] += vs['p'], l[1]  # Connect the resistor between the positive source terminal and one of the inductor terminals.
gnd += vs['n'], l[2]     # Connect the negative battery terminal and the other capacitor terminal to ground.

# Simulate the circuit.
circ = generate_netlist()            # Create the PySpice Circuit object from the SKiDL code.
print(circ)
sim = circ.simulator()               # Get a simulator for the Circuit object.
waveforms = sim.transient(step_time=0.01@u_ms, end_time=10@u_ms)  # Run a transient simulation from 0 to 10 msec.

# Get the simulation data.
time = waveforms.time                # Time values for each point on the waveforms.
pulses = waveforms[node(vs['p'])]    # Voltage on the positive terminal of the pulsed voltage source.
ind_voltage = waveforms[node(l[1])]  # Voltage on the capacitor.

# Plot the pulsed source and capacitor voltage values versus time.
figure = plt.figure(1)
plt.title('Inductor Voltage vs. Source Pulses')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
plt.plot(time*1000, pulses)       # Plot pulsed source waveform.
plt.plot(time*1000, ind_voltage)  # Plot capacitor charging waveform.
plt.legend(('Source Pulses', 'Inductor Voltage'), loc=(1.1, 0.5))
plt.show()
