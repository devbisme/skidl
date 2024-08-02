from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Transistor_IGBT = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'IRG4PF50W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IRG4PF50W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-247-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-247-3_Vertical', 'keywords':'N-Channel IGBT Power Transistor', 'description':'', 'datasheet':'http://www.irf.com/product-info/datasheets/data/irg4pf50w.pdf', 'pins':[
            Pin(num='1',name='G',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'STGP7NC60HD', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'STGP7NC60HD'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'N-Channel very fast IGBT with ultrafast diode Power Transistor', 'description':'', 'datasheet':'http://www.farnell.com/datasheets/2309889.pdf', 'pins':[
            Pin(num='1',name='G',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] })])