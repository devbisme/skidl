# -*- coding: utf-8 -*-

"""
generic driver 专用：rail 规划、主链布局、预布线保留网与识别/布局实现。
"""

import os
import re
from collections import defaultdict

from skidl.geometry import BBox, Point, Tx
from skidl.schematics.trunk_layout import (
    _place_parts_in_column,
    _place_parts_in_row,
    _resolve_overlaps,
    _set_part_center_x_safe,
    allow_anonymous_input_rail_promotion,
)
from . import common as _common

# 与单文件时同一命名空间：common 中的私有 helper 也需对 driver 可见
for _name, _val in _common.__dict__.items():
    if _name.startswith("__"):
        continue
    globals()[_name] = _val
del _name, _val, _common

def _score_driver_rail_candidate(net, node, main_part, part_set):
    """Score top/bottom/control rail candidacy with reasons for debug logging."""
    net_name = _net_label(net).upper()
    net_parts = node._net_connected_parts(net, allowed_parts=part_set)
    pin_names = (
        _pins_on_part_for_net(node, main_part, net, part_set) if main_part is not None else []
    )
    categories = _classify_net_semantic(net, main_part, node, part_set, None)
    refs = [str(getattr(part, "ref", "") or "").upper() for part in net_parts]

    top_score = 0
    bottom_score = 0
    control_score = 0
    reasons = []
    token_hits = []

    top_hits = _matched_tokens(net_name, _TOP_RAIL_TOKENS)
    bottom_hits = _matched_tokens(net_name, _BOTTOM_RAIL_TOKENS)
    control_hits = _matched_tokens(net_name, _CONTROL_TOKENS)
    pin_input_hits = []
    pin_ground_hits = []
    pin_control_hits = []

    for pname in pin_names:
        pin_input_hits.extend(_matched_tokens(pname, _INPUT_TOKENS))
        pin_ground_hits.extend(_matched_tokens(pname, _GROUND_TOKENS))
        pin_control_hits.extend(_matched_tokens(pname, _CONTROL_TOKENS))

    if top_hits:
        top_score += 4 + len(top_hits)
        token_hits.extend("token:%s" % token for token in top_hits)
        reasons.extend("token:%s" % token for token in top_hits)
    if bottom_hits:
        bottom_score += 4 + len(bottom_hits)
        token_hits.extend("token:%s" % token for token in bottom_hits)
        reasons.extend("token:%s" % token for token in bottom_hits)
    if control_hits:
        control_score += 3 + len(control_hits)
        reasons.extend("token:%s" % token for token in control_hits)

    if pin_input_hits:
        top_score += 4
        reasons.append("main_pin:%s" % pin_input_hits[0])
    if pin_ground_hits:
        bottom_score += 4
        reasons.append("main_pin:%s" % pin_ground_hits[0])
    if pin_control_hits:
        control_score += 2
        reasons.append("main_pin:%s" % pin_control_hits[0])

    if "input" in categories:
        top_score += 2
        reasons.append("semantic:input")
    if "ground" in categories:
        bottom_score += 2
        reasons.append("semantic:ground")
    if "control" in categories:
        control_score += 2
        reasons.append("semantic:control")
    if "switch" in categories:
        control_score += 1
        reasons.append("semantic:switch")

    fanout = len(net_parts)
    fanout_bonus = 0
    if fanout >= 4:
        fanout_bonus = 3
    elif fanout >= 3:
        fanout_bonus = 2
    elif fanout >= 2:
        fanout_bonus = 1
    if fanout_bonus:
        if top_score > 0:
            top_score += fanout_bonus
        if bottom_score > 0:
            bottom_score += fanout_bonus
        if control_score > 0:
            control_score += 1
        reasons.append("fanout>=%d" % fanout)

    if main_part in net_parts:
        if top_score > 0:
            top_score += 2
        if bottom_score > 0:
            bottom_score += 2
        if control_score > 0:
            control_score += 1
        reasons.append("connected_to_ic")

    if top_score > 0:
        if any(ref.startswith("C") for ref in refs):
            top_score += 2
            reasons.append("input_cap")
        if any(ref.startswith(("J", "P", "CN")) for ref in refs):
            top_score += 1
            reasons.append("input_connector")
        if any(ref.startswith("D") for ref in refs):
            top_score += 1
            reasons.append("input_diode")
        if any(ref.startswith("L") for ref in refs):
            top_score += 1
            reasons.append("inductor_near")

    direction = None
    final_score = 0
    if bottom_score >= max(top_score, control_score) and bottom_score > 0:
        direction = "bottom"
        final_score = bottom_score
    elif top_score >= max(bottom_score, control_score) and top_score > 0:
        direction = "top"
        final_score = top_score
    elif control_score > 0:
        direction = "control"
        final_score = control_score

    return {
        "net": net,
        "name": net_name,
        "direction": direction,
        "score": final_score,
        "top_score": top_score,
        "bottom_score": bottom_score,
        "control_score": control_score,
        "fanout": fanout,
        "reasons": reasons,
        "token_hits": token_hits,
        "categories": sorted(categories),
    }



def _is_anonymous_net(net):
    """内部匿名网 Net-(...) 不参与 rail 规划/预布线。"""
    name = _net_label(net).strip().upper()
    return name.startswith("NET-(") or name.startswith("NET_(")


