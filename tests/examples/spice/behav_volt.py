import matplotlib.pyplot as plt

from skidl import *
from skidl.pyspice import *

# lib_search_paths[SPICE] = ["../../test_data/SpiceLib"]

###############################################################################
# This example demonstrates a behavioral voltage source.
###############################################################################

reset()

# Make two test nets
n1, n2 = Net('N1'), Net('N2')

# Add a behavioral source B1 between N1 and N2, trying to set its voltage to a sine wave
b = B(v="sin(2*pi*1k*time)", footprint=None)
b[1, 2] += n1, n2

print(generate_netlist(tool=SPICE))
