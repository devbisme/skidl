import pytest

from skidl import *

from .setup_teardown import *


def test_search_1(capfd):
    search("pic18f")  # Should find 11 matches in xess.lib.
    out, err = capfd.readouterr()
    assert out.count("xess.lib:") == 11
