# -*- coding: utf-8 -*-

"""
human_readable 模式下的功能拓扑识别（首版：generic driver）。
与 trunk-aware 布局互斥：matched 时仅 apply_generic_driver_layout，否则 apply_trunk_aware_layout。
"""

import re
from collections import defaultdict

from skidl.geometry import BBox, Point, Tx
from skidl.schematics.trunk_layout import (
    _place_parts_in_column,
    _place_parts_in_row,
    _resolve_overlaps,
    _set_part_center_x_safe,
    apply_trunk_aware_layout,
    classify_trunk_nets,
)

# 网名 / pin 名 token（双通道分类）
_INPUT_TOKENS = ("VIN", "VCC", "VDD", "VM", "VBAT", "24V", "12V", "5V", "3V3", "SUPPLY", "POWER")
_GROUND_TOKENS = ("GND", "VSS", "PGND", "AGND", "DGND")
# 顶/底 power rail 网名 token（与 control/switch 分离）
_TOP_RAIL_TOKENS = _INPUT_TOKENS + ("W+", "LED+")
_BOTTOM_RAIL_TOKENS = _GROUND_TOKENS + ("W-", "LED-")
_OUTPUT_TOKENS = ("OUT", "OUTPUT", "LOAD", "LED", "MOTOR", "W+", "W-", "AOUT", "BOUT")
_CONTROL_TOKENS = ("PWM", "DIM", "EN", "ENABLE", "CTRL", "IN1", "IN2", "SLEEP", "FAULT")
_SWITCH_TOKENS = ("SW", "LX", "PH", "DRV", "GATE", "HO", "LO")
_SENSE_TOKENS = ("FB", "CS", "CSN", "CSP", "SENSE", "ISEN", "COMP")

_WEAK_IC_HINTS = ("DRIVER", "DRV", "LED", "MOTOR", "PT", "XL", "MP", "TPS", "IRS")
_LOW_R_VALUE_RE = re.compile(
    r"(^0\s*R|^0R|^0\.|MR|R050|0\.43|(^|[^0-9])1R([^0-9]|$))",
    re.IGNORECASE,
)


def _token_in_text(text, tokens):
    """token 作为独立词或常见分隔片段出现在 text 中。"""
    if not text:
        return False
    upper = str(text).upper()
    for token in tokens:
        if token in upper:
            return True
    return False


def _net_label(net):
    return str(getattr(net, "name", "") or "")


def _disabled_topology(fallback="trunk_aware"):
    return {
        "kind": "disabled",
        "matched": False,
        "confidence": 0,
        "main_part": None,
        "input_nets": [],
        "output_nets": [],
        "power_nets": [],
        "ground_nets": [],
        "control_nets": [],
        "switch_or_drive_nets": [],
        "sense_or_feedback_nets": [],
        "input_parts": set(),
        "output_parts": set(),
        "power_loop_parts": set(),
        "control_parts": set(),
        "sense_feedback_parts": set(),
        "fallback": fallback,
        "reasons": ["topology_detection disabled"],
    }


def _empty_topology(kind, confidence, main_part=None, reasons=None, fallback="trunk_aware"):
    return {
        "kind": kind,
        "matched": kind == "generic_driver",
        "confidence": confidence,
        "main_part": main_part,
        "input_nets": [],
        "output_nets": [],
        "power_nets": [],
        "ground_nets": [],
        "control_nets": [],
        "switch_or_drive_nets": [],
        "sense_or_feedback_nets": [],
        "input_parts": set(),
        "output_parts": set(),
        "power_loop_parts": set(),
        "control_parts": set(),
        "sense_feedback_parts": set(),
        "fallback": fallback,
        "reasons": reasons or [],
    }


def _topology_options(options):
    """仅在 human_readable 下启用 topology_detection。"""
    enabled = bool(options.get("human_readable", False)) and bool(
        options.get("topology_detection", True)
    )
    return {
        "enabled": enabled,
        "strong_threshold": int(options.get("topology_confidence_threshold", 60)),
        "weak_threshold": int(options.get("topology_weak_threshold", 40)),
        "gap": options.get("topology_gap"),
    }


def _candidate_ic_parts(parts, roles):
    """候选主控 IC：U* 或 role ic 且 pin 数较多。"""
    candidates = []
    for part in parts:
        ref = str(getattr(part, "ref", "") or "").upper()
        role = roles.get(part, "other")
        pin_count = len(getattr(part, "pins", []))
        if ref.startswith("U") or role == "ic":
            if pin_count >= 4:
                candidates.append(part)
    if not candidates:
        for part in parts:
            if roles.get(part) == "ic":
                candidates.append(part)
    return candidates


