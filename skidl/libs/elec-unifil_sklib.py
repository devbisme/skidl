from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

elec_unifil = SchLib(tool=SKIDL).add_parts(*[
        Part(name='A_1KVA',dest=TEMPLATE,tool=SKIDL,keywords='Parafoudre',description="Absorbeur d'ondes 1KVA",ref_prefix='EA',num_units=1,do_erc=True,pins=[
            Pin(num='3',name='~',do_erc=True),
            Pin(num='1',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True)]),
        Part(name='B_8',dest=TEMPLATE,tool=SKIDL,keywords='Boite',description='Boite de connexion',ref_prefix='EB',num_units=1,do_erc=True,pins=[
            Pin(num='7',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='6',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='8',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='5',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='1',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='2',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='3',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='4',name='~',func=Pin.UNSPEC,do_erc=True)]),
        Part(name='C_3x1.5mm2',dest=TEMPLATE,tool=SKIDL,keywords='Cable',description='Cable 3 conducteurs 1,5 mm2',ref_prefix='EC',num_units=1,do_erc=True,pins=[
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='C_3x2.5mm2',dest=TEMPLATE,tool=SKIDL,keywords='Cable',description='Cable 3 conducteurs 2,5 mm2',ref_prefix='EC',num_units=1,do_erc=True,pins=[
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='C_3x6mm2',dest=TEMPLATE,tool=SKIDL,keywords='Cable',description='Cable 3 conducteurs 6 mm2',ref_prefix='EC',num_units=1,do_erc=True,pins=[
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='D_06A',dest=TEMPLATE,tool=SKIDL,keywords='Disjoncteur',description='Disjoncteur thermique 6A',ref_prefix='ED',num_units=1,do_erc=True,pins=[
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='D_10A',dest=TEMPLATE,tool=SKIDL,keywords='Disjoncteur',description='Disjoncteur thermique 10A',ref_prefix='ED',num_units=1,do_erc=True,pins=[
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='D_16A',dest=TEMPLATE,tool=SKIDL,keywords='Disjoncteur',description='Disjoncteur thermique 16A',ref_prefix='ED',num_units=1,do_erc=True,pins=[
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='D_32A',dest=TEMPLATE,tool=SKIDL,keywords='Disjoncteur',description='Disjoncteur thermique 32A',ref_prefix='ED',num_units=1,do_erc=True,pins=[
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='E_09W',dest=TEMPLATE,tool=SKIDL,keywords='Eclairage',description='Eclairage 9W (basse consommation)',ref_prefix='EE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='F_10A',dest=TEMPLATE,tool=SKIDL,keywords='Fusible',description='Fusible 10A',ref_prefix='EF',num_units=1,do_erc=True,pins=[
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='G_Th_3KVA',dest=TEMPLATE,tool=SKIDL,keywords='Groupe',description='Groupe electrogene diesel 3KVA',ref_prefix='EG',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWROUT,do_erc=True)]),
        Part(name='I_25A_LUM',dest=TEMPLATE,tool=SKIDL,keywords='Interrupteur',description='Interrupteur 6A',ref_prefix='EI',num_units=1,do_erc=True,pins=[
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='I_6A',dest=TEMPLATE,tool=SKIDL,keywords='Interrupteur',description='Interrupteur 6A',ref_prefix='EI',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True)]),
        Part(name='J_40A_30mA',dest=TEMPLATE,tool=SKIDL,keywords='Interrupteur',description='Interrupteur 40A differentiel 30mA avec signalisation',ref_prefix='EJ',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='3',name='~',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='M_1.5KVA',dest=TEMPLATE,tool=SKIDL,keywords='Moteur',description='Moteur electrique 1,5 KVA',ref_prefix='EM',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='O_600VA',dest=TEMPLATE,tool=SKIDL,keywords='Onduleur',description='Onduleur 600VA batterie 24V 48A (1100W)',ref_prefix='EO',num_units=1,do_erc=True,pins=[
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='O_900VA',dest=TEMPLATE,tool=SKIDL,keywords='Onduleur',description='Onduleur 900VA batterie 24V 48A (1100W)',ref_prefix='EO',num_units=1,do_erc=True,pins=[
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='P_10A',dest=TEMPLATE,tool=SKIDL,keywords='Prise',description='Prise 10A',ref_prefix='EP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='P_10A_LUM',dest=TEMPLATE,tool=SKIDL,keywords='Prise',description='Prise 10A avec temoin',ref_prefix='EP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='P_10A_ROU',dest=TEMPLATE,tool=SKIDL,keywords='Prise',description='Prise 10A rouge (circuit protege)',ref_prefix='EP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='P_16A',dest=TEMPLATE,tool=SKIDL,keywords='Prise',description='Prise 16A',ref_prefix='EP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='Q_25A_2F2O',dest=TEMPLATE,tool=SKIDL,keywords='Contacteur',description='Contacteur 25A 2 fermes et 2 ouverts avec signalisation',ref_prefix='EQ',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='2',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='3',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='4',name='~',do_erc=True),
            Pin(num='5',name='~',func=Pin.UNSPEC,do_erc=True)]),
        Part(name='Q_2A_12O_40KV',dest=TEMPLATE,tool=SKIDL,keywords='Contacteur',description='Contacteur 2A 12 ouverts a grand cartement 40000V',ref_prefix='EQ',num_units=1,do_erc=True,pins=[
            Pin(num='22',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='18',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='7',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='23',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='14',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='19',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='10',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='11',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='6',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='15',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='24',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='20',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='16',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='12',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='8',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='4',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='21',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='17',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='13',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='9',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='5',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='3',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='2',name='~',func=Pin.UNSPEC,do_erc=True),
            Pin(num='25',name='~',do_erc=True),
            Pin(num='1',name='~',func=Pin.UNSPEC,do_erc=True)]),
        Part(name='R_16A_30mA',dest=TEMPLATE,tool=SKIDL,keywords='Disjoncteur',description='Disjoncteur 16A differentiel 30mA avec motorisation et signalisation',ref_prefix='ER',num_units=1,do_erc=True,pins=[
            Pin(num='3',name='~',func=Pin.OUTPUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='4',name='~',do_erc=True)]),
        Part(name='R_45A_500mA',dest=TEMPLATE,tool=SKIDL,keywords='Disjoncteur',description='Disjoncteur 45A differentiel 500mA avec motorisation et signalisation',ref_prefix='ER',num_units=1,do_erc=True,pins=[
            Pin(num='3',name='~',func=Pin.OUTPUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='4',name='~',do_erc=True)]),
        Part(name='S_63A',dest=TEMPLATE,tool=SKIDL,keywords='Sectionneur',description='Sectionneur 63A avec signalisation',ref_prefix='ES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='3',name='~',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='V_A10A',dest=TEMPLATE,tool=SKIDL,keywords='Mesure',description='Amperemetre 10A',ref_prefix='EV',num_units=1,do_erc=True,pins=[
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='V_F50Hz',dest=TEMPLATE,tool=SKIDL,keywords='Mesure',description='Frequencemetre 50Hz',ref_prefix='EV',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='V_U400V',dest=TEMPLATE,tool=SKIDL,keywords='Mesure',description='Voltmetre 400V',ref_prefix='EV',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='W_15KA',dest=TEMPLATE,tool=SKIDL,keywords='Parafoudre',description='Parafoudre 15 KA avec signalisation',ref_prefix='EW',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='3',name='~',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='W_40KA',dest=TEMPLATE,tool=SKIDL,keywords='Parafoudre',description='Parafoudre 40KA avec signalisation',ref_prefix='EW',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='3',name='~',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='W_65KA',dest=TEMPLATE,tool=SKIDL,keywords='Parafoudre',description='Parafoudre 65KA avec signalisation',ref_prefix='EW',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True),
            Pin(num='3',name='~',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='X_Sati',dest=TEMPLATE,tool=SKIDL,keywords='Secours',description='Bloc de secours SATI',ref_prefix='EX',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='Y_ELC',dest=TEMPLATE,tool=SKIDL,keywords='Terre',description='Terre electrique',ref_prefix='EY',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='Y_RAD',dest=TEMPLATE,tool=SKIDL,keywords='Terre',description='Terre radio',ref_prefix='EY',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True)])])
