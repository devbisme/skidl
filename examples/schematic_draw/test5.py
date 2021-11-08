from skidl import *

lib_search_paths[KICAD].append("/home/devb/tech_stuff/KiCad/libraries")
uc = Part(lib="wch.lib", name="CH551G", dest=TEMPLATE)
uc.split_pin_names("/")
usb = Part(lib="Connector.lib", name="USB_B_Micro", symtx="H")

uc1 = uc()
uc1["UDM, UDP"] += usb["D-, D+"]

uc_spare = uc()
uc_spare["UDP"] & uc_spare["UDM"]

stubs = uc1["UDM"].get_nets()
stubs.extend(uc1["UDP"].get_nets())
for s in stubs:
    s.stub = True

generate_svg()
