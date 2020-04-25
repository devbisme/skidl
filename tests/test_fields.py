import pytest

from skidl import *

from .setup_teardown import *


def test_fields_1():
    """Test field creation."""

    r1 = Part("Device", "R", value=500)

    num_fields = len(r1.fields)

    r1.fields["test1"] = "test1 value"

    assert len(r1.fields) == num_fields + 1
    assert r1.test1 == r1.fields["test1"]

    r1.test1 = "new test1 value"

    assert r1.fields["test1"] == "new test1 value"

    r2 = r1()

    assert id(r2.fields.attr_obj) == id(r2)
    assert id(r1.fields.attr_obj) == id(r1)

    assert r2.test1 == r1.test1

    r2.fields["test1"] = "new r2 test1 value"

    assert r2.test1 == "new r2 test1 value"

    assert r1.test1 == "new test1 value"
