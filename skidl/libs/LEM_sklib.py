from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

LEM = SchLib(tool=SKIDL).add_parts(*[
        Part(name='LEM_HO-NP',dest=TEMPLATE,tool=SKIDL,keywords='current transducer',description='LEM current transducer HO 8-NP-xxxx, 5V supply voltage, Nominal measurement current (Ipn) 8A, Standard option xxxx = 0000: 2.5V reference, 3.5us response time, EEPROM Control=yes, over current detection = 2,9*Ipn',ref_prefix='MT',num_units=1,do_erc=True,aliases=['LEM_HO_8-NP', 'LEM_HO_15-NP', 'LEM_HO_25-NP'],pins=[
            Pin(num='1',name='5V',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='Vout',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='Vref',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='Over_Current',func=Pin.OPENCOLL,do_erc=True),
            Pin(num='6',name='Standby',do_erc=True),
            Pin(num='7',name='N/A(GND)',do_erc=True),
            Pin(num='8',name='L1_1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='L2_1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='L3_1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='L3_2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='L2_2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='L1_2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LEM_HO-NP_SP33',dest=TEMPLATE,tool=SKIDL,keywords='current transducer',description='LEM current transducer HO 8-NP/SP33-xxxx, 3.3V supply voltage, Nominal measurement current (Ipn) 8A, Standard option xxxx = 1000: 1.65V reference, 3.5us response time, EEPROM Control=yes, over current detection = 2,9*Ipn',ref_prefix='MT',num_units=1,do_erc=True,aliases=['LEM_HO_8-NP_SP33', 'LEM_HO_15-NP_SP33', 'LEM_HO_25-NP_SP33'],pins=[
            Pin(num='1',name='3V3',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='Vout',func=Pin.OUTPUT,do_erc=True),
            Pin(num='4',name='Vref',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='Over_Current',func=Pin.OPENCOLL,do_erc=True),
            Pin(num='6',name='Standby',do_erc=True),
            Pin(num='7',name='N/A(GND)',do_erc=True),
            Pin(num='8',name='L1_1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='L2_1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='L3_1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='L3_2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='L2_2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='L1_2',func=Pin.PASSIVE,do_erc=True)])])
