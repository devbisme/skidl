# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import TEMPLATE, Part, generate_netlist

from .setup_teardown import setup_function, teardown_function


def test_skidl_loc():
    rt = Part("Device", "R", dest=TEMPLATE, footprint="null")
    r1 = rt()
    resistors = rt(5)
    generate_netlist()
