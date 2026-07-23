# -*- coding: utf-8 -*-

"""
Regression test for power-symbol *facing*: a GND / voltage-rail power symbol
emitted at a stub pin must orient so its body extends AWAY from the pin (clear
of the part body), in every pin orientation including mirrored parts.

This mirrors test_net_label_orientation.py. _power_symbol_to_sexp originally
carried its own copy of the orientation table with the vertical (U/D) values
swapped the wrong way -- the same bug that affected vertical net labels --
which made GND/rail symbols on vertical pins point back INTO the body. The two
emitters now share the module-level _PIN_LABEL_ANGLE table; this test pins the
power-symbol angle to that shared table so they can never drift apart again,
no rendering required.
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


def test_power_symbol_angle_table_is_shared():
    """The shared angle table must hold the corrected vertical values; an
    earlier table had U/D swapped, which mis-oriented vertical labels and
    power symbols alike."""
    assert sexp_schematic._PIN_LABEL_ANGLE == {
        "R": 180,
        "L": 0,
        "U": 270,
        "D": 90,
    }


def _instance_angle(power_sexp):
    for item in power_sexp:
        if isinstance(item, list) and item and item[0] == "at":
            return int(round(float(item[3]))) % 360
    raise AssertionError("no (at ...) in power symbol sexp")


# symtx values exercising rotations and mirrors; collectively they put the
# stubbed pin into all four world orientations.
_SYMTX_CASES = ["", "H", "V", "R", "L", "HR", "VL"]


@pytest.mark.parametrize("symtx", _SYMTX_CASES)
def test_power_symbol_tracks_shared_angle_table(symtx):
    """For every part transform, the emitted power-symbol instance angle must
    equal (shared_table_angle - intrinsic_pin_angle) % 360, i.e. it derives
    from _PIN_LABEL_ANGLE and never the old swapped vertical values."""
    _power_symbol_to_sexp = sexp_schematic._power_symbol_to_sexp
    _power_symbol_pin_angle = sexp_schematic._power_symbol_pin_angle
    calc_pin_dir = sexp_schematic.calc_pin_dir

    sexp_schematic.init_power_symbol_data()

    r = Part("Device", "R", value="R", symtx=symtx)
    r.tx = Tx.from_symtx(symtx)
    gnd = Net("GND")
    rail = Net("+3V3")
    gnd += r[1]
    rail += r[2]
    r[1].stub = True
    r[2].stub = True

    for pin, net_name in ((r[1], "GND"), (r[2], "+3V3")):
        pwr = _power_symbol_to_sexp(pin, net_name, Tx())
        assert pwr is not None, f"symtx={symtx!r}: no power symbol for {net_name}"
        angle = _instance_angle(pwr)
        intrinsic = _power_symbol_pin_angle(net_name)
        expected = (
            sexp_schematic._PIN_LABEL_ANGLE[calc_pin_dir(pin)] - intrinsic
        ) % 360
        assert angle == expected, (
            f"symtx={symtx!r} {net_name}: power symbol angle {angle} != "
            f"expected {expected} from shared _PIN_LABEL_ANGLE"
        )
