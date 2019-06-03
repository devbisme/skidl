from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

Worldsemi = SchLib(tool=SKIDL).add_parts(*[
        Part(name='WS2812B',dest=TEMPLATE,tool=SKIDL,keywords='RGB LED NeoPixel',description='RGB LED with integrated controller',ref_prefix='LED',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='DOUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='3',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='DIN',do_erc=True)]),
        Part(name='WS2812S',dest=TEMPLATE,tool=SKIDL,keywords='RGB LED',description='RGB LED with integrated controller',ref_prefix='LED',num_units=1,do_erc=True,aliases=['WS2812'],pins=[
            Pin(num='1',name='DOUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='2',name='DIN',do_erc=True),
            Pin(num='3',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='5',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='6',name='VSS',func=Pin.PWRIN,do_erc=True)]),
        Part(name='WS2822S_A',dest=TEMPLATE,tool=SKIDL,keywords='RGB LED',description='RGB LED with integrated controller',ref_prefix='LED',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='DIN',do_erc=True),
            Pin(num='2',name='ADRIN',do_erc=True),
            Pin(num='3',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='5',name='ADROUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='6',name='VDD',func=Pin.PWRIN,do_erc=True)]),
        Part(name='WS2822S_B',dest=TEMPLATE,tool=SKIDL,keywords='RGB LED',description='RGB LED with integrated controller',ref_prefix='LED',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='ADROUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='2',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='DIN',do_erc=True),
            Pin(num='5',name='ADRIN',do_erc=True),
            Pin(num='6',name='VCC',func=Pin.PWRIN,do_erc=True)])])
