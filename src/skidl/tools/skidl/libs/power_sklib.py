from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

power = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'+10V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+10V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+12C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+12C'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+12L', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+12L'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+12LF', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+12LF'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+12P', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+12P'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+12V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+12V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+12VA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+12VA'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+15V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+15V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+1V0', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+1V0'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+1V1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+1V1'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+1V2', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+1V2'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+1V35', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+1V35'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+1V5', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+1V5'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+1V8', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+1V8'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+24V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+24V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+28V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+28V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+2V5', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+2V5'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+2V8', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+2V8'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+3.3V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+3.3V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+3.3VA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+3.3VA'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+3.3VADC', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+3.3VADC'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'+3.3VDAC', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+3.3VDAC'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'+3.3VP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+3.3VP'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'+36V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+36V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+3V0', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+3V0'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+3V3', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+3V3'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+3V8', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+3V8'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+48V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+48V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+4V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+4V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+5C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+5C'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+5F', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+5F'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+5P', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+5P'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+5V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+5V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+5VA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+5VA'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+5VD', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+5VD'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+5VL', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+5VL'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+5VP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+5VP'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+6V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+6V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+7.5V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+7.5V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+8V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+8V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+9V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+9V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+9VA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+9VA'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+BATT', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+BATT'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power battery', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+VDC', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+VDC'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'+VSW', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'+VSW'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'-10V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-10V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-12V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-12V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-12VA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-12VA'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-15V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-15V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-24V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-24V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-2V5', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-2V5'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-36V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-36V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-3V3', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-3V3'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-48V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-48V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-5V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-5V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-5VA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-5VA'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-6V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-6V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-8V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-8V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'-9V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-9V'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'-9VA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-9VA'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'-BATT', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-BATT'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power battery', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'-VDC', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-VDC'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'-VSW', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'-VSW'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'AC', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AC'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Earth', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Earth'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global ground gnd', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Earth_Clean', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Earth_Clean'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global ground gnd clean signal', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Earth_Protective', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Earth_Protective'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global ground gnd clean', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'GND', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'GND'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'GND1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'GND1'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'GND2', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'GND2'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'GND3', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'GND3'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'GNDA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'GNDA'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'GNDD', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'GNDD'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'GNDPWR', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'GNDPWR'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global ground', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'GNDREF', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'GNDREF'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'GNDS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'GNDS'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'HT', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'HT'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'LINE', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LINE'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'NEUT', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'NEUT'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PRI_HI', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PRI_HI'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PRI_LO', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PRI_LO'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PRI_MID', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PRI_MID'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PWR_FLAG', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PWR_FLAG'}), 'ref_prefix':'#FLG', 'fplist':[''], 'footprint':'', 'keywords':'flag power', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWROUT)], 'unit_defs':[] }),
        Part(**{ 'name':'VAA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VAA'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VAC', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VAC'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VBUS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VBUS'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VCC', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VCC'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VCCQ', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VCCQ'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VCOM', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VCOM'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VD', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VD'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VDC', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VDC'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VDD', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VDD'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VDDA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VDDA'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VDDF', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VDDF'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VEE', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VEE'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VMEM', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VMEM'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VPP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VPP'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VS'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VSS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VSS'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VSSA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VSSA'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Vdrive', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Vdrive'}), 'ref_prefix':'#PWR', 'fplist':[''], 'footprint':'', 'keywords':'global power', 'description':'', 'datasheet':'', 'pins':[
            Pin(num='1',name='~',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] })])