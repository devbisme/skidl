from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Driver_Haptic = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'DRV2510-Q1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DRV2510-Q1'}), 'ref_prefix':'U', 'fplist':['Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask3x3mm_ThermalVias'], 'footprint':'Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask3x3mm_ThermalVias', 'keywords':'driver haptic solenoid coil', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/drv2510-q1.pdf', 'pins':[
            Pin(num='1',name='GND',func=Pin.types.PWRIN),
            Pin(num='10',name='BSTN',func=Pin.types.PASSIVE),
            Pin(num='11',name='OUT-',func=Pin.types.PWROUT),
            Pin(num='12',name='OUT+',func=Pin.types.PWROUT),
            Pin(num='13',name='BSTP',func=Pin.types.PASSIVE),
            Pin(num='14',name='INTZ',func=Pin.types.OPENCOLL),
            Pin(num='15',name='VDD',func=Pin.types.PWRIN),
            Pin(num='16',name='GND',func=Pin.types.PASSIVE),
            Pin(num='17',name='GND',func=Pin.types.PASSIVE),
            Pin(num='2',name='EN',func=Pin.types.INPUT),
            Pin(num='3',name='REG',func=Pin.types.PASSIVE),
            Pin(num='4',name='SDA',func=Pin.types.BIDIR),
            Pin(num='5',name='SCL',func=Pin.types.INPUT),
            Pin(num='6',name='IN+',func=Pin.types.INPUT),
            Pin(num='7',name='IN-',func=Pin.types.INPUT),
            Pin(num='8',name='STDBY',func=Pin.types.INPUT),
            Pin(num='9',name='GND',func=Pin.types.PASSIVE)], 'unit_defs':[] }),
        Part(**{ 'name':'DRV2605LDGS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DRV2605LDGS'}), 'ref_prefix':'U', 'fplist':['Package_SO:VSSOP-10_3x3mm_P0.5mm'], 'footprint':'Package_SO:VSSOP-10_3x3mm_P0.5mm', 'keywords':'haptic driver i2c', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/drv2605l.pdf', 'pins':[
            Pin(num='1',name='REG',func=Pin.types.PASSIVE,unit=1),
            Pin(num='10',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='2',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='4',name='IN/TRIG',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='EN',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='VDD/NC',func=Pin.types.PWRIN,unit=1),
            Pin(num='7',name='OUT+',func=Pin.types.OUTPUT,unit=1),
            Pin(num='8',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='9',name='OUT-',func=Pin.types.OUTPUT,unit=1)], 'unit_defs':[] })])