from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

__init___lib = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'R', 'dest':TEMPLATE, 'tool':SKIDL, 'reference':'R', 'num_units':None, '_match_pin_regex':False, 'pin':None, 'ref_prefix':'R', '_aliases':Alias({'R'}), 'footprint':'Resistors_SMD:R_0805', '_name':'R', 'ki_keywords':'R res resistor', 'fplist':[''], 'ki_fp_filters':'R_*', 'do_erc':True, 'aliases':Alias({'R'}), 'keywords':'R res resistor', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,do_erc=True)] })])