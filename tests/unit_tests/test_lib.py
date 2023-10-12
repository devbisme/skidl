# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import os.path

import pytest
import sexpdata

import skidl
from skidl import (
    KICAD,
    KICAD6,
    KICAD7,
    SKIDL,
    TEMPLATE,
    Part,
    Pin,
    SchLib,
    SkidlPart,
    generate_netlist,
    lib_search_paths,
    set_default_tool,
)
from skidl.tools import ALL_TOOLS, lib_suffixes
from skidl.utilities import to_list, find_and_read_file

from .setup_teardown import setup_function, teardown_function


def test_missing_lib():
    # Sometimes, loading a part from a non-existent library doesn't throw an
    # exception until the second time it's tried. This detects that error.
    
    # Don't allow searching backup lib that might exist from previous tests.
    SchLib.reset()
    skidl.config.query_backup_lib=False
    with pytest.raises(FileNotFoundError):
        a = Part("crap", "R")
    with pytest.raises(FileNotFoundError):
        b = Part("crap", "C")


def test_lib_import_1():
    SchLib.reset()
    lib = SchLib("xess.lib")
    assert len(lib) > 0


def test_lib_import_2():
    SchLib.reset()
    lib = SchLib("Device")


def test_lib_export_1():
    SchLib.reset()
    lib = SchLib("Device")
    lib.export("my_device", tool=SKIDL)
    my_lib = SchLib("my_device", tool=SKIDL)
    assert len(lib) == len(my_lib)


def test_lib_creation_1():
    SchLib.reset()
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
    SchLib.reset()
    a = Part("Device", "R", footprint="null")
    b = Part("Device", "C", footprint="null")
    c = Part("Device", "L", footprint="null")
    a & b & c  # Connect device to keep them from being culled.
    generate_netlist(do_backup=True)  # This creates the backup parts library.
    default_circuit.reset()
    skidl.config.query_backup_lib = True  # FIXME: this is already True by default!
    a = Part("crap", "R", footprint="null")
    b = Part("crap", "C", footprint="null")
    generate_netlist()


def test_backup_2():
    SchLib.reset()
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
    SchLib.reset()
    lib_kicad = SchLib("Device")
    lib_kicad.export("Device")
    SchLib.reset()
    lib_skidl = SchLib("Device", tool=SKIDL)
    assert len(lib_kicad) == len(lib_skidl)
    SchLib.reset()
    set_default_tool(SKIDL)
    skidl.config.query_backup_lib = False
    a = Part("Device", "R")
    assert a.tool == SKIDL
    b = Part("Device", "L")
    assert b.tool == SKIDL
    c = Part("Device", "C")
    assert c.tool == SKIDL


def test_non_existing_lib_cannot_be_loaded():
    SchLib.reset()
    for tool in ALL_TOOLS:
        with pytest.raises(FileNotFoundError):
            lib = SchLib("non-existing", tool=tool)


def test_part_from_non_existing_lib_cannot_be_instantiated():
    SchLib.reset()
    for tool in ALL_TOOLS:
        with pytest.raises(FileNotFoundError):
            part = Part("non-existing", "P", tool=tool)


def check_lib_part(part):
    part.parse()  # Parse lib part to fully instantiate pins, etc.
    pins = to_list(part.get_pins())
    if not pins:
        raise Exception("Part {} has no pins!".format(part.name))
    unit_pins = []
    for unit in part.unit.values():
        unit_pins.extend(unit.get_pins())
    if part.unit and len(unit_pins) != len(pins):
        raise Exception("Part {} with {} pins in {} units doesn't match {} total part pins!".format(part.name, len(unit_pins), len(part.unit), len(pins)))
    if len(part.pins) == 0:
        raise Exception("Part {part.name} has no pins: {part.pins}".format(**locals()))

def test_lib_kicad_v5():
    SchLib.reset()
    lib_name = "Device"
    lib_v5 = SchLib(lib_name)
    v5_part_names = [part.name for part in lib_v5.parts]
    lines = find_and_read_file(lib_name, ext=lib_suffixes[KICAD], paths=lib_search_paths[KICAD])[0].split("\n")
    part_cnt = len([l for l in lines if l.startswith("ENDDEF")])
    print("# of parts in {} = {}".format(lib_name, part_cnt))
    assert part_cnt == len(v5_part_names)
    assert part_cnt == 502
    for part in lib_v5.parts:
        check_lib_part(part)


