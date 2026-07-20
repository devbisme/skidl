# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""Net-label orientation regression tests.

A net label must always extend *away* from the pin it sits on, so the text
runs clear of the part body in every pin direction.  KiCad's ``global_label``
keeps text upright (angle 90 reads the same as 270, 0 the same as 180), so the
side the label extends is governed by ``justify`` together with the
horizontal/vertical angle.  The correct, render-verified mapping is:

    pin points R -> (180, "right")   # label reaches out to the right
    pin points L -> (0,   "left")    # ... to the left
    pin points U -> (270, "right")   # ... upward, clear of the body
    pin points D -> (90,  "left")    # ... downward

A previous regression left the KiCad 6/7/8 backends on ``{"D": 270, "U": 90}``
with justify derived from the angle, which flipped vertical labels so they
overprinted the part body.  These tests pin the mapping and, crucially, assert
that *all four* KiCad backends agree -- the drift that caused the bug.
"""

from types import SimpleNamespace

import pytest

from skidl.geometry import Point, Tx
from skidl.tools.kicad6 import sexp_schematic as k6
from skidl.tools.kicad7 import sexp_schematic as k7
from skidl.tools.kicad8 import sexp_schematic as k8
from skidl.tools.kicad9 import sexp_schematic as k9

BACKENDS = {"kicad6": k6, "kicad7": k7, "kicad8": k8, "kicad9": k9}


@pytest.fixture(autouse=True)
def _empty_power_symbols():
    """``net_label_to_sexp`` consults a module-global ``pwr_symbol_names`` that
    is normally populated during generation.  Calling the emitter in isolation
    needs it defined; an empty set routes the test net through the plain
    global_label path (no power symbol)."""
    saved = {}
    for mod in BACKENDS.values():
        saved[mod] = getattr(mod, "pwr_symbol_names", None)
        mod.pwr_symbol_names = set()
    yield
    for mod, val in saved.items():
        if val is None:
            delattr(mod, "pwr_symbol_names")
        else:
            mod.pwr_symbol_names = val


# pin direction -> (label angle, justify) that makes the label extend away.
EXPECTED = {
    "R": (180, "right"),
    "L": (0, "left"),
    "U": (270, "right"),
    "D": (90, "left"),
}


def _fake_pin(orientation):
    """A minimal stubbed pin whose ``calc_pin_dir`` resolves to ``orientation``
    (identity part transform leaves the pin orientation unchanged)."""
    part = SimpleNamespace(tx=Tx())
    net = SimpleNamespace(name="SIG")
    return SimpleNamespace(
        orientation=orientation,
        stub=True,
        net=net,
        part=part,
        pt=Point(0, 0),
        x=0,
        y=0,
        is_connected=lambda: True,
    )


def _angle_justify(sexp):
    """Pull (angle, justify) out of an emitted global_label S-expression."""
    angle = justify = None
    for el in sexp:
        if isinstance(el, list) and el and el[0] == "at":
            angle = el[3]
        if isinstance(el, list) and el and el[0] == "effects":
            for sub in el:
                if isinstance(sub, list) and sub and sub[0] == "justify":
                    justify = sub[1]
    return angle, justify


@pytest.mark.parametrize("backend_name,mod", BACKENDS.items())
@pytest.mark.parametrize("pin_dir", ["R", "L", "U", "D"])
def test_label_extends_away(backend_name, mod, pin_dir):
    """Each backend emits the away-extending angle/justify for every pin dir."""
    pin = _fake_pin(pin_dir)
    assert mod.calc_pin_dir(pin) == pin_dir  # identity tx sanity check
    sexp = mod.net_label_to_sexp(pin)
    assert _angle_justify(sexp) == EXPECTED[pin_dir]


@pytest.mark.parametrize("pin_dir", ["R", "L", "U", "D"])
def test_backends_agree(pin_dir):
    """All four KiCad backends must emit identical label orientation -- the
    cross-backend drift is exactly what regressed the vertical labels."""
    results = {
        name: _angle_justify(mod.net_label_to_sexp(_fake_pin(pin_dir)))
        for name, mod in BACKENDS.items()
    }
    assert len(set(results.values())) == 1, results


def test_vertical_labels_not_inverted():
    """Direct guard against the specific {"D":270,"U":90} swap: up and down
    pins must not collapse to the same justify, and neither may point inward."""
    for name, mod in BACKENDS.items():
        up = _angle_justify(mod.net_label_to_sexp(_fake_pin("U")))
        dn = _angle_justify(mod.net_label_to_sexp(_fake_pin("D")))
        assert up == (270, "right"), f"{name} U-pin label inverted: {up}"
        assert dn == (90, "left"), f"{name} D-pin label inverted: {dn}"
