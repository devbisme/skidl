from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Interface_LineDriver = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'DS7820', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DS7820'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-14_W7.62mm'], 'footprint':'Package_DIP:DIP-14_W7.62mm', 'keywords':'Dual line receiver', 'description':'', 'datasheet':'http://pdf1.alldatasheet.com/datasheet-pdf/view/942427/NSC/DS7820.html', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nDS7820\n\nDual line receiver', 'pins':[
            Pin(num='1',name='INPUT',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='STROBE',func=pin_types.INPUT,unit=1),
            Pin(num='11',name='INPUT',func=pin_types.INPUT,unit=1),
            Pin(num='12',name='TERMINATION',func=pin_types.INPUT,unit=1),
            Pin(num='13',name='INPUT',func=pin_types.INPUT,unit=1),
            Pin(num='14',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='TERMINATION',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='INPUT',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='STROBE',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='RESPONSE_TIME',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='OUTPUT',func=pin_types.INPUT,unit=1),
            Pin(num='7',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='8',name='OUTPUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='9',name='RESPONSE_TIME',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DS7830', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DS7830'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-14_W7.62mm'], 'footprint':'Package_DIP:DIP-14_W7.62mm', 'keywords':'Dual differential line driver', 'description':'', 'datasheet':'http://pdf1.alldatasheet.com/datasheet-pdf/view/8473/NSC/DS7830J.html', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nDS7830\n\nDual differential line driver', 'pins':[
            Pin(num='1',name='A_1',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='B_4',func=pin_types.INPUT,unit=1),
            Pin(num='11',name='B_3',func=pin_types.INPUT,unit=1),
            Pin(num='12',name='B_2',func=pin_types.INPUT,unit=1),
            Pin(num='13',name='B_1',func=pin_types.INPUT,unit=1),
            Pin(num='14',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='A_2',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='A_3',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='A_4',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='A_AND_OUTPUT',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='A_NAND_OUTPUT',func=pin_types.INPUT,unit=1),
            Pin(num='7',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='8',name='B_NAND_OUTPUT',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='B_AND_OUTPUT',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'DS89C21', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DS89C21'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'rs422 tranciever', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/ds89c21.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nDS89C21\n\nrs422 tranciever', 'pins':[
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='RO',func=pin_types.OUTPUT,unit=1),
            Pin(num='3',name='DI',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='~{DO}',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='DO',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='~{RI}',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='RI',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'EL7242C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'EL7242C'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-8_W7.62mm'], 'footprint':'Package_DIP:DIP-8_W7.62mm', 'keywords':'Translateur TTL->VMOS. Double driver VMOS', 'description':'', 'datasheet':'http://pdf.datasheetcatalog.com/datasheet/elantec/EL7242CN.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nEL7242C\n\nTranslateur TTL->VMOS. Double driver VMOS', 'pins':[
            Pin(num='5',name='GND',func=pin_types.PWRIN),
            Pin(num='8',name='V+',func=pin_types.PWRIN),
            Pin(num='1',name='IN1',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='IN',func=pin_types.INPUT,unit=1),
            Pin(num='7',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='3',name='IN1',func=pin_types.INPUT,unit=2),
            Pin(num='4',name='IN',func=pin_types.INPUT,unit=2),
            Pin(num='6',name='OUT',func=pin_types.OUTPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['5', '8', '2', '7', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '8', '6', '4', '3']}] }),
        Part(**{ 'name':'MC3486N', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MC3486N'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-14_W7.62mm'], 'footprint':'Package_DIP:DIP-14_W7.62mm', 'keywords':'Quadruple differential line receiver', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/mc3486.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nMC3486N\n\nQuadruple differential line receiver', 'pins':[
            Pin(num='1',name='E-',func=pin_types.INPUT,unit=1),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='E+',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='OUT',func=pin_types.TRISTATE,unit=1),
            Pin(num='4',name='ENABLE',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=2),
            Pin(num='4',name='ENABLE',func=pin_types.INPUT,unit=2),
            Pin(num='5',name='OUT',func=pin_types.TRISTATE,unit=2),
            Pin(num='6',name='E+',func=pin_types.INPUT,unit=2),
            Pin(num='7',name='E-',func=pin_types.INPUT,unit=2),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=2),
            Pin(num='10',name='E+',func=pin_types.INPUT,unit=3),
            Pin(num='11',name='OUT',func=pin_types.TRISTATE,unit=3),
            Pin(num='12',name='ENABLE',func=pin_types.INPUT,unit=3),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=3),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=3),
            Pin(num='9',name='E-',func=pin_types.INPUT,unit=3),
            Pin(num='12',name='ENABLE',func=pin_types.INPUT,unit=4),
            Pin(num='13',name='OUT',func=pin_types.TRISTATE,unit=4),
            Pin(num='14',name='E+',func=pin_types.INPUT,unit=4),
            Pin(num='15',name='E-',func=pin_types.INPUT,unit=4),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=4),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=4)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['8', '16', '3', '2', '4', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['4', '7', '5', '6', '16', '8']},{'label': 'uC', 'num': 3, 'pin_nums': ['8', '10', '12', '11', '16', '9']},{'label': 'uD', 'num': 4, 'pin_nums': ['8', '15', '13', '12', '16', '14']}] }),
        Part(**{ 'name':'MC3487DX', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MC3487DX'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-16_3.9x9.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm', 'keywords':'Four independent differential line drivers', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/mc3487.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nMC3487DX\n\nFour independent differential line drivers', 'pins':[
            Pin(num='1',name='INPUT',func=pin_types.INPUT,unit=1),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='OUT+',func=pin_types.TRISTATE,unit=1),
            Pin(num='3',name='OUT-',func=pin_types.TRISTATE,unit=1),
            Pin(num='4',name='ENABLE',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=2),
            Pin(num='4',name='ENABLE',func=pin_types.INPUT,unit=2),
            Pin(num='5',name='OUT-',func=pin_types.TRISTATE,unit=2),
            Pin(num='6',name='OUT+',func=pin_types.TRISTATE,unit=2),
            Pin(num='7',name='INPUT',func=pin_types.INPUT,unit=2),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=2),
            Pin(num='10',name='OUT+',func=pin_types.TRISTATE,unit=3),
            Pin(num='11',name='OUT-',func=pin_types.TRISTATE,unit=3),
            Pin(num='12',name='ENABLE',func=pin_types.INPUT,unit=3),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=3),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=3),
            Pin(num='9',name='INPUT',func=pin_types.INPUT,unit=3),
            Pin(num='12',name='ENABLE',func=pin_types.INPUT,unit=4),
            Pin(num='13',name='OUT-',func=pin_types.TRISTATE,unit=4),
            Pin(num='14',name='OUT+',func=pin_types.TRISTATE,unit=4),
            Pin(num='15',name='INPUT',func=pin_types.INPUT,unit=4),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=4),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=4)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['8', '1', '3', '16', '4', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['7', '5', '8', '16', '6', '4']},{'label': 'uC', 'num': 3, 'pin_nums': ['10', '12', '8', '16', '11', '9']},{'label': 'uD', 'num': 4, 'pin_nums': ['12', '16', '14', '15', '13', '8']}] }),
        Part(**{ 'name':'MC3487N', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MC3487N'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-16_W7.62mm'], 'footprint':'Package_DIP:DIP-16_W7.62mm', 'keywords':'Four independent differential line drivers', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/mc3487.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nMC3487N\n\nFour independent differential line drivers', 'pins':[
            Pin(num='1',name='INPUT',func=pin_types.INPUT,unit=1),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='OUT+',func=pin_types.TRISTATE,unit=1),
            Pin(num='3',name='OUT-',func=pin_types.TRISTATE,unit=1),
            Pin(num='4',name='ENABLE',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=2),
            Pin(num='4',name='ENABLE',func=pin_types.INPUT,unit=2),
            Pin(num='5',name='OUT-',func=pin_types.TRISTATE,unit=2),
            Pin(num='6',name='OUT+',func=pin_types.TRISTATE,unit=2),
            Pin(num='7',name='INPUT',func=pin_types.INPUT,unit=2),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=2),
            Pin(num='10',name='OUT+',func=pin_types.TRISTATE,unit=3),
            Pin(num='11',name='OUT-',func=pin_types.TRISTATE,unit=3),
            Pin(num='12',name='ENABLE',func=pin_types.INPUT,unit=3),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=3),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=3),
            Pin(num='9',name='INPUT',func=pin_types.INPUT,unit=3),
            Pin(num='12',name='ENABLE',func=pin_types.INPUT,unit=4),
            Pin(num='13',name='OUT-',func=pin_types.TRISTATE,unit=4),
            Pin(num='14',name='OUT+',func=pin_types.TRISTATE,unit=4),
            Pin(num='15',name='INPUT',func=pin_types.INPUT,unit=4),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=4),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=4)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['4', '1', '2', '16', '8', '3']},{'label': 'uB', 'num': 2, 'pin_nums': ['16', '6', '4', '7', '5', '8']},{'label': 'uC', 'num': 3, 'pin_nums': ['11', '16', '9', '10', '8', '12']},{'label': 'uD', 'num': 4, 'pin_nums': ['8', '15', '13', '12', '14', '16']}] }),
        Part(**{ 'name':'UA9637', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'UA9637'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-8_W7.62mm'], 'footprint':'Package_DIP:DIP-8_W7.62mm', 'keywords':'Dual differential line receiver', 'description':'', 'datasheet':'http://pdf.datasheetcatalog.com/datasheets2/28/284473_1.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nUA9637\n\nDual differential line receiver', 'pins':[
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='IN-',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='IN+',func=pin_types.INPUT,unit=1),
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=2),
            Pin(num='3',name='OUT',func=pin_types.OUTPUT,unit=2),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=2),
            Pin(num='5',name='IN-',func=pin_types.INPUT,unit=2),
            Pin(num='6',name='IN+',func=pin_types.INPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['7', '8', '1', '4', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['1', '5', '3', '6', '4']}] }),
        Part(**{ 'name':'UA9638CD', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'UA9638CD'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Dual high-speed differential line driver', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/ua9638.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nUA9638CD\n\nDual high-speed differential line driver', 'pins':[
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='IN',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='OUTA',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='OUTB',func=pin_types.OUTPUT,unit=1),
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=2),
            Pin(num='3',name='IN',func=pin_types.INPUT,unit=2),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=2),
            Pin(num='5',name='OUTA',func=pin_types.OUTPUT,unit=2),
            Pin(num='6',name='OUTB',func=pin_types.OUTPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '7', '4', '8']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '6', '4', '1']}] }),
        Part(**{ 'name':'UA9638CP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'UA9638CP'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-8_W7.62mm'], 'footprint':'Package_DIP:DIP-8_W7.62mm', 'keywords':'Dual high-speed differential line driver', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/ua9638.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nUA9638CP\n\nDual high-speed differential line driver', 'pins':[
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='IN',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='OUTA',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='OUTB',func=pin_types.OUTPUT,unit=1),
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=2),
            Pin(num='3',name='IN',func=pin_types.INPUT,unit=2),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=2),
            Pin(num='5',name='OUTA',func=pin_types.OUTPUT,unit=2),
            Pin(num='6',name='OUTB',func=pin_types.OUTPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['4', '8', '7', '2', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '6', '4', '1']}] }),
        Part(**{ 'name':'DS8830', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DS8830'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-14_W7.62mm', 'Package_DIP:DIP-14_W7.62mm'], 'footprint':'Package_DIP:DIP-14_W7.62mm', 'keywords':'Dual differential line driver', 'description':'', 'datasheet':'http://pdf1.alldatasheet.com/datasheet-pdf/view/8473/NSC/DS7830J.html', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nDS8830\n\nDual differential line driver', 'pins':[
            Pin(num='1',name='A_1',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='B_4',func=pin_types.INPUT,unit=1),
            Pin(num='11',name='B_3',func=pin_types.INPUT,unit=1),
            Pin(num='12',name='B_2',func=pin_types.INPUT,unit=1),
            Pin(num='13',name='B_1',func=pin_types.INPUT,unit=1),
            Pin(num='14',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='A_2',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='A_3',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='A_4',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='A_AND_OUTPUT',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='A_NAND_OUTPUT',func=pin_types.INPUT,unit=1),
            Pin(num='7',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='8',name='B_NAND_OUTPUT',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='B_AND_OUTPUT',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'UA9638CDE4', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'UA9638CDE4'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Dual high-speed differential line driver', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/ua9638.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nUA9638CDE4\n\nDual high-speed differential line driver', 'pins':[
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='IN',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='OUTA',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='OUTB',func=pin_types.OUTPUT,unit=1),
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=2),
            Pin(num='3',name='IN',func=pin_types.INPUT,unit=2),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=2),
            Pin(num='5',name='OUTA',func=pin_types.OUTPUT,unit=2),
            Pin(num='6',name='OUTB',func=pin_types.OUTPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '4', '8', '2', '7']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '1', '6', '4']}] }),
        Part(**{ 'name':'UA9638CDG4', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'UA9638CDG4'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Dual high-speed differential line driver', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/ua9638.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nUA9638CDG4\n\nDual high-speed differential line driver', 'pins':[
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='IN',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='OUTA',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='OUTB',func=pin_types.OUTPUT,unit=1),
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=2),
            Pin(num='3',name='IN',func=pin_types.INPUT,unit=2),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=2),
            Pin(num='5',name='OUTA',func=pin_types.OUTPUT,unit=2),
            Pin(num='6',name='OUTB',func=pin_types.OUTPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '7', '1', '4', '8']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '3', '6', '1', '4']}] }),
        Part(**{ 'name':'UA9638CDR', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'UA9638CDR'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Dual high-speed differential line driver', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/ua9638.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nUA9638CDR\n\nDual high-speed differential line driver', 'pins':[
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='IN',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='OUTA',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='OUTB',func=pin_types.OUTPUT,unit=1),
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=2),
            Pin(num='3',name='IN',func=pin_types.INPUT,unit=2),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=2),
            Pin(num='5',name='OUTA',func=pin_types.OUTPUT,unit=2),
            Pin(num='6',name='OUTB',func=pin_types.OUTPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '8', '4', '2', '7']},{'label': 'uB', 'num': 2, 'pin_nums': ['1', '3', '5', '6', '4']}] }),
        Part(**{ 'name':'UA9638CDRG4', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'UA9638CDRG4'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Dual high-speed differential line driver', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/ua9638.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nUA9638CDRG4\n\nDual high-speed differential line driver', 'pins':[
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='IN',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='OUTA',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='OUTB',func=pin_types.OUTPUT,unit=1),
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=2),
            Pin(num='3',name='IN',func=pin_types.INPUT,unit=2),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=2),
            Pin(num='5',name='OUTA',func=pin_types.OUTPUT,unit=2),
            Pin(num='6',name='OUTB',func=pin_types.OUTPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '4', '7', '8']},{'label': 'uB', 'num': 2, 'pin_nums': ['3', '5', '4', '1', '6']}] }),
        Part(**{ 'name':'UA9638CPE4', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'UA9638CPE4'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-8_W7.62mm', 'Package_DIP:DIP-8_W7.62mm'], 'footprint':'Package_DIP:DIP-8_W7.62mm', 'keywords':'Dual high-speed differential line driver', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/ua9638.pdf', 'search_text':'/usr/share/kicad/symbols/Interface_LineDriver.kicad_sym\nUA9638CPE4\n\nDual high-speed differential line driver', 'pins':[
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='IN',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='OUTA',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='OUTB',func=pin_types.OUTPUT,unit=1),
            Pin(num='1',name='VCC',func=pin_types.PWRIN,unit=2),
            Pin(num='3',name='IN',func=pin_types.INPUT,unit=2),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=2),
            Pin(num='5',name='OUTA',func=pin_types.OUTPUT,unit=2),
            Pin(num='6',name='OUTB',func=pin_types.OUTPUT,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '2', '4', '8', '7']},{'label': 'uB', 'num': 2, 'pin_nums': ['6', '1', '4', '3', '5']}] })])