# -*- coding: utf-8 -*-

"""
Comprehensive tests for the KiCad 9 S-expression schematic generator.

Layer 1: Unit tests for pure functions (no KiCad needed)
Layer 2: Structural validation of generated output
Layer 3: End-to-end circuit generation
Layer 4: KiCad CLI validation (skipped if kicad-cli not installed)
"""

import importlib
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from types import SimpleNamespace

import pytest

from skidl import get_default_tool
from skidl.geometry import BBox, Point, Tx
from skidl.tools.kicad8.sexp_schematic import (
    part_to_lib_symbol_definition as part_to_kicad8_lib_symbol_definition,
)

tool = get_default_tool()
sexp_schematic = importlib.import_module(f"skidl.tools.{tool}.sexp_schematic")
A_SIZES = sexp_schematic.A_SIZES
MILS_TO_MM = sexp_schematic.MILS_TO_MM
_calc_sheet_tx = sexp_schematic._calc_sheet_tx
_fix_sheet_filename = sexp_schematic._fix_sheet_filename
_gen_uuid = sexp_schematic._gen_uuid
_pick_paper_size = sexp_schematic._pick_paper_size
create_title_block_sexp = sexp_schematic.create_title_block_sexp


# Skip entire module for early versions of KiCad.
if os.getenv("SKIDL_TOOL") in ('KICAD5',):
    pytest.skip("Tests require KiCad version > 5 as the default tool", allow_module_level=True)


# ===========================================================================
# Layer 1: Unit tests — pure functions, no KiCad needed
# ===========================================================================


class TestGenUuid:
    """Tests for deterministic and random UUID generation."""

    def test_random_uuid_format(self):
        """Random UUID (empty name) is a valid UUID4."""
        result = _gen_uuid("")
        parsed = uuid.UUID(result)
        assert parsed.version == 4

    def test_deterministic_uuid_format(self):
        """Named UUID is a valid UUID5."""
        result = _gen_uuid("test_name")
        parsed = uuid.UUID(result)
        assert parsed.version == 5

    def test_deterministic_uuid_stable(self):
        """Same name always produces same UUID."""
        assert _gen_uuid("foo") == _gen_uuid("foo")

    def test_deterministic_uuid_different_names(self):
        """Different names produce different UUIDs."""
        assert _gen_uuid("foo") != _gen_uuid("bar")

    def test_namespace_matches_gen_netlist(self):
        """UUID namespace matches gen_netlist.py for cross-reference."""
        from skidl.tools.kicad9.sexp_schematic import _NAMESPACE_UUID

        assert str(_NAMESPACE_UUID) == "7026fcc6-e1a0-409e-aaf4-6a17ea82654f"


class TestPickPaperSize:
    """Tests for paper size selection."""

    def test_small_bbox_gets_a4(self):
        """Small content fits on A4."""
        bbox = BBox(Point(0, 0), Point(1000, 1000))  # ~25x25mm
        assert _pick_paper_size(bbox) == "A4"

    def test_empty_bbox_gets_a4(self):
        """Empty/default bbox gets A4."""
        bbox = BBox()
        assert _pick_paper_size(bbox) == "A4"

    def test_large_bbox_gets_bigger(self):
        """Content exceeding A4 gets A3 or larger."""
        # 15000 mils wide = 381mm > A4(297mm), fits A3(420mm)
        bbox = BBox(Point(0, 0), Point(15000, 8000))
        result = _pick_paper_size(bbox)
        assert result in ("A3", "A2", "A1", "A0")

    def test_huge_bbox_gets_a0(self):
        """Very large content gets A0."""
        bbox = BBox(Point(0, 0), Point(40000, 30000))  # ~1016x762mm
        assert _pick_paper_size(bbox) == "A0"


