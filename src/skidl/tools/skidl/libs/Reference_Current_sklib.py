from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Reference_Current = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'LM134H', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM134H'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-46-3'], 'footprint':'Package_TO_SOT_THT:TO-46-3', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM334M', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM334M'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='7',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM334SM', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM334SM'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM334Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM334Z'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LT3092xDD', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LT3092xDD'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:DFN-8-1EP_3x3mm_P0.5mm_EP1.66x2.38mm'], 'footprint':'Package_DFN_QFN:DFN-8-1EP_3x3mm_P0.5mm_EP1.66x2.38mm', 'keywords':'current source', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/3092fc.pdf', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='5',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='6',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='7',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='9',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LT3092xST', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LT3092xST'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'current source', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/3092fc.pdf', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LT3092xTS8', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LT3092xTS8'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:TSOT-23-8'], 'footprint':'Package_TO_SOT_SMD:TSOT-23-8', 'keywords':'current source', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/3092fc.pdf', 'pins':[
            Pin(num='1',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='5',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='7',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PSSI2021SAY', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PSSI2021SAY'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:SOT-353_SC-70-5'], 'footprint':'Package_TO_SOT_SMD:SOT-353_SC-70-5', 'keywords':'iref adjustable', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PSSI2021SAY.pdf', 'pins':[
            Pin(num='2',name='~',func=Pin.types.PWROUT),
            Pin(num='1',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='3',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='4',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='5',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'REF200AU', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'REF200AU'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Current Source/Sink 100Î¼A', 'description':'', 'datasheet':'www.ti.com/lit/ds/symlink/ref200.pdf', 'pins':[
            Pin(num='6',name='S',func=Pin.types.PASSIVE),
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=2),
            Pin(num='7',name='~',func=Pin.types.PASSIVE,unit=2),
            Pin(num='3',name='~',func=Pin.types.PASSIVE,unit=3),
            Pin(num='4',name='~',func=Pin.types.PASSIVE,unit=3),
            Pin(num='5',name='~',func=Pin.types.PASSIVE,unit=3)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '6', '8']},{'label': 'uB', 'num': 2, 'pin_nums': ['2', '6', '7']},{'label': 'uC', 'num': 3, 'pin_nums': ['4', '6', '3', '5']}] }),
        Part(**{ 'name':'LM234Z-3', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM234Z-3'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM234Z-6', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM234Z-6'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM334Z-LFT1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM334Z-LFT1'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] })])