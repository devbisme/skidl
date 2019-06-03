from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

nordicsemi = SchLib(tool=SKIDL).add_parts(*[
        Part(name='NRF8001',dest=TEMPLATE,tool=SKIDL,keywords='BLE, bluetooth',description='BLE chip from Nordic Semiconductor',ref_prefix='U',num_units=1,fplist=['QFN32'],do_erc=True,pins=[
            Pin(num='1',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='DEC1',func=Pin.BIDIR,do_erc=True),
            Pin(num='3',name='DEC2',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='XL2',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='XL1',func=Pin.BIDIR,do_erc=True),
            Pin(num='6',name='ACTIVE',func=Pin.BIDIR,do_erc=True),
            Pin(num='7',name='TXD',func=Pin.OUTPUT,do_erc=True),
            Pin(num='8',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='9',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='10',name='RXD',do_erc=True),
            Pin(num='20',name='VDD_PA',func=Pin.OUTPUT,do_erc=True),
            Pin(num='30',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='11',name='SCK',do_erc=True),
            Pin(num='21',name='ANT1',func=Pin.BIDIR,do_erc=True),
            Pin(num='31',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='12',name='REQN',func=Pin.BIDIR,do_erc=True),
            Pin(num='22',name='ANT2',func=Pin.BIDIR,do_erc=True),
            Pin(num='32',name='DCC',func=Pin.BIDIR,do_erc=True),
            Pin(num='13',name='MOSI',do_erc=True),
            Pin(num='23',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='33',name='GND_PAD',func=Pin.PWRIN,do_erc=True),
            Pin(num='14',name='MISO',func=Pin.OUTPUT,do_erc=True),
            Pin(num='24',name='AVDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='15',name='N/C',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='25',name='IREF',do_erc=True),
            Pin(num='16',name='RDYN',func=Pin.BIDIR,do_erc=True),
            Pin(num='26',name='AVDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='17',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='27',name='XC2',func=Pin.BIDIR,do_erc=True),
            Pin(num='18',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='28',name='XC1',func=Pin.BIDIR,do_erc=True),
            Pin(num='19',name='RESET',do_erc=True),
            Pin(num='29',name='AVDD',func=Pin.PWRIN,do_erc=True)])])
