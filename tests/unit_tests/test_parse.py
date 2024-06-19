# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import os.path

import pytest

from skidl import Part, netlist_to_skidl, generate_netlist, TEMPLATE
from skidl.utilities import find_and_read_file

from .setup_teardown import setup_function, teardown_function


def test_parser_1():
    r = Part("Device", "R", dest=TEMPLATE)
    c = Part("Device", "C", dest=TEMPLATE)
    (r(value=0.001) | c(value=0.001)) & (r(value=0.002) | c(value=0.002))
    generate_netlist(file_="test_parser_1.net")
    skidl_code = netlist_to_skidl(find_and_read_file("test_parser_1.net")[0])