def _is_rail_label_net(net):
    """具名网才进入 top/bottom rail 候选。"""
    if _is_anonymous_net(net):
        return False
    return bool(_net_label(net).strip())


def _dedupe_nets(nets):
    seen = set()
    out = []
    for net in nets:
        if net in seen:
            continue
        seen.add(net)
        out.append(net)
    return out


def _collect_driver_rail_nets(nets, topology, node, main_part, part_set):
    """
    从 topology 桶 + 网名/pin 语义收集 top/bottom/control rail 网表。
    control/switch 不进长水平 rail。
    """
    top = []
    bottom = []
    control = list(topology.get("control_nets", []))
    control_ids = {id(n) for n in control}
    switch_ids = {id(n) for n in topology.get("switch_or_drive_nets", [])}
    rail_debug = {}

    for net in nets:
        name = _net_label(net).upper()
        cats = sorted(_classify_net_semantic(net, main_part, node, part_set, None))
        if id(net) in switch_ids:
            rail_debug[name] = {
                "net": net,
                "name": name,
                "direction": None,
                "selected_direction": None,
                "rejected_reason": "switch_or_drive_net",
                "score": 0,
                "top_score": 0,
                "bottom_score": 0,
                "control_score": 0,
                "fanout": len(node._net_connected_parts(net, allowed_parts=part_set)),
                "reasons": [],
                "token_hits": [],
                "categories": cats,
            }
            _topology_debug_log(
                getattr(node, "_schematic_debug_options", {}),
                "rail_candidate",
                "net=%s fanout=%s semantic_types=%s score=%s matched_tokens=%s selected_direction=%s rejected_reason=%s"
                % (
                    name or "<anon>",
                    rail_debug[name]["fanout"],
                    cats,
                    0,
                    [],
                    None,
                    "switch_or_drive_net",
                ),
            )
            continue
        meta = _score_driver_rail_candidate(net, node, main_part, part_set)
        meta["selected_direction"] = None
        meta["rejected_reason"] = "unclassified"
        rail_debug[name] = meta
        _topology_debug_log(
            getattr(node, "_schematic_debug_options", {}),
            "rail_candidate",
            "net=%s fanout=%s semantic_types=%s score=%s matched_tokens=%s selected_direction=%s rejected_reason=%s reasons=%s"
            % (
                name or "<anon>",
                meta.get("fanout", 0),
                meta.get("categories", []),
                meta.get("score", 0),
                meta.get("token_hits", []),
                meta.get("selected_direction"),
                meta.get("rejected_reason"),
                meta.get("reasons", []),
            ),
        )
        _topology_debug_log(
            getattr(node, "_schematic_debug_options", {}),
            "rail_score",
            "net=%s top=%s bottom=%s control=%s fanout=%s token_matched=%s"
            % (
                name or "<anon>",
                meta.get("top_score", 0),
                meta.get("bottom_score", 0),
                meta.get("control_score", 0),
                meta.get("fanout", 0),
                meta.get("token_hits", []),
            ),
        )

        anonymous_promoted = False
        if _is_anonymous_net(net):
            anonymous_promoted = allow_anonymous_input_rail_promotion(
                name,
                meta.get("direction"),
                meta.get("categories", []),
                meta.get("reasons", []),
                meta.get("fanout", 0),
            )
            if not anonymous_promoted:
                meta["rejected_reason"] = "anonymous_or_blank"
                continue
            _topology_debug_log(
                getattr(node, "_schematic_debug_options", {}),
                "rail_promoted",
                "net=%s semantic=input reasons=%s"
                % (name or "<anon>", meta.get("reasons", [])),
            )

        if id(net) in control_ids or "control" in cats or _token_in_text(
            name, _CONTROL_TOKENS
        ):
            if net not in control:
                control.append(net)
            meta["direction"] = "control"
            meta["selected_direction"] = "control"
            meta["rejected_reason"] = ""
            continue
        if "switch" in cats or _token_in_text(name, _SWITCH_TOKENS):
            meta["rejected_reason"] = "switch_semantic"
            continue

        if meta.get("direction") == "bottom" and meta.get("score", 0) > 0:
            bottom.append(net)
            meta["selected_direction"] = "bottom"
            meta["rejected_reason"] = ""
            continue
        if meta.get("direction") == "top" and meta.get("score", 0) > 0:
            top.append(net)
            meta["selected_direction"] = "top"
            meta["rejected_reason"] = ""
            continue
        if net in topology.get("ground_nets", []):
            bottom.append(net)
            meta["selected_direction"] = "bottom"
            meta["rejected_reason"] = "fallback_ground_bucket"
        elif net in topology.get("input_nets", []) or net in topology.get(
            "power_nets", []
        ):
            top.append(net)
            meta["selected_direction"] = "top"
            meta["rejected_reason"] = "fallback_input_bucket"
        elif net in topology.get("output_nets", []):
            if _token_in_text(name, ("LED+", "W+", "LED", "OUT+")):
                top.append(net)
                meta["selected_direction"] = "top"
                meta["rejected_reason"] = "fallback_output_positive_bucket"
            elif _token_in_text(name, ("LED-", "W-")):
                bottom.append(net)
                meta["selected_direction"] = "bottom"
                meta["rejected_reason"] = "fallback_output_negative_bucket"
            else:
                meta["rejected_reason"] = "output_without_rail_token"
        else:
            meta["rejected_reason"] = meta.get("rejected_reason") or "score_zero_or_not_bucketed"

    top = _dedupe_nets(top)
    bottom = _dedupe_nets(bottom)
    control = _dedupe_nets(control)
    topology["rail_debug"] = rail_debug
    for meta in rail_debug.values():
        if meta.get("selected_direction"):
            continue
        _topology_debug_log(
            getattr(node, "_schematic_debug_options", {}),
            "rail_rejected",
            "net=%s fanout=%s semantic_types=%s score=%s matched_tokens=%s selected_direction=%s rejected_reason=%s"
            % (
                meta.get("name") or "<anon>",
                meta.get("fanout", 0),
                meta.get("categories", []),
                meta.get("score", 0),
                meta.get("token_hits", []),
                meta.get("selected_direction"),
                meta.get("rejected_reason") or "unknown",
            ),
        )
    for side, selected in (("top", top), ("bottom", bottom), ("control", control)):
        for net in selected:
            meta = rail_debug.get(_net_label(net).upper(), {})
            _topology_debug_log(
                getattr(node, "_schematic_debug_options", {}),
                "rail_selected",
                "net=%s score=%s reasons=%s token_matched=%s fanout=%s final_direction=%s"
                % (
                    _net_label(net).upper() or "<anon>",
                    meta.get("score", 0),
                    meta.get("reasons", []),
                    meta.get("token_hits", []),
                    meta.get("fanout", 0),
                    side,
                ),
            )

    return top, bottom, control


