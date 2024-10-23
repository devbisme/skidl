from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Transistor_FET_Other = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'DN2540N3-G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DN2540N3-G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'N-Channel Depletion-Mode MOSFET', 'description':'', 'datasheet':'https://ww1.microchip.com/downloads/en/DeviceDoc/DN2540%20B060313.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_FET_Other.kicad_sym\nDN2540N3-G\n\nN-Channel Depletion-Mode MOSFET', 'pins':[
            Pin(num='1',name='S',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='G',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='D',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DN2540N5-G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DN2540N5-G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'N-Channel Depletion-Mode MOSFET', 'description':'', 'datasheet':'https://ww1.microchip.com/downloads/en/DeviceDoc/DN2540%20B060313.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_FET_Other.kicad_sym\nDN2540N5-G\n\nN-Channel Depletion-Mode MOSFET', 'pins':[
            Pin(num='1',name='G',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='D',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='S',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DN2540N8-G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DN2540N8-G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'N-Channel Depletion-Mode MOSFET', 'description':'', 'datasheet':'https://ww1.microchip.com/downloads/en/DeviceDoc/DN2540%20B060313.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_FET_Other.kicad_sym\nDN2540N8-G\n\nN-Channel Depletion-Mode MOSFET', 'pins':[
            Pin(num='1',name='G',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='D',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='S',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] })])