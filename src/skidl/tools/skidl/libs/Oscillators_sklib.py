from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

Oscillators = SchLib(tool=SKIDL).add_parts(*[
        Part(name='ACO-xxxMHz-A',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='HCMOS Crystal Clock Oscillator, DIP14-style metal package',ref_prefix='X',num_units=1,fplist=['Oscillator*DIP*14*'],do_erc=True,pins=[
            Pin(num='1',name='Tri-State',func=Pin.TRISTATE,do_erc=True),
            Pin(num='7',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='14',name='Vcc',func=Pin.PWRIN,do_erc=True)]),
        Part(name='ASE-xxxMHz',dest=TEMPLATE,tool=SKIDL,keywords='3.3V CMOS SMD Crystal Clock Oscillator',description='3.3V CMOS SMD Crystal Clock Oscillator, Abracon',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*Abracon*ASE*3.2x2.5mm*'],do_erc=True,pins=[
            Pin(num='1',name='EN',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='Vdd',func=Pin.PWRIN,do_erc=True)]),
        Part(name='ASV-xxxMHz',dest=TEMPLATE,tool=SKIDL,keywords='3.3V HCMOS SMD Crystal Clock Oscillator',description='3.3V HCMOS SMD Crystal Clock Oscillator, Abracon',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*Abracon*ASV*7.0x5.1mm*'],do_erc=True,pins=[
            Pin(num='1',name='EN',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='Vdd',func=Pin.PWRIN,do_erc=True)]),
        Part(name='CXO_DIP14',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='Crystal Clock Oscillator, DIP14-style metal package',ref_prefix='X',num_units=1,fplist=['Oscillator*DIP*14*'],do_erc=True,aliases=['TFT680', 'GTXO-14T'],pins=[
            Pin(num='1',name='EN',do_erc=True),
            Pin(num='7',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='14',name='Vcc',func=Pin.PWRIN,do_erc=True)]),
        Part(name='CXO_DIP8',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='Crystal Clock Oscillator, DIP8-style metal package',ref_prefix='X',num_units=1,fplist=['Oscillator*DIP*8*'],do_erc=True,aliases=['TFT660'],pins=[
            Pin(num='1',name='EN',do_erc=True),
            Pin(num='4',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='5',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='8',name='Vcc',func=Pin.PWRIN,do_erc=True)]),
        Part(name='DFA-S11',dest=TEMPLATE,tool=SKIDL,keywords='Temperature compensated Crystal Clock Oscillator',description='Temperature compensated Crystal Clock Oscillator',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*Fordahl*DFAS11*7.0x5.0mm*'],do_erc=True,pins=[
            Pin(num='1',name='Vctrl',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)]),
        Part(name='DFA-S15',dest=TEMPLATE,tool=SKIDL,keywords='Temperature compensated Crystal Clock Oscillator',description='Temperature compensated Crystal Clock Oscillator',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*Fordahl*DFAS15*5.0x3.2mm*'],do_erc=True,pins=[
            Pin(num='1',name='Vctrl',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)]),
        Part(name='DFA-S2',dest=TEMPLATE,tool=SKIDL,keywords='Temperature compensated Crystal Clock Oscillator',description='Temperature compensated Crystal Clock Oscillator',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*Fordahl*DFAS2*7.3x5.1mm*'],do_erc=True,pins=[
            Pin(num='1',name='Vctrl',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)]),
        Part(name='DFA-S3',dest=TEMPLATE,tool=SKIDL,keywords='Temperature compensated Crystal Clock Oscillator',description='Temperature compensated Crystal Clock Oscillator',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*Fordahl*DFAS3*9.1x7.2mm*'],do_erc=True,pins=[
            Pin(num='1',name='Vctrl',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)]),
        Part(name='DGOF5S3',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='Temperature Compensated Crystal Clock Oscillator, DIP14-style metal package',ref_prefix='X',num_units=1,fplist=['Oscillator*DIP*14*'],do_erc=True,aliases=['ACO-xxxMHz', 'GTXO-S14T', 'TCXO-14'],pins=[
            Pin(num='1',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='7',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='14',name='Vcc',func=Pin.PWRIN,do_erc=True)]),
        Part(name='IQXO-70',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='Crystal Clock Oscillator, SMD package 7.5x5.0mm²',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*IQD*IQXO70*7.5x5.0mm*'],do_erc=True,pins=[
            Pin(num='1',name='E/B',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)]),
        Part(name='OCXO-14',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='Voltage-Controlled Crystal Clock Oscillator, DIP14-style metal package',ref_prefix='X',num_units=1,fplist=['Oscillator*DIP*14*'],do_erc=True,aliases=['GTXO-14V', 'GTXO-S14V', 'VTCXO-14'],pins=[
            Pin(num='1',name='Vcontrol',do_erc=True),
            Pin(num='7',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='14',name='Vcc',func=Pin.PWRIN,do_erc=True)]),
        Part(name='SG-210SED',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='Crystal Oscillator Low Profile / High Stability SPXO',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*SeikoEpson*SG210*2.5x2.0mm*'],do_erc=True,aliases=['SG-210SDD', 'SG-210SCD'],pins=[
            Pin(num='1',name='OE',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='Vcc',func=Pin.PWRIN,do_erc=True)]),
        Part(name='SG-210STF',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='CMOS Crystal Oscillator SPXO',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*SeikoEpson*SG210*2.5x2.0mm*'],do_erc=True,aliases=['SG-211'],pins=[
            Pin(num='1',name='~ST~',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='Vcc',func=Pin.PWRIN,do_erc=True)]),
        Part(name='SG-8002CA',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='CMOS Clock Oscillator',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*SeikoEpson*SG8002CA*7.0x5.0mm*'],do_erc=True,pins=[
            Pin(num='1',name='OE',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)]),
        Part(name='SG-8002CE',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='CMOS Clock Oscillator',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*SeikoEpson*SG8002CE*3.2x2.5mm*'],do_erc=True,pins=[
            Pin(num='1',name='OE',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)]),
        Part(name='SG-8002DB',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='Crystal Clock Oscillator, DIP14-style plastic package',ref_prefix='X',num_units=1,fplist=['Oscillator*SeikoEpson*SG?8002DB*'],do_erc=True,aliases=['SG-51'],pins=[
            Pin(num='1',name='OE',do_erc=True),
            Pin(num='7',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='14',name='Vcc',func=Pin.PWRIN,do_erc=True)]),
        Part(name='SG-8002DC',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='Crystal Clock Oscillator, DIP8-style plastic package',ref_prefix='X',num_units=1,fplist=['Oscillator*SeikoEpson*SG?8002DC*'],do_erc=True,aliases=['SG-531'],pins=[
            Pin(num='1',name='OE',do_erc=True),
            Pin(num='4',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='5',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='8',name='Vcc',func=Pin.PWRIN,do_erc=True)]),
        Part(name='SG-8002JA',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='CMOS Clock Oscillator',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*SeikoEpson*SG8002JA*14.0x8.7mm*'],do_erc=True,aliases=['SG-615'],pins=[
            Pin(num='1',name='OE',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)]),
        Part(name='SG-8002JC',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='CMOS Clock Oscillator',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*SeikoEpson*SG8002JC*10.5x5.0mm*'],do_erc=True,pins=[
            Pin(num='1',name='OE',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)]),
        Part(name='SG-8002LB',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='CMOS Clock Oscillator',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*SeikoEpson*SG8002LB*5.0x3.2mm*'],do_erc=True,pins=[
            Pin(num='1',name='OE',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)]),
        Part(name='Si570',dest=TEMPLATE,tool=SKIDL,keywords='10 MHZ TO 1.4 GHZ I2C PROGRAMMABLE XO/VCXO',description='10 MHZ TO 1.4 GHZ I2C PROGRAMMABLE XO/VCXO',ref_prefix='U',num_units=1,fplist=['Oscillator*SI570*SI571*'],do_erc=True,pins=[
            Pin(num='1',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='2',name='OE',do_erc=True),
            Pin(num='3',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='CLK+',func=Pin.OUTPUT,do_erc=True),
            Pin(num='5',name='CLK-',func=Pin.OUTPUT,do_erc=True),
            Pin(num='6',name='Vcc',func=Pin.PWRIN,do_erc=True),
            Pin(num='7',name='SDA',func=Pin.BIDIR,do_erc=True),
            Pin(num='8',name='SCL',func=Pin.BIDIR,do_erc=True)]),
        Part(name='Si571',dest=TEMPLATE,tool=SKIDL,keywords='10 MHZ TO 1.4 GHZ I2C PROGRAMMABLE XO/VCXO',description='10 MHZ TO 1.4 GHZ I2C PROGRAMMABLE XO/VCXO',ref_prefix='U',num_units=1,fplist=['Oscillator*SI570*SI571*'],do_erc=True,pins=[
            Pin(num='1',name='Vc',do_erc=True),
            Pin(num='2',name='OE',do_erc=True),
            Pin(num='3',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='CLK+',func=Pin.OUTPUT,do_erc=True),
            Pin(num='5',name='CLK-',func=Pin.OUTPUT,do_erc=True),
            Pin(num='6',name='Vcc',func=Pin.PWRIN,do_erc=True),
            Pin(num='7',name='SDA',func=Pin.BIDIR,do_erc=True),
            Pin(num='8',name='SCL',func=Pin.BIDIR,do_erc=True)]),
        Part(name='TCXO3',dest=TEMPLATE,tool=SKIDL,keywords='Temperature compensated crystal oscillator',description='Temperature compensated crystal oscillator',ref_prefix='X',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='FREQ',func=Pin.OUTPUT,do_erc=True),
            Pin(num='2',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='3',name='URef',func=Pin.PWROUT,do_erc=True),
            Pin(num='4',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='5',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='6',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='7',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='8',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='9',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='10',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='20',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='11',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='21',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='12',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='22',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='13',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='23',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='14',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='15',name='+5V',func=Pin.PWRIN,do_erc=True),
            Pin(num='16',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='17',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='18',name='Vctrl',do_erc=True),
            Pin(num='19',name='NC',func=Pin.NOCONNECT,do_erc=True)]),
        Part(name='TXC-7C',dest=TEMPLATE,tool=SKIDL,keywords='CMOS SMD Crystal Clock Oscillator',description='CMOS SMD Crystal Clock Oscillator, TXC',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*TXC*7C*5.0x3.2mm*'],do_erc=True,pins=[
            Pin(num='1',name='EN',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='Vdd',func=Pin.PWRIN,do_erc=True)]),
        Part(name='VC-81',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='Voltage-Controlled Crystal Clock Oscillator, DIP8-style metal package',ref_prefix='X',num_units=1,fplist=['Oscillator*DIP*8*'],do_erc=True,aliases=['VC-83'],pins=[
            Pin(num='1',name='Vcontrol',do_erc=True),
            Pin(num='4',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='5',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='8',name='Vcc',func=Pin.PWRIN,do_erc=True)]),
        Part(name='XO32',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='HCMOS Clock Oscillator',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*EuroQuartz*XO32*3.2x2.5mm*'],do_erc=True,pins=[
            Pin(num='1',name='EN',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)]),
        Part(name='XO53',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='Low Power Consumption Clock Oscillator',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*EuroQuartz*XO53*5.0x3.2mm*'],do_erc=True,pins=[
            Pin(num='1',name='EN',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)]),
        Part(name='XO91',dest=TEMPLATE,tool=SKIDL,keywords='Crystal Clock Oscillator',description='HCMOS Clock Oscillator',ref_prefix='X',num_units=1,fplist=['Oscillator*SMD*EuroQuartz*XO91*7.0x5.0mm*'],do_erc=True,pins=[
            Pin(num='1',name='EN',do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='V+',func=Pin.PWRIN,do_erc=True)])])
