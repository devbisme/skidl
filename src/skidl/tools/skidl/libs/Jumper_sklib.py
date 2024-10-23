from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Jumper = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'Jumper_2_Bridged', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Jumper_2_Bridged'}), 'ref_prefix':'JP', 'fplist':[''], 'footprint':'', 'keywords':'Jumper SPST', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Jumper.kicad_sym\nJumper_2_Bridged\n\nJumper SPST', 'pins':[
            Pin(num='1',name='A',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Jumper_2_Open', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Jumper_2_Open'}), 'ref_prefix':'JP', 'fplist':[''], 'footprint':'', 'keywords':'Jumper SPST', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Jumper.kicad_sym\nJumper_2_Open\n\nJumper SPST', 'pins':[
            Pin(num='1',name='A',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Jumper_2_Small_Bridged', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Jumper_2_Small_Bridged'}), 'ref_prefix':'JP', 'fplist':[''], 'footprint':'', 'keywords':'Jumper SPST', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Jumper.kicad_sym\nJumper_2_Small_Bridged\n\nJumper SPST', 'pins':[
            Pin(num='1',name='A',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Jumper_2_Small_Open', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Jumper_2_Small_Open'}), 'ref_prefix':'JP', 'fplist':[''], 'footprint':'', 'keywords':'Jumper SPST', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Jumper.kicad_sym\nJumper_2_Small_Open\n\nJumper SPST', 'pins':[
            Pin(num='1',name='A',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Jumper_3_Bridged12', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Jumper_3_Bridged12'}), 'ref_prefix':'JP', 'fplist':[''], 'footprint':'', 'keywords':'Jumper SPDT', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Jumper.kicad_sym\nJumper_3_Bridged12\n\nJumper SPDT', 'pins':[
            Pin(num='1',name='A',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Jumper_3_Open', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Jumper_3_Open'}), 'ref_prefix':'JP', 'fplist':[''], 'footprint':'', 'keywords':'Jumper SPDT', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Jumper.kicad_sym\nJumper_3_Open\n\nJumper SPDT', 'pins':[
            Pin(num='1',name='A',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SolderJumper_2_Bridged', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SolderJumper_2_Bridged'}), 'ref_prefix':'JP', 'fplist':[''], 'footprint':'', 'keywords':'solder jumper SPST', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Jumper.kicad_sym\nSolderJumper_2_Bridged\n\nsolder jumper SPST', 'pins':[
            Pin(num='1',name='A',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SolderJumper_2_Open', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SolderJumper_2_Open'}), 'ref_prefix':'JP', 'fplist':[''], 'footprint':'', 'keywords':'solder jumper SPST', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Jumper.kicad_sym\nSolderJumper_2_Open\n\nsolder jumper SPST', 'pins':[
            Pin(num='1',name='A',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SolderJumper_3_Bridged12', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SolderJumper_3_Bridged12'}), 'ref_prefix':'JP', 'fplist':[''], 'footprint':'', 'keywords':'Solder Jumper SPDT', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Jumper.kicad_sym\nSolderJumper_3_Bridged12\n\nSolder Jumper SPDT', 'pins':[
            Pin(num='1',name='A',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SolderJumper_3_Bridged123', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SolderJumper_3_Bridged123'}), 'ref_prefix':'JP', 'fplist':[''], 'footprint':'', 'keywords':'Solder Jumper SPDT', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Jumper.kicad_sym\nSolderJumper_3_Bridged123\n\nSolder Jumper SPDT', 'pins':[
            Pin(num='1',name='A',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SolderJumper_3_Open', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SolderJumper_3_Open'}), 'ref_prefix':'JP', 'fplist':[''], 'footprint':'', 'keywords':'Solder Jumper SPDT', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Jumper.kicad_sym\nSolderJumper_3_Open\n\nSolder Jumper SPDT', 'pins':[
            Pin(num='1',name='A',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] })])