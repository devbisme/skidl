# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import search, set_default_tool, KICAD, KICAD6, KICAD7

from .setup_teardown import setup_function, teardown_function


def test_search_1(capfd):
    set_default_tool(KICAD)
    search("pic18f")  # Should find 11 matches in xess.lib.
    out, err = capfd.readouterr()
    assert out.count("xess.lib:") == 11

def test_search_2(capfd):
    set_default_tool(KICAD6)
    search("ESP32")  # Should find 6 matches in RF_Module.kicad_sym.
    out, err = capfd.readouterr()
    assert out.count("RF_Module.kicad_sym:") == 6

def test_search_3(capfd):
    set_default_tool(KICAD7)
    search("ESP32")  # Should find 6 matches in RF_Module.kicad_sym.
    out, err = capfd.readouterr()
    assert out.count("RF_Module.kicad_sym:") == 6
