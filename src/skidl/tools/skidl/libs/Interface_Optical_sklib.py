from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Interface_Optical = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'IS471F', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IS471F'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Sharp_IS471F'], 'footprint':'OptoDevice:Sharp_IS471F', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.micropik.com/PDF/tsop17xx.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nIS471F\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='3',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='4',name='GLo',func=pin_types.OPENCOLL,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IS485', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IS485'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Sharp_IS485'], 'footprint':'OptoDevice:Sharp_IS485', 'keywords':'opto receiver amplifier light detector OPIC', 'description':'', 'datasheet':'https://media.digikey.com/pdf/Data%20Sheets/Sharp%20PDFs/is485,486_e.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nIS485\n\nopto receiver amplifier light detector OPIC', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IS486', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IS486'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Sharp_IS485'], 'footprint':'OptoDevice:Sharp_IS485', 'keywords':'opto receiver amplifier light detector OPIC', 'description':'', 'datasheet':'https://media.digikey.com/pdf/Data%20Sheets/Sharp%20PDFs/is485,486_e.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nIS486\n\nopto receiver amplifier light detector OPIC', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'QSE159', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'QSE159'}), 'ref_prefix':'U', 'fplist':['OptoDevice:ONSemi_QSE15x'], 'footprint':'OptoDevice:ONSemi_QSE15x', 'keywords':'opto IR', 'description':'', 'datasheet':'http://www.onsemi.com/pub/Collateral/QSE159-D.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nQSE159\n\nopto IR', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='Out',func=pin_types.OUTPUT,unit=1),
            Pin(num='3',name='Vcc',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SFP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SFP'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'', 'keywords':'SFP transceiver gigabit ethernet INF-8074i', 'description':'', 'datasheet':'http://www.10gtek.com/templates/wzten/pdf/INF-8074.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nSFP\n\nSFP transceiver gigabit ethernet INF-8074i', 'pins':[
            Pin(num='1',name='VeeT',func=pin_types.PWRIN,unit=1),
            Pin(num='10',name='VeeR',func=pin_types.PWRIN,unit=1),
            Pin(num='11',name='VeeR',func=pin_types.PASSIVE,unit=1),
            Pin(num='12',name='RD-',func=pin_types.OUTPUT,unit=1),
            Pin(num='13',name='RD+',func=pin_types.OUTPUT,unit=1),
            Pin(num='14',name='VeeR',func=pin_types.PASSIVE,unit=1),
            Pin(num='15',name='VccR',func=pin_types.PWRIN,unit=1),
            Pin(num='16',name='VccT',func=pin_types.PWRIN,unit=1),
            Pin(num='17',name='VeeT',func=pin_types.PASSIVE,unit=1),
            Pin(num='18',name='TD+',func=pin_types.INPUT,unit=1),
            Pin(num='19',name='TD-',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='TX_FAULT',func=pin_types.OPENCOLL,unit=1),
            Pin(num='20',name='VeeT',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='TX_DISABLE',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='MOD_DEF2',func=pin_types.BIDIR,unit=1),
            Pin(num='5',name='MOD_DEF1',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='MOD_DEF0',func=pin_types.PASSIVE,unit=1),
            Pin(num='7',name='RATE_SELECT',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='RX_LOS',func=pin_types.OPENCOLL,unit=1),
            Pin(num='9',name='VeeR',func=pin_types.PASSIVE,unit=1),
            Pin(num='CAGE',name='CAGE',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SFP+', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SFP+'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'', 'keywords':'SFP transceiver gigabit ethernet SFF-8432', 'description':'', 'datasheet':'https://members.snia.org/document/dl/25892', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nSFP+\n\nSFP transceiver gigabit ethernet SFF-8432', 'pins':[
            Pin(num='1',name='VeeT',func=pin_types.PWRIN,unit=1),
            Pin(num='10',name='VeeR',func=pin_types.PWRIN,unit=1),
            Pin(num='11',name='VeeR',func=pin_types.PASSIVE,unit=1),
            Pin(num='12',name='RD-',func=pin_types.OUTPUT,unit=1),
            Pin(num='13',name='RD+',func=pin_types.OUTPUT,unit=1),
            Pin(num='14',name='VeeR',func=pin_types.PASSIVE,unit=1),
            Pin(num='15',name='VccR',func=pin_types.PWRIN,unit=1),
            Pin(num='16',name='VccT',func=pin_types.PWRIN,unit=1),
            Pin(num='17',name='VeeT',func=pin_types.PASSIVE,unit=1),
            Pin(num='18',name='TD+',func=pin_types.INPUT,unit=1),
            Pin(num='19',name='TD-',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='TX_FAULT',func=pin_types.OPENCOLL,unit=1),
            Pin(num='20',name='VeeT',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='TX_DISABLE',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='SDA',func=pin_types.BIDIR,unit=1),
            Pin(num='5',name='SCL',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='MOD_ABS',func=pin_types.PASSIVE,unit=1),
            Pin(num='7',name='RS0',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='RX_LOS',func=pin_types.OPENCOLL,unit=1),
            Pin(num='9',name='RS1',func=pin_types.INPUT,unit=1),
            Pin(num='CAGE',name='CAGE',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSDP341xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSDP341xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82667/tsdp341.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSDP341xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSMP58138', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSMP58138'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINICAST-3Pin'], 'footprint':'OptoDevice:Vishay_MINICAST-3Pin', 'keywords':'opto IR repeater receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82486/tsmp58138.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSMP58138\n\nopto IR repeater receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP17xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP17xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_CAST-3Pin'], 'footprint':'OptoDevice:Vishay_CAST-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.micropik.com/PDF/tsop17xx.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP17xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='OUT',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP32S40F', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP32S40F'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82669/tsop32s40f.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP32S40F\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='GND',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP331xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP331xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINIMOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MINIMOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82742/tsop331.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP331xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP34S40F', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP34S40F'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82669/tsop32s40f.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP34S40F\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP581xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP581xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINICAST-3Pin'], 'footprint':'OptoDevice:Vishay_MINICAST-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82462/tsop581.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP581xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSDP343xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSDP343xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82667/tsdp341.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSDP343xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSMP58000', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSMP58000'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin'], 'footprint':'OptoDevice:Vishay_MINICAST-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82485/tsmp58000.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSMP58000\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP21xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP21xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82460/tsop45.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP21xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='GND',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP23xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP23xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82460/tsop45.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP23xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='GND',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP25xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP25xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82460/tsop45.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP25xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='GND',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP312xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP312xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_CAST-3Pin', 'OptoDevice:Vishay_CAST-3Pin'], 'footprint':'OptoDevice:Vishay_CAST-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82492/tsop312.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP312xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='OUT',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP314xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP314xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_CAST-3Pin', 'OptoDevice:Vishay_CAST-3Pin', 'OptoDevice:Vishay_CAST-3Pin'], 'footprint':'OptoDevice:Vishay_CAST-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82492/tsop312.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP314xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='OUT',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP321xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP321xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82490/tsop321.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP321xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='GND',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP323xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP323xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82490/tsop321.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP323xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='GND',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP325xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP325xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82490/tsop321.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP325xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='GND',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP333xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP333xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MINIMOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82742/tsop331.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP333xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP335xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP335xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MINIMOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82742/tsop331.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP335xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP341xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP341xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82490/tsop321.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP341xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP343xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP343xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82490/tsop321.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP343xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP345xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP345xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82490/tsop321.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP345xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP348xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP348xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'https://www.vishay.com/docs/82489/tsop322.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP348xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP382xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP382xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin'], 'footprint':'OptoDevice:Vishay_MINICAST-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82491/tsop382.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP382xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP384xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP384xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin'], 'footprint':'OptoDevice:Vishay_MINICAST-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82491/tsop382.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP384xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP38G36', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP38G36'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin'], 'footprint':'OptoDevice:Vishay_MINICAST-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82731/tsop38g36.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP38G36\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP41xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP41xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82460/tsop45.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP41xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP43xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP43xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82460/tsop45.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP43xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP45xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP45xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin', 'OptoDevice:Vishay_MOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82460/tsop45.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP45xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP531xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP531xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MINIMOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82745/tsop531.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP531xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP533xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP533xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MINIMOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82745/tsop531.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP533xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP535xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP535xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin', 'OptoDevice:Vishay_MINIMOLD-3Pin'], 'footprint':'OptoDevice:Vishay_MINIMOLD-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82745/tsop531.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP535xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP582xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP582xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin'], 'footprint':'OptoDevice:Vishay_MINICAST-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82461/tsop582.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP582xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP583xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP583xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin'], 'footprint':'OptoDevice:Vishay_MINICAST-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82462/tsop581.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP583xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP584xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP584xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin'], 'footprint':'OptoDevice:Vishay_MINICAST-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82461/tsop582.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP584xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TSOP585xx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TSOP585xx'}), 'ref_prefix':'U', 'fplist':['OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin', 'OptoDevice:Vishay_MINICAST-3Pin'], 'footprint':'OptoDevice:Vishay_MINICAST-3Pin', 'keywords':'opto IR receiver', 'description':'', 'datasheet':'http://www.vishay.com/docs/82462/tsop581.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_Optical.kicad_sym\nTSOP585xx\n\nopto IR receiver', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vs',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] })])