# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl import Part


def test_fields_1():
    """Test field creation and manipulation."""

    # Create a resistor part with a value of 500.
    r1 = Part("Device", "R", value=500)

    # Get the initial number of fields.
    num_fields = len(r1.fields)

    # Add a new field to the part.
    r1.fields["test1"] = "test1 value"

    # Check that the number of fields has increased by one.
    assert len(r1.fields) == num_fields + 1
    # Check that the new field can be accessed as an attribute.
    assert r1.test1 == r1.fields["test1"]

    # Change the value of the new field.
    r1.test1 = "new test1 value"

    # Check that the field value has been updated.
    assert r1.fields["test1"] == "new test1 value"

    # Create a copy of the part.
    r2 = r1()

    # Check that the new part has the same field value.
    assert r2.test1 == r1.test1

    # Change the field value in the new part.
    r2.fields["test1"] = "new r2 test1 value"

    # Check that the field value in the new part has been updated.
    assert r2.test1 == "new r2 test1 value"

    # Check that the field value in the original part has not changed.
    assert r1.test1 == "new test1 value"