def _union_placed_bbox(parts):
    """合并已放置 real parts 的 place_bbox。"""
    bb = BBox(Point(0, 0), Point(0, 0))
    any_part = False
    for part in parts:
        if getattr(part, "place_bbox", None) is None or getattr(part, "tx", None) is None:
            continue
        bb.add(part.place_bbox * part.tx)
        any_part = True
    if not any_part:
        return None
    return bb


def _part_visual_bbox(part):
    """原理图可见外框：lbl_bbox 优先，避免 place_bbox 布线膨胀把 rail 甩远。"""
    tx = getattr(part, "tx", None)
    if tx is None:
        return None
    lbl = getattr(part, "lbl_bbox", None)
    if lbl is not None:
        return lbl * tx
    place = getattr(part, "place_bbox", None)
    if place is not None:
        return place * tx
    return None


def _union_visual_bbox(parts):
    """合并已放置器件的可见外框，供 driver rail 顶/底 Y 与走廊计算。"""
    bb = BBox(Point(0, 0), Point(0, 0))
    any_part = False
    for part in parts:
        vis = _part_visual_bbox(part)
        if vis is None:
            continue
        bb.add(vis)
        any_part = True
    if not any_part:
        return None
    return bb


def _layout_bbox(part):
    """driver 分区/主链布局用的外框：可见符号框，不用 place 布线膨胀。"""
    vis = _part_visual_bbox(part)
    if vis is not None:
        return vis
    if getattr(part, "place_bbox", None) is not None and getattr(part, "tx", None) is not None:
        return part.place_bbox * part.tx
    return None


def _part_layout_h(part, grid):
    bb = _layout_bbox(part)
    return max(bb.h if bb is not None else 0, grid)


def _rail_corridor_intersects_bbox(bb, rail_y, x_min, x_max, grid, side="top"):
    """水平 rail 走廊（宽 GRID）是否与器件可见/放置框相交。"""
    if x_max < bb.min.x or x_min > bb.max.x:
        return False
    if side == "top":
        band_lo, band_hi = rail_y, rail_y + grid
    else:
        band_lo, band_hi = rail_y - grid, rail_y
    return not (bb.max.y < band_lo or bb.min.y > band_hi)


def _driver_chain_pin_y_span(node):
    """主功率链引脚 Y 范围（Y 向上）；无链时返回 None。"""
    row_parts = set(getattr(node, "_driver_chain_parts", set()) or [])
    if not row_parts:
        return None
    ys = []
    for part in row_parts:
        tx = getattr(part, "tx", None)
        if tx is None:
            continue
        for pin in getattr(part, "pins", []):
            if getattr(pin, "stub", False):
                continue
            if not pin.is_connected():
                continue
            ys.append((pin.pt * tx).y)
    if not ys:
        return None
    return min(ys), max(ys)


def _driver_rail_attachment_points(node, net, allowed_parts=None):
    """Collect actual driver rail attachment points from connected, placed pins."""
    from skidl.schematics.place import is_net_terminal

    pts = []
    allowed = set(allowed_parts) if allowed_parts is not None else None
    for pin in getattr(net, "pins", []):
        part = getattr(pin, "part", None)
        if part is None or is_net_terminal(part):
            continue
        if allowed is not None and part not in allowed:
            continue
        tx = getattr(part, "tx", None)
        pt = getattr(pin, "pt", None)
        if tx is None or pt is None:
            continue
        pts.append((pt * tx).round())
    return pts


