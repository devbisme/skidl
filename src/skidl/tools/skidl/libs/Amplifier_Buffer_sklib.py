from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Amplifier_Buffer = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'BUF602xD', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BUF602xD'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'buffer amplifier', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/buf602.pdf', 'pins':[
            Pin(num='1',name='V+',func=Pin.types.PWRIN,unit=1),
            Pin(num='2',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='IN',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='V-',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='VREF',func=Pin.types.OUTPUT,unit=1),
            Pin(num='7',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='8',name='~',func=Pin.types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BUF602xDBV', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BUF602xDBV'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:SOT-23-5'], 'footprint':'Package_TO_SOT_SMD:SOT-23-5', 'keywords':'buffer amplifier', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/buf602.pdf', 'pins':[
            Pin(num='1',name='~',func=Pin.types.OUTPUT,unit=1),
            Pin(num='2',name='V-',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='VREF',func=Pin.types.OUTPUT,unit=1),
            Pin(num='4',name='IN',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='V+',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'EL2001CN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'EL2001CN'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-8_W7.62mm'], 'footprint':'Package_DIP:DIP-8_W7.62mm', 'keywords':'Monolithic high slew rate, buffer amplifier', 'description':'', 'datasheet':'http://www.datasheetlib.com/datasheet/677973/el2001_intersil.html#datasheet', 'pins':[
            Pin(num='1',name='V+',func=Pin.types.PWRIN,unit=1),
            Pin(num='2',name='IN',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='V-',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='6',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='7',name='~',func=Pin.types.OUTPUT,unit=1),
            Pin(num='8',name='NC',func=Pin.types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LH0002H', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LH0002H'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-5-8'], 'footprint':'Package_TO_SOT_THT:TO-5-8', 'keywords':'Buffer', 'description':'', 'datasheet':'http://www.calogic.net/pdf/LH0002_Datasheet_Rev_A.pdf', 'pins':[
            Pin(num='1',name='V1+',func=Pin.types.PWRIN,unit=1),
            Pin(num='2',name='V2+',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='E3',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='~',func=Pin.types.OUTPUT,unit=1),
            Pin(num='5',name='E4',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='V2-',func=Pin.types.PWRIN,unit=1),
            Pin(num='7',name='V1-',func=Pin.types.PWRIN,unit=1),
            Pin(num='8',name='IN',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM6321H', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM6321H'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-5-8'], 'footprint':'Package_TO_SOT_THT:TO-5-8', 'keywords':'single buffer', 'description':'', 'datasheet':'http://www.electronica60norte.com/mwfls/pdf/LM6221.pdf', 'pins':[
            Pin(num='1',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='2',name='V+',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='~',func=Pin.types.OUTPUT,unit=1),
            Pin(num='5',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='6',name='V-',func=Pin.types.PWRIN,unit=1),
            Pin(num='7',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='8',name='IN',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM6321M', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM6321M'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-14_3.9x8.7mm_P1.27mm'], 'footprint':'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm', 'keywords':'single buffer', 'description':'', 'datasheet':'http://www.electronica60norte.com/mwfls/pdf/LM6221.pdf', 'pins':[
            Pin(num='1',name='V-',func=Pin.types.PASSIVE,unit=1),
            Pin(num='10',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='11',name='V+',func=Pin.types.PWRIN,unit=1),
            Pin(num='12',name='~',func=Pin.types.OUTPUT,unit=1),
            Pin(num='13',name='V-',func=Pin.types.PASSIVE,unit=1),
            Pin(num='14',name='V-',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='V-',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='V-',func=Pin.types.PWRIN,unit=1),
            Pin(num='4',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='5',name='IN',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='V-',func=Pin.types.PASSIVE,unit=1),
            Pin(num='7',name='V-',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='V-',func=Pin.types.PASSIVE,unit=1),
            Pin(num='9',name='V-',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM6321N', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM6321N'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-8_W7.62mm'], 'footprint':'Package_DIP:DIP-8_W7.62mm', 'keywords':'single buffer', 'description':'', 'datasheet':'http://www.electronica60norte.com/mwfls/pdf/LM6221.pdf', 'pins':[
            Pin(num='1',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='2',name='V+',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='~',func=Pin.types.OUTPUT,unit=1),
            Pin(num='5',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='6',name='V-',func=Pin.types.PWRIN,unit=1),
            Pin(num='7',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='8',name='IN',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] })])