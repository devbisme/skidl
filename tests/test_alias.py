import pytest
from skidl import *
from .setup_teardown import *

def test_alias_1():
    vreg = Part('xess.lib', '1117')
    vreg.set_pin_alias('my_alias', 1)
    vreg.set_pin_alias('my_alias', 2)
    assert len(vreg['my_alias']) == 2
    assert len(vreg['.*']) == 4

def test_alias_2():
    vreg = Part('xess.lib', '1117')
    vreg.set_pin_alias('my_alias', 1)
    vreg.set_pin_alias('my_alias', 2)
    with pytest.raises(Exception):
        vreg.set_pin_alias('new_alias', 'my_alias')

def test_alias_3():
    vreg = Part('xess.lib', '1117')
    vreg[1].alias = 'my_alias'
    vreg[2].alias = 'my_alias'
    assert len(vreg['my_alias']) == 2
    assert len(vreg['.*']) == 4
    with pytest.raises(Exception):
        vreg['my_alias'].alias = 'new_alias'