def _driver_rail_span_from_points(points, grid, fallback_min, fallback_max, margin_grids=1):
    """Derive a conservative horizontal rail span from actual attachment points."""
    if not points:
        return fallback_min, fallback_max

    margin = max(int(margin_grids), 0) * grid
    x_min = Point(min(pt.x for pt in points), 0).snap(grid).x - margin
    x_max = Point(max(pt.x for pt in points), 0).snap(grid).x + margin
    if x_min > x_max:
        return fallback_min, fallback_max
    return x_min, x_max


def _clamp_rail_y_to_driver_chain(node, top_y, bottom_y, grid, rail_margin):
    """
    把顶/底 rail 限制在主链引脚附近，避免 union/place 离群框把 rail 甩到页底。
    """
    span = _driver_chain_pin_y_span(node)
    if span is None:
        return top_y, bottom_y
    row_lo, row_hi = span
    band = max(rail_margin, 3 * grid)
    top_y = max(top_y, row_lo - band)
    bottom_y = min(bottom_y, row_hi + band)
    return top_y, bottom_y


def _find_clear_rail_y(node, parts, rail_y, x_min, x_max, grid, side, max_tries=5):
    """若走廊压到器件可见框，沿外侧逐格偏移 rail_y（最多 5 次）。"""
    for _ in range(max_tries):
        blocked = False
        for part in parts:
            bb = _part_visual_bbox(part)
            if bb is None:
                continue
            if _rail_corridor_intersects_bbox(bb, rail_y, x_min, x_max, grid, side):
                blocked = True
                break
        if not blocked:
            return rail_y
        if side == "top":
            rail_y -= grid
        else:
            rail_y += grid
    return rail_y


def build_driver_rail_plan(node, parts, nets, topology, main_part, **options):
    """
    generic_driver 且 fallback=False 时生成水平 rail 计划。
    结果供 route.py 预布线与布局走廊校验使用。
    """
    disabled = {
        "enabled": False,
        "top_nets": [],
        "bottom_nets": [],
        "control_nets": [],
        "top_y": 0,
        "bottom_y": 0,
        "x_min": 0,
        "x_max": 0,
    }
    if topology.get("kind") != "generic_driver" or topology.get("fallback") is not False:
        return disabled
    if not options.get("human_readable", False):
        return disabled
    if not options.get("driver_rail_routing", True):
        return disabled
    node._schematic_debug_options = options

    grid = int(options.get("grid", 100))
    rail_margin = 2 * grid
    part_set = set(parts)
    top_nets, bottom_nets, control_nets = _collect_driver_rail_nets(
        nets, topology, node, main_part, part_set
    )
    if not top_nets and not bottom_nets:
        return disabled

    real_parts = [
        p
        for p in parts
        if getattr(p, "place_bbox", None) is not None and getattr(p, "tx", None) is not None
    ]
    union = _union_visual_bbox(real_parts)
    if union is None:
        return disabled

    x_min = Point(union.min.x, 0).snap(grid).x - grid
    x_max = Point(union.max.x, 0).snap(grid).x + grid
    top_y = Point(0, union.min.y).snap(grid).y - rail_margin
    bottom_y = Point(0, union.max.y).snap(grid).y + rail_margin

    top_y = _find_clear_rail_y(
        node, real_parts, top_y, x_min, x_max, grid, side="top"
    )
    bottom_y = _find_clear_rail_y(
        node, real_parts, bottom_y, x_min, x_max, grid, side="bottom"
    )
    top_y, bottom_y = _clamp_rail_y_to_driver_chain(
        node, top_y, bottom_y, grid, rail_margin
    )

    real_part_set = set(real_parts)
    rail_spans = {}
    for net in top_nets + bottom_nets:
        rail_spans[net] = _driver_rail_span_from_points(
            _driver_rail_attachment_points(node, net, allowed_parts=real_part_set),
            grid,
            x_min,
            x_max,
        )

    return {
        "enabled": True,
        "top_nets": top_nets,
        "bottom_nets": bottom_nets,
        "control_nets": control_nets,
        "topology": topology,
        "top_y": top_y,
        "bottom_y": bottom_y,
        "x_min": x_min,
        "x_max": x_max,
        "rail_spans": rail_spans,
        "grid": grid,
    }


def _log_driver_rails(plan, options):
    if not options.get("schematic_progress", False) or not plan.get("enabled"):
        return
    from skidl.logger import active_logger

    top_names = [_net_label(n) for n in plan.get("top_nets", [])]
    bottom_names = [_net_label(n) for n in plan.get("bottom_nets", [])]
    active_logger.info(
        "[schematic] driver rails: top=%s, bottom=%s, top_y=%s, bottom_y=%s, x=(%s, %s)"
        % (
            top_names,
            bottom_names,
            plan.get("top_y"),
            plan.get("bottom_y"),
            plan.get("x_min"),
            plan.get("x_max"),
        )
    )
    rail_debug = (plan.get("topology") or {}).get("rail_debug", {})
    for side in ("top", "bottom"):
        for net in plan.get("%s_nets" % side, []):
            meta = rail_debug.get(_net_label(net).upper(), {})
            if not meta:
                continue
            _topology_debug_log(
                options,
                "rail_selected",
                "net=%s score=%s reasons=%s token_matched=%s fanout=%s final_direction=%s"
                % (
                    meta.get("name") or "<anon>",
                    meta.get("score", 0),
                    meta.get("reasons", []),
                    meta.get("token_hits", []),
                    meta.get("fanout", 0),
                    side,
                ),
            )


