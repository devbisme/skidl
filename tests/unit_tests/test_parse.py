# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import os.path

import pytest

from skidl import KICAD, lib_search_paths, netlist_to_skidl
from skidl.utilities import find_and_read_file

from .setup_teardown import setup_function, teardown_function


def test_parser_1():
    skidl_code = netlist_to_skidl(
        find_and_read_file(
            "Arduino_Uno_R3_From_Scratch.net", paths=lib_search_paths[KICAD]
        )[0]
    )
    # FIX: Under Python 2.7, the following line produces "SyntaxError: encoding declaration in Unicode string".
    # compile(skidl_code, "netlist_to_skidl_test_1", "exec")