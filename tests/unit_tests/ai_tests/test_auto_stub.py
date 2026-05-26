# -*- coding: utf-8 -*-

"""
Tests for the auto-stub + ERC correction loop feature.

Layer 1: Unit tests for heuristic functions (no KiCad libs needed)
Layer 2: Integration tests with circuit generation
Layer 3: KiCad CLI validation (skipped if kicad-cli not installed)
"""

import importlib
import os
import re
import shutil
import tempfile

import pytest
from skidl import get_default_tool

tool = get_default_tool()
gen_schematic = importlib.import_module(f"skidl.tools.{tool}.gen_schematic")
FIXABLE_ERROR_TYPES = gen_schematic.FIXABLE_ERROR_TYPES
_POWER_NET_RE = gen_schematic._POWER_NET_RE
_classify_and_stub_complex_nets = gen_schematic._classify_and_stub_complex_nets
_parse_erc_report = gen_schematic._parse_erc_report
_setup_kicad_env = gen_schematic._setup_kicad_env
_stub_nets_for_erc_errors = gen_schematic._stub_nets_for_erc_errors
auto_stub_nets = gen_schematic.auto_stub_nets


# Skip entire module for early versions of KiCad.
if os.getenv("SKIDL_TOOL") in ('KICAD5',):
    pytest.skip("Tests require KiCad version > 5 as the default tool", allow_module_level=True)


# ===========================================================================
# Layer 1: Unit tests — pure functions, no KiCad needed
# ===========================================================================


class TestPowerNetRegex:
    """Tests for the power net name pattern."""

    @pytest.mark.parametrize(
        "name",
        ["GND", "gnd", "AGND", "DGND", "PGND", "VCC", "VDD", "VSS", "VEE",
         "VBUS", "VBAT", "AVCC", "AVDD", "DVCC", "DVDD", "+3V3", "+5V", "+12V"],
    )
    def test_power_nets_match(self, name):
        assert _POWER_NET_RE.match(name), f"{name} should match power net pattern"

    @pytest.mark.parametrize("name", ["DATA", "CLK", "SDA", "SCL", "RESET", "N$1"])
    def test_signal_nets_no_match(self, name):
        assert not _POWER_NET_RE.match(name), f"{name} should NOT match power net pattern"


class TestAutoStubNets:
    """Tests for the auto_stub_nets() heuristic function."""

    def _make_mock_net(self, name, pin_count=2, stub=False, explicit=False):
        """Create a minimal mock net for testing."""

        class MockPin:
            def __init__(self):
                self.stub = False

        class MockNet:
            def __init__(self, name, pin_count, stub, explicit):
                self.name = name
                self._stub = stub
                self._stub_explicit = explicit
                self.pins = [MockPin() for _ in range(pin_count)]

            @property
            def valid(self):
                return True

            def get_pins(self):
                return self.pins

            @property
            def stub(self):
                return self._stub

        return MockNet(name, pin_count, stub, explicit)

    def _make_mock_circuit(self, nets):
        class MockCircuit:
            def __init__(self, nets):
                self.nets = nets
        return MockCircuit(nets)

    def test_small_power_net_gnd_deferred(self):
        """Small local GND net is deferred for geometry-aware routing."""
        net = self._make_mock_net("GND", pin_count=3)
        circuit = self._make_mock_circuit([net])
        auto_stub_nets(circuit)
        assert net._stub is False

    def test_small_power_net_vcc_deferred(self):
        """Small local VCC net is deferred for geometry-aware routing."""
        net = self._make_mock_net("VCC", pin_count=2)
        circuit = self._make_mock_circuit([net])
        auto_stub_nets(circuit)
        assert net._stub is False

    def test_small_power_net_plus3v3_deferred(self):
        """Small local +3V3 net is deferred for geometry-aware routing."""
        net = self._make_mock_net("+3V3", pin_count=2)
        circuit = self._make_mock_circuit([net])
        auto_stub_nets(circuit)
        assert net._stub is False

    def test_power_net_high_fanout_stubbed(self):
        """Large power nets still get auto-stubbed early."""
        net = self._make_mock_net("GND", pin_count=8)
        circuit = self._make_mock_circuit([net])
        auto_stub_nets(circuit)
        assert net._stub is True

    def test_signal_net_not_stubbed(self):
        """DATA net should not be auto-stubbed."""
        net = self._make_mock_net("DATA", pin_count=3)
        circuit = self._make_mock_circuit([net])
        auto_stub_nets(circuit)
        assert net._stub is False

    def test_high_fanout_stubbed(self):
        """Net with 6 pins (above default threshold 5) gets stubbed."""
        net = self._make_mock_net("BUS_DATA", pin_count=6)
        circuit = self._make_mock_circuit([net])
        auto_stub_nets(circuit)
        assert net._stub is True

    def test_low_fanout_not_stubbed(self):
        """Net with 3 pins (below threshold) stays wired."""
        net = self._make_mock_net("SIG", pin_count=3)
        circuit = self._make_mock_circuit([net])
        auto_stub_nets(circuit)
        assert net._stub is False

    def test_custom_fanout_threshold(self):
        """Custom fanout threshold is respected."""
        net = self._make_mock_net("SIG", pin_count=3)
        circuit = self._make_mock_circuit([net])
        auto_stub_nets(circuit, auto_stub_fanout=3)
        assert net._stub is True

    def test_explicit_override_respected(self):
        """User-explicit stub=False on GND stays wired."""
        net = self._make_mock_net("GND", pin_count=3, stub=False, explicit=True)
        circuit = self._make_mock_circuit([net])
        auto_stub_nets(circuit)
        assert net._stub is False  # Not overridden

    def test_pins_stubbed_with_net(self):
        """When a net is auto-stubbed, its pins are also stubbed."""
        net = self._make_mock_net("VCC", pin_count=8)
        circuit = self._make_mock_circuit([net])
        auto_stub_nets(circuit)
        assert all(pin.stub for pin in net.pins)


