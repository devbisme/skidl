# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import TEMPLATE, Bus, Net, Part, Pin, package
from skidl.protonet import ProtoNet

from .setup_teardown import setup_function, teardown_function


def test_protonet_1():
    """Test ProtoNet."""

    pn1 = ProtoNet("A")
    pn2 = ProtoNet("B")
    pn3 = ProtoNet("B")

    pn1 += Pin()
    assert isinstance(pn1, Net)

    pn2 += Bus("B", 3)
    assert isinstance(pn2, Bus)

    pn3 += Net()
    assert isinstance(pn3, Net)


def test_package_8():
    r = Part("Device", "R", dest=TEMPLATE)

    @package
    def r_sub(neta, netb):
        neta & r() & netb

    vcc, gnd = Net("VCC"), Net("GND")
    rr = r_sub()
    rr.neta += vcc
    gnd += rr.netb

    default_circuit.instantiate_packages()

    assert type(gnd) == Net
    assert type(vcc) == Net
    assert type(rr.neta) == Net
    assert type(rr.netb) == Net
    assert len(rr.neta) == 1
    assert len(vcc) == 1
    assert len(rr.netb) == 1
    assert len(gnd) == 1