def _pins_on_part_for_net(node, part, net, part_set):
    """返回 part 在 net 上的 pin 名列表。"""
    names = []
    for pin in getattr(net, "pins", []):
        p = getattr(pin, "part", None)
        if p is part and (part_set is None or p in part_set):
            names.append(str(getattr(pin, "name", "") or "").upper())
    return names


def _classify_net_semantic(net, main_part, node, part_set, adjacency):
    """
    按 net 名 + main_part 上 pin 名推断语义类别。
    返回 set of: input, ground, output, control, switch, sense
    """
    net_name = _net_label(net).upper()
    categories = set()

    if _token_in_text(net_name, _INPUT_TOKENS):
        categories.add("input")
    if _token_in_text(net_name, _GROUND_TOKENS) or (
        node._is_power_net_name(net_name) and any(t in net_name for t in _GROUND_TOKENS)
    ):
        categories.add("ground")
    if _token_in_text(net_name, _OUTPUT_TOKENS):
        categories.add("output")
    if _token_in_text(net_name, _CONTROL_TOKENS):
        categories.add("control")
    if _token_in_text(net_name, _SWITCH_TOKENS):
        categories.add("switch")
    if _token_in_text(net_name, _SENSE_TOKENS):
        categories.add("sense")

    if main_part is not None:
        pin_names = _pins_on_part_for_net(node, main_part, net, part_set)
        for pname in pin_names:
            if _token_in_text(pname, _INPUT_TOKENS):
                categories.add("input")
            if _token_in_text(pname, _GROUND_TOKENS):
                categories.add("ground")
            if _token_in_text(pname, _OUTPUT_TOKENS):
                categories.add("output")
            if _token_in_text(pname, _CONTROL_TOKENS):
                categories.add("control")
            if _token_in_text(pname, _SWITCH_TOKENS):
                categories.add("switch")
            if _token_in_text(pname, _SENSE_TOKENS):
                categories.add("sense")

    # SW 需绑主 IC pin 或邻接 L/D 才计 switch（避免单独 SW 网名误判）
    if "switch" in categories and main_part is not None:
        pin_names = _pins_on_part_for_net(node, main_part, net, part_set)
        on_main_sw = any(_token_in_text(p, _SWITCH_TOKENS) for p in pin_names)
        if not on_main_sw:
            net_parts = node._net_connected_parts(net, allowed_parts=part_set)
            has_ld = any(
                str(getattr(p, "ref", "") or "").upper().startswith(("L", "D", "Q"))
                for p in net_parts
            )
            if not has_ld:
                categories.discard("switch")

    return categories


