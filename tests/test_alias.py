# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import Part

from .setup_teardown import setup_function, teardown_function


def test_alias_1():
    vreg = Part("xess.lib", "1117")
    vreg.match_pin_regex = True
    vreg.set_pin_alias("my_alias", 1)
    vreg.set_pin_alias("my_alias", 2)
    assert len(vreg["my_alias"]) == 2
    assert len(vreg[".*"]) == 4


def test_alias_2():
    vreg = Part("xess.lib", "1117")
    vreg.set_pin_alias("my_alias", 1)
    vreg.set_pin_alias("my_alias", 2)
    with pytest.raises(ValueError):
        vreg.set_pin_alias("new_alias", "my_alias")


def test_alias_3():
    vreg = Part("xess.lib", "1117")
    vreg.match_pin_regex = True
    vreg[1].aliases = "my_alias_+"
    vreg[2].aliases = "my_alias_+"
    vreg[2].aliases += "my_other_alias"
    assert len(vreg["my_alias_+"]) == 2
    assert len((vreg["my_other_alias"],)) == 1
    assert len(vreg[".*"]) == 4
    with pytest.raises(NotImplementedError):
        vreg["my_alias_+"].aliases = "new_alias"

def test_alias_4():
    vreg = Part('xess.lib', '1117')
    vreg[1].name = 'AB/BC|DC|ED'
    vreg.split_pin_names('/|')
    assert(vreg[1] is vreg.AB)
    assert(vreg['AB'] is vreg.BC)
    assert(vreg[1] is vreg.DC)
    assert(vreg['DC'] is vreg.ED)
    vreg2 = vreg()
    assert(vreg2[1] is vreg2.AB)
    assert(vreg2['AB'] is vreg2.BC)
    assert(vreg2[1] is vreg2.DC)
    assert(vreg2['DC'] is vreg2.ED)
