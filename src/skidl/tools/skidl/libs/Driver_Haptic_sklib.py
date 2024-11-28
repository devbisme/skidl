from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Driver_Haptic = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'DRV2510-Q1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DRV2510-Q1'}), 'ref_prefix':'U', 'fplist':['Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask3x3mm_ThermalVias'], 'footprint':'Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask3x3mm_ThermalVias', 'keywords':'driver haptic solenoid coil', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/drv2510-q1.pdf', 'search_text':'/usr/share/kicad/symbols/Driver_Haptic.kicad_sym\nDRV2510-Q1\n\ndriver haptic solenoid coil', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN),
            Pin(num='10',name='BSTN',func=pin_types.PASSIVE),
            Pin(num='11',name='OUT-',func=pin_types.PWROUT),
            Pin(num='12',name='OUT+',func=pin_types.PWROUT),
            Pin(num='13',name='BSTP',func=pin_types.PASSIVE),
            Pin(num='14',name='INTZ',func=pin_types.OPENCOLL),
            Pin(num='15',name='VDD',func=pin_types.PWRIN),
            Pin(num='16',name='GND',func=pin_types.PASSIVE),
            Pin(num='17',name='GND',func=pin_types.PASSIVE),
            Pin(num='2',name='EN',func=pin_types.INPUT),
            Pin(num='3',name='REG',func=pin_types.PASSIVE),
            Pin(num='4',name='SDA',func=pin_types.BIDIR),
            Pin(num='5',name='SCL',func=pin_types.INPUT),
            Pin(num='6',name='IN+',func=pin_types.INPUT),
            Pin(num='7',name='IN-',func=pin_types.INPUT),
            Pin(num='8',name='STDBY',func=pin_types.INPUT),
            Pin(num='9',name='GND',func=pin_types.PASSIVE)], 'unit_defs':[] }),
        Part(**{ 'name':'DRV2605LDGS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DRV2605LDGS'}), 'ref_prefix':'U', 'fplist':['Package_SO:VSSOP-10_3x3mm_P0.5mm'], 'footprint':'Package_SO:VSSOP-10_3x3mm_P0.5mm', 'keywords':'haptic driver i2c', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/drv2605l.pdf', 'search_text':'/usr/share/kicad/symbols/Driver_Haptic.kicad_sym\nDRV2605LDGS\n\nhaptic driver i2c', 'pins':[
            Pin(num='1',name='REG',func=pin_types.PASSIVE,unit=1),
            Pin(num='10',name='VDD',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='SCL',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='SDA',func=pin_types.BIDIR,unit=1),
            Pin(num='4',name='IN/TRIG',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='EN',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='VDD/NC',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='OUT+',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='9',name='OUT-',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] })])