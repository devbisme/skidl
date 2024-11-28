# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from skidl import TEMPLATE, Part, generate_netlist

from .setup_teardown import setup_function, teardown_function


def test_skidl_loc():
    """Test the creation of parts and netlist generation in SKiDL."""
    # Create a resistor template part.
    rt = Part("Device", "R", dest=TEMPLATE, footprint="null")
    
    # Instantiate a single resistor from the template.
    r1 = rt()
    
    # Instantiate five resistors from the template.
    resistors = rt(5)
    
    # Generate the netlist.
    generate_netlist()
