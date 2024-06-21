import svg_setup
from skidl import *

fpga = Part(lib="FPGA_Lattice", name="ICE40HX8K-BG121")
fpga.uA.symtx = "R"
gnd = Net("GND")
fpga.uA.GND += gnd
fpga.uA.GNDPLL0 += gnd
gnd.stub = True
generate_svg(file_="fpga")
