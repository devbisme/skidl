from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

test_lib_lib = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'R', 'dest':TEMPLATE, 'tool':SKIDL, 'description':'Resistor', 'num_units':None, 'footprint':'null', 'aliases':Alias({'R'}), 'do_erc':True, 'ki_keywords':'R res resistor', 'keywords':'R res resistor', '_aliases':Alias({'R'}), 'fplist':[''], 'datasheet':'~', 'reference':'R', 'ki_description':'Resistor', '_match_pin_regex':False, 'ref_prefix':'R', 'pin':None, '_name':'R', 'ki_fp_filters':'R_*', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,do_erc=True)] }),
        Part(**{ 'name':'C', 'dest':TEMPLATE, 'tool':SKIDL, 'description':'Unpolarized capacitor', 'num_units':None, 'footprint':'null', 'aliases':Alias({'C'}), 'do_erc':True, 'ki_keywords':'cap capacitor', 'keywords':'cap capacitor', '_aliases':Alias({'C'}), 'fplist':[''], 'datasheet':'~', 'reference':'C', 'ki_description':'Unpolarized capacitor', '_match_pin_regex':False, 'ref_prefix':'C', 'pin':None, '_name':'C', 'ki_fp_filters':'C_*', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.types.PASSIVE,do_erc=True)] }),
        Part(**{ 'name':'L', 'dest':TEMPLATE, 'tool':SKIDL, 'description':'Inductor', 'num_units':None, 'footprint':'null', 'aliases':Alias({'L'}), 'do_erc':True, 'ki_keywords':'inductor choke coil reactor magnetic', 'keywords':'inductor choke coil reactor magnetic', '_aliases':Alias({'L'}), 'fplist':[''], 'datasheet':'~', 'reference':'L', 'ki_description':'Inductor', '_match_pin_regex':False, 'ref_prefix':'L', 'pin':None, '_name':'L', 'ki_fp_filters':'Choke_* *Coil* Inductor_* L_*', 'pins':[
            Pin(num='1',name='1',func=Pin.types.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.types.PASSIVE,do_erc=True)] })])