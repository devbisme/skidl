# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Part, Pin
from skidl.pin import pin_types

from .setup_teardown import setup_function, teardown_function


def test_pin_names_1():
    """Test pin name access."""
    mem = Part("Memory_RAM", "AS4C4M16SA")
    assert mem["DQ15"] == mem.n["DQ15"]  # Check pin name access.
    assert mem[1:4] == mem.p[1:4]  # Check pin range access.


def test_pin_names_2():
    """Test pin name and number modification."""
    mem = Part("Memory_RAM", "AS4C4M16SA")
    mem[4].name = "X1"  # Modify pin name.
    mem[8].name = "X2"  # Modify another pin name.
    mem[8].num = "X1"  # Modify pin number.
    assert mem[4] is mem.n["X1"]  # Check pin name access.
    assert mem.p[4] is mem.n["X1"]  # Check pin name access.
    assert mem[4] is mem.p[4]  # Check pin access.
    assert mem.p["X1"] is mem.n["X2"]  # Check pin name access.
    assert mem["X1"] is mem.n["X2"]  # Check pin name access.
    assert mem["X1"] is mem.p["X1"]  # Check pin name access.


def test_numerical_pin_order():
    """Test numerical pin order."""
    mem = Part("Memory_RAM", "AS4C4M16SA")
    p = mem.pins.pop(13)  # Remove pin from list.
    mem.pins.append(p)  # Append pin to list.
    assert [int(x.num) for x in mem.pins] != list(range(1, len(mem.pins) + 1))  # Check pin order.
    assert [int(x.num) for x in mem.ordered_pins] == list(range(1, len(mem.pins) + 1))  # Check ordered pins.


def test_alphanumeric_pin_order():
    """Test alphanumeric pin order."""
    mem = Part("Memory_RAM", "AS4C4M16SA")
    mem[3].num = "A1"  # Modify pin number.
    mem[5].num = "B1"  # Modify another pin number.
    assert [p.num for p in mem.ordered_pins[-6:]] == ["51", "52", "53", "54", "A1", "B1"]  # Check ordered pins.


def test_eq():
    """Test pin equality."""
    p1 = Pin(num=1)
    p2 = Pin(num=1)
    assert p1 == p2  # Check pin equality.
    assert p1 is not p2  # Check pin identity.
    p2.part = "new part"  # Modify pin part.
    assert p1 != p2  # Check pin inequality.


def test_numeric_sorts():
    """Test numeric pin sorting."""
    assert Pin(num=1) < Pin(num=2)  # Check pin sorting.
    assert Pin(num=9) < Pin(num=10) < Pin(num=11)  # Check pin sorting.
    assert Pin(num="1") < Pin(num="2")  # Check pin sorting.
    assert Pin(num="9") < Pin(num="10") < Pin(num="11")  # Check pin sorting.
    assert Pin(num="1") < Pin(num=2)  # Check pin sorting.
    assert Pin(num="9") < Pin(num=10) < Pin(num="11")  # Check pin sorting.
    with pytest.raises(ValueError):
        Pin(num=1) < Pin(num=2, part="newpart")  # Check pin sorting with exception.


def test_alphanum_sorts():
    """Test alphanumeric pin sorting."""
    assert Pin(num=1) < Pin(num="a1")  # Check pin sorting.
    assert Pin(num="a1") < Pin(num="a2")  # Check pin sorting.
    assert Pin(num="a100") < Pin(num="b1")  # Check pin sorting.
    assert Pin(num="a001") == Pin(num="a1")  # Check pin equality.
    assert Pin(num="AA100") > Pin(num="A1000")  # Check pin sorting.


def test_pin_search_1():
    """Test pin search by function."""
    mem = Part("Memory_RAM", "AS4C4M16SA")
    bidir = mem.get_pins(func=pin_types.BIDIR)  # Get bidirectional pins.
    input = mem.get_pins(func=pin_types.INPUT)  # Get input pins.
    passive = mem.get_pins(func=pin_types.PASSIVE)  # Get passive pins.
    nc = mem.get_pins(func=pin_types.NOCONNECT)  # Get no-connect pins.
    pwrin = mem.get_pins(func=pin_types.PWRIN)  # Get power input pins.
    assert len(bidir) == 16  # Check bidirectional pin count.
    assert len(pwrin) == 4  # Check power input pin count.
    assert len(bidir) + len(pwrin) + len(input) + len(passive) + len(nc) == len(mem)  # Check total pin count.
