# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Generate a KiCad 9 schematic from a Circuit object.

Thin wrapper around the shared sexp_schematic module.
Uses SKiDL's placement and routing infrastructure.
"""

import os
import re
import shutil
import subprocess
from collections import Counter, defaultdict

from skidl.geometry import BBox, Point, Tx, Vector
from skidl.schematics.net_terminal import NetTerminal
from skidl.scriptinfo import get_script_name
from skidl.utilities import export_to_all, rmv_attr

from .sexp_schematic import write_top_schematic
from .bboxes import calc_hier_label_bbox, calc_symbol_bbox


__all__ = []


def _setup_kicad_env():
    """Set KiCad footprint directory if not already set.

    Auto-detects the standard KiCad footprint directory so that
    generated schematics can reference footprints for PCB layout.
    """
    from skidl import get_default_tool

    kicad_version = get_default_tool()[len("kicad"):]
    if not os.environ.get(f"KICAD{kicad_version}_FOOTPRINT_DIR"):
        for path in [
            "/usr/share/kicad/footprints",
            "/usr/local/share/kicad/footprints",
            os.path.expanduser(f"~/.local/share/kicad/{kicad_version}.0/footprints"),
        ]:
            if os.path.isdir(path):
                os.environ[f"KICAD{kicad_version}_FOOTPRINT_DIR"] = path
                break


# Suppress legacy fp-lib-table warnings from older KiCad tool modules.
import warnings
warnings.filterwarnings("ignore", message=".*fp-lib-table.*")


# Pattern matching common power net names.
_POWER_NET_RE = re.compile(
    r"^(\+\d[\d.]*V[\d]*|GND|AGND|DGND|PGND|VCC|VDD|VSS|VEE|VBUS|VBAT|AVCC|AVDD|DVCC|DVDD)$",
    re.IGNORECASE,
)

# ERC error types that can be fixed by stubbing nets.
FIXABLE_ERROR_TYPES = frozenset(
    {"pin_not_connected", "pin_not_driven", "wire_not_connected"}
)


def auto_stub_nets(circuit, **options):
    """Auto-stub power nets and high-fanout nets before generation.

    Only modifies nets that haven't been explicitly set by the user.
    Called when auto_stub=True is passed to gen_schematic().

    Args:
        circuit: The Circuit object containing nets to analyze.
        options: Dict of options. Recognizes 'auto_stub_fanout' (default 5).
    """
    import sys

    fanout_threshold = options.get("auto_stub_fanout", 5)
    stubbed_power = []
    stubbed_fanout = []

    for net in circuit.nets:
        if getattr(net, "_stub_explicit", False):
            continue
        if not net.valid or len(net.pins) == 0:
            continue

        # Power nets: anything starting with "+" or matching common power names.
        if net.name.startswith("+") or _POWER_NET_RE.match(net.name):
            net._stub = True
            net._stub_explicit = False
            for pin in net.get_pins():
                pin.stub = True
            stubbed_power.append(f"{net.name}({len(net.pins)})")
            continue

        # High fanout nets: many pins connected to the same net.
        if len(net.pins) >= fanout_threshold:
            net._stub = True
            net._stub_explicit = False
            for pin in net.get_pins():
                pin.stub = True
            stubbed_fanout.append(f"{net.name}({len(net.pins)})")

    from skidl.logger import active_logger
    active_logger.info(
        f"  [auto_stub] power: {', '.join(stubbed_power[:10])}{'...' if len(stubbed_power) > 10 else ''}"
    )
    active_logger.info(
        f"  [auto_stub] fanout>={fanout_threshold}: {', '.join(stubbed_fanout[:10])}{'...' if len(stubbed_fanout) > 10 else ''}"
    )


def _run_erc(schematic_path):
    """Run kicad-cli ERC on a schematic file and return the report path.

    Args:
        schematic_path: Path to the .kicad_sch file.

    Returns:
        str: Path to the ERC report file, or None if kicad-cli is unavailable.
    """
    report_path = schematic_path.replace(".kicad_sch", "-erc.rpt")
    try:
        subprocess.run(
            [
                "kicad-cli",
                "sch",
                "erc",
                "--output",
                report_path,
                "--severity-all",
                schematic_path,
            ],
            capture_output=True,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return report_path if os.path.exists(report_path) else None


def _parse_erc_report(report_path):
    """Parse kicad-cli ERC report and return list of (error_type, symbol_ref, pin_num).

    The ERC report format has lines like:
        [pin_not_connected]: Pin not connected ...
        @(x,y): Symbol U1 Pin 3 ...

    Args:
        report_path: Path to the ERC .rpt file.

    Returns:
        list: List of (error_type, symbol_ref, pin_num) tuples.
    """
    if not report_path or not os.path.exists(report_path):
        return []

    errors = []
    current_error_type = None

    # Patterns for ERC report parsing.
    error_type_re = re.compile(r"^\[(\w+)\]")
    symbol_pin_re = re.compile(r"Symbol\s+(\S+)\s+Pin\s+(\S+)")

    with open(report_path, "r") as f:
        for line in f:
            line = line.strip()

            # Match error type header.
            m = error_type_re.match(line)
            if m:
                current_error_type = m.group(1)
                continue

            # Match symbol/pin reference in the detail line.
            if current_error_type:
                m = symbol_pin_re.search(line)
                if m:
                    errors.append((current_error_type, m.group(1), m.group(2)))
                    current_error_type = None

    return errors


def _stub_nets_for_erc_errors(circuit, errors):
    """Convert nets involved in ERC errors to stubs for regeneration.

    Args:
        circuit: The Circuit object.
        errors: List of (error_type, symbol_ref, pin_num) from _parse_erc_report.

    Returns:
        bool: True if any nets were newly stubbed.
    """
    stubbed_any = False
    for error_type, symbol_ref, pin_num in errors:
        if error_type not in FIXABLE_ERROR_TYPES:
            continue
        for part in circuit.parts:
            if part.ref == symbol_ref:
                for pin in part.pins:
                    if str(pin.num) == str(pin_num):
                        net = pin.net
                        if net and not getattr(net, "_stub_explicit", False):
                            net._stub = True
                            net._stub_explicit = False
                            for p in net.get_pins():
                                p.stub = True
                            stubbed_any = True
                break
    return stubbed_any


def _classify_and_stub_complex_nets(circuit, node, **options):
    """Classify nets after placement: stub complex ones, keep simple ones as wires.

    Called after placement succeeds, before routing. Nets with too many pins
    or pins too far apart get converted to labels for reliable connectivity.
    Simple 2-3 pin short-distance nets remain as wires.

    Args:
        circuit: The Circuit object.
        node: The placed SchNode.
        options: Dict of options including:
            auto_stub_max_wire_pins (int): Max pins for wire routing. Default 3.
            auto_stub_max_wire_dist (int): Max manhattan distance (mils) for wires. Default 2000.
    """
    from skidl.geometry import Point

    max_wire_pins = options.get("auto_stub_max_wire_pins", 3)
    max_wire_dist = options.get("auto_stub_max_wire_dist", 2000)

    node_parts = set(node.parts)
    stubbed_count = 0

    for net in node.get_internal_nets():
        if getattr(net, "_stub_explicit", False):
            continue
        if getattr(net, "_stub", False):
            continue

        pins = [p for p in net.pins if p.part in node_parts]

        # Too many pins → label.
        if len(pins) > max_wire_pins:
            net._stub = True
            net._stub_explicit = False
            for p in net.get_pins():
                p.stub = True
            stubbed_count += 1
            continue

        # Pins too far apart → label.
        if len(pins) >= 2:
            pts = []
            for p in pins:
                pin_pt = getattr(p, "place_pt", getattr(p, "pt", Point(p.x, p.y)))
                part_tx = getattr(p.part, "tx", None)
                if part_tx:
                    pts.append(pin_pt * part_tx)
                else:
                    pts.append(pin_pt)

            max_dist = 0
            for i, a in enumerate(pts):
                for b in pts[i + 1:]:
                    dist = abs(a.x - b.x) + abs(a.y - b.y)
                    if dist > max_dist:
                        max_dist = dist

            if max_dist > max_wire_dist:
                net._stub = True
                net._stub_explicit = False
                for p in net.get_pins():
                    p.stub = True
                stubbed_count += 1

    if stubbed_count:
        from skidl.logger import active_logger
        active_logger.info(
            f"  [selective_routing] Stubbed {stubbed_count} complex nets after placement"
        )


class LabelsOnlyWarning(UserWarning):
    """Warning raised when schematic falls back to labels-only output."""

    pass


def _handle_fallback(circuit, tool_module, filepath, top_name, title, flatness,
                     options, logger, reason=""):
    """Handle routing failure fallback according to the auto_stub_fallback policy.

    Args:
        circuit: The Circuit object.
        tool_module: The KiCad tool module.
        filepath, top_name, title, flatness: Schematic generation parameters.
        options: Dict of options including auto_stub_fallback policy.
        logger: The active logger.
        reason: Human-readable explanation of why we're falling back.
    """
    import warnings

    from skidl.schematics.sch_node import SchNode
    from skidl.tools.kicad9.sexp_schematic import write_top_schematic

    fallback = options.get("auto_stub_fallback", "labels")

    if fallback == "raise":
        finalize_parts_and_nets(circuit, **options)
        from skidl.schematics.route import RoutingFailure

        raise RoutingFailure(
            f"{reason}. Set auto_stub_fallback='labels' to produce "
            "labels-only output instead of crashing."
        )

    from skidl.schematics.place import PlacementFailure
    from skidl.schematics.route import RoutingFailure

    # Place with real connectivity so connected parts group together,
    # then stub for routing. This gives connectivity-aware placement
    # with labels-only routing (which always succeeds).
    placed = False
    for expansion in [1.5, 2.25, 3.0]:
        try:
            preprocess_circuit(circuit, **options)
            node = SchNode(circuit, tool_module, filepath, top_name, title, flatness)
            node.place(expansion_factor=expansion, **options)
            placed = True
            break
        except PlacementFailure:
            finalize_parts_and_nets(circuit, **options)
            logger.info(
                f"  [graceful_fallback] Connectivity-aware placement failed "
                f"at {expansion}x, trying wider"
            )

    if not placed:
        # Last resort: stub everything, place without connectivity.
        _stub_all_non_explicit(circuit)
        preprocess_circuit(circuit, **options)
        node = SchNode(circuit, tool_module, filepath, top_name, title, flatness)
        node.place(expansion_factor=1.5, **options)

    _snap_two_pin_parts(node)

    # Stub all remaining nets so routing is trivial (labels only).
    stubbed_nets = []
    for net in circuit.nets:
        if not getattr(net, "_stub_explicit", False) and not net._stub:
            stubbed_nets.append(net.name)
            net._stub = True
            for pin in net.get_pins():
                pin.stub = True

    node.route(**options)
    output_file = write_top_schematic(
        circuit, node, filepath, top_name, title, version=20230409
    )
    finalize_parts_and_nets(circuit, **options)

    msg = (
        f"{reason}. Produced schematic at {output_file} with "
        f"connectivity-aware placement. "
        f"{len(stubbed_nets)} nets as labels, close 2-pin nets wired directly."
    )
    logger.info(msg)

    if fallback == "warn":
        warnings.warn(msg, LabelsOnlyWarning, stacklevel=4)


def _is_two_pin_part(part):
    """Return True if part is a simple 2-pin component (LED, R, C, etc.)."""
    return not isinstance(part, NetTerminal) and len(part.pins) == 2


def _is_power_net(net):
    """Return True if net is a power rail (GND, VCC, +3.3V, etc.)."""
    name = getattr(net, 'name', '')
    return name.startswith("+") or bool(_POWER_NET_RE.match(name))


def _pin_world_orient(pin, part):
    """Get the world-space outward direction from a pin after part rotation.

    Transforms the pin's stub direction vector through the part's full
    transform (including mirrors/flips), then returns the opposite direction.
    """
    orient_to_vec = {"R": (1, 0), "L": (-1, 0), "U": (0, -1), "D": (0, 1)}
    outward = {"L": "R", "R": "L", "U": "D", "D": "U"}

    raw_orient = getattr(pin, "orientation", "R")
    vx, vy = orient_to_vec.get(raw_orient, (1, 0))
    tx = part.tx
    wx = tx.a * vx + tx.b * vy
    wy = tx.c * vx + tx.d * vy
    if abs(wx) >= abs(wy):
        world_orient = "R" if wx > 0 else "L"
    else:
        world_orient = "D" if wy > 0 else "U"
    return outward.get(world_orient, "R")


def _compute_snap_tx(my_pin, other_pin, target_world, extend_dir):
    """Compute the transform to snap a 2-pin part onto a target pin position.

    Orients the part so `other_pin` extends in `extend_dir` from the target,
    and places `my_pin` exactly at `target_world`.

    Returns:
        Tx: The new transform for the 2-pin part.
    """
    dx_local = other_pin.pt.x - my_pin.pt.x
    dy_local = other_pin.pt.y - my_pin.pt.y

    if extend_dir == "R":
        if abs(dx_local) >= abs(dy_local):
            symtx = "" if dx_local > 0 else "H"
        else:
            symtx = "R" if dy_local > 0 else "L"
    elif extend_dir == "L":
        if abs(dx_local) >= abs(dy_local):
            symtx = "" if dx_local < 0 else "H"
        else:
            symtx = "L" if dy_local > 0 else "R"
    elif extend_dir == "U":
        if abs(dy_local) >= abs(dx_local):
            symtx = "" if dy_local > 0 else "V"
        else:
            symtx = "L" if dx_local > 0 else "R"
    elif extend_dir == "D":
        if abs(dy_local) >= abs(dx_local):
            symtx = "" if dy_local < 0 else "V"
        else:
            symtx = "R" if dx_local > 0 else "L"
    else:
        symtx = ""

    new_tx = Tx.from_symtx(symtx)
    my_pin_placed = my_pin.pt * new_tx
    offset = Point(
        target_world.x - my_pin_placed.x,
        target_world.y - my_pin_placed.y,
    )
    return new_tx.move(offset)


def _snap_two_pin_parts(node):
    """Snap 2-pin parts onto their connected IC or already-snapped part pins.

    Pass 1: Snap onto IC pins (parts with >2 pins). Each IC pin only accepts
    one snapped part; extras keep their labels.

    Pass 2+: Iteratively snap remaining 2-pin parts onto the free pins of
    already-snapped 2-pin parts, building chains (e.g. IC ← R ← LED).

    Pass 3: Stack remaining 2-pin parts onto already-occupied IC pins,
    extending perpendicular to the first snapped part. Handles nets shared
    between multiple 2-pin parts (e.g. switch + pull-down on the same IC input).

    Recurses into child nodes first.
    """
    for child in node.children.values():
        _snap_two_pin_parts(child)

    node_part_ids = {id(p) for p in node.parts}
    snapped = set()
    occupied_pins = set()

    for part in list(node.parts):
        if not _is_two_pin_part(part):
            continue

        p1, p2 = part.pins[0], part.pins[1]
        net1 = getattr(p1, "net", None)
        net2 = getattr(p2, "net", None)
        if not net1 or not net2:
            continue

        target_pin = None
        target_part = None
        my_pin = None

        both_power = _is_power_net(net1) and _is_power_net(net2)
        min_target_pins = 8 if both_power else 2

        for my_p, other_net in [(p1, net1), (p2, net2)]:
            if _is_power_net(other_net) and not both_power:
                continue
            for net_pin in other_net.pins:
                other_part = net_pin.part
                if (
                    other_part is not part
                    and id(other_part) in node_part_ids
                    and not isinstance(other_part, NetTerminal)
                    and len(other_part.pins) > min_target_pins
                    and id(net_pin) not in occupied_pins
                ):
                    target_pin = net_pin
                    target_part = other_part
                    my_pin = my_p
                    break
            if target_pin:
                break

        if not target_pin:
            continue

        target_world = target_pin.pt * target_part.tx
        extend_dir = _pin_world_orient(target_pin, target_part)
        other_pin = p2 if my_pin is p1 else p1

        part.tx = _compute_snap_tx(my_pin, other_pin, target_world, extend_dir)
        if both_power:
            _offset_dir = {"R": (200, 0), "L": (-200, 0), "U": (0, 200), "D": (0, -200)}
            dx, dy = _offset_dir.get(extend_dir, (200, 0))
            part.tx = part.tx.move(Point(dx, dy))
            # Emit a wire from the IC's power pin back to the now-offset cap +ve pin
            # so the connection is visually drawn rather than relying on two power
            # labels. Suppress the cap +ve pin's label since the wire makes it
            # redundant.
            cap_pin_world = my_pin.pt * part.tx
            power_cap_wires = getattr(node, "_power_cap_wires", [])
            power_cap_wires.append(
                (target_world.x, target_world.y, cap_pin_world.x, cap_pin_world.y)
            )
            node._power_cap_wires = power_cap_wires
            power_cap_suppressed = getattr(node, "_power_cap_suppressed_pins", set())
            power_cap_suppressed.add(id(my_pin))
            node._power_cap_suppressed_pins = power_cap_suppressed
        snapped.add(id(part))
        occupied_pins.add(id(target_pin))

    for _iteration in range(5):
        newly_snapped = set()

        for part in list(node.parts):
            if id(part) in snapped or not _is_two_pin_part(part):
                continue

            p1, p2 = part.pins[0], part.pins[1]
            net1 = getattr(p1, "net", None)
            net2 = getattr(p2, "net", None)
            if not net1 or not net2:
                continue

            target_pin = None
            target_part = None
            my_pin = None

            both_power = _is_power_net(net1) and _is_power_net(net2)

            for my_p, other_net in [(p1, net1), (p2, net2)]:
                if _is_power_net(other_net) and not both_power:
                    continue
                for net_pin in other_net.pins:
                    other_part = net_pin.part
                    if (
                        other_part is not part
                        and id(other_part) in snapped
                        and id(net_pin) not in occupied_pins
                    ):
                        target_pin = net_pin
                        target_part = other_part
                        my_pin = my_p
                        break
                if target_pin:
                    break

            if not target_pin:
                continue

            target_world = target_pin.pt * target_part.tx
            extend_dir = _pin_world_orient(target_pin, target_part)
            other_pin = p2 if my_pin is p1 else p1

            part.tx = _compute_snap_tx(my_pin, other_pin, target_world, extend_dir)
            newly_snapped.add(id(part))
            occupied_pins.add(id(target_pin))

        if not newly_snapped:
            break
        snapped |= newly_snapped

    perp_map = {"R": "D", "L": "U", "U": "R", "D": "L"}
    for part in list(node.parts):
        if id(part) in snapped or not _is_two_pin_part(part):
            continue

        p1, p2 = part.pins[0], part.pins[1]
        net1 = getattr(p1, "net", None)
        net2 = getattr(p2, "net", None)
        if not net1 or not net2:
            continue

        target_pin = None
        target_part = None
        my_pin = None

        for my_p, other_net in [(p1, net1), (p2, net2)]:
            for net_pin in other_net.pins:
                other_part = net_pin.part
                if (
                    other_part is not part
                    and id(other_part) in node_part_ids
                    and not isinstance(other_part, NetTerminal)
                    and len(other_part.pins) > 2
                    and id(net_pin) in occupied_pins
                ):
                    target_pin = net_pin
                    target_part = other_part
                    my_pin = my_p
                    break
            if target_pin:
                break

        if not target_pin:
            continue

        target_world = target_pin.pt * target_part.tx
        ic_dir = _pin_world_orient(target_pin, target_part)
        extend_dir = perp_map.get(ic_dir, ic_dir)
        other_pin = p2 if my_pin is p1 else p1

        part.tx = _compute_snap_tx(my_pin, other_pin, target_world, extend_dir)
        snapped.add(id(part))

    _stagger_tjunctions(node, node_part_ids, snapped, occupied_pins)


def _stagger_tjunctions(node, node_part_ids, snapped, occupied_pins, min_group=2):
    """Detect repeating T-junction patterns and stagger parts outward from IC.

    Phase 1: identify stagger groups, compute how much space each needs,
    and shift ICs apart vertically so fans won't overlap.
    Phase 2: place the staggered parts at the (now separated) IC positions.
    """
    perp_map = {"R": "D", "L": "U", "U": "R", "D": "L"}
    anti_perp = {"U": "D", "D": "U", "L": "R", "R": "L"}
    _dir_vec = {"R": (1, 0), "L": (-1, 0), "U": (0, -1), "D": (0, 1)}

    ic_pin_to_parts = defaultdict(list)

    for part in node.parts:
        if not _is_two_pin_part(part):
            continue

        p1, p2 = part.pins[0], part.pins[1]
        net1 = getattr(p1, "net", None)
        net2 = getattr(p2, "net", None)
        if not net1 or not net2:
            continue

        for my_p, other_net in [(p1, net1), (p2, net2)]:
            if _is_power_net(other_net):
                continue
            for net_pin in other_net.pins:
                ic = net_pin.part
                if (
                    ic is not part
                    and id(ic) in node_part_ids
                    and not isinstance(ic, NetTerminal)
                    and len(ic.pins) > 2
                    and id(net_pin) in occupied_pins
                ):
                    other_pin = p2 if my_p is p1 else p1
                    ic_pin_to_parts[id(net_pin)].append(
                        (part, my_p, other_pin, net_pin, ic)
                    )
                    break
            else:
                continue
            break

    ic_groups = defaultdict(list)
    for ic_pin_id, parts_list in ic_pin_to_parts.items():
        if not parts_list:
            continue
        ic = parts_list[0][4]
        ic_groups[id(ic)].append((parts_list[0][3], parts_list))

    # ── Phase 1: identify qualifying groups and pre-shift ICs ─────────
    MM_TO_MILS = 1 / 0.0254
    stagger_plans = []

    for ic_id, pin_entries in ic_groups.items():
        fanout_counts = [len(pl) for _, pl in pin_entries]
        dominant = max(set(fanout_counts), key=fanout_counts.count)
        if dominant < 2:
            continue
        matching = [(ip, pl) for ip, pl in pin_entries if len(pl) == dominant]

        if len(matching) < min_group:
            continue

        ic_part = matching[0][1][0][4]
        ic_dir = _pin_world_orient(matching[0][0], ic_part)
        step_dx, step_dy = _dir_vec.get(ic_dir, (1, 0))

        max_span = 0
        for _, parts_list_scan in matching:
            for (scan_part, _, _, _, _) in parts_list_scan:
                pts = [getattr(p, "pt", Point(p.x * MM_TO_MILS, p.y * MM_TO_MILS)) for p in scan_part.pins]
                if pts:
                    span = max(
                        max(p.x for p in pts) - min(p.x for p in pts),
                        max(p.y for p in pts) - min(p.y for p in pts),
                    )
                    max_span = max(max_span, span)
        step_size = max(100, int(max_span) + 50)

        n_pins = len(matching)
        stagger_extent = step_size * n_pins + max_span

        stagger_plans.append({
            "ic_part": ic_part,
            "matching": matching,
            "ic_dir": ic_dir,
            "step_dx": step_dx,
            "step_dy": step_dy,
            "step_size": step_size,
            "stagger_extent": stagger_extent,
            "dominant": dominant,
        })

    if len(stagger_plans) > 1:
        _pre_shift_ics(stagger_plans, node, snapped)

    # ── Phase 2: place staggered parts at final IC positions ──────────
    junction_wires = getattr(node, "_tjunction_wires", [])
    suppressed_pins = set()

    for plan in stagger_plans:
        ic_part = plan["ic_part"]
        matching = plan["matching"]
        ic_dir = plan["ic_dir"]
        step_dx = plan["step_dx"]
        step_dy = plan["step_dy"]
        step_size = plan["step_size"]
        perp_dir = perp_map.get(ic_dir, ic_dir)

        def _pin_sort_key(entry, _ic_part=ic_part, _ic_dir=ic_dir):
            ic_pin = entry[0]
            w = ic_pin.pt * _ic_part.tx
            if _ic_dir in ("L", "R"):
                return w.y
            return w.x

        matching.sort(key=_pin_sort_key)

        parts_per_pin = plan["dominant"]
        anti = anti_perp.get(perp_dir, perp_dir)
        extend_dirs = [perp_dir, anti] if parts_per_pin >= 2 else [perp_dir]

        for pin_idx, (ic_pin, parts_list) in enumerate(matching):
            ic_pin_world = ic_pin.pt * ic_part.tx

            parts_list.sort(key=lambda t: getattr(t[0], "ref", ""))

            offset_n = pin_idx + 1
            ox = ic_pin_world.x + step_dx * step_size * offset_n
            oy = ic_pin_world.y + step_dy * step_size * offset_n
            junction_pt = Point(ox, oy)

            for part_idx, (part, my_pin, other_pin, _, _) in enumerate(parts_list):
                ext_dir = extend_dirs[part_idx % len(extend_dirs)]
                part.tx = _compute_snap_tx(
                    my_pin, other_pin, junction_pt, ext_dir
                )
                snapped.add(id(part))
                suppressed_pins.add(id(my_pin))
            junction_wires.append(
                (ic_pin_world.x, ic_pin_world.y, ox, oy)
            )

    node._tjunction_wires = junction_wires
    node._tjunction_suppressed_pins = suppressed_pins


def _pre_shift_ics(plans, node, snapped):
    """Shift ICs vertically BEFORE stagger placement so fans won't overlap.

    Collects all parts already snapped to each IC and moves them together.
    The stagger parts haven't been placed yet, so they'll naturally land
    at the shifted IC positions in phase 2.
    """
    for plan in plans:
        ic = plan["ic_part"]
        ic_deps = set()
        ic_id = id(ic)

        for part in node.parts:
            if id(part) == ic_id or id(part) not in snapped:
                continue
            if not _is_two_pin_part(part):
                continue
            for pin in part.pins:
                net = getattr(pin, "net", None)
                if not net:
                    continue
                for net_pin in net.pins:
                    if net_pin.part is ic:
                        ic_deps.add(id(part))
                        break
                if id(part) in ic_deps:
                    break

        plan["_deps"] = [p for p in node.parts if id(p) in ic_deps]

    def _ic_bbox(plan):
        ic = plan["ic_part"]
        all_parts = [ic] + plan["_deps"]
        min_y = float("inf")
        max_y = float("-inf")
        for part in all_parts:
            for pin in part.pins:
                w = pin.pt * part.tx
                min_y = min(min_y, w.y)
                max_y = max(max_y, w.y)
        return min_y, max_y

    plans.sort(key=lambda p: _ic_bbox(p)[0])

    margin = 200
    prev_max_y = None

    for plan in plans:
        ic_min_y, ic_max_y = _ic_bbox(plan)
        needed_height = plan["stagger_extent"]
        group_max_y = max(ic_max_y, ic_min_y + needed_height)

        if prev_max_y is not None and ic_min_y < prev_max_y + margin:
            shift = (prev_max_y + margin) - ic_min_y
            vec = Point(0, shift)
            shifted = set()
            for part in [plan["ic_part"]] + plan["_deps"]:
                if id(part) not in shifted:
                    part.tx = part.tx.move(vec)
                    shifted.add(id(part))
            ic_min_y += shift
            group_max_y += shift

        prev_max_y = group_max_y


def _stub_all_non_explicit(circuit):
    """Stub all nets that weren't explicitly set by the user (labels-only fallback).

    Args:
        circuit: The Circuit object.
    """
    for net in circuit.nets:
        if not getattr(net, "_stub_explicit", False):
            net._stub = True
            for pin in net.get_pins():
                pin.stub = True


def preprocess_circuit(circuit, **options):
    """Add stuff to parts & nets for doing placement and routing of schematics."""

    def units(part):
        if len(part.unit) == 0:
            return [part]
        else:
            return part.unit.values()

    def initialize(part):
        """Initialize part or its part units."""

        pin_limit = options.get("orientation_pin_limit", 44)

        # KiCad 6+ stores pin orientation as integer degrees; normalize to string.
        deg_to_orient = {0: "R", 90: "U", 180: "L", 270: "D"}

        for part_unit in units(part):
            part_unit.tx = Tx.from_symtx(getattr(part_unit, "symtx", ""))

            num_pins = len(part_unit.pins)
            part_unit.orientation_locked = getattr(part_unit, "symtx", False) or not (
                1 < num_pins <= pin_limit
            )

            part_unit.grab_pins()

            for pin in part_unit:
                # Normalize pin orientation from integer degrees to string direction.
                if isinstance(pin.orientation, int):
                    pin.orientation = deg_to_orient.get(pin.orientation % 360, "R")
                # Pin coords from KiCad 9 libs are in mm; convert to mils
                # so the placement/routing engine works in consistent units.
                MM_TO_MILS = 1 / 0.0254
                pin.pt = Point(pin.x * MM_TO_MILS, pin.y * MM_TO_MILS)
                pin.routed = False

    def rotate_power_pins(part):
        """Rotate a part based on the direction of its power pins."""

        if not getattr(part, "symtx", ""):
            return

        def is_pwr(net_name):
            return net_name.startswith("+")

        def is_gnd(net_name):
            return "gnd" in net_name.lower()

        dont_rotate_pin_cnt = options.get("dont_rotate_pin_count", 10000)

        for part_unit in units(part):
            if len(part_unit) > dont_rotate_pin_cnt:
                return

            rotation_tally = Counter()
            for pin in part_unit:
                net_name = getattr(pin.net, "name", "").lower()
                if is_gnd(net_name):
                    if pin.orientation == "U":
                        rotation_tally[0] += 1
                    if pin.orientation == "D":
                        rotation_tally[180] += 1
                    if pin.orientation == "L":
                        rotation_tally[90] += 1
                    if pin.orientation == "R":
                        rotation_tally[270] += 1
                elif is_pwr(net_name):
                    if pin.orientation == "D":
                        rotation_tally[0] += 1
                    if pin.orientation == "U":
                        rotation_tally[180] += 1
                    if pin.orientation == "L":
                        rotation_tally[270] += 1
                    if pin.orientation == "R":
                        rotation_tally[90] += 1

            try:
                rotation = rotation_tally.most_common()[0][0]
            except IndexError:
                pass
            else:
                tx_cw_90 = Tx(a=0, b=-1, c=1, d=0)
                for _ in range(int(round(rotation / 90))):
                    part_unit.tx = part_unit.tx * tx_cw_90

    def calc_part_bbox(part):
        """Calculate the labeled bounding boxes and store it in the part."""

        bare_bboxes = calc_symbol_bbox(part)[1:]

        for part_unit, bare_bbox in zip(units(part), bare_bboxes):
            resize_wh = Vector(0, 0)
            if bare_bbox.w < 100:
                resize_wh.x = (100 - bare_bbox.w) / 2
            if bare_bbox.h < 100:
                resize_wh.y = (100 - bare_bbox.h) / 2
            bare_bbox = bare_bbox.resize(resize_wh)

            part_unit.lbl_bbox = BBox()
            part_unit.lbl_bbox.add(bare_bbox)
            for pin in part_unit:
                if pin.stub:
                    hlbl_bbox = calc_hier_label_bbox(pin.net.name, pin.orientation)
                    hlbl_bbox *= Tx().move(pin.pt)
                    part_unit.lbl_bbox.add(hlbl_bbox)

            part_unit.bbox = part_unit.lbl_bbox

    for part in circuit.parts:
        initialize(part)
        rotate_power_pins(part)
        calc_part_bbox(part)


def finalize_parts_and_nets(circuit, **options):
    """Restore parts and nets after place & route is done."""

    net_terminals = (p for p in circuit.parts if isinstance(p, NetTerminal))
    circuit.rmv_parts(*net_terminals)

    for part in circuit.parts:
        part.grab_pins()

    rmv_attr(circuit.parts, ("force", "bbox", "lbl_bbox", "tx"))


@export_to_all
def gen_schematic(
    circuit,
    filepath=".",
    top_name=get_script_name(),
    title="SKiDL-Generated Schematic",
    flatness=0.0,
    retries=2,
    **options,
):
    """Create a KiCad 9 schematic file from a Circuit object.

    Args:
        circuit (Circuit): The Circuit object that will have a schematic generated for it.
        filepath (str, optional): The directory where the schematic files are placed. Defaults to ".".
        top_name (str, optional): The name for the top of the circuit hierarchy. Defaults to get_script_name().
        title (str, optional): The title of the schematic. Defaults to "SKiDL-Generated Schematic".
        flatness (float, optional): Determines how much the hierarchy is flattened in the schematic.
            Defaults to 0.0 (completely hierarchical). Use 1.0 to flatten everything into one sheet.
        retries (int, optional): Number of times to re-try if routing fails. Defaults to 2.
        options (dict, optional): Dict of options and values, usually for drawing/debugging.

    Auto-stub options (pass as keyword arguments):
        auto_stub (bool): Enable auto-stubbing for large/complex circuits. Converts nets that
            would fail routing into global labels, and runs a KiCad ERC correction loop to
            iteratively fix remaining issues. Power nets (GND, VCC, etc.) are automatically
            emitted as proper KiCad power symbols. Default False.
        auto_stub_fanout (int): Nets with more pins than this are stubbed pre-routing. Default 3.
        auto_stub_max_wire_pins (int): Max pins on a net before selective routing stubs it
            post-placement. Default 3.
        auto_stub_max_wire_dist (int): Max manhattan distance (mils) between pins before
            selective routing stubs the net. Default 2000.
        erc_max_iterations (int): Max ERC correction loop passes. Default 8.
        auto_stub_fallback (str): What to do when routing fails with auto_stub enabled.
            "labels" (default) — fall back to labels-only schematic.
            "raise" — raise the RoutingFailure so the caller sees it.
            "warn" — produce labels-only but also raise a warning exception.

    Tips for best results with auto_stub:
        - Use @subcircuit to group related parts (e.g. power supply, MCU, amplifier).
          Each subcircuit gets placed and routed independently, producing more wired
          connections and cleaner hierarchical sheets.
        - Keep subcircuits to 5-15 parts for best wire routing results.
        - Power nets are automatically detected and emitted as KiCad power symbols
          (e.g. power:GND, power:VCC) which display correctly in the schematic editor.

    Example::

        from skidl import *

        @subcircuit
        def power_supply(vin, vout, gnd):
            ldo = Part("Regulator_Linear", "AP2112K-3.3")
            ldo["VIN"] += vin
            ldo["VOUT"] += vout
            ldo["GND"] += gnd
            ldo["EN"] += vin
            for val in ["1uF", "1uF"]:
                c = Part("Device", "C", value=val)
                c[1] += vout if val == "1uF" else vin
                c[2] += gnd

        vcc = Net("VCC"); vcc.drive = POWER
        gnd = Net("GND"); gnd.drive = POWER
        vin = Net("VIN")

        power_supply(vin, vcc, gnd)

        generate_schematic(auto_stub=True)
    """

    from skidl import get_default_tool
    from skidl.logger import active_logger
    from skidl.schematics.place import PlacementFailure
    from skidl.schematics.route import RoutingFailure
    from skidl.schematics.sch_node import SchNode
    from skidl.tools import tool_modules

    tool_module = tool_modules[get_default_tool()]

    _setup_kicad_env()

    # Part placement options that should always be turned on.
    options["use_push_pull"] = True
    options["rotate_parts"] = True
    options["pt_to_pt_mult"] = 5
    options["pin_normalize"] = True

    # Phase 1: Heuristic auto-stubbing before first generation pass.
    if options.get("auto_stub", False):
        auto_stub_nets(circuit, **options)

    expansion_factor = 1.0
    failure_type = None

    for attempt in range(retries):
        preprocess_circuit(circuit, **options)

        node = SchNode(
            circuit, tool_module, filepath, top_name, title, flatness
        )

        try:
            node.place(expansion_factor=expansion_factor, **options)
            if options.get("auto_stub", False):
                _classify_and_stub_complex_nets(circuit, node, **options)
            node.route(**options)

        except PlacementFailure as e:
            finalize_parts_and_nets(circuit, **options)
            failure_type = e
            active_logger.warning(
                f"Placement failed on attempt {attempt + 1}/{retries}: {e}"
            )
            continue

        except RoutingFailure as e:
            finalize_parts_and_nets(circuit, **options)
            expansion_factor *= 1.5
            failure_type = e
            active_logger.warning(
                f"Routing failed on attempt {attempt + 1}/{retries}, expanding area by 1.5x: {e}"
            )
            continue

        # Generate S-expression schematic using shared module.
        # KiCad 8/9 use version 20230409.
        output_file = write_top_schematic(
            circuit, node, filepath, top_name, title, version=20230409
        )

        active_logger.info(f"Schematic written to {output_file}")

        finalize_parts_and_nets(circuit, **options)

        # Phase 2: ERC correction loop (only when auto_stub is enabled).
        if options.get("auto_stub", False) and shutil.which("kicad-cli"):
            max_erc_iterations = options.get("erc_max_iterations", 3)
            for erc_attempt in range(max_erc_iterations):
                erc_report = _run_erc(output_file)
                errors = _parse_erc_report(erc_report)
                fixable = [e for e in errors if e[0] in FIXABLE_ERROR_TYPES]

                if not fixable:
                    active_logger.info(
                        f"ERC clean after {erc_attempt + 1} iteration(s)"
                    )
                    break

                if not _stub_nets_for_erc_errors(circuit, fixable):
                    active_logger.info(
                        f"ERC: {len(fixable)} unfixable errors remain after {erc_attempt + 1} iteration(s)"
                    )
                    break

                active_logger.info(
                    f"ERC correction: stubbed nets for {len(fixable)} errors, regenerating (iteration {erc_attempt + 1})"
                )

                # Full regeneration — try with expansion before giving up.
                erc_regen_ok = False
                for erc_expansion in [1.0, 1.5, 2.25]:
                    try:
                        preprocess_circuit(circuit, **options)
                        node = SchNode(
                            circuit,
                            tool_module,
                            filepath,
                            top_name,
                            title,
                            flatness,
                        )
                        node.place(expansion_factor=erc_expansion, **options)
                        if options.get("auto_stub", False):
                            _classify_and_stub_complex_nets(circuit, node, **options)
                        node.route(**options)
                        output_file = write_top_schematic(
                            circuit, node, filepath, top_name, title, version=20230409
                        )
                        finalize_parts_and_nets(circuit, **options)
                        erc_regen_ok = True
                        break
                    except (RoutingFailure, PlacementFailure) as inner_e:
                        finalize_parts_and_nets(circuit, **options)
                        if erc_expansion < 2.25:
                            active_logger.info(
                                f"ERC regeneration routing failed at {erc_expansion}x, "
                                f"trying {erc_expansion * 1.5}x expansion"
                            )
                        else:
                            active_logger.warning(
                                f"ERC regeneration routing failed after all expansion attempts: {inner_e}"
                            )

                if not erc_regen_ok:
                    # Routing failed even with expansion — handle per fallback policy.
                    _handle_fallback(
                        circuit, tool_module, filepath, top_name,
                        title, flatness, options, active_logger,
                        reason=f"ERC correction regeneration failed after expansion attempts",
                    )
                    break

        return

    # All retries exhausted.
    if failure_type and options.get("auto_stub", False):
        _handle_fallback(
            circuit, tool_module, filepath, top_name,
            title, flatness, options, active_logger,
            reason=f"Routing failed after all {retries} retries",
        )
        return

    finalize_parts_and_nets(circuit, **options)

    if failure_type:
        raise failure_type
    else:
        raise RuntimeError("Schematic generation failed for unknown reasons")
