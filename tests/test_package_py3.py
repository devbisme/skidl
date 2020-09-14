import pytest

from skidl import *

from .setup_teardown import *


def test_package_keyword_only_args():
    """Test package keyword-only arguments"""

    @package
    def resistor(vin, gnd, *, value):
        vin & Part("Device", "R", dest=TEMPLATE, value=value) & gnd

    res = resistor(value='1K')
    vin, gnd = Net("VI"), Net("GND")

    res.vin = vin
    res.gnd = gnd

