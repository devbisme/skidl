from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

device = SchLib(tool=SKIDL).add_parts(*[
        Part(name='Amperemeter_AC',dest=TEMPLATE,tool=SKIDL,keywords='Amperemeter AC',description='AC Amperemeter',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Amperemeter_DC',dest=TEMPLATE,tool=SKIDL,keywords='Amperemeter DC',description='DC Amperemeter',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Antenna',dest=TEMPLATE,tool=SKIDL,keywords='antenna',description='Antenna symbol',ref_prefix='AE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',do_erc=True)]),
        Part(name='Antenna_Dipole',dest=TEMPLATE,tool=SKIDL,keywords='dipole antenna',description='Dipole Antenna symbol',ref_prefix='AE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',do_erc=True),
            Pin(num='2',name='~',do_erc=True)]),
        Part(name='Antenna_Loop',dest=TEMPLATE,tool=SKIDL,keywords='loop antenna',description='Loop Antenna symbol',ref_prefix='AE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',do_erc=True),
            Pin(num='2',name='~',do_erc=True)]),
        Part(name='Antenna_Shield',dest=TEMPLATE,tool=SKIDL,keywords='antenna',description='Antenna symbol with extra pin for shielding',ref_prefix='AE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',do_erc=True),
            Pin(num='2',name='Shield',do_erc=True)]),
        Part(name='Battery',dest=TEMPLATE,tool=SKIDL,keywords='batt voltage-source cell',description='Battery (multiple cells)',ref_prefix='BT',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Battery_Cell',dest=TEMPLATE,tool=SKIDL,keywords='battery cell',description='single battery cell',ref_prefix='BT',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Buzzer',dest=TEMPLATE,tool=SKIDL,keywords='Quartz Resonator Ceramic',description='Buzzer, polar',ref_prefix='BZ',num_units=1,fplist=['*Buzzer*'],do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='C',dest=TEMPLATE,tool=SKIDL,keywords='cap capacitor',description='Unpolarized capacitor',ref_prefix='C',num_units=1,fplist=['C_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CP',dest=TEMPLATE,tool=SKIDL,keywords='cap capacitor',description='Polarised capacitor',ref_prefix='C',num_units=1,fplist=['CP_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CP1',dest=TEMPLATE,tool=SKIDL,keywords='cap capacitor',description='Polarised capacitor',ref_prefix='C',num_units=1,fplist=['CP_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CP1_Small',dest=TEMPLATE,tool=SKIDL,keywords='cap capacitor',description='Polarised capacitor',ref_prefix='C',num_units=1,fplist=['CP_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CP_Small',dest=TEMPLATE,tool=SKIDL,keywords='cap capacitor',description='Polarised capacitor',ref_prefix='C',num_units=1,fplist=['CP_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CTRIM',dest=TEMPLATE,tool=SKIDL,keywords='trimmer variable capacitor',description='Trimmable capacitor',ref_prefix='C',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CTRIM_DIF',dest=TEMPLATE,tool=SKIDL,keywords='trimmer capacitor',description='Differential variable capacitor with two stators',ref_prefix='C',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='C_Feedthrough',dest=TEMPLATE,tool=SKIDL,keywords='EMI filter feedthrough capacitor',description='EMI filter, single capacitor',ref_prefix='C',num_units=1,do_erc=True,aliases=['EMI_Filter_C'],pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='C_Small',dest=TEMPLATE,tool=SKIDL,keywords='capacitor cap',description='Unpolarized capacitor',ref_prefix='C',num_units=1,fplist=['C_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='C_Variable',dest=TEMPLATE,tool=SKIDL,keywords='trimmer capacitor',description='Variable capacitor',ref_prefix='C',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal',dest=TEMPLATE,tool=SKIDL,keywords='quartz ceramic resonator oscillator',description='Two pin crystal',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND2',dest=TEMPLATE,tool=SKIDL,keywords='quartz ceramic resonator oscillator',description='Three pin crystal (GND on pin 2), e.g. in SMD package',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND23',dest=TEMPLATE,tool=SKIDL,keywords='quartz ceramic resonator oscillator',description='Four pin crystal (GND on pins 2 and 3), e.g. in SMD package',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND23_Small',dest=TEMPLATE,tool=SKIDL,keywords='quartz ceramic resonator oscillator',description='Two pin crystal, two ground/package pins (pin2 and 3) small symbol',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND24',dest=TEMPLATE,tool=SKIDL,keywords='quartz ceramic resonator oscillator',description='Four pin crystal (GND on pins 2 and 4), e.g. in SMD package',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND24_Small',dest=TEMPLATE,tool=SKIDL,keywords='quartz ceramic resonator oscillator',description='Two pin crystal, two ground/package pins (pin2 and 4) small symbol',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND2_Small',dest=TEMPLATE,tool=SKIDL,keywords='quartz ceramic resonator oscillator',description='Two pin crystal, one ground/package pins (pin2) small symbol',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND3',dest=TEMPLATE,tool=SKIDL,keywords='quartz ceramic resonator oscillator',description='Three pin crystal (GND on pin 3), e.g. in SMD package',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND3_Small',dest=TEMPLATE,tool=SKIDL,keywords='quartz ceramic resonator oscillator',description='Two pin crystal, one ground/package pins (pin3) small symbol',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_Small',dest=TEMPLATE,tool=SKIDL,keywords='quartz ceramic resonator oscillator',description='Two pin crystal, small symbol',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DIAC',dest=TEMPLATE,tool=SKIDL,keywords='AC diode DIAC',description='diode for alternating current',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DIAC_ALT',dest=TEMPLATE,tool=SKIDL,keywords='AC diode DIAC',description='diode for alternating current, alternativ symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_ALT',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Diode, alternativ symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Bridge_+-AA',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='D_Bridge_+A-A',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='D_Bridge_+AA-',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='D_Bridge_-A+A',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='D_Bridge_-AA+',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='D_Capacitance',dest=TEMPLATE,tool=SKIDL,keywords='capacitance diode varicap varactor',description='variable capacitance diode (varicap, varactor)',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Capacitance_ALT',dest=TEMPLATE,tool=SKIDL,keywords='capacitance diode varicap varactor',description='variable capacitance diode (varicap, varactor), alternativ symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Photo',dest=TEMPLATE,tool=SKIDL,keywords='photodiode diode opto',description='Photodiode',ref_prefix='D',num_units=1,fplist=['*photodiode*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Photo_ALT',dest=TEMPLATE,tool=SKIDL,keywords='photodiode diode opto',description='Photodiode, alternative symbol',ref_prefix='D',num_units=1,fplist=['*photodiode*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Radiation',dest=TEMPLATE,tool=SKIDL,keywords='radiation detector diode',description='semiconductor radiation detector',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Radiation_ALT',dest=TEMPLATE,tool=SKIDL,keywords='radiation detector diode',description='semiconductor radiation detector, alternativ symbol',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky',dest=TEMPLATE,tool=SKIDL,keywords='diode Schottky',description='Schottky diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_AAK',dest=TEMPLATE,tool=SKIDL,keywords='diode schotty SCHDPAK',description='Schottky diode, two anode pins',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='A',do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_AKA',dest=TEMPLATE,tool=SKIDL,keywords='diode schotty SCHDPAK',description='Schottky diode, two anode pins',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='A',do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_AKK',dest=TEMPLATE,tool=SKIDL,keywords='diode schotty SCHDPAK',description='Schottky diode, two cathode pins',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_ALT',dest=TEMPLATE,tool=SKIDL,keywords='diode schotty',description='Schottky diode, alternativ symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_KAA',dest=TEMPLATE,tool=SKIDL,keywords='diode schotty SCHDPAK',description='Schottky diode, two anode pins',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_KAK',dest=TEMPLATE,tool=SKIDL,keywords='diode schotty SCHDPAK',description='Schottky diode, two cathode pins',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_KKA',dest=TEMPLATE,tool=SKIDL,keywords='diode schotty SCHDPAK',description='Schottky diode, two cathode pins',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_Small',dest=TEMPLATE,tool=SKIDL,keywords='diode schottky',description='Schottky diode, small symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_Small_ALT',dest=TEMPLATE,tool=SKIDL,keywords='diode schottky',description='Schottky diode, small symbol, alternativ symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_ACom_AKK',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual schottky diode, common anode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_ACom_KAK',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual schottky diode, common anode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_ACom_KKA',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual schottky diode, common anode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_KCom_AAK',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual schottky diode, common cathode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_KCom_AKA',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual schottky diode, common cathode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_KCom_KAA',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual schottky diode, common cathode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_Serial_ACK',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual schottky diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_Serial_AKC',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual schottky diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='common',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_Serial_CAK',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual schottky diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_Serial_CKA',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual schottky diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_Serial_KAC',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual schottky diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='common',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_Serial_KCA',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual schottky diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Shockley',dest=TEMPLATE,tool=SKIDL,keywords='Shockley diode',description='Shockley Diode (PNPN Diode)',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Small',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Diode, small symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Small_ALT',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Diode, small symbol, alternativ symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_TVS',dest=TEMPLATE,tool=SKIDL,keywords='diode TVS thyrector',description='Bidirectional transient-voltage-suppression (TVS) diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_TVS_ALT',dest=TEMPLATE,tool=SKIDL,keywords='diode TVS thyrector',description='Bidirectional transient-voltage-suppression (TVS) diode, alternative symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_TVS_x2_AAC',dest=TEMPLATE,tool=SKIDL,keywords='diode TVS thyrector',description='Bidirectional dual transient-voltage-suppression (TVS) diode (center=pin3)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='common',do_erc=True)]),
        Part(name='D_TVS_x2_ACA',dest=TEMPLATE,tool=SKIDL,keywords='diode TVS thyrector',description='Bidirectional dual transient-voltage-suppression (TVS) diode (center=pin2)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='common',do_erc=True),
            Pin(num='3',name='A2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_TVS_x2_CAA',dest=TEMPLATE,tool=SKIDL,keywords='diode TVS thyrector',description='Bidirectional dual transient-voltage-suppression (TVS) diode (center=pin1)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='common',do_erc=True),
            Pin(num='2',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Temperature_Dependent',dest=TEMPLATE,tool=SKIDL,keywords='temperature sensor diode',description='temperature dependent diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Temperature_Dependent_ALT',dest=TEMPLATE,tool=SKIDL,keywords='temperature sensor diode',description='temperature dependent diode, alternativ symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Tunnel',dest=TEMPLATE,tool=SKIDL,keywords='tunnel diode',description='Tunnel Diode (Esaki Diode)',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Tunnel_ALT',dest=TEMPLATE,tool=SKIDL,keywords='tunnel diode',description='Tunnel Diode (Esaki Diode), alternativ symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Unitunnel',dest=TEMPLATE,tool=SKIDL,keywords='unitunnel diode',description='Unitunnel Diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Unitunnel_ALT',dest=TEMPLATE,tool=SKIDL,keywords='unitunnel diode',description='Unitunnel Diode, alternativ symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Zener',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Zener Diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Zener_ALT',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Zener Diode, alternativ symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Zener_Small',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Zener Diode, small symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Zener_Small_ALT',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Zener Diode, small symbol, alternativ symbol',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_ACom_AKK',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual diode, common anode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_ACom_KAK',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual diode, common anode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_ACom_KKA',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual diode, common anode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_KCom_AAK',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual diode, common cathode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_KCom_AKA',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual diode, common cathode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_KCom_KAA',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual diode, common cathode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_Serial_ACK',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_Serial_AKC',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='common',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_Serial_CAK',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_Serial_CKA',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_Serial_KAC',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='common',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_Serial_KCA',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Dual diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Delay_Line',dest=TEMPLATE,tool=SKIDL,keywords='delay propogation retard impedance',description='Delay line',ref_prefix='L',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='COMMUN',do_erc=True)]),
        Part(name='EMI_Filter_CLC',dest=TEMPLATE,tool=SKIDL,keywords='EMI T-filter',description='EMI T-filter (CLC)',ref_prefix='FL',num_units=1,fplist=['Resonator*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='EMI_Filter_LCL',dest=TEMPLATE,tool=SKIDL,keywords='EMI T-filter',description='EMI T-filter (LCL)',ref_prefix='FL',num_units=1,fplist=['Resonator*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='EMI_Filter_LL',dest=TEMPLATE,tool=SKIDL,keywords='EMI filter',description='EMI 2-inductor-filter',ref_prefix='FL',num_units=1,fplist=['L_*', 'L_CommonMode*'],do_erc=True,aliases=['EMI_Filter_CommonMode'],pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Earphone',dest=TEMPLATE,tool=SKIDL,keywords='earphone speaker headphone',description='earphone, polar',ref_prefix='LS',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Electromagnetic_Actor',dest=TEMPLATE,tool=SKIDL,keywords='electromagnet coil inductor',description='electro-magnetic actor',ref_prefix='L',num_units=1,fplist=['Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Ferrite_Bead',dest=TEMPLATE,tool=SKIDL,keywords='L ferite bead inductor filter',description='Ferrite bead',ref_prefix='L',num_units=1,fplist=['Inductor_*', 'L_*', '*Ferrite*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Ferrite_Bead_Small',dest=TEMPLATE,tool=SKIDL,keywords='L ferite bead inductor filter',description='Ferrite bead, small symbol',ref_prefix='L',num_units=1,fplist=['Inductor_*', 'L_*', '*Ferrite*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Frequency_Counter',dest=TEMPLATE,tool=SKIDL,keywords='Frequency Counter',description='Frequency Counter',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Fuse',dest=TEMPLATE,tool=SKIDL,keywords='Fuse',description='Fuse, generic',ref_prefix='F',num_units=1,fplist=['*Fuse*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Fuse_Polarized',dest=TEMPLATE,tool=SKIDL,keywords='Fuse',description='Fuse, generic',ref_prefix='F',num_units=1,fplist=['*Fuse*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True)]),
        Part(name='Fuse_Polarized_Small',dest=TEMPLATE,tool=SKIDL,keywords='fuse',description='Fuse, polarised',ref_prefix='F',num_units=1,fplist=['SM*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True)]),
        Part(name='Fuse_Small',dest=TEMPLATE,tool=SKIDL,keywords='fuse',description='Fuse, small symbol',ref_prefix='F',num_units=1,fplist=['SM*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Galvanometer',dest=TEMPLATE,tool=SKIDL,keywords='Galvanometer',description='Galvanometer',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Hall_Generator',dest=TEMPLATE,tool=SKIDL,keywords='Hall generator magnet',description='Hall generator',ref_prefix='HG',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='U1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='U2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='UH1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='UH2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Heater',dest=TEMPLATE,tool=SKIDL,keywords='heater R resistor',description='Resistive Heater',ref_prefix='R',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Jumper',dest=TEMPLATE,tool=SKIDL,keywords='jumper bridge link nc',description='Jumper, generic, normally closed',ref_prefix='JP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Jumper_NC_Dual',dest=TEMPLATE,tool=SKIDL,keywords='jumper bridge link nc',description='Dual Jumper, normally closed',ref_prefix='JP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Jumper_NC_Small',dest=TEMPLATE,tool=SKIDL,keywords='jumper link bridge',description='Jumper, normally closed',ref_prefix='JP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Jumper_NO_Small',dest=TEMPLATE,tool=SKIDL,keywords='jumper link bridge',description='Jumper, normally open',ref_prefix='JP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='L',dest=TEMPLATE,tool=SKIDL,keywords='inductor choke coil reactor magnetic',description='Inductor',ref_prefix='L',num_units=1,fplist=['Choke_*', '*Coil*', 'Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED',dest=TEMPLATE,tool=SKIDL,keywords='led diode',description='LED generic',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_ALT',dest=TEMPLATE,tool=SKIDL,keywords='led diode',description='LED generic, alternativ symbol',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_ARGB',dest=TEMPLATE,tool=SKIDL,keywords='led rgb diode',description='LED RGB, common anode (pin 1)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='RK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='GK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='BK',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_CRGB',dest=TEMPLATE,tool=SKIDL,keywords='led rgb diode',description='LED RGB, Common Cathode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='RA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='GA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='BA',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_Dual_2pin',dest=TEMPLATE,tool=SKIDL,keywords='led diode bicolor dual',description='LED dual, 2pin version',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='KA',do_erc=True),
            Pin(num='2',name='AK',do_erc=True)]),
        Part(name='LED_Dual_AAC',dest=TEMPLATE,tool=SKIDL,keywords='led diode bicolor dual',description='LED dual, common cathode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A1',do_erc=True),
            Pin(num='2',name='A2',do_erc=True),
            Pin(num='3',name='K',do_erc=True)]),
        Part(name='LED_Dual_AACC',dest=TEMPLATE,tool=SKIDL,keywords='led diode bicolor dual',description='LED dual, 4-pin',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A1',do_erc=True),
            Pin(num='2',name='A2',do_erc=True),
            Pin(num='3',name='K1',do_erc=True),
            Pin(num='4',name='K2',do_erc=True)]),
        Part(name='LED_Dual_ACA',dest=TEMPLATE,tool=SKIDL,keywords='led diode bicolor dual',description='LED dual, common cathode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A1',do_erc=True),
            Pin(num='2',name='K',do_erc=True),
            Pin(num='3',name='A2',do_erc=True)]),
        Part(name='LED_Dual_ACAC',dest=TEMPLATE,tool=SKIDL,keywords='led diode bicolor dual',description='LED dual, 4-pin',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A1',do_erc=True),
            Pin(num='2',name='K1',do_erc=True),
            Pin(num='3',name='A2',do_erc=True),
            Pin(num='4',name='K2',do_erc=True)]),
        Part(name='LED_Dual_CAC',dest=TEMPLATE,tool=SKIDL,keywords='led diode bicolor dual',description='LED dual, common anode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K1',do_erc=True),
            Pin(num='2',name='A',do_erc=True),
            Pin(num='3',name='K2',do_erc=True)]),
        Part(name='LED_Dual_CCA',dest=TEMPLATE,tool=SKIDL,keywords='led diode bicolor dual',description='LED dual, common anode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K1',do_erc=True),
            Pin(num='2',name='K2',do_erc=True),
            Pin(num='3',name='A',do_erc=True)]),
        Part(name='LED_PAD',dest=TEMPLATE,tool=SKIDL,keywords='led diode pad',description='LED with pad',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='PAD',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_RABG',dest=TEMPLATE,tool=SKIDL,keywords='led rgb diode',description='LED RGB, common anode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='RK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='BK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='GK',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_RAGB',dest=TEMPLATE,tool=SKIDL,keywords='led rgb diode',description='LED RGB, common anode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='RK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='GK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='BK',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_RCBG',dest=TEMPLATE,tool=SKIDL,keywords='led rgb diode',description='LED RGB, Common Cathode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='RA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='BA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='GA',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_RCGB',dest=TEMPLATE,tool=SKIDL,keywords='led rgb diode',description='LED RGB, Common Cathode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='RA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='GA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='BA',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_RGB',dest=TEMPLATE,tool=SKIDL,keywords='led rgb diode',description='LED RGB 6 pins',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='RK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='GK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='BK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='BA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='GA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='RA',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_RGB_EP',dest=TEMPLATE,tool=SKIDL,keywords='led rgb diode',description='LED RGB 6 pins, exposed pad',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='RK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='GK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='BK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='BA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='GA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='RA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='PAD',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_Series',dest=TEMPLATE,tool=SKIDL,keywords='led diode',description='several LEDs in series',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_Series_PAD',dest=TEMPLATE,tool=SKIDL,keywords='led diode pad',description='LED with pad',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='PAD',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_Small',dest=TEMPLATE,tool=SKIDL,keywords='led diode light-emitting-diode',description='LED, small symbol',ref_prefix='D',num_units=1,fplist=['LED-*', 'LED_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_Small_ALT',dest=TEMPLATE,tool=SKIDL,keywords='led diode light-emitting-diode',description='LED, small symbol, alternativ symbol',ref_prefix='D',num_units=1,fplist=['LED-*', 'LED_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LTRIM',dest=TEMPLATE,tool=SKIDL,keywords='inductor choke coil reactor magnetic',description='Variable Inductor',ref_prefix='L',num_units=1,fplist=['Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='L_Core_Ferrite',dest=TEMPLATE,tool=SKIDL,keywords='inductor choke coil reactor magnetic',description='Inductor with Ferrite Core',ref_prefix='L',num_units=1,fplist=['Choke_*', '*Coil*', 'Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='L_Core_Ferrite_Small',dest=TEMPLATE,tool=SKIDL,keywords='inductor choke coil reactor magnetic',description='Inductor with ferrite core, small symbol',ref_prefix='L',num_units=1,fplist=['Choke_*', '*Coil*', 'Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='L_Core_Iron',dest=TEMPLATE,tool=SKIDL,keywords='inductor choke coil reactor magnetic',description='Inductor with Iron Core',ref_prefix='L',num_units=1,fplist=['Choke_*', '*Coil*', 'Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='L_Core_Iron_Small',dest=TEMPLATE,tool=SKIDL,keywords='inductor choke coil reactor magnetic',description='Inductor with iron core, small symbol',ref_prefix='L',num_units=1,fplist=['Choke_*', '*Coil*', 'Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='L_Small',dest=TEMPLATE,tool=SKIDL,keywords='inductor choke coil reactor magnetic',description='Inductor, small symbol',ref_prefix='L',num_units=1,fplist=['Choke_*', '*Coil*', 'Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Lamp',dest=TEMPLATE,tool=SKIDL,keywords='lamp',description='lamp',ref_prefix='LA',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Lamp_Flash',dest=TEMPLATE,tool=SKIDL,keywords='flash lamp',description='flash lamp tube',ref_prefix='LA',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Lamp_Neon',dest=TEMPLATE,tool=SKIDL,keywords='neon lamp',description='neon lamp',ref_prefix='NE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Laserdiode_1A3C',dest=TEMPLATE,tool=SKIDL,keywords='opto laserdiode',description='Laser Diode in a 2-pin package',ref_prefix='LD',num_units=1,fplist=['*LaserDiode*'],do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Laserdiode_1C2A',dest=TEMPLATE,tool=SKIDL,keywords='opto laserdiode',description='Laser Diode in a 2-pin package',ref_prefix='LD',num_units=1,fplist=['*LaserDiode*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Laserdiode_M_TYPE',dest=TEMPLATE,tool=SKIDL,keywords='opto laserdiode photodiode',description='Laser Diode in a 3-pin package with photodiode (1=LD-A, 2=LD-C/PD-C, 3=PD-A)',ref_prefix='LD',num_units=1,fplist=['*LaserDiode*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Laserdiode_N_TYPE',dest=TEMPLATE,tool=SKIDL,keywords='opto laserdiode photodiode',description='Laser Diode in a 3-pin package with photodiode (1=LD-C, 2=LD-A/PD-C, 3=PD-A)',ref_prefix='LD',num_units=1,fplist=['*LaserDiode*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Laserdiode_P_TYPE',dest=TEMPLATE,tool=SKIDL,keywords='opto laserdiode photodiode',description='Laser Diode in a 3-pin package with photodiode (1=LD-A, 2=LD-C/PD-A, 3=PD-C)',ref_prefix='LD',num_units=1,fplist=['*LaserDiode*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='MEMRISTOR',dest=TEMPLATE,tool=SKIDL,keywords='Memristor',description='Memristor',ref_prefix='MR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Microphone',dest=TEMPLATE,tool=SKIDL,keywords='Microphone',description='Microphone',ref_prefix='MK',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Microphone_Condenser',dest=TEMPLATE,tool=SKIDL,keywords='Capacitance condenser Microphone',description='Condenser Microspcope',ref_prefix='MK',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Microphone_Crystal',dest=TEMPLATE,tool=SKIDL,keywords='Microphone Ultrasound crystal',description='Ultrasound receiver',ref_prefix='MK',num_units=1,do_erc=True,aliases=['Microphone_Ultrasound'],pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Ohmmeter',dest=TEMPLATE,tool=SKIDL,keywords='Ohmmeter',description='Ohmmeter, measures resistance',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Oscilloscope',dest=TEMPLATE,tool=SKIDL,keywords='Oscilloscope',description='Oscilloscope',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='POT',dest=TEMPLATE,tool=SKIDL,keywords='resistor variable',description='Potentionmeter',ref_prefix='RV',num_units=1,fplist=['Potentiometer*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='POT_Dual',dest=TEMPLATE,tool=SKIDL,keywords='resistor variable',description='Dual Potentionmeter',ref_prefix='RV',num_units=1,fplist=['Potentiometer*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='6',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='POT_Dual_Separate',dest=TEMPLATE,tool=SKIDL,keywords='resistor variable',description='Dual Potentionmeter, separate units',ref_prefix='RV',num_units=2,fplist=['Potentiometer*'],do_erc=True,pins=[
            Pin(num='1',name='4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='6',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='POT_TRIM',dest=TEMPLATE,tool=SKIDL,keywords='resistor variable trimpot trimmer',description='Trim-Potentionmeter',ref_prefix='RV',num_units=1,fplist=['Potentiometer*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Peltier_Element',dest=TEMPLATE,tool=SKIDL,keywords='Peltier TEC',description='Peltier Element, Thermoelectric Cooler (TEC)',ref_prefix='PE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Polyfuse',dest=TEMPLATE,tool=SKIDL,keywords='resettable fuse PTC PPTC polyfuse polyswitch',description='resettable fuse, polymeric positive temperature coefficient (PPTC)',ref_prefix='F',num_units=1,fplist=['*polyfuse*', '*PTC*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Polyfuse_Small',dest=TEMPLATE,tool=SKIDL,keywords='resettable fuse PTC PPTC polyfuse polyswitch',description='resettable fuse, polymeric positive temperature coefficient (PPTC), small symbol',ref_prefix='F',num_units=1,fplist=['*polyfuse*', '*PTC*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_DUAL_NPN_NPN_E1B1C2E2B2C1',dest=TEMPLATE,tool=SKIDL,keywords='NPN/NPN Transistor',description='Dual NPN/NPN Transistor, 6-pin package',ref_prefix='Q',num_units=2,fplist=['SC?70*', 'SC?88*', 'SOT?363*'],do_erc=True,pins=[
            Pin(num='1',name='E1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B1',do_erc=True),
            Pin(num='6',name='C1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='E2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='B2',do_erc=True)]),
        Part(name='Q_DUAL_NPN_PNP_E1B1C2E2B2C1',dest=TEMPLATE,tool=SKIDL,keywords='NPN/PNP Transistor',description='Dual NPN/PNP Transistor, 6-pin package',ref_prefix='Q',num_units=2,fplist=['SC?70*', 'SC?88*', 'SOT?363*'],do_erc=True,pins=[
            Pin(num='1',name='E1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B1',do_erc=True),
            Pin(num='6',name='C1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='E2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='B2',do_erc=True)]),
        Part(name='Q_DUAL_PNP_PNP_E1B1C2E2B2C1',dest=TEMPLATE,tool=SKIDL,keywords='PNP/PNP Transistor',description='Dual PNP/PNP Transistor, 6-pin package',ref_prefix='Q',num_units=2,fplist=['SC?70*', 'SC?88*', 'SOT?363*'],do_erc=True,pins=[
            Pin(num='1',name='E1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B1',do_erc=True),
            Pin(num='6',name='C1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='E2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='B2',do_erc=True)]),
        Part(name='Q_NIGBT_CEG',dest=TEMPLATE,tool=SKIDL,keywords='igbt n-igbt transistor',description='Transistor N-IGBT (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_NIGBT_CGE',dest=TEMPLATE,tool=SKIDL,keywords='igbt n-igbt transistor',description='Transistor N-IGBT (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NIGBT_ECG',dest=TEMPLATE,tool=SKIDL,keywords='igbt n-igbt transistor',description='Transistor N-IGBT (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_NIGBT_ECGC',dest=TEMPLATE,tool=SKIDL,keywords='igbt n-igbt transistor',description='Transistor N-IGBT, collector connected to mounting plane (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NIGBT_EGC',dest=TEMPLATE,tool=SKIDL,keywords='igbt n-igbt transistor',description='Transistor N-IGBT (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NIGBT_GCE',dest=TEMPLATE,tool=SKIDL,keywords='igbt n-igbt transistor',description='Transistor N-IGBT (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NIGBT_GCEC',dest=TEMPLATE,tool=SKIDL,keywords='igbt n-igbt transistor',description='Transistor N-IGBT, collector connected to mounting plane (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NIGBT_GEC',dest=TEMPLATE,tool=SKIDL,keywords='igbt n-igbt transistor',description='Transistor N-IGBT (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NJFET_DGS',dest=TEMPLATE,tool=SKIDL,keywords='njfet n-jfet transistor',description='Transistor N-JFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NJFET_DSG',dest=TEMPLATE,tool=SKIDL,keywords='njfet n-jfet transistor',description='Transistor N-JFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_NJFET_GDS',dest=TEMPLATE,tool=SKIDL,keywords='njfet n-jfet transistor',description='Transistor N-JFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NJFET_GSD',dest=TEMPLATE,tool=SKIDL,keywords='njfet n-jfet transistor',description='Transistor N-JFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NJFET_SDG',dest=TEMPLATE,tool=SKIDL,keywords='njfet n-jfet transistor',description='Transistor N-JFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_NJFET_SGD',dest=TEMPLATE,tool=SKIDL,keywords='njfet n-jfet transistor',description='Transistor N-JFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NMOS_DGS',dest=TEMPLATE,tool=SKIDL,keywords='nmos n-mos n-mosfet transistor',description='Transistor N-MOSFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NMOS_DSG',dest=TEMPLATE,tool=SKIDL,keywords='NMOS n-mos n-mosfet transistor',description='Transistor N-MOSFET with substrate diode (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_NMOS_GDS',dest=TEMPLATE,tool=SKIDL,keywords='nmos n-mos n-mosfet transistor',description='Transistor N-MOSFET with substrate diode (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NMOS_GDSD',dest=TEMPLATE,tool=SKIDL,keywords='NMOS n-mos n-mosfet transistor',description='Transistor N-MOSFETwith substrate diode, drain connected to mounting plane (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NMOS_GSD',dest=TEMPLATE,tool=SKIDL,keywords='NMOS n-mos n-mosfet transistor',description='Transistor N-MOSFETwith substrate diode (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NMOS_SDG',dest=TEMPLATE,tool=SKIDL,keywords='NMOS n-mos n-mosfet transistor',description='Transistor N-MOSFETwith substrate diode (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_NMOS_SDGD',dest=TEMPLATE,tool=SKIDL,keywords='NMOS n-mos n-mosfet transistor',description='Transistor N-MOSFETwith substrate diode, drain connected to mounting plane (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True),
            Pin(num='4',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NMOS_SGD',dest=TEMPLATE,tool=SKIDL,keywords='NMOS n-mos n-mosfet transistor',description='Transistor N-MOSFETwith substrate diode (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_BCE',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor',description='Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_BCEC',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor',description='Transistor NPN, collector connected to mounting plane (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_BEC',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor',description='Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_CBE',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor',description='Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_CEB',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor',description='Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Q_NPN_Darlington_BCE',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor darlington',description='Darlington Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_Darlington_BCEC',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor darlington',description='Darlington Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C2',do_erc=True)]),
        Part(name='Q_NPN_Darlington_BEC',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor darlington',description='Darlington Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_Darlington_CBE',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor darlington',description='Darlington Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_Darlington_CEB',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor darlington',description='Darlington Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Q_NPN_Darlington_EBC',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor darlington',description='Darlington Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_Darlington_ECB',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor darlington',description='Darlington Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_Darlington_ECBC',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor darlington',description='Darlington Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C2',do_erc=True)]),
        Part(name='Q_NPN_EBC',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor',description='Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_ECB',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor',description='Transistor NPN (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_ECBC',dest=TEMPLATE,tool=SKIDL,keywords='npn transistor',description='Transistor NPN, collector connected to mounting plane (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NUJT_BEB',dest=TEMPLATE,tool=SKIDL,keywords='UJT transistor',description='Transistor N-Type Unijunction (UJT, general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',do_erc=True),
            Pin(num='3',name='B1',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PJFET_DGS',dest=TEMPLATE,tool=SKIDL,keywords='pjfet p-jfet transistor',description='Transistor P-JFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PJFET_DSG',dest=TEMPLATE,tool=SKIDL,keywords='pjfet p-jfet transistor',description='Transistor P-JFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_PJFET_GDS',dest=TEMPLATE,tool=SKIDL,keywords='pjfet p-jfet transistor',description='Transistor P-JFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PJFET_GSD',dest=TEMPLATE,tool=SKIDL,keywords='pjfet p-jfet transistor',description='Transistor P-JFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PJFET_SDG',dest=TEMPLATE,tool=SKIDL,keywords='pjfet p-jfet transistor',description='Transistor P-JFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_PJFET_SGD',dest=TEMPLATE,tool=SKIDL,keywords='pjfet p-jfet transistor',description='Transistor P-JFET (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PMOS_DGS',dest=TEMPLATE,tool=SKIDL,keywords='pmos p-mos p-mosfet transistor',description='Transistor P-MOSFET with substrate diode (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PMOS_DSG',dest=TEMPLATE,tool=SKIDL,keywords='pmos p-mos p-mosfet transistor',description='Transistor P-MOSFET with substrate diode (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_PMOS_GDS',dest=TEMPLATE,tool=SKIDL,keywords='pmos p-mos p-mosfet transistor',description='Transistor P-MOSFET with substrate diode (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PMOS_GDSD',dest=TEMPLATE,tool=SKIDL,keywords='pmos p-mos p-mosfet transistor',description='Transistor P-MOSFET with substrate diode, drain connected to mounting plane (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PMOS_GSD',dest=TEMPLATE,tool=SKIDL,keywords='pmos p-mos p-mosfet transistor',description='Transistor P-MOSFET with substrate diode (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PMOS_SDG',dest=TEMPLATE,tool=SKIDL,keywords='pmos p-mos p-mosfet transistor',description='Transistor P-MOSFET with substrate diode (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_PMOS_SDGD',dest=TEMPLATE,tool=SKIDL,keywords='pmos p-mos p-mosfet transistor',description='Transistor P-MOSFET with substrate diode, drain connected to mounting plane (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True),
            Pin(num='4',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PMOS_SGD',dest=TEMPLATE,tool=SKIDL,keywords='pmos p-mos p-mosfet transistor',description='Transistor P-MOSFET with substrate diode (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_BCE',dest=TEMPLATE,tool=SKIDL,keywords='pnp transistor',description='Transistor PNP (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_BCEC',dest=TEMPLATE,tool=SKIDL,keywords='pnp transistor',description='Transistor PNP, collector connected to mounting plane (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_BEC',dest=TEMPLATE,tool=SKIDL,keywords='pnp transistor',description='Transistor PNP (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_CBE',dest=TEMPLATE,tool=SKIDL,keywords='pnp transistor',description='Transistor PNP (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_CEB',dest=TEMPLATE,tool=SKIDL,keywords='pnp transistor',description='Transistor PNP (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Q_PNP_Darlington_BCE',dest=TEMPLATE,tool=SKIDL,keywords='PNP transistor darlington',description='Darlington Transistor PNP (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_Darlington_BCEC',dest=TEMPLATE,tool=SKIDL,keywords='PNP transistor darlington',description='Darlington Transistor PNP, collector connected to mounting plane (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_Darlington_BEC',dest=TEMPLATE,tool=SKIDL,keywords='PNP transistor darlington',description='Darlington Transistor PNP (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_Darlington_CBE',dest=TEMPLATE,tool=SKIDL,keywords='PNP transistor darlington',description='Darlington Transistor PNP (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_Darlington_CEB',dest=TEMPLATE,tool=SKIDL,keywords='PNP transistor darlington',description='Darlington Transistor PNP (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Q_PNP_Darlington_EBC',dest=TEMPLATE,tool=SKIDL,keywords='PNP transistor darlington',description='Darlington Transistor PNP (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_Darlington_ECB',dest=TEMPLATE,tool=SKIDL,keywords='PNP transistor darlington',description='Darlington Transistor PNP (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Q_PNP_Darlington_ECBC',dest=TEMPLATE,tool=SKIDL,keywords='PNP transistor darlington',description='Darlington Transistor PNP, collector connected to mounting plane (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_EBC',dest=TEMPLATE,tool=SKIDL,keywords='pnp transistor',description='Transistor PNP (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_ECB',dest=TEMPLATE,tool=SKIDL,keywords='pnp transistor',description='Transistor PNP (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Q_PNP_ECBC',dest=TEMPLATE,tool=SKIDL,keywords='pnp transistor',description='Transistor PNP, collector connected to mounting plane (general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PUJT_BEB',dest=TEMPLATE,tool=SKIDL,keywords='UJT transistor',description='Transistor P-Type Unijunction (UJT, general)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',do_erc=True),
            Pin(num='3',name='B1',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Photo_NPN',dest=TEMPLATE,tool=SKIDL,keywords='npn phototransistor',description='Phototransistor NPN, 2-pin (C=1, E=2)',ref_prefix='Q',num_units=1,do_erc=True,aliases=['Q_Photo_NPN_CE'],pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Photo_NPN_CBE',dest=TEMPLATE,tool=SKIDL,keywords='npn phototransistor',description='Phototransistor NPN, 3-pin with base pin (C=1, B=2, E=3)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Photo_NPN_EBC',dest=TEMPLATE,tool=SKIDL,keywords='npn phototransistor',description='Phototransistor NPN, 3-pin with base pin (E=1, B=2, C=3)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Photo_NPN_EC',dest=TEMPLATE,tool=SKIDL,keywords='NPN phototransistor',description='Phototransistor NPN, 2-pin (C=1, E=2)',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_TRIAC_AAG',dest=TEMPLATE,tool=SKIDL,keywords='triode for alternating current TRIAC',description='triode for alternating current (TRIAC)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_TRIAC_AGA',dest=TEMPLATE,tool=SKIDL,keywords='triode for alternating current TRIAC',description='triode for alternating current (TRIAC)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='A2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_TRIAC_GAA',dest=TEMPLATE,tool=SKIDL,keywords='triode for alternating current TRIAC',description='triode for alternating current (TRIAC)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Thyristor_AGK',dest=TEMPLATE,tool=SKIDL,keywords='Thyristor silicon controlled rectifier',description='silicon controlled rectifier (Thyristor)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Thyristor_AKG',dest=TEMPLATE,tool=SKIDL,keywords='Thyristor silicon controlled rectifier',description='silicon controlled rectifier (Thyristor)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_Thyristor_GAK',dest=TEMPLATE,tool=SKIDL,keywords='Thyristor silicon controlled rectifier',description='silicon controlled rectifier (Thyristor)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Thyristor_GKA',dest=TEMPLATE,tool=SKIDL,keywords='Thyristor silicon controlled rectifier',description='silicon controlled rectifier (Thyristor)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Thyristor_KAG',dest=TEMPLATE,tool=SKIDL,keywords='Thyristor silicon controlled rectifier',description='silicon controlled rectifier (Thyristor)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_Thyristor_KGA',dest=TEMPLATE,tool=SKIDL,keywords='Thyristor silicon controlled rectifier',description='silicon controlled rectifier (Thyristor)',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R',dest=TEMPLATE,tool=SKIDL,keywords='r res resistor',description='Resistor',ref_prefix='R',num_units=1,fplist=['R_*', 'R_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='RF_Shield_One_Piece',dest=TEMPLATE,tool=SKIDL,keywords='RF EMI Shielding Cabinet',description='One-Piece EMI RF Shielding Cabinet',ref_prefix='J',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='Shield',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='RF_Shield_Two_Pieces',dest=TEMPLATE,tool=SKIDL,keywords='RF EMI Shielding Cabinet',description='Two-Piece EMI RF Shielding Cabinet',ref_prefix='J',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='Shield',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='RTRIM',dest=TEMPLATE,tool=SKIDL,keywords='r res resistor variable potentiometer trimmer',description='trimmable Resistor (Preset resistor)',ref_prefix='R',num_units=1,fplist=['R_*', 'R_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network03',dest=TEMPLATE,tool=SKIDL,keywords='R Network star-topology',description='3 Resistor network, star topology, bussed resistors, small symbol',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network04',dest=TEMPLATE,tool=SKIDL,keywords='R Network star-topology',description='4 Resistor network, star topology, bussed resistors, small symbol',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network05',dest=TEMPLATE,tool=SKIDL,keywords='R Network star-topology',description='5 Resistor network, star topology, bussed resistors, small symbol',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network06',dest=TEMPLATE,tool=SKIDL,keywords='R Network star-topology',description='6 Resistor network, star topology, bussed resistors, small symbol',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network07',dest=TEMPLATE,tool=SKIDL,keywords='R Network star-topology',description='7 Resistor network, star topology, bussed resistors, small symbol',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network08',dest=TEMPLATE,tool=SKIDL,keywords='R Network star-topology',description='8 Resistor network, star topology, bussed resistors, small symbol',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network09',dest=TEMPLATE,tool=SKIDL,keywords='R Network star-topology',description='9 Resistor network, star topology, bussed resistors, small symbol',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network10',dest=TEMPLATE,tool=SKIDL,keywords='R Network star-topology',description='10 Resistor network, star topology, bussed resistors, small symbol',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network11',dest=TEMPLATE,tool=SKIDL,keywords='R Network star-topology',description='11 Resistor network, star topology, bussed resistors, small symbol',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R11',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network12',dest=TEMPLATE,tool=SKIDL,keywords='R Network star-topology',description='12 Resistor network, star topology, bussed resistors, small symbol',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R11',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R12',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network13',dest=TEMPLATE,tool=SKIDL,keywords='R Network star-topology',description='13 Resistor network, star topology, bussed resistors, small symbol',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R11',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R12',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R13',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x02_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network divider topology',description='2 Voltage Dividers network, Dual Terminator, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x03_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network divider topology',description='3 Voltage Dividers network, Dual Terminator, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x04_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network divider topology',description='4 Voltage Dividers network, Dual Terminator, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x05_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network divider topology',description='5 Voltage Dividers network, Dual Terminator, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x06_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network divider topology',description='6 Voltage Dividers network, Dual Terminator, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x07_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network divider topology',description='7 Voltage Dividers network, Dual Terminator, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x08_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network divider topology',description='8 Voltage Dividers network, Dual Terminator, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x09_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network divider topology',description='9 Voltage Dividers network, Dual Terminator, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x10_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network divider topology',description='10 Voltage Dividers network, Dual Terminator, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x11_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network divider topology',description='11 Voltage Dividers network, Dual Terminator, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R11',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_PHOTO',dest=TEMPLATE,tool=SKIDL,keywords='resistor variable light opto LDR',description='Photoresistor, light sensitive resistor, LDR',ref_prefix='R',num_units=1,fplist=['R?', 'R?-*', 'LDR*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack02',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='2 Resistor network, parallel topology, DIP package',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack02_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='2 Resistor network, parallel topology, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R2.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack03',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='3 Resistor network, parallel topology, DIP package',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack03_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='3 Resistor network, parallel topology, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R3.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack04',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='4 Resistor network, parallel topology, DIP package',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack04_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='4 Resistor network, parallel topology, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R4.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack05',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='5 Resistor network, parallel topology, DIP package',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack05_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='5 Resistor network, parallel topology, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R5.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack06',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='6 Resistor network, parallel topology, DIP package',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack06_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='6 Resistor network, parallel topology, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R6.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack07',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='7 Resistor network, parallel topology, DIP package',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R7.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack07_SIP',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='7 Resistor network, parallel topology, SIP package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R7.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R7.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack08',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='8 Resistor network, parallel topology, DIP package',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R7.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R8.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R7.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='15',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='16',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack09',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='9 Resistor network, parallel topology, DIP package',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R7.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R8.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R9.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R8.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R7.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='15',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='16',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='17',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='18',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack10',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='10 Resistor network, parallel topology, DIP package',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R7.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R8.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R9.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R10.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='20',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R9.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R8.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R7.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='15',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='16',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='17',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='18',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='19',name='R2.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack11',dest=TEMPLATE,tool=SKIDL,keywords='R Network parallel topology',description='11 Resistor network, parallel topology, DIP package',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R7.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R8.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R9.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R10.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='20',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R11.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='21',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R11.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='22',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R10.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R9.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='15',name='R8.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='16',name='R7.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='17',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='18',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='19',name='R4.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Shunt',dest=TEMPLATE,tool=SKIDL,keywords='r res shunt resistor',description='Shunt Resistor',ref_prefix='R',num_units=1,fplist=['R_*Shunt*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Small',dest=TEMPLATE,tool=SKIDL,keywords='r resistor',description='Resistor, small symbol',ref_prefix='R',num_units=1,fplist=['R_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Variable',dest=TEMPLATE,tool=SKIDL,keywords='r res resistor variable potentiometer',description='variable Resistor (Rheostat)',ref_prefix='R',num_units=1,fplist=['R_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Resonator',dest=TEMPLATE,tool=SKIDL,keywords='Ceramic Resonator',description='Three pin ceramic resonator',ref_prefix='Y',num_units=1,fplist=['Resonator*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Resonator_Small',dest=TEMPLATE,tool=SKIDL,keywords='Ceramic Resonator',description='Three pin ceramic resonator',ref_prefix='Y',num_units=1,fplist=['Resonator*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Rotary_Encoder',dest=TEMPLATE,tool=SKIDL,keywords='rotary switch encoder',description='Rotary encoder, dual channel, incremental quadrate outputs',ref_prefix='SW',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',do_erc=True),
            Pin(num='2',name='C',do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Rotary_Encoder_Switch',dest=TEMPLATE,tool=SKIDL,keywords='rotary switch encoder switch push button',description='Rotary encoder, dual channel, incremental quadrate outputs, with switch',ref_prefix='SW',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',do_erc=True),
            Pin(num='2',name='C',do_erc=True),
            Pin(num='3',name='B',do_erc=True),
            Pin(num='4',name='~',do_erc=True),
            Pin(num='5',name='~',do_erc=True)]),
        Part(name='Solar_Cell',dest=TEMPLATE,tool=SKIDL,keywords='solar cell',description='single solar cell',ref_prefix='SC',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Solar_Cells',dest=TEMPLATE,tool=SKIDL,keywords='solar cell',description='multiple solar cells',ref_prefix='SC',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='SPARK_GAP',dest=TEMPLATE,tool=SKIDL,keywords='spark gap esd electrostatic suppression',description='Spark Gap',ref_prefix='E',num_units=1,fplist=['SG*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Speaker',dest=TEMPLATE,tool=SKIDL,keywords='speaker sound',description='speaker',ref_prefix='LS',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='1',do_erc=True),
            Pin(num='2',name='2',do_erc=True)]),
        Part(name='Speaker_Crystal',dest=TEMPLATE,tool=SKIDL,keywords='crystal speaker ultrasonic transducer',description='ultrasonic transducer',ref_prefix='LS',num_units=1,do_erc=True,aliases=['Speaker_Ultrasound'],pins=[
            Pin(num='1',name='1',do_erc=True),
            Pin(num='2',name='2',do_erc=True)]),
        Part(name='TEST',dest=TEMPLATE,tool=SKIDL,keywords='tp testpoint',description='Testpoint, connection for test equipment',ref_prefix='TP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor',dest=TEMPLATE,tool=SKIDL,keywords='r res thermistor',description='Thermistor, temperature-dependent resistor',ref_prefix='TH',num_units=1,fplist=['R_*', 'SM0603', 'SM0805'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor_NTC',dest=TEMPLATE,tool=SKIDL,keywords='thermistor NTC resistor sensor RTD',description='temperature dependent resistor, negative temperature coefficient (NTC)',ref_prefix='TH',num_units=1,fplist=['*NTC*', '*Thermistor*', 'PIN?ARRAY*', 'bornier*', '*Terminal?Block*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor_NTC_3wire',dest=TEMPLATE,tool=SKIDL,keywords='thermistor NTC resistor sensor RTD',description='temperature dependent resistor, negative temperature coefficient (NTC), 3-wire interface',ref_prefix='TH',num_units=1,fplist=['*NTC*', '*Thermistor*', 'PIN?ARRAY*', 'bornier*', '*Terminal?Block*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor_NTC_4wire',dest=TEMPLATE,tool=SKIDL,keywords='thermistor NTC resistor sensor RTD',description='temperature dependent resistor, negative temperature coefficient (NTC), 4-wire interface',ref_prefix='TH',num_units=1,fplist=['*NTC*', '*Thermistor*', 'PIN?ARRAY*', 'bornier*', '*Terminal?Block*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor_PTC',dest=TEMPLATE,tool=SKIDL,keywords='resistor PTC thermistor sensor RTD',description='temperature dependent resistor, positive temperature coefficient (PTC)',ref_prefix='TH',num_units=1,fplist=['*PTC*', '*Thermistor*', 'PIN?ARRAY*', 'bornier*', '*Terminal?Block*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor_PTC_3wire',dest=TEMPLATE,tool=SKIDL,keywords='resistor PTC thermistor sensor RTD',description='temperature dependent resistor, positive temperature coefficient (PTC), 3-wire interface',ref_prefix='TH',num_units=1,fplist=['PIN_ARRAY_3X1', 'bornier3', 'TerminalBlock*3pol'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor_PTC_4wire',dest=TEMPLATE,tool=SKIDL,keywords='resistor PTC thermistor sensor RTD',description='temperature dependent resistor, positive temperature coefficient (PTC), 3-wire interface',ref_prefix='TH',num_units=1,fplist=['PIN_ARRAY_4X1', 'bornier4', 'TerminalBlock*4pol'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermocouple',dest=TEMPLATE,tool=SKIDL,keywords='thermocouple temperature sensor cold junction',description='thermocouple',ref_prefix='TC',num_units=1,fplist=['PIN?ARRAY*', 'bornier*', '*Terminal?Block*', 'Thermo*Couple*'],do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermocouple_ALT',dest=TEMPLATE,tool=SKIDL,keywords='thermocouple temperature sensor cold junction',description='thermocouple with connector block',ref_prefix='TC',num_units=1,fplist=['PIN?ARRAY*', 'bornier*', '*Terminal?Block*', 'Thermo*Couple*'],do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermocouple_Block',dest=TEMPLATE,tool=SKIDL,keywords='thermocouple temperature sensor cold junction',description='thermocouple with isothermal block',ref_prefix='TC',num_units=1,fplist=['PIN?ARRAY*', 'bornier*', '*Terminal?Block*', 'Thermo*Couple*'],do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_1P_1S',dest=TEMPLATE,tool=SKIDL,keywords='transformer coil magnet',description='Transformer, single primary, single secondary',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='AA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='AB',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='SA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='SB',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_1P_1S_SO8',dest=TEMPLATE,tool=SKIDL,keywords='transformer coil magnet',description='Transformer, single primary, single secondary, SO-8 package',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='AA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='AB',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='SA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='SB',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_1P_2S',dest=TEMPLATE,tool=SKIDL,keywords='transformer coil magnet',description='Transformer, single primary, dual secondary',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='AA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='AB',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='SA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='SB',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='SC',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='SD',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_1P_SS',dest=TEMPLATE,tool=SKIDL,keywords='transformer coil magnet',description='Transformer, single primary, split secondary',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='AA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='AB',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='SA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='SC',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='SB',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_AUDIO',dest=TEMPLATE,tool=SKIDL,keywords='transformer coil magnet sound',description='Audio transformer',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='0',name='~',do_erc=True),
            Pin(num='1',name='AA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='AB',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='SA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='SB',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_SP_1S',dest=TEMPLATE,tool=SKIDL,keywords='transformer coil magnet',description='Transformer, split primary, single secondary',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='PR1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='PM',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='PR2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='S1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='S2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_SP_2S',dest=TEMPLATE,tool=SKIDL,keywords='transformer coil magnet',description='Transformer, split primary, dual secondary',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='IN+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='PM',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='IN-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='OUT1A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='OUT1B',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='OUT2A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='OUT2B',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Varistor',dest=TEMPLATE,tool=SKIDL,keywords='vdr resistance',description='Voltage dependent resistor',ref_prefix='RV',num_units=1,fplist=['RV_*', 'Varistor*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Voltage_Divider',dest=TEMPLATE,tool=SKIDL,keywords='R Network voltage divider',description='voltage divider in a single package',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*', 'SOT?23'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Voltage_Divider_CenterPin1',dest=TEMPLATE,tool=SKIDL,keywords='R Network voltage divider',description='Voltage Divider (center=pin1)',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*', 'SOT?23'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Voltage_Divider_CenterPin3',dest=TEMPLATE,tool=SKIDL,keywords='R Network voltage divider',description='Voltage Divider (center=pin3)',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*', 'SOT?23'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Voltmeter_AC',dest=TEMPLATE,tool=SKIDL,keywords='Voltmeter AC',description='AC Voltmeter',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Voltmeter_DC',dest=TEMPLATE,tool=SKIDL,keywords='Voltmeter DC',description='DC Voltmeter',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)])])
