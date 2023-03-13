# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import os.path

import pytest

from skidl import KICAD, lib_search_paths, netlist_to_skidl
from skidl.utilities import find_and_read_file

from .setup_teardown import setup_function, teardown_function


def test_parser_1():
    netlist_to_skidl(
        find_and_read_file(
            "Arduino_Uno_R3_From_Scratch.net", paths=lib_search_paths[KICAD]
        )[0]
    )
