# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

from skidl import Net, Part, PartTmplt, to_list

from .setup_teardown import setup_function, teardown_function


def test_part_1():
    vreg = Part("xess.lib", "1117")
    n = Net()
    # Connect all the part pins to a net...
    for pin in vreg:
        n += pin
    # Then see if the number of pins on the net equals the number of part pins.
    assert len(n) == len(vreg)


def test_part_2():
    vreg = Part("xess.lib", "1117")
    codec = Part("xess.lib", "ak4520a")
    parts = to_list(Part.get("u1"))
    assert len(parts) == 1
    parts = to_list(Part.get("ak4520a"))
    assert len(parts) == 1
    parts = to_list(Part.get(".*"))
    assert len(parts) == 2


def test_part_3():
    r = Part("Device", "R", ref=None)
    assert r.ref == "R1"


def test_part_tmplt_1():
    rt = PartTmplt("Device", "R", value=1000)
    r1, r2 = rt(num_copies=2)
    assert r1.ref == "R1"
    assert r2.ref == "R2"
    assert r1.value == 1000
    assert r2.value == 1000

def test_part_ref_prefix():
    c = Part("Device", "C", ref_prefix="test")
    assert c.ref == "test1"
