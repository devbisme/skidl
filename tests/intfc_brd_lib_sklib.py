from skidl import Pin, Part, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

intfc_brd_lib = SchLib(tool=SKIDL).add_parts(*[
        Part(name='TPS793XX',dest=TEMPLATE,tool=SKIDL,skidl_trace='C:\\xesscorp\\PRODUCTS\\INACTIVE\\XuLA_Developmental\\fmw\\intfc_brd\\intfc_brd.py#20',ref_prefix='U',num_units=1,do_erc=True,footprint='TO_SOT_Packages_SMD:SOT-23-5',pins=[
            Pin(num='1',name='IN',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='EN',do_erc=True),
            Pin(num='4',name='NR',func=Pin.OUTPUT,do_erc=True),
            Pin(num='5',name='OUT',func=Pin.PWROUT,do_erc=True)]),
        Part(name='C',dest=TEMPLATE,tool=SKIDL,skidl_trace='C:\\xesscorp\\PRODUCTS\\INACTIVE\\XuLA_Developmental\\fmw\\intfc_brd\\intfc_brd.py#21',keywords='cap capacitor',description='Unpolarized capacitor',ref_prefix='C',num_units=1,fplist=['C_*'],do_erc=True,footprint='Capacitors_SMD:C_0603',pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='PIC32MX2*0F***B-QFN28',dest=TEMPLATE,tool=SKIDL,skidl_trace='C:\\xesscorp\\PRODUCTS\\INACTIVE\\XuLA_Developmental\\fmw\\intfc_brd\\intfc_brd.py#30',ref_prefix='U',num_units=1,do_erc=True,footprint='Housings_DFN_QFN:QFN-28-1EP_6x6mm_Pitch0.65mm',pins=[
            Pin(num='15',name='TDO/RPB9/SDA1/CTED4/PMD3/RB9',func=Pin.BIDIR,do_erc=True),
            Pin(num='16',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='17',name='VCAP',func=Pin.PWROUT,do_erc=True),
            Pin(num='18',name='PGED2/RPB10/D+/CTED11/RB10',func=Pin.BIDIR,do_erc=True),
            Pin(num='19',name='PGEC2/RPB11/D-/RB11',func=Pin.BIDIR,do_erc=True),
            Pin(num='20',name='VUSB3V3',func=Pin.PWRIN,do_erc=True),
            Pin(num='21',name='AN11/RPB13/CTPLS/PMRD/RB13',func=Pin.BIDIR,do_erc=True),
            Pin(num='22',name='CVREFOUT/AN10/C3INB/RPB14/VBUSON/SCK1/CTED5/RB14',func=Pin.BIDIR,do_erc=True),
            Pin(num='23',name='AN9/C3INA/RPB15/SCK2/CTED6/PMCS1/RB15',func=Pin.BIDIR,do_erc=True),
            Pin(num='24',name='AVSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='25',name='AVDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='26',name='~MCLR',do_erc=True),
            Pin(num='27',name='PGED3/VREF+/CVREF+/AN0/C3INC/RPA0/CTED1/PMD7/RA0',func=Pin.BIDIR,do_erc=True),
            Pin(num='28',name='PGEC3/VREF-/CVREF-/AN1/RPA1/CTED2/PMD6/RA1',func=Pin.BIDIR,do_erc=True),
            Pin(num='29',name='PAD',func=Pin.PWRIN,do_erc=True),
            Pin(num='1',name='PGED1/AN2/C1IND/C2INB/C3IND/RPB0/PMD0/RB0',func=Pin.BIDIR,do_erc=True),
            Pin(num='2',name='PGEC1/AN3/C1INC/C2INA/RPB1/CTED12/PMD1/RB1',func=Pin.BIDIR,do_erc=True),
            Pin(num='3',name='AN4/C1INB/C2IND/RPB2/SDA2/CTED13/PMD2/RB2',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='AN5/C1INA/C2INC/RTCC/RPB3/SCL2/PMWR/RB3',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='6',name='OSC1/CLKI/RPA2/RA2',func=Pin.BIDIR,do_erc=True),
            Pin(num='7',name='OSC2/CLKO/RPA3/PMA0/RA3',func=Pin.BIDIR,do_erc=True),
            Pin(num='8',name='SOSCI/RPB4/RB4',func=Pin.BIDIR,do_erc=True),
            Pin(num='9',name='SOSCO/RPA4/T1CK/CTED9/PMA1/RA4',func=Pin.BIDIR,do_erc=True),
            Pin(num='10',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='11',name='TMS/RPB5/USBID/RB5',func=Pin.BIDIR,do_erc=True),
            Pin(num='12',name='VBUS',do_erc=True),
            Pin(num='13',name='TDI/RPB7/CTED3/PMD5/INT0/RB7',func=Pin.BIDIR,do_erc=True),
            Pin(num='14',name='TCK/RPB8/SCL1/CTED10/PMD4/RB8',func=Pin.BIDIR,do_erc=True)]),
        Part(name='R',dest=TEMPLATE,tool=SKIDL,skidl_trace='C:\\xesscorp\\PRODUCTS\\INACTIVE\\XuLA_Developmental\\fmw\\intfc_brd\\intfc_brd.py#47',keywords='r res resistor',description='Resistor',ref_prefix='R',num_units=1,fplist=['R_*', 'R_*'],do_erc=True,footprint='Resistors_SMD:R_0603',pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='USB-MicroB',dest=TEMPLATE,tool=SKIDL,skidl_trace='C:\\xesscorp\\PRODUCTS\\INACTIVE\\XuLA_Developmental\\fmw\\intfc_brd\\intfc_brd.py#55',keywords='USB, USBB, connector',description='USB Micro-B connector',ref_prefix='USB',num_units=1,do_erc=True,footprint='XESS:USB-microB-1',pins=[
            Pin(num='1',name='VBUS',func=Pin.PWROUT,do_erc=True),
            Pin(num='2',name='D-',func=Pin.BIDIR,do_erc=True),
            Pin(num='3',name='D+',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='NC',func=Pin.NOCONNECT,do_erc=True),
            Pin(num='5',name='GND',func=Pin.PWROUT,do_erc=True),
            Pin(num='SH',name='SHIELD',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED',dest=TEMPLATE,tool=SKIDL,skidl_trace='C:\\xesscorp\\PRODUCTS\\INACTIVE\\XuLA_Developmental\\fmw\\intfc_brd\\intfc_brd.py#65',keywords='led diode',description='LED generic',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,footprint='Diodes_SMD:D_0603',pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='XTAL4',dest=TEMPLATE,tool=SKIDL,skidl_trace='C:\\xesscorp\\PRODUCTS\\INACTIVE\\XuLA_Developmental\\fmw\\intfc_brd\\intfc_brd.py#71',ref_prefix='Y',num_units=1,do_erc=True,footprint='XESS:32x25-4',pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='PICkit3_hdr',dest=TEMPLATE,tool=SKIDL,skidl_trace='C:\\xesscorp\\PRODUCTS\\INACTIVE\\XuLA_Developmental\\fmw\\intfc_brd\\intfc_brd.py#79',ref_prefix='U',num_units=1,do_erc=True,footprint='Pin_Headers:Pin_Header_Straight_1x06',pins=[
            Pin(num='1',name='~MCLR',func=Pin.OUTPUT,do_erc=True),
            Pin(num='2',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='PGD',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='PGC',func=Pin.BIDIR,do_erc=True),
            Pin(num='6',name='NC',func=Pin.NOCONNECT,do_erc=True)]),
        Part(name='Conn_01x06',dest=TEMPLATE,tool=SKIDL,skidl_trace='C:\\xesscorp\\PRODUCTS\\INACTIVE\\XuLA_Developmental\\fmw\\intfc_brd\\intfc_brd.py#88',keywords='connector',description='Generic connector, single row, 01x06',ref_prefix='J',num_units=1,fplist=['Connector*:*_??x*mm*', 'Connector*:*1x??x*mm*', 'Pin?Header?Straight?1X*', 'Pin?Header?Angled?1X*', 'Socket?Strip?Straight?1X*', 'Socket?Strip?Angled?1X*'],do_erc=True,footprint='Pin_Headers:Pin_Header_Straight_1x06',pins=[
            Pin(num='1',name='Pin_1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='Pin_2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='Pin_3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='Pin_4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='Pin_5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='Pin_6',func=Pin.PASSIVE,do_erc=True)])])