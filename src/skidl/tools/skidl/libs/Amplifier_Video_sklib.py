from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Amplifier_Video = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'AD813', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AD813'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'', 'keywords':'triple opamp', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/AD813.pdf', 'pins':[
            Pin(num='1',name='~{DISABLE}',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='+',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='-',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='~',func=Pin.types.OUTPUT,unit=1),
            Pin(num='12',name='+',func=Pin.types.INPUT,unit=2),
            Pin(num='13',name='-',func=Pin.types.INPUT,unit=2),
            Pin(num='14',name='~',func=Pin.types.OUTPUT,unit=2),
            Pin(num='2',name='~{DISABLE}',func=Pin.types.INPUT,unit=2),
            Pin(num='10',name='+',func=Pin.types.INPUT,unit=3),
            Pin(num='3',name='~{DISABLE}',func=Pin.types.INPUT,unit=3),
            Pin(num='8',name='~',func=Pin.types.OUTPUT,unit=3),
            Pin(num='9',name='-',func=Pin.types.INPUT,unit=3),
            Pin(num='11',name='V-',func=Pin.types.PWRIN,unit=4),
            Pin(num='4',name='V+',func=Pin.types.PWRIN,unit=4)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '6', '5', '7']},{'label': 'uB', 'num': 2, 'pin_nums': ['12', '13', '2', '14']},{'label': 'uC', 'num': 3, 'pin_nums': ['10', '9', '3', '8']},{'label': 'uD', 'num': 4, 'pin_nums': ['11', '4']}] }),
        Part(**{ 'name':'MAX453', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MAX453'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'', 'keywords':'amplifier', 'description':'', 'datasheet':'https://datasheets.maximintegrated.com/en/ds/MAX452-MAX455.pdf', 'pins':[
            Pin(num='1',name='A0',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='V-',func=Pin.types.PWRIN,unit=1),
            Pin(num='4',name='IN0',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='IN1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='V+',func=Pin.types.PWRIN,unit=1),
            Pin(num='7',name='IN-',func=Pin.types.INPUT,unit=1),
            Pin(num='8',name='VOUT',func=Pin.types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'THS7374', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'THS7374'}), 'ref_prefix':'U', 'fplist':['Package_SO:TSSOP-14_4.4x5mm_P0.65mm'], 'footprint':'Package_SO:TSSOP-14_4.4x5mm_P0.65mm', 'keywords':'video amplifier sdtv cvbs rgb ypbpr', 'description':'', 'datasheet':'https://www.ti.com/lit/ds/symlink/ths7374.pdf', 'pins':[
            Pin(num='1',name='CH1_IN',func=Pin.types.INPUT,unit=1),
            Pin(num='10',name='V_{S+}',func=Pin.types.PWRIN,unit=1),
            Pin(num='11',name='CH4_OUT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='12',name='CH3_OUT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='13',name='CH2_OUT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='14',name='CH1_OUT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='2',name='CH2_IN',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='CH3_IN',func=Pin.types.INPUT,unit=1),
            Pin(num='4',name='CH4_IN',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='DISABLE',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='8',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='9',name='BYPASS',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] })])