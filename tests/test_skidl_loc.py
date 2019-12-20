import pytest
from skidl import *

from .setup_teardown import *


def test_skidl_loc():
    rt = Part("Device", "R", dest=TEMPLATE, footprint="null")
    r1 = rt()
    resistors = rt(5)
    generate_netlist()
