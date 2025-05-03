# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import os
import os.path

import pytest

import skidl
from skidl import (
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
from skidl.utilities import to_list, find_and_read_file, sexp_to_nested_list

from .setup_teardown import setup_function, teardown_function


def test_missing_lib():
    """Test loading a part from a non-existent library."""
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
    """Test importing a library."""
    # Reset the library.
    SchLib.reset()
    # Import the library.
    lib = SchLib("Device")
    # Assert that the library has parts.
    assert len(lib) > 0


def test_lib_export_1():
    """Test exporting a library."""
    # Reset the library.
    SchLib.reset()
    # Import the library.
    lib = SchLib("Device")
    # Export the library.
    lib.export("./my_device", tool=SKIDL, addtl_part_attrs=["value", "search_text"])
    # Import the exported library.
    my_lib = SchLib("./my_device", tool=SKIDL)
    # Assert that the original and exported libraries have the same number of parts.
    assert len(lib) == len(my_lib)
    # Assert that there are no errors in the logger.
    assert active_logger.error.count == 0
    # Instantiate a part from the exported library.
    my_res = Part(my_lib, "R")
    # Assert that the part has the specified attributes.
    assert hasattr(my_res, "value")
    assert hasattr(my_res, "search_text")
    assert hasattr(my_res, "name")


def test_lib_creation_1():
    """Test creating a library."""
    # Reset the library.
    SchLib.reset()
    # Create a new library.
    lib = SchLib()
    # Create a new part.
    prt1 = SkidlPart(name="Q", dest=TEMPLATE)
    # Add the part to the library.
    lib += prt1
    # Add the part again (duplicate entries are not added).
    lib += prt1
    # Assert that the library has only one part.
    assert len(lib.parts) == 1
    # Assert that a non-existent part is not in the library.
    assert not lib.get_parts(name="QQ")
    # Create another part.
    prt2 = SkidlPart(name="QQ", dest=TEMPLATE)
    # Add pins to the part.
    prt2.add_pins(
        Pin(num=1, name="Q1", func=pin_types.TRISTATE),
        Pin(num=2, name="Q2", func=pin_types.PWRIN),
    )
    # Add the part to the library.
    lib += prt2
    # Add another pin to the part.
    prt2.add_pins(Pin(num=3, name="Q1", func=pin_types.PWROUT))
    # Assert that the library has two parts.
    assert len(lib.parts) == 2
    # Assert that the first part has no pins.
    assert lib["Q"].name == "Q"
    assert len(lib["Q"].pins) == 0
    # Assert that the second part has two pins.
    assert lib["QQ"].name == "QQ"
    assert len(lib["QQ"].pins) == 2


def test_backup_1():
    """Test creating a backup parts library."""
    # Reset the library.
    SchLib.reset()
    # Create parts.
    a = Part("Device", "R", footprint="null")
    b = Part("Device", "C", footprint="null")
    c = Part("Device", "L", footprint="null")
    # Connect parts to keep them from being culled.
    a & b & c
    # Generate netlist and create backup parts library.
    generate_netlist(do_backup=True)
    # Reset the circuit.
    default_circuit.reset()
    # Enable querying the backup library.
    skidl.config.query_backup_lib = True
    # Instantiate parts from the non-existent library (should come from backup library).
    a = Part("crap", "R", footprint="null")
    b = Part("crap", "C", footprint="null")
    # Generate netlist.
    generate_netlist()


def test_backup_2():
    """Test backup parts library with netlist generation."""
    # Reset the library.
    SchLib.reset()
    # Create parts.
    a = Part("Device", "R", footprint="null")
    b = Part("Device", "C", footprint="null")
    c = Part("Device", "L", footprint="null")
    # Place parts in series.
    a & b & c
    # Get the number of pins per net before generating netlist.
    num_pins_per_net_1 = {net.name: len(net) for net in default_circuit.nets}
    # Generate netlist and create backup parts library.
    generate_netlist(do_backup=True)
    # Get the number of pins per net after generating netlist.
    num_pins_per_net_2 = {net.name: len(net) for net in default_circuit.nets}
    # Assert that the number of pins per net is the same before and after generating netlist.
    for nm in num_pins_per_net_1:
        assert num_pins_per_net_1[nm] == num_pins_per_net_2[nm]


def test_backup_3():
    """Test backup parts library with unit connections."""
    # Reset the library.
    SchLib.reset()
    # Create a part with units.
    rn1 = Part("Device", "R_Pack08_Split", footprint="null")
    # Connect units of the part.
    rn1.uA[1] & rn1.uC[3]
    # Generate netlist and create backup parts library.
    generate_netlist(do_backup=True)
    # Reset the circuit.
    default_circuit.reset()
    # Enable querying the backup library.
    skidl.config.query_backup_lib = True
    # Instantiate part from the non-existent library (should come from backup library).
    rn2 = Part("crap", "R_Pack08_Split", footprint="null")
    # Connect units of the part.
    rn2.uA[1] & rn2.uC[3]
    # Generate netlist.
    generate_netlist()


def test_lib_1():
    """Test library import and export."""
    # Reset the library.
    SchLib.reset()
    # Import the KiCad library.
    lib_kicad = SchLib("Device")
    # Export the library.
    lib_kicad.export("Device")
    # Reset the library.
    SchLib.reset()
    # Import the exported library.
    lib_skidl = SchLib("./Device", tool=SKIDL)
    # Assert that the original and exported libraries have the same number of parts.
    assert len(lib_kicad) == len(lib_skidl)
    # Reset the library.
    SchLib.reset()
    # Set the default tool to SKIDL.
    set_default_tool(SKIDL)
    # Disable querying the backup library.
    skidl.config.query_backup_lib = False
    # Instantiate parts from the library.
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
    """Test loading a non-existing library."""
    # Reset the library.
    SchLib.reset()
    # Try to load a non-existing library for each tool.
    for tool in ALL_TOOLS:
        with pytest.raises(FileNotFoundError):
            lib = SchLib("non-existing", tool=tool)


def test_part_from_non_existing_lib_cannot_be_instantiated():
    """Test instantiating a part from a non-existing library."""
    # Reset the library.
    SchLib.reset()
    # Try to instantiate a part from a non-existing library for each tool.
    for tool in ALL_TOOLS:
        with pytest.raises((FileNotFoundError, ValueError)):
            part = Part("non-existing", "P", tool=tool)


def check_lib_part(part):
    """Check the integrity of a library part."""
    # Parse lib part to fully instantiate pins, etc.
    part.parse()
    # Get the list of pins.
    pins = to_list(part.get_pins())
    # Raise an exception if the part has no pins.
    if not pins:
        raise Exception("Part {} has no pins!".format(part.name))
    # Get the list of pins for each unit.
    unit_pins = []
    for unit in part.unit.values():
        unit_pins.extend(unit.get_pins())
    # Remove duplicates of pins shared between units.
    unit_pins = list(set(unit_pins))
    # Raise an exception if the number of pins in the units doesn't match the total number of pins.
    if part.unit and len(unit_pins) != len(pins):
        raise Exception(
            "Part {} with {} pins in {} units doesn't match {} total part pins!".format(
                part.name, len(unit_pins), len(part.unit), len(pins)
            )
        )
    # Raise an exception if the part has no pins.
    if len(part.pins) == 0:
        raise Exception("Part {part.name} has no pins: {part.pins}".format(**locals()))


def test_lib_kicad_1():
    """Test KiCad library import and part checking."""
    # Reset the library.
    SchLib.reset()
    # Set the library name.
    lib_name = "Device"
    # Import the library.
    lib = SchLib(lib_name)
    # Get the list of part names.
    part_names = [part.name for part in lib.parts]
    # Get the default tool.
    tool = get_default_tool()
    # Read the library file.
    lines = find_and_read_file(
        lib_name, ext=lib_suffixes[tool], paths=lib_search_paths[tool]
    )[0].split("\n")
    # Count the number of parts in the library file.
    part_cnt = len([l for l in lines if l.startswith("ENDDEF")])
    # If no parts are found, parse the library file as an S-expression.
    if not part_cnt:
        nested_list = sexp_to_nested_list("\n".join(lines))
        parts = {
            item[1]: item[2:]
            for item in nested_list[1:]
            if item[0].lower() == "symbol"
        }
        part_cnt = len(parts.keys())
    # Assert that the number of parts in the library file matches the number of parts in the library.
    assert part_cnt == len(part_names)
    # Assert that the number of parts is within the expected range.
    assert part_cnt in (559, 571, 596, 600)
    # Check the integrity of each part in the library.
    for part in lib.parts:
        check_lib_part(part)


def test_lib_kicad_2():
    """Test another KiCad library import and part checking."""
    # Reset the library.
    SchLib.reset()
    # Set the library name.
    lib_name = "4xxx"
    # Import the library.
    lib = SchLib(lib_name)
    # Get the list of part names.
    part_names = [part.name for part in lib.parts]
    # Get the default tool.
    tool = get_default_tool()
    # Read the library file.
    lines = find_and_read_file(
        lib_name, ext=lib_suffixes[tool], paths=lib_search_paths[tool]
    )[0].split("\n")
    # Count the number of parts in the library file.
    part_cnt = len([l for l in lines if l.startswith("ENDDEF")])
    # If no parts are found, parse the library file as an S-expression.
    if not part_cnt:
        nested_list = sexp_to_nested_list("\n".join(lines))
        parts = {
            item[1]: item[2:]
            for item in nested_list[1:]
            if item[0].lower() == "symbol"
        }
        part_cnt = len(parts.keys())
    # Assert that the number of parts in the library file matches the number of parts in the library.
    assert part_cnt == len(part_names)
    # Assert that the number of parts is within the expected range.
    assert part_cnt in (44, 48, 49, 51)
    # Check the integrity of each part in the library.
    for part in lib.parts:
        check_lib_part(part)


def test_lib_kicad_top_level_pins():
    """Test KiCad library with top-level pins."""
    # Reset the library.
    SchLib.reset()
    # Set the library name.
    lib_name = "ecad_example"
    try:
        # Try to import the library.
        lib = SchLib(lib_name)
    except FileNotFoundError:
        # No test library exists for this tool.
        return
    # Get the default tool.
    tool = get_default_tool()
    # Get the list of part names.
    part_names = [part.name for part in lib.parts]
    # Open the .kicad_sym file and get the S-expression for each part.
    sexp, _ = find_and_read_file(
        lib_name, ext=lib_suffixes[tool], paths=lib_search_paths[tool]
    )
    nested_list = sexp_to_nested_list(sexp)
    parts = {
        item[1]: item[2:]
        for item in nested_list[1:]
        if item[0].value().lower() == "symbol"
    }
    # Assert that the number of parts in the library file matches the number of parts in the library.
    assert len(parts.keys()) == len(part_names)
    # Check the integrity of each part in the library.
    for name in parts.keys():
        part = lib[name]
    for part in lib.parts:
        check_lib_part(part)


def test_lib_kicad_repository():
    """Test KiCad library repository."""
    # Reset the library.
    SchLib.reset()
    # Get the default tool.
    tool = get_default_tool()
    # Set the repository URLs for each tool.
    repo_urls = {
        KICAD5: "https://raw.githubusercontent.com/KiCad/kicad-symbols/master/",
        KICAD6: "https://gitlab.com/kicad/libraries/kicad-symbols/-/raw/master",
        KICAD7: "https://gitlab.com/kicad/libraries/kicad-symbols/-/raw/master",
        KICAD8: "https://gitlab.com/kicad/libraries/kicad-symbols/-/raw/master",
    }
    # Set the library name.
    lib_name = "4xxx"
    # Set the search paths to the repository URL.
    lib_search_paths[tool] = [repo_urls[tool]]
    # Import the library from the repository.
    lib_4xxx = SchLib(lib_name)
    # Assert that the library has parts.
    assert len(lib_4xxx.parts) > 0
    # Check the integrity of each part in the library.
    for part in lib_4xxx.parts:
        check_lib_part(part)

# Skip this test for KiCad 5 since the custom library doesn't exist in the KiCad 5 format.
@pytest.mark.skipif(os.environ.get('SKIDL_TOOL', '')=='KICAD5', reason="Custom library not available in KiCad 5")
def test_lib_custom():
    """Test custom library."""
    # Reset the library.
    SchLib.reset()
    # Set the library name.
    lib_name = "220-3342-00-0602J"
    # Create a custom library.
    lib = SchLib(lib_name)
    # Check that the part can be instantiated.
    part = lib["220-3342-00-0602J"]