def _score_candidate_ic(node, candidate, parts, nets, roles, part_set, adjacency):
    """对单颗候选 IC 计算 driver 特征分与 reasons。"""
    score = 0
    reasons = []
    feature_flags = {
        "input": False,
        "ground": False,
        "output_switch": False,
        "control": False,
        "sense": False,
        "inductor": False,
        "diode": False,
        "out_connector": False,
        "sense_r": False,
        "weak_hint": False,
    }

    cand_nets = set()
    for net in nets:
        net_parts = node._net_connected_parts(net, allowed_parts=part_set)
        if candidate not in net_parts:
            continue
        cand_nets.add(net)
        cats = _classify_net_semantic(net, candidate, node, part_set, adjacency)
        pin_names = _pins_on_part_for_net(node, candidate, net, part_set)

        if "input" in cats or _token_in_text(" ".join(pin_names), _INPUT_TOKENS):
            if not feature_flags["input"]:
                score += 2
                feature_flags["input"] = True
                reasons.append("input_pin_or_net")
        if "ground" in cats:
            if not feature_flags["ground"]:
                score += 2
                feature_flags["ground"] = True
                reasons.append("ground")
        if "output" in cats or "switch" in cats:
            if not feature_flags["output_switch"]:
                score += 3
                feature_flags["output_switch"] = True
                reasons.append("output_or_switch")
        if "control" in cats:
            # PWM 等需与其它强特征组合；此处只记 control 特征位
            feature_flags["control"] = True
        if "sense" in cats:
            if not feature_flags["sense"]:
                score += 2
                feature_flags["sense"] = True
                reasons.append("sense_fb")

    # control 加分：仅当已有 input/ground/output_switch/sense 之一
    if feature_flags["control"] and any(
        feature_flags[k]
        for k in ("input", "ground", "output_switch", "sense")
    ):
        score += 1
        reasons.append("control_with_power")

    for part in parts:
        if part is candidate:
            continue
        ref = str(getattr(part, "ref", "") or "").upper()
        value = str(getattr(part, "value", "") or "").upper()
        name = str(getattr(part, "name", "") or "").upper()
        connected = False
        for net in nets:
            net_parts = node._net_connected_parts(net, allowed_parts=part_set)
            if part in net_parts and candidate in net_parts:
                connected = True
                break
        if not connected and adjacency:
            if part not in adjacency.get(id(candidate), set()):
                continue

        if ref.startswith("L") and not feature_flags["inductor"]:
            score += 2
            feature_flags["inductor"] = True
            reasons.append("inductor_near")
        if ref.startswith("D") and not feature_flags["diode"]:
            score += 1
            feature_flags["diode"] = True
            reasons.append("diode_near")

        if ref.startswith(("J", "P", "CN")) and roles.get(part) == "connector":
            net_names = [n.upper() for n in node._net_names_of(part)]
            if any(_token_in_text(n, _OUTPUT_TOKENS) for n in net_names):
                if not feature_flags["out_connector"]:
                    score += 2
                    feature_flags["out_connector"] = True
                    reasons.append("output_connector")

        if ref.startswith("R") and _LOW_R_VALUE_RE.search(value.replace(" ", "")):
            if not feature_flags["sense_r"]:
                score += 1
                feature_flags["sense_r"] = True
                reasons.append("sense_resistor")

    name = str(getattr(candidate, "name", "") or "").upper()
    value = str(getattr(candidate, "value", "") or "").upper()
    ic_text = f"{value} {name}".upper()
    for hint in _WEAK_IC_HINTS:
        if hint in ic_text:
            if not feature_flags["weak_hint"]:
                score += 1
                feature_flags["weak_hint"] = True
                reasons.append(f"weak_hint:{hint}")
            break

    # 组合约束：至少 3 类强特征，且含 output/switch 或 input+ground
    strong_categories = sum(
        1
        for k in ("input", "ground", "output_switch", "sense", "inductor")
        if feature_flags[k]
    )
    has_power_path = feature_flags["input"] and (
        feature_flags["ground"] or feature_flags["output_switch"]
    )
    combo_ok = strong_categories >= 3 and (
        feature_flags["output_switch"] or has_power_path
    )

    confidence = min(100, score * 5)
    return score, confidence, reasons, combo_ok, feature_flags


def _build_net_lists(node, candidate, parts, nets, part_set, adjacency):
    """基于候选 main 做网级语义分类。"""
    buckets = {
        "input_nets": [],
        "output_nets": [],
        "power_nets": [],
        "ground_nets": [],
        "control_nets": [],
        "switch_or_drive_nets": [],
        "sense_or_feedback_nets": [],
    }
    seen = set()
    for net in nets:
        if net in seen:
            continue
        net_parts = node._net_connected_parts(net, allowed_parts=part_set)
        if candidate not in net_parts and len(net_parts) < 2:
            continue
        cats = _classify_net_semantic(net, candidate, node, part_set, adjacency)
        if not cats:
            continue
        seen.add(net)
        if "input" in cats:
            buckets["input_nets"].append(net)
            buckets["power_nets"].append(net)
        if "ground" in cats:
            buckets["ground_nets"].append(net)
        if "output" in cats:
            buckets["output_nets"].append(net)
        if "control" in cats:
            buckets["control_nets"].append(net)
        if "switch" in cats:
            buckets["switch_or_drive_nets"].append(net)
        if "sense" in cats:
            buckets["sense_or_feedback_nets"].append(net)
    return buckets


