# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Bus, Net, Part

from .setup_teardown import setup_function, teardown_function


def test_iters_1():
    """Test bus iterator."""
    b_size = 4  # Define the size of the bus.
    b = Bus("chplx", b_size)  # Create a bus with the given size.
    for hi in b:  # Iterate over the bus.
        for lo in b:  # Iterate over the bus again.
            if hi != lo:  # Check if the two bus lines are different.
                led = Part("Device", "LED")  # Create an LED part.
                hi += led["A"]  # Connect the high bus line to the anode of the LED.
                lo += led["K"]  # Connect the low bus line to the cathode of the LED.
    for l in b:  # Iterate over the bus.
        # Check if the length of each bus line is correct.
        assert len(l) == 2 * (b_size - 1)


def test_iters_2():
    """Test pin iterator."""
    try:
        q = Part("Device", "Q_NPN_CEB")  # Create a transistor part.
    except ValueError:
        q = Part("Transistor_BJT", "Q_NPN_CEB")  # Create a transistor part.
    s = 0  # Initialize a counter.
    for p1 in q:  # Iterate over the pins of the transistor.
        for p2 in q:  # Iterate over the pins of the transistor again.
            if p1 != p2:  # Check if the two pins are different.
                s += 1  # Increment the counter.
    assert s == len(q) * (len(q) - 1)  # Check if the counter value is correct.


def test_iters_3():
    """Test net iterator."""
    b = Net()  # Create a net.
    for hi in b:  # Iterate over the net.
        for lo in b:  # Iterate over the net again.
            if hi != lo:  # Check if the two net lines are different.
                led = Part("Device", "LED")  # Create an LED part.
                hi += led["A"]  # Connect the high net line to the anode of the LED.
                lo += led["K"]  # Connect the low net line to the cathode of the LED.
    for l in b:  # Iterate over the net.
        assert len(l) == 0  # Check if the length of each net line is correct.
