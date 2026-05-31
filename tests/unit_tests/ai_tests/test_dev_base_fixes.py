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