def _assign_topology_part_groups(node, parts, roles, topology, part_set):
    """按已分类 net 将器件归入各功能区。"""
    net_sets = {
        "input": set(topology["input_nets"]),
        "output": set(topology["output_nets"]),
        "switch": set(topology["switch_or_drive_nets"]),
        "control": set(topology["control_nets"]),
        "sense": set(topology["sense_or_feedback_nets"]),
        "ground": set(topology["ground_nets"]),
    }
    main = topology.get("main_part")

    def touches(part, key):
        for net in net_sets.get(key, ()):
            if part in node._net_connected_parts(net, allowed_parts=part_set):
                return True
        return False

    for part in parts:
        if part is main:
            continue
        ref = str(getattr(part, "ref", "") or "").upper()
        role = roles.get(part, "other")

        if touches(part, "input") and (
            ref[:1] in ("C", "D") or role == "connector"
        ):
            topology["input_parts"].add(part)
        if touches(part, "output") or (
            role == "connector" and touches(part, "output")
        ):
            topology["output_parts"].add(part)
        if touches(part, "switch") or (
            ref.startswith(("L", "D", "Q")) and touches(part, "switch")
        ):
            topology["power_loop_parts"].add(part)
        if touches(part, "control") or (
            ref.startswith(("R", "C")) and touches(part, "control")
        ):
            topology["control_parts"].add(part)
        if touches(part, "sense") and ref.startswith(("R", "C")):
            topology["sense_feedback_parts"].add(part)
        if touches(part, "ground") and ref.startswith("C"):
            # 地相关去耦可偏下，由布局 Y 处理
            pass

    # 输出侧 L/D/C 连 output 或 switch
    for part in parts:
        if part is main:
            continue
        ref = str(getattr(part, "ref", "") or "").upper()
        if ref.startswith(("L", "D")) and (
            touches(part, "output") or touches(part, "switch")
        ):
            topology["power_loop_parts"].add(part)
        if ref.startswith("C") and touches(part, "output"):
            topology["output_parts"].add(part)


def _part_ref_prefix(part):
    """取器件前缀，便于按 L/D/C/R/J 等做轻度分型。"""
    return str(getattr(part, "ref", "") or "").upper()[:1]


def _part_width(part, grid):
    return max(getattr(part.place_bbox, "w", 0), grid)


def _row_total_width(parts, gap, grid):
    if not parts:
        return 0
    return sum(_part_width(part, grid) for part in parts) + max(0, len(parts) - 1) * gap


def _build_driver_chain_order(node, roles, topology, main_part):
    """
    主功率链顺序：输入 C/D -> 主 IC -> 电感 -> 输出连接器。
    buck/LED driver 手画图通常沿这条水平线阅读。
    """
    def by_ref(parts_):
        return sorted(parts_, key=node._part_ref_key)

    left = []
    for part in topology.get("input_parts", set()):
        if part is main_part:
            continue
        if _part_ref_prefix(part) in ("C", "D"):
            left.append(part)
    for part in topology.get("power_loop_parts", set()):
        if _part_ref_prefix(part) == "D" and part not in left:
            left.append(part)
    left = by_ref([p for p in left if _part_ref_prefix(p) == "C"]) + by_ref(
        [p for p in left if _part_ref_prefix(p) == "D"]
    )

    right = []
    for part in topology.get("power_loop_parts", set()):
        if _part_ref_prefix(part) == "L":
            right.append(part)
    for part in topology.get("output_parts", set()):
        if roles.get(part) == "connector":
            right.append(part)
    right = by_ref(right)

    chain = left + [main_part] + right
    return chain, set(chain)


