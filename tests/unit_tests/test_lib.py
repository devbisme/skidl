# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import os.path

import pytest
import sexpdata

from skidl import (
    KICAD,
    SKIDL,
    TEMPLATE,
    Part,
    Pin,
    SchLib,
    SkidlPart,
    generate_netlist,
    lib_search_paths,
    set_default_tool,
    set_query_backup_lib,
)
from skidl.tools import ALL_TOOLS
from skidl.utilities import find_and_read_file

from .setup_teardown import setup_function, teardown_function


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
    a & b & c  # Connect device to keep them from being culled.
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
    num_pins_per_net_1 = {net.name: len(net) for net in default_circuit.nets}
    generate_netlist(do_backup=True)  # This creates the backup parts library.
    num_pins_per_net_2 = {net.name: len(net) for net in default_circuit.nets}
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


def test_lib_kicad_v5():
    lib_name = "Device.lib"
    lib_v5 = SchLib(lib_name)
    v5_part_names = [part.name for part in lib_v5.parts]
    lines = find_and_read_file(lib_name, paths=lib_search_paths[KICAD])[0].split("\n")
    part_cnt = len([l for l in lines if l.startswith("ENDDEF")])
    print("# of parts in {} = {}".format(lib_name, part_cnt))
    assert part_cnt == len(v5_part_names)
    assert part_cnt == 502


def test_lib_kicad_v6_1():
    lib_name = "Device.kicad_sym"
    lib_v6 = SchLib(lib_name)
    v6_part_names = [part.name for part in lib_v6.parts]
    sexp, _ = find_and_read_file(lib_name, paths=lib_search_paths[KICAD])
    nested_list = sexpdata.loads(sexp)
    parts = {
        item[1]: item[2:]
        for item in nested_list[1:]
        if item[0].value().lower() == "symbol"
    }
    print("# of parts in {} = {}".format(lib_name, len(lib_v6.parts)))
    assert len(parts.keys()) == len(v6_part_names)
    for name in parts.keys():
        part = lib_v6[name]


def test_lib_kicad_v6_2():
    lib_name = "4xxx.kicad_sym"
    lib_v6 = SchLib(lib_name)
    v6_part_names = [part.name for part in lib_v6.parts]
    sexp, _ = find_and_read_file(lib_name, paths=lib_search_paths[KICAD])
    nested_list = sexpdata.loads(sexp)
    parts = {
        item[1]: item[2:]
        for item in nested_list[1:]
        if item[0].value().lower() == "symbol"
    }
    print("# of parts in {} = {}".format(lib_name, len(lib_v6.parts)))
    assert len(parts.keys()) == len(v6_part_names)
    for name in parts.keys():
        part = lib_v6[name]


def test_lib_kicad5_repository():
    repo_url = "https://raw.githubusercontent.com/KiCad/kicad-symbols/master/"
    lib_search_paths[KICAD] = [repo_url]
    lib_4xxx = SchLib("4xxx.lib")


def test_lib_kicad6_repository():
    repo_url = "https://gitlab.com/kicad/libraries/kicad-symbols/-/raw/master"
    lib_search_paths[KICAD] = [repo_url]
    lib_4xxx = SchLib("4xxx.kicad_sym")
