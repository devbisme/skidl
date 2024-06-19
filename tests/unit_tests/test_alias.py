# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Part

from .setup_teardown import setup_function, teardown_function


def test_alias_1():
    LED = Part("Device", "LED_ABGR")
    LED.match_pin_regex = True
    LED.p1.aliases += "my_alias"
    LED.p2.aliases += "my_alias"
    assert len(LED["my_alias"]) == 2
    assert len(LED.my_alias) == 2
    assert len(LED[".*"]) == 4


def test_alias_2():
    LED = Part("Device", "LED_ABGR")
    LED.match_pin_regex = True
    LED[1].aliases = "my_alias_+"
    LED[2].aliases = "my_alias_+"
    LED[2].aliases += "my_other_alias"
    assert len(LED["my_alias_+"]) == 2
    assert len((LED["my_other_alias"],)) == 1
    assert len(LED[".*"]) == 4
    with pytest.raises(NotImplementedError):
        LED["my_alias_+"].aliases = "new_alias"


def test_alias_3():
    LED = Part("Device", "LED_ABGR")
    LED[1].name = "AB/BC|DC|ED"
    LED.split_pin_names("/|")
    assert LED[1] is LED.AB
    assert LED["AB"] is LED.BC
    assert LED[1] is LED.DC
    assert LED["DC"] is LED.ED
    LED2 = LED()
    assert LED2[1] is LED2.AB
    assert LED2["AB"] is LED2.BC
    assert LED2[1] is LED2.DC
    assert LED2["DC"] is LED2.ED
