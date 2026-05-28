# -*- coding: utf-8 -*-

"""
MCU 引脚级分叉布局：anchor net 存在真实 T 型/星型分叉时，主干 + 支路 slot 摆放。
与贪心单链共线布局互斥（同 pin）；默认开启，mcu_fork_layout=False 回退旧行为。
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from skidl.geometry import BBox, Point, Segment, Tx

from .mcu import (
    _MCU_COMM_NET_TOKENS,
    _MCU_IO_NET_TOKENS,
    _chain_neighbor_pin,
    _colinear_chain_sort_key,
    _ensure_anchor_toward_hub,
    _hub_pin_side,
    _is_anonymous_net,
    _is_colinear_chain_part,
    _layout_bbox,
    _mcu_layout_bbox,
    _mcu_part_is_connector,
    _mcu_pin_route_pt,
    _mcu_place_part_pin_to_y,
    _mcu_wire_two_pins,
    _net_label,
    _pair_pins_to_main,
    _place_colinear_chain,
    _placement_bbox,
    _token_in_text,
    _walk_colinear_chain,
)

# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------


@dataclass
class BranchSpec:
    """从 anchor net 上某一 neighbor 向外延伸的支路。"""

    parts: List
    anchor_neighbor: object
    exit_net_label: str = ""
    role: str = "other"
    score: int = 0
    branch_id: int = 0
    overflow_stub: bool = False

    @property
    def refs(self):
        return [str(getattr(p, "ref", "") or "") for p in self.parts]


@dataclass
class PinForkSpec:
    """单颗 MCU 信号引脚的分叉布局规格。"""

    mcu_pin: object
    anchor_net: object
    trunk: BranchSpec
    branches: List[BranchSpec] = field(default_factory=list)
    fork_hub: Optional[object] = None
    slot_assignments: Dict[int, str] = field(default_factory=dict)
    fork_point: Optional[Point] = None
    pin_side: str = "right"

    def all_parts(self):
        out = list(self.trunk.parts)
        for b in self.branches:
            out.extend(b.parts)
        return out

    def handled_pin_ids(self):
        return {id(self.mcu_pin)}


def _fork_options(options):
    grid = int(options.get("grid", 100))
    gap = options.get("topology_gap") or options.get(
        "trunk_gap", max(int(options.get("blk_int_pad", 100)), grid * 2)
    )
    return {
        "enabled": bool(options.get("mcu_fork_layout", True)),
        "margin": int(options.get("mcu_fork_margin") or gap),
        "max_branches": int(options.get("mcu_fork_max_branches", 4)),
        "overflow_dist": int(
            options.get("mcu_fork_stub_overflow_dist") or (8 * grid)
        ),
        "grid": grid,
        "gap": int(gap),
        "debug": bool(
            options.get("mcu_fork_debug", False)
            or options.get("schematic_progress", False)
        ),
    }


def _pin_label(pin):
    return str(getattr(pin, "name", "") or "?")


def _log_fork(node, msg, options):
    if not _fork_options(options).get("debug"):
        return
    from skidl.logger import active_logger

    active_logger.info("[mcu_fork] %s" % msg)


def preview_fork_reserved_parts(node, main_part, parts, nets, roles, **options):
    """
    布局前预扫描：返回将被 pin 分叉接管的器件（避免 rowbased passive_far 抢先摆放）。
    """
    if not _fork_options(options)["enabled"]:
        return set()
    specs = discover_pin_forks(
        node, main_part, parts, nets, roles, set(), **options
    )
    reserved = set()
    for spec in specs:
        for part in spec.all_parts():
            reserved.add(part)
    node._mcu_fork_specs_preview = specs
    node._mcu_fork_reserved_parts = reserved
    return reserved


def _anchor_neighbors(node, main_part, anchor_net, part_set):
    """anchor net 上除 MCU 外的可共线器件。"""
    net_parts = node._net_connected_parts(anchor_net, allowed_parts=part_set)
    return sorted(
        [
            p
            for p in net_parts
            if p is not main_part and _is_colinear_chain_part(p, main_part)
        ],
        key=lambda p: _colinear_chain_sort_key(p),
    )


def _neighbor_exit_semantics(node, neighbor, anchor_net, part_set):
    """neighbor 离开 anchor net 后的网名语义集合（非电源）。"""
    labels = set()
    for pin in getattr(neighbor, "pins", []):
        net = getattr(pin, "net", None)
        if net is None or net is anchor_net:
            continue
        label = _net_label(net)
        if node._is_power_net_name(label):
            continue
        labels.add(label.upper())
    return labels


def _neighbor_non_anchor_degrees(node, neighbor, anchor_net, part_set):
    """neighbor 在非 anchor、非电源网上的可共线延续数。"""
    count = 0
    for pin in getattr(neighbor, "pins", []):
        net = getattr(pin, "net", None)
        if net is None or net is anchor_net:
            continue
        if node._is_power_net_name(_net_label(net)):
            continue
        for p in node._net_connected_parts(net, allowed_parts=part_set):
            if p is neighbor:
                continue
            if _is_colinear_chain_part(p, neighbor):
                count += 1
    return count


def _is_decouple_only_star(node, main_part, anchor_net, neighbors, part_set):
    """MCU + 多颗仅接 GND/VCC 的 C：非信号分叉。"""
    if not neighbors:
        return False
    if not all(
        str(getattr(p, "ref", "") or "").upper().startswith("C") for p in neighbors
    ):
        return False
    for part in neighbors:
        has_signal = False
        for pin in getattr(part, "pins", []):
            net = getattr(pin, "net", None)
            if net is None or net is anchor_net:
                continue
            label = _net_label(net)
            if not node._is_power_net_name(label):
                has_signal = True
                break
        if has_signal:
            return False
    return True


def _merged_extension_is_single_chain(
    node, main_part, anchor_net, neighbors, part_set, used_parts
):
    """
    多个 anchor neighbor 向外的一步语义若相同，视为单链延续而非分叉。
    """
    if len(neighbors) < 2:
        return True
    semantics = set()
    for nb in neighbors:
        semantics |= _neighbor_exit_semantics(node, nb, anchor_net, part_set)
    if not semantics:
        return True
    return len(semantics) <= 1


def is_real_fork(node, main_part, anchor_pin, anchor_net, part_set, used_parts=None):
    """anchor net 是否为需分叉布局的真实 T 型/星型结构。"""
    if anchor_pin is None or anchor_net is None:
        return False
    if node._is_power_net_name(_net_label(anchor_net)):
        return False
    neighbors = _anchor_neighbors(node, main_part, anchor_net, part_set)
    if len(neighbors) < 2:
        return False
    if _is_decouple_only_star(node, main_part, anchor_net, neighbors, part_set):
        return False
    if _merged_extension_is_single_chain(
        node, main_part, anchor_net, neighbors, part_set, used_parts or set()
    ):
        return False

    semantics = []
    for nb in neighbors:
        semantics.append(_neighbor_exit_semantics(node, nb, anchor_net, part_set))

    # 至少两个 neighbor 的「一步之外」网语义不同
    for i in range(len(neighbors)):
        for j in range(i + 1, len(neighbors)):
            if semantics[i] != semantics[j] and (semantics[i] or semantics[j]):
                return True

    # 某 neighbor 有多条非 anchor 信号延续（如 R10：TX + 回到 LED 网不算，需不同网）
    for nb in neighbors:
        if _neighbor_non_anchor_degrees(node, nb, anchor_net, part_set) >= 2:
            return True

    return len(neighbors) >= 2


def _walk_branch_from_neighbor(
    node,
    main_part,
    anchor_net,
    start_part,
    part_set,
    used_parts,
    anchor_neighbor_roots=None,
):
    """
    从 anchor net 上的 neighbor 向外走链，不跨入其它 anchor 根（避免合并支路）。
    """
    roots = set(anchor_neighbor_roots or ())
    chain = [start_part]
    visited = {id(main_part), id(start_part)}
    prev = start_part

    while True:
        candidates = []
        for pin in getattr(prev, "pins", []):
            net = getattr(pin, "net", None)
            if net is None:
                continue
            if node._is_power_net_name(_net_label(net)):
                continue
            for p in node._net_connected_parts(net, allowed_parts=part_set):
                if id(p) in visited:
                    continue
                if p is prev:
                    continue
                if not _is_colinear_chain_part(p, main_part):
                    continue
                if id(p) in used_parts:
                    continue
                if net is anchor_net and p in roots and p is not start_part:
                    continue
                candidates.append(p)
        if not candidates:
            break
        candidates.sort(key=_colinear_chain_sort_key)
        nxt = candidates[0]
        chain.append(nxt)
        visited.add(id(nxt))
        prev = nxt

    return chain


def _branch_exit_label(node, branch_parts, anchor_net, part_set):
    """支路最远非电源网名（分类用）。"""
    if not branch_parts:
        return ""
    last = branch_parts[-1]
    best = ""
    for pin in getattr(last, "pins", []):
        net = getattr(pin, "net", None)
        if net is None or net is anchor_net:
            continue
        label = _net_label(net)
        if node._is_power_net_name(label):
            continue
        if label and (not best or label.startswith("/")):
            best = label
    if best:
        return best
    for part in branch_parts:
        for pin in getattr(part, "pins", []):
            net = getattr(pin, "net", None)
            if net is None or net is anchor_net:
                continue
            label = _net_label(net)
            if not node._is_power_net_name(label):
                return label
    return ""


def _classify_branch_role(node, branch_parts, exit_label, part_adj, roles):
    """支路角色与评分。"""
    score = 0
    role = "other"
    label_u = (exit_label or "").upper()

    if _token_in_text(label_u, _MCU_COMM_NET_TOKENS) or label_u.startswith("/"):
        score += 100
        role = "comm"
    for part in branch_parts:
        ref = str(getattr(part, "ref", "") or "").upper()
        if _mcu_part_is_connector(part, roles):
            score += 80
            role = "connector"
        if ref.startswith("LED") or "LED" in str(getattr(part, "value", "") or "").upper():
            score += 10
            role = "indicator"
        if ref.startswith("C"):
            for pin in getattr(part, "pins", []):
                net = getattr(pin, "net", None)
                if net and node._is_power_net_name(_net_label(net)):
                    score -= 50
                    role = "decouple"

    if _token_in_text(label_u, _MCU_IO_NET_TOKENS):
        score += 40
        if role == "other":
            role = "io"

    if node._is_power_net_name(label_u) or "VCC" in label_u or "VDD" in label_u:
        score += 10
        if role == "other":
            role = "indicator"

    for part in branch_parts:
        for nb in part_adj.get(id(part), set()):
            if _mcu_part_is_connector(nb, roles):
                score += 80
                role = "connector"

    return role, score


def _enumerate_branches(
    node, main_part, anchor_pin, anchor_net, part_set, used_parts, part_adj, roles
):
    """枚举 anchor net 上各 neighbor 支路并分类。"""
    neighbors = _anchor_neighbors(node, main_part, anchor_net, part_set)
    branches = []
    bid = 0
    for nb in neighbors:
        parts = _walk_branch_from_neighbor(
            node,
            main_part,
            anchor_net,
            nb,
            part_set,
            used_parts,
            anchor_neighbor_roots=set(neighbors),
        )
        exit_label = _branch_exit_label(node, parts, anchor_net, part_set)
        role, score = _classify_branch_role(
            node, parts, exit_label, part_adj, roles
        )
        branches.append(
            BranchSpec(
                parts=parts,
                anchor_neighbor=nb,
                exit_net_label=exit_label,
                role=role,
                score=score,
                branch_id=bid,
            )
        )
        bid += 1
    return branches


def _pick_trunk(branches: List[BranchSpec]) -> Tuple[BranchSpec, List[BranchSpec]]:
    """选视觉主干，其余为支路。"""
    if not branches:
        empty = BranchSpec(parts=[], anchor_neighbor=None)
        return empty, []
    if len(branches) == 1:
        return branches[0], []

    def sort_key(b: BranchSpec):
        named = 1 if (b.exit_net_label or "").startswith("/") else 0
        ref = str(getattr(b.anchor_neighbor, "ref", "") or "")
        return (b.score, named, len(b.parts), ref)

    ordered = sorted(branches, key=sort_key, reverse=True)
    return ordered[0], ordered[1:]


def build_pin_fork_spec(
    node, main_part, anchor_pin, parts, nets, used_parts, part_adj, roles
):
    """为单 pin 构建分叉规格；非分叉返回 None。"""
    anchor_net = getattr(anchor_pin, "net", None)
    part_set = set(parts)
    if not is_real_fork(
        node, main_part, anchor_pin, anchor_net, part_set, used_parts
    ):
        return None

    all_branches = _enumerate_branches(
        node, main_part, anchor_pin, anchor_net, part_set, used_parts, part_adj, roles
    )
    trunk, side_branches = _pick_trunk(all_branches)
    if trunk.parts:
        trunk_fork_hub = trunk.parts[-1]
    else:
        trunk_fork_hub = None

    pin_side = _hub_pin_side(main_part, anchor_pin)
    slots = _assign_branch_slots(side_branches, pin_side)

    return PinForkSpec(
        mcu_pin=anchor_pin,
        anchor_net=anchor_net,
        trunk=trunk,
        branches=side_branches,
        fork_hub=trunk_fork_hub,
        slot_assignments=slots,
        pin_side=pin_side,
    )


def _assign_branch_slots(branches: List[BranchSpec], pin_side: str) -> Dict[int, str]:
    """为支路分配 up/down/left/right slot；同侧 stack。"""
    horizontal = pin_side in ("left", "right")
    preferred = {
        "indicator": "up" if horizontal else "left",
        "decouple": "down" if horizontal else "right",
        "comm": "down" if horizontal else "right",
        "connector": "down" if horizontal else "right",
        "io": "down" if horizontal else "right",
        "other": "down" if horizontal else "right",
    }
    slot_counts = {}
    assignments = {}
    for b in branches:
        base = preferred.get(b.role, "down" if horizontal else "right")
        k = slot_counts.get(base, 0)
        slot_counts[base] = k + 1
        if k == 0:
            assignments[b.branch_id] = base
        else:
            assignments[b.branch_id] = f"{base}_stack{k}"
    return assignments


def pin_handled_by_fork(node, anchor_pin) -> bool:
    specs = getattr(node, "_mcu_fork_specs", None) or []
    pid = id(anchor_pin)
    for spec in specs:
        if id(spec.mcu_pin) == pid:
            return True
    return False


def discover_pin_forks(node, main_part, parts, nets, roles, used_parts, **options):
    """枚举所有需分叉的 MCU 引脚规格。"""
    if not _fork_options(options)["enabled"]:
        return []

    from skidl.schematics.trunk_layout import build_part_adjacency

    part_set = set(parts)
    part_adj = (
        build_part_adjacency(parts, nets) if nets else {id(p): set() for p in parts}
    )
    specs = []
    local_used = set(used_parts or ())

    for pin in getattr(main_part, "pins", []):
        net = getattr(pin, "net", None)
        if net is None:
            continue
        if node._is_power_net_name(_net_label(net)):
            continue
        spec = build_pin_fork_spec(
            node, main_part, pin, parts, nets, local_used, part_adj, roles
        )
        if spec is None:
            continue
        specs.append(spec)
        for p in spec.all_parts():
            local_used.add(id(p))

    return specs


# ---------------------------------------------------------------------------
# 摆放
# ---------------------------------------------------------------------------


def _slot_offset(slot_name: str, pin_side: str, grid: int, gap: int, stack_index: int):
    """支路 slot 相对 fork 点的法向偏移。"""
    base = slot_name.split("_stack")[0]
    mag = (gap + grid) * (1 + stack_index)
    horizontal = pin_side in ("left", "right")
    if horizontal:
        if base == "up":
            return Point(0, mag)
        if base == "down":
            return Point(0, -mag)
        if base == "left":
            return Point(-mag, 0)
        return Point(mag, 0)
    if base == "left":
        return Point(-mag, 0)
    if base == "right":
        return Point(mag, 0)
    if base == "up":
        return Point(0, mag)
    return Point(0, -mag)


def _place_trunk(
    node, main_part, anchor_pin, trunk: BranchSpec, gap, grid
):
    """主干：MCU + trunk.parts 沿 pin 法向共线摆。"""
    chain = [main_part] + list(trunk.parts)
    return _place_colinear_chain(node, main_part, anchor_pin, chain, gap, grid)


def _place_branch_chain(
    node,
    hub_part,
    fork_pt: Point,
    branch: BranchSpec,
    slot_name: str,
    pin_side: str,
    gap,
    grid,
    stack_index: int,
    main_part=None,
):
    """从 fork 点沿 slot 方向摆放支路链；首颗从 anchor_neighbor 侧接出。"""
    placed = set()
    if not branch.parts:
        return placed

    offset = _slot_offset(slot_name, pin_side, grid, gap, stack_index)
    start = fork_pt + offset
    horizontal = pin_side in ("left", "right")
    part_set = set(getattr(node, "parts", branch.parts))
    if main_part is not None:
        part_set.add(main_part)

    if horizontal:
        row_y = start.y
        x_edge = start.x
        outward_sign = 1 if pin_side == "right" else -1
        prev = hub_part
        for part in branch.parts:
            bb = _mcu_layout_bbox(part) or _layout_bbox(part)
            if bb is None:
                continue
            w = max(bb.w, grid)
            if outward_sign < 0:
                x_left = x_edge - w
                pin = _chain_neighbor_pin(part, prev, node, part_set)
                if pin is None and prev is hub_part:
                    pin = _chain_neighbor_pin(part, branch.anchor_neighbor, node, part_set)
                _mcu_place_part_pin_to_y(part, x_left, row_y, grid, pin)
                _ensure_anchor_toward_hub(part, pin, outward_sign)
                placed.add(part)
                x_edge = x_left - gap
            else:
                pin = _chain_neighbor_pin(part, prev, node, part_set)
                if pin is None and prev is hub_part:
                    pin = _chain_neighbor_pin(part, branch.anchor_neighbor, node, part_set)
                _mcu_place_part_pin_to_y(part, x_edge, row_y, grid, pin)
                _ensure_anchor_toward_hub(part, pin, outward_sign)
                placed.add(part)
                x_edge += max(bb.w, grid) + gap
            prev = part
    else:
        col_x = start.x
        y_edge = start.y
        prev = hub_part
        for part in branch.parts:
            bb = _mcu_layout_bbox(part) or _layout_bbox(part)
            if bb is None:
                continue
            h = max(bb.h, grid)
            pin = _chain_neighbor_pin(part, prev, node, part_set)
            if pin is None and prev is hub_part:
                pin = _chain_neighbor_pin(part, branch.anchor_neighbor, node, part_set)
            if pin_side == "top":
                _mcu_place_part_pin_to_y(part, col_x, y_edge, grid, pin)
                y_edge += h + gap
            else:
                _mcu_place_part_pin_to_y(part, col_x, y_edge - h, grid, pin)
                y_edge -= h + gap
            placed.add(part)
            prev = part
    return placed


def _compute_fork_point(node, main_part, anchor_pin, trunk, margin, gap, grid):
    """主干末端外侧 fork 锚点。"""
    hp = _mcu_pin_route_pt(anchor_pin)
    if not trunk.parts:
        side = _hub_pin_side(main_part, anchor_pin)
        if side == "right":
            return Point(hp.x + margin, hp.y)
        if side == "left":
            return Point(hp.x - margin, hp.y)
        if side == "top":
            return Point(hp.x, hp.y + margin)
        return Point(hp.x, hp.y - margin)

    hub = trunk.parts[-1]
    part_set = set(getattr(node, "parts", trunk.parts))
    prev = trunk.parts[-2] if len(trunk.parts) >= 2 else main_part
    pin = _chain_neighbor_pin(hub, prev, node, part_set)
    if pin is None:
        pin = _chain_neighbor_pin(hub, main_part, node, part_set)
    if pin is None:
        return hp

    pt = _mcu_pin_route_pt(pin)
    side = _hub_pin_side(main_part, anchor_pin)
    if side == "right":
        bb = _mcu_layout_bbox(hub) or _layout_bbox(hub)
        w = max(bb.w, grid) if bb else grid
        return Point(pt.x + w + margin, pt.y)
    if side == "left":
        bb = _mcu_layout_bbox(hub) or _layout_bbox(hub)
        w = max(bb.w, grid) if bb else grid
        return Point(pt.x - margin, pt.y)
    if side == "top":
        bb = _mcu_layout_bbox(hub) or _layout_bbox(hub)
        h = max(bb.h, grid) if bb else grid
        return Point(pt.x, pt.y + h + margin)
    bb = _mcu_layout_bbox(hub) or _layout_bbox(hub)
    h = max(bb.h, grid) if bb else grid
    return Point(pt.x, pt.y - h - margin)


def place_pin_fork_layout(node, main_part, spec: PinForkSpec, gap, grid, margin, **options):
    """摆放单 pin 分叉规格，返回已放置器件集合。"""
    opts = _fork_options(options)
    placed = set()
    trunk_placed = _place_trunk(
        node, main_part, spec.mcu_pin, spec.trunk, gap, grid
    )
    placed |= trunk_placed

    fork_pt = _compute_fork_point(
        node, main_part, spec.mcu_pin, spec.trunk, margin, gap, grid
    )
    spec.fork_point = fork_pt

    hub_for_branch = spec.fork_hub or main_part
    slot_stack_idx = {}
    for branch in spec.branches:
        slot = spec.slot_assignments.get(branch.branch_id, "down")
        base = slot.split("_stack")[0]
        idx = slot_stack_idx.get(base, 0)
        slot_stack_idx[base] = idx + 1

        bp = _place_branch_chain(
            node,
            hub_for_branch,
            fork_pt,
            branch,
            slot,
            spec.pin_side,
            gap,
            grid,
            idx,
            main_part=main_part,
        )
        placed |= bp
        if not bp:
            branch.overflow_stub = True

    return placed


def place_all_pin_forks(node, main_part, parts, nets, roles, used_parts, **options):
    """
    发现、摆放所有 pin 分叉；写入 node._mcu_fork_specs / _mcu_fork_part_sets。
    返回 (specs, placed_parts, updated_used_ids, colinear_part_sets)。
    """
    opts = _fork_options(options)
    if not opts["enabled"]:
        return [], set(), set(used_parts or ()), []

    specs = discover_pin_forks(
        node, main_part, parts, nets, roles, used_parts, **options
    )
    node._mcu_fork_specs = specs
    node._mcu_fork_part_sets = []
    reserved = set()
    for spec in specs:
        for part in spec.all_parts():
            reserved.add(part)
    node._mcu_fork_reserved_parts = reserved

    margin = opts["margin"]
    gap = opts["gap"]
    grid = opts["grid"]

    placed = set()
    used = set(used_parts or ())
    colinear_sets = []

    for spec in specs:
        # 先占用器件 id，防止 Header 端口链在摆放前抢走 R12 等支路器件
        for part in spec.all_parts():
            used.add(id(part))

        fp = place_pin_fork_layout(node, main_part, spec, gap, grid, margin)
        placed |= fp
        for p in fp:
            used.add(id(p))

        pin_name = _pin_label(spec.mcu_pin)
        trunk_refs = spec.trunk.refs
        branch_refs = [b.refs for b in spec.branches]
        placed_refs = sorted(
            str(getattr(p, "ref", "") or "") for p in fp
        )
        _log_fork(
            node,
            "pin %s trunk=%s branches=%s placed=%s"
            % (pin_name, trunk_refs, branch_refs, placed_refs),
            options,
        )

        # 按 branch 登记 part_sets（供 label / 布线）
        trunk_set = frozenset([main_part] + list(spec.trunk.parts))
        node._mcu_fork_part_sets.append(trunk_set)
        colinear_sets.append(trunk_set)

        for branch in spec.branches:
            if branch.overflow_stub:
                continue
            bset = frozenset(
                [main_part, spec.fork_hub] + list(branch.parts)
                if spec.fork_hub
                else [main_part] + list(branch.parts)
            )
            bset = frozenset(p for p in bset if p is not None)
            node._mcu_fork_part_sets.append(bset)
            colinear_sets.append(bset)

    return specs, placed, used, colinear_sets


# ---------------------------------------------------------------------------
# 分叉感知布线
# ---------------------------------------------------------------------------


def find_fork_spec_for_net(node, net):
    """若 net 为某 pin fork 的 anchor 星型网，返回 PinForkSpec。"""
    for spec in getattr(node, "_mcu_fork_specs", None) or []:
        if getattr(spec, "anchor_net", None) is net:
            return spec
    return None


def route_fork_anchor_net(node, net, spec: PinForkSpec, grid):
    """
    anchor 星型网：主干水平段 + fork 竖 stub 到支路（避免三器件共线母线）。
    """
    from skidl.schematics.place import is_net_terminal

    pins = [
        pin
        for pin in net.pins
        if pin.part in getattr(node, "parts", [])
        and not is_net_terminal(pin.part)
    ]
    if len(pins) < 2:
        return None

    # 从 topology 取 main_part
    topo = getattr(node, "_last_topology_result", None) or {}
    main_part = topo.get("main_part") or getattr(
        node, "_human_readable_main_part", None
    )
    if main_part is None:
        return None

    mcu_pins = [p for p in pins if p.part is main_part]
    if not mcu_pins:
        return None
    mcu_pin = mcu_pins[0]
    trunk_y = _mcu_pin_route_pt(mcu_pin).y

    segs = []
    trunk_parts = set(spec.trunk.parts)
    branch_first = {}
    for br in spec.branches:
        if br.parts and not br.overflow_stub:
            branch_first[id(br.parts[0])] = br

    for pin in pins:
        if pin.part is main_part:
            continue
        pt = _mcu_pin_route_pt(pin)
        if pin.part in trunk_parts:
            if abs(pt.y - trunk_y) > 1:
                segs.append(Segment(copy.copy(pt), Point(pt.x, trunk_y)))
        else:
            for br in spec.branches:
                if br.overflow_stub:
                    continue
                if pin.part in br.parts:
                    # 支路器件：竖 stub 接到主干水平线（T 型拐点）
                    if abs(pt.y - trunk_y) > 1:
                        segs.append(Segment(copy.copy(pt), Point(pt.x, trunk_y)))
                    break

    trunk_pin_pts = [
        _mcu_pin_route_pt(p)
        for p in pins
        if p.part in trunk_parts or p.part is main_part
    ]
    if trunk_pin_pts:
        xs = [p.x for p in trunk_pin_pts] + [_mcu_pin_route_pt(mcu_pin).x]
        x_min, x_max = min(xs), max(xs)
        if x_min != x_max:
            segs.insert(0, Segment(Point(x_min, trunk_y), Point(x_max, trunk_y)))

    return segs if segs else None


def mark_fork_overflow_stubs(node, nets, **options):
    """支路 overflow 时标记远端网为 stub。"""
    for spec in getattr(node, "_mcu_fork_specs", None) or []:
        for branch in spec.branches:
            if not branch.overflow_stub:
                continue
            for part in branch.parts:
                for pin in getattr(part, "pins", []):
                    net = getattr(pin, "net", None)
                    if net is None:
                        continue
                    net._stub = True
                    net.stub = True
                    net._fork_overflow_stub = True
                    for p in net.get_pins():
                        p.stub = True
