from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Diode_Laser = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'PLT5_450B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PLT5_450B'}), 'ref_prefix':'LD', 'fplist':['OptoDevice:LaserDiode_TO56-3'], 'footprint':'OptoDevice:LaserDiode_TO56-3', 'keywords':'opto laserdiode', 'description':'', 'datasheet':'https://look.ams-osram.com/m/711b74151583f43/original/PLT5-450B.pdf', 'search_text':'/usr/share/kicad/symbols/Diode_Laser.kicad_sym\nPLT5_450B\n\nopto laserdiode', 'pins':[
            Pin(num='1',name='A',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='3',name='C',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PLT5_488', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PLT5_488'}), 'ref_prefix':'LD', 'fplist':['OptoDevice:LaserDiode_TO56-3'], 'footprint':'OptoDevice:LaserDiode_TO56-3', 'keywords':'opto laserdiode', 'description':'', 'datasheet':'https://look.ams-osram.com/m/451ee5087173918f/original/PLT5-488.pdf', 'search_text':'/usr/share/kicad/symbols/Diode_Laser.kicad_sym\nPLT5_488\n\nopto laserdiode', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SPL_PL90', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SPL_PL90'}), 'ref_prefix':'LD', 'fplist':['LED_THT:LED_D5.0mm'], 'footprint':'LED_THT:LED_D5.0mm', 'keywords':'opto laserdiode', 'description':'', 'datasheet':'https://look.ams-osram.com/m/2e6f6e5edf55ddfe/original/SPL-PL90.pdf', 'search_text':'/usr/share/kicad/symbols/Diode_Laser.kicad_sym\nSPL_PL90\n\nopto laserdiode', 'pins':[
            Pin(num='1',name='C',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PL520', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PL520'}), 'ref_prefix':'LD', 'fplist':['OptoDevice:LaserDiode_TO56-3', 'OptoDevice:LaserDiode_TO38ICut-3'], 'footprint':'OptoDevice:LaserDiode_TO56-3', 'keywords':'opto laserdiode', 'description':'', 'datasheet':'http://www.osram-os.com/Graphics/XPic7/00234693_0.pdf/PL%20520.pdf', 'search_text':'/usr/share/kicad/symbols/Diode_Laser.kicad_sym\nPL520\n\nopto laserdiode', 'pins':[
            Pin(num='1',name='A',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='3',name='C',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PLT5_510', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PLT5_510'}), 'ref_prefix':'LD', 'fplist':['OptoDevice:LaserDiode_TO56-3', 'OptoDevice:LaserDiode_TO38ICut-3', 'OptoDevice:LaserDiode_TO56-3'], 'footprint':'OptoDevice:LaserDiode_TO56-3', 'keywords':'opto laserdiode', 'description':'', 'datasheet':'https://look.ams-osram.com/m/2562f8ca3a03a793/original/PLT5-510.pdf', 'search_text':'/usr/share/kicad/symbols/Diode_Laser.kicad_sym\nPLT5_510\n\nopto laserdiode', 'pins':[
            Pin(num='1',name='A',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='3',name='C',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] })])