# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Part


def test_note_1():
    """Test adding notes to parts and pins."""
    # Create a part representing an RGB LED.
    led = Part("Device", "LED_ARBG")
    
    # Add a note to the LED part.
    led.notes += "This is an RBG LED."
    
    # Add an alias to pin 1 and a note to pin 1 using different methods.
    led[1].aliases += "pin_1"
    led.p1.notes += "Here is a note on pin 1!"
    led["pin_1"].notes += "Here is another note on pin 1!"
    
    # Add a note to pin 2.
    led.p2.notes = "A first note on pin 2."
    
    # Add a multi-line note to the LED part.
    led.notes += """
This is a docstring
type of note."""
    
    # Assert the number of notes on pins and the part.
    assert len(led[1].notes) == 2
    assert len(led[2].notes) == 1
    assert len(led.notes) == 2
    
    # Print the notes for debugging purposes.
    print("\n\n", led.notes)
    print("\n\n", led.p1.notes)
    print("\n\n", led[2].notes)
