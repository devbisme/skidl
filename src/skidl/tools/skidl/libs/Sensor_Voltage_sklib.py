from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Sensor_Voltage = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'LV25-P', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LV25-P'}), 'ref_prefix':'U', 'fplist':['Sensor_Voltage:LEM_LV25-P'], 'footprint':'Sensor_Voltage:LEM_LV25-P', 'keywords':'Voltage transducer', 'description':'', 'datasheet':'https://www.lem.com/sites/default/files/products_datasheets/lv_25-p.pdf', 'pins':[
            Pin(num='1',name='HV+',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='HV-',func=Pin.types.INPUT,unit=1),
            Pin(num='4',name='M',func=Pin.types.OUTPUT,unit=1),
            Pin(num='5',name='V+',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='V-',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] })])