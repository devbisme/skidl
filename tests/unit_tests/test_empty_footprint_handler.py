# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""Regression test for issue #331: drawing functions must call a user-supplied
empty_footprint_handler for parts that have no footprint."""

import pytest

from skidl import Part, Net, generate_schematic, generate_svg


def _make_circuit():
    r = Part("Device", "R", footprint="")
    r[1] += Net("A")
    r[2] += Net("B")
    return r


@pytest.mark.parametrize("generate", [generate_schematic, generate_svg])
def test_custom_handler_is_called(generate, tmp_path):
    r = _make_circuit()
    called = []
    generate(
        filepath=str(tmp_path),
        empty_footprint_handler=lambda part: called.append(part.ref),
    )
    assert called == [r.ref]


@pytest.mark.parametrize("generate", [generate_schematic, generate_svg])
def test_default_handler_assigns_placeholder(generate, tmp_path):
    r = _make_circuit()
    generate(filepath=str(tmp_path))
    assert r.footprint == ":"


@pytest.mark.parametrize("generate", [generate_schematic, generate_svg])
def test_global_handler_restored(generate, tmp_path):
    import skidl

    saved = skidl.empty_footprint_handler
    _make_circuit()
    generate(filepath=str(tmp_path), empty_footprint_handler=lambda part: None)
    assert skidl.empty_footprint_handler is saved
