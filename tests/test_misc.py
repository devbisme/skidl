# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import Net, Part

from .setup_teardown import setup_function, teardown_function


def test_string_indices_1():
    vreg1 = Part("xess.lib", "1117", footprint="null")
    gnd = Net("GND")
    vin = Net("Vin")
    vreg1["GND, IN, OUT"] += gnd, vin, vreg1["HS"]
    assert vreg1.is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vreg1["IN"].net) == 1
    assert len(vreg1["HS"].net) == 2
    assert len(vreg1["OUT"].net) == 2
    assert vreg1["OUT"].net.is_attached(vreg1["HS"].net)
