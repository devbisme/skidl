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
    """Adapter exposing kicad9 geometry + emission as a SchematicBackend.

    Interface status (honest): geometry queries (pin_render_pos, pin_render_dir,
    is_power_net_name, render_xy, label_bbox) are LIVE — consumed by
    schematics.decisions. Among emission primitives, emit_wire and
    emit_no_connect ARE on the live path; emit_label/emit_part/
    emit_power_symbol/emit_junction are defined for completeness but the renderer
    still uses the module-level functions for those. solve_snap_tx is DEFERRED
    (raises; see doc P1b).
    """

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
        # DEFERRED (doc P1b) and NOT wired into the snap pipeline, which solves
        # part.tx in PLACEMENT space via schematics.snap._compute_snap_tx called
        # directly from snap.py. This interface method can't delegate correctly
        # anyway (it lacks `other_pin`, which _compute_snap_tx requires), and a
        # render-space solver here would change output. Raise rather than
        # silently mis-solve.
        raise NotImplementedError(
            "solve_snap_tx is deferred (doc P1b); snap solves in placement space "
            "via schematics.snap._compute_snap_tx, not through this interface."
        )

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
        # `at`/`angle` override placement is part of the interface contract but
        # not implemented here (the renderer positions labels at the pin via
        # net_label_to_sexp). Reject explicitly so callers can't assume override
        # support that isn't present.
        if at is not None or angle is not None:
            raise NotImplementedError(
                "emit_label override placement (at/angle) is not yet supported."
            )
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

    def apply_label_deconfliction(self, elements, node, sheet_tx):
        """Read global_label/wire Sexps, run the agnostic deconfliction
        decision, then mutate label ``at`` coords + append connecting wires.

        The Sexp reading and mutation (tool-specific) stay here; the overlap
        detection + nudge-target decision lives in
        ``schematics.decisions.deconflict_labels``.
        """
        from skidl.schematics import decisions as _decisions

        GRID = 1.27

        def _cell(x, y):
            return (round(x / GRID), round(y / GRID))

        # Build the occupancy seed in element order (label anchors keyed by
        # net, wire endpoints keyed None) — one pass, matching the original.
        occupied_seed = []
        for elem in elements:
            if not hasattr(elem, "__getitem__") or len(elem) < 1:
                continue
            if elem[0] == "global_label":
                at = next(
                    (s for s in elem if hasattr(s, "__getitem__") and len(s) and s[0] == "at"),
                    None,
                )
                if at and len(at) >= 3:
                    occupied_seed.append((_cell(float(at[1]), float(at[2])), elem[1]))
            elif elem[0] == "wire":
                pts = next(
                    (s for s in elem if hasattr(s, "__getitem__") and len(s) and s[0] == "pts"),
                    None,
                )
                if pts:
                    for xy in pts[1:]:
                        if hasattr(xy, "__getitem__") and len(xy) >= 3 and xy[0] == "xy":
                            occupied_seed.append((_cell(float(xy[1]), float(xy[2])), None))

        # Extract label records to move (in element order), with their `at` sexp.
        labels = []
        at_by_idx = {}
        for i, elem in enumerate(elements):
            if not (hasattr(elem, "__getitem__") and len(elem) >= 1 and elem[0] == "global_label"):
                continue
            at = next(
                (s for s in elem if hasattr(s, "__getitem__") and len(s) > 0 and s[0] == "at"),
                None,
            )
            if at is None or len(at) < 4:
                continue
            labels.append((i, elem[1], float(at[1]), float(at[2]), int(at[3])))
            at_by_idx[i] = at

        moves, new_wires = _decisions.deconflict_labels(
            labels, occupied_seed, node, self, sheet_tx
        )
        # Apply moves.
        for idx, nx, ny in moves:
            at = at_by_idx[idx]
            at[1], at[2] = nx, ny
        # Append connecting wires.
        from simp_sexp import Sexp

        for ax, ay, nx, ny in new_wires:
            elements.append(
                Sexp(
                    [
                        "wire",
                        ["pts", ["xy", _ksch._round_mm(ax), _ksch._round_mm(ay)], ["xy", nx, ny]],
                        ["stroke", ["width", 0], ["type", "default"]],
                        ["uuid", _ksch._gen_uuid(f"dcwire:{ax}:{ay}:{nx}:{ny}")],
                    ]
                )
            )

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
