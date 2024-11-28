from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Buffer = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'CDCV304', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'CDCV304'}), 'ref_prefix':'U', 'fplist':['Package_SO:TSSOP-8_4.4x3mm_P0.65mm'], 'footprint':'Package_SO:TSSOP-8_4.4x3mm_P0.65mm', 'keywords':'texas quadruple', 'description':'', 'datasheet':'https://www.ti.com/lit/ds/symlink/cdcv304.pdf', 'search_text':'/usr/share/kicad/symbols/Buffer.kicad_sym\nCDCV304\n\ntexas quadruple', 'pins':[
            Pin(num='1',name='CLKIN',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='OE',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='1Y0',func=pin_types.OUTPUT,unit=1),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='1Y1',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='V_{DD}',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='1Y2',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='1Y3',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PI6C5946002ZH', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PI6C5946002ZH'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:TQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm'], 'footprint':'Package_DFN_QFN:TQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm', 'keywords':'buffer clock data', 'description':'', 'datasheet':'https://www.diodes.com/assets/Datasheets/PI6C5946002.pdf', 'search_text':'/usr/share/kicad/symbols/Buffer.kicad_sym\nPI6C5946002ZH\n\nbuffer clock data', 'pins':[
            Pin(num='1',name='Q0+',func=pin_types.OUTPUT,unit=1),
            Pin(num='10',name='VREF-AC',func=pin_types.OUTPUT,unit=1),
            Pin(num='11',name='VTH',func=pin_types.INPUT,unit=1),
            Pin(num='12',name='REF_IN+',func=pin_types.INPUT,unit=1),
            Pin(num='13',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='14',name='VDD',func=pin_types.PASSIVE,unit=1),
            Pin(num='15',name='DNC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='16',name='DNC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='17',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Q0-',func=pin_types.OUTPUT,unit=1),
            Pin(num='3',name='Q1+',func=pin_types.OUTPUT,unit=1),
            Pin(num='4',name='Q1-',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='DNC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='6',name='DNC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='7',name='VDD',func=pin_types.PWRIN,unit=1),
            Pin(num='8',name='EN',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='REF_IN-',func=pin_types.INPUT,unit=1)], 'unit_defs':[] })])