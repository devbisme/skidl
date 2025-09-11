# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import search


def test_search_1(capfd):
    search("ESP32")  # Find matches in RF_Module library.
    out, err = capfd.readouterr() # Capture standard output and error.
    
    # KICAD 5 uses .lib files, while later versions use .kicad_sym files. And the
    # RF_Module library has different # of parts in it for various versions of KiCad.
    assert out.count("RF_Module:") in (4,6,11,14,18)

