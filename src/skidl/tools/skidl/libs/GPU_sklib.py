from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

GPU = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'MC6845', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MC6845'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-40_W15.24mm'], 'footprint':'Package_DIP:DIP-40_W15.24mm', 'keywords':'CRT controller', 'description':'', 'datasheet':'http://pdf.datasheetcatalog.com/datasheet_pdf/motorola/MC6845L_and_MC6845P.pdf', 'search_text':'/usr/share/kicad/symbols/GPU.kicad_sym\nMC6845\n\nCRT controller', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='10',name='MA6',func=pin_types.OUTPUT,unit=1),
            Pin(num='11',name='MA7',func=pin_types.OUTPUT,unit=1),
            Pin(num='12',name='MA8',func=pin_types.OUTPUT,unit=1),
            Pin(num='13',name='MA9',func=pin_types.OUTPUT,unit=1),
            Pin(num='14',name='MA10',func=pin_types.OUTPUT,unit=1),
            Pin(num='15',name='MA11',func=pin_types.OUTPUT,unit=1),
            Pin(num='16',name='MA12',func=pin_types.OUTPUT,unit=1),
            Pin(num='17',name='MA13',func=pin_types.OUTPUT,unit=1),
            Pin(num='18',name='DE',func=pin_types.OUTPUT,unit=1),
            Pin(num='19',name='CURSOR',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='~{RESET}',func=pin_types.INPUT,unit=1),
            Pin(num='20',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='21',name='CLK',func=pin_types.INPUT,unit=1),
            Pin(num='22',name='R/~{W}',func=pin_types.INPUT,unit=1),
            Pin(num='23',name='E',func=pin_types.INPUT,unit=1),
            Pin(num='24',name='RS',func=pin_types.INPUT,unit=1),
            Pin(num='25',name='~{CS}',func=pin_types.INPUT,unit=1),
            Pin(num='26',name='D7',func=pin_types.BIDIR,unit=1),
            Pin(num='27',name='D6',func=pin_types.BIDIR,unit=1),
            Pin(num='28',name='D5',func=pin_types.BIDIR,unit=1),
            Pin(num='29',name='D4',func=pin_types.BIDIR,unit=1),
            Pin(num='3',name='LPSTB',func=pin_types.INPUT,unit=1),
            Pin(num='30',name='D3',func=pin_types.BIDIR,unit=1),
            Pin(num='31',name='D2',func=pin_types.BIDIR,unit=1),
            Pin(num='32',name='D1',func=pin_types.BIDIR,unit=1),
            Pin(num='33',name='D0',func=pin_types.BIDIR,unit=1),
            Pin(num='34',name='RA4',func=pin_types.OUTPUT,unit=1),
            Pin(num='35',name='RA3',func=pin_types.OUTPUT,unit=1),
            Pin(num='36',name='RA2',func=pin_types.OUTPUT,unit=1),
            Pin(num='37',name='RA1',func=pin_types.OUTPUT,unit=1),
            Pin(num='38',name='RA0',func=pin_types.OUTPUT,unit=1),
            Pin(num='39',name='HS',func=pin_types.OUTPUT,unit=1),
            Pin(num='4',name='MA0',func=pin_types.OUTPUT,unit=1),
            Pin(num='40',name='VS',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='MA1',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='MA2',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='MA3',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='MA4',func=pin_types.OUTPUT,unit=1),
            Pin(num='9',name='MA5',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MC68A45', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MC68A45'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-40_W15.24mm', 'Package_DIP:DIP-40_W15.24mm'], 'footprint':'Package_DIP:DIP-40_W15.24mm', 'keywords':'CRT controller', 'description':'', 'datasheet':'http://pdf.datasheetcatalog.com/datasheet_pdf/motorola/MC6845L_and_MC6845P.pdf', 'search_text':'/usr/share/kicad/symbols/GPU.kicad_sym\nMC68A45\n\nCRT controller', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='10',name='MA6',func=pin_types.OUTPUT,unit=1),
            Pin(num='11',name='MA7',func=pin_types.OUTPUT,unit=1),
            Pin(num='12',name='MA8',func=pin_types.OUTPUT,unit=1),
            Pin(num='13',name='MA9',func=pin_types.OUTPUT,unit=1),
            Pin(num='14',name='MA10',func=pin_types.OUTPUT,unit=1),
            Pin(num='15',name='MA11',func=pin_types.OUTPUT,unit=1),
            Pin(num='16',name='MA12',func=pin_types.OUTPUT,unit=1),
            Pin(num='17',name='MA13',func=pin_types.OUTPUT,unit=1),
            Pin(num='18',name='DE',func=pin_types.OUTPUT,unit=1),
            Pin(num='19',name='CURSOR',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='~{RESET}',func=pin_types.INPUT,unit=1),
            Pin(num='20',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='21',name='CLK',func=pin_types.INPUT,unit=1),
            Pin(num='22',name='R/~{W}',func=pin_types.INPUT,unit=1),
            Pin(num='23',name='E',func=pin_types.INPUT,unit=1),
            Pin(num='24',name='RS',func=pin_types.INPUT,unit=1),
            Pin(num='25',name='~{CS}',func=pin_types.INPUT,unit=1),
            Pin(num='26',name='D7',func=pin_types.BIDIR,unit=1),
            Pin(num='27',name='D6',func=pin_types.BIDIR,unit=1),
            Pin(num='28',name='D5',func=pin_types.BIDIR,unit=1),
            Pin(num='29',name='D4',func=pin_types.BIDIR,unit=1),
            Pin(num='3',name='LPSTB',func=pin_types.INPUT,unit=1),
            Pin(num='30',name='D3',func=pin_types.BIDIR,unit=1),
            Pin(num='31',name='D2',func=pin_types.BIDIR,unit=1),
            Pin(num='32',name='D1',func=pin_types.BIDIR,unit=1),
            Pin(num='33',name='D0',func=pin_types.BIDIR,unit=1),
            Pin(num='34',name='RA4',func=pin_types.OUTPUT,unit=1),
            Pin(num='35',name='RA3',func=pin_types.OUTPUT,unit=1),
            Pin(num='36',name='RA2',func=pin_types.OUTPUT,unit=1),
            Pin(num='37',name='RA1',func=pin_types.OUTPUT,unit=1),
            Pin(num='38',name='RA0',func=pin_types.OUTPUT,unit=1),
            Pin(num='39',name='HS',func=pin_types.OUTPUT,unit=1),
            Pin(num='4',name='MA0',func=pin_types.OUTPUT,unit=1),
            Pin(num='40',name='VS',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='MA1',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='MA2',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='MA3',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='MA4',func=pin_types.OUTPUT,unit=1),
            Pin(num='9',name='MA5',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MC68B45', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MC68B45'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-40_W15.24mm', 'Package_DIP:DIP-40_W15.24mm', 'Package_DIP:DIP-40_W15.24mm'], 'footprint':'Package_DIP:DIP-40_W15.24mm', 'keywords':'CRT controller', 'description':'', 'datasheet':'http://pdf.datasheetcatalog.com/datasheet_pdf/motorola/MC6845L_and_MC6845P.pdf', 'search_text':'/usr/share/kicad/symbols/GPU.kicad_sym\nMC68B45\n\nCRT controller', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='10',name='MA6',func=pin_types.OUTPUT,unit=1),
            Pin(num='11',name='MA7',func=pin_types.OUTPUT,unit=1),
            Pin(num='12',name='MA8',func=pin_types.OUTPUT,unit=1),
            Pin(num='13',name='MA9',func=pin_types.OUTPUT,unit=1),
            Pin(num='14',name='MA10',func=pin_types.OUTPUT,unit=1),
            Pin(num='15',name='MA11',func=pin_types.OUTPUT,unit=1),
            Pin(num='16',name='MA12',func=pin_types.OUTPUT,unit=1),
            Pin(num='17',name='MA13',func=pin_types.OUTPUT,unit=1),
            Pin(num='18',name='DE',func=pin_types.OUTPUT,unit=1),
            Pin(num='19',name='CURSOR',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='~{RESET}',func=pin_types.INPUT,unit=1),
            Pin(num='20',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='21',name='CLK',func=pin_types.INPUT,unit=1),
            Pin(num='22',name='R/~{W}',func=pin_types.INPUT,unit=1),
            Pin(num='23',name='E',func=pin_types.INPUT,unit=1),
            Pin(num='24',name='RS',func=pin_types.INPUT,unit=1),
            Pin(num='25',name='~{CS}',func=pin_types.INPUT,unit=1),
            Pin(num='26',name='D7',func=pin_types.BIDIR,unit=1),
            Pin(num='27',name='D6',func=pin_types.BIDIR,unit=1),
            Pin(num='28',name='D5',func=pin_types.BIDIR,unit=1),
            Pin(num='29',name='D4',func=pin_types.BIDIR,unit=1),
            Pin(num='3',name='LPSTB',func=pin_types.INPUT,unit=1),
            Pin(num='30',name='D3',func=pin_types.BIDIR,unit=1),
            Pin(num='31',name='D2',func=pin_types.BIDIR,unit=1),
            Pin(num='32',name='D1',func=pin_types.BIDIR,unit=1),
            Pin(num='33',name='D0',func=pin_types.BIDIR,unit=1),
            Pin(num='34',name='RA4',func=pin_types.OUTPUT,unit=1),
            Pin(num='35',name='RA3',func=pin_types.OUTPUT,unit=1),
            Pin(num='36',name='RA2',func=pin_types.OUTPUT,unit=1),
            Pin(num='37',name='RA1',func=pin_types.OUTPUT,unit=1),
            Pin(num='38',name='RA0',func=pin_types.OUTPUT,unit=1),
            Pin(num='39',name='HS',func=pin_types.OUTPUT,unit=1),
            Pin(num='4',name='MA0',func=pin_types.OUTPUT,unit=1),
            Pin(num='40',name='VS',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='MA1',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='MA2',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='MA3',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='MA4',func=pin_types.OUTPUT,unit=1),
            Pin(num='9',name='MA5',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] })])