def test_lib_kicad_v6_1():
    SchLib.reset()
    lib_name = "Device"
    lib_v6 = SchLib(lib_name, tool=KICAD6)
    v6_part_names = [part.name for part in lib_v6.parts]
    sexp, _ = find_and_read_file(lib_name, ext=lib_suffixes[KICAD7], paths=lib_search_paths[KICAD6])
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
    for part in lib_v6.parts:
        check_lib_part(part)


def test_lib_kicad_v6_2():
    SchLib.reset()
    lib_name = "4xxx"
    lib_v6 = SchLib(lib_name, tool=KICAD6)
    v6_part_names = [part.name for part in lib_v6.parts]
    sexp, _ = find_and_read_file(lib_name, ext=lib_suffixes[KICAD6], paths=lib_search_paths[KICAD6])
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
    for part in lib_v6.parts:
        check_lib_part(part)


def test_lib_kicad_v7_1():
    SchLib.reset()
    lib_name = "Device"
    lib_v7 = SchLib(lib_name, tool=KICAD7)
    v7_part_names = [part.name for part in lib_v7.parts]
    sexp, _ = find_and_read_file(lib_name, ext=lib_suffixes[KICAD7], paths=lib_search_paths[KICAD7])
    nested_list = sexpdata.loads(sexp)
    parts = {
        item[1]: item[2:]
        for item in nested_list[1:]
        if item[0].value().lower() == "symbol"
    }
    print("# of parts in {} = {}".format(lib_name, len(lib_v7.parts)))
    assert len(parts.keys()) == len(v7_part_names)
    for name in parts.keys():
        part = lib_v7[name]
    for part in lib_v7.parts:
        check_lib_part(part)


def test_lib_kicad_v7_2():
    SchLib.reset()
    lib_name = "4xxx"
    lib_v7 = SchLib(lib_name, tool=KICAD7)
    v7_part_names = [part.name for part in lib_v7.parts]
    sexp, _ = find_and_read_file(lib_name, ext=lib_suffixes[KICAD7], paths=lib_search_paths[KICAD7])
    nested_list = sexpdata.loads(sexp)
    parts = {
        item[1]: item[2:]
        for item in nested_list[1:]
        if item[0].value().lower() == "symbol"
    }
    print("# of parts in {} = {}".format(lib_name, len(lib_v7.parts)))
    assert len(parts.keys()) == len(v7_part_names)
    for name in parts.keys():
        part = lib_v7[name]
    for part in lib_v7.parts:
        check_lib_part(part)

def test_lib_kicad_ecad_v7_2():
    SchLib.reset()
    lib_name = "ecad_example"
    lib_v7 = SchLib(lib_name, tool=KICAD7)
    v7_part_names = [part.name for part in lib_v7.parts]
    sexp, _ = find_and_read_file(lib_name, ext=lib_suffixes[KICAD7], paths=lib_search_paths[KICAD7])
    nested_list = sexpdata.loads(sexp)
    parts = {
        item[1]: item[2:]
        for item in nested_list[1:]
        if item[0].value().lower() == "symbol"
    }
    print("# of parts in {} = {}".format(lib_name, len(lib_v7.parts)))
    assert len(parts.keys()) == len(v7_part_names)
    for name in parts.keys():
        part = lib_v7[name]
    for part in lib_v7.parts:
        check_lib_part(part)

def test_lib_kicad5_repository():
    SchLib.reset()
    lib_name = "4xxx"
    repo_url = "https://raw.githubusercontent.com/KiCad/kicad-symbols/master/"
    lib_search_paths[KICAD] = [repo_url]
    lib_4xxx = SchLib(lib_name, tool=KICAD)
    print("# of parts in {} = {}".format(lib_name, len(lib_4xxx.parts)))
    for part in lib_4xxx.parts:
        check_lib_part(part)


def test_lib_kicad6_repository():
    SchLib.reset()
    lib_name = "4xxx"
    repo_url = "https://gitlab.com/kicad/libraries/kicad-symbols/-/raw/master"
    lib_search_paths[KICAD6] = [repo_url]
    lib_4xxx = SchLib(lib_name, tool=KICAD6)
    print("# of parts in {} = {}".format(lib_name, len(lib_4xxx.parts)))
    for part in lib_4xxx.parts:
        check_lib_part(part)