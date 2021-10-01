# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import netlist_to_skidl

from .setup_teardown import setup_function, teardown_function, get_filename


def test_parser_1():
    netlist_to_skidl(get_filename("Arduino_Uno_R3_From_Scratch.net"))
