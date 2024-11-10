from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Interface_CurrentLoop = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'XTR111AxDGQ', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'XTR111AxDGQ'}), 'ref_prefix':'U', 'fplist':['Package_SO:MSOP-10-1EP_3x3mm_P0.5mm_EP2.2x3.1mm_Mask1.83x1.89mm_ThermalVias'], 'footprint':'Package_SO:MSOP-10-1EP_3x3mm_P0.5mm_EP2.2x3.1mm_Mask1.83x1.89mm_ThermalVias', 'keywords':'0-20mA 4-20mA Current Loop Transmitter Voltage To Current', 'description':'', 'datasheet':'https://www.ti.com/lit/ds/symlink/xtr111.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_CurrentLoop.kicad_sym\nXTR111AxDGQ\n\n0-20mA 4-20mA Current Loop Transmitter Voltage To Current', 'pins':[
            Pin(num='1',name='VSP',func=pin_types.PWRIN,unit=1),
            Pin(num='10',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='11',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='IS',func=pin_types.OUTPUT,unit=1),
            Pin(num='3',name='VG',func=pin_types.OUTPUT,unit=1),
            Pin(num='4',name='REGS',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='REGF',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='VIN',func=pin_types.INPUT,unit=1),
            Pin(num='7',name='SET',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',name='~{EF}',func=pin_types.OPENCOLL,unit=1),
            Pin(num='9',name='OD',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'XTR115U', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'XTR115U'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'4-20mA Current Loop Transmitter', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/xtr115.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_CurrentLoop.kicad_sym\nXTR115U\n\n4-20mA Current Loop Transmitter', 'pins':[
            Pin(num='1',name='VREF',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='IIN',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='IRET',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='IO',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='E',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='B',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='V+',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='VREG',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'XTR116U', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'XTR116U'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'4-20mA Current Loop Transmitter', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/xtr115.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_CurrentLoop.kicad_sym\nXTR116U\n\n4-20mA Current Loop Transmitter', 'pins':[
            Pin(num='1',name='VREF',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='IIN',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='IRET',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='IO',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='E',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='B',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='V+',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='VREG',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] })])