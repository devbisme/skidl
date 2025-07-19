# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Net, Pin


def test_net_merge_1():
    """Test merging of two nets."""
    a = Net("A")  # Create net A.
    b = Net("B")  # Create net B.
    a += Pin(), Pin(), Pin(), Pin(), Pin()  # Add 5 pins to net A.
    assert len(a) == 5  # Check that net A has 5 pins.
    b += Pin(), Pin(), Pin()  # Add 3 pins to net B.
    assert len(b) == 3  # Check that net B has 3 pins.
    a += b  # Merge net B into net A.
    assert len(a) == 8  # Check that net A now has 8 pins.