def _log_rail_blockers(node, parts, plan, options):
    """若 place_bbox 仍与 rail 走廊相交，输出 blocker 便于调试。"""
    if not options.get("schematic_progress", False) or not plan.get("enabled"):
        return
    from skidl.logger import active_logger

    grid = plan.get("grid", 100)
    x_min = plan["x_min"]
    x_max = plan["x_max"]
    for side, rail_y in (("top", plan["top_y"]), ("bottom", plan["bottom_y"])):
        for part in parts:
            bb = _part_visual_bbox(part)
            if bb is None:
                continue
            if _rail_corridor_intersects_bbox(bb, rail_y, x_min, x_max, grid, side):
                active_logger.info(
                    "[schematic] driver rail blocker: ref=%s bbox=%s rail=%s"
                    % (getattr(part, "ref", ""), bb, side)
                )


def _part_on_net_set(part, net_set):
    for pin in getattr(part, "pins", []):
        if getattr(pin, "net", None) in net_set:
            return True
    return False


def _chain_row_satellite_parts(node, parts, chain_parts, nets, topology=None):
    """
    与主链器件共网、但不在 chain 内的 R/C（如 R1、输入侧小电容），
    应排在主链同一水平行，避免 switch 网被 switchbox 绕外围。
    """
    chain_set = set(chain_parts)
    part_set = set(parts)
    reserved = set()
    if topology:
        reserved |= set(topology.get("sense_feedback_parts", set()) or [])
        reserved |= set(topology.get("control_parts", set()) or [])
    satellites = []
    for net in nets:
        connected = node._net_connected_parts(net, allowed_parts=part_set)
        if not connected or not chain_set.intersection(connected):
            continue
        for part in connected:
            if part in chain_set or part in reserved:
                continue
            if _part_ref_prefix(part) not in ("R", "C"):
                continue
            if part not in satellites:
                satellites.append(part)
    return sorted(satellites, key=node._part_ref_key)


def _insert_satellites_into_row(node, chain, satellites, nets):
    """把 satellite 插到与其共网的 chain 器件右侧，保持阅读顺序。"""
    row = list(chain)
    known = set(row)
    for sat in satellites:
        insert_at = None
        for idx, cp in enumerate(row):
            for net in nets:
                con = set(
                    node._net_connected_parts(net, allowed_parts=known | {sat})
                )
                if sat in con and cp in con:
                    if insert_at is None:
                        insert_at = idx + 1
                    else:
                        insert_at = min(insert_at, idx + 1)
        if insert_at is None:
            insert_at = len(row)
        row.insert(insert_at, sat)
        known.add(sat)
    return row


def _led_rail_decoupling_caps(parts, top_set, bottom_set, chain_parts):
    """LED+/LED- 去耦电容：不放进主链行，改贴主控两侧（两 rail 之间）。"""
    caps = []
    for part in parts:
        if part in chain_parts or _part_ref_prefix(part) != "C":
            continue
        on_top = _part_on_net_set(part, top_set)
        on_bot = _part_on_net_set(part, bottom_set)
        if on_top or on_bot:
            caps.append(part)
    return caps


