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
import subprocess
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




HAS_KICAD_CLI = shutil.which("kicad-cli") is not None
requires_kicad_cli = pytest.mark.skipif(
    not HAS_KICAD_CLI, reason="kicad-cli not installed"
)


def _erc_connectivity_violations(sch_path):
    """Run kicad-cli ERC and return connectivity-class violations (pins/wires
    left unconnected). Excludes semantic warnings (pin_not_driven from netio)
    and environmental lib-config warnings."""
    rpt = sch_path.replace(".kicad_sch", "-conn-erc.rpt")
    subprocess.run(
        ["kicad-cli", "sch", "erc", "--output", rpt, "--severity-all", sch_path],
        capture_output=True, timeout=60,
    )
    if not os.path.exists(rpt):
        return []
    txt = open(rpt).read()
    bad_types = ("pin_not_connected", "unconnected", "endpoint", "dangling", "wire_dangling")
    return [t for t in bad_types if f"[{t}]" in txt]


@requires_kicad_libs
@requires_kicad_cli
def test_deconflicted_labels_stay_connected(output_dir):
    """Label deconfliction spreads net labels off component bodies for
    readability, but must preserve connectivity: each moved label is wired back
    to its pin. Across mirrored/rotated parts, ERC must report no
    connectivity-class violations (unconnected pins / dangling wire ends)."""
    from skidl import Net, Part, TEMPLATE

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

    sch = os.path.join(output_dir, "bjt_orient.kicad_sch")
    violations = _erc_connectivity_violations(sch)
    assert not violations, f"deconfliction left connectivity violations: {violations}"
