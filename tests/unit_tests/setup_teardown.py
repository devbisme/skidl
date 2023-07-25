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
    lib_search_paths.clear()
    lib_dir = os.path.join(this_file_dir, "..", "test_data")
    lib_search_paths.update({tool: [os.getcwd(), lib_dir] for tool in ALL_TOOLS})

    skidl_lib_dir = os.path.join(this_file_dir, "../..", "src/skidl/libs")
    lib_search_paths[SKIDL].append(skidl_lib_dir)

    skywater_lib_dir = (
        "/home/devb/tmp/skywater-pdk/libraries/sky130_fd_pr/latest/models"
    )
    lib_search_paths[SPICE].append(skywater_lib_dir)

    skidl.config.tool = KICAD
    skidl.config.query_backup_lib = True


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