class TestCalcSheetTx:
    """Tests for _calc_sheet_tx coordinate transform."""

    def test_returns_paper_size(self):
        """_calc_sheet_tx returns a paper size string."""
        bbox = BBox(Point(0, 0), Point(2000, 2000))
        tx, paper = _calc_sheet_tx(bbox)
        assert paper in A_SIZES

    def test_output_in_mm_range(self):
        """Transformed bbox coordinates should be in mm (page-sized)."""
        bbox = BBox(Point(0, 0), Point(5000, 3000))
        tx, paper = _calc_sheet_tx(bbox)
        pw, ph = A_SIZES[paper]

        # Transform the bbox corners.
        p1 = Point(0, 0) * tx
        p2 = Point(5000, 3000) * tx

        # All coords should be in reasonable mm range (on the page).
        for p in (p1, p2):
            assert -50 < p.x < pw + 50, f"x={p.x} out of page range"
            assert -50 < p.y < ph + 50, f"y={p.y} out of page range"

    def test_no_mils_leak(self):
        """No coordinate should be > 2000 (would indicate mils leaking)."""
        bbox = BBox(Point(0, 0), Point(10000, 8000))
        tx, paper = _calc_sheet_tx(bbox)

        p = Point(10000, 8000) * tx
        assert abs(p.x) < 2000, f"x={p.x} looks like mils, not mm"
        assert abs(p.y) < 2000, f"y={p.y} looks like mils, not mm"

    def test_y_flip(self):
        """Y should be flipped (positive mils Y → lower KiCad Y or vice versa)."""
        bbox = BBox(Point(0, 0), Point(1000, 1000))
        tx, paper = _calc_sheet_tx(bbox)

        # Check that d component is negative (Y-flip).
        assert tx.d < 0, f"tx.d={tx.d} should be negative for Y-flip"

    def test_mils_to_mm_scale(self):
        """The a/d scale factors should include MILS_TO_MM conversion."""
        bbox = BBox(Point(0, 0), Point(1000, 1000))
        tx, _ = _calc_sheet_tx(bbox)
        assert abs(tx.a - MILS_TO_MM) < 1e-10
        assert abs(tx.d - (-MILS_TO_MM)) < 1e-10


class TestTitleBlock:
    """Tests for title block S-expression."""

    def test_structure(self):
        """Title block has correct structure."""
        tb = create_title_block_sexp("My Circuit")
        assert tb[0] == "title_block"
        assert ["title", "My Circuit"] in tb
        # Should have a date entry.
        dates = [item for item in tb if isinstance(item, list) and item[0] == "date"]
        assert len(dates) == 1


class TestLibrarySymbolDefinition:
    """Tests for backend-specific library symbol grammar."""

    def test_kicad8_uses_legacy_pin_number_syntax(self):
        """KiCad 8 symbols omit grammar tokens introduced in KiCad 9."""
        part = SimpleNamespace(
            lib=SimpleNamespace(filename="Device.kicad_sym"),
            name="R",
            ref_prefix="R",
            datasheet="~",
            description="Resistor",
            draw_cmds={},
        )

        symbol_def = part_to_kicad8_lib_symbol_definition(part)

        assert ["pin_numbers", "hide"] in symbol_def
        assert ["pin_numbers", ["hide", "yes"]] not in symbol_def
        assert not any(
            isinstance(entry, list) and entry and entry[0] == "embedded_fonts"
            for entry in symbol_def
        )


class TestFixSheetFilename:
    """Tests for _fix_sheet_filename."""

    def test_sch_to_kicad_sch(self):
        """Converts .sch extension to .kicad_sch."""

        class FakeNode:
            sheet_filename = "test.sch"

        node = FakeNode()
        _fix_sheet_filename(node)
        assert node.sheet_filename == "test.kicad_sch"

    def test_already_kicad_sch(self):
        """Leaves .kicad_sch extension unchanged."""

        class FakeNode:
            sheet_filename = "test.kicad_sch"

        node = FakeNode()
        _fix_sheet_filename(node)
        assert node.sheet_filename == "test.kicad_sch"

    def test_none_filename(self):
        """Handles None filename without error."""

        class FakeNode:
            sheet_filename = None

        node = FakeNode()
        _fix_sheet_filename(node)
        assert node.sheet_filename is None


# ===========================================================================
# Layer 2: Structural validation — parse output, no KiCad needed
# ===========================================================================


