from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

onsemi = SchLib(tool=SKIDL).add_parts(*[
        Part(name='CM1213A-01SO',dest=TEMPLATE,tool=SKIDL,keywords='ESD Protection diodes transient suppressor',description='Single Channel ESD Protection Array',ref_prefix='D',num_units=1,fplist=['SOT-23*'],do_erc=True,pins=[
            Pin(num='1',name='CH1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='VP',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='VN',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='NCP45560',dest=TEMPLATE,tool=SKIDL,keywords='load switch',description='- Controlled Load Switch with Low Ron',ref_prefix='U',num_units=1,fplist=['TO263-5'],do_erc=True,aliases=['NCP45560H', 'NCP45560L'],pins=[
            Pin(num='1',name='VIN',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='EN',do_erc=True),
            Pin(num='3',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='GND',do_erc=True),
            Pin(num='5',name='SR',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='PG',func=Pin.OPENCOLL,do_erc=True),
            Pin(num='7',name='BLEED',do_erc=True),
            Pin(num='8',name='VOUT',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='VOUT',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='VOUT',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='VOUT',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='VOUT',func=Pin.PWROUT,do_erc=True),
            Pin(num='13',name='VIN',func=Pin.PWRIN,do_erc=True)]),
        Part(name='NUP2202',dest=TEMPLATE,tool=SKIDL,keywords='ESD Protection diodes transient suppressor',description='Transient voltage suppressor designed to protect high speed data lines from ESD, EFT, and lightning',ref_prefix='U',num_units=1,fplist=['*SC-70*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='4',name='~',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='5',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='NUP4202',dest=TEMPLATE,tool=SKIDL,keywords='ESD Protection diodes transient suppressor',description='Transient voltage suppressor designed to protect high speed data lines from ESD, EFT, and lightning',ref_prefix='U',num_units=1,fplist=['*SC-70*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='~',func=Pin.PASSIVE,do_erc=True)])])