def _chain_row_start_x(node, chain, main_part, gap, grid):
    """让 main_part 大致留在当前 X，向左排开整条主链。"""
    main_ctr = node._placement_ctr(main_part)
    x_before = 0
    for part in chain:
        if part is main_part:
            break
        x_before += _part_width(part, grid) + gap
    return main_ctr.x - x_before


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

    for net in nets:
        if not _is_rail_label_net(net):
            continue
        if id(net) in switch_ids:
            continue
        name = _net_label(net).upper()
        cats = _classify_net_semantic(net, main_part, node, part_set, None)

        if id(net) in control_ids or "control" in cats or _token_in_text(
            name, _CONTROL_TOKENS
        ):
            if net not in control:
                control.append(net)
            continue
        if "switch" in cats or _token_in_text(name, _SWITCH_TOKENS):
            continue

        if _token_in_text(name, _BOTTOM_RAIL_TOKENS) or "ground" in cats:
            bottom.append(net)
            continue
        if _token_in_text(name, _TOP_RAIL_TOKENS) or "input" in cats:
            top.append(net)
            continue
        if net in topology.get("ground_nets", []):
            bottom.append(net)
        elif net in topology.get("input_nets", []) or net in topology.get(
            "power_nets", []
        ):
            top.append(net)
        elif net in topology.get("output_nets", []):
            if _token_in_text(name, ("LED+", "W+", "LED", "OUT+")):
                top.append(net)
            elif _token_in_text(name, ("LED-", "W-")):
                bottom.append(net)

    return _dedupe_nets(top), _dedupe_nets(bottom), _dedupe_nets(control)


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

    return {
        "enabled": True,
        "top_nets": top_nets,
        "bottom_nets": bottom_nets,
        "control_nets": control_nets,
        "top_y": top_y,
        "bottom_y": bottom_y,
        "x_min": x_min,
        "x_max": x_max,
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


def _chain_row_satellite_parts(node, parts, chain_parts, nets):
    """
    与主链器件共网、但不在 chain 内的 R/C（如 R1、输入侧小电容），
    应排在主链同一水平行，避免 switch 网被 switchbox 绕外围。
    """
    chain_set = set(chain_parts)
    part_set = set(parts)
    satellites = []
    for net in nets:
        connected = node._net_connected_parts(net, allowed_parts=part_set)
        if not connected or not chain_set.intersection(connected):
            continue
        for part in connected:
            if part in chain_set:
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
        insert_at = len(row)
        for idx, cp in enumerate(row):
            for net in nets:
                con = set(
                    node._net_connected_parts(net, allowed_parts=known | {sat})
                )
                if sat in con and cp in con:
                    insert_at = max(insert_at, idx + 1)
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

    satellites = _chain_row_satellite_parts(node, parts, chain_parts, nets)
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
        if part in row_parts or part is main_part or part in decoup_caps:
            continue
        h = _part_layout_h(part, grid)
        if _part_on_net_set(part, top_set) and not _part_on_net_set(part, bottom_set):
            _nudge_y(part, top_y + grid + h / 2)
        elif _part_on_net_set(part, bottom_set) and not _part_on_net_set(part, top_set):
            _nudge_y(part, bottom_y - grid - h / 2)

    # 控制支路：主控右侧中部，避免拉到顶/底 rail。
    control_parts = sorted(
        [p for p in topology.get("control_parts", set()) if p not in chain_parts],
        key=node._part_ref_key,
    )
    if control_parts:
        main_vis = _layout_bbox(main_part)
        if main_vis is None:
            main_vis = main_part.place_bbox * main_part.tx
        ctrl_x = main_vis.max.x + gap * 2
        ctrl_y = mid_y + gap
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


def detect_known_topology(
    node, parts, nets, roles, main_part, trunk_map=None, **options
):
    """拓扑识别门面；当前仅 generic_driver detector。"""
    topo_opts = _topology_options(options)
    if not topo_opts["enabled"]:
        return _disabled_topology()

    adjacency = None
    if parts and nets:
        from skidl.schematics.trunk_layout import build_part_adjacency

        adjacency = build_part_adjacency(parts, nets)

    return detect_generic_driver_topology(
        node,
        parts,
        nets,
        roles,
        main_part,
        trunk_map=trunk_map,
        adjacency=adjacency,
        **options,
    )


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
    generic_driver matched 时的布线顺序偏置（保守，不改变拓扑）。
    返回值越小越先布。
    """
    if not topology or topology.get("kind") != "generic_driver":
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


def apply_topology_or_trunk_layout(
    node, parts, nets, roles, main_part, **options
):
    """
    互斥分支：generic_driver 仅 apply_generic_driver_layout，否则 trunk-aware。
    结果写入 node._last_topology_result。
    """
    trunk_map = classify_trunk_nets(node, parts, nets, roles, main_part, **options)
    topology = detect_known_topology(
        node, parts, nets, roles, main_part, trunk_map=trunk_map, **options
    )
    node._last_topology_result = topology

    topo_opts = _topology_options(options)
    layout_main = topology.get("main_part") or main_part
    strong_th = topo_opts["strong_threshold"]

    if (
        topology.get("kind") == "generic_driver"
        and topology.get("confidence", 0) >= strong_th
        and layout_main is not None
    ):
        node._human_readable_main_part = layout_main
        layout_opts = dict(options)
        layout_opts.setdefault("grid", 100)
        layout_opts.setdefault("blk_int_pad", 100)
        apply_generic_driver_layout(
            node,
            parts,
            roles,
            layout_main,
            topology,
            trunk_map,
            nets=nets,
            **layout_opts,
        )
    else:
        node._driver_rail_plan = {"enabled": False}
        layout_opts = dict(options)
        layout_opts.setdefault("grid", 100)
        layout_opts.setdefault("blk_int_pad", 100)
        apply_trunk_aware_layout(
            node,
            parts,
            roles,
            layout_main,
            trunk_map,
            **layout_opts,
        )
