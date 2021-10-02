# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import TEMPLATE, Net, Part, package

from .setup_teardown import setup_function, teardown_function


def test_package_keyword_only_args():
    """Test package keyword-only arguments"""

    @package
    def resistor(vin, gnd, *, value):
        vin & Part("Device", "R", dest=TEMPLATE, value=value) & gnd

    res = resistor(value="1K")
    vin, gnd = Net("VI"), Net("GND")

    res.vin = vin
    res.gnd = gnd
