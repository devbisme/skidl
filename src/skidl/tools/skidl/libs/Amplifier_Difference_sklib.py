from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Amplifier_Difference = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'AD628', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AD628'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'', 'keywords':'difference amplifier', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/AD628.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nAD628\n\ndifference amplifier', 'pins':[
            Pin(num='1',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='VREF',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='CFILT',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='~',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='RG',func=pin_types.PASSIVE,unit=1),
            Pin(num='7',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='8',name='-',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'AD8207', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AD8207'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'highside HS current sense difference amplifier linear buffered', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/AD8207.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nAD8207\n\nhighside HS current sense difference amplifier linear buffered', 'pins':[
            Pin(num='1',name='-IN',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='Vref2',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='RANGE',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='Vref1',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='+IN',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'AD8276', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AD8276'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'', 'keywords':'difference amplifier', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/AD8276_8277.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nAD8276\n\ndifference amplifier', 'pins':[
            Pin(num='1',name='REF',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='SENSE',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='~',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='8',name='~',func=pin_types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'AD8475ACPZ', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AD8475ACPZ'}), 'ref_prefix':'U', 'fplist':['Package_CSP:LFCSP-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm'], 'footprint':'Package_CSP:LFCSP-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm', 'keywords':'selectable gain ADC driver', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/AD8475.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nAD8475ACPZ\n\nselectable gain ADC driver', 'pins':[
            Pin(num='1',name='+IN0.4x',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='+',func=pin_types.OUTPUT,unit=1),
            Pin(num='11',name='-',func=pin_types.OUTPUT,unit=1),
            Pin(num='12',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='13',name='-Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='14',name='-Vs',func=pin_types.PASSIVE,unit=1),
            Pin(num='15',name='-Vs',func=pin_types.PASSIVE,unit=1),
            Pin(num='16',name='+IN0.4x',func=pin_types.INPUT,unit=1),
            Pin(num='17',name='EP',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+IN0.8x',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='-IN0.8x',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='-IN0.4x',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='-IN0.4x',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='+Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='+Vs',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',name='+Vs',func=pin_types.PASSIVE,unit=1),
            Pin(num='9',name='VOCM',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'AD8475xRMZ', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AD8475xRMZ'}), 'ref_prefix':'U', 'fplist':['Package_SO:MSOP-10_3x3mm_P0.5mm'], 'footprint':'Package_SO:MSOP-10_3x3mm_P0.5mm', 'keywords':'selectable gain ADC driver', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/AD8475.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nAD8475xRMZ\n\nselectable gain ADC driver', 'pins':[
            Pin(num='1',name='-IN0.8x',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='+IN0.8x',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='-IN0.4x',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='+Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='4',name='VOCM',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='+',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='-',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='8',name='-Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='9',name='+IN0.4x',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ADA4938-1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ADA4938-1'}), 'ref_prefix':'U', 'fplist':['Package_CSP:LFCSP-16-1EP_3x3mm_P0.5mm_EP1.3x1.3mm_ThermalVias'], 'footprint':'Package_CSP:LFCSP-16-1EP_3x3mm_P0.5mm_EP1.3x1.3mm_ThermalVias', 'keywords':'Fully-Differential Amplifier ADC Driver', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/ADA4938-1_4938-2.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nADA4938-1\n\nFully-Differential Amplifier ADC Driver', 'pins':[
            Pin(num='1',name='FB-',func=pin_types.OUTPUT,unit=1),
            Pin(num='10',func=pin_types.OUTPUT,unit=1),
            Pin(num='11',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='FB+',func=pin_types.OUTPUT,unit=1),
            Pin(num='9',name='V_{OCM}',func=pin_types.INPUT,unit=1),
            Pin(num='12',name='~{PD}',func=pin_types.INPUT,unit=2),
            Pin(num='13',name='V-',func=pin_types.PWRIN,unit=2),
            Pin(num='14',name='V-',func=pin_types.PASSIVE,unit=2),
            Pin(num='15',name='V-',func=pin_types.PASSIVE,unit=2),
            Pin(num='16',name='V-',func=pin_types.PASSIVE,unit=2),
            Pin(num='17',name='PAD',func=pin_types.PASSIVE,unit=2),
            Pin(num='5',name='V+',func=pin_types.PWRIN,unit=2),
            Pin(num='6',name='V+',func=pin_types.PASSIVE,unit=2),
            Pin(num='7',name='V+',func=pin_types.PASSIVE,unit=2),
            Pin(num='8',name='V+',func=pin_types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '9', '10', '3', '11', '1', '4']},{'label': 'uB', 'num': 2, 'pin_nums': ['17', '7', '16', '13', '6', '15', '5', '8', '12', '14']}] }),
        Part(**{ 'name':'ADA4940-1xCP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ADA4940-1xCP'}), 'ref_prefix':'U', 'fplist':['Package_CSP:LFCSP-16-1EP_3x3mm_P0.5mm_EP1.3x1.3mm_ThermalVias'], 'footprint':'Package_CSP:LFCSP-16-1EP_3x3mm_P0.5mm_EP1.3x1.3mm_ThermalVias', 'keywords':'differential amplifier', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/ADA4940-1_4940-2.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nADA4940-1xCP\n\ndifferential amplifier', 'pins':[
            Pin(num='1',name='-FB',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='+OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='11',name='-OUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='12',name='~{DISABLE}',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='+IN',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='-IN',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='+FB',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='VOCM',func=pin_types.INPUT,unit=1),
            Pin(num='13',name='-Vs',func=pin_types.PWRIN,unit=2),
            Pin(num='14',name='-Vs',func=pin_types.PASSIVE,unit=2),
            Pin(num='15',name='-Vs',func=pin_types.PASSIVE,unit=2),
            Pin(num='16',name='-Vs',func=pin_types.PASSIVE,unit=2),
            Pin(num='17',name='EP',func=pin_types.PASSIVE,unit=2),
            Pin(num='5',name='+Vs',func=pin_types.PWRIN,unit=2),
            Pin(num='6',name='+Vs',func=pin_types.PASSIVE,unit=2),
            Pin(num='7',name='+Vs',func=pin_types.PASSIVE,unit=2),
            Pin(num='8',name='+Vs',func=pin_types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '11', '12', '4', '2', '10', '9', '3']},{'label': 'uB', 'num': 2, 'pin_nums': ['14', '13', '6', '17', '15', '7', '5', '8', '16']}] }),
        Part(**{ 'name':'ADA4940-2', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ADA4940-2'}), 'ref_prefix':'U', 'fplist':['Package_CSP:LFCSP-24-1EP_4x4mm_P0.5mm_EP2.5x2.5mm'], 'footprint':'Package_CSP:LFCSP-24-1EP_4x4mm_P0.5mm_EP2.5x2.5mm', 'keywords':'differential amplifier', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/ADA4940-1_4940-2.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nADA4940-2\n\ndifferential amplifier', 'pins':[
            Pin(num='1',name='-IN1',func=pin_types.INPUT,unit=1),
            Pin(num='17',name='VOCM1',func=pin_types.INPUT,unit=1),
            Pin(num='18',name='+1',func=pin_types.OUTPUT,unit=1),
            Pin(num='19',name='-1',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='+FB1',func=pin_types.INPUT,unit=1),
            Pin(num='20',name='~{DISABLE1}',func=pin_types.INPUT,unit=1),
            Pin(num='23',name='-FB1',func=pin_types.INPUT,unit=1),
            Pin(num='24',name='+IN1',func=pin_types.INPUT,unit=1),
            Pin(num='11',name='VOCM2',func=pin_types.INPUT,unit=2),
            Pin(num='12',name='+2',func=pin_types.OUTPUT,unit=2),
            Pin(num='13',name='-2',func=pin_types.OUTPUT,unit=2),
            Pin(num='14',name='~{DISABLE2}',func=pin_types.INPUT,unit=2),
            Pin(num='5',name='-FB2',func=pin_types.INPUT,unit=2),
            Pin(num='6',name='+IN2',func=pin_types.INPUT,unit=2),
            Pin(num='7',name='-IN2',func=pin_types.INPUT,unit=2),
            Pin(num='8',name='+FB2',func=pin_types.INPUT,unit=2),
            Pin(num='21',name='-FB2',func=pin_types.INPUT,unit=3),
            Pin(num='22',name='-FB2',func=pin_types.INPUT,unit=3),
            Pin(num='25',name='EP',func=pin_types.PASSIVE,unit=3),
            Pin(num='3',name='+FB2',func=pin_types.INPUT,unit=3),
            Pin(num='4',name='+FB2',func=pin_types.INPUT,unit=3),
            Pin(num='10',name='+FB2',func=pin_types.INPUT,unit=4),
            Pin(num='15',name='-FB2',func=pin_types.INPUT,unit=4),
            Pin(num='16',name='-FB2',func=pin_types.INPUT,unit=4),
            Pin(num='9',name='+FB2',func=pin_types.INPUT,unit=4)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['23', '18', '1', '2', '17', '24', '20', '19']},{'label': 'uB', 'num': 2, 'pin_nums': ['11', '12', '6', '14', '8', '7', '5', '13']},{'label': 'uC', 'num': 3, 'pin_nums': ['21', '25', '22', '4', '3']},{'label': 'uD', 'num': 4, 'pin_nums': ['10', '16', '15', '9']}] }),
        Part(**{ 'name':'AMC1100DWV', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AMC1100DWV'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_7.5x5.85mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_7.5x5.85mm_P1.27mm', 'keywords':'isolated difference amplifier', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/amc1100.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nAMC1100DWV\n\nisolated difference amplifier', 'pins':[
            Pin(num='1',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='-',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='+',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='V+',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM733CH', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM733CH'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-5-10'], 'footprint':'Package_TO_SOT_THT:TO-5-10', 'keywords':'single differential video opamp', 'description':'', 'datasheet':'http://www.soemtron.org/downloads/disposals/lm733cn.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nLM733CH\n\nsingle differential video opamp', 'pins':[
            Pin(num='1',name='~',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='2A',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='2B',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='1B',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='~',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='~',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='9',name='1A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM733CN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM733CN'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-14_W7.62mm'], 'footprint':'Package_DIP:DIP-14_W7.62mm', 'keywords':'single differential video opamp', 'description':'', 'datasheet':'http://www.soemtron.org/downloads/disposals/lm733cn.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nLM733CN\n\nsingle differential video opamp', 'pins':[
            Pin(num='1',name='~',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='11',name='1A',func=pin_types.PASSIVE,unit=1),
            Pin(num='12',name='2A',func=pin_types.PASSIVE,unit=1),
            Pin(num='13',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='14',name='~',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='3',name='2B',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='1B',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='7',name='~',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='~',func=pin_types.OUTPUT,unit=1),
            Pin(num='9',name='NC',func=pin_types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LTC1992-x-xMS8', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LTC1992-x-xMS8'}), 'ref_prefix':'U', 'fplist':['Package_SO:MSOP-8_3x3mm_P0.65mm'], 'footprint':'Package_SO:MSOP-8_3x3mm_P0.65mm', 'keywords':'fully differential amplifier', 'description':'', 'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/1992fb.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nLTC1992-x-xMS8\n\nfully differential amplifier', 'pins':[
            Pin(num='1',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='V_{OCM}',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='+V_{S}',func=pin_types.PWRIN,unit=1),
            Pin(num='4',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='-V_{S}',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='V_{Mid}',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='+',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'THS4521IDGK', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'THS4521IDGK'}), 'ref_prefix':'U', 'fplist':['Package_SO:VSSOP-8_3x3mm_P0.65mm'], 'footprint':'Package_SO:VSSOP-8_3x3mm_P0.65mm', 'keywords':'differential amplifier', 'description':'', 'datasheet':'https://www.ti.com/lit/ds/symlink/ths4521.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nTHS4521IDGK\n\ndifferential amplifier', 'pins':[
            Pin(num='1',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='V_{OCM}',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='V_{S+}',func=pin_types.PWRIN,unit=1),
            Pin(num='4',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='V_{S-}',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='~{PD}',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='+',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'THS4551xRGT', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'THS4551xRGT'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm'], 'footprint':'Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm', 'keywords':'differential amplifier', 'description':'', 'datasheet':'https://www.ti.com/lit/ds/symlink/ths4551.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nTHS4551xRGT\n\ndifferential amplifier', 'pins':[
            Pin(num='1',name='FB-',func=pin_types.OUTPUT,unit=1),
            Pin(num='10',name='OUT+',func=pin_types.OUTPUT,unit=1),
            Pin(num='11',name='OUT-',func=pin_types.OUTPUT,unit=1),
            Pin(num='12',name='~{PD}',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='IN+',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='IN-',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='FB+',func=pin_types.OUTPUT,unit=1),
            Pin(num='9',name='VOCM',func=pin_types.INPUT,unit=1),
            Pin(num='13',name='VS-',func=pin_types.PWRIN,unit=2),
            Pin(num='14',name='VS-',func=pin_types.PASSIVE,unit=2),
            Pin(num='15',name='VS-',func=pin_types.PASSIVE,unit=2),
            Pin(num='16',name='VS-',func=pin_types.PASSIVE,unit=2),
            Pin(num='17',name='EP',func=pin_types.PASSIVE,unit=2),
            Pin(num='5',name='VS+',func=pin_types.PWRIN,unit=2),
            Pin(num='6',name='VS+',func=pin_types.PASSIVE,unit=2),
            Pin(num='7',name='VS+',func=pin_types.PASSIVE,unit=2),
            Pin(num='8',name='VS+',func=pin_types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['9', '3', '11', '12', '4', '10', '2', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['14', '16', '17', '7', '5', '13', '6', '15', '8']}] }),
        Part(**{ 'name':'AMC1200BDWV', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AMC1200BDWV'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_7.5x5.85mm_P1.27mm', 'Package_SO:SOIC-8_7.5x5.85mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_7.5x5.85mm_P1.27mm', 'keywords':'isolated difference amplifier', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/amc1200.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nAMC1200BDWV\n\nisolated difference amplifier', 'pins':[
            Pin(num='1',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='-',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='+',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='V+',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'AMC1300BDWV', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AMC1300BDWV'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_7.5x5.85mm_P1.27mm', 'Package_SO:SOIC-8_7.5x5.85mm_P1.27mm', 'Package_SO:SOIC-8_7.5x5.85mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_7.5x5.85mm_P1.27mm', 'keywords':'isolated difference amplifier', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/amc1300.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nAMC1300BDWV\n\nisolated difference amplifier', 'pins':[
            Pin(num='1',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='-',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='+',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='V+',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'AMC1300DWV', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AMC1300DWV'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_7.5x5.85mm_P1.27mm', 'Package_SO:SOIC-8_7.5x5.85mm_P1.27mm', 'Package_SO:SOIC-8_7.5x5.85mm_P1.27mm', 'Package_SO:SOIC-8_7.5x5.85mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_7.5x5.85mm_P1.27mm', 'keywords':'isolated difference amplifier', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/amc1300.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nAMC1300DWV\n\nisolated difference amplifier', 'pins':[
            Pin(num='1',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='-',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='+',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='V+',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'INA105KP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'INA105KP'}), 'ref_prefix':'U', 'fplist':['', 'Package_DIP:DIP-8_W7.62mm'], 'footprint':'', 'keywords':'difference amplifier', 'description':'', 'datasheet':'https://www.ti.com/lit/ds/symlink/ina105.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nINA105KP\n\ndifference amplifier', 'pins':[
            Pin(num='1',name='REF',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='SENSE',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='~',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='8',name='~',func=pin_types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'INA105KU', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'INA105KU'}), 'ref_prefix':'U', 'fplist':['', 'Package_DIP:DIP-8_W7.62mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'', 'keywords':'difference amplifier', 'description':'', 'datasheet':'https://www.ti.com/lit/ds/symlink/ina105.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nINA105KU\n\ndifference amplifier', 'pins':[
            Pin(num='1',name='REF',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='SENSE',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='~',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='8',name='~',func=pin_types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM733H', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM733H'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-5-10', 'Package_TO_SOT_THT:TO-5-10'], 'footprint':'Package_TO_SOT_THT:TO-5-10', 'keywords':'single differential video opamp', 'description':'', 'datasheet':'http://www.soemtron.org/downloads/disposals/lm733cn.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nLM733H\n\nsingle differential video opamp', 'pins':[
            Pin(num='1',name='~',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='2A',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='2B',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='1B',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='~',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='~',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='9',name='1A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'THS4521ID', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'THS4521ID'}), 'ref_prefix':'U', 'fplist':['Package_SO:VSSOP-8_3x3mm_P0.65mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:VSSOP-8_3x3mm_P0.65mm', 'keywords':'differential amplifier', 'description':'', 'datasheet':'https://www.ti.com/lit/ds/symlink/ths4521.pdf', 'search_text':'/usr/share/kicad/symbols/Amplifier_Difference.kicad_sym\nTHS4521ID\n\ndifferential amplifier', 'pins':[
            Pin(num='1',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='V_{OCM}',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='V_{S+}',func=pin_types.PWRIN,unit=1),
            Pin(num='4',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='V_{S-}',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='~{PD}',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='+',func=pin_types.INPUT,unit=1)], 'unit_defs':[] })])