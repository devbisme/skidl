# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import os

from skidl import *
from skidl.tools import ALL_TOOLS

this_file_dir = os.path.dirname(os.path.abspath(__file__))

files_at_start = set([])


def setup_function(f):
    # Record files originally in directory so we know which ones not to delete.
    global files_at_start
    files_at_start = set(os.listdir(os.getcwd()))

    # Mini-reset to remove circuitry but retain any loaded libraries.
    default_circuit.mini_reset()

    # Setup part library search paths.
    for tool in ALL_TOOLS:
        # Each tool has a specific directory that stores the libraries used for testing.
        lib_dir = os.path.join(this_file_dir, "..", "test_data", tool)
        lib_search_paths[tool] = [os.getcwd(), lib_dir]

    # Extra library directory for SKiDL tool.
    skidl_lib_dir = os.path.join(this_file_dir, "../..", "src/skidl/libs")
    lib_search_paths[SKIDL].append(skidl_lib_dir)

    # SPICE models from the SkyWater 130nm process.
    skywater_lib_dir = os.path.join(this_file_dir, "..", "test_data", "skywater", "models")
    lib_search_paths[SPICE].append(skywater_lib_dir)

    spice_lib_dir = os.path.join(this_file_dir, "..", "test_data", "SpiceLib")
    lib_search_paths[SPICE].append(spice_lib_dir)

    skidl.config.query_backup_lib = True

    # Set the default tool for the test suite.
    tool = KICAD8
    set_default_tool(tool)


def teardown_function(f):
    # Delete files created during testing.
    files_at_end = set(os.listdir(os.getcwd()))
    for file in files_at_end - files_at_start:
        try:
            os.remove(file)
        except Exception:
            pass


if __name__ == "__main__":
    setup_function(None)
    with open("test.txt", "wb") as f:
        f.write("test")
    teardown_function(None)
