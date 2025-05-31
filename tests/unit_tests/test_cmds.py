# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import search

from .setup_teardown import setup_function, teardown_function


def test_search_1(capfd):
    search("ESP32")  # Find matches in RF_Module library.
    out, err = capfd.readouterr() # Capture standard output and error.
    
    # KICAD 5 uses .lib files, while later versions use .kicad_sym files. And the
    # RF_Module library has different # of parts in it for various versions of KiCad.
    assert (out.count("RF_Module.lib:"), out.count("RF_Module.kicad_sym:")) in ((6,0), (0,6), (0,12), (0,14), (0,19))

