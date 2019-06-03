from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

power = SchLib(tool=SKIDL).add_parts(*[
        Part(name='+12C',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+12L',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+12LF',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+12P',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+12V',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+12VA',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+15V',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+1V0',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+1V1',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+1V2',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+1V35',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+1V5',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+1V8',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+24V',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+28V',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+2V5',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+2V8',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+3.3VA',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+3.3VADC',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+3.3VDAC',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+3.3VP',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+36V',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+3V3',dest=TEMPLATE,tool=SKIDL,do_erc=True,aliases=['+3.3V']),
        Part(name='+48V',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+5C',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+5F',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+5P',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+5V',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+5VA',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+5VD',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+5VL',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+5VP',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+6V',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+8V',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+9V',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+9VA',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='+BATT',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='-10V',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-10V',func=Pin.PWRIN,do_erc=True)]),
        Part(name='-12V',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-12V',func=Pin.PWRIN,do_erc=True)]),
        Part(name='-12VA',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-12VA',func=Pin.PWRIN,do_erc=True)]),
        Part(name='-15V',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-15V',func=Pin.PWRIN,do_erc=True)]),
        Part(name='-24V',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-24V',func=Pin.PWRIN,do_erc=True)]),
        Part(name='-36V',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-36V',func=Pin.PWRIN,do_erc=True)]),
        Part(name='-48V',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-48V',func=Pin.PWRIN,do_erc=True)]),
        Part(name='-5V',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-5V',func=Pin.PWRIN,do_erc=True)]),
        Part(name='-5VA',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-5VA',func=Pin.PWRIN,do_erc=True)]),
        Part(name='-6V',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-6V',func=Pin.PWRIN,do_erc=True)]),
        Part(name='-8V',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-8V',func=Pin.PWRIN,do_erc=True)]),
        Part(name='-9VA',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-9VA',func=Pin.PWRIN,do_erc=True)]),
        Part(name='AC',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='AC',func=Pin.PWRIN,do_erc=True)]),
        Part(name='~Earth',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='~Earth_Clean',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='~Earth_Protective',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='GND',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='GND',func=Pin.PWRIN,do_erc=True)]),
        Part(name='GNDA',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='GNDA',func=Pin.PWRIN,do_erc=True)]),
        Part(name='GNDD',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='GNDD',func=Pin.PWRIN,do_erc=True)]),
        Part(name='GNDPWR',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='GNDPWR',func=Pin.PWRIN,do_erc=True)]),
        Part(name='GNDREF',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='GNDREF',func=Pin.PWRIN,do_erc=True)]),
        Part(name='HT',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='PWR_FLAG',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='VAA',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='VAA',func=Pin.PWRIN,do_erc=True)]),
        Part(name='VCC',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='VCC',func=Pin.PWRIN,do_erc=True)]),
        Part(name='VCOM',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='VCOM',func=Pin.PWRIN,do_erc=True)]),
        Part(name='VDD',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='VDD',func=Pin.PWRIN,do_erc=True)]),
        Part(name='VDDA',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='VDDA',func=Pin.PWRIN,do_erc=True)]),
        Part(name='VEE',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='VEE',func=Pin.PWRIN,do_erc=True)]),
        Part(name='VMEM',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='VMEM',func=Pin.PWRIN,do_erc=True)]),
        Part(name='VPP',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='VPP',func=Pin.PWRIN,do_erc=True)]),
        Part(name='VSS',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='VSS',func=Pin.PWRIN,do_erc=True)]),
        Part(name='VSSA',dest=TEMPLATE,tool=SKIDL,keywords='POWER, PWR',ref_prefix='#PWR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='VSSA',func=Pin.PWRIN,do_erc=True)])])
