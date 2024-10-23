from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

MCU_NXP_NTAG = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'NHS3100', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'NHS3100'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:HVQFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm'], 'footprint':'Package_DFN_QFN:HVQFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm', 'keywords':'NFC Cortex-M0', 'description':'', 'datasheet':'https://www.nxp.com/docs/en/data-sheet/NHS3100.pdf', 'search_text':'/usr/share/kicad/symbols/MCU_NXP_NTAG.kicad_sym\nNHS3100\n\nNFC Cortex-M0', 'pins':[
            Pin(num='1',name='P0/WAKEUP',func=Pin.types.BIDIR,unit=1),
            Pin(num='10',name='reserved',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='11',name='P4/SCL',func=Pin.types.BIDIR,unit=1),
            Pin(num='12',name='P5/SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='13',name='P7/CT16B_M1',func=Pin.types.BIDIR,unit=1),
            Pin(num='14',name='P3/CT16B_M0',func=Pin.types.BIDIR,unit=1),
            Pin(num='15',name='P10/SWCLK',func=Pin.types.BIDIR,unit=1),
            Pin(num='16',name='P11/SWDIO',func=Pin.types.BIDIR,unit=1),
            Pin(num='17',name='VSS',func=Pin.types.PASSIVE,unit=1),
            Pin(num='18',name='VSS',func=Pin.types.PASSIVE,unit=1),
            Pin(num='19',name='LB',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='P1/CLKOUT',func=Pin.types.BIDIR,unit=1),
            Pin(num='20',name='LA',func=Pin.types.PASSIVE,unit=1),
            Pin(num='21',name='VSS',func=Pin.types.PASSIVE,unit=1),
            Pin(num='22',name='VSS',func=Pin.types.PASSIVE,unit=1),
            Pin(num='23',name='VSS',func=Pin.types.PASSIVE,unit=1),
            Pin(num='24',name='VSS',func=Pin.types.PASSIVE,unit=1),
            Pin(num='25',name='VSS',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='P2/SSEL',func=Pin.types.BIDIR,unit=1),
            Pin(num='4',name='P6/SCLK',func=Pin.types.BIDIR,unit=1),
            Pin(num='5',name='P8/MISO',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='P9/MOSI',func=Pin.types.BIDIR,unit=1),
            Pin(num='7',name='VDDBAT',func=Pin.types.PWRIN,unit=1),
            Pin(num='8',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='9',name='~{RESET}',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] })])