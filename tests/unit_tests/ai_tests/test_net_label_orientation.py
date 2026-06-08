# -*- coding: utf-8 -*-

<<<<<<< HEAD
"""
Regression test for net-label *facing*: a stub net label must always extend
AWAY from its pin (and therefore clear of the part body), in every pin
orientation including mirrored parts.

This is the bug that 4bd527dc ("Fixed incorrect orientation of vertical net
labels") silently re-introduced by swapping the vertical orient_map values the
wrong way: vertical labels then pointed *into* the body. Orientation bugs do
not trip ERC, so nothing caught it. This test asserts the geometric invariant
directly, no rendering required.
"""

import importlib
import os

import pytest

from skidl import Net, Part, get_default_tool
from skidl.geometry import Point, Tx

tool = get_default_tool()

if os.getenv("SKIDL_TOOL") in ("KICAD5",):
    pytest.skip("Requires KiCad > 5", allow_module_level=True)

sexp_schematic = importlib.import_module(f"skidl.tools.{tool}.sexp_schematic")
net_label_to_sexp = sexp_schematic.net_label_to_sexp

# Normally populated during generate_schematic; ensure it exists so the
# power-symbol short-circuit in net_label_to_sexp is a no-op for our signal net.
if not hasattr(sexp_schematic, "pwr_symbol_names"):
    sexp_schematic.pwr_symbol_names = set()


# Empirically verified by rendering each combo in KiCad 9: which way the
# global_label text extends (render/screen space, Y-down) for a given
# (angle, justify). These four are the only pairs net_label_to_sexp emits.
_LABEL_PROJECTS = {
    (0, "left"): "R",
    (180, "right"): "L",
    (90, "left"): "U",
    (270, "right"): "D",
}


def _outward_render_dir(pin):
    """Direction the pin's stub points, away from the part body, in KiCad
    render space (Y-down). For a 2-pin part that's simply the direction from
    the other pin toward this one."""
    part_tx = getattr(pin.part, "tx", Tx())
    me = getattr(pin, "pt", Point(pin.x, pin.y)) * part_tx
    other_pin = next(p for p in pin.part.pins if p is not pin)
    other = getattr(other_pin, "pt", Point(other_pin.x, other_pin.y)) * part_tx
    dx = me.x - other.x
    dy = -(me.y - other.y)  # SKiDL Y-up -> KiCad sheet Y-down
    if abs(dx) >= abs(dy):
        return "R" if dx > 0 else "L"
    return "D" if dy > 0 else "U"


def _angle_justify(label_sexp):
    angle = None
    justify = None
    for item in label_sexp:
        if isinstance(item, list) and item and item[0] == "at":
            angle = int(round(float(item[3])))
        if isinstance(item, list) and item and item[0] == "effects":
            for sub in item:
=======
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
>>>>>>> 4f145dac6a03a8f525f8ce5c49d303485952f301
                if isinstance(sub, list) and sub and sub[0] == "justify":
                    justify = sub[1]
    return angle, justify


<<<<<<< HEAD
# symtx values exercising rotations and mirrors; collectively they put the
# stubbed pin into all four world orientations.
_SYMTX_CASES = ["", "H", "V", "R", "L", "HR", "VL"]


@pytest.mark.parametrize("symtx", _SYMTX_CASES)
def test_stub_label_extends_away_from_pin(symtx):
    """For every part transform, the emitted net label must project in the
    pin's outward direction (away from the body), never into it."""
    r = Part("Device", "R", value="R", symtx=symtx)
    r.tx = Tx.from_symtx(symtx)
    # Connect both pins so the stub pin is "connected"; stub pin[1].
    net = Net("SIG")
    gnd = Net("GND2")
    net += r[1]
    gnd += r[2]
    r[1].stub = True
    net.stub = True

    label = net_label_to_sexp(r[1], force=True)
    assert label is not None, f"no label emitted for symtx={symtx!r}"

    angle, justify = _angle_justify(label)
    assert (angle, justify) in _LABEL_PROJECTS, (
        f"symtx={symtx!r}: unexpected (angle={angle}, justify={justify}); "
        "net_label_to_sexp must emit an 'always-away' angle/justify pair"
    )

    projects = _LABEL_PROJECTS[(angle, justify)]
    outward = _outward_render_dir(r[1])
    assert projects == outward, (
        f"symtx={symtx!r}: label projects {projects} but pin points {outward} "
        f"(angle={angle}, justify={justify}) -- label faces INTO the body"
    )


def test_all_four_orientations_are_covered():
    """Guard the guard: make sure the symtx cases actually exercise all four
    pin directions, so the away-invariant test isn't silently vacuous."""
    seen = set()
    for symtx in _SYMTX_CASES:
        r = Part("Device", "R", value="R", symtx=symtx)
        r.tx = Tx.from_symtx(symtx)
        seen.add(_outward_render_dir(r[1]))
    assert seen == {"R", "L", "U", "D"}, f"orientations covered: {seen}"
=======
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
>>>>>>> 4f145dac6a03a8f525f8ce5c49d303485952f301
