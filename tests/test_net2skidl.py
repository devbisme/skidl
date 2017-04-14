import pytest
from skidl import *
from .setup_teardown import *

def test_netlist_to_skidl_1():
    netlist_to_skidl(r'C:\xesscorp\KiCad\tools\skidl\tests\Arduino_Uno_R3_From_Scratch.net')
