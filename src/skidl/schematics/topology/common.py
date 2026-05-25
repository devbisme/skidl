# -*- coding: utf-8 -*-

"""
topology 子包：检测与布局共用的 token、网语义分类与 topology dict 构造。
"""

import os
import re

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
    apply_trunk_aware_layout,
    classify_trunk_nets,
)

# 网名 / pin 名 token（双通道分类）
_INPUT_TOKENS = (
    "VIN",
    "VCC",
    "VDD",
    "VM",
    "VBAT",
    "VBUS",
    "VSUP",
    "24V",
    "12V",
    "9V",
    "5V",
    "3V3",
    "3V",
    "1V8",
    "SUPPLY",
    "POWER",
    "PWR",
    "B+",
    "BATT",
    "BAT+",
    "IN+",
    "DC_IN",
)
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
_SENSE_PART_TOKENS = ("SENSE", "CS", "CSN", "CSP", "RS", "ISEN")


def _token_in_text(text, tokens):
    """token 作为独立词或常见分隔片段出现在 text 中。"""
    if not text:
        return False
    upper = str(text).upper()
    for token in tokens:
        if token in upper:
            return True
    return False


def _matched_tokens(text, tokens):
    """Return matched tokens in stable order for classification/debug logging."""
    if not text:
        return []
    upper = str(text).upper()
    matches = []
    for token in tokens:
        token_u = str(token).upper()
        if token_u in upper and token_u not in matches:
            matches.append(token_u)
    matches.sort(key=len, reverse=True)
    return matches


def _token_in_text(text, tokens):
    return bool(_matched_tokens(text, tokens))


def _net_label(net):
    return str(getattr(net, "name", "") or "")


def _attach_debug_enabled(options=None):
    if options and options.get("schematic_attach_debug") is not None:
        return bool(options.get("schematic_attach_debug"))
    value = str(os.environ.get("SKIDL_SCH_DEBUG_ATTACH", "") or "").strip().lower()
    return value not in ("", "0", "false", "no", "off")


def _attach_debug_log(options, message):
    if not _attach_debug_enabled(options):
        return
    from skidl.logger import active_logger

    active_logger.info("[attach-debug] %s" % message)


def _topology_debug_log(options, tag, message):
    if not options.get("schematic_progress", False):
        return
    from skidl.logger import active_logger

    active_logger.info("[%s] %s" % (tag, message))


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
    net_parts = node._net_connected_parts(net, allowed_parts=part_set)
    net_refs = [str(getattr(part, "ref", "") or "").upper() for part in net_parts]
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

        if (
            "input" not in categories
            and pin_names
            and any(_matched_tokens(pname, _INPUT_TOKENS) for pname in pin_names)
        ):
            categories.add("input")

    if "input" not in categories and _matched_tokens(net_name, ("POWER", "PWR", "SUPPLY")):
        if any(ref.startswith(("C", "D", "L", "J", "P", "CN")) for ref in net_refs):
            categories.add("input")

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
        control_like = touches(part, "control") or _part_is_control_branch_passive(
            part, main
        )
        sense_like = touches(part, "sense") or _part_looks_like_low_ohm_sense_resistor(
            part, node, main
        )
        inductor_like = _part_looks_like_inductor(part, roles)

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
        if control_like:
            topology["control_parts"].add(part)
        if sense_like and ref.startswith(("R", "C")):
            topology["sense_feedback_parts"].add(part)
        if inductor_like and (touches(part, "switch") or touches(part, "output")):
            topology["power_loop_parts"].add(part)
        if touches(part, "ground") and ref.startswith("C"):
            # 地相关去耦可偏下，由布局 Y 处理
            pass

    # 输出侧 L/D/C 连 output 或 switch
    for part in parts:
        if part is main:
            continue
        ref = str(getattr(part, "ref", "") or "").upper()
        if (_part_looks_like_inductor(part, roles) or ref.startswith("D")) and (
            touches(part, "output") or touches(part, "switch")
        ):
            topology["power_loop_parts"].add(part)
        if ref.startswith("C") and touches(part, "output"):
            topology["output_parts"].add(part)


def _part_ref_prefix(part):
    """取器件前缀，便于按 L/D/C/R/J 等做轻度分型。"""
    return str(getattr(part, "ref", "") or "").upper()[:1]


def _part_connected_nets(part):
    return {
        getattr(pin, "net", None)
        for pin in getattr(part, "pins", [])
        if getattr(pin, "net", None) is not None
    }


def _connected_main_pin_names(part, main_part):
    if main_part is None:
        return set()
    names = set()
    for net in _part_connected_nets(part):
        for pin in getattr(net, "pins", []):
            if getattr(pin, "part", None) is main_part:
                pname = str(getattr(pin, "name", "") or "").upper()
                if pname:
                    names.add(pname)
    return names


def _part_looks_like_inductor(part, roles):
    ref = str(getattr(part, "ref", "") or "").upper()
    role = str(roles.get(part, "") or "").lower()
    text = "%s %s" % (
        str(getattr(part, "value", "") or ""),
        str(getattr(part, "name", "") or ""),
    )
    text = text.upper()
    return (
        ref.startswith("L")
        or role == "inductor"
        or "INDUCTOR" in text
        or "CHOKE" in text
    )


def _parse_resistor_ohms(value):
    text = str(value or "").upper().replace(" ", "")
    if not text:
        return None
    text = text.replace("OHMS", "").replace("OHM", "")
    if "MR" in text:
        match = re.search(r"(\d+(?:\.\d+)?)MR", text)
        if match:
            return float(match.group(1)) / 1000.0
    if text.startswith("R") and text[1:].isdigit():
        return float("0." + text[1:])
    match = re.match(r"(\d+)R(\d+)$", text)
    if match:
        return float("%s.%s" % (match.group(1), match.group(2)))
    match = re.match(r"(\d+(?:\.\d+)?)R$", text)
    if match:
        return float(match.group(1))
    match = re.match(r"(\d+(?:\.\d+)?)$", text)
    if match:
        return float(match.group(1))
    return None


def _part_looks_like_low_ohm_sense_resistor(part, node, main_part):
    ref = str(getattr(part, "ref", "") or "").upper()
    if not ref.startswith("R"):
        return False
    value = str(getattr(part, "value", "") or "")
    ident = "%s %s %s" % (
        ref,
        value,
        str(getattr(part, "name", "") or ""),
    )
    ident_u = ident.upper()
    ohms = _parse_resistor_ohms(value)
    main_pin_names = _connected_main_pin_names(part, main_part)
    return (
        _LOW_R_VALUE_RE.search(value.replace(" ", "")) is not None
        or (ohms is not None and ohms < 1.0)
        or _token_in_text(ident_u, _SENSE_PART_TOKENS)
        or any(_token_in_text(name, _SENSE_TOKENS) for name in main_pin_names)
    )


def _part_is_control_branch_passive(part, main_part):
    ref = str(getattr(part, "ref", "") or "").upper()
    if not ref.startswith(("R", "C")):
        return False
    return any(
        _token_in_text(name, _CONTROL_TOKENS)
        for name in _connected_main_pin_names(part, main_part)
    )


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
        if _part_looks_like_inductor(part, roles):
            right.append(part)
    for part in topology.get("output_parts", set()):
        if roles.get(part) == "connector":
            right.append(part)
    inductors = by_ref([p for p in right if _part_looks_like_inductor(p, roles)])
    outputs = by_ref([p for p in right if p not in inductors])
    right = inductors + outputs

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

