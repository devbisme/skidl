from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

bosch = SchLib(tool=SKIDL).add_parts(*[
        Part(name='BMF055',dest=TEMPLATE,tool=SKIDL,keywords='9-axis motion sensor IMU SAMD20 ARM Cortex-M0+',description='Custom programmable 9-axis motion sensor',ref_prefix='U',num_units=1,fplist=['LGA-28*'],do_erc=True,pins=[
            Pin(num='1',name='PB03(ACC_GYRO_INT2)',func=Pin.BIDIR,do_erc=True),
            Pin(num='2',name='GND',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='4',name='PB02',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='PB01',func=Pin.BIDIR,do_erc=True),
            Pin(num='6',name='PB00',func=Pin.BIDIR,do_erc=True),
            Pin(num='7',name='(SWDIO)PA31',func=Pin.BIDIR,do_erc=True),
            Pin(num='8',name='(SWCLK)PA30',func=Pin.BIDIR,do_erc=True),
            Pin(num='9',name='CAP',func=Pin.BIDIR,do_erc=True),
            Pin(num='10',name='PA28',func=Pin.BIDIR,do_erc=True),
            Pin(num='20',name='PB16',func=Pin.BIDIR,do_erc=True),
            Pin(num='11',name='~RESET',do_erc=True),
            Pin(num='21',name='(MISO)PA19',func=Pin.BIDIR,do_erc=True),
            Pin(num='12',name='(GYRO_CSB)PA27',func=Pin.BIDIR,do_erc=True),
            Pin(num='22',name='(ACC_MAG_CSB)PA18',func=Pin.BIDIR,do_erc=True),
            Pin(num='13',name='PB23(ACC_GYRO_INT1)',func=Pin.BIDIR,do_erc=True),
            Pin(num='23',name='(SCLK)PA17',func=Pin.BIDIR,do_erc=True),
            Pin(num='14',name='PA24',do_erc=True),
            Pin(num='24',name='(MOSI)PA16',func=Pin.BIDIR,do_erc=True),
            Pin(num='15',name='PA23',func=Pin.BIDIR,do_erc=True),
            Pin(num='25',name='GNDIO',func=Pin.PWRIN,do_erc=True),
            Pin(num='16',name='PA22',func=Pin.BIDIR,do_erc=True),
            Pin(num='26',name='PA01',func=Pin.BIDIR,do_erc=True),
            Pin(num='17',name='PA21',func=Pin.BIDIR,do_erc=True),
            Pin(num='27',name='PA00',func=Pin.BIDIR,do_erc=True),
            Pin(num='18',name='PA20',func=Pin.BIDIR,do_erc=True),
            Pin(num='28',name='VDDIO',func=Pin.PWRIN,do_erc=True),
            Pin(num='19',name='PB17',func=Pin.BIDIR,do_erc=True)])])
