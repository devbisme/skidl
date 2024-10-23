from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Memory_UniqueID = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'DS2401P', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DS2401P'}), 'ref_prefix':'U', 'fplist':['Package_SO_J-Lead:TSOC-6_3.76x3.94mm_P1.27mm'], 'footprint':'Package_SO_J-Lead:TSOC-6_3.76x3.94mm_P1.27mm', 'keywords':'OneWire 1-Wire 1Wire Maxim Dallas ID', 'description':'', 'datasheet':'http://pdfserv.maximintegrated.com/en/ds/DS2401.pdf', 'search_text':'/usr/share/kicad/symbols/Memory_UniqueID.kicad_sym\nDS2401P\n\nOneWire 1-Wire 1Wire Maxim Dallas ID', 'pins':[
            Pin(num='1',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='2',name='DQ',func=Pin.types.BIDIR,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='5',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='6',name='NC',func=Pin.types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DS2401Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DS2401Z'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:SOT-223'], 'footprint':'Package_TO_SOT_SMD:SOT-223', 'keywords':'OneWire 1-Wire 1Wire Maxim Dallas ID', 'description':'', 'datasheet':'http://pdfserv.maximintegrated.com/en/ds/DS2401.pdf', 'search_text':'/usr/share/kicad/symbols/Memory_UniqueID.kicad_sym\nDS2401Z\n\nOneWire 1-Wire 1Wire Maxim Dallas ID', 'pins':[
            Pin(num='1',name='DQ',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='GND',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] })])