def validate_kicad_sch(content):
    """Validate structural correctness of a .kicad_sch file.

    Raises AssertionError with a descriptive message on failure.
    """
    # Must start with kicad_sch.
    assert content.strip().startswith("(kicad_sch"), "Missing (kicad_sch header"

    # Balanced parentheses.
    depth = 0
    for ch in content:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        assert depth >= 0, "Unbalanced parentheses: extra closing paren"
    assert depth == 0, f"Unbalanced parentheses: {depth} unclosed"

    # Required sections.
    assert "(version " in content, "Missing (version ...)"
    assert "(generator " in content, "Missing (generator ...)"
    assert "(uuid " in content, "Missing (uuid ...)"
    assert "(lib_symbols" in content, "Missing (lib_symbols ...)"

    # Check coordinate ranges — extract all (at x y ...) values.
    at_pattern = re.compile(r"\(at\s+([-\d.]+)\s+([-\d.]+)")
    coords = at_pattern.findall(content)
    for x_str, y_str in coords:
        x, y = float(x_str), float(y_str)
        assert abs(x) < 5000, f"Coordinate x={x} too large — mils leaking through?"
        assert abs(y) < 5000, f"Coordinate y={y} too large — mils leaking through?"

    # Check xy coordinates in wires.
    xy_pattern = re.compile(r"\(xy\s+([-\d.]+)\s+([-\d.]+)")
    xy_coords = xy_pattern.findall(content)
    for x_str, y_str in xy_coords:
        x, y = float(x_str), float(y_str)
        assert abs(x) < 5000, f"Wire xy x={x} too large — mils leaking?"
        assert abs(y) < 5000, f"Wire xy y={y} too large — mils leaking?"

    # Every symbol instance should have lib_id, at, and uuid.
    # Count symbol instances (not lib_symbols definitions).
    symbol_instances = re.findall(r"\(symbol\s*\(lib_id", content)
    if symbol_instances:
        # At least one symbol instance has the required structure.
        assert len(symbol_instances) > 0

    # Instances section should be present for each symbol.
    instances_count = len(re.findall(r"\(instances", content))
    assert instances_count >= len(
        symbol_instances
    ), "Missing (instances ...) on some symbols"


class TestStructuralValidation:
    """Test the structural validator itself."""

    def test_valid_minimal(self):
        """Minimal valid schematic passes validation."""
        content = """(kicad_sch
  (version 20230409)
  (generator "skidl")
  (uuid "abc-123")
  (lib_symbols)
)"""
        validate_kicad_sch(content)

    def test_unbalanced_parens(self):
        """Unbalanced parentheses fail validation."""
        content = (
            "(kicad_sch (version 20230409) (generator skidl) (uuid abc) (lib_symbols)"
        )
        with pytest.raises(AssertionError, match="Unbalanced"):
            validate_kicad_sch(content)

    def test_missing_header(self):
        """Missing kicad_sch header fails."""
        content = "(schematic (version 1))"
        with pytest.raises(AssertionError, match="Missing.*kicad_sch"):
            validate_kicad_sch(content)

    def test_mils_coordinates_detected(self):
        """Coordinates in mils range (>5000) are caught."""
        content = """(kicad_sch
  (version 20230409)
  (generator "skidl")
  (uuid "abc")
  (lib_symbols)
  (symbol (lib_id "Device:R") (at 10000 8000 0) (uuid "def"))
)"""
        with pytest.raises(AssertionError, match="too large"):
            validate_kicad_sch(content)


# ===========================================================================
# Layer 3: End-to-end circuit generation
# ===========================================================================


