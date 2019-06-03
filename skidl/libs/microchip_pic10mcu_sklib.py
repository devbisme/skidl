from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

microchip_pic10mcu = SchLib(tool=SKIDL).add_parts(*[
        Part(name='PIC10(L)F320-I/MC',dest=TEMPLATE,tool=SKIDL,do_erc=True,aliases=['PIC10(L)F322-I/MC']),
        Part(name='PIC10(L)F320-I/OT',dest=TEMPLATE,tool=SKIDL,do_erc=True,aliases=['PIC10(L)F322-I/OT']),
        Part(name='PIC10(L)F320-I/P',dest=TEMPLATE,tool=SKIDL,do_erc=True,aliases=['PIC10(L)F322-I/P']),
        Part(name='PIC10F200-I/MC',dest=TEMPLATE,tool=SKIDL,keywords='FLASH 8-Bit CMOS Microcontroller',description='PIC10F202, 512W Flash, 24B SRAM, DFN8',ref_prefix='U',num_units=1,do_erc=True,aliases=['PIC10F202-I/MC'],pins=[
            Pin(num='2',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='T0CKI/FOSC4/GP2',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='ICSPCLK/GP1',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='ICSPDAT/GP0',func=Pin.BIDIR,do_erc=True),
            Pin(num='7',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='Vpp/~MCLR~/GP3',do_erc=True)]),
        Part(name='PIC10F200-I/OT',dest=TEMPLATE,tool=SKIDL,keywords='FLASH 8-Bit CMOS Microcontroller',description='PIC10F202, 512W Flash, 24B SRAM, SOT-23-6',ref_prefix='U',num_units=1,do_erc=True,aliases=['PIC10F202-I/OT'],pins=[
            Pin(num='1',name='ICSPDAT/GP0',func=Pin.BIDIR,do_erc=True),
            Pin(num='2',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='ICSPCLK/GP1',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='T0CKI/FOSC4/GP2',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='6',name='Vpp/~MCLR~/GP3',do_erc=True)]),
        Part(name='PIC10F200-I/P',dest=TEMPLATE,tool=SKIDL,keywords='FLASH 8-Bit CMOS Microcontroller',description='512W Flash, 24B SRAM, PDIP8',ref_prefix='U',num_units=1,do_erc=True,aliases=['PIC10F202-I/P'],pins=[
            Pin(num='2',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='T0CKI/FOSC4/GP2',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='ICSPCLK/GP1',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='ICSPDAT/GP0',func=Pin.BIDIR,do_erc=True),
            Pin(num='7',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='Vpp/~MCLR~/GP3',do_erc=True)]),
        Part(name='PIC10F204-I/MC',dest=TEMPLATE,tool=SKIDL,keywords='FLASH 8-Bit CMOS Microcontroller',description='PIC10F206, 512W Flash, 24B SRAM, DFN8',ref_prefix='U',num_units=1,do_erc=True,aliases=['PIC10F206-I/MC'],pins=[
            Pin(num='2',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='T0CKI/COUT/FOSC4/GP2',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='ICSPCLK/CIN-/GP1',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='ICSPDAT/CIN+/GP0',func=Pin.BIDIR,do_erc=True),
            Pin(num='7',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='Vpp/~MCLR~/GP3',do_erc=True)]),
        Part(name='PIC10F204-I/OT',dest=TEMPLATE,tool=SKIDL,keywords='FLASH 8-Bit CMOS Microcontroller',description='PIC10F206, 512W Flash, 24B SRAM, SOT-23-6',ref_prefix='U',num_units=1,do_erc=True,aliases=['PIC10F206-I/OT'],pins=[
            Pin(num='1',name='ICSPDAT/CIN+/GP0',func=Pin.BIDIR,do_erc=True),
            Pin(num='2',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='ICSPCLK/CIN-/GP1',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='T0CKI/COUT/FOSC4/GP2',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='6',name='Vpp/~MCLR~/GP3',do_erc=True)]),
        Part(name='PIC10F204-I/P',dest=TEMPLATE,tool=SKIDL,keywords='FLASH 8-Bit CMOS Microcontroller',description='512W Flash, 24B SRAM, PDIP8',ref_prefix='U',num_units=1,do_erc=True,aliases=['PIC10F206-I/P'],pins=[
            Pin(num='2',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='T0CKI/COUT/FOSC4/GP2',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='ICSPCLK/CIN-/GP1',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='ICSPDAT/CIN+/GP0',func=Pin.BIDIR,do_erc=True),
            Pin(num='7',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='Vpp/~MCLR~/GP3',do_erc=True)]),
        Part(name='PIC10F220-I/MC',dest=TEMPLATE,tool=SKIDL,keywords='FLASH 8-Bit CMOS Microcontroller',description='PIC10F222, 512W Flash, 24B SRAM, DFN8',ref_prefix='U',num_units=1,do_erc=True,aliases=['PIC10F222-I/MC'],pins=[
            Pin(num='2',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='T0CKI/FOSC4/GP2',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='ICSPCLK/AN1/GP1',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='ICSPDAT/AN0/GP0',func=Pin.BIDIR,do_erc=True),
            Pin(num='7',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='Vpp/~MCLR~/GP3',do_erc=True)]),
        Part(name='PIC10F220-I/OT',dest=TEMPLATE,tool=SKIDL,keywords='FLASH 8-Bit CMOS Microcontroller',description='PIC10F222, 512W Flash, 24B SRAM, SOT-23-6',ref_prefix='U',num_units=1,do_erc=True,aliases=['PIC10F222-I/OT'],pins=[
            Pin(num='1',name='ICSPDAT/AN0/GP0',func=Pin.BIDIR,do_erc=True),
            Pin(num='2',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='ICSPCLK/AN1/GP1',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='T0CKI/FOSC4/GP2',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='6',name='Vpp/~MCLR~/GP3',do_erc=True)]),
        Part(name='PIC10F220-I/P',dest=TEMPLATE,tool=SKIDL,keywords='FLASH 8-Bit CMOS Microcontroller',description='512W Flash, 24B SRAM, PDIP8',ref_prefix='U',num_units=1,do_erc=True,aliases=['PIC10F222-I/P'],pins=[
            Pin(num='2',name='VDD',func=Pin.PWRIN,do_erc=True),
            Pin(num='3',name='T0CKI/FOSC4/GP2',func=Pin.BIDIR,do_erc=True),
            Pin(num='4',name='ICSPCLK/AN1/GP1',func=Pin.BIDIR,do_erc=True),
            Pin(num='5',name='ICSPDAT/AN0/GP0',func=Pin.BIDIR,do_erc=True),
            Pin(num='7',name='VSS',func=Pin.PWRIN,do_erc=True),
            Pin(num='8',name='Vpp/~MCLR~/GP3',do_erc=True)])])
