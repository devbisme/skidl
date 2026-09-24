# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Generic, hierarchical netlist emitter for schematic generation.

SKiDL's job is to describe electrical interconnection. The *graphical* work of
turning that interconnection into a schematic (placement, routing, KiCad file
generation) is done by a separate tool. The bridge between the two is the
JSON document produced here by :func:`build_generic_netlist`.

The document is deliberately tool-neutral and easy to extend:

- Component symbol geometry is **embedded** (one definition per unique
  ``lib_id``), so the downstream tool needs no access to KiCad symbol
  libraries and the result is fully reproducible.
- Orientation/layout *hints* the downstream placer consumes are carried
  alongside the electrical data: per-component ``symtx`` (mirror/rotate) and
  per-net ``stub``/``netio``. New hints can be added as new keys without
  breaking readers.

Coordinates are emitted in native KiCad units (mm) and integer degrees; the
downstream tool performs the mm->mils and degrees->direction normalization
(the equivalent of ``preprocess_circuit`` in the current KiCad backends).
"""

import os.path

from skidl.utilities import export_to_all

__all__ = ["build_generic_netlist"]

# Schema identifier and version. Bump SCHEMA_VERSION on incompatible changes;
# additive hints do not require a bump.
SCHEMA_NAME = "skidl-generic-netlist"
SCHEMA_VERSION = 1


def _lib_name_of(part):
    """Return the library name (no extension/path) a part came from."""
    filename = getattr(getattr(part, "lib", None), "filename", "") or ""
    if filename:
        return os.path.splitext(os.path.basename(filename))[0]
    return "Device"


def _lib_id_of(part):
    """Return the ``lib:part`` identifier used to key embedded symbols."""
    return "{}:{}".format(_lib_name_of(part), part.name or "Unknown")


def _units_of(part):
    """Yield ``(unit_num, unit_obj)`` for a part.

    Mirrors ``preprocess_circuit.units``: a part with no explicit units is its
    own single unit. Multi-unit parts yield each sub-unit.
    """
    if not getattr(part, "unit", None):
        yield 1, part
    else:
        for unit in part.unit.values():
            yield getattr(unit, "num", 1), unit


def _jsonify(obj):
    """Convert Sexp/nested-list draw commands into plain JSON-safe lists.

    ``draw_cmds`` are ``simp_sexp.Sexp`` objects (a ``list`` subclass) holding
    strings and numbers. Recurse to strip the subclass so ``json`` accepts them
    and so the document does not depend on Sexp for reading.
    """
    if isinstance(obj, (list, tuple)):
        return [_jsonify(x) for x in obj]
    return obj


def _pin_geometry(pin):
    """Serialize the symbol-level geometry of a single pin."""
    return {
        "num": str(pin.num),
        "name": getattr(pin, "name", "") or "",
        "x": pin.x,
        "y": pin.y,
        # Native symbol orientation. May already be a direction string
        # ("R"/"U"/"L"/"D") after library parsing, or an integer angle.
        "orient": pin.orientation,
        "rotation": getattr(pin, "rotation", 0),
        "length": getattr(pin, "length", 0),
        "func": str(getattr(pin, "func", "")),
    }


def _symbol_def(part):
    """Build the embedded, reusable symbol definition for a part's ``lib_id``.

    Captures both the raw draw commands (needed to emit KiCad ``lib_symbols``)
    and per-unit pin geometry (needed by the placement/routing engine).
    """
    units = {}
    for unit_num, unit in _units_of(part):
        units[str(unit_num)] = {
            "pins": [_pin_geometry(p) for p in unit.pins],
        }

    draw_cmds = {}
    for unit_num, cmds in getattr(part, "draw_cmds", {}).items():
        draw_cmds[str(unit_num)] = _jsonify(cmds)

    return {
        "ref_prefix": getattr(part, "ref_prefix", "") or "U",
        "name": part.name or "Unknown",
        "lib": _lib_name_of(part),
        "description": getattr(part, "description", "") or "",
        "datasheet": getattr(part, "datasheet", "") or "",
        "draw_cmds": draw_cmds,
        "units": units,
    }


def _component(part):
    """Serialize one placeable component instance (electrical + hints)."""
    pins = []
    for unit_num, unit in _units_of(part):
        for pin in unit.pins:
            net = getattr(pin, "net", None)
            pins.append(
                {
                    "num": str(pin.num),
                    "unit": unit_num,
                    "net": net.name if net is not None else None,
                }
            )

    return {
        "ref": part.ref,
        "lib_id": _lib_id_of(part),
        "value": part.value_to_str(),
        "footprint": getattr(part, "footprint", "") or "",
        "hiertuple": list(part.hiertuple),
        # --- layout hints ---
        "symtx": getattr(part, "symtx", "") or "",
        "orientation_locked": bool(getattr(part, "orientation_locked", False)),
        "pins": pins,
    }


def _net(net, code):
    """Serialize one net: connectivity plus stub/io hints."""
    nodes = []
    for pin in sorted(net.pins, key=str):
        try:
            _, _, pin_type = pin.get_pin_info()
        except Exception:
            pin_type = ""
        nodes.append(
            {
                "ref": pin.part.ref,
                "pin": str(pin.num),
                "pintype": pin_type,
            }
        )

    return {
        "name": net.name,
        "code": code,
        # --- layout hints ---
        # ``stub`` is the effective value; ``stub_explicit`` records whether the
        # user set it (vs. an automatic heuristic the downstream tool may apply).
        "stub": bool(getattr(net, "stub", False)),
        "stub_explicit": bool(getattr(net, "_stub_explicit", False)),
        "netio": (getattr(net, "netio", "") or "").lower(),
        "implicit": bool(net.is_implicit()),
        "nodes": nodes,
    }


@export_to_all
def build_generic_netlist(circuit, title="", top_name=""):
    """Build a generic, hierarchical netlist document from a circuit.

    Args:
        circuit (Circuit): The circuit to serialize. It should already be
            merged (``merge_net_names``/``merge_nets``) as ``generate_schematic``
            does before calling this.
        title (str): Optional schematic title carried through to the tool.
        top_name (str): Optional top-of-hierarchy name for output filenames.

    Returns:
        dict: A JSON-serializable document with ``symbols``, ``components``,
        ``nets`` and ``sheets`` sections. The structure is stable and additive;
        readers should ignore unknown keys.
    """

    # Real parts only. NetTerminals are a placement-time construct created by
    # the downstream tool, so they never appear here.
    parts = [p for p in circuit.parts if getattr(p, "name", None) != "NT"]

    # Embedded symbol definitions, one per unique lib_id (deduplicated).
    symbols = {}
    for part in parts:
        lib_id = _lib_id_of(part)
        if lib_id not in symbols:
            symbols[lib_id] = _symbol_def(part)

    # Components, sorted by reference for deterministic output.
    components = [_component(p) for p in sorted(parts, key=lambda p: str(p.ref))]

    # Nets, sorted by name; assign sequential codes (matches gen_netlist).
    nets = []
    sorted_nets = sorted(circuit.get_nets(), key=lambda n: str(n.name))
    for code, net in enumerate(sorted_nets, 1):
        nets.append(_net(net, code))

    # Hierarchy sheet names (each is a hiertuple, e.g. ("", "stage1")).
    sheets = [list(name) for name in circuit.get_node_names()]

    return {
        "format": SCHEMA_NAME,
        "version": SCHEMA_VERSION,
        "title": title,
        "top_name": top_name,
        "sheets": sheets,
        "symbols": symbols,
        "components": components,
        "nets": nets,
    }
