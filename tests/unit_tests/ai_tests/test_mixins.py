import pytest

from skidl.mixins import PinMixin
from skidl.pin import Pin


class DummyPart(PinMixin):
    """Minimal object using PinMixin for testing."""

    def __init__(self):
        super().__init__()
        # Attributes used by PinMixin methods
        self.name = "DUMMY"
        self.ref = "D1"
        self.unit = {}


def make_part_with_pins(pins):
    p = DummyPart()
    for pin in pins:
        p.add_pins(pin)
    return p


def test_rmv_pins_removes_by_number_and_name():
    # Create pins
    p1 = Pin(num=1, name="A")
    p2 = Pin(num=2, name="B")
    part = make_part_with_pins([p1, p2])

    # Remove by number and by name
    part.rmv_pins(1, "B")

    # Expect both pins removed (no pins left)
    assert len(part.pins) == 0


def test_swap_pins_swaps_num_and_name():
    p1 = Pin(num=1, name="ONE")
    p1.orig_id = "ONE"
    p2 = Pin(num=2, name="TWO")
    p2.orig_id = "TWO"
    part = make_part_with_pins([p1, p2])

    # Swap by numeric id and name id.
    part.swap_pins(1, "TWO")
    
    # After swap the pins' numbers and names should be exchanged but not the orig_id values.
    nums = {pin.name: pin.num for pin in part.pins}
    assert part[1].orig_id == "TWO"
    assert part["ONE"].orig_id == "TWO"
    assert part[2].orig_id == "ONE"
    assert part["TWO"].orig_id == "ONE"


def test_rename_pin_changes_name():
    p1 = Pin(num=1, name="OLD")
    part = make_part_with_pins([p1])

    part.rename_pin(1, "NEW")

    assert part.pins[0].name == "NEW"
    assert part[1].name == "NEW"
    assert part["NEW"].num == 1


def test_renumber_pin_changes_number():
    p1 = Pin(num=1, name="P")
    part = make_part_with_pins([p1])

    part.renumber_pin("P", 99)

    assert part.pins[0].num == 99
    assert part[99].num == 99
    assert part["P"].num == 99
