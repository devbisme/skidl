from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

triac_thyristor = SchLib(tool=SKIDL).add_parts(*[
        Part(name='BT169B',dest=TEMPLATE,tool=SKIDL,keywords='thyristor logic level',description='0.5A Ion, 600V Voff, Thyristors logic level, Silicon Controlled Rectifier (Thyristor), TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*Inline*Narrow*'],do_erc=True,aliases=['BT169D', 'BT169G'],pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='TIC106',dest=TEMPLATE,tool=SKIDL,keywords='thyristor',description='12A Ion, 400-800V Voff, Silicon Controlled Rectifier (Thyristor), TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['TIC116', 'TIC126'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='TIC226',dest=TEMPLATE,tool=SKIDL,keywords='Triac',description='8A RMS, 400-800V Off-State Voltage, Triac, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['TIC206', 'BT138-600', 'BT138-800', 'TIC216', 'BT136-500', 'BT136-600', 'BT136-800', 'BT139-600'],pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Z0103MN',dest=TEMPLATE,tool=SKIDL,keywords='4Q Triac',description='4Q Triac, 1A RMS, 800V VDRM, 25mA Igt, 25mA Ih, SOT-223',ref_prefix='D',num_units=1,fplist=['SOT*223*'],do_erc=True,aliases=['Z0103NN', 'Z0107MN', 'Z0107NN', 'Z0109MN', 'Z0109NN', 'Z0110MN', 'Z0110NN'],pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True),
            Pin(num='4',name='A4',func=Pin.PASSIVE,do_erc=True)])])