def apply_driver_rail_safe_placement(
    node, parts, nets, roles, main_part, topology, chain, chain_parts, **options
):
    """
    rail 安全后处理：主链居中于 top/bottom 走廊之间；
    顶/底网器件不压在 rail_y 上，控制支路留在中部侧边。
    """
    grid = int(options.get("grid", 100))
    gap = options.get("topology_gap") or options.get(
        "trunk_gap", max(int(options.get("blk_int_pad", 100)), grid * 2)
    )
    blk_pad = int(options.get("blk_int_pad", 100))
    part_set = set(parts)

    real_parts = [
        p
        for p in parts
        if getattr(p, "place_bbox", None) is not None and getattr(p, "tx", None) is not None
    ]
    union = _union_visual_bbox(real_parts)
    if union is None:
        return

    top_y = Point(0, union.min.y).snap(grid).y - 2 * grid
    bottom_y = Point(0, union.max.y).snap(grid).y + 2 * grid
    mid_y = Point(0, (top_y + bottom_y) / 2).snap(grid).y

    top_nets, bottom_nets, _control = _collect_driver_rail_nets(
        nets, topology, node, main_part, part_set
    )
    top_set = set(top_nets)
    bottom_set = set(bottom_nets)

    satellites = _chain_row_satellite_parts(node, parts, chain_parts, nets, topology)
    row = _insert_satellites_into_row(node, chain, satellites, nets)
    row_parts = set(row)

    # 主功率链 + 同行卫星件：水平居中，不占用顶/底 rail 线。
    if row:
        start_x = _chain_row_start_x(node, chain, main_part, gap, grid)
        _place_parts_in_row(node, row, start_x, mid_y, gap, grid)

    node._driver_chain_parts = row_parts

    def _nudge_y(part, target_cy):
        ctr = node._placement_ctr(part)
        snapped = Point(ctr.x, target_cy).snap(grid)
        dy = snapped.y - ctr.y
        if dy:
            part.tx *= Tx(dx=0, dy=dy)

    decoup_caps = _led_rail_decoupling_caps(parts, top_set, bottom_set, row_parts)

    for part in parts:
        if (
            part in row_parts
            or part is main_part
            or part in decoup_caps
            or part in topology.get("sense_feedback_parts", set())
            or part in topology.get("control_parts", set())
        ):
            continue
        h = _part_layout_h(part, grid)
        if _part_on_net_set(part, top_set) and not _part_on_net_set(part, bottom_set):
            _nudge_y(part, top_y + grid + h / 2)
        elif _part_on_net_set(part, bottom_set) and not _part_on_net_set(part, top_set):
            _nudge_y(part, bottom_y - grid - h / 2)

    sense_parts = sorted(
        [p for p in topology.get("sense_feedback_parts", set()) if p not in chain_parts],
        key=node._part_ref_key,
    )
    if sense_parts:
        main_vis = _layout_bbox(main_part)
        if main_vis is None:
            main_vis = main_part.place_bbox * main_part.tx
        sense_x = main_vis.max.x + gap
        sense_y = mid_y + gap
        _place_parts_in_row(node, sense_parts, sense_x, sense_y, gap, grid)

    # 控制支路：主控右侧中部，避免拉到顶/底 rail。
    control_parts = sorted(
        [p for p in topology.get("control_parts", set()) if p not in chain_parts],
        key=node._part_ref_key,
    )
    if control_parts:
        main_vis = _layout_bbox(main_part)
        if main_vis is None:
            main_vis = main_part.place_bbox * main_part.tx
        ctrl_width = _row_total_width(control_parts, gap, grid)
        ctrl_x = main_vis.min.x - ctrl_width
        ctrl_y = main_vis.max.y + gap * 2
        _place_parts_in_row(node, control_parts, ctrl_x, ctrl_y, gap, grid)

    # LED+/LED- 去耦：贴在主控右侧、两 rail 之间竖排，避免甩到图纸底部。
    if decoup_caps:
        main_vis = _layout_bbox(main_part)
        if main_vis is None:
            main_vis = main_part.place_bbox * main_part.tx
        cx = main_vis.max.x + gap * 2
        y_cursor = top_y + grid
        for cap in sorted(decoup_caps, key=node._part_ref_key):
            h = _part_layout_h(cap, grid)
            _nudge_y(cap, y_cursor + h / 2)
            ctr = node._placement_ctr(cap)
            snapped_x = Point(cx, ctr.y).snap(grid).x
            dx = snapped_x - ctr.x
            if dx:
                cap.tx *= Tx(dx=dx, dy=0)
            y_cursor += h + gap

    _resolve_overlaps(node, parts, grid, max(gap, blk_pad), exclude=row_parts)


def driver_wire_preserve_net_set(node, nets=None, **options):
    """
    generic_driver + driver_rail_routing 时应保留物理导线的网表。
    含 rail 顶/底网、主链行内网（含 Net-(D1-*) 等匿名网）。
    """
    if not options.get("driver_rail_routing", True):
        return set()
    if not options.get("human_readable", False):
        return set()
    topology = getattr(node, "_last_topology_result", None) or {}
    if topology.get("kind") != "generic_driver" or topology.get("fallback") is not False:
        return set()

    plan = getattr(node, "_driver_rail_plan", None) or {}
    preserve = set(plan.get("top_nets", [])) | set(plan.get("bottom_nets", []))

    row_parts = set(getattr(node, "_driver_chain_parts", set()) or [])
    if nets and row_parts:
        from skidl.schematics.place import is_net_terminal

        for net in nets:
            pins = [
                p
                for p in net.pins
                if p.part in node.parts and not is_net_terminal(p.part)
            ]
            if len(pins) < 2:
                continue
            if {p.part for p in pins}.issubset(row_parts):
                preserve.add(net)
    return preserve


def restore_driver_wire_nets(node, nets=None, **options):
    """取消 driver 保留网的 stub，使预布线与 KiCad wire 能写出。"""
    if nets is None:
        nets = node.get_internal_nets()
    preserve = driver_wire_preserve_net_set(node, nets, **options)
    if preserve:
        _attach_debug_log(
            options,
            "restore_driver_wire_nets sheet=%s preserve=%s"
            % (getattr(node, "name", "?"), [_net_label(net) for net in preserve]),
        )
    for net in preserve:
        net._stub = False
        for pin in net.pins:
            if pin.part in node.parts:
                pin.stub = False
    return preserve


def restore_driver_wire_nets_deep(node, **options):
    """递归子页恢复 driver 保留网的 wire 模式。"""
    for child in node.children.values():
        restore_driver_wire_nets_deep(child, **options)
    restore_driver_wire_nets(node, **options)


