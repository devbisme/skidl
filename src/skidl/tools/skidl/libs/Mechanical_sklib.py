from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Mechanical = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'DIN_Rail_Adapter', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'DIN_Rail_Adapter'}), 'ref_prefix':'DRA', 'fplist':[''], 'footprint':'', 'keywords':'Mounting holes, DIN rail adapter', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Mechanical.kicad_sym\nDIN_Rail_Adapter\n\nMounting holes, DIN rail adapter' }),
        Part(**{ 'name':'Fiducial', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fiducial'}), 'ref_prefix':'FID', 'fplist':[''], 'footprint':'', 'keywords':'fiducial marker', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Mechanical.kicad_sym\nFiducial\n\nfiducial marker' }),
        Part(**{ 'name':'Heatsink', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Heatsink'}), 'ref_prefix':'HS', 'fplist':[''], 'footprint':'', 'keywords':'thermal heat temperature', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Mechanical.kicad_sym\nHeatsink\n\nthermal heat temperature' }),
        Part(**{ 'name':'Heatsink_Pad', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Heatsink_Pad'}), 'ref_prefix':'HS', 'fplist':[''], 'footprint':'', 'keywords':'thermal heat temperature', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Mechanical.kicad_sym\nHeatsink_Pad\n\nthermal heat temperature', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Heatsink_Pad_2Pin', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Heatsink_Pad_2Pin'}), 'ref_prefix':'HS', 'fplist':[''], 'footprint':'', 'keywords':'thermal heat temperature', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Mechanical.kicad_sym\nHeatsink_Pad_2Pin\n\nthermal heat temperature', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Heatsink_Pad_3Pin', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Heatsink_Pad_3Pin'}), 'ref_prefix':'HS', 'fplist':[''], 'footprint':'', 'keywords':'thermal heat temperature', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Mechanical.kicad_sym\nHeatsink_Pad_3Pin\n\nthermal heat temperature', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Housing', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Housing'}), 'ref_prefix':'N', 'fplist':[''], 'footprint':'', 'keywords':'housing enclosure', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Mechanical.kicad_sym\nHousing\n\nhousing enclosure' }),
        Part(**{ 'name':'Housing_Pad', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Housing_Pad'}), 'ref_prefix':'N', 'fplist':[''], 'footprint':'', 'keywords':'housing enclosure shield', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Mechanical.kicad_sym\nHousing_Pad\n\nhousing enclosure shield', 'pins':[
            Pin(num='1',name='PAD',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MountingHole', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MountingHole'}), 'ref_prefix':'H', 'fplist':[''], 'footprint':'', 'keywords':'mounting hole', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Mechanical.kicad_sym\nMountingHole\n\nmounting hole' }),
        Part(**{ 'name':'MountingHole_Pad', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MountingHole_Pad'}), 'ref_prefix':'H', 'fplist':[''], 'footprint':'', 'keywords':'mounting hole', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Mechanical.kicad_sym\nMountingHole_Pad\n\nmounting hole', 'pins':[
            Pin(num='1',name='1',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MountingHole_Pad_MP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MountingHole_Pad_MP'}), 'ref_prefix':'H', 'fplist':[''], 'footprint':'', 'keywords':'mounting hole', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Mechanical.kicad_sym\nMountingHole_Pad_MP\n\nmounting hole', 'pins':[
            Pin(num='MP',name='MP',func=pin_types.INPUT,unit=1)], 'unit_defs':[] })])