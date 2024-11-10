from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Amplifier_Video = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'AD813', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AD813'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'', 'keywords':'triple opamp', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/AD813.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Video.kicad_sym\nAD813\n\ntriple opamp', 'pins':[
            Pin(num='1',name='~{DISABLE}',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='7',name='~',func=pin_types.OUTPUT,unit=1),
            Pin(num='12',name='+',func=pin_types.INPUT,unit=2),
            Pin(num='13',name='-',func=pin_types.INPUT,unit=2),
            Pin(num='14',name='~',func=pin_types.OUTPUT,unit=2),
            Pin(num='2',name='~{DISABLE}',func=pin_types.INPUT,unit=2),
            Pin(num='10',name='+',func=pin_types.INPUT,unit=3),
            Pin(num='3',name='~{DISABLE}',func=pin_types.INPUT,unit=3),
            Pin(num='8',name='~',func=pin_types.OUTPUT,unit=3),
            Pin(num='9',name='-',func=pin_types.INPUT,unit=3),
            Pin(num='11',name='V-',func=pin_types.PWRIN,unit=4),
            Pin(num='4',name='V+',func=pin_types.PWRIN,unit=4)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '7', '5', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['12', '13', '14', '2']},{'label': 'uC', 'num': 3, 'pin_nums': ['10', '3', '8', '9']},{'label': 'uD', 'num': 4, 'pin_nums': ['11', '4']}] }),
        Part(**{ 'name':'MAX453', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MAX453'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'', 'keywords':'amplifier', 'description':'', 'datasheet':'https://datasheets.maximintegrated.com/en/ds/MAX452-MAX455.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Video.kicad_sym\nMAX453\n\namplifier', 'pins':[
            Pin(num='1',name='A0',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='4',name='IN0',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='IN1',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='IN-',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='VOUT',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'THS7374', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'THS7374'}), 'ref_prefix':'U', 'fplist':['Package_SO:TSSOP-14_4.4x5mm_P0.65mm'], 'footprint':'Package_SO:TSSOP-14_4.4x5mm_P0.65mm', 'keywords':'video amplifier sdtv cvbs rgb ypbpr', 'description':'', 'datasheet':'https://www.ti.com/lit/ds/symlink/ths7374.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Video.kicad_sym\nTHS7374\n\nvideo amplifier sdtv cvbs rgb ypbpr', 'pins':[
            Pin(num='1',name='CH1_IN',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='V_{S+}',func=pin_types.PWRIN,unit=1),
            Pin(num='11',name='CH4_OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='12',name='CH3_OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='13',name='CH2_OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='14',name='CH1_OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='CH2_IN',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='CH3_IN',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='CH4_IN',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='DISABLE',func=pin_types.INPUT,unit=1),
            Pin(num='7',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='8',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='9',name='BYPASS',func=pin_types.INPUT,unit=1)], 'unit_defs':[] })])