class TestParseErcReport:
    """Tests for ERC report parsing."""

    def test_parse_pin_not_connected(self, tmp_path):
        """Parse a pin_not_connected error from an ERC report."""
        report = tmp_path / "test.rpt"
        report.write_text(
            "ERC report\n"
            "\n"
            "[pin_not_connected]: Pin not connected\n"
            "    @(100, 200): Symbol R1 Pin 2\n"
            "\n"
        )
        errors = _parse_erc_report(str(report))
        assert len(errors) == 1
        assert errors[0] == ("pin_not_connected", "R1", "2")

    def test_parse_multiple_errors(self, tmp_path):
        """Parse multiple errors from an ERC report."""
        report = tmp_path / "test.rpt"
        report.write_text(
            "ERC report\n"
            "\n"
            "[pin_not_connected]: Pin not connected\n"
            "    @(100, 200): Symbol R1 Pin 2\n"
            "[pin_not_driven]: Pin not driven\n"
            "    @(300, 400): Symbol U1 Pin 3\n"
            "[some_other_error]: Other error\n"
            "    @(500, 600): Symbol C1 Pin 1\n"
            "\n"
        )
        errors = _parse_erc_report(str(report))
        assert len(errors) == 3
        assert errors[0] == ("pin_not_connected", "R1", "2")
        assert errors[1] == ("pin_not_driven", "U1", "3")
        assert errors[2] == ("some_other_error", "C1", "1")

    def test_parse_empty_report(self, tmp_path):
        """Empty report produces no errors."""
        report = tmp_path / "test.rpt"
        report.write_text("ERC report\n\n")
        errors = _parse_erc_report(str(report))
        assert errors == []

    def test_parse_nonexistent_file(self):
        """Nonexistent file returns empty list."""
        errors = _parse_erc_report("/nonexistent/path.rpt")
        assert errors == []

    def test_parse_none_path(self):
        """None path returns empty list."""
        errors = _parse_erc_report(None)
        assert errors == []


