from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

transistors = SchLib(tool=SKIDL).add_parts(*[
        Part(name='2N2219',dest=TEMPLATE,tool=SKIDL,keywords='NPN transistor',description='Vce 60V, Ic 1000mA, NPN Transistor, TO-39',ref_prefix='Q',num_units=1,fplist=['TO?39*'],do_erc=True,aliases=['BC140', 'BC141'],pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='2N2646',dest=TEMPLATE,tool=SKIDL,keywords='UJT',description='Unijunction transistor',ref_prefix='Q',num_units=1,fplist=['TO?18*'],do_erc=True,aliases=['2N2647'],pins=[
            Pin(num='1',name='B2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',do_erc=True),
            Pin(num='3',name='B1',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='2N3055',dest=TEMPLATE,tool=SKIDL,keywords='NPN power transistor',description='60V Vce, 15A Ic, NPN, Power Transistor, TO-3',ref_prefix='Q',num_units=1,fplist=['TO?3*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='2N3904',dest=TEMPLATE,tool=SKIDL,keywords='NPN Transistor',description='40V Vce, 0.2A Ic, NPN, Small Signal Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='2N3906',dest=TEMPLATE,tool=SKIDL,keywords='PNP Transistor',description='-40V Vce, -0.2A Ic, PNP, Small Signal Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,aliases=['2N3905'],pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='2N7000',dest=TEMPLATE,tool=SKIDL,keywords='P-Channel MOSFET',description='-60V Vds, -0.18A Id, P-Channel MOSFET, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,aliases=['TP0610L', 'VP0610L'],pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='2SA1015',dest=TEMPLATE,tool=SKIDL,keywords='Low Noise Audio PNP Transistor',description='-50V Vce, -0.15A Ic, Low Noise Audio PNP Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='2SB631',dest=TEMPLATE,tool=SKIDL,keywords='High Voltage Transistor',description='Vce -100V, Ic -1A, High Voltage Power Transistor, TO-126',ref_prefix='Q',num_units=1,fplist=['TO?126*'],do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='2SB817',dest=TEMPLATE,tool=SKIDL,keywords='Power Transistor PNP',description='-12A Ic, -140V Vce, Silicon Power Transistors PNP, TO-3PB',ref_prefix='Q',num_units=1,fplist=['TO-3PB*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='2SC1815',dest=TEMPLATE,tool=SKIDL,keywords='Low Noise Audio NPN Transistor',description='50V Vce, 0.15A Ic, Low Noise Audio NPN Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='2SC1941',dest=TEMPLATE,tool=SKIDL,keywords='Audio High Voltage NPN Transistor',description='160V Vce, 0.05A Ic, Audio High Voltage NPN Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='2SC1945',dest=TEMPLATE,tool=SKIDL,keywords='RF Power Transistor NPN',description='6A Ic, 80V Vce, Silicon 27MHz RF Power Transistors NPN, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='2SD1047',dest=TEMPLATE,tool=SKIDL,keywords='Power Transistor NPN',description='12A Ic, 140V Vce, Silicon Power Transistors NPN, TO-3PB',ref_prefix='Q',num_units=1,fplist=['TO-3PB*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='2SD600',dest=TEMPLATE,tool=SKIDL,keywords='High Voltage Power Transistor',description='Vce 100V, Ic 1A, High Voltage Power Transistor, TO-126',ref_prefix='Q',num_units=1,fplist=['TO?126*'],do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='3SK263',dest=TEMPLATE,tool=SKIDL,keywords='NMOS Dual Gate',description='30mA Id, 15V Vds, N-Channel Dual Gate MOSFET, SOT-143/343',ref_prefix='Q',num_units=1,fplist=['SOT-143*', 'SOT-343*'],do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='AUIR3315S',dest=TEMPLATE,tool=SKIDL,keywords='Hiside power switch',description='Automotive Q101 Programmable Current Sense High Side Switch in a 5-Lead (TO-263-5) Package',ref_prefix='U',num_units=1,fplist=['TO-263*'],do_erc=True,pins=[
            Pin(num='1',name='IN',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='Ifb',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='Vcc',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='OUT',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='OUT',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC107',dest=TEMPLATE,tool=SKIDL,keywords='NPN low noise transistor',description='25V Vce, 0.2A Ic, NPN, Low Noise General Purpose Transistor, TO-18',ref_prefix='Q',num_units=1,fplist=['TO?18*'],do_erc=True,aliases=['BC108', 'BC109'],pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC160',dest=TEMPLATE,tool=SKIDL,keywords='PNP power transistor',description='60V Vce, 1A Ic, PNP, Power Transistor, TO-39',ref_prefix='Q',num_units=1,fplist=['TO?39*'],do_erc=True,aliases=['BC161'],pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC237',dest=TEMPLATE,tool=SKIDL,keywords='NPN Epitaxial Silicon Transistor',description='Vce 50V, Ic 100mA, NPN Epitaxial Silicon Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC240',dest=TEMPLATE,tool=SKIDL,keywords='NPN RF Transistor',description='40V Vce, 0.05A Ic, NPN, RF Signal Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='BC307',dest=TEMPLATE,tool=SKIDL,keywords='PNP Epitaxial Silicon Transistor',description='Vce 45V, Ic 100mA, PNP Epitaxial Silicon Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC413',dest=TEMPLATE,tool=SKIDL,keywords='NPN Transistor',description='45V Vce, 0.1A Ic, NPN, Small Signal Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,aliases=['BC413B', 'BC413C', 'BC414', 'BC414B', 'BC414C'],pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC516',dest=TEMPLATE,tool=SKIDL,keywords='PNP Darlington Darl Transistor',description='30V Vce, 1A Ic, PNP Darlington Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC517',dest=TEMPLATE,tool=SKIDL,keywords='NPN Darlington Darl Transistor',description='30V Vce, 1A Ic, NPN Darlington Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC547',dest=TEMPLATE,tool=SKIDL,keywords='NPN Transistor',description='45V Vce, 0.1A Ic, NPN, Small Signal Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,aliases=['BC546', 'BC548', 'BC549', 'BC550', 'BC337', 'BC338'],pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC557',dest=TEMPLATE,tool=SKIDL,keywords='PNP Transistor',description='45V Vce, 0.1A Ic, PNP Small Signal Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,aliases=['BC556', 'BC558', 'BC559', 'BC560', 'BC327', 'BC328'],pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC636',dest=TEMPLATE,tool=SKIDL,keywords='PNP Transistor',description='45V Vce, 1A Ic, PNP Medium Power Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='BC807',dest=TEMPLATE,tool=SKIDL,keywords='PNP Transistor',description='-40V Vce, -0.2A Ic, PNP, Small Signal Transistor, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*'],do_erc=True,aliases=['BC808', 'BC856', 'BC857', 'BC858', 'BC859', 'BC860', 'MMBT3906'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC807W',dest=TEMPLATE,tool=SKIDL,keywords='PNP Transistor',description='45V Vce, 0.1A Ic, PNP Small Signal Transistor, SOT-323',ref_prefix='Q',num_units=1,fplist=['SOT?323*'],do_erc=True,aliases=['BC808W', 'BC856W', 'BC857W', 'BC858W', 'BC859W', 'BC860W'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC817',dest=TEMPLATE,tool=SKIDL,keywords='NPN Transistor',description='40V Vce, 0.2A Ic, NPN, Small Signal Transistor, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*'],do_erc=True,aliases=['BC818', 'BC847', 'BC848', 'BC849', 'BC850', 'MMBT3904'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC817W',dest=TEMPLATE,tool=SKIDL,keywords='NPN Small Signal Transistor',description='45V Vce, 0.1A Ic, NPN, SOT-323',ref_prefix='Q',num_units=1,fplist=['SOT?323*'],do_erc=True,aliases=['BC818W', 'BC847W', 'BC848W', 'BC849W', 'BC850W'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BC846BPN',dest=TEMPLATE,tool=SKIDL,keywords='Transistor NPN/PNP',description='40V Vce, 200mA IC, Dual NPN/PNP Transistors, SOT-363',ref_prefix='Q',num_units=2,fplist=['SC?70*', 'SC?88*', 'SOT?363*'],do_erc=True,aliases=['BC846BPDW1', 'BC847BPN', 'BC847BPDW1', 'PMBT3946YPN', 'MMDT3946', 'MBT3946DW1T1', 'FFB3946'],pins=[
            Pin(num='1',name='E1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B1',do_erc=True),
            Pin(num='6',name='C1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='E2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='B2',do_erc=True)]),
        Part(name='BC846BS',dest=TEMPLATE,tool=SKIDL,keywords='Transistor NPN/NPN',description='40V Vce, 200mA IC, Dual NPN/NPN Transistors, SOT-363',ref_prefix='Q',num_units=2,fplist=['SC?70*', 'SC?88*', 'SOT?363*'],do_erc=True,aliases=['BC846BDW1', 'BC847BS', 'BC847BDW1', 'PMBT2222AYS', 'MMDT2222A', 'MBT2222ADW1T1', 'FFB2222A', 'PMBT3904YS', 'MMDT3904', 'MBT3904DW1', 'FFB3904', 'MMDT5551', 'FFB5551'],pins=[
            Pin(num='1',name='E1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B1',do_erc=True),
            Pin(num='6',name='C1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='E2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='B2',do_erc=True)]),
        Part(name='BC856BS',dest=TEMPLATE,tool=SKIDL,keywords='Transistor PNP/PNP',description='40V Vce, 200mA IC, Dual PNP/PNP Transistors, SOT-363',ref_prefix='Q',num_units=2,fplist=['SC?70*', 'SC?88*', 'SOT?363*'],do_erc=True,aliases=['BC856BDW1', 'BC857BS', 'BC857BDW1', 'PMBT3906YS', 'MMDT3906', 'MBT3906DW1', 'FFB3906', 'MMDT5401'],pins=[
            Pin(num='1',name='E1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B1',do_erc=True),
            Pin(num='6',name='C1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='E2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='B2',do_erc=True)]),
        Part(name='BCP51',dest=TEMPLATE,tool=SKIDL,keywords='PNP Transistor',description='45V Vce, 1A Ic, PNP Medium Power Transistor, SOT-223',ref_prefix='Q',num_units=1,fplist=['SOT?223*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BCV61',dest=TEMPLATE,tool=SKIDL,keywords='Transistor Double NPN',description='30V Vce, 100mA IC, Double NPN Transistors, Current mirror configuration, SOT-143',ref_prefix='Q',num_units=1,fplist=['SOT?143*'],do_erc=True,pins=[
            Pin(num='1',name='C2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='E2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BCV62',dest=TEMPLATE,tool=SKIDL,keywords='Transistor Double PNP',description='30V Vce, 100mA IC, Double PNP Transistors, Current mirror configuration, SOT-143',ref_prefix='Q',num_units=1,fplist=['SOT?143*'],do_erc=True,pins=[
            Pin(num='1',name='C2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='E2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BCX51',dest=TEMPLATE,tool=SKIDL,keywords='PNP Transistor',description='80V Vce, 1A Ic, PNP Medium Power Transistor, SOT-89',ref_prefix='Q',num_units=1,fplist=['SOT?89*'],do_erc=True,aliases=['BCX52', 'BCX53'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BCX56',dest=TEMPLATE,tool=SKIDL,keywords='NPN Transistor',description='80V Vce, 1A Ic, NPN Medium Power Transistor, SOT-89',ref_prefix='Q',num_units=1,fplist=['SOT?89*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BD139',dest=TEMPLATE,tool=SKIDL,keywords='Low Voltage Transistor',description='Vce 80V, Ic 2A, Low Voltage Transistor, TO-126',ref_prefix='Q',num_units=1,fplist=['TO?126*'],do_erc=True,aliases=['BD135', 'BD137', 'BD233', 'BD235', 'BD237'],pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='BD140',dest=TEMPLATE,tool=SKIDL,keywords='Low Voltage Transistor',description='Vce 80V, Ic 2A, Low Voltage Transistor, TO-126',ref_prefix='Q',num_units=1,fplist=['TO?126*'],do_erc=True,aliases=['BD136', 'BD138', 'BD234', 'BD236', 'BD238'],pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='BD249',dest=TEMPLATE,tool=SKIDL,keywords='Power Transistor NPN',description='25A Ic, 115V Vce, Silicon Power Transistors NPN, SOT-93',ref_prefix='Q',num_units=1,fplist=['SOT?93*'],do_erc=True,aliases=['BD249A', 'BD249B', 'BD249C'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BD250',dest=TEMPLATE,tool=SKIDL,keywords='Power Transistor PNP',description='25A Ic, 115V Vce, Silicon Power Transistors PNP, SOT-93',ref_prefix='Q',num_units=1,fplist=['SOT?93*'],do_erc=True,aliases=['BD250A', 'BD250B', 'BD250C'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BD433',dest=TEMPLATE,tool=SKIDL,keywords='NPN Power Transistor',description='80V Vce, 4A Ic, NPN Power Transistor, TO-126',ref_prefix='Q',num_units=1,fplist=['TO?126*'],do_erc=True,aliases=['BD435', 'BD437', 'BD439', 'BD441'],pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='BD434',dest=TEMPLATE,tool=SKIDL,keywords='PNP Power Transistor',description='80V Vce, 4A Ic, PNP Power Transistor, TO-126',ref_prefix='Q',num_units=1,fplist=['TO?126*'],do_erc=True,aliases=['BD436', 'BD438', 'BD440', 'BD442'],pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='BD910',dest=TEMPLATE,tool=SKIDL,keywords='PNP power transistor',description='-100V Vce, -6A Ic, PNP, Power Transistor, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['BD912', 'TIP42', 'TIP42A', 'TIP42B', 'TIP42C'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BD911',dest=TEMPLATE,tool=SKIDL,keywords='NPN power transistor',description='100V Vce, 6A Ic, NPN, Power Transistor, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['BD909', 'TIP41A', 'TIP41B', 'TIP41C', 'TIP41'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BDW93',dest=TEMPLATE,tool=SKIDL,keywords='NPN Darlington Transistor',description='100V Vce, 12A Ic, NPN Power Darlington Transistor, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['BDW93A', 'BDW93B', 'BDW93C'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BDW94',dest=TEMPLATE,tool=SKIDL,keywords='PNP Darlington Transistor',description='100V Vce, 12A Ic, PNP Power Darlington Transistor, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['BDW94A', 'BDW94B', 'BDW94C'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BF199',dest=TEMPLATE,tool=SKIDL,keywords='NPN RF Transistor',description='25V Vce, 0.05A Ic, NPN Radio Frequency Transistor, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='BF244A',dest=TEMPLATE,tool=SKIDL,keywords='N-Channel FET Transistor Low Voltage',description='30V Vgs, 0.05A Id, N-Cannel FET Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,aliases=['BF244B', 'BF244C'],pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='BF245A',dest=TEMPLATE,tool=SKIDL,keywords='N-Channel FET Transistor Low Voltage',description='30V Vgs, 0.01A Id, N-Cannel FET Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,aliases=['BF245B', 'BF245C'],pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BF457',dest=TEMPLATE,tool=SKIDL,keywords='NPN HV High Voltage Transistor',description='300V Vce, 0.1A Ic, NPN, High Voltage Transistor, TO-126',ref_prefix='Q',num_units=1,fplist=['TO?126*'],do_erc=True,aliases=['BF458', 'BF459'],pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='BFR92',dest=TEMPLATE,tool=SKIDL,keywords='RF 5GHz NPN Transistor',description='15V Vce, 0.025A Ic, NPN 5GHz Wideband Transistor, SOT-323',ref_prefix='Q',num_units=1,fplist=['SOT?323*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BFT92',dest=TEMPLATE,tool=SKIDL,keywords='RF 5GHz NPN Transistor',description='15V Vce, 0.025A Ic, PNP 5GHz Wideband Transistor, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BS107',dest=TEMPLATE,tool=SKIDL,keywords='N-Channel MOSFET',description='60V Vds 0.5A Id, N-Channel MOSFET, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,aliases=['BS108', 'BS170'],pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BS250',dest=TEMPLATE,tool=SKIDL,keywords='P-Channel MOSFET',description='-60V Vds, -0.18A Id, P-Channel MOSFET, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BSS138',dest=TEMPLATE,tool=SKIDL,keywords='P-Channel MOSFET',description='-60V Vds, -0.18A Id, P-Channel MOSFET, SOT-23-3',ref_prefix='Q',num_units=1,fplist=['SOT?23*'],do_erc=True,aliases=['2N7002', 'TP0610T', 'VP0610T'],pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BUT11',dest=TEMPLATE,tool=SKIDL,keywords='High Voltage Power Transistor NPN',description='5A 450V, Silicon Power Transistors NPN, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['BUT11A'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BUZ11',dest=TEMPLATE,tool=SKIDL,keywords='Single N-Channel HEXFET Power MOSFET',description='47A Id, 55V Vds, 22mOhm Rds, Single N-Channel HEXFET Power MOSFET in a TO-220AB package',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['IRLZ44N', 'IRLIZ44N', 'IRLZ34N', 'IRF3205', 'IRF540N'],pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CSD17578Q5A',dest=TEMPLATE,tool=SKIDL,keywords='NexFET Power MOSFET N-MOS',description='NexFET N-Channel Power MOSFET, Vds 100V, Rdson 15.1mOhm, Id 50A, Qg (typ) 17nC, SON8 5x6mm',ref_prefix='Q',num_units=1,fplist=['TDSON*'],do_erc=True,aliases=['CSD17579Q5A', 'CSD16570Q5B', 'CSD17577Q5A', 'CSD18509Q5B', 'CSD18540Q5B', 'CSD17573Q5B', 'CSD17576Q5B', 'CSD19534Q5A', 'CSD17570Q5B', 'CSD19533Q5A', 'CSD19502Q5B', 'CSD19532Q5B', 'CSD19531Q5A', 'CSD18563Q5A', 'CSD18537NQ5A', 'CSD18532NQ5B', 'CSD17556Q5B', 'CSD18502Q5B', 'CSD18532Q5B', 'CSD17552Q5A', 'CSD17559Q5', 'CSD18534Q5A', 'CSD18533Q5A', 'CSD17555Q5A', 'CSD17551Q5A', 'CSD18501Q5A', 'CSD18503Q5A', 'CSD18504Q5A', 'CSD18531Q5A', 'CSD17553Q5A', 'CSD16342Q5A', 'CSD17322Q5A', 'CSD17327Q5A', 'CSD17522Q5A', 'CSD17527Q5A', 'CSD17501Q5A', 'CSD17506Q5A', 'CSD17505Q5A', 'CSD17507Q5A', 'CSD17510Q5A', 'CSD17311Q5', 'CSD17312Q5', 'CSD17303Q5', 'CSD16415Q5', 'CSD17302Q5A', 'CSD17305Q5A', 'CSD17306Q5A', 'CSD17307Q5A', 'CSD17310Q5A', 'CSD17301Q5A', 'CSD16408Q5', 'CSD16322Q5', 'CSD16325Q5', 'CSD16321Q5', 'CSD16414Q5', 'CSD16401Q5', 'CSD16403Q5A', 'CSD16404Q5A', 'CSD16407Q5', 'CSD16410Q5A', 'CSD16412Q5A', 'CSD16413Q5A', 'BSC026N08NS5ATMA1', 'BSC030N08NS5ATMA1', 'BSC035N10NS5ATMA1', 'BSC037N08NS5ATMA1', 'BSC040N10NS5ATMA1', 'BSC040N08NS5ATMA1', 'BSC046N10NS3GATMA1', 'BSC047N08NS3GATMA1', 'BSC052N08NS5ATMA1', 'BSC057N08NS3GATMA1', 'BSC060N10NS3GATMA1', 'BSC061N08NS5ATMA1', 'BSC070N10NS3GATMA1', 'BSC070N10NS5ATMA1', 'BSC072N08NS5ATMA1', 'BSC079N10NSGATMA1', 'BSC082N10LSGATMA1', 'BSC098N10NS5ATMA1', 'BSC100N10NSFGATMA1', 'BSC105N10LSFGATMA1', 'BSC109N10NS3GATMA1', 'BSC117N08NS5ATMA1', 'BSC118N10NSGATMA1', 'BSC123N08NS3GATMA1', 'BSC123N10LSGATMA1', 'BSC159N10LSFGATMA1', 'BSC160N10NS3GATMA1', 'BSC196N10NSGATMA1', 'BSC252N10NSFGATMA1', 'BSC265N10LSFGATMA1', 'BSC340N08NS3GATMA1', 'BSC440N10NS3GATMA1', 'BSC028N06LS3'],pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CSD19537Q3',dest=TEMPLATE,tool=SKIDL,keywords='NexFET Power MOSFET N-MOS',description='NexFET N-Channel Power MOSFET, Vds 100V, Rdson 13mOhm, Id 50A, Qg Typ 16.0nC, VSON8 3.3x3.3mm',ref_prefix='Q',num_units=1,fplist=['SON*3.3x3.3mm*Pitch0.65mm*'],do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA113T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 1k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA113Z',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 1k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA114E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA114G',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 0k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA114T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA114W',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/4.7k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA114Y',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA115E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='DTA114E, Digital Transistor, 100k/100k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA115G',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 0k/100k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA115T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 100k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA115U',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='DTA114U, Digital Transistor, 100k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA123E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k2/2k2, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA123J',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k2/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA123Y',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k2/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA124E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 22k/22k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA124G',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 0k/22k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA124T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 22k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA124X',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 22k/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA125T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 200k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA143E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 4k7/4k7, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA143T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 4k7/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA143X',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 4k7/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA143Y',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 4k7/22k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA143Z',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 4k7/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA144E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 47k/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA144G',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 0k/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA144T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 47k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA144V',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 47k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA144W',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 47k/22k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA1D3R',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k7/1k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTA214Y',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTB113E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 1k/1k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTB113Z',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 1k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTB114E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTB114G',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 0k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTB114T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTB122J',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 0k22/4k7, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTB123E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k2/2k2, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTB123T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k2/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTB123Y',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k2/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTB133H',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 3k3/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTB143T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 4k7/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTB163T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 6k8/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC113T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 1k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC113Z',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 1k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC114E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC114G',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 0k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC114T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC114W',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/4k7, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC114Y',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC115E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 100k/100k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC115G',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 0k/100k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC115T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 100k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC115U',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 100k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC123E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k2/2k2, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC123J',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k2/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC123Y',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k2/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC124E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 22k/22k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC124G',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 0k/22k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC124T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 22k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC124X',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 22k/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC125T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 200k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC143E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 4k7/4k7, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC143T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 4k7/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC143X',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 4k7/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC143Y',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 4k7/22k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC143Z',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 4k7/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC144E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 47k/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC144G',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 0k/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC144T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 47k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC144V',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 47k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC144W',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 47k/22k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC1D3R',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k7/1k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTC214Y',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/47k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTD113E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 1k/1k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTD113Z',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 1k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTD114E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTD114G',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 0k/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTD114T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 10k/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTD122J',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 0k22/4k7, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTD123E',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k2/2k2, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTD123T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k2/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTD123Y',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 2k2/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTD133H',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 3k3/10k, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTD143T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 4k7/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DTD163T',dest=TEMPLATE,tool=SKIDL,keywords='ROHM Digital Transistor',description='Digital Transistor, 6k8/NONE, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*', 'SC-59*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='FDG1024NZ',dest=TEMPLATE,tool=SKIDL,keywords='Dual N-Channel MOSFET Logic Level',description='20V Vds, 1.2A Id, 175mOhm Rds, Dual N-Channel MOSFET, SC-70-6',ref_prefix='Q',num_units=2,fplist=['*SC-70*'],do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='G',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='FDMS8350LET40',dest=TEMPLATE,tool=SKIDL,keywords='dual-cool-powertrench mosfet fairchild',description='N-Channel Dual Cool PowerTrench MOSFET, Vds=80V, Rds=1.35mΩ, Id(const)=36A, Qg(max)=273nC, Temp=-55 to 150 °C, SON8 5x6mm package',ref_prefix='Q',num_units=1,fplist=['SON*'],do_erc=True,aliases=['FDMT80060DC', 'FDMT80080DC', 'FDMT800120DC', 'FDMT800100DC', 'FDMT800150DC', 'FDMT800152DC', 'FDMS8050ET30', 'FDMS86202ET120', 'FDMS86150ET100', 'FDMS86255ET150', 'FDMS86350ET80', 'FDMS86550ET60', 'FDMS8050', 'FDMS8350L', 'FDMS86255', 'FDMS86550', 'FDMS86202', 'FDMS86350', 'FDMS86152', 'FDMS86150'],pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='FDS6890A',dest=TEMPLATE,tool=SKIDL,keywords='Dual N-Channel MOSFET',description='20V Vds, 6.5A Id, 30mOhm Rds, Dual N-Channel MOSFET, SO-8',ref_prefix='Q',num_units=2,fplist=['SOIC*3.9x4.9mm*Pitch1.27mm*'],do_erc=True,aliases=['FDS6892A', 'FDS6898A', 'FDS9926A'],pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='FDS9934C',dest=TEMPLATE,tool=SKIDL,keywords='Dual N-Channel P-Channel MOSFET',description='Dual N and P Channel MOSFET, 30V Vds, 6A Id, 28mΩ Rds @ 10V Vgs, SO8L',ref_prefix='Q',num_units=2,fplist=['SOIC*3.9x4.9mm*Pitch1.27mm*'],do_erc=True,aliases=['Si4542DY', 'FDS4559', 'Si4532DY', 'FDS4897AC', 'FDS4897C', 'FDS8960C'],pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='7',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G',do_erc=True),
            Pin(num='5',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='IPS6011PBF',dest=TEMPLATE,tool=SKIDL,keywords='Intelligent Power Switch High Side MOSFET',description='39V, 5A, Intelligent Power Switch High Side, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['IPS6021PBF', 'IPS6031PBF', 'IPS6041PBF'],pins=[
            Pin(num='1',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='IN',do_erc=True),
            Pin(num='3',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='DG',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='OUT',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='IPS6011RPBF',dest=TEMPLATE,tool=SKIDL,keywords='Intelligent Power Switch High Side MOSFET',description='39V, 5A, Intelligent Power Switch High Side, DPAK 5pin',ref_prefix='Q',num_units=1,do_erc=True,aliases=['IPS6021RPBF', 'IPS6031RPBF', 'IPS6041RPBF'],pins=[
            Pin(num='1',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='IN',do_erc=True),
            Pin(num='3',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='DG',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='OUT',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='IPS6011SPBF',dest=TEMPLATE,tool=SKIDL,keywords='Intelligent Power Switch High Side MOSFET',description='39V, 5A, Intelligent Power Switch High Side, D2PAK 5pin',ref_prefix='Q',num_units=1,do_erc=True,aliases=['IPS6021SPBF', 'IPS6031SPBF', 'IPS6041SPBF'],pins=[
            Pin(num='1',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='IN',do_erc=True),
            Pin(num='3',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='DG',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='OUT',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='IPS6041GPBF',dest=TEMPLATE,tool=SKIDL,keywords='Intelligent Power Switch High Side MOSFET',description='39V, 5A, Intelligent Power Switch High Side, SO-8',ref_prefix='Q',num_units=1,fplist=['SOIC*3.9x4.9mm*Pitch1.27mm*'],do_erc=True,pins=[
            Pin(num='1',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='IN',do_erc=True),
            Pin(num='3',name='DG',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='5',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='6',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='7',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='IPS7091GPBF',dest=TEMPLATE,tool=SKIDL,keywords='Intelligent Power Switch High Side MOSFET',description='70V, 5A, Intelligent Power Switch High Side, D2-PAK 5pin',ref_prefix='Q',num_units=1,fplist=['SOIC*3.9x4.9mm*Pitch1.27mm*'],do_erc=True,pins=[
            Pin(num='1',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='IN',do_erc=True),
            Pin(num='3',name='DG',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='OUT',func=Pin.OUTPUT,do_erc=True),
            Pin(num='5',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='6',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='7',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='~',func=Pin.PWRIN,do_erc=True)]),
        Part(name='IPS7091PBF',dest=TEMPLATE,tool=SKIDL,keywords='Intelligent Power Switch High Side MOSFET',description='70V, 5A, Intelligent Power Switch High Side, TO-220-5',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,pins=[
            Pin(num='1',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='IN',do_erc=True),
            Pin(num='3',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='DG',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='OUT',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='IPS7091SPBF',dest=TEMPLATE,tool=SKIDL,keywords='Intelligent Power Switch High Side MOSFET',description='70V, 5A, Intelligent Power Switch High Side, D2-PAK 5pin',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='IN',do_erc=True),
            Pin(num='3',name='VCC',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='DG',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='OUT',func=Pin.OUTPUT,do_erc=True)]),
        Part(name='IPT012N08N5ATMA1',dest=TEMPLATE,tool=SKIDL,keywords='OptiMOS Power MOSFET N-MOS',description='OptiMOS N-Channel Power MOSFET, Vds 100V, Rdson 2.0mOhm, Id 300A, Qg (typ) 156.0nC, PG-HSOF-8',ref_prefix='Q',num_units=1,do_erc=True,aliases=['IPT015N10N5ATMA1', 'IPT020N10N3ATMA1'],pins=[
            Pin(num='1',name='G',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='IRF7309IPBF',dest=TEMPLATE,tool=SKIDL,keywords='Dual HEXFET N-Channel P-Channel MOSFET',description='30V Vds, 3A Id, Dual HEXFET MOSFET, SO-8',ref_prefix='Q',num_units=2,fplist=['SOIC*3.9x4.9mm*Pitch1.27mm*'],do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='7',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G',do_erc=True),
            Pin(num='5',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='IRF7324',dest=TEMPLATE,tool=SKIDL,keywords='Dual HEXFET P-Channel MOSFET',description='-20V Vds, 9A Id, Dual HEXFET P-Channel MOSFET, SO-8',ref_prefix='Q',num_units=2,fplist=['SOIC*3.9x4.9mm*Pitch1.27mm*'],do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='7',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G',do_erc=True),
            Pin(num='5',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='IRF7343PBF',dest=TEMPLATE,tool=SKIDL,keywords='Dual HEXFET N-Channel P-Channel MOSFET',description='55V Vds, 4A Id, Dual HEXFET MOSFET, SO-8',ref_prefix='Q',num_units=2,fplist=['SOIC*3.9x4.9mm*Pitch1.27mm*'],do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='7',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G',do_erc=True),
            Pin(num='5',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='IRF7404',dest=TEMPLATE,tool=SKIDL,keywords='P-Channel MOSFET',description='-20V Vds, -6.7A Id, P-Channel HEXFET Power MOSFET, SO-8',ref_prefix='U',num_units=1,fplist=['SO*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='IRF7606PBF',dest=TEMPLATE,tool=SKIDL,keywords='HexFET Power Mosfet P-MOS',description='HexFET P-MOS Power Mosfet, Vds -30V, Rdson 0.09R, Id -3.6A, Micro8',ref_prefix='Q',num_units=1,fplist=['MSOP*3x3mm?Pitch0.65mm*'],do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='IRF7607PBF',dest=TEMPLATE,tool=SKIDL,keywords='HexFET Power Mosfet N-MOS',description='HexFET N-MOS Power Mosfet, Vds 20V, Rdson 0.03R, Id 5.2A, Micro8',ref_prefix='Q',num_units=1,fplist=['MSOP*3x3mm?Pitch0.65mm*'],do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='IRF8721PBF-1',dest=TEMPLATE,tool=SKIDL,keywords='HEXFET N-Channel MOSFET',description='30V Vds, 14A Id, HEXFET MOSFET, SO-8',ref_prefix='Q',num_units=1,fplist=['SOIC*3.9x4.9mm*Pitch1.27mm*'],do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='G',do_erc=True),
            Pin(num='5',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='IRF9540N',dest=TEMPLATE,tool=SKIDL,keywords='HEXFET P-Channel MOSFET',description='-100V Vds, -23A Id, HEXFET P-Channel MOSFET, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['IRF4905'],pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='IRG4PF50W',dest=TEMPLATE,tool=SKIDL,keywords='N-Channel IGBT Power Transistor',description='28A, 900V, N-Channel IGBT',ref_prefix='Q',num_units=1,fplist=['TO?247*'],do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='IRLB8721PBF',dest=TEMPLATE,tool=SKIDL,keywords='N-Channel HEXFET Power MOSFET',description='30V Vds, 62A Id, N-Channel MOSFET, TO-220',ref_prefix='Q',num_units=1,fplist=['TO-220*'],do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='KTD1624',dest=TEMPLATE,tool=SKIDL,keywords='NPN Switching Transistor',description='EPITAXIAL PLANAR NPN TRANSISTOR, SOT-89',ref_prefix='Q',num_units=1,fplist=['SOT?89*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='MAT02',dest=TEMPLATE,tool=SKIDL,keywords='Precision Dual Monolithic Transistor Low Noise EOL',description='Precision Dual Monolithic Transistor, Low Noise, Low Offset, Vce 40V, Ic 20mA, TO-78',ref_prefix='Q',num_units=2,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='7',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='B',do_erc=True),
            Pin(num='7',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='MJ2955',dest=TEMPLATE,tool=SKIDL,keywords='PNP power transistor',description='-60V Vce, -15A Ic, PNP, Power Transistor, TO-3',ref_prefix='Q',num_units=1,fplist=['TO?3*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='MJE13003',dest=TEMPLATE,tool=SKIDL,keywords='Switching Power High Voltage Transistor NPN',description='1.5A Ic, 400V Vce, Silicon Switching Power Transistor NPN, TO-225',ref_prefix='Q',num_units=1,fplist=['TO?225*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='MJE13007G',dest=TEMPLATE,tool=SKIDL,keywords='Switching Power Transistor NPN',description='12A Ic, 400V Vce, Silicon Switching Power Transistors NPN, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['MJE13005G', 'MJE13009G'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='MMBF170',dest=TEMPLATE,tool=SKIDL,keywords='N-Channel MOSFET',description='60V Vds 0.5A Id, N-Channel MOSFET, SOT-23',ref_prefix='Q',num_units=1,fplist=['SOT?23*'],do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='MPSA42',dest=TEMPLATE,tool=SKIDL,keywords='NPN High Voltage Transistor',description='Vce 300V, Ic 500mA, NPN High Voltage Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='MPSA92',dest=TEMPLATE,tool=SKIDL,keywords='PNP High Voltage Transistor',description='Vce 300V, Ic 500mA, PNP High Voltage Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='PN2222A',dest=TEMPLATE,tool=SKIDL,keywords='NPN Transistor',description='40V Vce, 1A Ic, NPN, General Purpose Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='PZT2222A',dest=TEMPLATE,tool=SKIDL,keywords='NPN General Puprose Transistor SMD',description='40V Vce, 1A Ic, NPN, General Purpose Transistor, SOT-223',ref_prefix='Q',num_units=1,fplist=['SOT?223*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='PZT3904',dest=TEMPLATE,tool=SKIDL,keywords='NPN Transistor',description='40V Vce, 0.2A Ic, NPN, Small Signal Transistor, SOT-223',ref_prefix='Q',num_units=1,fplist=['SOT?223*'],do_erc=True,aliases=['BCP56'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='PZT3906',dest=TEMPLATE,tool=SKIDL,keywords='PNP Transistor',description='-40V Vce, -0.2A Ic, PNP, Small Signal Transistor, SOT-223',ref_prefix='Q',num_units=1,fplist=['SOT?223*'],do_erc=True,aliases=['BCP53'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='PZTA42',dest=TEMPLATE,tool=SKIDL,keywords='NPN High Voltage Transistor SMD',description='300V Vce, 0.2A Ic, NPN, High Voltage Transistor, SOT-223',ref_prefix='Q',num_units=1,fplist=['SOT?223*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='S8050',dest=TEMPLATE,tool=SKIDL,keywords='S8050 NPN Low Voltage High Current Transistor',description='20V Vce, 0.7A Ic, NPN, Low Voltage High Current Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='S8550',dest=TEMPLATE,tool=SKIDL,keywords='S8550 PNP Low Voltage High Current Transistor',description='20V Vce, 0.7A Ic, PNP Low Voltage High Current Transistor, TO-92',ref_prefix='Q',num_units=1,fplist=['TO?92*'],do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='TIP120',dest=TEMPLATE,tool=SKIDL,keywords='Darlington Power Transistor NPN',description='5A Ic, 100V Vce, Silicon Darlington Power Transistor NPN, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['TIP121', 'TIP122'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='TIP125',dest=TEMPLATE,tool=SKIDL,keywords='Darlington Power Transistor PNP',description='5A Ic, 100V Vce, Silicon Darlington Power Transistor PNP, TO-220',ref_prefix='Q',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['TIP126', 'TIP127'],pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='TIP2955',dest=TEMPLATE,tool=SKIDL,keywords='PNP power transistor',description='-60V Vce, -15A Ic, PNP, Power Transistor, TO-218/TO-247',ref_prefix='Q',num_units=1,fplist=['TO?247*', 'TO?218*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='TIP3055',dest=TEMPLATE,tool=SKIDL,keywords='NPN power transistor',description='60V Vce, 15A Ic, NPN, Power Transistor, TO-218/TO-247',ref_prefix='Q',num_units=1,fplist=['TO?247*', 'TO?218*'],do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)])])
