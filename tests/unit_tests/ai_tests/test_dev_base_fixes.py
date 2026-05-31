# -*- coding: utf-8 -*-

"""Regression tests for bugs in the `development` schematic backend, found while
designing the snap backend split (see ARCHITECTURE-snap-backend-split.md).

Bug 1 (missing symbols): power-symbol *definitions* were scoped per-sheet from
`node.wires`, but power-symbol *instances* are emitted from power-net pins. With
auto_stub, power nets are stubbed (labels, not wires), so instances were emitted
on child sheets with no matching lib_symbols definition -> KiCad "unknown
component".

Bug 2 (label orientation): net-label angle must follow the pin's *rendered*
direction (after the sheet Y-flip), not the abstract pin direction.
"""

import glob
import os
import re
import shutil
import tempfile

import pytest
from skidl import Circuit, Net, Part, Interface, subcircuit

HAS_KICAD_LIBS = os.path.isdir(
    os.getenv("KICAD9_SYMBOL_DIR", "/usr/share/kicad/symbols")
)
requires_kicad_libs = pytest.mark.skipif(
    not HAS_KICAD_LIBS, reason="KiCad 9 symbol libraries not installed"
)


@pytest.fixture
def output_dir():
    d = tempfile.mkdtemp(prefix="skidl_dev_base_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _power_symbol_integrity(output_dir):
    """Map {sheet_filename: [power lib_ids emitted as instances with no def]}."""
    result = {}
    for f in glob.glob(os.path.join(output_dir, "**", "*.kicad_sch"), recursive=True):
        txt = open(f).read()
        defined = set(re.findall(r'\(symbol\s+"([^"]+)"', txt))
        instances = set(re.findall(r'\(lib_id\s+"([^"]+)"', txt))
        missing = sorted(
            i for i in instances if i.startswith("power:") and i not in defined
        )
        if missing:
            result[os.path.basename(f)] = missing
    return result


def _build_two_stage_power_design(circuit):
    """Two instances of a stage sharing VCC/GND power nets — hierarchical, so
    each stage becomes its own sheet and the power nets get auto-stubbed."""
    with circuit:

        @subcircuit
        def stage():
            vcc, gnd, sig = Net("VCC"), Net("GND"), Net()
            r1 = Part("Device", "R")
            r2 = Part("Device", "R")
            c1 = Part("Device", "C")
            vcc & r1 & sig & r2 & gnd
            sig & c1 & gnd
            return Interface(vcc=vcc, gnd=gnd)

        vcc, gnd = Net("VCC"), Net("GND")
        s1 = stage()
        s2 = stage()
        s1.vcc += vcc
        s2.vcc += vcc
        s1.gnd += gnd
        s2.gnd += gnd


@requires_kicad_libs
def test_power_symbol_defs_complete_under_autostub(output_dir):
    """Every power-symbol instance must have a matching lib_symbols definition on
    the same sheet (regression: development dropped them on stubbed child sheets)."""
    circuit = Circuit(name="two_stage_power")
    _build_two_stage_power_design(circuit)
    circuit.generate_schematic(
        filepath=output_dir, top_name="two_stage_power",
        auto_stub=True, auto_stub_fanout=2,
    )
    missing = _power_symbol_integrity(output_dir)
    assert not missing, f"power symbols emitted without definitions: {missing}"


# KiCad global_label angle -> the unit vector the label text extends along.
_ANGLE_VEC = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}


def _labels_pointing_into_parts(output_dir, threshold=-0.3):
    """Bug 2 guard (coarse): a net label must not point back INTO the body of the
    part it sits on. This catches gross orientation flips (e.g. a bad orient_map
    or a deconfliction anchor-move), NOT subtle/aesthetic angle preferences —
    those need a visual check and are the maintainer's domain.

    Returns list of (sheet, net, angle, dot) for labels pointing into a part.
    """
    import math
    bad = []
    for f in glob.glob(os.path.join(output_dir, "**", "*.kicad_sch"), recursive=True):
        txt = open(f).read()
        syms = [
            (float(m.group(2)), float(m.group(3)))
            for m in re.finditer(
                r'\(symbol\s+\(lib_id "([^"]+)"\)\s*\(at ([\d.\-]+) ([\d.\-]+) ([\d.\-]+)\)',
                txt,
            )
            if not m.group(1).startswith("power:")
        ]
        labels = [
            (m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)))
            for m in re.finditer(
                r'\(global_label "([^"]+)"\s*\(shape \w+\)\s*\(at ([\d.\-]+) ([\d.\-]+) ([\d.\-]+)\)',
                txt,
            )
        ]
        if not syms or not labels:
            continue
        for name, lx, ly, la in labels:
            sx, sy = min(syms, key=lambda s: (s[0] - lx) ** 2 + (s[1] - ly) ** 2)
            ox, oy = lx - sx, ly - sy
            n = math.hypot(ox, oy) or 1.0
            ox, oy = ox / n, oy / n
            vx, vy = _ANGLE_VEC.get(int(la) % 360, (0, 0))
            dot = ox * vx + oy * vy
            if dot <= threshold:
                bad.append((os.path.basename(f), name, int(la), round(dot, 2)))
    return bad


@requires_kicad_libs
def test_net_labels_do_not_point_into_parts(output_dir):
    """Coarse orientation guard across mirrored/rotated parts: no net label points
    into the body of its part. (Fine orientation/justification is visual and not
    asserted here.)"""
    from skidl import Net, Part, TEMPLATE, generate_schematic

    circuit = Circuit(name="bjt_orient")
    with circuit:
        e, b, c = Net("ENET"), Net("BNET"), Net("CNET")
        b.netio = "i"
        e.stub, b.stub, c.stub = True, True, True
        qt = Part(lib="Transistor_BJT", name="Q_PNP_CBE", dest=TEMPLATE)
        for q, tx in zip(qt(8), ["", "H", "V", "R", "L", "VL", "HR", "LV"]):
            q["E B C"] += e, b, c
            q.ref = "Q_" + tx
            q.symtx = tx
        circuit.generate_schematic(filepath=output_dir, top_name="bjt_orient", flatness=1.0)

    bad = _labels_pointing_into_parts(output_dir)
    assert not bad, f"labels pointing into their part: {bad}"
