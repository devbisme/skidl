from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Sensor_Voltage = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'LV25-P', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LV25-P'}), 'ref_prefix':'U', 'fplist':['Sensor_Voltage:LEM_LV25-P'], 'footprint':'Sensor_Voltage:LEM_LV25-P', 'keywords':'Voltage transducer', 'description':'', 'datasheet':'https://www.lem.com/sites/default/files/products_datasheets/lv_25-p.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Voltage.kicad_sym\nLV25-P\n\nVoltage transducer', 'pins':[
            Pin(num='1',name='HV+',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='HV-',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='M',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='V-',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] })])