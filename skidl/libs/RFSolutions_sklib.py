from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

RFSolutions = SchLib(tool=SKIDL).add_parts(*[
        Part(name='ZETA-433-SO',dest=TEMPLATE,tool=SKIDL,keywords='RF TRANSCEIVER MODULE',description='FM ZETA TRANSCEIVER MODULE, OPTIMISED FOR 433MHZ',ref_prefix='U',num_units=1,do_erc=True,aliases=['ZETA-868-SO', 'ZETA-915-SO'],pins=[
            Pin(num='1',name='ANT',func=Pin.BIDIR,do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='SDN',do_erc=True),
            Pin(num='4',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='5',name='IRQ',func=Pin.OUTPUT,do_erc=True),
            Pin(num='6',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='7',name='GPIO1',func=Pin.BIDIR,do_erc=True),
            Pin(num='8',name='GPIO2',func=Pin.BIDIR,do_erc=True),
            Pin(num='9',name='SCLK',do_erc=True),
            Pin(num='10',name='SDI',do_erc=True),
            Pin(num='11',name='SDO',do_erc=True),
            Pin(num='12',name='SEL',do_erc=True)])])
