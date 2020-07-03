import pytest

from skidl import *
from skidl.common import *  # pylint: disable=wildcard-import

from .setup_teardown import *


def test_missing_lib():
    # Sometimes, loading a part from a non-existent library doesn't throw an
    # exception until the second time it's tried. This detects that error.
    set_query_backup_lib(
        False
    )  # Don't allow searching backup lib that might exist from previous tests.
    with pytest.raises(FileNotFoundError):
        a = Part("crap", "R")
    with pytest.raises(FileNotFoundError):
        b = Part("crap", "C")


def test_lib_import_1():
    lib = SchLib("xess.lib")
    assert len(lib) > 0


def test_lib_import_2():
    lib = SchLib("Device")


def test_lib_export_1():
    lib = SchLib("Device")
    lib.export("my_device", tool=SKIDL)
    my_lib = SchLib("my_device", tool=SKIDL)
    assert len(lib) == len(my_lib)


def test_lib_creation_1():
    lib = SchLib()
    prt1 = SkidlPart(name="Q", dest=TEMPLATE)
    lib += prt1
    lib += prt1  # Duplicate library entries are not added.
    assert len(lib.parts) == 1
    assert not lib.get_parts(name="QQ")  # Part not in library.
    prt2 = SkidlPart(name="QQ", dest=TEMPLATE)
    prt2.add_pins(
        Pin(num=1, name="Q1", func=Pin.types.TRISTATE),
        Pin(num=2, name="Q2", func=Pin.types.PWRIN),
    )
    lib += prt2
    prt2.add_pins(Pin(num=3, name="Q1", func=Pin.types.PWROUT))
    assert len(lib.parts) == 2
    assert lib["Q"].name == "Q"
    assert len(lib["Q"].pins) == 0
    assert lib["QQ"].name == "QQ"
    assert len(lib["QQ"].pins) == 2


def test_backup_1():
    a = Part("Device", "R", footprint="null")
    b = Part("Device", "C", footprint="null")
    c = Part("Device", "L", footprint="null")
    generate_netlist(do_backup=True)  # This creates the backup parts library.
    default_circuit.reset()
    set_query_backup_lib(True)  # FIXME: this is already True by default!
    a = Part("crap", "R", footprint="null")
    b = Part("crap", "C", footprint="null")
    generate_netlist()


def test_backup_2():
    a = Part("Device", "R", footprint="null")
    b = Part("Device", "C", footprint="null")
    c = Part("Device", "L", footprint="null")
    a & b & c  # Place parts in series.
    num_pins_per_net_1 = {net.name: len(net) for net in default_circuit.get_nets()}
    generate_netlist(do_backup=True)  # This creates the backup parts library.
    num_pins_per_net_2 = {net.name: len(net) for net in default_circuit.get_nets()}
    for nm in num_pins_per_net_1:
        assert num_pins_per_net_1[nm] == num_pins_per_net_2[nm]


def test_lib_1():
    lib_kicad = SchLib("Device")
    lib_kicad.export("Device")
    SchLib.reset()
    lib_skidl = SchLib("Device", tool=SKIDL)
    assert len(lib_kicad) == len(lib_skidl)
    SchLib.reset()
    set_default_tool(SKIDL)
    set_query_backup_lib(False)
    a = Part("Device", "R")
    assert a.tool == SKIDL
    b = Part("Device", "L")
    assert b.tool == SKIDL
    c = Part("Device", "C")
    assert c.tool == SKIDL


def test_non_existing_lib_cannot_be_loaded():
    for tool in ALL_TOOLS:
        with pytest.raises(FileNotFoundError):
            lib = SchLib("non-existing", tool=tool)


def test_part_from_non_existing_lib_cannot_be_instantiated():
    for tool in ALL_TOOLS:
        with pytest.raises(ValueError):
            part = Part("non-existing", "P", tool=tool)
