# -*- coding: utf-8 -*-

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
                if isinstance(sub, list) and sub and sub[0] == "justify":
                    justify = sub[1]
    return angle, justify


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
