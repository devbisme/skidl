# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import SKIDL, TEMPLATE, Circuit, Part, Pin, subcircuit
from skidl.pin import pin_types

from .setup_teardown import setup_function, teardown_function


def test_NC_1():
    """Test the NC (No Connect) functionality."""
    
    @subcircuit
    def circ_nc():
        """Create a subcircuit with a resistor."""
        res = Part(
            tool=SKIDL,
            name="res",
            ref_prefix="R",
            dest=TEMPLATE,
            pins=[
                Pin(num=1, func=pin_types.PASSIVE),  # Define pin 1 as passive
                Pin(num=2, func=pin_types.PASSIVE),  # Define pin 2 as passive
            ],
        )
        r1 = res()  # Instantiate the resistor part
        r1[1] += NC  # Connect pin 1 to NC (No Connect)

    default_circuit.name = "DEFAULT"  # Set the name of the default circuit
    circuit1 = Circuit(name="CIRCUIT1")  # Create a new circuit named CIRCUIT1
    circ_nc()  # Add the subcircuit to the default circuit
    circ_nc(circuit=circuit1)  # Add the subcircuit to circuit1
