# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import os.path

import pytest
import sexpdata

import skidl
from skidl import (
    KICAD,
    KICAD5,
    KICAD6,
    KICAD7,
    KICAD8,
    SKIDL,
    TEMPLATE,
    Part,
    Pin,
    SchLib,
    SkidlPart,
    generate_netlist,
    lib_search_paths,
    get_default_tool,
    set_default_tool,
)
from skidl.logger import active_logger
from skidl.pin import pin_types
from skidl.tools import ALL_TOOLS, lib_suffixes
from skidl.utilities import to_list, find_and_read_file

from .setup_teardown import setup_function, teardown_function


def test_missing_lib():
    # Sometimes, loading a part from a non-existent library doesn't throw an
    # exception until the second time it's tried. This detects that error.

    # Don't allow searching backup lib that might exist from previous tests.
    SchLib.reset()
    skidl.config.query_backup_lib = False
    with pytest.raises(FileNotFoundError):
        a = Part("crap", "R")
    with pytest.raises(FileNotFoundError):
        b = Part("crap", "C")


def test_lib_import_1():
    SchLib.reset()
    lib = SchLib("Device")
    assert len(lib) > 0


def test_lib_export_1():
    SchLib.reset()
    lib = SchLib("Device")
    lib.export("my_device", tool=SKIDL, addtl_part_attrs=["value","search_text"])
    my_lib = SchLib("my_device", tool=SKIDL)
    assert len(lib) == len(my_lib)
    assert active_logger.error.count == 0
    my_res = Part(my_lib, "R")
    assert hasattr(my_res, "value")
    assert hasattr(my_res, "search_text")
    assert hasattr(my_res, "name")


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
        Pin(num=1, name="Q1", func=pin_types.TRISTATE),
        Pin(num=2, name="Q2", func=pin_types.PWRIN),
    )
    lib += prt2
    prt2.add_pins(Pin(num=3, name="Q1", func=pin_types.PWROUT))
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
    # Non-existent library so these parts should come from the backup library.
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

def test_backup_3():
    SchLib.reset()
    rn1 = Part("Device", "R_Pack08_Split", footprint="null")
    rn1.uA[1] & rn1.uC[3]
    generate_netlist(do_backup=True)  # This creates the backup parts library.
    default_circuit.reset()
    skidl.config.query_backup_lib = True  # FIXME: this is already True by default!
    # Non-existent library so these parts should come from the backup library.
    rn2 = Part("crap", "R_Pack08_Split", footprint="null")
    # Connect parts using them as units.
    rn2.uA[1] & rn2.uC[3]
    generate_netlist()



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
    assert len(a.pins) == 2
    b = Part("Device", "L")
    assert b.tool == SKIDL
    assert len(b.pins) == 2
    c = Part("Device", "C")
    assert c.tool == SKIDL
    assert len(c.pins) == 2


def test_non_existing_lib_cannot_be_loaded():
    SchLib.reset()
    for tool in ALL_TOOLS:
        with pytest.raises(FileNotFoundError):
            lib = SchLib("non-existing", tool=tool)


def test_part_from_non_existing_lib_cannot_be_instantiated():
    SchLib.reset()
    for tool in ALL_TOOLS:
        with pytest.raises((FileNotFoundError, ValueError)):
            part = Part("non-existing", "P", tool=tool)


def check_lib_part(part):
    part.parse()  # Parse lib part to fully instantiate pins, etc.
    pins = to_list(part.get_pins())
    if not pins:
        raise Exception("Part {} has no pins!".format(part.name))
    unit_pins = []
    for unit in part.unit.values():
        unit_pins.extend(unit.get_pins())
    unit_pins = list(set(unit_pins))  # Remove dups of pins shared between units.
    if part.unit and len(unit_pins) != len(pins):
        raise Exception(
            "Part {} with {} pins in {} units doesn't match {} total part pins!".format(
                part.name, len(unit_pins), len(part.unit), len(pins)
            )
        )
    if len(part.pins) == 0:
        raise Exception("Part {part.name} has no pins: {part.pins}".format(**locals()))


def test_lib_kicad_1():
    SchLib.reset()
    lib_name = "Device"
    lib = SchLib(lib_name)
    part_names = [part.name for part in lib.parts]
    tool = get_default_tool()
    lines = find_and_read_file(
        lib_name, ext=lib_suffixes[tool], paths=lib_search_paths[tool]
    )[0].split("\n")
    part_cnt = len([l for l in lines if l.startswith("ENDDEF")])
    if not part_cnt:
        nested_list = sexpdata.loads("\n".join(lines))
        parts = {
            item[1]: item[2:]
            for item in nested_list[1:]
            if item[0].value().lower() == "symbol"
        }
        part_cnt = len(parts.keys())
    assert part_cnt == len(part_names)
    assert part_cnt in (559, 571, 596, 600)
    for part in lib.parts:
        check_lib_part(part)


def test_lib_kicad_2():
    SchLib.reset()
    lib_name = "4xxx"
    lib = SchLib(lib_name)
    part_names = [part.name for part in lib.parts]
    tool = get_default_tool()
    lines = find_and_read_file(
        lib_name, ext=lib_suffixes[tool], paths=lib_search_paths[tool]
    )[0].split("\n")
    part_cnt = len([l for l in lines if l.startswith("ENDDEF")])
    if not part_cnt:
        nested_list = sexpdata.loads("\n".join(lines))
        parts = {
            item[1]: item[2:]
            for item in nested_list[1:]
            if item[0].value().lower() == "symbol"
        }
        part_cnt = len(parts.keys())
    assert part_cnt == len(part_names)
    assert part_cnt in (44, 48, 49, 51)
    for part in lib.parts:
        check_lib_part(part)


def test_lib_kicad_top_level_pins():
    SchLib.reset()
    lib_name = "ecad_example"
    try:
        lib = SchLib(lib_name)
    except FileNotFoundError:
        # No test library exists for this tool.
        return
    # lib = SchLib(lib_name, tool=tool)
    tool = get_default_tool()
    part_names = [part.name for part in lib.parts]
    sexp, _ = find_and_read_file(
        lib_name, ext=lib_suffixes[tool], paths=lib_search_paths[tool]
    )
    nested_list = sexpdata.loads(sexp)
    parts = {
        item[1]: item[2:]
        for item in nested_list[1:]
        if item[0].value().lower() == "symbol"
    }
    assert len(parts.keys()) == len(part_names)
    for name in parts.keys():
        part = lib[name]
    for part in lib.parts:
        check_lib_part(part)


def test_lib_kicad_repository():
    SchLib.reset()
    tool = get_default_tool()
    repo_urls = {
        KICAD: "https://raw.githubusercontent.com/KiCad/kicad-symbols/master/",
        KICAD5: "https://raw.githubusercontent.com/KiCad/kicad-symbols/master/",
        KICAD6: "https://gitlab.com/kicad/libraries/kicad-symbols/-/raw/master",
        KICAD7: "https://gitlab.com/kicad/libraries/kicad-symbols/-/raw/master",
        KICAD8: "https://gitlab.com/kicad/libraries/kicad-symbols/-/raw/master",
    }
    lib_name = "4xxx"
    lib_search_paths[tool] = [repo_urls[tool]]
    lib_4xxx = SchLib(lib_name)
    assert len(lib_4xxx.parts) > 0
    for part in lib_4xxx.parts:
        check_lib_part(part)
