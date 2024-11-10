from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Fiber_Optic = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'AFBR-1624Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AFBR-1624Z'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'', 'keywords':'Fiber optic transmitter', 'description':'', 'datasheet':'https://docs.broadcom.com/docs/AV02-4369EN', 'search_text':'/usr/share/kicad/symbols/Fiber_Optic.kicad_sym\nAFBR-1624Z\n\nFiber optic transmitter', 'pins':[
            Pin(num='1',name='VCCT',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='3',name='VEET',func=pin_types.PWRIN,unit=1),
            Pin(num='4',name='Data_in',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='HP',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',name='HP',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'AFBR-2624Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AFBR-2624Z'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'', 'keywords':'fiber optic receiver', 'description':'', 'datasheet':'https://docs.broadcom.com/docs/AV02-4369EN', 'search_text':'/usr/share/kicad/symbols/Fiber_Optic.kicad_sym\nAFBR-2624Z\n\nfiber optic receiver', 'pins':[
            Pin(num='1',name='Data_Out',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='VEER',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='VCCR',func=pin_types.PWRIN,unit=1),
            Pin(num='4',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='5',name='HP',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',name='HP',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] })])