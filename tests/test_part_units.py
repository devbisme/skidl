import pytest
from skidl import *
from .setup_teardown import *
import logging

def test_part_unit_1():
    vreg = Part('xess.lib', '1117')
    vreg.make_unit('A', 1, 2)
    vreg.make_unit('B', 3)
    assert len(vreg.unit['A']['.*']) == 2
    assert len((vreg.unit['B']['.*'],)) == 1

def test_part_unit_2():
    vreg = Part('xess.lib', '1117')
    vreg.make_unit('A', 1, 2)
    vreg.make_unit('A', 3)
    assert len((vreg.unit['A']['.*'],)) == 1
    
def test_part_unit_3():
    vreg = Part('xess.lib', '1117')
    vreg.make_unit('1', 1, 2)    
