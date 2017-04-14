import pytest
from skidl import *
from .setup_teardown import *

def test_net_merge_1():
    a = Net('A')
    b = Net('B')
    a += Pin(), Pin(), Pin(), Pin(), Pin()
    assert len(a) == 5
    b += Pin(), Pin(), Pin()
    assert len(b) == 3
    a += b
    assert len(a) == 8
