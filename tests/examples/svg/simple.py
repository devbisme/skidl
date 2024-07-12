import svg_setup
from skidl import *

q = Part(lib="Device", name="Q_PNP_CBE", symtx="")
e = Net("E")
q.E += e
q.C += e
# q.C += q.E

c = Part("Device", "C_Polarized")
l = Part("Device", "L")
c | l

fc = Part("Device", "FrequencyCounter")
fc[1] += fc[2]

# layout_options = """
# org.eclipse.elk.layered.spacing.nodeNodeBetweenLayers="5"
# org.eclipse.elk.layered.compaction.postCompaction.strategy="4"
# org.eclipse.elk.spacing.nodeNode="50"
# org.eclipse.elk.direction="LEFT"
# """
# generate_svg(layout_options=layout_options)
generate_svg()