def detect_generic_driver_topology(
    node, parts, nets, roles, main_part, trunk_map=None, adjacency=None, **options
):
    """打分识别 generic driver，返回完整 topology dict。"""
    topo_opts = _topology_options(options)
    part_set = set(parts)
    if adjacency is None:
        from skidl.schematics.trunk_layout import build_part_adjacency

        adjacency = build_part_adjacency(parts, nets)

    candidates = _candidate_ic_parts(parts, roles)
    if not candidates:
        return _empty_topology(
            "unrecognized", 0, main_part=main_part, reasons=["no_ic_candidate"]
        )

    best = None
    best_conf = -1
    best_score = 0
    best_reasons = []
    best_combo = False

    for cand in candidates:
        sc, conf, reasons, combo, _flags = _score_candidate_ic(
            node, cand, parts, nets, roles, part_set, adjacency
        )
        if conf > best_conf or (conf == best_conf and sc > best_score):
            best = cand
            best_conf = conf
            best_score = sc
            best_reasons = reasons
            best_combo = combo

    strong_th = topo_opts["strong_threshold"]
    weak_th = topo_opts["weak_threshold"]

    if not best_combo or best_conf < weak_th:
        kind = "unrecognized"
        fallback = "trunk_aware"
    elif best_conf < strong_th:
        kind = "weak_generic_driver"
        fallback = "trunk_aware"
    else:
        kind = "generic_driver"
        fallback = False

    topology = _empty_topology(kind, best_conf, main_part=best, reasons=best_reasons, fallback=fallback)
    if kind == "unrecognized":
        return topology

    net_buckets = _build_net_lists(node, best, parts, nets, part_set, adjacency)
    for key, val in net_buckets.items():
        topology[key] = val

    _assign_topology_part_groups(node, parts, roles, topology, part_set)
    return topology


def apply_generic_driver_layout(
    node, parts, roles, main_part, topology, trunk_map, nets=None, **options
):
    """
    generic driver 布局：支路先分区，最后强制主功率链水平横排。
    主链器件不参与末尾去重叠，避免被垂直推开。
    """
    if not parts or main_part is None:
        return

    grid = options.get("grid", 100)
    blk_pad = int(options.get("blk_int_pad", 100))
    gap = options.get("topology_gap") or options.get(
        "trunk_gap", max(blk_pad, grid * 2)
    )

    main_bbox = _layout_bbox(main_part)
    if main_bbox is None:
        return
    main_ctr = node._placement_ctr(main_part)
    chain, chain_parts = _build_driver_chain_order(
        node, roles, topology, main_part
    )

    moved_count = 0
    attempt_count = 1

    use_rail = options.get("driver_rail_routing", True) and options.get(
        "human_readable", False
    )

    # 非主链输出滤波电容：放在主链上方一小行（rail 模式下去耦改由 rail_safe 处理）。
    aux_output = sorted(
        [
            p
            for p in topology.get("output_parts", set())
            if p not in chain_parts and _part_ref_prefix(p) == "C"
        ],
        key=node._part_ref_key,
    )
    if aux_output and not use_rail:
        top_y = main_bbox.min.y - gap - max(_part_layout_h(p, grid) for p in aux_output)
        _place_parts_in_row(
            node,
            aux_output,
            main_bbox.min.x,
            top_y,
            gap,
            grid,
        )
        moved_count += len(aux_output)

    # 控制支路：放在主控正下方横排，避免拉到最右侧形成超长回路线。
    control_parts = sorted(
        [p for p in topology.get("control_parts", set()) if p not in chain_parts],
        key=node._part_ref_key,
    )
    if control_parts and not use_rail:
        ctrl_y = main_bbox.max.y + gap
        _place_parts_in_row(
            node,
            control_parts,
            main_bbox.min.x,
            ctrl_y,
            gap,
            grid,
        )
        moved_count += len(control_parts)

    # 反馈采样电阻等：贴近主控上方。
    sense_parts = sorted(
        [p for p in topology.get("sense_feedback_parts", set()) if p not in chain_parts],
        key=node._part_ref_key,
    )
    if sense_parts:
        max_h = max(_part_layout_h(p, grid) for p in sense_parts)
        sense_y = main_bbox.min.y - gap - max_h
        _place_parts_in_row(
            node,
            sense_parts,
            main_bbox.max.x + gap,
            sense_y,
            gap,
            grid,
        )
        moved_count += len(sense_parts)

    # 其余输入/功率器件：轻量靠左或靠下，不抢主链位置。
    left_x = main_bbox.min.x - (3 * gap)
    for part in sorted(topology.get("input_parts", set()), key=node._part_ref_key):
        if part in chain_parts:
            continue
        attempt_count += 1
        _set_part_center_x_safe(node, part, parts, left_x, grid)

    bottom_y = main_bbox.max.y + (3 * gap)
    for part in sorted(topology.get("power_loop_parts", set()), key=node._part_ref_key):
        if part in chain_parts:
            continue
        attempt_count += 1
        node._set_part_center_y_safe(part, parts, bottom_y)

    # 最后放置主功率链：直接横排，覆盖此前对齐造成的错位。
    if len(chain) >= 2:
        chain_y = main_bbox.min.y
        start_x = _chain_row_start_x(node, chain, main_part, gap, grid)
        _place_parts_in_row(node, chain, start_x, chain_y, gap, grid)
        moved_count += len(chain)

    _resolve_overlaps(node, parts, grid, max(gap, blk_pad), exclude=chain_parts)

    if attempt_count > 0 and moved_count == 0:
        topology["fallback"] = "trunk_aware"
        topology["reasons"] = list(topology.get("reasons", [])) + ["layout_safety"]
    else:
        topology["fallback"] = False
        if (
            options.get("driver_rail_routing", True)
            and options.get("human_readable", False)
            and nets
        ):
            if options.get("schematic_progress", False):
                from skidl.logger import active_logger

                active_logger.info("[schematic] driver rail placement ...")
            apply_driver_rail_safe_placement(
                node,
                parts,
                nets,
                roles,
                main_part,
                topology,
                chain,
                chain_parts,
                **options,
            )
            plan = build_driver_rail_plan(
                node, parts, nets, topology, main_part, **options
            )
            node._driver_rail_plan = plan
            node._driver_chain_parts = getattr(node, "_driver_chain_parts", chain_parts)
            _log_driver_rails(plan, options)
            _log_rail_blockers(node, parts, plan, options)


