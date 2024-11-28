# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Part

from .setup_teardown import setup_function, teardown_function


def test_alias_1():
    """Test adding and accessing pin aliases for a Part object."""
    # Create a Part object for an LED.
    LED = Part("Device", "LED_ABGR")
    # Enable regex matching for pin names.
    LED.match_pin_regex = True
    # Add aliases to the pins.
    LED.p1.aliases += "my_alias"
    LED.p2.aliases += "my_alias"
    # Count the number of pins fetched to see if the aliases were added correctly.
    assert len(LED["my_alias"]) == 2
    assert len(LED.my_alias) == 2
    assert len(LED[".*"]) == 4


def test_alias_2():
    """Test the aliasing functionality of the Part object for an LED."""
    # Create a Part object for an LED.
    LED = Part("Device", "LED_ABGR")
    # Enable regex matching for pin names.
    LED.match_pin_regex = True
    # Add aliases to the pins.
    LED[1].aliases = "my_alias_+"
    LED[2].aliases = "my_alias_+"
    LED[2].aliases += "my_other_alias"
    # Count the number of pins fetched to see if the aliases were added correctly.
    assert len(LED["my_alias_+"]) == 2
    assert len((LED["my_other_alias"],)) == 1
    assert len(LED[".*"]) == 4
    # Check that assigning aliases to an alias raises an error.
    with pytest.raises(NotImplementedError):
        LED["my_alias_+"].aliases = "new_alias"


def test_alias_3():
    """Test the aliasing and splitting of pin names for a Part object."""
    # Create a Part object for an LED.
    LED = Part("Device", "LED_ABGR")
    # Set the name of the first pin.
    LED[1].name = "AB/BC|DC|ED"
    # Split the pin names using the specified delimiters.
    LED.split_pin_names("/|")
    # Check that the pin names were split correctly.
    assert LED[1] is LED.AB
    assert LED["AB"] is LED.BC
    assert LED[1] is LED.DC
    assert LED["DC"] is LED.ED
    # Create a copy of the LED part.
    LED2 = LED()
    # Check that the pin names were copied correctly.
    assert LED2[1] is LED2.AB
    assert LED2["AB"] is LED2.BC
    assert LED2[1] is LED2.DC
    assert LED2["DC"] is LED2.ED
