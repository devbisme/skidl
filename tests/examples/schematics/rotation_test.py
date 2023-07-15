from skidl import PartTmplt, generate_schematic

r = PartTmplt("Device.lib", "R")

r(symtx="RL") & r() & r(symtx="RL")

generate_schematic(
    draw_placement=True, rotate_parts=True, compress_before_place=True, normalize=True
)
