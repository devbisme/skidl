# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Shared S-expression schematic generation for KiCad 6/8/9.

Converts placed+routed SchNode trees into .kicad_sch files.
Used by kicad6, kicad8, and kicad9 gen_schematic thin wrappers.

Sources:
  - part_to_sexp / wire_to_sexp: upstream sexp_schematics branch (devbisme)
  - Hierarchy / custom fields / lib_symbols: feature/kicad8-gen-schematic (PR #281)
  - Net label logic: feature/inject-net-labels (PR #280)
  - Original kicad5 hierarchy walker: node_to_eeschema (kicad5/gen_schematic.py)
  - Credit: cyberhuman (PR #270) for initial KiCad 8 schematic work
"""

import copy
import datetime
import os
import uuid
from collections import OrderedDict

from simp_sexp import Sexp

from skidl.geometry import Point, Tx
from skidl.pckg_info import __version__
from skidl.schematics.net_terminal import NetTerminal
from skidl.utilities import export_to_all

# UUID namespace — same as gen_netlist.py so UUIDs are cross-referenceable.
_NAMESPACE_UUID = uuid.UUID("7026fcc6-e1a0-409e-aaf4-6a17ea82654f")

# ---------------------------------------------------------------------------
# Power symbol support
# ---------------------------------------------------------------------------

# Cached set of power symbol names from the KiCad library.
_power_symbol_names_cache = None
# Cached raw S-expression text for power lib symbols.
_power_lib_text_cache = None
# Track which power symbols are used in the current schematic.
_used_power_symbols = set()
# Counter for #PWR references.
_pwr_counter = [0]


def _get_power_lib_text():
    """Load the raw text of the power symbol library. Cached."""
    from skidl import get_default_tool

    kicad_version = get_default_tool()[len("kicad"):]

    global _power_lib_text_cache
    if _power_lib_text_cache is not None:
        return _power_lib_text_cache

    for path in [
        os.environ.get(f"KICAD{kicad_version}_SYMBOL_DIR", ""),
        "/usr/share/kicad/symbols",
        "/usr/local/share/kicad/symbols",
        os.path.expanduser(f"~/.local/share/kicad/{kicad_version}.0/symbols"),
    ]:
        lib_path = os.path.join(path, "power.kicad_sym") if path else ""
        if lib_path and os.path.exists(lib_path):
            with open(lib_path, "r") as f:
                _power_lib_text_cache = f.read()
            return _power_lib_text_cache

    _power_lib_text_cache = ""
    return _power_lib_text_cache


def _get_power_symbol_names():
    """Return set of available power symbol names from the KiCad library."""
    global _power_symbol_names_cache
    if _power_symbol_names_cache is not None:
        return _power_symbol_names_cache

    import re

    text = _get_power_lib_text()
    if text:
        # Match top-level symbol definitions: (symbol "NAME" at indent level 1.
        _power_symbol_names_cache = set(
            re.findall(r'^\t\(symbol "([^"]+)"', text, re.MULTILINE)
        )
    else:
        # Fallback: hardcoded common power names.
        _power_symbol_names_cache = {
            "GND", "AGND", "DGND", "PGND", "GNDA", "GNDD", "GNDREF",
            "VCC", "VDD", "VSS", "VEE", "VBUS", "VBAT",
            "+3V3", "+3.3V", "+5V", "+12V", "+1V8", "+2V5", "+1V5",
            "+3.3VA", "+3.3VADC", "+3.3VDAC",
            "AVCC", "AVDD", "DVCC", "DVDD",
        }

    return _power_symbol_names_cache


def _extract_power_lib_symbol_raw(name):
    """Extract the raw S-expression text for a power symbol.

    Args:
        name: Power symbol name (e.g., "GND", "+3V3").

    Returns:
        str: Raw S-expression text for the symbol, or None if not found.
    """
    import re

    text = _get_power_lib_text()
    if not text:
        return None

    # Find the symbol definition start.
    pattern = re.compile(r'^\t\(symbol "' + re.escape(name) + r'"', re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None

    # Extract from opening paren to matching closing paren.
    start = match.start() + 1  # Skip the leading tab.
    depth = 0
    i = start
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1

    return None


def _parse_sexp_text(text):
    """Parse an S-expression string into a nested list structure.

    Handles escaped quotes inside quoted strings (e.g. ``"name \\"GND\\""``)
    which are common in KiCad power symbol Description fields.

    Args:
        text: S-expression string like '(symbol "GND" (pin ...))'.

    Returns:
        list: Nested list suitable for Sexp().
    """
    # Tokenize: handle escaped quotes inside quoted strings.
    tokens = []
    i = 0
    while i < len(text):
        c = text[i]
        if c in " \t\n\r":
            i += 1
        elif c == "(":
            tokens.append("(")
            i += 1
        elif c == ")":
            tokens.append(")")
            i += 1
        elif c == '"':
            # Quoted string — collect until unescaped closing quote.
            j = i + 1
            chars = []
            while j < len(text):
                if text[j] == "\\" and j + 1 < len(text):
                    chars.append(text[j + 1])
                    j += 2
                elif text[j] == '"':
                    j += 1
                    break
                else:
                    chars.append(text[j])
                    j += 1
            tokens.append(("Q", "".join(chars)))  # Tagged as quoted.
            i = j
        else:
            # Unquoted token.
            j = i
            while j < len(text) and text[j] not in " \t\n\r()\"":
                j += 1
            tokens.append(text[i:j])
            i = j

    stack = [[]]
    for token in tokens:
        if token == "(":
            stack.append([])
        elif token == ")":
            completed = stack.pop()
            stack[-1].append(completed)
        elif isinstance(token, tuple) and token[0] == "Q":
            stack[-1].append(token[1])  # Quoted string value.
        else:
            # Try numeric conversion for unquoted tokens.
            try:
                stack[-1].append(int(token))
            except ValueError:
                try:
                    stack[-1].append(float(token))
                except ValueError:
                    stack[-1].append(token)
    # Return the single top-level expression.
    return stack[0][0] if stack[0] else []


def _extract_power_lib_symbol(name):
    """Extract and parse the lib_symbol definition for a power symbol.

    The returned Sexp has its top-level symbol name changed to "power:NAME"
    so it matches the lib_id used in symbol instances.

    Args:
        name: Power symbol name (e.g., "GND", "+3V3").

    Returns:
        Sexp: Parsed symbol definition, or None if not found.
    """
    raw = _extract_power_lib_symbol_raw(name)
    if not raw:
        return None

    parsed = _parse_sexp_text(raw)
    if parsed and len(parsed) > 1:
        # Change the symbol name from "NAME" to "power:NAME" for lib_id matching.
        parsed[1] = f"power:{name}"

    return Sexp(parsed)


def _power_symbol_to_sexp(pin, net_name, tx):
    """Generate a power symbol instance S-expression.

    Args:
        pin: The pin where the power symbol should be placed.
        net_name: The power net name (e.g., "GND", "+3V3").
        tx: Sheet-level transformation matrix.

    Returns:
        Sexp: Power symbol instance, or None on failure.
    """
    _used_power_symbols.add(net_name)

    _pwr_counter[0] += 1
    pwr_ref = f"#PWR{_pwr_counter[0]:03d}"

    # Position at pin location.
    part_tx = getattr(pin.part, "tx", Tx())
    combined_tx = part_tx * tx
    pin_pt = getattr(pin, "pt", Point(pin.x, pin.y))
    pt = pin_pt * combined_tx

    x = _round_mm(pt.x)
    y = _round_mm(pt.y)

    # Power symbol angle: the symbol's pin orientation determines how
    # it should be rotated.  For most power symbols, the connection pin
    # is at (0, 0) and the graphical part extends in one direction.
    # We don't rotate — KiCad power symbols are designed to display correctly
    # at angle 0 (voltage symbols point up, GND symbols point down).
    angle = 0

    lib_id = f"power:{net_name}"
    inst_uuid = _gen_uuid(f"pwr:{net_name}:{x}:{y}:{_pwr_counter[0]}")

    symbol = Sexp(
        [
            "symbol",
            ["lib_id", lib_id],
            ["at", x, y, angle],
            ["unit", 1],
            ["exclude_from_sim", "yes"],
            ["in_bom", "no"],
            ["on_board", "yes"],
            ["dnp", "no"],
            ["fields_autoplaced", "yes"],
            ["uuid", inst_uuid],
        ]
    )

    # Reference property.
    symbol.append(
        Sexp(
            [
                "property",
                "Reference",
                pwr_ref,
                ["at", x, y - 1.27, 0],
                ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]],
            ]
        )
    )

    # Value property.
    symbol.append(
        Sexp(
            [
                "property",
                "Value",
                net_name,
                ["at", x, y - 3.81, 0],
                ["effects", ["font", ["size", 1.27, 1.27]]],
            ]
        )
    )

    # Footprint property.
    symbol.append(
        Sexp(
            [
                "property",
                "Footprint",
                "",
                ["at", x, y, 0],
                ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]],
            ]
        )
    )

    # Datasheet property.
    symbol.append(
        Sexp(
            [
                "property",
                "Datasheet",
                "",
                ["at", x, y, 0],
                ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]],
            ]
        )
    )

    # Pin entry (power symbols have a single pin "1").
    pin_uuid = _gen_uuid(f"pwr_pin:{net_name}:{x}:{y}:{_pwr_counter[0]}")
    symbol.append(Sexp(["pin", '"1"', ["uuid", pin_uuid]]))

    # Instances section.
    symbol.append(
        Sexp(
            [
                "instances",
                [
                    "project",
                    "SKiDL-Generated",
                    [
                        "path",
                        f"/{_gen_uuid('root_schematic')}",
                        ["reference", pwr_ref],
                        ["unit", 1],
                    ],
                ],
            ]
        )
    )

    return symbol


def _reset_power_symbol_state():
    """Reset power symbol state between schematic generations."""
    global _used_power_symbols
    _used_power_symbols = set()
    _pwr_counter[0] = 0


def _gen_uuid(name=""):
    """Generate a deterministic UUID from *name*, or a random one if empty."""
    if not name:
        return str(uuid.uuid4())
    return str(uuid.uuid5(_NAMESPACE_UUID, name))


def _round_mm(val, ndigits=2):
    """Round a value to *ndigits* decimal places for mm output.

    KiCad 9 uses mm with decimal precision.  The old integer .round()
    was fine for kicad5 (mils) but destroys sub-mm precision needed
    for pin-to-wire alignment in KiCad 9.
    """
    return round(val, ndigits)


# ---------------------------------------------------------------------------
# Paper sizes
# ---------------------------------------------------------------------------

A_SIZES = OrderedDict(
    [
        ("A4", (297, 210)),
        ("A3", (420, 297)),
        ("A2", (594, 420)),
        ("A1", (841, 594)),
        ("A0", (1189, 841)),
    ]
)


def _pick_paper_size(bbox):
    """Choose the smallest A-size paper that fits *bbox* (in mils)."""
    import math

    w = abs(bbox.w) if bbox.w and not math.isinf(bbox.w) else 0
    h = abs(bbox.h) if bbox.h and not math.isinf(bbox.h) else 0

    # Convert bbox dimensions from mils to mm.
    w_mm = w * 0.0254 if w else 0
    h_mm = h * 0.0254 if h else 0

    for name, (pw, ph) in A_SIZES.items():
        if w_mm <= pw and h_mm <= ph:
            return name
    return "A0"


# ---------------------------------------------------------------------------
# Part → S-expression
# ---------------------------------------------------------------------------


def part_to_sexp(part, tx=Tx()):
    """Create S-expression for a symbol instance.

    Applies part transform and sheet transform (Y-flip is in sheet_tx).
    Adds ``(mirror y)`` because the sheet transform's Y-flip negates pin
    Y-offsets, and KiCad must be told to mirror pin positions to match.

    Args:
        part: SKiDL Part object (placed).
        tx: Sheet-level transformation matrix.

    Returns:
        Sexp: Symbol S-expression.
    """
    part_tx = getattr(part, "tx", Tx())
    angle, mx, my = part_tx.analyze_transform()
    if mx:
        mirror = ["mirror", "x"]
    elif my:
        mirror = ["mirror", "y"]
    else:
        mirror = []
    tx = part_tx * tx
    origin = Point(_round_mm(tx.origin.x), _round_mm(tx.origin.y))
    unit_num = getattr(part, "num", 1)

    lib_name = (
        os.path.splitext(part.lib.filename)[0]
        if hasattr(part.lib, "filename") and part.lib.filename
        else "Device"
    )
    part_name = part.name or "Unknown"
    lib_id = f"{lib_name}:{part_name}"

    symbol_list = [
        "symbol",
        ["lib_id", lib_id],
        ["at", origin.x, origin.y, angle],
        mirror,
        ["unit", unit_num],
        ["exclude_from_sim", "no"],
        ["in_bom", "yes"],
        ["on_board", "yes"],
        ["dnp", "no"],
        ["fields_autoplaced", "yes"],
        ["uuid", _gen_uuid(part.hiername)],
    ]
    if not mirror:
        symbol_list.remove([])
    symbol = Sexp(symbol_list)

    # Reference
    symbol.append(
        Sexp(
            [
                "property",
                "Reference",
                part.ref,
                ["at", origin.x, origin.y - 2.54, angle],
                ["effects", ["font", ["size", 1.27, 1.27]], ["justify", "left"]],
            ]
        )
    )

    # Value
    symbol.append(
        Sexp(
            [
                "property",
                "Value",
                str(part.value),
                ["at", origin.x, origin.y + 2.54, angle],
                ["effects", ["font", ["size", 1.27, 1.27]], ["justify", "left"]],
            ]
        )
    )

    # Footprint
    symbol.append(
        Sexp(
            [
                "property",
                "Footprint",
                getattr(part, "footprint", ""),
                ["at", origin.x, origin.y, angle],
                ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]],
            ]
        )
    )

    # Datasheet
    symbol.append(
        Sexp(
            [
                "property",
                "Datasheet",
                getattr(part, "datasheet", "~") or "~",
                ["at", origin.x, origin.y, angle],
                ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]],
            ]
        )
    )

    # Description
    symbol.append(
        Sexp(
            [
                "property",
                "Description",
                getattr(part, "description", "") or "",
                ["at", origin.x, origin.y, angle],
                ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]],
            ]
        )
    )

    # Custom fields from part.fields dict.
    y_offset = 5.08
    if hasattr(part, "fields") and part.fields:
        for field_name, field_value in part.fields.items():
            if field_name.lower() in (
                "reference",
                "value",
                "footprint",
                "datasheet",
                "description",
            ):
                continue
            if field_value and str(field_value).strip():
                symbol.append(
                    Sexp(
                        [
                            "property",
                            field_name,
                            str(field_value),
                            ["at", origin.x, origin.y + y_offset, angle],
                            [
                                "effects",
                                ["font", ["size", 1.27, 1.27]],
                                ["hide", "yes"],
                            ],
                        ]
                    )
                )
                y_offset += 1.27

    # Pin entries (required by KiCad 8/9 for connectivity tracking).
    for pin in part.pins:
        pin_num = str(pin.num)
        pin_uuid = _gen_uuid(f"{part.hiername}_pin_{pin_num}")
        symbol.append(Sexp(["pin", f'"{pin_num}"', ["uuid", pin_uuid]]))

    # Instances section (required by KiCad 8/9 for correct reference display).
    symbol.append(
        Sexp(
            [
                "instances",
                [
                    "project",
                    "SKiDL-Generated",
                    [
                        "path",
                        f"/{_gen_uuid('root_schematic')}",
                        ["reference", part.ref],
                        ["unit", unit_num],
                    ],
                ],
            ]
        )
    )

    return symbol


# ---------------------------------------------------------------------------
# Library symbol definition
# ---------------------------------------------------------------------------


def part_to_lib_symbol_definition(part):
    """Extract library symbol definition from a part's draw_cmds.

    Args:
        part: SKiDL Part object.

    Returns:
        list: Nested list for the lib_symbols section.
    """
    lib_name = (
        os.path.splitext(part.lib.filename)[0]
        if hasattr(part.lib, "filename") and part.lib.filename
        else "Device"
    )
    part_name = part.name or "Unknown"
    lib_id = f"{lib_name}:{part_name}"

    symbol_def = [
        "symbol",
        lib_id,
        ["pin_numbers", ["hide", "yes"]],
        ["pin_names", ["offset", 0]],
        ["exclude_from_sim", "no"],
        ["in_bom", "yes"],
        ["on_board", "yes"],
    ]

    # Standard properties.
    symbol_def.extend(
        [
            [
                "property",
                "Reference",
                part.ref_prefix or "U",
                ["at", 2.032, 0, 90],
                ["effects", ["font", ["size", 1.27, 1.27]]],
            ],
            [
                "property",
                "Value",
                part_name,
                ["at", 0, 0, 90],
                ["effects", ["font", ["size", 1.27, 1.27]]],
            ],
            [
                "property",
                "Footprint",
                "",
                ["at", 0, 0, 0],
                ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]],
            ],
            [
                "property",
                "Datasheet",
                getattr(part, "datasheet", "~") or "~",
                ["at", 0, 0, 0],
                ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]],
            ],
        ]
    )

    if hasattr(part, "description") and part.description:
        symbol_def.append(
            [
                "property",
                "Description",
                part.description,
                ["at", 0, 0, 0],
                ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]],
            ]
        )

    # Process draw_cmds into sub-symbols.
    if hasattr(part, "draw_cmds") and part.draw_cmds:
        # Common graphics (unit 0).
        if 0 in part.draw_cmds:
            graphics = [
                copy.deepcopy(cmd) for cmd in part.draw_cmds[0] if cmd[0] != "pin"
            ]
            if graphics:
                symbol_def.append(["symbol", f"{part_name}_0_1"] + graphics)

        # Per-unit graphics and pins.
        for unit_num, draw_cmds in part.draw_cmds.items():
            if unit_num == 0:
                continue
            pin_cmds = [copy.deepcopy(cmd) for cmd in draw_cmds if cmd[0] == "pin"]
            graphics = [
                copy.deepcopy(cmd)
                for cmd in draw_cmds
                if cmd[0] not in ("pin", "property")
            ]
            if pin_cmds or graphics:
                unit_sym = ["symbol", f"{part_name}_{unit_num}_{unit_num}"]
                unit_sym.extend(graphics)
                unit_sym.extend(pin_cmds)
                symbol_def.append(unit_sym)

    symbol_def.append(["embedded_fonts", "no"])

    return symbol_def


# ---------------------------------------------------------------------------
# Wires, junctions, net labels
# ---------------------------------------------------------------------------


def wire_to_sexp(net, wire, tx=Tx(), junctions=None):
    """Create S-expression for wire segments.

    Splits segments at junction points so KiCad properly connects
    pins at wire endpoints.  Without this, a junction in the middle
    of a wire does **not** create separate connectivity segments.

    Args:
        net: Net associated with the wire.
        wire: List of Segments.
        tx: Transformation matrix.
        junctions: Optional list of junction Points (pre-transform).

    Returns:
        list[Sexp]: Wire S-expression objects.
    """

    # Build set of junction coordinates in mm (post-transform).
    junc_pts = set()
    if junctions:
        for j in junctions:
            jt = j * tx
            junc_pts.add((_round_mm(jt.x), _round_mm(jt.y)))

    def _make_wire(x1, y1, x2, y2):
        return Sexp(
            [
                "wire",
                ["pts", ["xy", x1, y1], ["xy", x2, y2]],
                ["stroke", ["width", 0], ["type", "default"]],
                ["uuid", _gen_uuid(f"wire:{net.name}:{x1}:{y1}:{x2}:{y2}")],
            ]
        )

    wires = []
    for segment in wire:
        w = segment * tx
        x1, y1 = _round_mm(w.p1.x), _round_mm(w.p1.y)
        x2, y2 = _round_mm(w.p2.x), _round_mm(w.p2.y)

        # Collect junction points that lie strictly between endpoints.
        splits = []
        for jx, jy in junc_pts:
            if x1 == x2 == jx:  # Vertical wire.
                lo, hi = min(y1, y2), max(y1, y2)
                if lo < jy < hi:
                    splits.append(jy)
            elif y1 == y2 == jy:  # Horizontal wire.
                lo, hi = min(x1, x2), max(x1, x2)
                if lo < jx < hi:
                    splits.append(jx)

        if not splits:
            wires.append(_make_wire(x1, y1, x2, y2))
        else:
            # Split into ordered sub-segments.
            if x1 == x2:  # Vertical – split by Y.
                pts = sorted({y1, y2, *splits})
                if y1 > y2:
                    pts.reverse()
                for a, b in zip(pts, pts[1:]):
                    wires.append(_make_wire(x1, a, x2, b))
            else:  # Horizontal – split by X.
                pts = sorted({x1, x2, *splits})
                if x1 > x2:
                    pts.reverse()
                for a, b in zip(pts, pts[1:]):
                    wires.append(_make_wire(a, y1, b, y2))

    return wires


def junction_to_sexp(net, junctions, tx=Tx()):
    """Create S-expression for junction points.

    Args:
        net: Net associated with the junctions.
        junctions: List of junction Points.
        tx: Transformation matrix.

    Returns:
        list[Sexp]: Junction S-expression objects.
    """
    result = []
    for junction in junctions:
        pt = junction * tx
        x, y = _round_mm(pt.x), _round_mm(pt.y)
        result.append(
            Sexp(
                [
                    "junction",
                    ["at", x, y],
                    ["diameter", 0],
                    ["color", 0, 0, 0, 0],
                    ["uuid", _gen_uuid(f"junction:{x}:{y}")],
                ]
            )
        )
    return result


def calc_pin_dir(pin):
    """Calculate pin direction accounting for part transformation matrix."""

    # Copy the part trans. matrix, but remove the translation vector, leaving only scaling/rotation stuff.
    tx = pin.part.tx
    tx = Tx(a=tx.a, b=tx.b, c=tx.c, d=tx.d)

    # Use the pin orientation to compute the pin direction vector.
    pin_vector = {
        "U": Point(0, 1),
        "D": Point(0, -1),
        "L": Point(-1, 0),
        "R": Point(1, 0),
    }[pin.orientation]

    # Rotate the direction vector using the part rotation matrix.
    pin_vector = pin_vector * tx

    # Create an integer tuple from the rotated direction vector.
    pin_vector = (int(round(pin_vector.x)), int(round(pin_vector.y)))

    # Return the pin orientation based on its rotated direction vector.
    return {
        (0, 1): "U",
        (0, -1): "D",
        (-1, 0): "L",
        (1, 0): "R",
    }[pin_vector]


def net_label_to_sexp(pin, tx=Tx(), force=False):
    """Create S-expression for a net label at a pin stub.

    Generates a power symbol if the net name matches a known KiCad power
    symbol, otherwise generates a global_label.

    Args:
        pin: Pin with net connection.
        tx: Transformation matrix.
        force: If True, skip the stub check (used for NetTerminal pins
            which always need a label regardless of stub state).

    Returns:
        Sexp or None: Label/power symbol S-expression, or None if no label needed.
    """
    if not force and (not pin.stub or not pin.is_connected()):
        return None
    
    # Check if this net matches a known KiCad power symbol.
    # If so, emit a power symbol instance instead of a global_label.
    # This eliminates power_pin_not_driven ERC errors.
    if pin.is_connected() and pin.net.name in _get_power_symbol_names():
        pwr = _power_symbol_to_sexp(pin, pin.net.name, tx)
        if pwr:
            return pwr

    # Use global_label for reliable connectivity.  KiCad 9's ERC treats
    # plain labels as dangling unless they sit in the interior of a wire
    # segment between two connection points.  global_label connects at
    # any pin or wire endpoint, producing only an informational "not
    # connected elsewhere" warning on single-sheet designs.
    label_type = "global_label"

    # Position at pin location (Y-flip is already in sheet_tx).
    pin_pt = getattr(pin, "pt", Point(pin.x, pin.y))
    part_tx = getattr(pin.part, "tx", Tx())
    pt = pin_pt * part_tx * tx

    # Map pin orientation to angle (degrees).
    orient_map = {"R": 180, "D": 90, "L": 0, "U": 270}
    angle = orient_map[calc_pin_dir(pin)]

    # Justify depends on label direction.
    justify = "left" if angle in (0, 90) else "right"

    label = Sexp(
        [
            label_type,
            pin.net.name,
            ["shape", "bidirectional"],
            ["at", _round_mm(pt.x), _round_mm(pt.y), angle],
            ["effects", ["font", ["size", 1.27, 1.27]], ["justify", justify]],
            ["uuid", _gen_uuid(f"label:{pin.net.name}:{pt.x}:{pt.y}")],
        ]
    )

    return label


# ---------------------------------------------------------------------------
# Title block
# ---------------------------------------------------------------------------


def create_title_block_sexp(title):
    """Create a title block S-expression."""
    return [
        "title_block",
        ["title", title],
        ["date", datetime.date.today().isoformat()],
        ["company", ""],
        ["comment", 1, "Generated with SKiDL"],
        ["comment", 2, ""],
        ["comment", 3, ""],
        ["comment", 4, ""],
    ]


# ---------------------------------------------------------------------------
# Hierarchical sheet reference
# ---------------------------------------------------------------------------


def create_hierarchical_sheet_sexp(node, sheet_tx):
    """Create a hierarchical sheet S-expression for insertion into a parent sheet.

    Includes sheet pins for boundary nets (nets connecting the child's
    circuitry to the parent).

    Args:
        node: SchNode for the child sheet.
        sheet_tx: Transformation matrix of the parent sheet.

    Returns:
        Sexp: Sheet S-expression.
    """
    bbox = node.bbox * node.tx * sheet_tx
    bx = _round_mm(bbox.ll.x)
    by = _round_mm(bbox.ll.y)
    bw = _round_mm(bbox.w)
    bh = _round_mm(bbox.h)
    sheet_uuid = _gen_uuid(f"sheet:{node.sheet_filename}")

    sheet = Sexp(
        [
            "sheet",
            ["at", bx, by],
            ["size", bw, bh],
            ["exclude_from_sim", "no"],
            ["in_bom", "yes"],
            ["on_board", "yes"],
            ["dnp", "no"],
            ["fields_autoplaced", "yes"],
            ["stroke", ["width", 0.1524], ["type", "solid"]],
            ["fill", ["color", 0, 0, 0, 0.0]],
            ["uuid", sheet_uuid],
            [
                "property",
                "Sheetname",
                node.name,
                ["at", bx, _round_mm(by - 0.7116), 0],
                [
                    "effects",
                    ["font", ["size", 1.27, 1.27]],
                    ["justify", "left", "bottom"],
                ],
            ],
            [
                "property",
                "Sheetfile",
                node.sheet_filename,
                ["at", bx, _round_mm(by + bh + 0.5846), 0],
                ["effects", ["font", ["size", 1.27, 1.27]], ["justify", "left", "top"]],
            ],
        ]
    )

    # Add sheet pins for boundary nets.
    if hasattr(node, "get_boundary_nets"):
        boundary_nets = node.get_boundary_nets()
        pin_spacing = 2.54  # mm between pins
        pin_y = by + pin_spacing
        for net in boundary_nets:
            # Skip power nets that become power symbols (they don't need sheet pins).
            if net.name in _get_power_symbol_names():
                continue
            # Skip stubbed nets (they use global labels).
            if getattr(net, "stub", False) or getattr(net, "_stub", False):
                continue

            pin_uuid = _gen_uuid(f"sheet_pin:{node.sheet_filename}:{net.name}")
            # Place pins along the left edge of the sheet.
            sheet.append(
                Sexp(
                    [
                        "pin",
                        net.name,
                        "bidirectional",
                        ["at", bx, _round_mm(pin_y), 180],
                        [
                            "effects",
                            ["font", ["size", 1.27, 1.27]],
                            ["justify", "left"],
                        ],
                        ["uuid", pin_uuid],
                    ]
                )
            )
            pin_y += pin_spacing

    return sheet


def hierarchical_label_to_sexp(net_name, pt_x, pt_y, angle=180):
    """Create a hierarchical_label S-expression for a boundary net in a child sheet.

    Args:
        net_name: Name of the boundary net.
        pt_x: X coordinate in mm.
        pt_y: Y coordinate in mm.
        angle: Label angle (degrees).

    Returns:
        Sexp: Hierarchical label S-expression.
    """
    return Sexp(
        [
            "hierarchical_label",
            net_name,
            ["shape", "bidirectional"],
            ["at", _round_mm(pt_x), _round_mm(pt_y), angle],
            ["effects", ["font", ["size", 1.27, 1.27]], ["justify", "left"]],
            ["uuid", _gen_uuid(f"hlabel:{net_name}:{pt_x}:{pt_y}")],
        ]
    )


# ---------------------------------------------------------------------------
# Sheet-level transform calculation (mirrors kicad5 calc_sheet_tx)
# ---------------------------------------------------------------------------

MILS_TO_MM = 0.0254


def _calc_sheet_tx(bbox):
    """Calculate transformation matrix for placing circuitry in a sheet.

    Mirrors the kicad5 calc_sheet_tx pattern:
      1. Y-flip via d=-1 (placement engine is Y-up, KiCad is Y-down)
      2. Mils-to-mm conversion via a/d scaling (KiCad 9 uses mm)
      3. Center content on the chosen paper size

    The Y-flip is built into this transform so callers must NOT apply
    tx_flip_y separately (that would double-flip and cancel it out).
    """
    paper = _pick_paper_size(bbox)
    pw, ph = A_SIZES[paper]  # mm

    # Apply Y-flip + mils→mm in one transform, then center on page.
    page_bbox = bbox * Tx(a=MILS_TO_MM, d=-MILS_TO_MM)
    page_ctr = Point(pw / 2, ph / 2)
    content_ctr = Point(
        (page_bbox.ll.x + page_bbox.ur.x) / 2,
        (page_bbox.ll.y + page_bbox.ur.y) / 2,
    )
    move = page_ctr - content_ctr

    # Snap centering offset to KiCad's 1.27mm grid (50 mils) so that
    # grid-aligned placement coordinates stay on-grid after the move.
    GRID_MM = 1.27
    move = Point(
        round(move.x / GRID_MM) * GRID_MM,
        round(move.y / GRID_MM) * GRID_MM,
    )

    tx = Tx(a=MILS_TO_MM, d=-MILS_TO_MM).move(move)

    return tx, paper


# ---------------------------------------------------------------------------
# Recursive hierarchy walker — node_to_sexp_schematic
# ---------------------------------------------------------------------------


def _fix_sheet_filename(node):
    """Ensure node.sheet_filename uses .kicad_sch extension (SchNode defaults to .sch)."""
    if node.sheet_filename and node.sheet_filename.endswith(".sch"):
        node.sheet_filename = node.sheet_filename[:-4] + ".kicad_sch"


@export_to_all
def node_to_sexp_schematic(node, sheet_tx=Tx(), version=20230409):
    """Convert a SchNode tree to S-expression schematic(s).

    Follows the same recursive pattern as kicad5's node_to_eeschema():
    - Flattened nodes: return elements for inclusion in the parent sheet.
    - Unflattened nodes: write a separate .kicad_sch file and return a
      sheet reference for the parent.

    Args:
        node: SchNode to convert.
        sheet_tx: Parent sheet transformation matrix.
        version: S-expression version number (20240108 for kicad6, 20230409 for kicad8/9).

    Returns:
        list[Sexp]: S-expression elements (parts, wires, labels, or a sheet ref).
    """
    # Fix filename extension for KiCad 6+ S-expression format.
    _fix_sheet_filename(node)

    elements = []

    if node.flattened:
        tx = node.tx * sheet_tx
    else:
        # Unflattened node gets its own sheet.
        flattened_bbox = node.internal_bbox()
        tx, paper = _calc_sheet_tx(flattened_bbox)

    # Recurse into children.
    for child in node.children.values():
        elements.extend(node_to_sexp_schematic(child, tx, version=version))

    # Collect lib_symbols needed for this node's parts.
    lib_symbols = {}
    for part in node.parts:
        if not isinstance(part, NetTerminal):
            lib_id = f"{part.lib.filename}:{part.name}"
            if lib_id not in lib_symbols:
                lib_symbols[lib_id] = part

    # Generate part S-expressions.
    for part in node.parts:
        if isinstance(part, NetTerminal):
            # NetTerminals become net labels.
            label = net_label_to_sexp(part.pins[0], tx=tx, force=True)
            if label:
                elements.append(label)
        else:
            elements.append(part_to_sexp(part, tx=tx))

    # Generate wire S-expressions (split at junction points).
    for net, wire in node.wires.items():
        net_junctions = node.junctions.get(net, [])
        elements.extend(wire_to_sexp(net, wire, tx=tx, junctions=net_junctions))

    # Generate junction S-expressions.
    for net, junctions in node.junctions.items():
        elements.extend(junction_to_sexp(net, junctions, tx=tx))

    # Generate net labels for stubbed pins.
    for part in node.parts:
        if isinstance(part, NetTerminal):
            continue
        for pin in part:
            label = net_label_to_sexp(pin, tx=tx)
            if label:
                elements.append(label)

    if node.flattened:
        # Return elements for inclusion in the parent sheet.
        return elements

    # --- Unflattened node: write a separate .kicad_sch file. ---

    # Add hierarchical labels for boundary nets (nets that cross the sheet boundary).
    if hasattr(node, "get_boundary_nets"):
        boundary_nets = node.get_boundary_nets()
        hlabel_y = 10.0  # Starting Y position in mm for labels along the left edge.
        for net in boundary_nets:
            # Skip power nets and stubbed nets.
            if net.name in _get_power_symbol_names():
                continue
            if getattr(net, "stub", False) or getattr(net, "_stub", False):
                continue
            elements.append(
                hierarchical_label_to_sexp(net.name, 5.0, hlabel_y, angle=180)
            )
            hlabel_y += 2.54

    # Build lib_symbols section for this sheet.
    lib_symbols_sexp = Sexp(["lib_symbols"])
    for lib_id, part in lib_symbols.items():
        lib_symbols_sexp.append(Sexp(part_to_lib_symbol_definition(part)))

    # Add power lib_symbols for any power symbols used in this sheet.
    for pwr_name in sorted(_used_power_symbols):
        pwr_lib_id = f"power:{pwr_name}"
        if pwr_lib_id not in lib_symbols:
            pwr_sexp = _extract_power_lib_symbol(pwr_name)
            if pwr_sexp:
                lib_symbols_sexp.append(pwr_sexp)

    schematic = Sexp(
        [
            "kicad_sch",
            ["version", version],
            ["generator", "skidl"],
            ["generator_version", __version__],
            ["uuid", _gen_uuid(f"sheet:{node.sheet_filename}")],
            ["paper", paper if not node.flattened else "A3"],
        ]
    )
    schematic.append(Sexp(create_title_block_sexp(node.title)))
    schematic.append(lib_symbols_sexp)

    for elem in elements:
        schematic.append(elem)

    # Write schematic file.
    filepath = os.path.join(node.filepath, node.sheet_filename)
    _write_sexp_schematic(schematic, filepath)

    # Return a hierarchical sheet reference for the parent.
    return [create_hierarchical_sheet_sexp(node, sheet_tx)]


# ---------------------------------------------------------------------------
# Top-level schematic assembly + write
# ---------------------------------------------------------------------------


@export_to_all
def write_top_schematic(circuit, node, filepath, top_name, title, version=20230409):
    """Generate and write the complete schematic from a placed+routed node tree.

    This is the main entry point called by each tool's gen_schematic().

    Args:
        circuit: The Circuit object.
        node: Root SchNode (placed and routed).
        filepath: Output directory.
        top_name: Base filename (without extension).
        title: Schematic title.
        version: S-expression version number.
    """
    top_name = top_name or "schematic"
    _fix_sheet_filename(node)
    _reset_power_symbol_state()

    # Calculate root sheet transform.
    root_bbox = node.internal_bbox()
    sheet_tx, paper = _calc_sheet_tx(root_bbox)

    elements = []

    # Recurse into children — they write their own files if unflattened.
    for child in node.children.values():
        elements.extend(node_to_sexp_schematic(child, sheet_tx, version=version))

    # Collect lib_symbols for ALL parts in the circuit.
    lib_symbols = {}
    for part in circuit.parts:
        if not isinstance(part, NetTerminal):
            lib_id = f"{part.lib.filename}:{part.name}"
            if lib_id not in lib_symbols:
                lib_symbols[lib_id] = part

    # Generate part S-expressions for root-level parts.
    for part in node.parts:
        if isinstance(part, NetTerminal):
            label = net_label_to_sexp(part.pins[0], tx=sheet_tx, force=True)
            if label:
                elements.append(label)
        else:
            elements.append(part_to_sexp(part, tx=sheet_tx))

    # Generate wire S-expressions (split at junction points).
    for net, wire in node.wires.items():
        net_junctions = node.junctions.get(net, [])
        elements.extend(wire_to_sexp(net, wire, tx=sheet_tx, junctions=net_junctions))

    # Generate junction S-expressions.
    for net, junctions in node.junctions.items():
        elements.extend(junction_to_sexp(net, junctions, tx=sheet_tx))

    # Generate net labels for stubbed pins.
    for part in node.parts:
        if isinstance(part, NetTerminal):
            continue
        for pin in part:
            label = net_label_to_sexp(pin, tx=sheet_tx)
            if label:
                elements.append(label)

    # Build lib_symbols section.
    lib_symbols_sexp = Sexp(["lib_symbols"])
    for lib_id, part in lib_symbols.items():
        lib_symbols_sexp.append(Sexp(part_to_lib_symbol_definition(part)))

    # Add power lib_symbols for any power symbols used in this schematic.
    for pwr_name in sorted(_used_power_symbols):
        pwr_lib_id = f"power:{pwr_name}"
        if pwr_lib_id not in lib_symbols:
            pwr_sexp = _extract_power_lib_symbol(pwr_name)
            if pwr_sexp:
                lib_symbols_sexp.append(pwr_sexp)

    root_uuid = _gen_uuid("root_schematic")

    schematic = Sexp(
        [
            "kicad_sch",
            ["version", version],
            ["generator", "skidl"],
            ["generator_version", __version__],
            ["uuid", root_uuid],
            ["paper", paper],
        ]
    )
    schematic.append(Sexp(create_title_block_sexp(title)))
    schematic.append(lib_symbols_sexp)

    for elem in elements:
        schematic.append(elem)

    # Write root schematic.
    output_file = os.path.join(filepath, f"{top_name}.kicad_sch")
    os.makedirs(filepath, exist_ok=True)
    _write_sexp_schematic(schematic, output_file)

    # Optional: validate with kicad-cli if available.
    _validate_with_kicad_cli(output_file)

    return output_file


# ---------------------------------------------------------------------------
# Optional KiCad CLI validation
# ---------------------------------------------------------------------------


def _validate_with_kicad_cli(filepath):
    """Run kicad-cli ERC on generated schematic if available."""
    import shutil
    import subprocess

    kicad_cli = shutil.which("kicad-cli")
    if not kicad_cli:
        return  # Silent skip if not installed.
    try:
        result = subprocess.run(
            [kicad_cli, "sch", "erc", "--exit-code-violations", filepath],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            from skidl.logger import active_logger

            active_logger.warning(
                f"KiCad ERC found issues in {filepath}:\n{result.stderr}"
            )
    except (subprocess.TimeoutExpired, OSError):
        pass  # Don't fail generation if CLI has issues.


# ---------------------------------------------------------------------------
# File writer
# ---------------------------------------------------------------------------


def _write_sexp_schematic(schematic, filepath):
    """Write an Sexp schematic object to a file with proper quoting.

    Args:
        schematic: Sexp object.
        filepath: Output file path.
    """

    def need_quote(x):
        tag = x[0]
        if tag == "symbol" and len(x) > 1 and isinstance(x[1], str):
            # Quote lib_symbol names like "Device:R", "power:GND", "R_0_1"
            return True
        return tag in (
            "title",
            "date",
            "company",
            "comment",
            "path",
            "project",
            "property",
            "name",
            "number",
            "lib_id",
            "reference",
            "label",
            "global_label",
            "hierarchical_label",
            "generator",
            "generator_version",
            "paper",
        )

    def need_quote_alternate(x):
        return x[0] == "alternate"

    schematic.add_quotes(need_quote)
    schematic.add_quotes(need_quote_alternate, stop_idx=2)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(schematic.to_str())
