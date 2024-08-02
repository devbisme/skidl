from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Transistor_BJT = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'2N2219', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N2219'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-39-3'], 'footprint':'Package_TO_SOT_THT:TO-39-3', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/2N2219-D.PDF', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2N2646', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N2646'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-18-3'], 'footprint':'Package_TO_SOT_THT:TO-18-3', 'keywords':'UJT', 'description':'', 'datasheet':'http://www.bucek.name/pdf/2n2646,2647.pdf', 'pins':[
            Pin(num='1',name='B2',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='B1',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2N3055', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N3055'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-3'], 'footprint':'Package_TO_SOT_THT:TO-3', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/2N3055-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2N3904', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N3904'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/2N3903-D.PDF', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2N3906', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N3906'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/2N3906-D.PDF', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SA1015', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SA1015'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Low Noise Audio PNP Transistor', 'description':'', 'datasheet':'http://www.datasheetcatalog.org/datasheet/toshiba/905.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SB631', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SB631'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'High Voltage Transistor', 'description':'', 'datasheet':'http://pdf.datasheetcatalog.com/datasheet/sanyo/ds_pdf_e/2SB631.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SB817', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SB817'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-3PB-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-3PB-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://skory.gylcomp.hu/alkatresz/2SB817.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SC1815', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SC1815'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Low Noise Audio NPN Transistor', 'description':'', 'datasheet':'https://media.digikey.com/pdf/Data%20Sheets/Toshiba%20PDFs/2SC1815.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SC1941', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SC1941'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Audio High Voltage NPN Transistor', 'description':'', 'datasheet':'http://rtellason.com/transdata/2sc1941.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SC1945', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SC1945'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'RF Power NPN Transistor', 'description':'', 'datasheet':'http://rtellason.com/transdata/2sc1945.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SD1047', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SD1047'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-3PB-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-3PB-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.st.com/resource/en/datasheet/2sd1047.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SD600', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SD600'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'High Voltage Power Transistor', 'description':'', 'datasheet':'http://pdf.datasheetcatalog.com/datasheet/sanyo/ds_pdf_e/2SB631.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'320S14-U', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'320S14-U'}), 'ref_prefix':'Q', 'fplist':['Package_SO:SOIC-14_3.9x8.7mm_P1.27mm'], 'footprint':'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm', 'keywords':'dual pair pnp matched transistors', 'description':'', 'datasheet':'https://www.thatcorp.com/datashts/THAT_300-Series_Datasheet.pdf', 'pins':[
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
            Pin(num='9',func=Pin.types.INPUT,unit=4)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['3', '1', '11', '4', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['13', '14', '4', '11', '12']},{'label': 'uC', 'num': 3, 'pin_nums': ['7', '5', '6', '4', '11']},{'label': 'uD', 'num': 4, 'pin_nums': ['9', '8', '10', '4', '11']}] }),
        Part(**{ 'name':'BC107', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC107'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-18-3'], 'footprint':'Package_TO_SOT_THT:TO-18-3', 'keywords':'NPN low noise transistor', 'description':'', 'datasheet':'http://www.b-kainka.de/Daten/Transistor/BC108.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC160', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC160'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-39-3'], 'footprint':'Package_TO_SOT_THT:TO-39-3', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'http://www.farnell.com/datasheets/1697389.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC237', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC237'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Epitaxial Silicon NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC237-D.PDF', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC240', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC240'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'RF NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BF420-D.PDF', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC307', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC307'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'Epitaxial Silicon PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC307-D.PDF', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC413', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC413'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bc413_14_b_c.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC516', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC516'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Darlington Darl Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC516-D.PDF', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC517', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC517'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Darlington Darl Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC517-D74Z-D.PDF', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC547', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC547'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC550-D.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC557', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC557'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC556BTA-D.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC636', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC636'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC636-D.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC807', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC807'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC808-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC807W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC807W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC808-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC817', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC817'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC818-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC817W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC817W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC818-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC846BPN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC846BPN'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC846BPN.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '4']}] }),
        Part(**{ 'name':'BC846BS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC846BS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC846BS.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '5', '3']}] }),
        Part(**{ 'name':'BC856BS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC856BS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC856BS.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '6', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'BCP51', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCP51'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BCP51-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCV29', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCV29'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'transistor NPN Darlington', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BCV29_49.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCV61', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCV61'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-143'], 'footprint':'Package_TO_SOT_SMD:SOT-143', 'keywords':'Transistor Double NPN', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BCV61.pdf', 'pins':[
            Pin(num='1',name='C2',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCV62', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCV62'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-143'], 'footprint':'Package_TO_SOT_SMD:SOT-143', 'keywords':'Transistor Double PNP', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BCV62.pdf', 'pins':[
            Pin(num='1',name='C2',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCX51', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCX51'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/bcx51_bcx52_bcx53.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCX56', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCX56'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.nxp.com/docs/en/data-sheet/BCP56_BCX56_BC56PA.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD139', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD139'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001225.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD140', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD140'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001225.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD249', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD249'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD250', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD250'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD433', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD433'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD434', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD434'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD910', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD910'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001277.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD911', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD911'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001277.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW93', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW93'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BDW93C-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW94', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW94'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington PNP Transistor', 'description':'', 'datasheet':'http://www.bourns.com/data/global/pdfs/bdw94.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BF199', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BF199'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'RF NPN Transistor', 'description':'', 'datasheet':'http://www.micropik.com/PDF/BF199.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BF457', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BF457'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'NPN HV High Voltage Transistor', 'description':'', 'datasheet':'https://www.pcpaudio.com/pcpfiles/transistores/BF457-8-9.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BFR92', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BFR92'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'RF 5GHz NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BFR92A_N.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BFT92', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BFT92'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'RF 5GHz NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BFT92_CNV.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BUT11', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BUT11'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'High Voltage Power NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BUT11A-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DMMT5401', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DMMT5401'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23-6'], 'footprint':'Package_TO_SOT_SMD:SOT-23-6', 'keywords':'transistor PNP', 'description':'', 'datasheet':'https://www.diodes.com/assets/Datasheets/ds30437.pdf', 'pins':[
            Pin(num='1',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='4',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='E2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'DTA113T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA113T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA113Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA113Z'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA114E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA114E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA114G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA114G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA114T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA114T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA114W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA114W'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA114Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA114Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA115E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA115E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA115G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA115G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA115T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA115T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA115U', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA115U'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA123E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA123E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA123J', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA123J'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA123Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA123Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA124E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA124E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA124G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA124G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA124T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA124T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA124X', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA124X'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA125T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA125T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA143E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA143E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA143T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA143T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA143X', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA143X'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA143Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA143Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA143Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA143Z'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA144E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA144E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA144G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA144G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA144T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA144T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA144V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA144V'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA144W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA144W'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA1D3R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA1D3R'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTA214Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTA214Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB113E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB113E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB113Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB113Z'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB114E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB114E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB114G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB114G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB114T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB114T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB122J', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB122J'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB123E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB123E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB123T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB123T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB123Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB123Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB133H', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB133H'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB143T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB143T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTB163T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTB163T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital PNP Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC113T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC113T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC113Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC113Z'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC114E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC114E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC114G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC114G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC114T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC114T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC114W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC114W'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC114Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC114Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC115E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC115E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC115G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC115G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC115T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC115T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC115U', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC115U'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC123E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC123E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC123J', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC123J'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC123Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC123Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC124E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC124E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC124G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC124G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC124T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC124T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC124X', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC124X'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC125T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC125T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC143E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC143E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC143T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC143T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC143X', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC143X'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC143Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC143Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC143Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC143Z'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC144E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC144E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC144G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC144G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC144T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC144T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC144V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC144V'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC144W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC144W'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC1D3R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC1D3R'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTC214Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTC214Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD113E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD113E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD113Z', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD113Z'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD114E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD114E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD114G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD114G'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD114T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD114T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD122J', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD122J'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD123E', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD123E'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD123T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD123T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD123Y', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD123Y'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD133H', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD133H'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD143T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD143T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DTD163T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DTD163T'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'ROHM Digital NPN Transistor', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'EMH3', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'EMH3'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-563'], 'footprint':'Package_TO_SOT_SMD:SOT-563', 'keywords':'Dual NPN Transistor', 'description':'', 'datasheet':'http://rohmfs.rohm.com/en/products/databook/datasheet/discrete/transistor/digital/emh3t2r-e.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '3', '5']}] }),
        Part(**{ 'name':'FMB2227A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FMB2227A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SuperSOT-6'], 'footprint':'Package_TO_SOT_SMD:SuperSOT-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub/Collateral/FMB2227A-D.PDF', 'pins':[
            Pin(num='1',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='3',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='4',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '5', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['2', '4', '3']}] }),
        Part(**{ 'name':'IMH3A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IMH3A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:ROHM_SOT-457_ClockwisePinNumbering'], 'footprint':'Package_TO_SOT_SMD:ROHM_SOT-457_ClockwisePinNumbering', 'keywords':'Dual NPN Transistor', 'description':'', 'datasheet':'http://rohmfs.rohm.com/en/products/databook/datasheet/discrete/transistor/digital/emh3t2r-e.pdf', 'pins':[
            Pin(num='1',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='5',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='3',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '5', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '2']}] }),
        Part(**{ 'name':'KTD1624', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'KTD1624'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'Switching NPN Transistor', 'description':'', 'datasheet':'http://www2.kec.co.kr/data/databook/pdf/KTD/Eng/KTD1624.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MAT02', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MAT02'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-78-6'], 'footprint':'Package_TO_SOT_THT:TO-78-6', 'keywords':'Precision Dual Monolithic Transistor Low Noise EOL', 'description':'', 'datasheet':'http://www.elenota.pl/datasheet_download/93431/MAT02', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='E',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B',func=Pin.types.INPUT,unit=2),
            Pin(num='6',name='C',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '3', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '6', '5']}] }),
        Part(**{ 'name':'MJ2955', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MJ2955'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-3'], 'footprint':'Package_TO_SOT_THT:TO-3', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/2N3055-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MJE13003', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MJE13003'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Switching Power High Voltage NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MJE13003-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MJE13007G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MJE13007G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Switching Power NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MJE13007-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBTA42', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBTA42'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN High Voltage Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/MMBTA42LT1-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBTA92', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBTA92'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP High Voltage Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/MMBTA92LT1-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMDTA06', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDTA06'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SC-74-6_1.55x2.9mm_P0.95mm'], 'footprint':'Package_TO_SOT_SMD:SC-74-6_1.55x2.9mm_P0.95mm', 'keywords':'dual transistor NPN', 'description':'', 'datasheet':'https://www.diodes.com/assets/Datasheets/MMDTA06.pdf', 'pins':[
            Pin(num='1',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='3',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='4',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '5', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '3', '2']}] }),
        Part(**{ 'name':'MPSA42', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MPSA42'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN High Voltage Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MPSA42-D.PDF', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MPSA92', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MPSA92'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP High Voltage Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MPSA92-D.PDF', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MUN5211DW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MUN5211DW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'Dual NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub/Collateral/DTC114ED-D.PDF', 'pins':[
            Pin(num='3',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='5',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='1',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='2',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='6',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['3', '4', '5']},{'label': 'uB', 'num': 2, 'pin_nums': ['2', '6', '1']}] }),
        Part(**{ 'name':'PN2222A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PN2222A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/PN2222-D.PDF', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PZT2222A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PZT2222A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'NPN General Puprose Transistor SMD', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/PN2222-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PZT3904', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PZT3904'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pdf/datasheet/pzt3904-d.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PZT3906', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PZT3906'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pdf/datasheet/pzt3906-d.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PZTA42', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PZTA42'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'NPN High Voltage Transistor SMD', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/PZTA42T1-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PZTA92', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PZTA92'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'PNP High Voltage Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/PZTA92T1-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'S8050', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'S8050'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'S8050 NPN Low Voltage High Current Transistor', 'description':'', 'datasheet':'http://www.unisonic.com.tw/datasheet/S8050.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'S8550', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'S8550'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'S8550 PNP Low Voltage High Current Transistor', 'description':'', 'datasheet':'http://www.unisonic.com.tw/datasheet/S8550.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SSM2210', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SSM2210'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'audio npn dual', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/obsolete-data-sheets/SSM2210.pdf', 'pins':[
            Pin(num='1',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='7',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='8',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['3', '1', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['7', '8', '6']}] }),
        Part(**{ 'name':'SSM2220', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SSM2220'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'audio pnp dual', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/SSM2220.pdf', 'pins':[
            Pin(num='1',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='7',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='8',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '3', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['7', '8', '6']}] }),
        Part(**{ 'name':'TIP120', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP120'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington Power NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/TIP120-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP125', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP125'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington Power PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/TIP120-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP2955', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP2955'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-218-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-218-3_Vertical', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/TIP3055-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP2955G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP2955G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-247-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-247-3_Vertical', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/TIP3055-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP3055', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP3055'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-218-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-218-3_Vertical', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/TIP3055-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP3055G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP3055G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-247-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-247-3_Vertical', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/TIP3055-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'UMH3N', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'UMH3N'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'Dual NPN Transistor', 'description':'', 'datasheet':'http://rohmfs.rohm.com/en/products/databook/datasheet/discrete/transistor/digital/emh3t2r-e.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'2N2647', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N2647'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-18-3', 'Package_TO_SOT_THT:TO-18-3'], 'footprint':'Package_TO_SOT_THT:TO-18-3', 'keywords':'UJT', 'description':'', 'datasheet':'http://www.bucek.name/pdf/2n2646,2647.pdf', 'pins':[
            Pin(num='1',name='B2',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='B1',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2N3905', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N3905'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.nteinc.com/specs/original/2N3905_06.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2SC4213', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2SC4213'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://toshiba.semicon-storage.com/info/docget.jsp?did=19305&prodName=2SC4213', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC108', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC108'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-18-3', 'Package_TO_SOT_THT:TO-18-3'], 'footprint':'Package_TO_SOT_THT:TO-18-3', 'keywords':'NPN low noise transistor', 'description':'', 'datasheet':'http://www.b-kainka.de/Daten/Transistor/BC108.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC109', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC109'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-18-3', 'Package_TO_SOT_THT:TO-18-3', 'Package_TO_SOT_THT:TO-18-3'], 'footprint':'Package_TO_SOT_THT:TO-18-3', 'keywords':'NPN low noise transistor', 'description':'', 'datasheet':'http://www.farnell.com/datasheets/296634.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC140', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC140'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-39-3', 'Package_TO_SOT_THT:TO-39-3'], 'footprint':'Package_TO_SOT_THT:TO-39-3', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.farnell.com/datasheets/296634.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC141', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC141'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-39-3', 'Package_TO_SOT_THT:TO-39-3', 'Package_TO_SOT_THT:TO-39-3'], 'footprint':'Package_TO_SOT_THT:TO-39-3', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.farnell.com/datasheets/296634.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC161', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC161'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-39-3', 'Package_TO_SOT_THT:TO-39-3'], 'footprint':'Package_TO_SOT_THT:TO-39-3', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'http://www.farnell.com/datasheets/1697389.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC212', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC212'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://media.digikey.com/pdf/Data%20Sheets/Fairchild%20PDFs/BC212.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC327', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC327'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC327-D.PDF', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC328', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC328'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.redrok.com/PNP_BC327_-45V_-800mA_0.625W_Hfe100_TO-92.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC337', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC337'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://diotec.com/tl_files/diotec/files/pdf/datasheets/bc337.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC338', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC338'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://diotec.com/tl_files/diotec/files/pdf/datasheets/bc337', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC413B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC413B'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bc413_14_b_c.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC413C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC413C'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bc413_14_b_c.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC414', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC414'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bc413_14_b_c.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC414B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC414B'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bc413_14_b_c.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC414C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC414C'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bc413_14_b_c.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC546', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC546'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC550-D.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC548', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC548'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC550-D.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC549', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC549'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC550-D.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC550', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC550'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC550-D.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC556', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC556'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC556BTA-D.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC558', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC558'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC556BTA-D.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC559', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC559'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC556BTA-D.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC560', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC560'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline', 'Package_TO_SOT_THT:TO-92_Inline'], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC556BTA-D.pdf', 'pins':[
            Pin(num='1',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC808', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC808'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC808-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC808W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC808W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC808-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC818', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC818'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC818-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC818W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC818W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC818-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC846', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC846'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC846_SER.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC846BDW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC846BDW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC846BDW1T1-D.PDF', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'BC846BPDW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC846BPDW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC846BPDW1T1-D.PDF', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '6', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '4', '3']}] }),
        Part(**{ 'name':'BC847', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC847BDW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847BDW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC846BDW1T1-D.PDF', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'BC847BPDW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847BPDW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC846BPDW1T1-D.PDF', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '2', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'BC847BPN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847BPN'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC847BPN.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'BC847BS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847BS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC847BS.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'BC847W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC848', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC848'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC848W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC848W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC849', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC849'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC849W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC849W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC850', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC850'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC850W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC850W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'NPN Small Signal Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC856', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC856'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC860-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC856BDW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC856BDW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC856BDW1T1-D.PDF', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '6', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '3', '5']}] }),
        Part(**{ 'name':'BC856W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC856W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC860-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC857', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC857'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC860-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC857BDW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC857BDW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BC856BDW1T1-D.PDF', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '6', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'BC857BS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC857BS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BC857BS.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'BC857W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC857W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC857SERIES_BC858SERIES_BC859SERIES_BC860SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541da0e3a1661', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC858', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC858'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BC860-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC858W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC858W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC857SERIES_BC858SERIES_BC859SERIES_BC860SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541da0e3a1661', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC859', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC859'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC857SERIES_BC858SERIES_BC859SERIES_BC860SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541da0e3a1661', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC859W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC859W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC857SERIES_BC858SERIES_BC859SERIES_BC860SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541da0e3a1661', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC860', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC860'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC857SERIES_BC858SERIES_BC859SERIES_BC860SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541da0e3a1661', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BC860W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC860W'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70', 'Package_TO_SOT_SMD:SOT-323_SC-70'], 'footprint':'Package_TO_SOT_SMD:SOT-323_SC-70', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC857SERIES_BC858SERIES_BC859SERIES_BC860SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541da0e3a1661', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCP53', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCP53'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/BCP53T1-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCP56', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCP56'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.nxp.com/docs/en/data-sheet/BCP56_BCX56_BC56PA.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCV49', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCV49'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3', 'Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'transistor NPN Darlington', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/BCV29_49.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCX52', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCX52'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3', 'Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/bcx51_bcx52_bcx53.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BCX53', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BCX53'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-89-3', 'Package_TO_SOT_SMD:SOT-89-3', 'Package_TO_SOT_SMD:SOT-89-3'], 'footprint':'Package_TO_SOT_SMD:SOT-89-3', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/bcx51_bcx52_bcx53.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD135', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD135'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001225.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD136', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD136'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001225.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD137', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD137'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001225.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD138', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD138'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001225.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD233', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD233'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'https://media.digikey.com/pdf/Data%20Sheets/Micro%20Commercial%20PDFs/BD233,235,237.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD234', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD234'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.electronica-pt.com/datasheets/bd/BD234.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD235', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD235'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'https://media.digikey.com/pdf/Data%20Sheets/Micro%20Commercial%20PDFs/BD233,235,237.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD236', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD236'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.electronica-pt.com/datasheets/bd/BD234.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD237', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD237'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'https://media.digikey.com/pdf/Data%20Sheets/Micro%20Commercial%20PDFs/BD233,235,237.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD238', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD238'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Low Voltage Transistor', 'description':'', 'datasheet':'http://www.electronica-pt.com/datasheets/bd/BD234.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD249A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD249A'}), 'ref_prefix':'Q', 'fplist':['', ''], 'footprint':'', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD249B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD249B'}), 'ref_prefix':'Q', 'fplist':['', '', ''], 'footprint':'', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD249C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD249C'}), 'ref_prefix':'Q', 'fplist':['', '', '', ''], 'footprint':'', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD250A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD250A'}), 'ref_prefix':'Q', 'fplist':['', ''], 'footprint':'', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD250B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD250B'}), 'ref_prefix':'Q', 'fplist':['', '', ''], 'footprint':'', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD250C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD250C'}), 'ref_prefix':'Q', 'fplist':['', '', '', ''], 'footprint':'', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.mospec.com.tw/pdf/power/BD249.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD435', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD435'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD436', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD436'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD437', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD437'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD438', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD438'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD439', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD439'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD440', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD440'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD441', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD441'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD442', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD442'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.cdil.com/datasheets/bd433_42.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD909', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD909'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Power NPN Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001277.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BD912', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BD912'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Power PNP Transistor', 'description':'', 'datasheet':'http://www.st.com/internet/com/TECHNICAL_RESOURCES/TECHNICAL_LITERATURE/DATASHEET/CD00001277.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW93A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW93A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BDW93C-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW93B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW93B'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BDW93C-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW93C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW93C'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BDW93C-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW94A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW94A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington PNP Transistor', 'description':'', 'datasheet':'http://www.bourns.com/data/global/pdfs/bdw94.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW94B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW94B'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington PNP Transistor', 'description':'', 'datasheet':'http://www.bourns.com/data/global/pdfs/bdw94.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BDW94C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BDW94C'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington PNP Transistor', 'description':'', 'datasheet':'http://www.bourns.com/data/global/pdfs/bdw94.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BF458', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BF458'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'NPN HV High Voltage Transistor', 'description':'', 'datasheet':'https://www.pcpaudio.com/pcpfiles/transistores/BF457-8-9.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BF459', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BF459'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical', 'Package_TO_SOT_THT:TO-126-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-126-3_Vertical', 'keywords':'NPN HV High Voltage Transistor', 'description':'', 'datasheet':'https://www.pcpaudio.com/pcpfiles/transistores/BF457-8-9.pdf', 'pins':[
            Pin(num='1',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='B',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BUT11A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BUT11A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'High Voltage Power NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/BUT11A-D.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'FFB2222A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FFB2222A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/MMPQ2222A-D.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '6', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '5', '3']}] }),
        Part(**{ 'name':'FFB2227A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FFB2227A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub/Collateral/FMB2227A-D.PDF', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '6', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '4']}] }),
        Part(**{ 'name':'FFB3904', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FFB3904'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/MMPQ3904-D.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'FFB3906', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FFB3906'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/MMPQ3906-D.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '6', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'FFB3946', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FFB3946'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub/Collateral/FMB3946-D.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '6', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'FFB5551', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FFB5551'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/FFB5551-D.PDF', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '2', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '3', '5']}] }),
        Part(**{ 'name':'FMB3946', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'FMB3946'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SuperSOT-6', 'Package_TO_SOT_SMD:SuperSOT-6'], 'footprint':'Package_TO_SOT_SMD:SuperSOT-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub/Collateral/FMB3946-D.pdf', 'pins':[
            Pin(num='1',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='3',name='B2',func=Pin.types.INPUT,unit=2),
            Pin(num='4',name='C2',func=Pin.types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '6', '5']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '2']}] }),
        Part(**{ 'name':'MBT2222ADW1T1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MBT2222ADW1T1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MBT2222ADW1T1-D.PDF', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'MBT3904DW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MBT3904DW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MBT3904DW1T1-D.PDF', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'MBT3906DW1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MBT3906DW1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MBT3906DW1T1-D.PDF', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'MBT3946DW1T1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MBT3946DW1T1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MBT3946DW1T1-D.PDF', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '6', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '4']}] }),
        Part(**{ 'name':'MJE13005G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MJE13005G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Switching Power NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MJE13005-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MJE13009G', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MJE13009G'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Switching Power NPN Transistor', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/MJE13009-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBT3904', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBT3904'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pdf/datasheet/pzt3904-d.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBT3906', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBT3906'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pdf/datasheet/pzt3906-d.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBT5550L', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBT5550L'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'www.onsemi.com/pub/Collateral/MMBT5550LT1-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBT5551L', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBT5551L'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'www.onsemi.com/pub/Collateral/MMBT5550LT1-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBTA06', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBTA06'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'SMD', 'description':'', 'datasheet':'https://diotec.com/request/datasheet/mmbta06.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBTA44', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBTA44'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'SMD', 'description':'', 'datasheet':'https://diotec.com/request/datasheet/mmbta42.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBTA56', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBTA56'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'SMD', 'description':'', 'datasheet':'https://diotec.com/request/datasheet/mmbta56.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBTA94', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBTA94'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'PNP', 'description':'', 'datasheet':'https://diotec.com/request/datasheet/mmbta92.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMDT2222A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDT2222A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.diodes.com/_files/datasheets/ds30125.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '5', '3']}] }),
        Part(**{ 'name':'MMDT3904', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDT3904'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.diodes.com/_files/datasheets/ds30088.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '5', '3']}] }),
        Part(**{ 'name':'MMDT3906', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDT3906'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'http://www.diodes.com/_files/datasheets/ds30124.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'MMDT3946', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDT3946'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'http://www.diodes.com/_files/datasheets/ds30123.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '5', '3']}] }),
        Part(**{ 'name':'MMDT5401', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDT5401'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'http://www.diodes.com/_files/datasheets/ds30169.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '1', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'MMDT5551', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMDT5551'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'http://www.diodes.com/_files/datasheets/ds30172.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '6', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '4', '5']}] }),
        Part(**{ 'name':'PBSS301PZ', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PBSS301PZ'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PBSS301PZ.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='4',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PMBT2222AYS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PMBT2222AYS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PMBT2222AYS.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '5', '3']}] }),
        Part(**{ 'name':'PMBT3904YS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PMBT3904YS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PMBT3904YS.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '4', '3']}] }),
        Part(**{ 'name':'PMBT3906YS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PMBT3906YS'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PMBT3906YS.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '4', '3']}] }),
        Part(**{ 'name':'PMBT3946YPN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PMBT3946YPN'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PMBT3946YPN.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '6']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '4']}] }),
        Part(**{ 'name':'PUMT1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PUMT1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'PNP/PNP Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PUMT1.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '6', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '4']}] }),
        Part(**{ 'name':'PUMX1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PUMX1'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'], 'footprint':'Package_TO_SOT_SMD:SOT-363_SC-70-6', 'keywords':'NPN/NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PUMX1.pdf', 'pins':[
            Pin(num='1',name='E1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='C1',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='4',name='E2',func=Pin.types.PASSIVE,unit=2),
            Pin(num='5',name='B2',func=Pin.types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['6', '1', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '3', '5']}] }),
        Part(**{ 'name':'TIP121', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP121'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington Power NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/TIP120-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP122', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP122'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington Power NPN Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/TIP120-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP126', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP126'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington Power PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/TIP120-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP127', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP127'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Darlington Power PNP Transistor', 'description':'', 'datasheet':'https://www.onsemi.com/pub/Collateral/TIP120-D.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP41', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP41'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=tip41.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP41A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP41A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=tip41.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP41B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP41B'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=tip41.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP41C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP41C'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power NPN Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=tip41.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP42', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP42'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=TIP42.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP42A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP42A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=TIP42.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP42B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP42B'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=TIP42.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TIP42C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TIP42C'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical', 'Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'power PNP Transistor', 'description':'', 'datasheet':'https://www.centralsemi.com/get_document.php?cmp=1&mergetype=pd&mergepath=pd&pdf_id=TIP42.PDF', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='C',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='E',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MMBT2222A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MMBT2222A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/MMBT2222A.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PMBT2222A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PMBT2222A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Transistor', 'description':'', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/PMBT2222A.pdf', 'pins':[
            Pin(num='1',name='B',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='E',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] })])