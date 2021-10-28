# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import Part

from .setup_teardown import setup_function, teardown_function


def test_note_1():
    vreg = Part("xess.lib", "1117")
    vreg.notes += "This is a voltage regulator."
    vreg[1].aliases += "pin_1"
    vreg.p1.notes += "Here is a note on pin 1!"
    vreg["pin_1"].notes += "Here is another note on pin 1!"
    vreg.p2.notes = "A first note on pin 2."
    vreg.notes += """
This is a docstring
type of note."""
    assert len(vreg[1].notes) == 2
    assert len(vreg[2].notes) == 1
    assert len(vreg.notes) == 2
    print("\n\n", vreg.notes)
    print("\n\n", vreg.p1.notes)
    print("\n\n", vreg[2].notes)
