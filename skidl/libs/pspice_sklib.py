from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

pspice = SchLib(tool=SKIDL).add_parts(*[
        Part(name='0',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='CAP',dest=TEMPLATE,tool=SKIDL,do_erc=True,aliases=['C']),
        Part(name='DIODE',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='INDUCTOR',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='ISOURCE',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='QNPN',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='QPNP',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='R',dest=TEMPLATE,tool=SKIDL,keywords='R DEV',description='Resistance',ref_prefix='R',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='VSOURCE',dest=TEMPLATE,tool=SKIDL,do_erc=True)])
