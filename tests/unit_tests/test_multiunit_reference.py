# -*- coding: utf-8 -*-

"""Regression for devbisme/skidl #318.

``generate_schematic`` dropped all wiring of the non-first units of a multi-unit
part.  The cause was in ``part_to_sexp``: skidl's compound ``PartUnit`` reference
("U1.uA".."U1.uE") was emitted for both the ``Reference`` property and the
``(instances ... (path ... (reference ...)))`` entry.  KiCad reads a compound
reference as a *distinct component*, so a multi-unit part's units never
associated with one another -- the dedicated power unit's pins were orphaned and
the netlist read back from the generated schematic diverged from the logical
netlist (the reported "dropped wiring").

All units of a part must share ONE reference ("U1") and be told apart only by
``(unit N)``.  This asserts the generated KiCad-9 schematic emits the shared base
reference, with no compound "U1.u" ref leaking, and more than one unit placed.
"""

import builtins
import re

import pytest

from skidl import Net, Part, generate_schematic


def test_multiunit_shares_base_reference(tmp_path):
    default_circuit = builtins.default_circuit
    default_circuit.mini_reset()

    # Pick whichever multi-unit op-amp resolves from the installed libraries.
    part = None
    for name in ("LM324", "LM2902", "TL074", "LM358"):
        try:
            part = Part("Amplifier_Operational", name, ref="U1")
            break
        except Exception:
            default_circuit.mini_reset()
    if part is None:
        pytest.skip("no multi-unit op-amp available in the installed libraries")
    if len(getattr(part, "unit", {})) < 2:
        pytest.skip(f"{getattr(part, 'name', '?')} did not resolve as multi-unit")
    base_ref = part.ref

    # Connect the supply pins so the dedicated power unit is placed too.
    vp, vn = Net("V+"), Net("V-")
    for pin in part.pins:
        nm = (getattr(pin, "name", "") or "").upper()
        if nm in ("V+", "VCC", "VDD"):
            pin += vp
        elif nm in ("V-", "VEE", "VSS"):
            pin += vn

    out = tmp_path / "mu"
    out.mkdir()
    generate_schematic(filepath=str(out), top_name="mu")

    # KiCad 6-9 emit S-expression ".kicad_sch"; KiCad 5 emits the legacy ".sch".
    sch_files = sorted(out.glob("*.kicad_sch")) or sorted(out.glob("*.sch"))
    assert sch_files, "no schematic file was generated"
    text = sch_files[0].read_text(encoding="utf-8")
    legacy = sch_files[0].suffix == ".sch"

    # The compound PartUnit reference must never leak into the schematic (all tools).
    assert "U1.u" not in text, "compound PartUnit reference leaked into the schematic"

    if legacy:
        # Legacy format: every unit is a "$Comp" sharing the "L <lib>:<name> U1"
        # reference, distinguished only by the unit number in its "U <n> 1 ..." line.
        assert re.search(r"^L \S+ U1$", text, re.MULTILINE), "shared base ref missing"
        units = set(re.findall(r"^U (\d+) ", text, re.MULTILINE))
    else:
        # S-expression format: every instance references the shared base "U1",
        # distinguished only by "(unit N)".
        assert '(reference "U1")' in text or '(reference U1)' in text
        units = set(re.findall(r"\(unit (\d+)\)", text))
    # More than one distinct unit present -> the part really rendered multi-unit.
    assert len(units) >= 2, f"expected >=2 units placed, got {units}"
