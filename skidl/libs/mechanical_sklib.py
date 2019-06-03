from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

mechanical = SchLib(tool=SKIDL).add_parts(*[
        Part(name='Heatsink',dest=TEMPLATE,tool=SKIDL,keywords='thermal heat temperature',description='Heatsink',ref_prefix='HS',num_units=1,do_erc=True),
        Part(name='Heatsink_PAD',dest=TEMPLATE,tool=SKIDL,keywords='thermal heat temperature',description='Heatsink with electrical connection',ref_prefix='HS',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Housing',dest=TEMPLATE,tool=SKIDL,keywords='housing',description='Housing',ref_prefix='MK',num_units=1,do_erc=True),
        Part(name='Housing_PAD',dest=TEMPLATE,tool=SKIDL,keywords='housing',description='Housing with connection pin',ref_prefix='MK',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='PAD',do_erc=True)]),
        Part(name='Mounting_Hole',dest=TEMPLATE,tool=SKIDL,keywords='mounting hole',description='Mounting Hole without connection',ref_prefix='MK',num_units=1,fplist=['Mounting?Hole*', 'Hole*'],do_erc=True),
        Part(name='Mounting_Hole_PAD',dest=TEMPLATE,tool=SKIDL,keywords='mounting hole',description='Mounting Hole with connection',ref_prefix='MK',num_units=1,fplist=['Mounting?Hole*', 'Hole*'],do_erc=True,pins=[
            Pin(num='1',name='1',do_erc=True)])])
