# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import pytest

from skidl import SKIDL, TEMPLATE, Circuit, Part, Pin, subcircuit

from .setup_teardown import setup_function, teardown_function


def test_NC_1():
    @subcircuit
    def circ_nc():
        res = Part(
            tool=SKIDL,
            name="res",
            ref_prefix="R",
            dest=TEMPLATE,
            pins=[
                Pin(num=1, func=Pin.types.PASSIVE),
                Pin(num=2, func=Pin.types.PASSIVE),
            ],
        )
        r1 = res()
        r1[1] += NC

    default_circuit.name = "DEFAULT"
    circuit1 = Circuit(name="CIRCUIT1")
    circ_nc()
    circ_nc(circuit=circuit1)
