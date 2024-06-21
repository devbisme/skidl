import svg_setup
from skidl import *

uc = Part(lib="MCU_Microchip_PIC18", name="PIC18F27J53_ISS", dest=TEMPLATE)
uc.split_pin_names("/")
usb = Part(lib="Connector", name="USB_B_Micro", symtx="H")

uc1 = uc()
uc1["D-, D+"] += usb["D-, D+"]

uc_spare = uc()
uc_spare["D+"] & uc_spare["D-"]

stubs = uc1["D-"].get_nets()
stubs.extend(uc1["D+"].get_nets())
for s in stubs:
    s.stub = True

generate_svg()
