from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

contrib = SchLib(tool=SKIDL).add_parts(*[
        Part(name='FX614',dest=TEMPLATE,tool=SKIDL,keywords='Bell Modem',description='Bell 202 Compatible Modem, DIP-16/SO-16',ref_prefix='U',num_units=1,fplist=['DIP*', 'PDIP*', 'SO*'],do_erc=True,pins=[
            Pin(num='1',name='XTALN',func=Pin.OUTPUT,do_erc=True),
            Pin(num='2',name='XTAL/CLK',do_erc=True),
            Pin(num='3',name='M0',do_erc=True),
            Pin(num='4',name='M1',do_erc=True),
            Pin(num='5',name='RXIN',do_erc=True),
            Pin(num='6',name='RXFB',func=Pin.OUTPUT,do_erc=True),
            Pin(num='7',name='TXOP',func=Pin.OUTPUT,do_erc=True),
            Pin(num='8',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='9',name='VBIAS',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='RXEQ',do_erc=True),
            Pin(num='11',name='TXD',do_erc=True),
            Pin(num='12',name='CLK',do_erc=True),
            Pin(num='13',name='RXD',func=Pin.OUTPUT,do_erc=True),
            Pin(num='14',name='DET',func=Pin.OUTPUT,do_erc=True),
            Pin(num='15',name='~RDYN~',func=Pin.OUTPUT,do_erc=True),
            Pin(num='16',name='VDD',func=Pin.PWRIN,do_erc=True)])])
