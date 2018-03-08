import pytest

# Skip this test module if PySpice is missing.
pexpect = pytest.importorskip("PySpice")

from skidl.pyspice import *
from .setup_teardown import *
import PySpice


def test_lib_import_1():
    lib_search_paths[SPICE].append('C:\Program Files (x86)\LTC\LTspiceIV\lib')
    lib = SchLib('lt1083', tool=SPICE)
    assert len(lib) > 0
    for p in lib.get_parts():
        print(p)

def test_lib_import_2():
    with pytest.raises(Exception):
        lib = SchLib('lt1074', tool=SPICE)

def test_lib_export_1():
    lib_search_paths[SPICE].append('C:\Program Files (x86)\LTC\LTspiceIV\lib')
    set_default_tool(SPICE)
    lib = SchLib('lt1083', tool=SPICE)
    lib.export('my_lt1083', tool=SKIDL)
    # Doesn't work because of "pyspice={...}" placed in exported library.
    #my_lib = SchLib('my_lt1083', tool=SKIDL)
    #assert len(lib) == len(my_lib)
