# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""Concrete KiCad-9 implementation of the tool-agnostic SchematicBackend.

Every method here delegates VERBATIM to the existing functions in
``sexp_schematic.py`` — this is a thin adapter so the agnostic decision layer
(``schematics/decisions.py``) can reach the KiCad render geometry and emission
primitives through the interface in ``schematics/backend.py`` without importing
``skidl.tools.kicad9`` directly. The KiCad coordinate math and S-expression
syntax stay in ``sexp_schematic.py``; nothing here changes output.
"""

from skidl.geometry import Point, Tx

from . import sexp_schematic as _ksch


class Kicad9Backend:
    """Adapter exposing kicad9 geometry + emission as a SchematicBackend."""

    supports_snap = True

    # ---- GEOMETRY ----

    def pin_render_pos(self, pin, sheet_tx):
        """KiCad render-mm position of a pin == ``_kicad_pin_pos``."""
        return _ksch._kicad_pin_pos(pin, getattr(pin.part, "tx", Tx()), sheet_tx)

    def pin_render_dir(self, pin, sheet_tx):
        """Render-space pin direction == ``calc_pin_dir``.

        Note: the present ``calc_pin_dir`` ignores ``sheet_tx`` (see the
        architecture doc, section 3 / section 6). Folding ``sheet_tx`` in would
        change output, so this adapter preserves the current behavior exactly.
        """
        return _ksch.calc_pin_dir(pin)

    def is_power_net_name(self, name):
        return name in _ksch.pwr_symbol_names

    def render_xy(self, lx, ly, part, sheet_tx):
        """Render-mm of an arbitrary part-local point == ``_render_xy``."""
        return _ksch._render_xy(lx, ly, getattr(part, "tx", Tx()), sheet_tx)

    def round_mm(self, val):
        return _ksch._round_mm(val)

    def solve_snap_tx(self, part, my_pin, target_render_xy, extend_dir, sheet_tx):
        """Delegates to snap's placement-space transform solver.

        The current snap pipeline solves ``part.tx`` in SKiDL placement space
        (``schematics.snap._compute_snap_tx``); exposing it here keeps the
        interface complete without altering the (placement-space) behavior.
        """
        from skidl.schematics.snap import _compute_snap_tx

        return _compute_snap_tx(my_pin, part, target_render_xy, extend_dir)

    def label_bbox(self, text):
        """Rendered net-label box size in mm.

        Matches the fixed box that ``_deconflict_labels`` uses today
        (LABEL_W x LABEL_H), so the relocated deconfliction is byte-identical.
        """
        return (10.0, 2.0)

    # ---- EMISSION ----

    def emit_wire(self, x1, y1, x2, y2, *, net_name=None, uuid_seed=None):
        """Build a bare wire Sexp at render-mm coords.

        Mirrors the inline wire construction in the decision functions; the
        caller supplies the UUID seed so emitted UUIDs match the originals.
        """
        from simp_sexp import Sexp

        if uuid_seed is None:
            uuid_seed = f"wire:{x1}:{y1}:{x2}:{y2}"
        return Sexp(
            [
                "wire",
                ["pts", ["xy", x1, y1], ["xy", x2, y2]],
                ["stroke", ["width", 0], ["type", "default"]],
                ["uuid", _ksch._gen_uuid(uuid_seed)],
            ]
        )

    def emit_label(self, pin, sheet_tx, *, at=None, angle=None, force=False):
        return _ksch.net_label_to_sexp(pin, tx=sheet_tx, force=force)

    def emit_no_connect(self, x, y, *, uuid_seed=None):
        from simp_sexp import Sexp

        if uuid_seed is None:
            uuid_seed = f"nc:{x}:{y}"
        return Sexp(
            [
                "no_connect",
                ["at", _ksch._round_mm(x), _ksch._round_mm(y)],
                ["uuid", _ksch._gen_uuid(uuid_seed)],
            ]
        )

    def emit_power_symbol(self, pin, net_name, sheet_tx):
        return _ksch._power_symbol_to_sexp(pin, net_name, sheet_tx)

    def emit_part(self, part, sheet_tx, uuid_path):
        return _ksch.part_to_sexp(part, uuid_path, tx=sheet_tx)

    def emit_junction(self, x, y):
        # Junctions are emitted per-net via junction_to_sexp today; this
        # primitive is provided for interface completeness.
        from simp_sexp import Sexp

        return Sexp(
            [
                "junction",
                ["at", _ksch._round_mm(x), _ksch._round_mm(y)],
                ["diameter", 0],
                ["color", 0, 0, 0, 0],
                ["uuid", _ksch._gen_uuid(f"junction:{x}:{y}")],
            ]
        )


__all__ = ["Kicad9Backend"]