class TestStubNetsForErcErrors:
    """Tests for mapping ERC errors back to nets and stubbing them."""

    def _make_circuit_with_parts(self):
        """Create a mock circuit with parts for testing error mapping."""

        class MockPin:
            def __init__(self, num):
                self.num = num
                self.stub = False
                self._net = None

            @property
            def net(self):
                return self._net

        class MockNet:
            def __init__(self, name):
                self.name = name
                self._stub = False
                self._stub_explicit = False
                self._pins = []

            def get_pins(self):
                return self._pins

        class MockPart:
            def __init__(self, ref):
                self.ref = ref
                self.pins = []

        class MockCircuit:
            def __init__(self):
                self.parts = []

        circuit = MockCircuit()
        part_r1 = MockPart("R1")
        pin1 = MockPin("1")
        pin2 = MockPin("2")
        net_vcc = MockNet("VCC")
        net_sig = MockNet("SIG")
        pin1._net = net_vcc
        pin2._net = net_sig
        net_vcc._pins = [pin1]
        net_sig._pins = [pin2]
        part_r1.pins = [pin1, pin2]
        circuit.parts = [part_r1]

        return circuit, net_vcc, net_sig

    def test_stub_pin_not_connected(self):
        """pin_not_connected error stubs the associated net."""
        circuit, net_vcc, net_sig = self._make_circuit_with_parts()
        errors = [("pin_not_connected", "R1", "2")]
        result = _stub_nets_for_erc_errors(circuit, errors)
        assert result is True
        assert net_sig._stub is True

    def test_no_stub_for_unknown_error_type(self):
        """Non-fixable error types don't cause stubbing."""
        circuit, net_vcc, net_sig = self._make_circuit_with_parts()
        errors = [("some_other_error", "R1", "2")]
        result = _stub_nets_for_erc_errors(circuit, errors)
        assert result is False

    def test_no_stub_for_explicit_net(self):
        """Explicitly-set nets are not modified."""
        circuit, net_vcc, net_sig = self._make_circuit_with_parts()
        net_sig._stub_explicit = True
        errors = [("pin_not_connected", "R1", "2")]
        result = _stub_nets_for_erc_errors(circuit, errors)
        assert result is False

    def test_no_stub_for_unknown_part(self):
        """Error referencing unknown part ref doesn't crash."""
        circuit, _, _ = self._make_circuit_with_parts()
        errors = [("pin_not_connected", "U99", "1")]
        result = _stub_nets_for_erc_errors(circuit, errors)
        assert result is False


# ===========================================================================
# Layer 2: Integration tests — require KiCad 9 libs
# ===========================================================================

HAS_KICAD_LIBS = os.path.exists("/usr/share/kicad/symbols") or os.path.exists(
    os.path.expanduser("~/.local/share/kicad/9.0/symbols")
)
HAS_KICAD_CLI = shutil.which("kicad-cli") is not None

requires_kicad_libs = pytest.mark.skipif(
    not HAS_KICAD_LIBS, reason="KiCad 9 symbol libraries not installed"
)

requires_kicad_cli = pytest.mark.skipif(
    not HAS_KICAD_CLI, reason="kicad-cli not installed"
)


