import logging

import pytest

from skidl import *

from .setup_teardown import *


def test_part_unit_1():
    vreg = Part("xess.lib", "1117")
    vreg.match_pin_regex = True
    vreg.make_unit("A", 1, 2)
    vreg.make_unit("B", 3)
    assert len(vreg.unit["A"][".*"]) == 2
    assert len((vreg.unit["B"][".*"],)) == 1


def test_part_unit_2():
    vreg = Part("xess.lib", "1117")
    vreg.match_pin_regex = True
    vreg.make_unit("A", 1, 2)
    vreg.make_unit("A", 3)
    assert len((vreg.unit["A"][".*"],)) == 1


def test_part_unit_3():
    vreg = Part("xess.lib", "1117")
    vreg.make_unit("1", 1, 2)


def test_part_unit_4():
    mem = Part("xess", "SDRAM_16Mx16_TSOPII-54")
    mem.match_pin_regex = True
    data_pin_names = [p.name for p in mem[".*DQ[0:15].*"]]
    mem.make_unit("A", data_pin_names)
    # Wildcard pin matching OFF globally.
    mem.match_pin_regex = False
    assert mem[".*"] == None
    assert mem.A[".*"] == None
    # Wildcard pin matching ON globally.
    mem.match_pin_regex = True
    assert len(mem[".*"]) != 0
    assert len(mem.A[".*"]) == 16
    # Wildcard matching OFF for part unit, but ON globally.
    mem.A.match_pin_regex = False
    assert len(mem[".*"]) != 0
    assert mem.A[".*"] == None
