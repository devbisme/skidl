# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""Tool-agnostic schematic decision logic.

These functions decide *what* to draw — which overlapping-pin labels are
redundant, which co-linear power pins form a bus, where no-connect flags go,
how net labels deconflict from component bodies — and return ABSTRACT data
(sets of ``id(pin)``, lists of ``(x1, y1, x2, y2)`` segments in render-mm,
``LabelPlacement`` data). The concrete backend (``tools/kicad9``) measures
geometry and emits elements; this module never imports ``skidl.tools.*`` and
never constructs a tool-native element.

All coordinates here are **render-mm** as returned by
``backend.pin_render_pos`` — the single coordinate source of truth (see the
architecture doc, sections 2, 3, 6).
"""

from collections import defaultdict

from skidl.geometry import Point, Tx
from skidl.net import NCNet
from skidl.schematics.net_terminal import NetTerminal


def find_overlapping_pins(node, backend, sheet_tx, max_dist_mm=80.0):
    """Pins whose labels are redundant because snap made them coincide.

    Builds connected clusters of overlapping pins per net (distance < 0.01mm
    in RENDER space). Within each cluster only one label is needed for
    cross-sheet connectivity; the rest are suppressed. Returns a ``set`` of
    ``id(pin)`` to suppress.

    Relocated from the decision body of ``_find_wireable_nets`` (which emitted
    nothing). Uses ``backend.pin_render_pos`` / ``backend.is_power_net_name``
    instead of the module-level kicad helpers; the math is identical.
    """
    node_part_ids = {id(p) for p in node.parts}
    wired_pin_ids = set()

    seen_nets = set()
    for part in node.parts:
        if isinstance(part, NetTerminal):
            continue
        for pin in part:
            if not pin.stub or not pin.is_connected():
                continue
            net = pin.net
            if id(net) in seen_nets:
                continue
            seen_nets.add(id(net))

            is_power = backend.is_power_net_name(net.name)

            # For non-power nets, only consider stubbed pins (these get labels).
            # For power nets, consider ALL pins on this sheet.
            if is_power:
                pins_in_node = [
                    p
                    for p in net.pins
                    if id(p.part) in node_part_ids
                    and not isinstance(p.part, NetTerminal)
                ]
            else:
                pins_in_node = [
                    p
                    for p in net.pins
                    if id(p.part) in node_part_ids
                    and not isinstance(p.part, NetTerminal)
                    and p.stub
                ]
            if len(pins_in_node) < 2:
                continue

            positions = []
            for p in pins_in_node:
                x, y = backend.pin_render_pos(p, sheet_tx)
                positions.append((x, y, p))

            # Union-find to cluster overlapping pins (dist < 0.01mm).
            parent = list(range(len(positions)))

            def find(i):
                while parent[i] != i:
                    parent[i] = parent[parent[i]]
                    i = parent[i]
                return i

            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    dist = (
                        (positions[i][0] - positions[j][0]) ** 2
                        + (positions[i][1] - positions[j][1]) ** 2
                    ) ** 0.5
                    if dist < 0.01:
                        ri, rj = find(i), find(j)
                        if ri != rj:
                            parent[ri] = rj

            # Group pins by cluster.
            clusters = {}
            for i in range(len(positions)):
                r = find(i)
                clusters.setdefault(r, []).append(i)

            # Check if the net has pins outside this sheet.
            all_real_pins = [p for p in net.pins if not isinstance(p.part, NetTerminal)]
            has_pins_outside = len(all_real_pins) > len(pins_in_node)

            for members in clusters.values():
                if len(members) < 2:
                    continue

                pins_outside_cluster = len(pins_in_node) - len(members)

                if not has_pins_outside and pins_outside_cluster == 0:
                    # All net pins are in this cluster — fully connected by
                    # overlap, no labels needed at all.
                    for idx in members:
                        wired_pin_ids.add(id(positions[idx][2]))
                else:
                    # Net has pins elsewhere — keep one label for cross-sheet
                    # connectivity, suppress the rest.
                    for idx in members[1:]:
                        wired_pin_ids.add(id(positions[idx][2]))

    return wired_pin_ids


def _seg_crosses_box(a, b, bmin, bmax, inset=0.5):
    """True if segment a->b passes through the interior of box [bmin,bmax]
    shrunk by ``inset`` mm. Liang-Barsky. Pure geometry — tool-agnostic."""
    xmin, ymin = bmin[0] + inset, bmin[1] + inset
    xmax, ymax = bmax[0] - inset, bmax[1] - inset
    if xmin >= xmax or ymin >= ymax:
        return False
    x1, y1 = a
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - xmin), (dx, xmax - x1), (-dy, y1 - ymin), (dy, ymax - y1)):
        if p == 0:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                if r > t1:
                    return False
                t0 = max(t0, r)
            else:
                if r < t0:
                    return False
                t1 = min(t1, r)
    return t0 <= t1


def _part_render_bbox(part, backend, sheet_tx):
    """Axis-aligned (min, max) of a part's body in render-mm, or None.

    Reconstructs the body box from its local-coordinate corners run through
    ``backend.pin_render_pos``-equivalent geometry. Implemented via the
    backend's point transform so the agnostic layer stays render-space-only.
    """
    bbox = getattr(part, "place_bbox", None) or getattr(part, "lbl_bbox", None)
    if bbox is None:
        return None
    corners = [
        backend.render_xy(bbox.min.x, bbox.min.y, part, sheet_tx),
        backend.render_xy(bbox.max.x, bbox.min.y, part, sheet_tx),
        backend.render_xy(bbox.min.x, bbox.max.y, part, sheet_tx),
        backend.render_xy(bbox.max.x, bbox.max.y, part, sheet_tx),
    ]
    xs = [c[0] for c in corners]
    ys = [c[1] for c in corners]
    return (min(xs), min(ys)), (max(xs), max(ys))


def find_power_bus_runs(node, backend, sheet_tx, max_gap_mm=10.0):
    """Co-linear runs of 3+ power-net pins -> (wire segments, pins to skip).

    Returns ``(segments, bus_pin_ids)`` where ``segments`` is a list of
    ``(x1, y1, x2, y2, net_name)`` in render-mm (caller emits via
    ``backend.emit_wire``) and ``bus_pin_ids`` is the set of ``id(pin)`` that
    should NOT get individual power symbols.

    Relocated DECISION half of ``_gen_power_bus_wires``; the wire Sexp
    construction stays in the backend.
    """
    node_part_ids = {id(p) for p in node.parts}
    bus_pin_ids = set()
    segments = []

    # Part body bboxes in render-mm, so we can drop bus segments routed
    # straight through a component.
    part_bodies = []
    for _p in node.parts:
        if isinstance(_p, NetTerminal):
            continue
        rb = _part_render_bbox(_p, backend, sheet_tx)
        if rb:
            part_bodies.append((rb[0], rb[1], _p))

    seen_nets = set()
    for part in node.parts:
        if isinstance(part, NetTerminal):
            continue
        for pin in part:
            if not pin.is_connected():
                continue
            net = pin.net
            if id(net) in seen_nets:
                continue
            seen_nets.add(id(net))

            if not backend.is_power_net_name(net.name):
                continue

            pins_in_node = [
                p
                for p in net.pins
                if id(p.part) in node_part_ids
                and not isinstance(p.part, NetTerminal)
                and len(p.part.pins) == 2
                and not all(
                    pp.is_connected() and backend.is_power_net_name(pp.net.name)
                    for pp in p.part.pins
                )
            ]
            if len(pins_in_node) < 3:
                continue

            positions = []
            for p in pins_in_node:
                x, y = backend.pin_render_pos(p, sheet_tx)
                positions.append((backend.round_mm(x), backend.round_mm(y), p))

            # Group pins by shared X coordinate (vertical columns).
            x_groups = defaultdict(list)
            for pos in positions:
                x_key = round(pos[0], 1)
                x_groups[x_key].append(pos)

            # Group pins by shared Y coordinate (horizontal rows).
            y_groups = defaultdict(list)
            for pos in positions:
                y_key = round(pos[1], 1)
                y_groups[y_key].append(pos)

            def _split_runs(sorted_group, axis):
                """Split sorted positions into contiguous runs by max_gap_mm."""
                runs = [[sorted_group[0]]]
                for j in range(1, len(sorted_group)):
                    gap = abs(sorted_group[j][axis] - sorted_group[j - 1][axis])
                    if gap <= max_gap_mm:
                        runs[-1].append(sorted_group[j])
                    else:
                        runs.append([sorted_group[j]])
                return [r for r in runs if len(r) >= 3]

            def _seg_clear(x1, y1, x2, y2, p1, p2):
                """Allowed only if it doesn't pass through a part body other
                than the two pins it connects."""
                for bmin, bmax, bp in part_bodies:
                    if bp is p1.part or bp is p2.part:
                        continue
                    if _seg_crosses_box((x1, y1), (x2, y2), bmin, bmax):
                        return False
                return True

            def _emit_run(run, net_name):
                # Split the run at any segment that would cross a part body.
                subruns = [[run[0]]]
                for j in range(len(run) - 1):
                    x1, y1, p1 = run[j]
                    x2, y2, p2 = run[j + 1]
                    if _seg_clear(x1, y1, x2, y2, p1, p2):
                        subruns[-1].append(run[j + 1])
                    else:
                        subruns.append([run[j + 1]])
                for sub in subruns:
                    if len(sub) < 2:
                        continue  # isolated pin -> gets its own power symbol
                    for j in range(len(sub) - 1):
                        x1, y1, _ = sub[j]
                        x2, y2, _ = sub[j + 1]
                        segments.append((x1, y1, x2, y2, net_name))
                    for _, _, p in sub[:-1]:
                        bus_pin_ids.add(id(p))

            # Process vertical groups (same X, split by Y gap).
            for x_key, group in x_groups.items():
                if len(group) < 3:
                    continue
                group.sort(key=lambda p: p[1])
                for run in _split_runs(group, axis=1):
                    _emit_run(run, net.name)

            # Process horizontal groups (same Y, split by X gap).
            for y_key, group in y_groups.items():
                if len(group) < 3:
                    continue
                group.sort(key=lambda p: p[0])
                for run in _split_runs(group, axis=0):
                    _emit_run(run, net.name)

    return segments, bus_pin_ids


def deconflict_labels(labels, occupied_seed, node, backend, sheet_tx):
    """Decide which net labels to nudge off component bodies.

    Relocated DECISION half of ``_deconflict_labels`` (the Sexp reading +
    mutation stays in the backend). Inputs are abstract:

      * ``labels``  — list of ``(idx, net_name, lx, ly, langle)`` for every
        ``global_label`` element, in element order. ``idx`` is opaque to this
        function (returned back so the caller can locate the element).
        ``langle is None`` marks a record that only seeds occupancy.
      * ``occupied_seed`` — list of ``(cell, owner)`` in element order; applied
        in order so later entries overwrite earlier ones at a shared cell,
        exactly as the original single-pass element scan did. ``owner`` is the
        net name for a label anchor, or ``None`` for a wire endpoint.

    Returns ``(moves, new_wires)`` where ``moves`` is a list of
    ``(idx, nx, ny)`` label repositions (render-mm) and ``new_wires`` is a list
    of ``(ax, ay, nx, ny)`` short connecting wires (render-mm) to preserve
    connectivity. The label/box geometry comes from ``backend.label_bbox`` so
    box sizing is tool-specific; the math is identical to the original.
    """
    from math import cos, radians, sin

    from skidl.geometry import BBox

    MARGIN_MM = 1.27  # ~50 mils clearance from the body
    GRID = 1.27  # KiCad 50-mil grid

    def _snap(v):
        return round(round(v / GRID) * GRID, 2)

    def _cell(x, y):
        return (round(x / GRID), round(y / GRID))

    def _on_grid(v):
        return abs(v / GRID - round(v / GRID)) < 0.02

    # Names of stubbed nets on this node. A stubbed net's label sits ON its pin
    # and connectivity is carried by the net NAME, not by a wire. Nudging such a
    # label off its pin (and adding a connecting wire) defeats the stub design:
    # the wire it would draw runs the full width of whatever neighbouring body
    # the label happens to graze, producing the long cross-sheet wires the user
    # sees. So these labels must stay put — they are excluded from relocation
    # below (overlap is harmless: the name still resolves connectivity).
    stub_net_names = set()
    for part in node.parts:
        if isinstance(part, NetTerminal):
            continue
        for pin in part:
            net = getattr(pin, "net", None)
            if net is None:
                continue
            if (
                getattr(pin, "stub", False)
                or getattr(net, "stub", False)
                or getattr(net, "_stub", False)
            ):
                stub_net_names.add(net.name)

    # Component body bboxes in sheet (mm) coordinates.
    comp_bboxes = []
    for part in node.parts:
        if isinstance(part, NetTerminal):
            continue
        bbox = getattr(part, "place_bbox", None) or getattr(part, "lbl_bbox", None)
        if bbox is None:
            continue
        tb = bbox * (getattr(part, "tx", Tx()) * sheet_tx)
        comp_bboxes.append(
            BBox(
                Point(min(tb.min.x, tb.max.x), min(tb.min.y, tb.max.y)),
                Point(max(tb.min.x, tb.max.x), max(tb.min.y, tb.max.y)),
            )
        )
    if not comp_bboxes:
        return [], []

    # Occupied grid cells, applied in original element order: existing label
    # anchors (keyed by net) and wire endpoints (net unknown -> never reuse).
    occupied = {}
    for cell, owner in occupied_seed:
        occupied[cell] = owner

    def _label_dir(a):
        r = radians(a)
        return (cos(r), sin(r))

    LABEL_W, LABEL_H = backend.label_bbox(None)
    moves = []
    new_wires = []
    for idx, net, lx, ly, langle in labels:
        # Records without a resolved angle only seeded `occupied` above
        # (they matched the original's len(at)<4 case) and are not moved.
        if langle is None:
            continue
        # Stubbed-net labels are connected by NAME and must stay on their pin;
        # relocating them would draw a long connecting wire across a neighbour.
        if net in stub_net_names:
            continue
        # Only spread labels whose anchor (pin) is already on-grid.
        if not (_on_grid(lx) and _on_grid(ly)):
            continue
        dx, dy = _label_dir(langle)
        x_end, y_end = lx + dx * LABEL_W, ly + dy * LABEL_W
        lbl_bbox = BBox(
            Point(min(lx, x_end) - LABEL_H / 2, min(ly, y_end) - LABEL_H / 2),
            Point(max(lx, x_end) + LABEL_H / 2, max(ly, y_end) + LABEL_H / 2),
        )
        for cb in comp_bboxes:
            if not lbl_bbox.intersects(cb):
                continue
            # Skip the label's OWN component: a net label is anchored at its pin,
            # which sits on that part's body-edge by construction, so an
            # outward-pointing on-pin label always grazes its own bbox. That is
            # correct placement, not a conflict — nudging it here is what stepped
            # every label off its pin (one dcwire per label). Only relocate when
            # the label projects into a DIFFERENT body it isn't anchored to.
            if (
                cb.min.x - 0.05 <= lx <= cb.max.x + 0.05
                and cb.min.y - 0.05 <= ly <= cb.max.y + 0.05
            ):
                continue
            ax, ay = lx, ly  # original anchor (on the pin)
            if abs(dx) > abs(dy):
                offset = (
                    (cb.max.x - lx + MARGIN_MM)
                    if dx > 0
                    else (cb.min.x - lx - MARGIN_MM)
                )
                nx, ny = _snap(lx + offset), _snap(ly)
            else:
                offset = (
                    (cb.max.y - ly + MARGIN_MM)
                    if dy > 0
                    else (cb.min.y - ly - MARGIN_MM)
                )
                nx, ny = _snap(lx), _snap(ly + offset)
            if (nx, ny) == (ax, ay):
                break
            # Reject moves that would collide with a different net or a wire end.
            owner = occupied.get(_cell(nx, ny), "__free__")
            if owner not in ("__free__", net):
                break  # leave the label on its pin rather than risk a short
            moves.append((idx, nx, ny))
            occupied[_cell(nx, ny)] = net
            new_wires.append((ax, ay, nx, ny))
            break  # resolve first overlap per label

    return moves, new_wires


def find_no_connect_pins(node, backend, sheet_tx):
    """No-connect flag positions (render-mm) for pins on an NCNet.

    Returns a list of ``(x, y, part_ref, pin_num)`` so the caller can emit a
    no_connect flag per NC pin with the original UUID seed. Relocated detection
    half of ``_gen_no_connect_flags``; the no_connect Sexp stays in the backend.
    """
    flags = []
    for part in node.parts:
        if isinstance(part, NetTerminal):
            continue
        for pin in part:
            if not isinstance(getattr(pin, "net", None), NCNet):
                continue
            pin_pt = getattr(pin, "pt", Point(pin.x, pin.y))
            part_tx = getattr(pin.part, "tx", Tx())
            pt = pin_pt * part_tx * sheet_tx
            flags.append((pt.x, pt.y, part.ref, pin.num))
    return flags
