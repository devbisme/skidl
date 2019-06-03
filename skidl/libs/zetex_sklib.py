from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

zetex = SchLib(tool=SKIDL).add_parts(*[
        Part(name='ZXGD3001E6',dest=TEMPLATE,tool=SKIDL,keywords='gate driver',description='8A (peak) Gate driver, 40V, 1ns delay',ref_prefix='U',num_units=1,fplist=['SOT?23-*'],do_erc=True,aliases=['ZXGD3004E6', 'ZXGD3002E6', 'ZXGD3003E6'],pins=[
            Pin(num='1',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='IN1',do_erc=True),
            Pin(num='3',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='SINK',func=Pin.OPENCOLL,do_erc=True),
            Pin(num='5',name='IN2',do_erc=True),
            Pin(num='6',name='SOURCE',func=Pin.OPENEMIT,do_erc=True)])])
