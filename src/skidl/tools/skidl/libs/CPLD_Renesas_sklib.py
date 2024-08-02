from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

CPLD_Renesas = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'SLG46826G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SLG46826G'}), 'ref_prefix':'U', 'fplist':['Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm'], 'footprint':'Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm', 'keywords':'cpld programmable logic low-cost renesas silego', 'description':'', 'datasheet':'https://www.renesas.com/in/en/document/dst/slg46826-datasheet', 'pins':[
            Pin(num='1',name='IO14',func=Pin.types.BIDIR,unit=1),
            Pin(num='10',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='11',name='IO6',func=Pin.types.OUTPUT,unit=1),
            Pin(num='12',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='13',name='SCL',func=Pin.types.BIDIR,unit=1),
            Pin(num='14',name='IO5',func=Pin.types.BIDIR,unit=1),
            Pin(num='15',name='IO4',func=Pin.types.BIDIR,unit=1),
            Pin(num='16',name='IO3',func=Pin.types.BIDIR,unit=1),
            Pin(num='17',name='IO2',func=Pin.types.BIDIR,unit=1),
            Pin(num='18',name='IO1',func=Pin.types.BIDIR,unit=1),
            Pin(num='19',name='IO0',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='IO13',func=Pin.types.BIDIR,unit=1),
            Pin(num='20',name='V_{DD}',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='IO12',func=Pin.types.BIDIR,unit=1),
            Pin(num='4',name='IO11',func=Pin.types.BIDIR,unit=1),
            Pin(num='5',name='IO10',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='IO9',func=Pin.types.BIDIR,unit=1),
            Pin(num='7',name='V_{DD2}',func=Pin.types.PWRIN,unit=1),
            Pin(num='8',name='IO8',func=Pin.types.BIDIR,unit=1),
            Pin(num='9',name='IO7',func=Pin.types.OUTPUT,unit=1)], 'unit_defs':[] })])