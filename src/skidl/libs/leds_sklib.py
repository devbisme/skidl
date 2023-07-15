from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

leds = SchLib(tool=SKIDL).add_parts(*[
        Part(name='LED_Cree_XHP50_12V',dest=TEMPLATE,tool=SKIDL,keywords='led diode',description='XLamp® XHP50 LED, 12V footprint (all 4 LEDs in series)',ref_prefix='D',num_units=1,fplist=['LED?CREE?XHP50?12V*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='PAD',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_Cree_XHP50_6V',dest=TEMPLATE,tool=SKIDL,keywords='led diode',description='XLamp® XHP50 LED, 6V footprint (2x2 serial LEDs in parallel)',ref_prefix='D',num_units=1,fplist=['LED?CREE?XHP50?6V*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='PAD',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_Cree_XHP70_12V',dest=TEMPLATE,tool=SKIDL,keywords='led diode',description='XLamp® XHP70 LED, 12V footprint (all 4 LEDs in series)',ref_prefix='D',num_units=1,fplist=['LED?CREE?XHP70?12V*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='PAD',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_Cree_XHP70_6V',dest=TEMPLATE,tool=SKIDL,keywords='led diode',description='XLamp® XHP70 LED, 6V footprint (2x2 serial LEDs in parallel)',ref_prefix='D',num_units=1,fplist=['LED?CREE?XHP70?6V*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='PAD',func=Pin.PASSIVE,do_erc=True)])])
