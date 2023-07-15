from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

siliconi = SchLib(tool=SKIDL).add_parts(*[
        Part(name='D469',dest=TEMPLATE,tool=SKIDL,keywords='High-Current Driver',description='Quad High-Current Power Driver',ref_prefix='U',num_units=4,do_erc=True,pins=[
            Pin(num='7',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='14',name='V+',func=Pin.PWRIN,do_erc=True),
            Pin(num='1',name='IN1',do_erc=True),
            Pin(num='2',name='IN',do_erc=True),
            Pin(num='13',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='3',name='IN1',do_erc=True),
            Pin(num='4',name='IN',do_erc=True),
            Pin(num='12',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='5',name='IN1',do_erc=True),
            Pin(num='6',name='IN',do_erc=True),
            Pin(num='11',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='8',name='IN1',do_erc=True),
            Pin(num='9',name='IN',do_erc=True),
            Pin(num='10',name='OUT',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='DG411',dest=TEMPLATE,tool=SKIDL,keywords='CMOS Analog Switche',description='Monolithic Quad SPST, CMOS Analog Switches',ref_prefix='U',num_units=4,do_erc=True,pins=[
            Pin(num='4',name='V-',func=Pin.PWRIN,do_erc=True),
            Pin(num='5',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='12',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='13',name='V+',func=Pin.PWRIN,do_erc=True),
            Pin(num='1',name='SW',do_erc=True),
            Pin(num='2',name='IN',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='OUT',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='IN',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='SW',do_erc=True),
            Pin(num='9',name='SW',do_erc=True),
            Pin(num='10',name='IN',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='OUT',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='OUT',func=Pin.PASSIVE,do_erc=True),
            Pin(num='15',name='IN',func=Pin.PASSIVE,do_erc=True),
            Pin(num='16',name='SW',do_erc=True)])])
