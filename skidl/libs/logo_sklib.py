from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

logo = SchLib(tool=SKIDL).add_parts(*[
        Part(name='OPEN_HARDWARE_1',dest=TEMPLATE,tool=SKIDL,keywords='Logo',description='Open Hardware Logo',ref_prefix='LOGO',num_units=1,do_erc=True),
        Part(name='OPEN_HARDWARE_2',dest=TEMPLATE,tool=SKIDL,keywords='Logo',description='Large Open hardware Logo',ref_prefix='LOGO',num_units=1,do_erc=True)])