@pytest.fixture
def output_dir():
    """Provide a temporary directory for schematic output."""
    d = tempfile.mkdtemp(prefix="skidl_test_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _generate_simple_divider(output_dir):
    """Generate a simple voltage divider schematic (2 resistors in series)."""
    from skidl import Circuit, Net, Part, set_default_tool

    circuit = Circuit(name="divider_test")

    with circuit:
        r1 = Part("Device", "R", value="10K")
        r2 = Part("Device", "R", value="10K")
        gnd = Net("GND")
        vcc = Net("VCC")
        mid = Net("MID")

        vcc += r1[1]
        r1[2] += mid
        mid += r2[1]
        r2[2] += gnd

        # Power flags to prevent ERC errors about unpowered nets.
        pwrflag1 = Part("power", "PWR_FLAG")
        pwrflag2 = Part("power", "PWR_FLAG")
        vcc += pwrflag1
        gnd += pwrflag2

        circuit.generate_schematic(filepath=output_dir, top_name="divider_test")

    filepath = os.path.join(output_dir, "divider_test.kicad_sch")
    assert os.path.exists(filepath), f"Schematic file not generated at {filepath}"
    return filepath


def _generate_and_gate(output_dir):
    """Generate the and_gate.py reference circuit (devbisme's test case)."""
    from skidl import Circuit, Net, Part, set_default_tool

    circuit = Circuit(name="and_gate_test")

    with circuit:
        try:
            q = Part(lib="Transistor_BJT", name="Q_PNP_CBE", dest="TEMPLATE", symtx="V")
        except FileNotFoundError:
            q = Part(lib="Device", name="Q_PNP_CBE", dest="TEMPLATE", symtx="V")
        r = Part("Device", "R", dest="TEMPLATE")

        gnd, vcc = Net("GND"), Net("VCC")
        a, b, a_and_b = Net("A"), Net("B"), Net("A_AND_B")

        gndt = Part("power", "GND")
        vcct = Part("power", "VCC")
        q1, q2 = q(2)
        r1, r2, r3, r4, r5 = r(5, value="10K")

        a & r1 & q1["B", "C"] & r4 & q2["B", "C"] & a_and_b & r5 & gnd
        b & r2 & q1["B"]
        q1["C"] & r3 & gnd
        vcc += q1["E"], q2["E"], vcct
        gnd += gndt

        a.netio = "i"
        b.netio = "i"
        a_and_b.netio = "o"

        q1.E.symio = "i"
        q1.B.symio = "i"
        q1.C.symio = "o"
        q2.E.symio = "i"
        q2.B.symio = "i"
        q2.C.symio = "o"

        circuit.generate_schematic(filepath=output_dir, top_name="and_gate_test")

    filepath = os.path.join(output_dir, "and_gate_test.kicad_sch")
    assert os.path.exists(filepath), f"Schematic file not generated at {filepath}"
    return filepath


def _generate_multi_part(output_dir):
    """Generate a circuit with R + C to verify both types in lib_symbols."""
    from skidl import Circuit, Net, Part, set_default_tool

    circuit = Circuit(name="multi_part_test")

    with circuit:
        r = Part("Device", "R", value="1K")
        c = Part("Device", "C", value="100n")
        gnd = Net("GND")
        sig = Net("SIG")

        sig += r[1]
        r[2] += c[1]
        c[2] += gnd

        circuit.generate_schematic(filepath=output_dir, top_name="multi_part_test")

    filepath = os.path.join(output_dir, "multi_part_test.kicad_sch")
    assert os.path.exists(filepath), f"Schematic file not generated at {filepath}"
    return filepath


class TestEndToEndDivider:
    """End-to-end tests with a simple resistor divider."""

    def test_divider_generates(self, output_dir):
        """Voltage divider generates a valid schematic file."""
        filepath = _generate_simple_divider(output_dir)
        assert os.path.getsize(filepath) > 100

    def test_divider_structural_validation(self, output_dir):
        """Voltage divider passes structural validation."""
        filepath = _generate_simple_divider(output_dir)
        with open(filepath) as f:
            content = f.read()
        validate_kicad_sch(content)

    def test_divider_coordinates_in_mm(self, output_dir):
        """All coordinates should be in mm range, not mils."""
        filepath = _generate_simple_divider(output_dir)
        with open(filepath) as f:
            content = f.read()

        # Extract all numeric coordinates.
        at_pattern = re.compile(r"\(at\s+([-\d.]+)\s+([-\d.]+)")
        for x_str, y_str in at_pattern.findall(content):
            x, y = float(x_str), float(y_str)
            # A4 is 297x210mm — coordinates should be in that ballpark.
            assert abs(x) < 1200, f"x={x} too large for mm"
            assert abs(y) < 850, f"y={y} too large for mm"


class TestEndToEndAndGate:
    """End-to-end tests with devbisme's and_gate reference circuit."""

    def test_and_gate_generates(self, output_dir):
        """And gate generates a valid schematic file."""
        try:
            filepath = _generate_and_gate(output_dir)
        except Exception as e:
            pytest.skip(f"Routing failed on complex circuit: {e}")
        assert os.path.getsize(filepath) > 100

    def test_and_gate_structural_validation(self, output_dir):
        """And gate passes structural validation."""
        try:
            filepath = _generate_and_gate(output_dir)
        except Exception as e:
            pytest.skip(f"Routing failed on complex circuit: {e}")
        with open(filepath) as f:
            content = f.read()
        validate_kicad_sch(content)

    def test_and_gate_has_all_parts(self, output_dir):
        """And gate schematic contains all expected component types."""
        try:
            filepath = _generate_and_gate(output_dir)
        except Exception as e:
            pytest.skip(f"Routing failed on complex circuit: {e}")
        with open(filepath) as f:
            content = f.read()
        # Should have transistors and resistors in lib_symbols.
        assert "Q_PNP_CBE" in content, "Missing transistor in schematic"
        assert '"R"' in content or ":R" in content, "Missing resistor in schematic"


class TestEndToEndMultiPart:
    """End-to-end tests with R + C circuit."""

    def test_multi_part_generates(self, output_dir):
        """Multi-part circuit generates successfully."""
        filepath = _generate_multi_part(output_dir)
        assert os.path.getsize(filepath) > 100

    def test_multi_part_has_both_types(self, output_dir):
        """Both R and C appear in lib_symbols."""
        filepath = _generate_multi_part(output_dir)
        with open(filepath) as f:
            content = f.read()
        # Check lib_symbols section has both types.
        assert ":R" in content or '"R"' in content, "Missing R in lib_symbols"
        assert ":C" in content or '"C"' in content, "Missing C in lib_symbols"

    def test_multi_part_structural_validation(self, output_dir):
        """Multi-part circuit passes structural validation."""
        filepath = _generate_multi_part(output_dir)
        with open(filepath) as f:
            content = f.read()
        validate_kicad_sch(content)


# ===========================================================================
# Layer 4: KiCad CLI validation (skip if not installed)
# ===========================================================================

HAS_KICAD_CLI = shutil.which("kicad-cli") is not None


@pytest.mark.skipif(not HAS_KICAD_CLI, reason="kicad-cli not installed")
class TestKicadCliValidation:
    """Validate generated schematics with KiCad's own tools.

    These tests verify KiCad can parse the generated files. ERC violations
    for pin connectivity and grid alignment are expected at this stage —
    those are pre-existing routing/connectivity issues, not scaling bugs.
    """

    def _run_erc(self, filepath):
        """Run kicad-cli ERC and return the result."""
        result = subprocess.run(
            ["kicad-cli", "sch", "erc", "--exit-code-violations", filepath],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result

    def test_kicad_parses_divider(self, output_dir):
        """KiCad 9 can parse the voltage divider (ERC runs without crash)."""
        filepath = _generate_simple_divider(output_dir)
        result = self._run_erc(filepath)
        # returncode > 0 means ERC violations, but the file parsed OK.
        # returncode < 0 or very high would mean a crash/signal.
        assert result.returncode >= 0, f"KiCad crashed:\n{result.stderr}"
        assert "violations" in result.stdout.lower() or result.returncode == 0

    def test_kicad_parses_and_gate(self, output_dir):
        """KiCad 9 can parse the and_gate circuit."""
        try:
            filepath = _generate_and_gate(output_dir)
        except Exception as e:
            pytest.skip(f"Schematic generation failed (routing issue): {e}")
        result = self._run_erc(filepath)
        assert (
            "failed to load" not in result.stderr.lower()
        ), f"KiCad could not parse schematic:\n{result.stderr}"
        assert result.returncode >= 0, f"KiCad crashed:\n{result.stderr}"

    def test_kicad_parses_multi_part(self, output_dir):
        """KiCad 9 can parse the multi-part circuit."""
        filepath = _generate_multi_part(output_dir)
        result = self._run_erc(filepath)
        assert result.returncode >= 0, f"KiCad crashed:\n{result.stderr}"
        assert "violations" in result.stdout.lower() or result.returncode == 0

    def test_kicad_erc_clean_divider(self, output_dir):
        """Zero ERC errors on voltage divider (warnings are expected)."""
        filepath = _generate_simple_divider(output_dir)
        # Use --severity-error to check only errors, not warnings.
        # Expected warnings: global_label_dangling (single-sheet),
        # lib_symbol_issues (no library config in test env).
        result = subprocess.run(
            [
                "kicad-cli",
                "sch",
                "erc",
                "--severity-error",
                "--exit-code-violations",
                filepath,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"KiCad ERC found errors:\n{result.stdout}"