def topology_route_rank_bias(net, topology):
    """
    generic_driver / mcu matched 时的布线顺序偏置（保守，不改变拓扑）。
    返回值越小越先布。
    """
    if not topology:
        return 0
    kind = topology.get("kind")
    if kind == "mcu":
        from .mcu import mcu_route_rank_bias

        return mcu_route_rank_bias(net, topology)
    if kind != "generic_driver":
        return 0

    name = _net_label(net).upper()
    net_obj = net

    def in_bucket(key):
        for n in topology.get(key, []):
            if n is net_obj:
                return True
        return False

    if in_bucket("input_nets") or in_bucket("power_nets"):
        return -600
    if in_bucket("output_nets"):
        return -550
    if in_bucket("ground_nets"):
        return -500
    if in_bucket("control_nets"):
        return -200
    if in_bucket("switch_or_drive_nets"):
        # 开关网不做长 trunk，局部优先但弱于电源/输出
        return -80
    if in_bucket("sense_or_feedback_nets"):
        return -150

    # 未入 topology 桶的具名网：不用 trunk 对 SW 的 right 主干误导
    if _token_in_text(name, _SWITCH_TOKENS):
        return -50
    return 0


def format_topology_log_line(topology):
    """单行中文拓扑识别结果（便于在日志末尾快速阅读）。"""
    kind = topology.get("kind", "unrecognized")
    conf = topology.get("confidence", 0)
    fb = topology.get("fallback", "trunk_aware")
    mp = topology.get("main_part")
    main_ref = str(getattr(mp, "ref", "") or "") if mp is not None else ""

    if kind == "disabled":
        return "[schematic] 拓扑识别：未启用拓扑识别，使用常规布局。"

    if kind == "mcu" and fb is False:
        if main_ref:
            return (
                f"[schematic] 拓扑识别：已识别为 MCU 模块（主控 {main_ref}），"
                "已启用专用布局。"
            )
        return "[schematic] 拓扑识别：已识别为 MCU 模块，已启用专用布局。"

    if kind == "mcu":
        if main_ref:
            return (
                f"[schematic] 拓扑识别：已识别为 MCU 模块（主控 {main_ref}），"
                "专用布局未生效，使用常规布局。"
            )
        return "[schematic] 拓扑识别：已识别为 MCU 模块，专用布局未生效，使用常规布局。"

    if kind == "weak_mcu":
        if main_ref:
            return (
                f"[schematic] 拓扑识别：疑似 MCU 模块（主控 {main_ref}，"
                f"置信度 {conf}），使用常规布局。"
            )
        return f"[schematic] 拓扑识别：疑似 MCU 模块（置信度 {conf}），使用常规布局。"

    if kind == "generic_driver" and fb is False:
        if main_ref:
            return f"[schematic] 拓扑识别：已识别为 driver 模块（主控 {main_ref}），已启用专用布局。"
        return "[schematic] 拓扑识别：已识别为 driver 模块，已启用专用布局。"

    if kind == "generic_driver":
        if main_ref:
            return f"[schematic] 拓扑识别：已识别为 driver 模块（主控 {main_ref}），专用布局未生效，使用常规布局。"
        return "[schematic] 拓扑识别：已识别为 driver 模块，专用布局未生效，使用常规布局。"

    if kind == "weak_generic_driver":
        if main_ref:
            return (
                f"[schematic] 拓扑识别：疑似 driver 模块（主控 {main_ref}，"
                f"置信度 {conf}），使用常规布局。"
            )
        return f"[schematic] 拓扑识别：疑似 driver 模块（置信度 {conf}），使用常规布局。"

    return "[schematic] 拓扑识别：未识别为 driver 模块，使用常规布局。"


def log_topology_summary(node, options):
    """输出单个 node 的 topology 日志（schematic_progress 时）。"""
    if not options.get("schematic_progress", False):
        return
    from skidl.logger import active_logger

    topology = getattr(node, "_last_topology_result", None)
    if topology is None:
        return
    active_logger.info(format_topology_log_line(topology))


def log_topology_summaries_deep(node, options):
    """递归子页后输出各 sheet 的 topology 行，作为 place/route 流程末行日志。"""
    if not options.get("schematic_progress", False):
        return
    for child in getattr(node, "children", {}).values():
        log_topology_summaries_deep(child, options)
    log_topology_summary(node, options)

