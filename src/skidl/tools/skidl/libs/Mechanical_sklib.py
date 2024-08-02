from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Mechanical = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'DIN_Rail_Adapter', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DIN_Rail_Adapter'}), 'ref_prefix':'DRA', 'fplist':[''], 'footprint':'', 'keywords':'Mounting holes, DIN rail adapter', 'description':'', 'datasheet':'~' }),
        Part(**{ 'name':'Fiducial', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fiducial'}), 'ref_prefix':'FID', 'fplist':[''], 'footprint':'', 'keywords':'fiducial marker', 'description':'', 'datasheet':'~' }),
        Part(**{ 'name':'Heatsink', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Heatsink'}), 'ref_prefix':'HS', 'fplist':[''], 'footprint':'', 'keywords':'thermal heat temperature', 'description':'', 'datasheet':'~' }),
        Part(**{ 'name':'Heatsink_Pad', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Heatsink_Pad'}), 'ref_prefix':'HS', 'fplist':[''], 'footprint':'', 'keywords':'thermal heat temperature', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Heatsink_Pad_2Pin', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Heatsink_Pad_2Pin'}), 'ref_prefix':'HS', 'fplist':[''], 'footprint':'', 'keywords':'thermal heat temperature', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Heatsink_Pad_3Pin', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Heatsink_Pad_3Pin'}), 'ref_prefix':'HS', 'fplist':[''], 'footprint':'', 'keywords':'thermal heat temperature', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Housing', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Housing'}), 'ref_prefix':'N', 'fplist':[''], 'footprint':'', 'keywords':'housing enclosure', 'description':'', 'datasheet':'~' }),
        Part(**{ 'name':'Housing_Pad', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Housing_Pad'}), 'ref_prefix':'N', 'fplist':[''], 'footprint':'', 'keywords':'housing enclosure shield', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='PAD',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MountingHole', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MountingHole'}), 'ref_prefix':'H', 'fplist':[''], 'footprint':'', 'keywords':'mounting hole', 'description':'', 'datasheet':'~' }),
        Part(**{ 'name':'MountingHole_Pad', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MountingHole_Pad'}), 'ref_prefix':'H', 'fplist':[''], 'footprint':'', 'keywords':'mounting hole', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='1',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MountingHole_Pad_MP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MountingHole_Pad_MP'}), 'ref_prefix':'H', 'fplist':[''], 'footprint':'', 'keywords':'mounting hole', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='MP',name='MP',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] })])