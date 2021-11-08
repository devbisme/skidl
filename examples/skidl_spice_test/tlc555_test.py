# Load the package for drawing graphs.
import matplotlib.pyplot as plt
# Omit the following line if you're not using a Jupyter notebook.
# %matplotlib inline

# Load the SKiDL + PySpice packages and initialize them for doing circuit simulations.
from skidl.pyspice import *
import skidl
lib_search_paths[SPICE].append('/media/devb/Main/TEMP/ngspice-33/examples/p-to-n-examples')
print(lib_search_paths[SPICE])

reset()  # Clear out the existing circuitry from the previous example.
# Create a pulsed voltage source, a resistor, and a capacitor.
v2 = V(ref='V2', dc_value=5@u_V)
vreset = PULSEV(ref='VRESET',initial_value=0,pulsed_value=5@u_V,delay_time=1@u_us,rise_time=1@u_us,fall_time=1@u_us,pulse_width=30@u_ms,period=50@u_ms)
ra=R(ref='RA',value=1@u_kOhm)
rb=R(ref='RB',value=5@u_kOhm)
c=C(ref='C',value=0.5@u_uF)
ccont=C(ref='Ccont',value=0.5@u_uF)
rl=R(ref='RL',value=1@u_kOhm)
ra['+','-']+=v2['p'],rb['+']
rl['+']+=v2['p']
c['+']+=rb['-']
x1 = Part('TLC555.LIB','TLC555')
#x1 = Part('NE555','NE555')
c['+']+=x1['THRES'],x1['TRIG']
x1['RESET']+=vreset['p']
x1['OUT']+=rl['-']
x1['DISC']+=rb['+']

x1['VCC']+=v2['p']
x1['CONT']+=ccont['+']
x1['GND']+=gnd
gnd +=v2['n'],c['-'],vreset['n'],ccont['-']
# Simulate the circuit.
circ = generate_netlist()            # Create the PySpice Circuit object from the SKiDL code.
print(circ)
sim = circ.simulator()               # Get a simulator for the Circuit object.
waveforms = sim.transient(step_time=0.01@u_ms, end_time=100@u_ms)  # Run a transient simulation from 0 to 100 msec.
# Get the simulation data.
time = waveforms.time                  # Time values for each point on the waveforms.
# TLC 555 pin names below
thres = waveforms[node(x1['THRES'])]      # Voltage on the positive terminal of the pulsed voltage source.
out = waveforms[node(x1['OUT'])]
disc = waveforms[node(x1['DISC'])]  
figure = plt.figure(1)
plt.title('555 Timer output vs threshold vs. discharge')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
plt.plot(time*1000, thres)
plt.plot(time*1000, out)
plt.plot(time*1000, disc)
plt.legend(('Threshold', 'Output Voltage','Discharge'), loc=(1.1, 0.5))
plt.show()
