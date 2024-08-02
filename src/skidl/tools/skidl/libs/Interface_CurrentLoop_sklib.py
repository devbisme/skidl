from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Interface_CurrentLoop = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'XTR111AxDGQ', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'XTR111AxDGQ'}), 'ref_prefix':'U', 'fplist':['Package_SO:MSOP-10-1EP_3x3mm_P0.5mm_EP2.2x3.1mm_Mask1.83x1.89mm_ThermalVias'], 'footprint':'Package_SO:MSOP-10-1EP_3x3mm_P0.5mm_EP2.2x3.1mm_Mask1.83x1.89mm_ThermalVias', 'keywords':'0-20mA 4-20mA Current Loop Transmitter Voltage To Current', 'description':'', 'datasheet':'https://www.ti.com/lit/ds/symlink/xtr111.pdf', 'pins':[
            Pin(num='1',name='VSP',func=Pin.types.PWRIN,unit=1),
            Pin(num='10',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='11',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='IS',func=Pin.types.OUTPUT,unit=1),
            Pin(num='3',name='VG',func=Pin.types.OUTPUT,unit=1),
            Pin(num='4',name='REGS',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='REGF',func=Pin.types.OUTPUT,unit=1),
            Pin(num='6',name='VIN',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='SET',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='~{EF}',func=Pin.types.OPENCOLL,unit=1),
            Pin(num='9',name='OD',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'XTR115U', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'XTR115U'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'4-20mA Current Loop Transmitter', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/xtr115.pdf', 'pins':[
            Pin(num='1',name='VREF',func=Pin.types.OUTPUT,unit=1),
            Pin(num='2',name='IIN',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='IRET',func=Pin.types.INPUT,unit=1),
            Pin(num='4',name='IO',func=Pin.types.PASSIVE,unit=1),
            Pin(num='5',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='B',func=Pin.types.OUTPUT,unit=1),
            Pin(num='7',name='V+',func=Pin.types.OUTPUT,unit=1),
            Pin(num='8',name='VREG',func=Pin.types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'XTR116U', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'XTR116U'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'4-20mA Current Loop Transmitter', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/xtr115.pdf', 'pins':[
            Pin(num='1',name='VREF',func=Pin.types.OUTPUT,unit=1),
            Pin(num='2',name='IIN',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='IRET',func=Pin.types.INPUT,unit=1),
            Pin(num='4',name='IO',func=Pin.types.PASSIVE,unit=1),
            Pin(num='5',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='B',func=Pin.types.OUTPUT,unit=1),
            Pin(num='7',name='V+',func=Pin.types.OUTPUT,unit=1),
            Pin(num='8',name='VREG',func=Pin.types.OUTPUT,unit=1)], 'unit_defs':[] })])