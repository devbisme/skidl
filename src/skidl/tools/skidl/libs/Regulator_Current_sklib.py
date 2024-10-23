from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Regulator_Current = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'HV100K5-G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'HV100K5-G'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'Hot-Swap Current Limiter', 'description':'', 'datasheet':'http://ww1.microchip.com/downloads/en/devicedoc/hv100%20b060513.pdf', 'search_text':'/usr/share/kicad/symbols/Regulator_Current.kicad_sym\nHV100K5-G\n\nHot-Swap Current Limiter', 'pins':[
            Pin(num='1',name='VPP',func=Pin.types.PWRIN,unit=1),
            Pin(num='2',name='VNN',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='GATE',func=Pin.types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'HV101K5-G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'HV101K5-G'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'Hot-Swap Current Limiter', 'description':'', 'datasheet':'http://www.supertex.com/pdf/datasheets/HV100.pdf', 'search_text':'/usr/share/kicad/symbols/Regulator_Current.kicad_sym\nHV101K5-G\n\nHot-Swap Current Limiter', 'pins':[
            Pin(num='1',name='VPP',func=Pin.types.PWRIN,unit=1),
            Pin(num='2',name='VNN',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='GATE',func=Pin.types.OUTPUT,unit=1)], 'unit_defs':[] })])