from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Transistor_BJT = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'2N2219', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N2219'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-39-3'], 'footprint':'Package_TO_SOT_THT:TO-39-3', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/2N2219-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2N2219\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2N2646', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N2646'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-18-3'], 'footprint':'Package_TO_SOT_THT:TO-18-3', 'keywords':'UJT', 'description':'', 'datasheet':'http://www.bucek.name/pdf/2n2646,2647.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2N2646\n\nUJT', 'pins':[
            Pin(num='1',name='B2',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='B1',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2N3055', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N3055'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-3'], 'footprint':'Package_TO_SOT_THT:TO-3', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/2N3055-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2N3055\n\npower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2N3904', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N3904'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/2N3903-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2N3904\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2N3906', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N3906'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/2N3906-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2N3906\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SA1015', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SA1015'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Low Noise Audio PNP Transistor', 'description':'', 'datasheet':'http://www.datasheetcatalog.org/datasheet/toshiba/905.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2SA1015\n\nLow Noise Audio PNP Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SB631', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SB631'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'High Voltage Transistor', 'description':'', 'datasheet':'http://pdf.datasheetcatalog.com/datasheet/sanyo/ds_pdf_e/2SB631.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2SB631\n\nHigh Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SB817', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SB817'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-3PB-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-3PB-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://skory.gylcomp.hu/alkatresz/2SB817.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2SB817\n\nPower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SC1815', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SC1815'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Low Noise Audio NPN Transistor', 'description':'', 'datasheet':'https://media.digikey.com/pdf/Data%20Sheets/Toshiba%20PDFs/2SC1815.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2SC1815\n\nLow Noise Audio NPN Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SC1941', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SC1941'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Audio High Voltage NPN Transistor', 'description':'', 'datasheet':'http://rtellason.com/transdata/2sc1941.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2SC1941\n\nAudio High Voltage NPN Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SC1945', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SC1945'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'RF Power NPN Transistor', 'description':'', 'datasheet':'http://rtellason.com/transdata/2sc1945.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2SC1945\n\nRF Power NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SD1047', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SD1047'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-3PB-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-3PB-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.st.com/resource/en/datasheet/2sd1047.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2SD1047\n\nPower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SD600', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SD600'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'High Voltage Power Transistor', 'description':'', 'datasheet':'http://pdf.datasheetcatalog.com/datasheet/sanyo/ds_pdf_e/2SB631.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2SD600\n\nHigh Voltage Power Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'320S14-U', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'320S14-U'}), 'ref_prefix':'Q', 'fplist':['Package_SO:SOIC-14_3.9x8.7mm_P1.27mm'], 'footprint':'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm', 'keywords':'dual pair pnp matched transistors', 'description':'', 'datasheet':'https://www.thatcorp.com/datashts/THAT_300-Series_Datasheet.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n320S14-U\n\ndual pair pnp matched transistors', 'pins':[
            Pin(num='11',func=Pin.types.PASSIVE),
            Pin(num='4',func=Pin.types.PASSIVE),
            Pin(num='1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',func=Pin.types.INPUT,unit=1),
            Pin(num='3',func=Pin.types.PASSIVE,unit=1),
            Pin(num='12',func=Pin.types.PASSIVE,unit=2),
            Pin(num='13',func=Pin.types.INPUT,unit=2),
            Pin(num='14',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',func=Pin.types.PASSIVE,unit=3),
            Pin(num='6',func=Pin.types.INPUT,unit=3),
            Pin(num='7',func=Pin.types.PASSIVE,unit=3),
            Pin(num='10',func=Pin.types.PASSIVE,unit=4),
            Pin(num='8',func=Pin.types.PASSIVE,unit=4),
            Pin(num='9',func=Pin.types.INPUT,unit=4)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['11', '3', '1', '2', '4']},{'label': 'uB', 'num': 2, 'pin_nums': ['11', '13', '14', '12', '4']},{'label': 'uC', 'num': 3, 'pin_nums': ['5', '11', '6', '7', '4']},{'label': 'uD', 'num': 4, 'pin_nums': ['10', '11', '8', '9', '4']}] }),
        Part(**{ 'name':'BC107', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC107'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-18-3'], 'footprint':'Package_TO_SOT_THT:TO-18-3', 'keywords':'NPN low noise transistor', 'description':'', 'datasheet':'http://www.b-kainka.de/Daten/Transistor/BC108.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC107\n\nNPN low noise transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC160', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC160'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-39-3'], 'footprint':'Package_TO_SOT_THT:TO-39-3', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'http://www.farnell.com/datasheets/1697389.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC160\n\npower PNP Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC237', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC237'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Epitaxial Silicon NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC237-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC237\n\nEpitaxial Silicon NPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC240', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC240'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'RF NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BF420-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC240\n\nRF NPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC307', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC307'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Epitaxial Silicon PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC307-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC307\n\nEpitaxial Silicon PNP Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC413', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC413'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bc413_14_b_c.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC413\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC516', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC516'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Darlington Darl Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC516-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC516\n\nPNP Darlington Darl Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC517', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC517'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Darlington Darl Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC517-D74Z-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC517\n\nNPN Darlington Darl Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC547', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC547'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC550-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC547\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC557', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC557'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC556BTA-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC557\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC636', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC636'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC636-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC636\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC807', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC807'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC808-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC807\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC807W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC807W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC808-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC807W\n\nPNP transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC817', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC817'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC818-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC817\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC817W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC817W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC818-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC817W\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC846BPN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC846BPN'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC846BPN.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC846BPN\n\nNPN/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'BC846BS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC846BS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC846BS.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC846BS\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '6', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'BC856BS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC856BS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC856BS.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC856BS\n\nPNP/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'BCP51', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCP51'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BCP51-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBCP51\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCV29', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCV29'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'transistor NPN Darlington', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BCV29_49.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBCV29\n\ntransistor NPN Darlington', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCV61', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCV61'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-143'], 'footprint':'Package_TO_SOT_SMD:SOT-143', 'keywords':'Transistor Double NPN', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BCV61.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBCV61\n\nTransistor Double NPN', 'pins':[
            Pin(num='1',name='C2',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCV62', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCV62'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-143'], 'footprint':'Package_TO_SOT_SMD:SOT-143', 'keywords':'Transistor Double PNP', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BCV62.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBCV62\n\nTransistor Double PNP', 'pins':[
            Pin(num='1',name='C2',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCX51', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCX51'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/bcx51_bcx52_bcx53.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBCX51\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCX56', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCX56'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.nxp.com/docs/en/data-sheet/BCP56_BCX56_BC56PA.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBCX56\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD139', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD139'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001225.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD139\n\nLow Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD140', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD140'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001225.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD140\n\nLow Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD249', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD249'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD249\n\nPower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD250', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD250'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD250\n\nPower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD433', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD433'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD433\n\nPower NPN Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD434', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD434'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD434\n\nPower PNP Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD910', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD910'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001277.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD910\n\nPower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD911', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD911'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001277.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD911\n\nPower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW93', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW93'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BDW93C-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBDW93\n\nDarlington NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW94', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW94'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington PNP Transistor', 'description':'', 'datasheet':'http://www.bourns.com/data/global/pdfs/bdw94.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBDW94\n\nDarlington PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BF199', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BF199'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'RF NPN Transistor', 'description':'', 'datasheet':'http://www.micropik.com/PDF/BF199.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBF199\n\nRF NPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BF457', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BF457'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'NPN HV High Voltage Transistor', 'description':'', 'datasheet':'https://www.pcpaudio.com/pcpfiles/transistores/BF457-8-9.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBF457\n\nNPN HV High Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BFR92', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BFR92'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'RF 5GHz NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BFR92A_N.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBFR92\n\nRF 5GHz NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BFT92', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BFT92'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'RF 5GHz NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BFT92_CNV.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBFT92\n\nRF 5GHz NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BUT11', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BUT11'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'High Voltage Power NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BUT11A-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBUT11\n\nHigh Voltage Power NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DMMT5401', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DMMT5401'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23-6'], 'footprint':'Package_TO_SOT_SMD:SOT-23-6', 'keywords':'transistor PNP', 'description':'', 'datasheet':'https://www.diodes.com/assets/Datasheets/ds30437.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDMMT5401\n\ntransistor PNP', 'pins':[
            Pin(num='1',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='4',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='E2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'DTA113T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA113T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA113T\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA113Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA113Z'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA113Z\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA114E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA114E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA114E\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA114G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA114G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA114G\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA114T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA114T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA114T\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA114W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA114W'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA114W\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA114Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA114Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA114Y\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA115E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA115E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA115E\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA115G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA115G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA115G\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA115T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA115T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA115T\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA115U', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA115U'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA115U\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA123E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA123E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA123E\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA123J', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA123J'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA123J\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA123Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA123Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA123Y\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA124E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA124E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA124E\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA124G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA124G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA124G\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA124T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA124T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA124T\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA124X', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA124X'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA124X\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA125T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA125T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA125T\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA143E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA143E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA143E\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA143T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA143T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA143T\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA143X', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA143X'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA143X\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA143Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA143Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA143Y\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA143Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA143Z'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA143Z\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA144E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA144E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA144E\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA144G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA144G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA144G\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA144T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA144T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA144T\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA144V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA144V'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA144V\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA144W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA144W'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA144W\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA1D3R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA1D3R'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA1D3R\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA214Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA214Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTA214Y\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB113E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB113E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTB113E\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB113Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB113Z'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTB113Z\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB114E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB114E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTB114E\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB114G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB114G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTB114G\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB114T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB114T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTB114T\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB122J', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB122J'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTB122J\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB123E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB123E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTB123E\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB123T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB123T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTB123T\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB123Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB123Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTB123Y\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB133H', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB133H'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTB133H\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB143T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB143T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTB143T\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB163T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB163T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTB163T\n\nROHM Digital PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC113T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC113T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC113T\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC113Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC113Z'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC113Z\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC114E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC114E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC114E\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC114G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC114G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC114G\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC114T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC114T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC114T\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC114W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC114W'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC114W\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC114Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC114Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC114Y\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC115E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC115E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC115E\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC115G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC115G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC115G\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC115T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC115T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC115T\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC115U', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC115U'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC115U\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC123E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC123E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC123E\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC123J', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC123J'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC123J\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC123Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC123Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC123Y\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC124E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC124E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC124E\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC124G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC124G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC124G\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC124T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC124T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC124T\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC124X', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC124X'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC124X\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC125T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC125T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC125T\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC143E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC143E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC143E\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC143T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC143T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC143T\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC143X', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC143X'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC143X\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC143Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC143Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC143Y\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC143Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC143Z'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC143Z\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC144E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC144E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC144E\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC144G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC144G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC144G\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC144T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC144T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC144T\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC144V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC144V'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC144V\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC144W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC144W'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC144W\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC1D3R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC1D3R'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC1D3R\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC214Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC214Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTC214Y\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD113E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD113E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTD113E\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD113Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD113Z'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTD113Z\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD114E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD114E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTD114E\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD114G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD114G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTD114G\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD114T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD114T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTD114T\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD122J', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD122J'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTD122J\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD123E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD123E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTD123E\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD123T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD123T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTD123T\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD123Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD123Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTD123Y\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD133H', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD133H'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTD133H\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD143T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD143T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTD143T\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD163T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD163T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nDTD163T\n\nROHM Digital NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'EMH3', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'EMH3'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-563'], 'footprint':'Package_TO_SOT_SMD:SOT-563', 'keywords':'Dual NPN Transistor', 'description':'', 'datasheet':'http://rohmfs.rohm.com/en/products/databook/datasheet/discrete/transistor/digital/emh3t2r-e.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nEMH3\n\nDual NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '5', '3']}] }),
        Part(**{ 'name':'FMB2227A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FMB2227A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SuperSOT-6'], 'footprint':'Package_TO_SOT_SMD:SuperSOT-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub/Collateral/FMB2227A-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nFMB2227A\n\nNPN/PNP Transistor', 'pins':[
            Pin(num='1',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='3',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='4',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['5', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['2', '3', '4']}] }),
        Part(**{ 'name':'IMH3A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IMH3A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:ROHM_SOT-457_ClockwisePinNumbering'], 'footprint':'Package_TO_SOT_SMD:ROHM_SOT-457_ClockwisePinNumbering', 'keywords':'Dual NPN Transistor', 'description':'', 'datasheet':'http://rohmfs.rohm.com/en/products/databook/datasheet/discrete/transistor/digital/emh3t2r-e.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nIMH3A\n\nDual NPN Transistor', 'pins':[
            Pin(num='1',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='5',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='3',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '5', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['2', '4', '3']}] }),
        Part(**{ 'name':'KTD1624', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'KTD1624'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'Switching NPN Transistor', 'description':'', 'datasheet':'http://www2.kec.co.kr/data/databook/pdf/KTD/Eng/KTD1624.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nKTD1624\n\nSwitching NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MAT02', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MAT02'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-78-6'], 'footprint':'Package_TO_SOT_THT:TO-78-6', 'keywords':'Precision Dual Monolithic Transistor Low Noise EOL', 'description':'', 'datasheet':'http://www.elenota.pl/datasheet_download/93431/MAT02', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMAT02\n\nPrecision Dual Monolithic Transistor Low Noise EOL', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='E',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B',func=Pin.types.INPUT,unit=2),
            Pin(num='6',name='C',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '3', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '5', '6']}] }),
        Part(**{ 'name':'MJ2955', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MJ2955'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-3'], 'footprint':'Package_TO_SOT_THT:TO-3', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/2N3055-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMJ2955\n\npower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MJE13003', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MJE13003'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Switching Power High Voltage NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MJE13003-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMJE13003\n\nSwitching Power High Voltage NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MJE13007G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MJE13007G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Switching Power NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MJE13007-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMJE13007G\n\nSwitching Power NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBTA42', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBTA42'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN High Voltage Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/MMBTA42LT1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMBTA42\n\nNPN High Voltage Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBTA92', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBTA92'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP High Voltage Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/MMBTA92LT1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMBTA92\n\nPNP High Voltage Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMDTA06', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDTA06'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SC-74-6_1.55x2.9mm_P0.95mm'], 'footprint':'Package_TO_SOT_SMD:SC-74-6_1.55x2.9mm_P0.95mm', 'keywords':'dual transistor NPN', 'description':'', 'datasheet':'https://www.diodes.com/assets/Datasheets/MMDTA06.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMDTA06\n\ndual transistor NPN', 'pins':[
            Pin(num='1',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='3',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='4',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '5', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['2', '3', '4']}] }),
        Part(**{ 'name':'MPSA42', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MPSA42'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN High Voltage Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MPSA42-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMPSA42\n\nNPN High Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MPSA92', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MPSA92'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP High Voltage Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MPSA92-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMPSA92\n\nPNP High Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MUN5211DW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MUN5211DW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'Dual NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub/Collateral/DTC114ED-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMUN5211DW1\n\nDual NPN Transistor', 'pins':[
            Pin(num='3',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='5',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='1',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='2',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='6',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['5', '3', '4']},{'label': 'uB', 'num': 2, 'pin_nums': ['1', '2', '6']}] }),
        Part(**{ 'name':'PN2222A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PN2222A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/PN2222-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPN2222A\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PZT2222A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PZT2222A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'NPN General Puprose Transistor SMD', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/PN2222-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPZT2222A\n\nNPN General Puprose Transistor SMD', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PZT3904', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PZT3904'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pdf/datasheet/pzt3904-d.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPZT3904\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PZT3906', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PZT3906'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pdf/datasheet/pzt3906-d.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPZT3906\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PZTA42', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PZTA42'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'NPN High Voltage Transistor SMD', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/PZTA42T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPZTA42\n\nNPN High Voltage Transistor SMD', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PZTA92', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PZTA92'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'PNP High Voltage Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/PZTA92T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPZTA92\n\nPNP High Voltage Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'S8050', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'S8050'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'S8050 NPN Low Voltage High Current Transistor', 'description':'', 'datasheet':'http://www.unisonic.com.tw/datasheet/S8050.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nS8050\n\nS8050 NPN Low Voltage High Current Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'S8550', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'S8550'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'S8550 PNP Low Voltage High Current Transistor', 'description':'', 'datasheet':'http://www.unisonic.com.tw/datasheet/S8550.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nS8550\n\nS8550 PNP Low Voltage High Current Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SSM2210', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SSM2210'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'audio npn dual', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/obsolete-data-sheets/SSM2210.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nSSM2210\n\naudio npn dual', 'pins':[
            Pin(num='1',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='7',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='8',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '3', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['7', '6', '8']}] }),
        Part(**{ 'name':'SSM2220', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SSM2220'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'audio pnp dual', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/SSM2220.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nSSM2220\n\naudio pnp dual', 'pins':[
            Pin(num='1',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='7',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='8',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '3', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['6', '7', '8']}] }),
        Part(**{ 'name':'TIP120', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP120'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington Power NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/TIP120-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP120\n\nDarlington Power NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP125', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP125'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington Power PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/TIP120-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP125\n\nDarlington Power PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP2955', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP2955'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-218-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-218-3_Vertical', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/TIP3055-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP2955\n\npower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP2955G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP2955G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-247-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-247-3_Vertical', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/TIP3055-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP2955G\n\npower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP3055', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP3055'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-218-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-218-3_Vertical', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/TIP3055-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP3055\n\npower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP3055G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP3055G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-247-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-247-3_Vertical', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/TIP3055-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP3055G\n\npower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'UMH3N', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'UMH3N'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'Dual NPN Transistor', 'description':'', 'datasheet':'http://rohmfs.rohm.com/en/products/databook/datasheet/discrete/transistor/digital/emh3t2r-e.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nUMH3N\n\nDual NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '6', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '4']}] }),
        Part(**{ 'name':'2N2647', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N2647'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-18-3', 'Package_TO_SOT_THT:TO-18-3'], 'footprint':'Package_TO_SOT_THT:TO-18-3', 'keywords':'UJT', 'description':'', 'datasheet':'http://www.bucek.name/pdf/2n2646,2647.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2N2647\n\nUJT', 'pins':[
            Pin(num='1',name='B2',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='B1',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2N3905', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N3905'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.nteinc.com/specs/original/2N3905_06.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2N3905\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SC4213', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SC4213'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://toshiba.semicon-storage.com/info/docget.jsp?did=19305&prodName=2SC4213', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\n2SC4213\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC108', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC108'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-18-3', 'Package_TO_SOT_THT:TO-18-3'], 'footprint':'Package_TO_SOT_THT:TO-18-3', 'keywords':'NPN low noise transistor', 'description':'', 'datasheet':'http://www.b-kainka.de/Daten/Transistor/BC108.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC108\n\nNPN low noise transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC109', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC109'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-18-3', 'Package_TO_SOT_THT:TO-18-3', 'Package_TO_SOT_THT:TO-18-3'], 'footprint':'Package_TO_SOT_THT:TO-18-3', 'keywords':'NPN low noise transistor', 'description':'', 'datasheet':'http://www.farnell.com/datasheets/296634.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC109\n\nNPN low noise transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC140', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC140'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-39-3', 'Package_TO_SOT_THT:TO-39-3'], 'footprint':'Package_TO_SOT_THT:TO-39-3', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.farnell.com/datasheets/296634.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC140\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC141', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC141'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-39-3', 'Package_TO_SOT_THT:TO-39-3', 'Package_TO_SOT_THT:TO-39-3'], 'footprint':'Package_TO_SOT_THT:TO-39-3', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.farnell.com/datasheets/296634.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC141\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC161', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC161'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-39-3', 'Package_TO_SOT_THT:TO-39-3'], 'footprint':'Package_TO_SOT_THT:TO-39-3', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'http://www.farnell.com/datasheets/1697389.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC161\n\npower PNP Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC212', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC212'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://media.digikey.com/pdf/Data%20Sheets/Fairchild%20PDFs/BC212.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC212\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC327', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC327'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC327-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC327\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC328', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC328'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.redrok.com/PNP_BC327_-45V_-800mA_0.625W_Hfe100_TO-92.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC328\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC337', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC337'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://diotec.com/tl_files/diotec/files/pdf/datasheets/bc337.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC337\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC338', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC338'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://diotec.com/tl_files/diotec/files/pdf/datasheets/bc337', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC338\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC413B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC413B'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bc413_14_b_c.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC413B\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC413C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC413C'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bc413_14_b_c.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC413C\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC414', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC414'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bc413_14_b_c.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC414\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC414B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC414B'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bc413_14_b_c.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC414B\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC414C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC414C'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bc413_14_b_c.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC414C\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC546', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC546'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC550-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC546\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC548', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC548'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC550-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC548\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC549', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC549'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC550-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC549\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC550', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC550'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC550-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC550\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC556', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC556'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC556BTA-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC556\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC558', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC558'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC556BTA-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC558\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC559', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC559'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC556BTA-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC559\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC560', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC560'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC556BTA-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC560\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC808', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC808'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC808-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC808\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC808W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC808W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC808-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC808W\n\nPNP transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC818', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC818'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC818-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC818\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC818W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC818W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC818-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC818W\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC846', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC846'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC846_SER.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC846\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC846BDW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC846BDW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC846BDW1T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC846BDW1\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '2', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '4']}] }),
        Part(**{ 'name':'BC846BPDW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC846BPDW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC846BPDW1T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC846BPDW1\n\nNPN/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'BC847', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC847\n\nNPN Small Signal Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC847BDW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847BDW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC846BDW1T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC847BDW1\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '2', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'BC847BPDW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847BPDW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC846BPDW1T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC847BPDW1\n\nNPN/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '6', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '4']}] }),
        Part(**{ 'name':'BC847BPN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847BPN'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC847BPN.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC847BPN\n\nNPN/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'BC847BS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847BS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC847BS.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC847BS\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '1', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'BC847W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC847W\n\nNPN Small Signal Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC848', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC848'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC848\n\nNPN Small Signal Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC848W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC848W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC848W\n\nNPN Small Signal Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC849', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC849'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC849\n\nNPN Small Signal Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC849W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC849W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC849W\n\nNPN Small Signal Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC850', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC850'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC850\n\nNPN Small Signal Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC850W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC850W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC850W\n\nNPN Small Signal Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC856', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC856'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC860-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC856\n\nPNP transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC856BDW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC856BDW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC856BDW1T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC856BDW1\n\nPNP/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '2', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'BC856W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC856W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC860-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC856W\n\nPNP transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC857', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC857'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC860-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC857\n\nPNP transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC857BDW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC857BDW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC856BDW1T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC857BDW1\n\nPNP/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '6', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'BC857BS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC857BS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC857BS.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC857BS\n\nPNP/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'BC857W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC857W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC857SERIES_BC858SERIES_BC859SERIES_BC860SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541da0e3a1661', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC857W\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC858', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC858'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC860-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC858\n\nPNP transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC858W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC858W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC857SERIES_BC858SERIES_BC859SERIES_BC860SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541da0e3a1661', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC858W\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC859', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC859'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC857SERIES_BC858SERIES_BC859SERIES_BC860SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541da0e3a1661', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC859\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC859W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC859W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC857SERIES_BC858SERIES_BC859SERIES_BC860SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541da0e3a1661', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC859W\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC860', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC860'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC857SERIES_BC858SERIES_BC859SERIES_BC860SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541da0e3a1661', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC860\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC860W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC860W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC857SERIES_BC858SERIES_BC859SERIES_BC860SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541da0e3a1661', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBC860W\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCP53', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCP53'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BCP53T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBCP53\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCP56', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCP56'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.nxp.com/docs/en/data-sheet/BCP56_BCX56_BC56PA.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBCP56\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCV49', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCV49'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3', 'Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'transistor NPN Darlington', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BCV29_49.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBCV49\n\ntransistor NPN Darlington', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCX52', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCX52'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3', 'Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/bcx51_bcx52_bcx53.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBCX52\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCX53', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCX53'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3', 'Package_TO_SOT_SMD:SOT-89-3', 'Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/bcx51_bcx52_bcx53.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBCX53\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD135', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD135'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001225.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD135\n\nLow Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD136', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD136'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001225.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD136\n\nLow Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD137', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD137'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001225.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD137\n\nLow Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD138', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD138'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001225.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD138\n\nLow Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD233', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD233'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'https://media.digikey.com/pdf/Data%20Sheets/Micro%20Commercial%20PDFs/BD233,235,237.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD233\n\nLow Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD234', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD234'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.electronica-pt.com/datasheets/bd/BD234.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD234\n\nLow Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD235', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD235'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'https://media.digikey.com/pdf/Data%20Sheets/Micro%20Commercial%20PDFs/BD233,235,237.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD235\n\nLow Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD236', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD236'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.electronica-pt.com/datasheets/bd/BD234.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD236\n\nLow Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD237', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD237'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'https://media.digikey.com/pdf/Data%20Sheets/Micro%20Commercial%20PDFs/BD233,235,237.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD237\n\nLow Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD238', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD238'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.electronica-pt.com/datasheets/bd/BD234.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD238\n\nLow Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD249A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD249A'}), 'ref_prefix':'Q', 'fplist':['', ''], 'footprint':'', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD249A\n\nPower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD249B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD249B'}), 'ref_prefix':'Q', 'fplist':['', '', ''], 'footprint':'', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD249B\n\nPower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD249C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD249C'}), 'ref_prefix':'Q', 'fplist':['', '', '', ''], 'footprint':'', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD249C\n\nPower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD250A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD250A'}), 'ref_prefix':'Q', 'fplist':['', ''], 'footprint':'', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD250A\n\nPower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD250B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD250B'}), 'ref_prefix':'Q', 'fplist':['', '', ''], 'footprint':'', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD250B\n\nPower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD250C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD250C'}), 'ref_prefix':'Q', 'fplist':['', '', '', ''], 'footprint':'', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD250C\n\nPower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD435', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD435'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD435\n\nPower NPN Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD436', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD436'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD436\n\nPower PNP Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD437', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD437'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD437\n\nPower NPN Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD438', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD438'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD438\n\nPower PNP Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD439', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD439'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD439\n\nPower NPN Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD440', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD440'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD440\n\nPower PNP Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD441', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD441'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD441\n\nPower NPN Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD442', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD442'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD442\n\nPower PNP Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD909', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD909'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001277.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD909\n\nPower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD912', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD912'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001277.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBD912\n\nPower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW93A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW93A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BDW93C-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBDW93A\n\nDarlington NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW93B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW93B'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BDW93C-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBDW93B\n\nDarlington NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW93C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW93C'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BDW93C-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBDW93C\n\nDarlington NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW94A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW94A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington PNP Transistor', 'description':'', 'datasheet':'http://www.bourns.com/data/global/pdfs/bdw94.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBDW94A\n\nDarlington PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW94B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW94B'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington PNP Transistor', 'description':'', 'datasheet':'http://www.bourns.com/data/global/pdfs/bdw94.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBDW94B\n\nDarlington PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW94C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW94C'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington PNP Transistor', 'description':'', 'datasheet':'http://www.bourns.com/data/global/pdfs/bdw94.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBDW94C\n\nDarlington PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BF458', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BF458'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'NPN HV High Voltage Transistor', 'description':'', 'datasheet':'https://www.pcpaudio.com/pcpfiles/transistores/BF457-8-9.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBF458\n\nNPN HV High Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BF459', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BF459'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'NPN HV High Voltage Transistor', 'description':'', 'datasheet':'https://www.pcpaudio.com/pcpfiles/transistores/BF457-8-9.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBF459\n\nNPN HV High Voltage Transistor', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BUT11A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BUT11A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'High Voltage Power NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BUT11A-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nBUT11A\n\nHigh Voltage Power NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'FFB2222A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FFB2222A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/MMPQ2222A-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nFFB2222A\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'FFB2227A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FFB2227A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub/Collateral/FMB2227A-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nFFB2227A\n\nNPN/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '5', '3']}] }),
        Part(**{ 'name':'FFB3904', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FFB3904'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/MMPQ3904-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nFFB3904\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '2', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'FFB3906', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FFB3906'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/MMPQ3906-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nFFB3906\n\nPNP/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '6', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'FFB3946', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FFB3946'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub/Collateral/FMB3946-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nFFB3946\n\nNPN/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '1', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '4']}] }),
        Part(**{ 'name':'FFB5551', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FFB5551'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/FFB5551-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nFFB5551\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '5', '3']}] }),
        Part(**{ 'name':'FMB3946', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FMB3946'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SuperSOT-6', 'Package_TO_SOT_SMD:SuperSOT-6'], 'footprint':'Package_TO_SOT_SMD:SuperSOT-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub/Collateral/FMB3946-D.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nFMB3946\n\nNPN/PNP Transistor', 'pins':[
            Pin(num='1',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='3',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='4',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['5', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['2', '4', '3']}] }),
        Part(**{ 'name':'MBT2222ADW1T1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MBT2222ADW1T1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MBT2222ADW1T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMBT2222ADW1T1\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '2', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'MBT3904DW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MBT3904DW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MBT3904DW1T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMBT3904DW1\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '6', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '4', '3']}] }),
        Part(**{ 'name':'MBT3906DW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MBT3906DW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MBT3906DW1T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMBT3906DW1\n\nPNP/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '2', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'MBT3946DW1T1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MBT3946DW1T1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MBT3946DW1T1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMBT3946DW1T1\n\nNPN/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'MJE13005G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MJE13005G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Switching Power NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MJE13005-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMJE13005G\n\nSwitching Power NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MJE13009G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MJE13009G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Switching Power NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MJE13009-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMJE13009G\n\nSwitching Power NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBT3904', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBT3904'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pdf/datasheet/pzt3904-d.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMBT3904\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBT3906', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBT3906'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pdf/datasheet/pzt3906-d.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMBT3906\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBT5550L', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBT5550L'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'www.onsemi.com/pub/Collateral/MMBT5550LT1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMBT5550L\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBT5551L', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBT5551L'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'www.onsemi.com/pub/Collateral/MMBT5550LT1-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMBT5551L\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBTA06', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBTA06'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'SMD', 'description':'', 'datasheet':'https://diotec.com/request/datasheet/mmbta06.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMBTA06\n\nSMD', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBTA44', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBTA44'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'SMD', 'description':'', 'datasheet':'https://diotec.com/request/datasheet/mmbta42.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMBTA44\n\nSMD', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBTA56', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBTA56'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'SMD', 'description':'', 'datasheet':'https://diotec.com/request/datasheet/mmbta56.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMBTA56\n\nSMD', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBTA94', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBTA94'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP', 'description':'', 'datasheet':'https://diotec.com/request/datasheet/mmbta92.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMBTA94\n\nPNP', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMDT2222A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDT2222A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.diodes.com/_files/datasheets/ds30125.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMDT2222A\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '1', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '4', '3']}] }),
        Part(**{ 'name':'MMDT3904', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDT3904'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.diodes.com/_files/datasheets/ds30088.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMDT3904\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '6', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '4']}] }),
        Part(**{ 'name':'MMDT3906', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDT3906'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'http://www.diodes.com/_files/datasheets/ds30124.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMDT3906\n\nPNP/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'MMDT3946', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDT3946'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.diodes.com/_files/datasheets/ds30123.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMDT3946\n\nNPN/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '4']}] }),
        Part(**{ 'name':'MMDT5401', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDT5401'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'http://www.diodes.com/_files/datasheets/ds30169.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMDT5401\n\nPNP/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '4']}] }),
        Part(**{ 'name':'MMDT5551', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDT5551'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.diodes.com/_files/datasheets/ds30172.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMDT5551\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '1', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'PBSS301PZ', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PBSS301PZ'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PBSS301PZ.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPBSS301PZ\n\nPNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PMBT2222AYS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PMBT2222AYS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PMBT2222AYS.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPMBT2222AYS\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '6', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'PMBT3904YS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PMBT3904YS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PMBT3904YS.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPMBT3904YS\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '6', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '5', '3']}] }),
        Part(**{ 'name':'PMBT3906YS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PMBT3906YS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PMBT3906YS.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPMBT3906YS\n\nPNP/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'PMBT3946YPN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PMBT3946YPN'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PMBT3946YPN.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPMBT3946YPN\n\nNPN/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '5', '3']}] }),
        Part(**{ 'name':'PUMT1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PUMT1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PUMT1.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPUMT1\n\nPNP/PNP Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '3', '5']}] }),
        Part(**{ 'name':'PUMX1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PUMX1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PUMX1.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPUMX1\n\nNPN/NPN Transistor', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'SS8050', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SS8050'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'SS8050 NPN Transistor', 'description':'', 'datasheet':'http://www.secosgmbh.com/datasheet/products/SSMPTransistor/SOT-23/SS8050.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nSS8050\n\nSS8050 NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SS8550', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SS8550'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'SS8550 PNP Transistor', 'description':'', 'datasheet':'http://www.secosgmbh.com/datasheet/products/SSMPTransistor/SOT-23/SS8550.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nSS8550\n\nSS8550 PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP121', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP121'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington Power NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/TIP120-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP121\n\nDarlington Power NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP122', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP122'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington Power NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/TIP120-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP122\n\nDarlington Power NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP126', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP126'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington Power PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/TIP120-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP126\n\nDarlington Power PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP127', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP127'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington Power PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/TIP120-D.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP127\n\nDarlington Power PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP41', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP41'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=tip41.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP41\n\npower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP41A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP41A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=tip41.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP41A\n\npower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP41B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP41B'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=tip41.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP41B\n\npower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP41C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP41C'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=tip41.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP41C\n\npower NPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP42', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP42'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=TIP42.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP42\n\npower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP42A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP42A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=TIP42.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP42A\n\npower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP42B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP42B'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=TIP42.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP42B\n\npower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP42C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP42C'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=TIP42.PDF', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nTIP42C\n\npower PNP Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBT2222A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBT2222A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/MMBT2222A.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nMMBT2222A\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PMBT2222A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PMBT2222A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PMBT2222A.pdf', 'search_text':'/usr/share/kicad/symbols/Transistor_BJT.kicad_sym\nPMBT2222A\n\nNPN Transistor', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] })])