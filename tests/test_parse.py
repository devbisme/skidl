import pytest
from skidl import *
from .setup_teardown import *

def test_parser_1():
    netlist_to_skidl(get_filename('Arduino_Uno_R3_From_Scratch.net'))
