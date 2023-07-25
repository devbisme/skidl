# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import search

from .setup_teardown import setup_function, teardown_function


def test_search_1(capfd):
    search("pic18f")  # Should find 11 matches in xess.lib.
    out, err = capfd.readouterr()
    assert out.count("xess.lib:") == 11
