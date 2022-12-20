from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

supertex = SchLib(tool=SKIDL).add_parts(*[
        Part(name='CL220K4-G',dest=TEMPLATE,tool=SKIDL,keywords='Constant Current LED Driver IC',description='Temperature Compensated Constant Current LED IC, D-PAK',ref_prefix='U',num_units=1,fplist=['TO-252*', 'DPAK*'],do_erc=True,pins=[
            Pin(num='1',name='VA',do_erc=True),
            Pin(num='2',name='VB',do_erc=True)]),
        Part(name='CL220N5-G',dest=TEMPLATE,tool=SKIDL,keywords='Constant Current LED Driver IC',description='Temperature Compensated Constant Current LED IC, TO-220',ref_prefix='U',num_units=1,fplist=['TO-220*'],do_erc=True,pins=[
            Pin(num='1',name='VA',do_erc=True),
            Pin(num='2',name='VB',do_erc=True)]),
        Part(name='HV100K5-G',dest=TEMPLATE,tool=SKIDL,keywords='Hot-Swap Current Limiter',description='Hot-Swap Current Limiter Controller, SOT223',ref_prefix='U',num_units=1,fplist=['SOT-223*'],do_erc=True,aliases=['HV101K5-G'],pins=[
            Pin(num='1',name='VPP',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='VNN',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='GATE',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='HV9921N8-G',dest=TEMPLATE,tool=SKIDL,keywords='CC LED Driver High Voltage',description='3pin Constant Current 30mA LED Driver, SOT89',ref_prefix='U',num_units=1,fplist=['SOT*'],do_erc=True,aliases=['HV9922N8-G', 'HV9923N8-G'],pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='VDD',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='HV9925SG-G',dest=TEMPLATE,tool=SKIDL,keywords='Programmable Current LED Lamp Driver High Voltage',description='Programmable Current LED Lamp Driver, SO8 w/Heat Slug',ref_prefix='U',num_units=1,fplist=['SO*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='Rs',func=Pin.OUTPUT,do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='PWMD',do_erc=True),
            Pin(num='4',name='VDD',func=Pin.PWROUT,do_erc=True),
            Pin(num='6',name='D',do_erc=True),
            Pin(num='7',name='D',do_erc=True),
            Pin(num='8',name='D',do_erc=True)]),
        Part(name='HV9930LG-G',dest=TEMPLATE,tool=SKIDL,keywords='Buck-Boost LED Lamp Driver High Voltage',description='Boost-Buck LED Lamp Driver, SO8',ref_prefix='U',num_units=1,fplist=['SO*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='VIN',do_erc=True),
            Pin(num='2',name='CS1',do_erc=True),
            Pin(num='3',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='GATE',func=Pin.OUTPUT,do_erc=True),
            Pin(num='5',name='PWMD',func=Pin.OUTPUT,do_erc=True),
            Pin(num='6',name='VDD',func=Pin.PWROUT,do_erc=True),
            Pin(num='7',name='CS2',do_erc=True),
            Pin(num='8',name='REF',do_erc=True)]),
        Part(name='HV9931LG-G',dest=TEMPLATE,tool=SKIDL,keywords='Buck-Boost LED Lamp Driver High Voltage PFC',description='PFC Boost-Buck LED Lamp Driver, SO8',ref_prefix='U',num_units=1,fplist=['SO*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='VIN',do_erc=True),
            Pin(num='2',name='CS1',do_erc=True),
            Pin(num='3',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='GATE',func=Pin.OUTPUT,do_erc=True),
            Pin(num='5',name='PWMD',func=Pin.OUTPUT,do_erc=True),
            Pin(num='6',name='VDD',func=Pin.PWROUT,do_erc=True),
            Pin(num='7',name='CS2',do_erc=True),
            Pin(num='8',name='REF',do_erc=True)]),
        Part(name='HV9961LG-G',dest=TEMPLATE,tool=SKIDL,keywords='Buck LED Lamp Driver High Voltage Average CC',description='Buck LED Lamp Driver Average-Mode Constant Current, SO8',ref_prefix='U',num_units=1,fplist=['SO*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='VIN',do_erc=True),
            Pin(num='2',name='CS',do_erc=True),
            Pin(num='3',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='GATE',func=Pin.OUTPUT,do_erc=True),
            Pin(num='5',name='PWMD',func=Pin.OUTPUT,do_erc=True),
            Pin(num='6',name='VDD',func=Pin.PWROUT,do_erc=True),
            Pin(num='7',name='LD',do_erc=True),
            Pin(num='8',name='RT',do_erc=True)]),
        Part(name='HV9961NG-G',dest=TEMPLATE,tool=SKIDL,keywords='Buck LED Lamp Driver High Voltage Average CC',description='Buck LED Lamp Driver Average-Mode Constant Current, SO16',ref_prefix='U',num_units=1,fplist=['SO*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='VIN',do_erc=True),
            Pin(num='4',name='CS',do_erc=True),
            Pin(num='5',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='GATE',func=Pin.OUTPUT,do_erc=True),
            Pin(num='9',name='PWMD',func=Pin.OUTPUT,do_erc=True),
            Pin(num='12',name='VDD',func=Pin.PWROUT,do_erc=True),
            Pin(num='13',name='LD',do_erc=True),
            Pin(num='14',name='RT',do_erc=True)]),
        Part(name='HV9967BK7-G',dest=TEMPLATE,tool=SKIDL,keywords='Buck LED Lamp Driver Low Voltage Average CC',description='Buck LED Lamp Driver Average-Mode Constant Current, DFN8 (3x3mm)',ref_prefix='U',num_units=1,fplist=['DFN*'],do_erc=True,pins=[
            Pin(num='1',name='SW',func=Pin.OUTPUT,do_erc=True),
            Pin(num='2',name='Rs',do_erc=True),
            Pin(num='3',name='PGND',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='PWMD',func=Pin.OUTPUT,do_erc=True),
            Pin(num='6',name='RT',do_erc=True),
            Pin(num='7',name='AGND',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='VDD',func=Pin.PWROUT,do_erc=True)]),
        Part(name='HV9967BMG-G',dest=TEMPLATE,tool=SKIDL,keywords='Buck LED Lamp Driver Low Voltage Average CC',description='Buck LED Lamp Driver Average-Mode Constant Current, MSOP8',ref_prefix='U',num_units=1,fplist=['MSOP*'],do_erc=True,pins=[
            Pin(num='1',name='SW',func=Pin.OUTPUT,do_erc=True),
            Pin(num='2',name='Rs',do_erc=True),
            Pin(num='3',name='PGND',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='PWMD',func=Pin.OUTPUT,do_erc=True),
            Pin(num='6',name='RT',do_erc=True),
            Pin(num='7',name='AGND',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='VDD',func=Pin.PWROUT,do_erc=True)]),
        Part(name='HV9972LG-G',dest=TEMPLATE,tool=SKIDL,keywords='Isolated LED Lamp Driver High Voltage CC',description='Isolated LED Lamp Driver Constant Current, SO8',ref_prefix='U',num_units=1,fplist=['SOIC*', 'SO*'],do_erc=True,pins=[
            Pin(num='1',name='BIAS',do_erc=True),
            Pin(num='2',name='VIN',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='VD',do_erc=True),
            Pin(num='4',name='PWMD',func=Pin.OUTPUT,do_erc=True),
            Pin(num='5',name='CS',do_erc=True),
            Pin(num='6',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='7',name='GATE',func=Pin.OUTPUT,do_erc=True),
            Pin(num='8',name='VDD',func=Pin.PWROUT,do_erc=True)]),
        Part(name='LR8K4-G',dest=TEMPLATE,tool=SKIDL,keywords='High-Voltage Regulator Adjustable Positive',description='30mA 450V High-Voltage Linear Regulator (Adjustable), TO-252 (D-PAK)',ref_prefix='U',num_units=1,fplist=['TO-252*', 'DPAK*'],do_erc=True,pins=[
            Pin(num='1',name='IN',do_erc=True),
            Pin(num='2',name='OUT',func=Pin.PWROUT,do_erc=True),
            Pin(num='3',name='ADJ',do_erc=True)]),
        Part(name='LR8N3-G',dest=TEMPLATE,tool=SKIDL,keywords='High-Voltage Regulator Adjustable Positive',description='30mA 450V High-Voltage Linear Regulator (Adjustable), TO-92',ref_prefix='U',num_units=1,fplist=['TO-92*'],do_erc=True,pins=[
            Pin(num='1',name='IN',do_erc=True),
            Pin(num='2',name='OUT',func=Pin.PWROUT,do_erc=True),
            Pin(num='3',name='ADJ',do_erc=True)]),
        Part(name='LR8N8-G',dest=TEMPLATE,tool=SKIDL,keywords='High-Voltage Regulator Adjustable Positive',description='30mA 450V High-Voltage Linear Regulator (Adjustable), SOT-89',ref_prefix='U',num_units=1,fplist=['SOT*'],do_erc=True,pins=[
            Pin(num='1',name='IN',do_erc=True),
            Pin(num='2',name='OUT',func=Pin.PWROUT,do_erc=True),
            Pin(num='3',name='ADJ',do_erc=True)])])
