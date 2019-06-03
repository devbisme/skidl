from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

allegro = SchLib(tool=SKIDL).add_parts(*[
        Part(name='ACS706ELC-05C',dest=TEMPLATE,tool=SKIDL,keywords='hall effect current monitor sensor isolated obsolete',description='15A, Hall Effect Linear Current Sensor, SO-8, OBSOLETE',ref_prefix='U',num_units=1,fplist=['SOIC*3.9x4.9mm*Pitch1.27mm*'],do_erc=True,pins=[
            Pin(num='1',name='IP+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='IP+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='IP-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='IP-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='6',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='7',name='VIout',func=Pin.OUTPUT,do_erc=True),
            Pin(num='8',name='VCC',func=Pin.PWRIN,do_erc=True)]),
        Part(name='ACS711xLCTR-12AB',dest=TEMPLATE,tool=SKIDL,keywords='hall effect current monitor sensor isolated',description='±25A, Bidirectional, hall-effect current sensor, +3.3V supply, 55mV/A, SO-8',ref_prefix='U',num_units=1,fplist=['SOIC*3.9x4.9mm*Pitch1.27mm*'],do_erc=True,aliases=['ACS711xLCTR-25AB'],pins=[
            Pin(num='1',name='IP+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='IP+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='IP-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='IP-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='6',name='~FAULT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='7',name='VIout',func=Pin.OUTPUT,do_erc=True),
            Pin(num='8',name='VCC',func=Pin.PWRIN,do_erc=True)]),
        Part(name='ACS712ELCTR-05B-T',dest=TEMPLATE,tool=SKIDL,keywords='hall effect current monitor sensor isolated',description='30A Unidirectional hall-effect current sensor, +5.0V supply, 133mV/A, SO-8',ref_prefix='U',num_units=1,fplist=['SOIC*3.9x4.9m*Pitch1.27mm*'],do_erc=True,aliases=['ACS712ELCTR-20A-T', 'ACS712ELCTR-30A-T', 'ACS713ELCTR-20A-T', 'ACS713ELCTR-30A-T'],pins=[
            Pin(num='1',name='IP+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='IP+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='IP-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='IP-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='6',name='Filter',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='VIout',func=Pin.OUTPUT,do_erc=True),
            Pin(num='8',name='VCC',func=Pin.PWRIN,do_erc=True)]),
        Part(name='ACS722LLCTR-05AB-T',dest=TEMPLATE,tool=SKIDL,keywords='hall effect current monitor sensor isolated',description='40A Unidirectional hall-effect current sensor, +3.3V supply, 66mV/A, SO-8',ref_prefix='U',num_units=1,fplist=['SOIC*3.9x4.9mm*Pitch1.27mm*'],do_erc=True,aliases=['ACS722LLCTR-10AU-T', 'ACS722LLCTR-10AB-T', 'ACS722LLCTR-20AU-T', 'ACS722LLCTR-20AB-T', 'ACS722LLCTR-40AU-T', 'ACS722LLCTR-40AB-T'],pins=[
            Pin(num='1',name='IP+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='IP+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='IP-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='IP-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='6',name='BWSel',do_erc=True),
            Pin(num='7',name='VIout',func=Pin.OUTPUT,do_erc=True),
            Pin(num='8',name='VCC',func=Pin.PWRIN,do_erc=True)]),
        Part(name='ACS756SCB-050B',dest=TEMPLATE,tool=SKIDL,keywords='hall effect current monitor sensor isolated',description='±100A Bidirectional hall-effect current sensor, +3.3V supply, 13.2mV/A, CB-5 leadform',ref_prefix='U',num_units=1,do_erc=True,aliases=['ACS756SCB-100B', 'ACS758LCB-050B', 'ACS758LCB-050U', 'ACS758LCB-100B', 'ACS758LCB-100U', 'ACS758KCB-150B', 'ACS758KCB-150U', 'ACS758ECB-200B', 'ACS758ECB-200U', 'ACS759LCB-050B', 'ACS759LCB-100B', 'ACS759KCB-150B', 'ACS759ECB-200B'],pins=[
            Pin(num='1',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='IP+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='IP-',func=Pin.PASSIVE,do_erc=True)])])
