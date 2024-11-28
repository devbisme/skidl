from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Reference_Current = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'LM134H', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM134H'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-46-3'], 'footprint':'Package_TO_SOT_THT:TO-46-3', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'search_text':'/usr/share/kicad/symbols/Reference_Current.kicad_sym\nLM134H\n\nAdjustable Current Source 10mA', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM334M', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM334M'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'search_text':'/usr/share/kicad/symbols/Reference_Current.kicad_sym\nLM334M\n\nAdjustable Current Source 10mA', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='7',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM334SM', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM334SM'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'search_text':'/usr/share/kicad/symbols/Reference_Current.kicad_sym\nLM334SM\n\nAdjustable Current Source 10mA', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM334Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM334Z'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'search_text':'/usr/share/kicad/symbols/Reference_Current.kicad_sym\nLM334Z\n\nAdjustable Current Source 10mA', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LT3092xDD', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LT3092xDD'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:DFN-8-1EP_3x3mm_P0.5mm_EP1.66x2.38mm'], 'footprint':'Package_DFN_QFN:DFN-8-1EP_3x3mm_P0.5mm_EP1.66x2.38mm', 'keywords':'current source', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/3092fc.pdf', 'search_text':'/usr/share/kicad/symbols/Reference_Current.kicad_sym\nLT3092xDD\n\ncurrent source', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='4',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='6',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='7',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='9',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LT3092xST', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LT3092xST'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'current source', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/3092fc.pdf', 'search_text':'/usr/share/kicad/symbols/Reference_Current.kicad_sym\nLT3092xST\n\ncurrent source', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LT3092xTS8', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LT3092xTS8'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:TSOT-23-8'], 'footprint':'Package_TO_SOT_SMD:TSOT-23-8', 'keywords':'current source', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/3092fc.pdf', 'search_text':'/usr/share/kicad/symbols/Reference_Current.kicad_sym\nLT3092xTS8\n\ncurrent source', 'pins':[
            Pin(num='1',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='7',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PSSI2021SAY', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PSSI2021SAY'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:SOT-353_SC-70-5'], 'footprint':'Package_TO_SOT_SMD:SOT-353_SC-70-5', 'keywords':'iref adjustable', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PSSI2021SAY.pdf', 'search_text':'/usr/share/kicad/symbols/Reference_Current.kicad_sym\nPSSI2021SAY\n\niref adjustable', 'pins':[
            Pin(num='2',name='~',func=pin_types.PWROUT),
            Pin(num='1',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='3',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='4',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='~',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'REF200AU', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'REF200AU'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Current Source/Sink 100Î¼A', 'description':'', 'datasheet':'www.ti.com/lit/ds/symlink/ref200.pdf', 'search_text':'/usr/share/kicad/symbols/Reference_Current.kicad_sym\nREF200AU\n\nCurrent Source/Sink 100Î¼A', 'pins':[
            Pin(num='6',name='S',func=pin_types.PASSIVE),
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=2),
            Pin(num='7',name='~',func=pin_types.PASSIVE,unit=2),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=3),
            Pin(num='4',name='~',func=pin_types.PASSIVE,unit=3),
            Pin(num='5',name='~',func=pin_types.PASSIVE,unit=3)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['8', '6', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['2', '6', '7']},{'label': 'uC', 'num': 3, 'pin_nums': ['4', '5', '3', '6']}] }),
        Part(**{ 'name':'LM234Z-3', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM234Z-3'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'search_text':'/usr/share/kicad/symbols/Reference_Current.kicad_sym\nLM234Z-3\n\nAdjustable Current Source 10mA', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM234Z-6', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM234Z-6'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'search_text':'/usr/share/kicad/symbols/Reference_Current.kicad_sym\nLM234Z-6\n\nAdjustable Current Source 10mA', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM334Z-LFT1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM334Z-LFT1'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Adjustable Current Source 10mA', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm134.pdf', 'search_text':'/usr/share/kicad/symbols/Reference_Current.kicad_sym\nLM334Z-LFT1\n\nAdjustable Current Source 10mA', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] })])