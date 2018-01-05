import pytest
from skidl import *
from .setup_teardown import *

def test_lib_import_1():
    lib = SchLib('xess.lib')
    assert len(lib) > 0

def test_lib_import_2():
    lib = SchLib('device')

def test_lib_export_1():
    lib = SchLib('device')
    lib.export('my_device', tool=SKIDL)
    my_lib = SchLib('my_device', tool=SKIDL)
    assert len(lib) == len(my_lib)

def test_lib_creation_1():
    lib = SchLib()
    prt1 = SkidlPart(name='Q', dest=TEMPLATE)
    lib += prt1
    lib += prt1  # Duplicate library entries are not added.
    assert(len(lib.parts) == 1)
    assert(not lib.get_parts(name='QQ')) # Part not in library.
    prt2 = SkidlPart(name='QQ', dest=TEMPLATE)
    prt2.add_pins(Pin(num=1,name='Q1',func=Pin.TRISTATE), Pin(num=2,name='Q2',func=Pin.PWRIN))
    lib += prt2
    prt2.add_pins(Pin(num=3,name='Q1',func=Pin.PWROUT))
    assert(len(lib.parts) == 2)
    assert(lib['Q'].name == 'Q')
    assert(len(lib['Q'].pins) == 0)
    assert(lib['QQ'].name == 'QQ')
    assert(len(lib['QQ'].pins) == 2)

def test_backup_1():
    a = Part('device','R',footprint='null')
    b = Part('device','C',footprint='null')
    c = Part('device','L',footprint='null')
    generate_netlist()  # This creates the backup parts library.
    default_circuit.reset()
    QUERY_BACKUP_LIB = True
    a = Part('crap','R',footprint='null')
    b = Part('crap','C',footprint='null')
    generate_netlist()

def test_lib_1():
    lib_kicad = SchLib('device')
    lib_kicad.export('device')
    lib_skidl = SchLib('device', tool=SKIDL)
    assert(len(lib_kicad) == len(lib_skidl))
    DEFAULT_TOOL = SKIDL
    QUERY_BACKUP_LIB = False
    a = Part('device','R')
    b = Part('device','L')
    c = Part('device','C')
    QUERY_BACKUP_LIB = True
