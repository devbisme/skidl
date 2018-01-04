import pytest
from skidl import *
from .setup_teardown import *

def test_parser_1():
    parse_netlist(get_filename('Arduino_Uno_R3_From_Scratch.net'))