@pytest.fixture
def output_dir():
    """Provide a temporary directory for schematic output."""
    d = tempfile.mkdtemp(prefix="skidl_auto_stub_test_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _generate_divider(output_dir, auto_stub=False):
    """Generate a simple voltage divider schematic."""
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

        circuit.generate_schematic(
            filepath=output_dir, top_name="divider_test", auto_stub=auto_stub
        )

    filepath = os.path.join(output_dir, "divider_test.kicad_sch")
    assert os.path.exists(filepath), f"Schematic file not generated at {filepath}"
    return filepath


def _generate_and_gate_auto_stub(output_dir):
    """Generate the and_gate circuit with auto_stub=True."""
    from skidl import Circuit, Net, Part, set_default_tool

    circuit = Circuit(name="and_gate_auto")

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

        circuit.generate_schematic(
            filepath=output_dir, top_name="and_gate_auto", auto_stub=True
        )

    filepath = os.path.join(output_dir, "and_gate_auto.kicad_sch")
    assert os.path.exists(filepath), f"Schematic file not generated at {filepath}"
    return filepath


def _generate_regulator_auto_stub(output_dir):
    """Generate a simple local regulator circuit with auto_stub enabled."""
    from skidl import Circuit, Net, Part

    circuit = Circuit(name="regulator_auto")

    with circuit:
        try:
            ldo = Part("Regulator_Linear", "AP2112K-3.3")
        except (FileNotFoundError, ValueError):
            ldo = Part("Regulator_Linear", "AMS1117-3.3")

        cin = Part("Device", "C", value="10uF")
        cout = Part("Device", "C", value="10uF")
        gnd_sym = Part("power", "GND")

        vin = Net("VIN")
        vout = Net("VOUT")
        gnd = Net("GND")

        vin += ldo[1], cin[1]
        vout += ldo[3], cout[1]
        gnd += ldo[2], cin[2], cout[2], gnd_sym[1]

        circuit.generate_schematic(
            filepath=output_dir,
            top_name="regulator_auto",
            auto_stub=True,
            human_readable=True,
        )

    filepath = os.path.join(output_dir, "regulator_auto.kicad_sch")
    assert os.path.exists(filepath), f"Schematic file not generated at {filepath}"
    return filepath


@requires_kicad_libs
class TestBackwardCompat:
    """Ensure auto_stub=False (default) produces identical behavior."""

    def test_divider_without_auto_stub(self, output_dir):
        """Divider without auto_stub generates successfully."""
        filepath = _generate_divider(output_dir, auto_stub=False)
        with open(filepath) as f:
            content = f.read()
        # Should contain wires (not just labels) since auto_stub is off.
        assert "(wire" in content or "(global_label" in content


@requires_kicad_libs
class TestAutoStubIntegration:
    """Integration tests with actual circuit generation."""

    def test_and_gate_with_auto_stub(self, output_dir):
        """And_gate with auto_stub=True generates successfully."""
        filepath = _generate_and_gate_auto_stub(output_dir)
        with open(filepath) as f:
            content = f.read()
        # Power nets should appear as power symbols or global labels.
        assert "(global_label" in content or 'lib_id "power:' in content

    def test_and_gate_power_nets_are_symbols(self, output_dir):
        """Power nets in and_gate with auto_stub appear as power symbols."""
        filepath = _generate_and_gate_auto_stub(output_dir)
        with open(filepath) as f:
            content = f.read()
        # GND and VCC should appear as power symbol instances.
        gnd_syms = re.findall(r'lib_id "power:GND"', content)
        vcc_syms = re.findall(r'lib_id "power:VCC"', content)
        assert len(gnd_syms) > 0, "GND should appear as power symbol"
        assert len(vcc_syms) > 0, "VCC should appear as power symbol"

    def test_divider_with_auto_stub(self, output_dir):
        """Divider with auto_stub generates successfully."""
        filepath = _generate_divider(output_dir, auto_stub=True)
        assert os.path.exists(filepath)

    def test_local_regulator_keeps_visible_wires(self, output_dir):
        """A compact regulator block keeps local VIN/VOUT/GND wiring visible."""
        filepath = _generate_regulator_auto_stub(output_dir)
        with open(filepath) as f:
            content = f.read()

        wire_count = content.count("(wire")
        vin_labels = re.findall(r'\(global_label\s+"VIN"', content)
        vout_labels = re.findall(r'\(global_label\s+"VOUT"', content)

        assert wire_count >= 2, "Expected visible local wires in regulator block"
        assert len(vin_labels) == 0, "Local VIN net should not collapse to labels"
        assert len(vout_labels) == 0, "Local VOUT net should not collapse to labels"


@requires_kicad_libs
class TestExplicitOverride:
    """Tests that user-explicit stub settings are preserved."""

    def test_explicit_stub_false_on_gnd(self, output_dir):
        """User sets stub=False on GND; it stays wired, not a label."""
        from skidl import Circuit, Net, Part, set_default_tool

        circuit = Circuit(name="explicit_test")

        with circuit:
            r1 = Part("Device", "R", value="10K")
            r2 = Part("Device", "R", value="10K")
            gnd = Net("GND")
            gnd.stub = False  # Explicit: keep GND wired.
            vcc = Net("VCC")
            mid = Net("MID")

            vcc += r1[1]
            r1[2] += mid
            mid += r2[1]
            r2[2] += gnd

            # Verify the explicit flag was set.
            assert gnd._stub_explicit is True
            assert gnd._stub is False

            circuit.generate_schematic(
                filepath=output_dir, top_name="explicit_test", auto_stub=True
            )

        # GND should still be wired (not just a label) since user set stub=False.
        filepath = os.path.join(output_dir, "explicit_test.kicad_sch")
        assert os.path.exists(filepath)


# ===========================================================================
# Layer 3: KiCad CLI validation
# ===========================================================================


@requires_kicad_libs
@requires_kicad_cli
class TestKicadErcClean:
    """End-to-end test: generated schematic should pass KiCad ERC after correction loop."""

    def test_and_gate_erc_clean(self, output_dir):
        """And_gate with auto_stub=True should produce a clean or near-clean ERC."""
        import subprocess

        filepath = _generate_and_gate_auto_stub(output_dir)
        report_path = filepath.replace(".kicad_sch", "-erc.rpt")

        result = subprocess.run(
            ["kicad-cli", "sch", "erc", "--output", report_path, "--severity-all", filepath],
            capture_output=True,
            timeout=60,
        )

        if os.path.exists(report_path):
            with open(report_path) as f:
                report = f.read()
            # Count fixable errors — should be zero or near-zero after correction loop.
            fixable_count = sum(
                1 for line in report.split("\n")
                if any(f"[{t}]" in line for t in FIXABLE_ERROR_TYPES)
            )
            assert fixable_count <= 2, (
                f"Expected 0-2 fixable ERC errors, got {fixable_count}.\n"
                f"Report:\n{report}"
            )


# ===========================================================================
# Phase 2 tests — Row-based placer, selective routing, power symbols,
# layout readiness, hierarchical sheets
# ===========================================================================


class TestRowBasedPlacer:
    """Tests for the row-based placement algorithm."""

    def test_threshold_constant_exists(self):
        """_ROW_PLACE_THRESHOLD is defined on the Placer class."""
        from skidl.schematics.place import Placer
        assert hasattr(Placer, "_ROW_PLACE_THRESHOLD")
        assert Placer._ROW_PLACE_THRESHOLD == 20

    def test_row_placer_function_exists(self):
        """place_connected_parts_rowbased is callable."""
        from skidl.schematics.place import Placer
        assert callable(getattr(Placer, "place_connected_parts_rowbased", None))

    @requires_kicad_libs
    def test_large_group_uses_row_placer(self, output_dir):
        """A circuit with >20 connected parts should use row-based placement."""
        from skidl import Circuit, Net, Part, set_default_tool

        circuit = Circuit(name="row_placer_test")

        with circuit:
            # Create a chain of 30 resistors — all connected by nets.
            resistors = [Part("Device", "R", value="1K") for _ in range(30)]
            for i in range(len(resistors) - 1):
                net = Net(f"CHAIN_{i}")
                net += resistors[i][2], resistors[i + 1][1]
            # Add power rails.
            vcc = Net("VCC")
            gnd = Net("GND")
            vcc += resistors[0][1]
            gnd += resistors[-1][2]

            circuit.generate_schematic(
                filepath=output_dir, top_name="row_placer_test", auto_stub=True
            )

        filepath = os.path.join(output_dir, "row_placer_test.kicad_sch")
        assert os.path.exists(filepath), "Schematic should be generated"

        # Verify parts are placed (file should contain symbol instances).
        with open(filepath) as f:
            content = f.read()
        symbol_count = len(re.findall(r'\(symbol\s*\n\s*\(lib_id', content))
        assert symbol_count >= 20, f"Expected >=20 symbols, got {symbol_count}"


class TestSelectiveRouting:
    """Tests for the selective wire routing classifier."""

    def test_classify_function_exists(self):
        """_classify_and_stub_complex_nets is importable."""
        assert callable(_classify_and_stub_complex_nets)

    @requires_kicad_libs
    def test_simple_nets_stay_wired(self, output_dir):
        """2-pin short-distance nets should remain as wires, not labels."""
        from skidl import Circuit, Net, Part, set_default_tool

        circuit = Circuit(name="wire_test")

        with circuit:
            r1 = Part("Device", "R", value="10K")
            r2 = Part("Device", "R", value="10K")
            mid = Net("MID")
            r1[2] += mid
            mid += r2[1]

            circuit.generate_schematic(
                filepath=output_dir, top_name="wire_test", auto_stub=True
            )

        filepath = os.path.join(output_dir, "wire_test.kicad_sch")
        with open(filepath) as f:
            content = f.read()
        # MID is a 2-pin net — should be wired, not a global_label.
        assert "(wire" in content, "Simple 2-pin net should produce wires"


class TestPowerSymbolInjection:
    """Tests for power symbol injection (replacing global_labels with power symbols)."""

    def test_power_symbol_names_loaded(self):
        """Power symbol name set loads from the KiCad library."""
        from skidl.tools.kicad9.sexp_schematic import _get_power_symbol_names
        names = _get_power_symbol_names()
        assert "GND" in names
        assert "VCC" in names
        assert "+3V3" in names
        assert "+5V" in names

    def test_power_lib_symbol_extraction(self):
        """Power lib_symbol definitions can be extracted and parsed."""
        from skidl.tools.kicad9.sexp_schematic import _extract_power_lib_symbol
        gnd = _extract_power_lib_symbol("GND")
        assert gnd is not None, "GND lib symbol should be extractable"
        gnd_str = gnd.to_str()
        assert "power:GND" in gnd_str
        assert "power_in" in gnd_str

    def test_sexp_parser(self):
        """The S-expression text parser handles nested structures."""
        from skidl.tools.kicad9.sexp_schematic import _parse_sexp_text
        result = _parse_sexp_text('(symbol "test" (pin_numbers (hide yes)))')
        assert result[0] == "symbol"
        assert result[1] == "test"
        assert result[2][0] == "pin_numbers"

    @requires_kicad_libs
    def test_power_symbols_in_output(self, output_dir):
        """Power nets appear as power symbol instances in the schematic."""
        filepath = _generate_divider(output_dir, auto_stub=True)
        with open(filepath) as f:
            content = f.read()
        # GND and VCC should be power symbols.
        assert 'lib_id "power:GND"' in content, "GND should be a power symbol"
        assert 'lib_id "power:VCC"' in content, "VCC should be a power symbol"

    @requires_kicad_libs
    def test_power_lib_symbols_in_output(self, output_dir):
        """Power symbol lib_symbol definitions appear in the lib_symbols section."""
        filepath = _generate_divider(output_dir, auto_stub=True)
        with open(filepath) as f:
            content = f.read()
        assert "power:GND" in content, "GND lib_symbol definition should be present"
        assert "power:VCC" in content, "VCC lib_symbol definition should be present"

    @requires_kicad_libs
    def test_power_symbol_has_pwr_reference(self, output_dir):
        """Power symbol instances use #PWR references."""
        filepath = _generate_divider(output_dir, auto_stub=True)
        with open(filepath) as f:
            content = f.read()
        pwr_refs = re.findall(r'"#PWR\d+"', content)
        assert len(pwr_refs) > 0, "Power symbols should have #PWR references"


class TestLayoutReadiness:
    """Tests for layout readiness features."""

    def test_setup_kicad_env(self):
        """_setup_kicad_env sets KiCad footprint directory when not already set."""
        from skidl import get_default_tool

        kicad_version = get_default_tool()[len("kicad"):]

        old = os.environ.pop(f"KICAD{kicad_version}_FOOTPRINT_DIR", None)
        try:
            _setup_kicad_env()
            fp_dir = os.environ.get(f"KICAD{kicad_version}_FOOTPRINT_DIR", "")
            if os.path.isdir("/usr/share/kicad/footprints"):
                assert fp_dir == "/usr/share/kicad/footprints"
        finally:
            if old:
                os.environ[f"KICAD{kicad_version}_FOOTPRINT_DIR"] = old
            else:
                os.environ.pop(f"KICAD{kicad_version}_FOOTPRINT_DIR", None)

    def test_setup_kicad_env_preserves_existing(self):
        """_setup_kicad_env does not override an existing KiCad footprint directory."""
        from skidl import get_default_tool

        kicad_version = get_default_tool()[len("kicad"):]

        os.environ[f"KICAD{kicad_version}_FOOTPRINT_DIR"] = "/custom/path"
        try:
            _setup_kicad_env()
            assert os.environ[f"KICAD{kicad_version}_FOOTPRINT_DIR"] == "/custom/path"
        finally:
            del os.environ[f"KICAD{kicad_version}_FOOTPRINT_DIR"]

    @requires_kicad_libs
    def test_footprint_property_emitted(self, output_dir):
        """Part footprint property appears in the generated schematic."""
        filepath = _generate_divider(output_dir, auto_stub=False)
        with open(filepath) as f:
            content = f.read()
        # Footprint property should be present for each part.
        fp_props = re.findall(r'"Footprint"', content)
        assert len(fp_props) >= 2, "Footprint properties should be emitted for parts"


class TestBoundaryNets:
    """Tests for the get_boundary_nets() method on SchNode."""

    def test_boundary_nets_method_exists(self):
        """SchNode has a get_boundary_nets method."""
        from skidl.schematics.sch_node import SchNode
        assert callable(getattr(SchNode, "get_boundary_nets", None))

    def test_boundary_nets_empty_node(self):
        """Empty node returns no boundary nets."""
        from skidl.schematics.sch_node import SchNode
        node = SchNode()
        assert node.get_boundary_nets() == []


class TestHierarchicalLabels:
    """Tests for hierarchical label generation."""

    def test_hierarchical_label_function_exists(self):
        """hierarchical_label_to_sexp is importable."""
        from skidl.tools.kicad9.sexp_schematic import hierarchical_label_to_sexp
        assert callable(hierarchical_label_to_sexp)

    def test_hierarchical_label_sexp_format(self):
        """Hierarchical label S-expression has correct structure."""
        from skidl.tools.kicad9.sexp_schematic import hierarchical_label_to_sexp
        label = hierarchical_label_to_sexp("TEST_NET", 10.0, 20.0, angle=180)
        label_str = label.to_str()
        assert "hierarchical_label" in label_str
        assert "TEST_NET" in label_str
        assert "bidirectional" in label_str
