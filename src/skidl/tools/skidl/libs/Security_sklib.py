from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Security = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'ATAES132A-SH', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ATAES132A-SH'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'cryptographic security AES SPI', 'description':'', 'datasheet':'http://ww1.microchip.com/downloads/en/DeviceDoc/ATAES132A-Data-Sheet-40002023A.pdf', 'pins':[
            Pin(num='1',name='~{CS}',func=Pin.types.INPUT,unit=1),
            Pin(num='2',name='SO',func=Pin.types.OUTPUT,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='SI/SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='SCK',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='8',name='VCC',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ATECC608A-MAHDA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ATECC608A-MAHDA'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:DFN-8-1EP_3x2mm_P0.5mm_EP1.3x1.5mm'], 'footprint':'Package_DFN_QFN:DFN-8-1EP_3x2mm_P0.5mm_EP1.3x1.5mm', 'keywords':'Cryptographic coprocessor', 'description':'', 'datasheet':'http://ww1.microchip.com/downloads/en/DeviceDoc/ATECC608A-CryptoAuthentication-Device-Summary-Data-Sheet-DS40001977B.pdf', 'pins':[
            Pin(num='1',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='2',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='8',name='VCC',func=Pin.types.PWRIN,unit=1),
            Pin(num='9',name='EP',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ATECC608A-SSHDA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ATECC608A-SSHDA'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Cryptographic coprocessor', 'description':'', 'datasheet':'http://ww1.microchip.com/downloads/en/DeviceDoc/ATECC608A-CryptoAuthentication-Device-Summary-Data-Sheet-DS40001977B.pdf', 'pins':[
            Pin(num='1',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='2',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='8',name='VCC',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ATECC508A-MAHDA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ATECC508A-MAHDA'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:DFN-8-1EP_3x2mm_P0.5mm_EP1.3x1.5mm', 'Package_DFN_QFN:DFN-8-1EP_3x2mm_P0.5mm_EP1.3x1.5mm'], 'footprint':'Package_DFN_QFN:DFN-8-1EP_3x2mm_P0.5mm_EP1.3x1.5mm', 'keywords':'Cryptographic coprocessor', 'description':'', 'datasheet':'https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/20005928A.pdf', 'pins':[
            Pin(num='1',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='2',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='8',name='VCC',func=Pin.types.PWRIN,unit=1),
            Pin(num='9',name='EP',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ATECC508A-SSHDA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ATECC508A-SSHDA'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Cryptographic coprocessor', 'description':'', 'datasheet':'https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/20005928A.pdf', 'pins':[
            Pin(num='1',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='2',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='8',name='VCC',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ATECC608B-MAHDA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ATECC608B-MAHDA'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:DFN-8-1EP_3x2mm_P0.5mm_EP1.3x1.5mm', 'Package_DFN_QFN:DFN-8-1EP_3x2mm_P0.5mm_EP1.3x1.5mm', 'Package_DFN_QFN:DFN-8-1EP_3x2mm_P0.5mm_EP1.3x1.5mm'], 'footprint':'Package_DFN_QFN:DFN-8-1EP_3x2mm_P0.5mm_EP1.3x1.5mm', 'keywords':'Cryptographic coprocessor', 'description':'', 'datasheet':'https://ww1.microchip.com/downloads/aemDocuments/documents/SCBU/ProductDocuments/DataSheets/ATECC608B-CryptoAuthentication-Device-Summary-Data-Sheet-DS40002239B.pdf', 'pins':[
            Pin(num='1',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='2',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='8',name='VCC',func=Pin.types.PWRIN,unit=1),
            Pin(num='9',name='EP',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ATECC608B-SSHDA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ATECC608B-SSHDA'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'Cryptographic coprocessor', 'description':'', 'datasheet':'https://ww1.microchip.com/downloads/aemDocuments/documents/SCBU/ProductDocuments/DataSheets/ATECC608B-CryptoAuthentication-Device-Summary-Data-Sheet-DS40002239B.pdf', 'pins':[
            Pin(num='1',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='2',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='8',name='VCC',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] })])