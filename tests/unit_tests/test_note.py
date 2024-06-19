# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Part

from .setup_teardown import setup_function, teardown_function


def test_note_1():
    led = Part("Device", "LED_ARBG")
    led.notes += "This is an RBG LED."
    led[1].aliases += "pin_1"
    led.p1.notes += "Here is a note on pin 1!"
    led["pin_1"].notes += "Here is another note on pin 1!"
    led.p2.notes = "A first note on pin 2."
    led.notes += """
This is a docstring
type of note."""
    assert len(led[1].notes) == 2
    assert len(led[2].notes) == 1
    assert len(led.notes) == 2
    print("\n\n", led.notes)
    print("\n\n", led.p1.notes)
    print("\n\n", led[2].notes)
