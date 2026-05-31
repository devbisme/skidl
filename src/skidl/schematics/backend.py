# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""Tool-agnostic schematic backend interface.

This module defines the dependency surface that the tool-agnostic decision
layer (``schematics/decisions.py``, ``schematics/snap.py``) needs from a
concrete schematic backend (e.g. ``tools/kicad9``). It is deliberately
tool-agnostic: it imports nothing from any ``skidl.tools.*`` package, and the
KiCad coordinate convention / S-expression syntax never leaks across this
boundary.

The split is: the agnostic layer *decides* (which pins overlap, which power
pins form a bus, how labels deconflict), expressed entirely in **render-mm**
coordinates as returned by ``backend.pin_render_pos``; the backend *measures*
(geometry queries) and *writes* (emission primitives).

See ``ARCHITECTURE-snap-backend-split.md`` (branch ``docs/snap-backend-split``)
for the full design, especially sections 2, 3, 5 and 7.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

try:  # pragma: no cover - typing.Protocol is stdlib on 3.8+
    from typing import Protocol, runtime_checkable
except ImportError:  # pragma: no cover
    from typing_extensions import Protocol, runtime_checkable  # type: ignore

# A pin direction in RENDER space: one of "U" | "D" | "L" | "R".
PinDir = str

# An opaque backend element (KiCad: an Sexp). The agnostic layer never
# inspects this; it only collects elements the backend produced.
Element = object


@dataclass
class LabelPlacement:
    """A resolved net-label / power-symbol placement (render-mm).

    ``anchor_xy`` is the electrical connection point and is FIXED on the pin
    (in KiCad the label/power-symbol ``at`` *is* the connection point).
    ``text_xy`` is where the label text renders and may be nudged by
    deconfliction. ``deconflictable`` is False for power symbols, whose anchor
    must not move (moving it disconnects the net).
    """

    anchor_xy: Tuple[float, float]
    text_xy: Tuple[float, float]
    deconflictable: bool


@runtime_checkable
class SchematicBackend(Protocol):
    """The geometry + emission surface a backend exposes to the agnostic layer.

    Geometry queries answer "where/which-way does the tool draw this?" in the
    tool's own flip/mirror/rotate convention. Emission primitives write the
    tool's native elements. See the architecture doc, section 3.
    """

    # capability gate — backends that do not implement the geometry interface
    # report supports_snap=False so the snap phase is skipped explicitly.
    supports_snap: bool

    # ---- GEOMETRY (tool-specific) ----

    def pin_render_pos(self, pin, sheet_tx) -> Tuple[float, float]:
        """(x, y) in mm where the tool will actually DRAW this pin."""
        ...

    def pin_render_dir(self, pin, sheet_tx) -> PinDir:
        """Which way the pin points AFTER the tool's transform."""
        ...

    def is_power_net_name(self, name: str) -> bool:
        """True if ``name`` matches a tool power-symbol."""
        ...

    def render_xy(self, lx, ly, part, sheet_tx) -> Tuple[float, float]:
        """Render-mm position of an arbitrary part-local point (e.g. a body
        bbox corner) under the tool's transform convention. Same convention as
        ``pin_render_pos`` but for non-pin points; needed by power-bus
        body-crossing checks."""
        ...

    def round_mm(self, val) -> float:
        """Round a coordinate to the tool's grid precision (KiCad: 2 dp)."""
        ...

    def solve_snap_tx(self, part, my_pin, target_render_xy, extend_dir, sheet_tx):
        """Return a new ``part.tx`` so ``my_pin`` renders at the target."""
        ...

    def label_bbox(self, text: str) -> Tuple[float, float]:
        """(width, height) in mm of a rendered net-label box for ``text``."""
        ...

    # ---- EMISSION (tool-specific) ----

    def emit_wire(self, x1, y1, x2, y2, *, net_name: Optional[str] = None) -> Element:
        ...

    def emit_label(self, pin, sheet_tx, *, at=None, angle=None, force: bool = False) -> Optional[Element]:
        ...

    def emit_no_connect(self, x, y) -> Element:
        ...

    def emit_power_symbol(self, pin, net_name, sheet_tx) -> Optional[Element]:
        ...

    def emit_part(self, part, sheet_tx, uuid_path) -> Element:
        ...

    def emit_junction(self, x, y) -> Element:
        ...


class RenderContext:
    """Memoizes ``pin_render_pos`` / ``pin_render_dir`` for a backend.

    Per architecture doc section 7, item 6: the cache key cannot be just
    ``(pin, sheet_tx)`` because snap mutates ``part.tx`` mid-pipeline. The
    simplest safe discipline (adopted here) is to only use the cache once snap
    has finalized all ``part.tx`` values; snap's own pre-finalization
    measurements go straight to the backend and are not cached.

    The key folds in the part's transform coefficients so that any ``part.tx``
    mutation invalidates a stale entry automatically.
    """

    def __init__(self, backend: SchematicBackend):
        self._backend = backend
        self._pos_cache: Dict[tuple, Tuple[float, float]] = {}
        self._dir_cache: Dict[tuple, PinDir] = {}

    @staticmethod
    def _tx_key(tx):
        if tx is None:
            return None
        return (tx.a, tx.b, tx.c, tx.d, tx.dx, tx.dy)

    def _key(self, pin, sheet_tx):
        part_tx = getattr(getattr(pin, "part", None), "tx", None)
        return (id(pin), self._tx_key(part_tx), self._tx_key(sheet_tx))

    def pin_render_pos(self, pin, sheet_tx) -> Tuple[float, float]:
        k = self._key(pin, sheet_tx)
        v = self._pos_cache.get(k)
        if v is None:
            v = self._backend.pin_render_pos(pin, sheet_tx)
            self._pos_cache[k] = v
        return v

    def pin_render_dir(self, pin, sheet_tx) -> PinDir:
        k = self._key(pin, sheet_tx)
        v = self._dir_cache.get(k)
        if v is None:
            v = self._backend.pin_render_dir(pin, sheet_tx)
            self._dir_cache[k] = v
        return v

    def invalidate(self):
        """Drop all cached geometry (call after any phase that moves parts)."""
        self._pos_cache.clear()
        self._dir_cache.clear()


__all__ = [
    "PinDir",
    "Element",
    "LabelPlacement",
    "SchematicBackend",
    "RenderContext",
]
