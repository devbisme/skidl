from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

diode = SchLib(tool=SKIDL).add_parts(*[
        Part(name='1N4001',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='1000V 1A Fast recovery Rectifier Diode, DO-41',ref_prefix='D',num_units=1,fplist=['D*DO?41*', 'D*DO?204AL*', 'D*SOD81*'],do_erc=True,aliases=['1N4002', '1N4003', '1N4004', '1N4005', '1N4006', '1N4007', 'BA157', 'BA158', 'BA159'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='1N4148',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='20V 0.115A Very Fast Switching Diode, DO-35',ref_prefix='D',num_units=1,fplist=['D*DO?35*', 'D*SOD27*'],do_erc=True,aliases=['1N4448', '1N4149', '1N4151', '1N914', 'BA243', 'BA244', 'BA282', 'BA283', 'BAV17', 'BAV18', 'BAV19', 'BAV20', 'BAV21', 'BAW75', 'BAW76', 'BAY93'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='1N5400',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='1000V 3A Soft Recovery Ultrafast Rectifier Diode, DO-201AD',ref_prefix='D',num_units=1,fplist=['D*DO?201AD*'],do_erc=True,aliases=['1N5401', '1N5402', '1N5404', '1N5405', '1N5406', '1N5407', '1N5408', 'UF5400', 'UF5401', 'UF5402', 'UF5403', 'UF5404', 'UF5405', 'UF5406', 'UF5407', 'UF5408', '1N5403'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='1N5820',dest=TEMPLATE,tool=SKIDL,keywords='diode Schottky',description='40V 3A Schottky Barrier Rectifier Diode, DO-201AD',ref_prefix='D',num_units=1,fplist=['D*DO?201AD*'],do_erc=True,aliases=['1N5821', '1N5822', 'MBR340'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='1N6263',dest=TEMPLATE,tool=SKIDL,keywords='diode Schottky',description='50V 0.2A Small Signal Schottky Diode, DO-35',ref_prefix='D',num_units=1,fplist=['D*SOD23*', 'D*DO?35*'],do_erc=True,aliases=['BAT41', 'BAT42', 'BAT43', 'BAT46', 'BAT48RL', 'BAT85', 'BAT86S', 'BAT86'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='B120-E3',dest=TEMPLATE,tool=SKIDL,keywords='diode Schottky',description='60V 1A Schottky Barrier Rectifier Diode, SMA/DO-214AC',ref_prefix='D',num_units=1,fplist=['D*DO?214AC*', 'D*SMA*', 'DO?214AC*', 'SMA*'],do_erc=True,aliases=['B130-E3', 'B140-E3', 'B150-E3', 'B160-E3'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='B220',dest=TEMPLATE,tool=SKIDL,keywords='diode Schottky',description='60V 2A Schottky Barrier Rectifier Diode, SMB',ref_prefix='D',num_units=1,fplist=['D*DO?214AC*', 'D*SMA*', 'DO?214AC*', 'SMA*'],do_erc=True,aliases=['B230', 'B240', 'B250', 'B260'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='B320',dest=TEMPLATE,tool=SKIDL,keywords='diode Schottky',description='60V 3A Schottky Barrier Rectifier Diode, SMC',ref_prefix='D',num_units=1,fplist=['D*DO?214AC*', 'D*SMA*', 'DO?214AC*', 'SMA*'],do_erc=True,aliases=['B330', 'B340', 'B350', 'B360'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BAR42FILM',dest=TEMPLATE,tool=SKIDL,keywords='diode Schottky',description='30V 0.1A Small signal Schottky diode, SOT-23',ref_prefix='D',num_units=1,fplist=['SOT?23*'],do_erc=True,aliases=['BAR43FILM'],pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BAS16TW',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Fast switching diode array 3 independent',ref_prefix='D',num_units=3,fplist=['*SC-70-6*', '*SC-88*', '*SOT-363*'],do_erc=True,aliases=['BAS16VY', 'MMBD4148TW', 'MMBD4448HTW', 'HN2D02FU', 'Comchip_ACDSV6-4448TI-G', 'Central_Semi_CMKD6001', 'Central_Semi_CMKD4448', 'Comchip_CDSV6-4148-G', 'Comchip_CDSV6-4448TI-G'],pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BAT48JFILM',dest=TEMPLATE,tool=SKIDL,keywords='diode Schottky',description='40V 0.35A Small Signal Schottky Diode, SOD-323',ref_prefix='D',num_units=1,fplist=['D*SOD?323*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BAT48ZFILM',dest=TEMPLATE,tool=SKIDL,keywords='diode Schottky',description='80V 0.5A Schottky Power Rectifier Diode, SOD-123',ref_prefix='D',num_units=1,fplist=['D*SOD?123*'],do_erc=True,aliases=['MBR0520LT', 'MBR0520', 'MBR0530', 'MBR0540', 'MBR0550', 'MBR0560', 'MBR0570', 'MBR0580', 'BAT42W-V', 'BAT43W-V'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BAT54A',dest=TEMPLATE,tool=SKIDL,keywords='schottky diode',description='schottky barrier diode',ref_prefix='D',num_units=1,fplist=['SOT-23*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BAT54ADW',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Schottky diode array 2 pair Com A',ref_prefix='D',num_units=4,fplist=['*SC-70-6*', '*SC-88*', '*SOT-363*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BAV99',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='BAV99 High-speed switching diodes',ref_prefix='D',num_units=2,fplist=['SOT?23*'],do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='BYV79-100',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='200V 14A Ultrafast Rectifier Diode, TO-220',ref_prefix='D',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['BYV79-200', 'BYV79-150'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DB3',dest=TEMPLATE,tool=SKIDL,keywords='AC diode DIAC',description='40V 2A Bidirectional trigger diode, DO-35',ref_prefix='D',num_units=1,fplist=['D*SOD27*', 'D*DO?35*'],do_erc=True,aliases=['DB4', 'DC34'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LL41',dest=TEMPLATE,tool=SKIDL,keywords='diode Schottky',description='30V 0.2A Small Signal Schottky diode, MiniMELF',ref_prefix='D',num_units=1,fplist=['D*MiniMELF*', 'MiniMELF*'],do_erc=True,aliases=['LL42', 'LL43'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LL4148',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='100V 0.15A standard switching diode, MiniMELF',ref_prefix='D',num_units=1,fplist=['D*MiniMELF*', 'MiniMELF*'],do_erc=True,aliases=['LL4448'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='MBR735',dest=TEMPLATE,tool=SKIDL,keywords='diode Schottky',description='45V 7.5A Schottky Barrier Rectifier Diode, TO-220',ref_prefix='D',num_units=1,fplist=['TO?220*'],do_erc=True,aliases=['MBR745'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='MRA4003T3G',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='1000V 1A General Purpose Rectifier Diode, SMA/DO-214AC',ref_prefix='D',num_units=1,fplist=['DO*214AC', '*SMA*'],do_erc=True,aliases=['MRA4004T3G', 'MRA4005T3G', 'MRA4006T3G', 'MRA4007T3G', 'NRVA4003T3G', 'NRVA4004T3G', 'NRVA4005T3G', 'NRVA4006T3G', 'NRVA4007T3G'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Rohm_UMN1N',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='High-speed switching diodes 2 pair Com A',ref_prefix='D',num_units=4,fplist=['*SOT-353*'],do_erc=True,aliases=['MMBD4448HCQW', 'Panasonic_MA5J002E'],pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Rohm_UMP11N',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='Ultra High Speed Switching Diode Array 2 pair Com A',ref_prefix='D',num_units=4,fplist=['*SC-70-6*', '*SC-88*', '*SOT-363*'],do_erc=True,aliases=['BAW56DW', 'BAW56S', 'MMBD4448HADW', 'Toshiba_HN1D01FU'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='SB120',dest=TEMPLATE,tool=SKIDL,keywords='diode Schottky',description='60V 1A Schottky Barrier Rectifier Diode, DO-41',ref_prefix='D',num_units=1,fplist=['D*SOD81*', 'D*DO?41*'],do_erc=True,aliases=['SB130', 'SB140', 'SB150', 'SB160', '1N5817', '1N5818', '1N5819'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='SM4001',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='1800V 1A General Purpose Rectifier Diode, MELF',ref_prefix='D',num_units=1,fplist=['D*MELF*', 'MELF*'],do_erc=True,aliases=['SM4002', 'SM4003', 'SM4004', 'SM4005', 'SM4006', 'SM4007', 'SM513', 'SM516', 'SM518', 'SM2000'],pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='ZMDxx',dest=TEMPLATE,tool=SKIDL,keywords='zener diode',description='1000mW Zener Diode, MiniMELF',ref_prefix='D',num_units=1,fplist=['D*MiniMELF*', 'MiniMELF*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='ZMYxx',dest=TEMPLATE,tool=SKIDL,keywords='zener diode',description='1300mW Zener Diode, MELF',ref_prefix='D',num_units=1,fplist=['D*MELF*', 'MELF*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='ZPDxx',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='500mW Zener Diode, DO-35',ref_prefix='D',num_units=1,fplist=['D*DO?35*', 'D*SOD27*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='ZPYxx',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='1300mW Zener Diode, DO-41',ref_prefix='D',num_units=1,fplist=['D*DO?41*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)])])
