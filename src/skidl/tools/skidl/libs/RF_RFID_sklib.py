from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

RF_RFID = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'HTRC11001T', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'HTRC11001T'}), 'ref_prefix':'U', 'fplist':['Package_SO:SOIC-14_3.9x8.7mm_P1.27mm'], 'footprint':'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm', 'keywords':'HITAG RFID', 'description':'', 'datasheet':'https://www.nxp.com/docs/en/data-sheet/037031.pdf', 'search_text':'/usr/share/kicad/symbols/RF_RFID.kicad_sym\nHTRC11001T\n\nHITAG RFID', 'pins':[
            Pin(num='1',name='VSS',func=pin_types.PWRIN,unit=1),
            Pin(num='10',name='DOUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='12',name='CEXT',func=pin_types.PASSIVE,unit=1),
            Pin(num='13',name='QGND',func=pin_types.PASSIVE,unit=1),
            Pin(num='14',name='RX',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='TX2',func=pin_types.OUTPUT,unit=1),
            Pin(num='3',name='VDD',func=pin_types.PWRIN,unit=1),
            Pin(num='4',name='TX1',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='MODE',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='XTAL1',func=pin_types.INPUT,unit=1),
            Pin(num='7',name='XTAL2',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='SCLK',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='DIN',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PN5120A0HN1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PN5120A0HN1'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:HVQFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm'], 'footprint':'Package_DFN_QFN:HVQFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm', 'keywords':'PN512 RFID', 'description':'', 'datasheet':'https://www.nxp.com/docs/en/data-sheet/PN512.pdf', 'search_text':'/usr/share/kicad/symbols/RF_RFID.kicad_sym\nPN5120A0HN1\n\nPN512 RFID', 'pins':[
            Pin(num='1',name='A1',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='TVSS',func=pin_types.PWRIN,unit=1),
            Pin(num='11',name='TX1',func=pin_types.OUTPUT,unit=1),
            Pin(num='12',name='TVDD',func=pin_types.PWRIN,unit=1),
            Pin(num='13',name='TX2',func=pin_types.OUTPUT,unit=1),
            Pin(num='14',name='TVSS',func=pin_types.PASSIVE,unit=1),
            Pin(num='15',name='AVDD',func=pin_types.PWRIN,unit=1),
            Pin(num='16',name='VMID',func=pin_types.PWROUT,unit=1),
            Pin(num='17',name='RX',func=pin_types.INPUT,unit=1),
            Pin(num='18',name='AVSS',func=pin_types.PWRIN,unit=1),
            Pin(num='19',name='AUX1',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='PVDD',func=pin_types.PWRIN,unit=1),
            Pin(num='20',name='AUX2',func=pin_types.OUTPUT,unit=1),
            Pin(num='21',name='OSCIN',func=pin_types.INPUT,unit=1),
            Pin(num='22',name='OSCOUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='23',name='IRQ',func=pin_types.OUTPUT,unit=1),
            Pin(num='24',name='ALE',func=pin_types.INPUT,unit=1),
            Pin(num='25',name='D1',func=pin_types.BIDIR,unit=1),
            Pin(num='26',name='D2',func=pin_types.BIDIR,unit=1),
            Pin(num='27',name='D3',func=pin_types.BIDIR,unit=1),
            Pin(num='28',name='D4',func=pin_types.BIDIR,unit=1),
            Pin(num='29',name='D5',func=pin_types.BIDIR,unit=1),
            Pin(num='3',name='DVDD',func=pin_types.PWRIN,unit=1),
            Pin(num='30',name='D6',func=pin_types.BIDIR,unit=1),
            Pin(num='31',name='D7',func=pin_types.BIDIR,unit=1),
            Pin(num='32',name='A0',func=pin_types.INPUT,unit=1),
            Pin(num='33',name='EP',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='DVSS',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='PVSS',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='~{NRSTPD}',func=pin_types.INPUT,unit=1),
            Pin(num='7',name='SIGIN',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='SIGOUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='9',name='SVDD',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] })])