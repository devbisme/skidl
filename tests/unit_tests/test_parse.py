# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import os.path
import pytest

from skidl import netlist_to_skidl

from .setup_teardown import setup_function, teardown_function


def test_parser_1():
    this_file_dir = os.path.dirname(os.path.abspath(__file__))
    net_filename = os.path.join(
        this_file_dir, "..", "test_data", "Arduino_Uno_R3_From_Scratch.net"
    )
    netlist_to_skidl(net_filename)
