# -*- coding: utf-8 -*-

"""
generic MCU 专用：星型拓扑识别、分区布局与布线顺序偏置。
与 generic_driver 互斥；不启用 driver rail 预布线。
"""

import copy

from skidl.geometry import BBox, Point, Segment, Tx

from . import common as _common
from .driver import _is_anonymous_net, _layout_bbox, _part_layout_h

for _name, _val in _common.__dict__.items():
    if _name.startswith("__"):
        continue
    globals()[_name] = _val
del _name, _val, _common

# MCU 身份与引脚语义 token（识别用）
_MCU_IDENTITY_TOKENS = (
    "MCU",
    "STM32",
    "F103",
    "F407",
    "ATMEGA",
    "MEGA",
    "ATTINY",
    "PIC",
    "DSPIC",
    "ESP32",
    "ESP8266",
    "ESP",
    "MJ6050",
    "CA51F551",
    "CA51",
    "CORTEX",
    "SAM",
    "NRF",
    "CH32",
    "GD32",
    "MSP430",
    "LPC",
    "HC32",
)
_MCU_PIN_TOKENS = (
    "PA",
    "PB",
    "PC",
    "PD",
    "PE",
    "PF",
    "NRST",
    "RESET",
    "OSC",
    "HSE",
    "LSE",
    "XI",
    "XO",
    "SWDIO",
    "SWCLK",
    "BOOT0",
    "BOOT1",
    "IIC_SDA",
    "IIC_SCL",
    "GPIO",
    "TK",
    "TKCAP",
    "VDD",
    "VSS",
    "VDDA",
)
_MCU_COMM_NET_TOKENS = ("TX", "RX", "SWD", "SDA", "SCL", "UART")
_MCU_IO_NET_TOKENS = ("TK", "PWM", "MISO", "MOSI", "ADC", "DAC")


def _mcu_text_fields(part):
    """合并 value/name 供 token 匹配。"""
    value = str(getattr(part, "value", "") or "").upper()
    name = str(getattr(part, "name", "") or "").upper()
    lib = str(getattr(part, "lib", "") or "").upper()
    part_name = str(getattr(part, "name", "") or "").upper()
    ref = str(getattr(part, "ref", "") or "").upper()
    return f"{value} {name} {lib} {part_name} {ref}"


def _collect_mcu_pin_names(node, candidate, nets, part_set):
    """候选 MCU 上所有连接 pin 名。"""
    names = []
    for net in nets:
        net_parts = node._net_connected_parts(net, allowed_parts=part_set)
        if candidate not in net_parts:
            continue
        names.extend(_pins_on_part_for_net(node, candidate, net, part_set))
    return names


def _is_nc_net_name(name):
    upper = str(name or "").upper()
    return upper.startswith("UNCONNECTED") or "NOCONNECT" in upper


def _count_decouple_caps(node, candidate, parts, nets, part_set):
    """统计贴 MCU 且接 GND 的去耦电容颗数。"""
    count = 0
    for part in parts:
        if part is candidate:
            continue
        ref = str(getattr(part, "ref", "") or "").upper()
        if not ref.startswith("C"):
            continue
        touches_mcu = False
        touches_gnd = False
        for net in nets:
            net_parts = node._net_connected_parts(net, allowed_parts=part_set)
            if part not in net_parts:
                continue
            if candidate in net_parts:
                touches_mcu = True
            if _token_in_text(_net_label(net), _GROUND_TOKENS):
                touches_gnd = True
        if touches_mcu and touches_gnd:
            count += 1
    return count


def _has_crystal_subgraph(node, candidate, parts, nets, part_set):
    """Y + 负载电容挂 OSC/HSE 脚。"""
    y_parts = [
        p
        for p in parts
        if p is not candidate
        and str(getattr(p, "ref", "") or "").upper().startswith("Y")
    ]
    if not y_parts:
        return False
    pin_names = _collect_mcu_pin_names(node, candidate, nets, part_set)
    if not any(
        _token_in_text(n, ("OSC", "HSE", "LSE", "XI", "XO")) for n in pin_names
    ):
        return False
    for yp in y_parts:
        caps = 0
        for net in nets:
            np = node._net_connected_parts(net, allowed_parts=part_set)
            if yp not in np:
                continue
            if candidate in np:
                return True
            for p in np:
                if str(getattr(p, "ref", "") or "").upper().startswith("C"):
                    caps += 1
        if caps >= 2:
            return True
    return False


def _has_reset_subgraph(node, candidate, parts, nets, part_set):
    pin_names = _collect_mcu_pin_names(node, candidate, nets, part_set)
    if not any(_token_in_text(n, ("NRST", "RESET")) for n in pin_names):
        return False
    has_r = has_c = False
    for part in parts:
        if part is candidate:
            continue
        ref = str(getattr(part, "ref", "") or "").upper()
        for net in nets:
            np = node._net_connected_parts(net, allowed_parts=part_set)
            if part not in np or candidate not in np:
                continue
            pnames = _pins_on_part_for_net(node, candidate, net, part_set)
            if any(_token_in_text(n, ("NRST", "RESET")) for n in pnames):
                if ref.startswith("R"):
                    has_r = True
                if ref.startswith("C"):
                    has_c = True
    return has_r and has_c


def _has_comm_pair(node, candidate, nets, part_set):
    names = set()
    for net in nets:
        if candidate not in node._net_connected_parts(net, allowed_parts=part_set):
            continue
        label = _net_label(net).upper()
        if _token_in_text(label, ("TX", "RX")):
            names.add("uart")
        if _token_in_text(label, ("SWDIO", "SWCLK", "SWD")):
            names.add("swd")
    pin_names = _collect_mcu_pin_names(node, candidate, nets, part_set)
    if any(_token_in_text(n, ("TX", "RX", "UART")) for n in pin_names):
        names.add("uart")
    if any(_token_in_text(n, ("SWDIO", "SWCLK")) for n in pin_names):
        names.add("swd")
    return "uart" in names or "swd" in names


def _count_io_series_resistors(node, candidate, parts, nets, part_set):
    """串阻：一端连 MCU，另一端具名功能网。"""
    count = 0
    for part in parts:
        if part is candidate:
            continue
        ref = str(getattr(part, "ref", "") or "").upper()
        if not ref.startswith("R"):
            continue
        mcu_nets = []
        other_named = False
        for net in nets:
            np = node._net_connected_parts(net, allowed_parts=part_set)
            if part not in np:
                continue
            if candidate in np:
                mcu_nets.append(net)
            else:
                label = _net_label(net)
                if label and not _is_nc_net_name(label) and not _is_anonymous_net(net):
                    if _token_in_text(label.upper(), _MCU_IO_NET_TOKENS + _MCU_COMM_NET_TOKENS):
                        other_named = True
        if mcu_nets and other_named:
            count += 1
    return count


def _score_mcu_candidate_ic(node, candidate, parts, nets, roles, part_set, adjacency):
    """对单颗候选 IC 计算 MCU 特征分。"""
    score = 0
    reasons = []
    flags = {
        "mcu_identity": False,
        "mcu_pins": False,
        "decouple": False,
        "crystal": False,
        "reset": False,
        "comm": False,
        "io_series": False,
        "buck_veto": False,
    }

    ic_text = _mcu_text_fields(candidate)
    if _token_in_text(ic_text, _MCU_IDENTITY_TOKENS):
        score += 10
        flags["mcu_identity"] = True
        reasons.append("mcu_identity")

    pin_names = _collect_mcu_pin_names(node, candidate, nets, part_set)
    pin_hits = sum(1 for n in pin_names if _token_in_text(n, _MCU_PIN_TOKENS))
    if pin_hits >= 2:
        score += min(6, pin_hits * 2)
        flags["mcu_pins"] = True
        reasons.append("mcu_pin_names")

    pin_count = len(getattr(candidate, "pins", []))
    if pin_count >= 8:
        score += 2
        reasons.append("pin_count>=%d" % pin_count)

    dec = _count_decouple_caps(node, candidate, parts, nets, part_set)
    if dec >= 2:
        score += 8
        flags["decouple"] = True
        reasons.append("decouple_cluster")
    elif dec >= 1:
        score += 4
        reasons.append("decouple_single")

    if _has_crystal_subgraph(node, candidate, parts, nets, part_set):
        score += 6
        flags["crystal"] = True
        reasons.append("crystal_subgraph")

    if _has_reset_subgraph(node, candidate, parts, nets, part_set):
        score += 4
        flags["reset"] = True
        reasons.append("reset_subgraph")

    if _has_comm_pair(node, candidate, nets, part_set):
        score += 4
        flags["comm"] = True
        reasons.append("comm_debug")

    io_r = _count_io_series_resistors(node, candidate, parts, nets, part_set)
    if io_r >= 3:
        score += 4
        flags["io_series"] = True
        reasons.append("io_series_resistors")

    # PMIC/buck 否决：强 driver 特征且无 MCU 身份
    drv_sc, _, _, drv_combo, drv_flags = _score_candidate_ic(
        node, candidate, parts, nets, roles, part_set, adjacency
    )
    if drv_flags.get("inductor") and drv_flags.get("output_switch"):
        if not flags["mcu_identity"]:
            score = max(0, score - 15)
            flags["buck_veto"] = True
            reasons.append("buck_veto")
        elif drv_combo and drv_sc > score // 5:
            score = max(0, score - 8)
            flags["buck_veto"] = True
            reasons.append("buck_competes")

    if _token_in_text(ic_text, ("DRIVER", "DRV", "LED_DRIVER")) and not flags["mcu_pins"]:
        score = max(0, score - 5)
        reasons.append("driver_name_without_mcu_pins")

    combo_ok = flags["mcu_identity"] and (
        flags["decouple"]
        or flags["crystal"]
        or flags["comm"]
        or flags["io_series"]
        or (flags["mcu_pins"] and pin_count >= 8)
    )
    confidence = min(100, score * 5)
    return score, confidence, reasons, combo_ok, flags


def _assign_mcu_part_groups(node, parts, roles, topology, part_set, adjacency):
    """按 ref/网语义将 MCU 周边器件归入专用桶（BFS 1-hop 邻域）。"""
    main = topology.get("main_part")
    if main is None or adjacency is None:
        return

    for key in (
        "decouple_parts",
        "clock_parts",
        "reset_parts",
        "boot_parts",
        "io_series_parts",
        "connector_parts",
        "indicator_parts",
        "tk_parts",
    ):
        topology[key] = set()

    visited = {id(main)}
    queue = [main]
    satellite = []
    while queue:
        cur = queue.pop(0)
        for nb in adjacency.get(id(cur), set()):
            if id(nb) not in visited:
                visited.add(id(nb))
                queue.append(nb)
                if nb is not main:
                    satellite.append(nb)

    for part in satellite:
        ref = str(getattr(part, "ref", "") or "").upper()
        role = roles.get(part, "other")

        if ref.startswith("C"):
            # 接 GND 且接 MCU 的 C 视为去耦
            is_dec = False
            for pin in getattr(part, "pins", []):
                net = getattr(pin, "net", None)
                if net is None:
                    continue
                np = node._net_connected_parts(net, allowed_parts=part_set)
                if main not in np:
                    continue
                if _token_in_text(_net_label(net), _GROUND_TOKENS):
                    is_dec = True
                    break
            if is_dec:
                topology["decouple_parts"].add(part)
                continue

        if ref.startswith("Y"):
            topology["clock_parts"].add(part)
            continue

        if ref.startswith("R"):
            boot_pin = any(
                _token_in_text(n, ("BOOT0", "BOOT1"))
                for n in _connected_main_pin_names(part, main)
            )
            reset_pin = any(
                _token_in_text(n, ("NRST", "RESET"))
                for n in _connected_main_pin_names(part, main)
            )
            led_neighbor = False
            for nb in adjacency.get(id(part), set()):
                if nb is main:
                    continue
                nref = str(getattr(nb, "ref", "") or "").upper()
                if nref.startswith("LED") or "LED" in str(
                    getattr(nb, "value", "") or ""
                ).upper():
                    led_neighbor = True
                    break
            if boot_pin:
                topology["boot_parts"].add(part)
            elif reset_pin:
                topology["reset_parts"].add(part)
            elif led_neighbor:
                topology["indicator_parts"].add(part)
            else:
                topology["io_series_parts"].add(part)
            continue

        if ref.startswith("LED") or (role != "connector" and "LED" in str(getattr(part, "value", "") or "").upper()):
            topology["indicator_parts"].add(part)
            continue

        if ref.startswith("TK"):
            topology["tk_parts"].add(part)
            continue

        if role == "connector" or ref.startswith(("J", "P", "CN", "H", "X")):
            topology["connector_parts"].add(part)
            continue

        if ref.startswith("C") and part not in topology["decouple_parts"]:
            topology["decouple_parts"].add(part)


def detect_generic_mcu_topology(
    node, parts, nets, roles, main_part, trunk_map=None, adjacency=None, **options
):
    """打分识别 MCU 星型模块，返回完整 topology dict。"""
    topo_opts = _topology_options(options)
    part_set = set(parts)
    if adjacency is None and parts and nets:
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
        sc, conf, reasons, combo, _flags = _score_mcu_candidate_ic(
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
        kind = "weak_mcu"
        fallback = "trunk_aware"
    else:
        kind = "mcu"
        fallback = False

    topology = _empty_topology(
        kind, best_conf, main_part=best, reasons=best_reasons, fallback=fallback
    )
    if kind == "unrecognized":
        return topology

    net_buckets = _build_net_lists(node, best, parts, nets, part_set, adjacency)
    for key, val in net_buckets.items():
        topology[key] = val

    _assign_mcu_part_groups(node, parts, roles, topology, part_set, adjacency)
    return topology


def _tk_partner_for_resistor(part, main_part, adjacency):
    """串阻另一侧的 TK 弹簧焊盘（与 R 成对布线）。"""
    if adjacency is None:
        return None
    for nb in adjacency.get(id(part), set()):
        if nb is main_part:
            continue
        ref = str(getattr(nb, "ref", "") or "").upper()
        if ref.startswith("TK"):
            return nb
    return None


def _mcu_touch_key_text(part):
    tokens = (
        getattr(part, "ref", ""),
        getattr(part, "name", ""),
        getattr(part, "value", ""),
        getattr(part, "description", ""),
    )
    return " ".join(str(tok or "") for tok in tokens).upper()


def _mcu_is_left_touch_key_candidate(part):
    if len(getattr(part, "pins", []) or []) != 1:
        return False
    text = _mcu_touch_key_text(part)
    ref = str(getattr(part, "ref", "") or "").upper()
    if "SPRING" in text or "TK_SPRING" in text:
        return True
    return ref.startswith("TK") and "TOUCH" in text


def _mcu_mark_left_touch_key_render(part):
    if not _mcu_is_left_touch_key_candidate(part):
        return
    text = _mcu_touch_key_text(part)
    part._kicad_render_kind = "mcu_touch_key_original_pin_right"
    part._mcu_touch_key_side = "left"
    if "TK_SPRING" in text:
        part._kicad_force_lib_part = "TK_Spring_Center"
        part._kicad_force_pin_offset_mm = 5.08

def _io_side_score(node, part):
    """连接器/串阻侧：正=偏右，负=偏左。"""
    names = [n.upper() for n in node._net_names_of(part)]
    right_tokens = ("OUT", "TX", "MISO", "SCL", "CS", "PWM")
    left_tokens = ("IN", "RX", "MOSI", "SDA", "ADC", "SENSE")
    right = sum(any(token in n for token in right_tokens) for n in names)
    left = sum(any(token in n for token in left_tokens) for n in names)
    return right - left


def _mcu_net_keep_local_wire(net_parts, main_part):
    """MCU 星型板上 2 器件网一律短直线（TK—R、R—U3、LED 等）。"""
    return len(net_parts) == 2


def _mcu_pin_route_pt(pin):
    """与 cleanup_wires / 导出一致的引脚绝对坐标（mils）。"""
    tx = getattr(pin.part, "tx", None) or Tx()
    return (pin.pt * tx).round()


def _pin_abs_pt(pin):
    """引脚在原理图坐标系中的绝对位置（mils）。"""
    base = getattr(pin, "place_pt", None) or pin.pt
    tx = getattr(pin.part, "tx", None) or Tx()
    return (base * tx).round()


def _mcu_pin_looks_like_power(pin):
    """MCU 引脚名像电源/地时，不作为去耦对齐目标。"""
    name = str(getattr(pin, "name", "") or "").upper()
    return _token_in_text(
        name, ("VSS", "VDD", "VCC", "GND", "AVDD", "AGND", "DVDD", "DVSS", "VBAT")
    )


def _pair_pins_to_main(part, main_part, node=None, prefer_signal=True):
    """
    返回 (main_pin, part_pin) 若二者共网。
    去耦电容等同器件双网接 MCU 时，优先信号脚（如 P35/TKCAP），避免误选 VSS/VDD。
    """
    signal_pairs = []
    power_pairs = []
    for pin in part.pins:
        net = getattr(pin, "net", None)
        if net is None:
            continue
        for mp in main_part.pins:
            if getattr(mp, "net", None) is not net:
                continue
            if prefer_signal and node is not None:
                label = _net_label(net)
                if node._is_power_net_name(label) or _token_in_text(
                    label, _GROUND_TOKENS + ("VDD", "VCC", "VSS", "VDDA", "VCCA")
                ):
                    power_pairs.append((mp, pin))
                else:
                    signal_pairs.append((mp, pin))
            else:
                return mp, pin
    if signal_pairs:
        non_pwr = [
            (mp, pp) for mp, pp in signal_pairs if not _mcu_pin_looks_like_power(mp)
        ]
        if non_pwr:
            return non_pwr[0]
        return signal_pairs[0]
    if power_pairs:
        return power_pairs[0]
    return None, None


def _mcu_x_outward_of_pin(main_part, main_pin, part_w, gap):
    """水平外扩：器件放在引脚远离 MCU 几何中心的一侧。"""
    bb = _layout_bbox(main_part)
    if bb is None:
        pt = _pin_abs_pt(main_pin)
        return pt.x - (2 * gap) - part_w
    pt = _pin_abs_pt(main_pin)
    dx = pt.x - bb.ctr.x
    if dx < 0:
        return pt.x - (2 * gap) - part_w
    if dx > 0:
        return pt.x + gap
    return pt.x - (2 * gap) - part_w


def _hub_pin_side(hub_part, hub_pin):
    """按引脚在锚点外框上的坐标分侧（MCU/Header 通用）。"""
    bb = _layout_bbox(hub_part)
    if bb is None:
        return "left"
    pt = _pin_abs_pt(hub_pin)
    dx = pt.x - bb.ctr.x
    dy = pt.y - bb.ctr.y
    if abs(dx) >= abs(dy):
        return "left" if dx < 0 else "right"
    return "top" if dy > 0 else "bottom"


def _main_pin_side(main_part, main_pin):
    return _hub_pin_side(main_part, main_pin)


def _mcu_wants_horizontal(part):
    """贴片 R/C 等 2-pin 被动件在 MCU 图上应横放（与水平连线一致）。"""
    ref = str(getattr(part, "ref", "") or "").upper()
    return ref.startswith("R") or ref.startswith("C")


def _mcu_horizontal_tx(part):
    """
    返回使器件「宽 >= 高」的旋转（仅旋转、不平移）。
    TG032 库中 R_0603 默认 0° 为竖直（pin 上下），需旋 90° 才横放。
    """
    pb = getattr(part, "place_bbox", None) or getattr(part, "bbox", None)
    if pb is None:
        return Tx()
    tx = Tx()
    bb = pb * tx
    if bb.w < bb.h:
        c = bb.ctr
        tx = tx.move(-c).rot_90cw().move(c)
    return tx


def _mcu_layout_bbox(part):
    """MCU 布局用外框（被动件按横放后的尺寸算列宽/行高）。"""
    pb = getattr(part, "place_bbox", None) or getattr(part, "bbox", None)
    if pb is None:
        return _layout_bbox(part)
    base = _mcu_horizontal_tx(part) if _mcu_wants_horizontal(part) else Tx()
    try:
        return pb * base
    except Exception:
        return _layout_bbox(part)


def _mcu_pin_local_pt(pin, base_tx):
    """引脚在 base_tx 旋转下的坐标（不含平移）。"""
    base = getattr(pin, "place_pt", None) or pin.pt
    return (base * base_tx).round()


def _mcu_place_part_pin_to_y(part, x_left, row_y, grid, anchor_pin):
    """
    横放被动件，使 anchor_pin 与 MCU 引脚同一 row_y（水平短线的前提）。
    x_left 为器件放置外框左缘目标 X。
    """
    if anchor_pin is None:
        _place_part_row_y(part, x_left, row_y, grid)
        return
    base = _mcu_horizontal_tx(part) if _mcu_wants_horizontal(part) else Tx()
    pb = getattr(part, "place_bbox", None) or getattr(part, "bbox", None)
    if pb is None:
        part.tx = base.move(Point(x_left, row_y).snap(grid))
        return
    bb = pb * base
    pin_local = _mcu_pin_local_pt(anchor_pin, base)
    # 仅 X 吸附网格，Y 保持与 MCU pin 严格共线。
    ox = Point(x_left - bb.min.x, 0).snap(grid).x
    oy = row_y - pin_local.y
    part.tx = base.move(Point(ox, oy))


def _ensure_anchor_toward_hub(part, anchor_pin, outward_sign):
    """
    确保 2-pin 横放被动件的 anchor 引脚在 hub 方向侧。
    outward_sign < 0 表示链向左展开（hub 在右），> 0 则反之。
    若 anchor 在反侧，则围绕器件中心旋转 180° 交换引脚。
    """
    if not _mcu_wants_horizontal(part):
        return
    pins = getattr(part, "pins", [])
    if len(pins) != 2 or anchor_pin is None:
        return
    other = [p for p in pins if p is not anchor_pin]
    if not other:
        return
    ap = _mcu_pin_route_pt(anchor_pin)
    op = _mcu_pin_route_pt(other[0])
    wrong = (
        (outward_sign < 0 and ap.x < op.x)
        or (outward_sign > 0 and ap.x > op.x)
    )
    if not wrong:
        return
    bb = _placement_bbox(part)
    if bb is None:
        return
    cx, cy = bb.ctr.x, bb.ctr.y
    part.tx = part.tx.move(Point(-cx, -cy)).rot(180).move(Point(cx, cy))


def _place_part_row_y(part, x_min, row_y, grid, anchor_pin=None):
    """把器件放在 x_min；若给 anchor_pin 则该脚 Y=row_y，否则外框竖直居中。"""
    if anchor_pin is not None:
        _mcu_place_part_pin_to_y(part, x_min, row_y, grid, anchor_pin)
        return
    base = _mcu_horizontal_tx(part) if _mcu_wants_horizontal(part) else Tx()
    pb = getattr(part, "place_bbox", None) or getattr(part, "bbox", None)
    if pb is None:
        part.tx = base.move(Point(x_min, row_y).snap(grid))
        return
    bb = pb * base
    h = max(bb.h, grid)
    part.tx = base.move(Point(x_min, row_y - h / 2).snap(grid))


def _mcu_anchor_main_center(node, main_part, parts, grid):
    """MCU 固定在组中心锚点 (0,0)，外围相对它排布。"""
    main_part.tx = Tx().move(Point(0, 0).snap(grid))
    node._human_readable_main_part = main_part


def _mcu_place_pin_side_chains(
    node, main_part, chains, gap, grid
):
    """
    TK—R—MCU 短链：按 MCU 引脚所在侧外扩，与引脚同一水平线。
    chains: [(resistor, tk_or_none, main_pin), ...]
    """
    for resistor, tk, main_pin in chains:
        if main_pin is None:
            continue
        side = _main_pin_side(main_part, main_pin)
        row_y = _mcu_pin_route_pt(main_pin).y
        mp_pt = _mcu_pin_route_pt(main_pin)
        parts_out = []
        if resistor is not None:
            parts_out.append(resistor)
        if tk is not None:
            parts_out.append(tk)
        if not parts_out:
            continue
        if side == "right":
            x_edge = mp_pt.x + gap
            prev = main_part
            for part in parts_out:
                bb = _mcu_layout_bbox(part)
                if bb is None:
                    continue
                pin = _chain_neighbor_pin(part, prev, node, set(node.parts))
                if pin is None:
                    _, pin = _pair_pins_to_main(part, main_part, node=node)
                _mcu_place_part_pin_to_y(part, x_edge, row_y, grid, pin)
                prev = part
                x_edge += max(bb.w, grid) + gap
        elif side == "left":
            total_w = sum(
                max((_mcu_layout_bbox(p).w if _mcu_layout_bbox(p) else grid), grid)
                for p in parts_out
            )
            total_w += max(0, len(parts_out) - 1) * gap
            x_edge = mp_pt.x - gap - total_w
            prev = main_part
            for part in parts_out:
                bb = _mcu_layout_bbox(part)
                if bb is None:
                    continue
                w = max(bb.w, grid)
                pin = _chain_neighbor_pin(part, prev, node, set(node.parts))
                if pin is None:
                    _, pin = _pair_pins_to_main(part, main_part, node=node)
                _mcu_place_part_pin_to_y(part, x_edge, row_y, grid, pin)
                _mcu_mark_left_touch_key_render(part)
                prev = part
                x_edge += w + gap
        else:
            if resistor is not None:
                _mcu_place_io_on_main_pin(
                    node, main_part, resistor, gap, grid, side=side
                )
            if tk is not None:
                _mcu_place_io_on_main_pin(node, main_part, tk, gap, grid, side=side)


def _mcu_collect_pin_chains(node, main_part, parts, part_adj, io_series, tk_parts):
    """IO 串阻 + TK：按 MCU 引脚分行，供引脚侧短链摆放。"""
    chains = []
    seen_r = set()
    for part in io_series:
        if part in seen_r:
            continue
        mp, _ = _pair_pins_to_main(part, main_part, node=node)
        if mp is None:
            continue
        tk = _tk_partner_for_resistor(part, main_part, part_adj)
        chains.append((part, tk, mp))
        seen_r.add(part)
    for tk in tk_parts:
        if tk in {c[1] for c in chains if c[1]}:
            continue
        mp, _ = _pair_pins_to_main(tk, main_part, node=node)
        if mp is None:
            continue
        chains.append((None, tk, mp))
    chains.sort(key=lambda item: _mcu_pin_route_pt(item[2]).y)
    return chains


def _is_colinear_chain_part(part, hub_part):
    """可排在锚点引脚共线上的串联器件（2 脚被动/指示/触摸焊盘）。"""
    if part is hub_part:
        return False
    ref = str(getattr(part, "ref", "") or "").upper()
    if ref.startswith(("R", "C", "D", "LED", "TK")):
        return True
    if len(getattr(part, "pins", [])) > 3:
        return False
    return ref.startswith("D")


def _colinear_chain_sort_key(part):
    """星型网多器件时：串阻优先，其次 LED/二极管，再电容。"""
    ref = str(getattr(part, "ref", "") or "").upper()
    if ref.startswith("R"):
        return (0, ref)
    if ref.startswith(("D", "LED")):
        return (1, ref)
    if ref.startswith("C"):
        return (2, ref)
    if ref.startswith("TK"):
        return (3, ref)
    return (4, ref)


def _chain_neighbor_pin(part, neighbor, node, part_set):
    """part 上与 neighbor 共网的引脚。"""
    for pin in getattr(part, "pins", []):
        net = getattr(pin, "net", None)
        if net is None:
            continue
        if neighbor in node._net_connected_parts(net, allowed_parts=part_set):
            return pin
    return None


def _walk_colinear_chain(
    node,
    hub_part,
    anchor_pin,
    part_set,
    used_parts,
    stop_parts=None,
    skip_power_nets=True,
):
    """
    从锚点（MCU/Header 等）某一引脚沿网向外走，得到共线链 [hub, p1, p2, ...]。
    stop_parts 内的器件不会入链（如 MCU 不应出现在 Header 链上）。
    """
    if anchor_pin is None:
        return [hub_part], anchor_pin
    chain = [hub_part]
    visited = {id(hub_part)}
    prev = hub_part
    stop = set(stop_parts or ())

    first_step = True
    while True:
        candidates = []
        # 首步只沿 anchor_pin 那根网走，不扫 hub 全部引脚；
        # 否则字母序靠前的器件会被错误抢给不相关的 MCU 引脚。
        pins_to_scan = (
            [anchor_pin] if first_step and prev is hub_part
            else getattr(prev, "pins", [])
        )
        for pin in pins_to_scan:
            net = getattr(pin, "net", None)
            if net is None:
                continue
            if skip_power_nets and node._is_power_net_name(_net_label(net)):
                continue
            net_parts = list(
                node._net_connected_parts(net, allowed_parts=part_set)
            )
            for p in net_parts:
                if id(p) in visited:
                    continue
                if p is prev:
                    continue
                if p in stop:
                    continue
                if not _is_colinear_chain_part(p, hub_part):
                    continue
                if id(p) in used_parts:
                    continue
                candidates.append(p)
        if not candidates:
            break
        candidates.sort(key=_colinear_chain_sort_key)
        nxt = candidates[0]
        chain.append(nxt)
        visited.add(id(nxt))
        first_step = False
        nxt_pin = _chain_neighbor_pin(nxt, prev, node, part_set)
        if nxt_pin is None:
            break
        prev = nxt

    return chain, anchor_pin


def _mcu_walk_colinear_chain(
    node, main_part, anchor_pin, nets, part_set, used_parts
):
    """MCU 引脚共线链：跳过电源网，链首为 MCU。"""
    return _walk_colinear_chain(
        node,
        main_part,
        anchor_pin,
        part_set,
        used_parts,
        stop_parts=None,
        skip_power_nets=True,
    )


def _find_port_colinear_chains(
    node, hub_part, parts, nets, stop_parts, used_parts=None
):
    """枚举连接器/非 MCU 锚点各引脚上的串联链（可含 GND/VCC 串阻）。"""
    part_set = set(parts)
    used = set(used_parts or ())
    specs = []
    seen_keys = set()
    stop = set(stop_parts or ())
    stop.discard(hub_part)

    for pin in getattr(hub_part, "pins", []):
        chain, anchor = _walk_colinear_chain(
            node,
            hub_part,
            pin,
            part_set,
            used,
            stop_parts=stop,
            skip_power_nets=False,
        )
        if len(chain) < 2:
            continue
        outward = tuple(chain[1:])
        key = (id(anchor), outward)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        specs.append((anchor, chain))
        for p in outward:
            used.add(id(p))
    return specs, used


def _mcu_find_colinear_chains(node, main_part, parts, nets, used_parts=None):
    """枚举各 MCU 引脚上的信号串联链（不含仅主控+去耦的网）。"""
    part_set = set(parts)
    used = set(used_parts or ())
    specs = []
    seen_keys = set()

    for pin in getattr(main_part, "pins", []):
        net = getattr(pin, "net", None)
        if net is None:
            continue
        if node._is_power_net_name(_net_label(net)):
            continue
        chain, anchor = _mcu_walk_colinear_chain(
            node, main_part, pin, nets, part_set, used
        )
        if len(chain) < 2:
            continue
        outward = tuple(chain[1:])
        key = (id(anchor), outward)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        specs.append((anchor, chain))
        for p in outward:
            used.add(id(p))
    return specs


def _place_colinear_chain(node, hub_part, anchor_pin, chain, gap, grid):
    """
    将 chain=[hub, p1, p2, ...] 排在 anchor_pin 同一水平线（左/右引脚）
    或竖直线（上/下引脚）。返回已放置器件集合。
    """
    placed = set()
    if not chain or len(chain) < 2 or anchor_pin is None:
        return placed

    side = _hub_pin_side(hub_part, anchor_pin)
    row_y = _mcu_pin_route_pt(anchor_pin).y
    hp_pt = _mcu_pin_route_pt(anchor_pin)
    outward = [p for p in chain if p is not hub_part]
    part_set = set(getattr(node, "parts", chain))

    if side in ("left", "right"):
        bb_h = _layout_bbox(hub_part)
        outward_sign = -1 if bb_h and hp_pt.x < bb_h.ctr.x else 1
        if outward_sign < 0:
            x_edge = hp_pt.x - gap
            for idx, part in enumerate(outward, start=1):
                bb = _mcu_layout_bbox(part) or _layout_bbox(part)
                if bb is None:
                    continue
                w = max(bb.w, grid)
                x_left = x_edge - w
                prev = chain[idx - 1]
                pin = _chain_neighbor_pin(part, prev, node, part_set)
                if pin is None:
                    _, pin = _pair_pins_to_main(part, hub_part, node=node)
                _mcu_place_part_pin_to_y(part, x_left, row_y, grid, pin)
                _mcu_mark_left_touch_key_render(part)
                _ensure_anchor_toward_hub(part, pin, outward_sign)
                placed.add(part)
                x_edge = x_left - gap
        else:
            x_edge = hp_pt.x + gap
            for idx, part in enumerate(outward, start=1):
                bb = _mcu_layout_bbox(part) or _layout_bbox(part)
                if bb is None:
                    continue
                prev = chain[idx - 1]
                pin = _chain_neighbor_pin(part, prev, node, part_set)
                if pin is None:
                    _, pin = _pair_pins_to_main(part, hub_part, node=node)
                _mcu_place_part_pin_to_y(part, x_edge, row_y, grid, pin)
                _ensure_anchor_toward_hub(part, pin, outward_sign)
                placed.add(part)
                x_edge += max(bb.w, grid) + gap
        return placed

    # 上/下引脚：沿竖直方向外扩（被动件仍横放，脚 Y 对齐）
    col_x = hp_pt.x
    if side == "top":
        y_edge = hp_pt.y + gap
        for idx, part in enumerate(outward, start=1):
            bb = _mcu_layout_bbox(part)
            if bb is None:
                continue
            h = max(bb.h, grid)
            prev = chain[idx - 1]
            pin = _chain_neighbor_pin(part, prev, node, part_set)
            if pin is None:
                _, pin = _pair_pins_to_main(part, hub_part, node=node)
            _mcu_place_part_pin_to_y(part, col_x, y_edge, grid, pin)
            placed.add(part)
            y_edge += h + gap
    else:
        y_edge = hp_pt.y - gap
        for idx, part in enumerate(outward, start=1):
            bb = _mcu_layout_bbox(part)
            if bb is None:
                continue
            h = max(bb.h, grid)
            prev = chain[idx - 1]
            pin = _chain_neighbor_pin(part, prev, node, part_set)
            if pin is None:
                _, pin = _pair_pins_to_main(part, hub_part, node=node)
            _mcu_place_part_pin_to_y(part, col_x, y_edge - h, grid, pin)
            placed.add(part)
            y_edge -= h + gap
    return placed


def _mcu_place_colinear_chain(
    node, main_part, anchor_pin, chain, gap, grid
):
    return _place_colinear_chain(node, main_part, anchor_pin, chain, gap, grid)


def _apply_connector_port_layout(
    node, main_part, connectors, parts, nets, gap, grid, used_parts=None
):
    """
    Header 等连接器：每引脚向外共线排 R/C 串链，遇 MCU 即止。
    返回 (已放置器件集合, 各链器件集合列表)。
    """
    placed = set()
    part_sets = []
    if not connectors or not nets:
        return placed, part_sets

    stop = {main_part} | set(connectors)
    used = set(used_parts or ())
    for conn in sorted(connectors, key=node._part_ref_key):
        stop_parts = stop - {conn}
        specs, used = _find_port_colinear_chains(
            node, conn, parts, nets, stop_parts, used_parts=used
        )
        for anchor_pin, chain in specs:
            chain_placed = _place_colinear_chain(
                node, conn, anchor_pin, chain, gap, grid
            )
            if chain_placed:
                placed |= chain_placed
                part_sets.append(frozenset(chain_placed | {conn}))
    return placed, part_sets


def _all_colinear_part_sets(node):
    """MCU 与连接器端口共线链的网集合（布线/stub 白名单）。"""
    sets = list(getattr(node, "_mcu_colinear_part_sets", None) or [])
    sets += list(getattr(node, "_connector_port_part_sets", None) or [])
    return sets


def _header_port_chain_parts(node):
    """Header 端口共线链上的器件（含连接器与串阻/电容链）。"""
    parts = set()
    for cset in getattr(node, "_connector_port_part_sets", None) or []:
        parts |= set(cset)
    return parts


def _mcu_net_bridges_mcu_and_header(node, main_part, net_parts):
    """
    网是否同时触及 MCU 与 Header 端口链。
    此类桥接网不画贯通导线，两端用 stub/同名 label 连通。
    """
    if main_part is None or main_part not in net_parts:
        return False
    header_parts = _header_port_chain_parts(node)
    if not header_parts:
        return False
    return bool((net_parts - {main_part}) & header_parts)


def _mcu_net_connector_named_signal(node, net, net_parts, roles=None):
    """
    Header 上的具名通信网（/TX、/RX 等）。
    原理图仅用 global_label 连通，不画 R10–Header 本地导线。
    """
    name = _net_label(net)
    if node._is_power_net_name(name):
        return False
    label_u = name.upper()
    if not (
        str(name).startswith("/")
        or _token_in_text(label_u, _MCU_COMM_NET_TOKENS)
    ):
        return False
    for part in net_parts:
        if _mcu_part_is_connector(part, roles):
            return True
    return False


def _mcu_preserve_label_only_stub(net):
    """纯标签网（无本地线）：route 不得清 stub 后再拉线。"""
    return bool(
        getattr(net, "_fork_overflow_stub", False)
        or getattr(net, "_mcu_header_bridge_stub", False)
        or getattr(net, "_mcu_connector_signal_stub", False)
    )


def _mcu_apply_label_only_stub(node, net, pins):
    """标记整网 stub 并删除已有导线（电源桥接等纯标签网）。"""
    net._stub = True
    net.stub = True
    _mcu_mark_net_stub(net, pins)
    wires = getattr(node, "wires", {})
    if net in wires:
        del wires[net]


def _mcu_place_io_on_main_pin(node, main_part, part, gap, grid, side=None):
    """串阻/电容等：接 MCU 的脚与 MCU pin 同 Y，水平横放。"""
    mp, pp = _pair_pins_to_main(part, main_part, node=node, prefer_signal=True)
    if mp is None or pp is None:
        return False
    row_y = _mcu_pin_route_pt(mp).y
    bb = _mcu_layout_bbox(part) or _layout_bbox(part)
    if bb is None:
        return False
    w = max(bb.w, grid)
    side = side or _main_pin_side(main_part, mp)
    mp_pt = _mcu_pin_route_pt(mp)
    if side in ("top", "bottom"):
        x_left = mp_pt.x - w / 2
    else:
        x_left = _mcu_x_outward_of_pin(main_part, mp, w, gap)
    _mcu_place_part_pin_to_y(part, x_left, row_y, grid, pp)
    if side == "left":
        _mcu_mark_left_touch_key_render(part)
    return True


def _mcu_force_place_decouple_at_signal_pin(node, main_part, part, gap, grid):
    """去耦电容必须贴在 MCU 信号脚外侧（覆盖共线/力导向留下的错误坐标）。"""
    if not _mcu_place_io_on_main_pin(node, main_part, part, gap, grid):
        return False
    ctx = _mcu_decouple_ground_context(node, main_part, part)
    if ctx is None:
        return True

    signal_pin = ctx["cap_signal_pin"]
    old_signal_pt = _mcu_pin_route_pt(signal_pin)
    mcu_signal_pt = _mcu_pin_route_pt(ctx["mcu_signal_pin"])
    signal_pt = Point(old_signal_pt.x, mcu_signal_pt.y)
    base = Tx().rot(90)
    signal_local = (signal_pin.pt * base).round()
    part.tx = base.move(Point(signal_pt.x - signal_local.x, signal_pt.y - signal_local.y))
    part._mcu_decouple_ground_context = ctx
    return True


def _mcu_is_ground_net(node, net):
    name = _net_label(net)
    if not name:
        return False
    text = str(name).upper()
    return node._is_power_net_name(name) and (
        _token_in_text(text, _GROUND_TOKENS) or "VSS" in text
    )


def _mcu_pin_text(pin):
    return " ".join(
        str(getattr(pin, attr, "") or "").upper()
        for attr in ("name", "num", "func", "function")
    )


def _mcu_decouple_ground_context(node, main_part, cap_part):
    pins = list(getattr(cap_part, "pins", []) or [])
    if len(pins) != 2:
        return None

    ground_pin = None
    signal_pin = None
    mcu_ground_pin = None
    mcu_signal_pin = None
    for pin in pins:
        net = getattr(pin, "net", None)
        if net is None:
            continue
        matching_main = [
            mp for mp in getattr(main_part, "pins", []) if getattr(mp, "net", None) is net
        ]
        if _mcu_is_ground_net(node, net):
            ground_pin = pin
            if matching_main:
                mcu_ground_pin = next(
                    (
                        mp
                        for mp in matching_main
                        if _token_in_text(_mcu_pin_text(mp), _GROUND_TOKENS + ("VSS",))
                    ),
                    matching_main[0],
                )
        elif matching_main:
            signal_pin = pin
            mcu_signal_pin = next(
                (mp for mp in matching_main if not _mcu_pin_looks_like_power(mp)),
                matching_main[0],
            )

    if not (ground_pin and signal_pin and mcu_ground_pin and mcu_signal_pin):
        return None

    signal_text = _mcu_pin_text(mcu_signal_pin)
    if not _token_in_text(signal_text, ("TKCAP", "P35", "CAP")):
        return None

    return {
        "cap": cap_part,
        "cap_ground_pin": ground_pin,
        "cap_signal_pin": signal_pin,
        "mcu_ground_pin": mcu_ground_pin,
        "mcu_signal_pin": mcu_signal_pin,
        "ground_net": ground_pin.net,
        "signal_net": signal_pin.net,
    }


def _route_chain_net_wires(node, net, pins, anchor_part, grid):
    """共线链上的网：水平母线 + 引脚竖 stub（锚点可为 MCU 或 Header）。"""
    pin_pts = [_mcu_pin_route_pt(p) for p in pins]
    net_parts = {p.part for p in pins}
    bus_y = pin_pts[0].y
    if anchor_part in net_parts:
        for p in pins:
            if p.part is anchor_part:
                bus_y = _mcu_pin_route_pt(p).y
                break
    x_min = min(pt.x for pt in pin_pts)
    x_max = max(pt.x for pt in pin_pts)
    segs = [Segment(Point(x_min, bus_y), Point(x_max, bus_y))]
    for pt in pin_pts:
        stub_end = Point(pt.x, bus_y)
        if pt != stub_end:
            segs.append(Segment(copy.copy(pt), stub_end))
    return segs


def _mcu_route_chain_net_wires(node, net, pins, main, grid):
    return _route_chain_net_wires(node, net, pins, main, grid)


def _mcu_apply_label_stub_policy(node, nets, **options):
    """
    MCU 板：仅对无法本地直线化的长网/多脚网使用 label，2-pin 星型支路保留 wire。
    """
    if not options.get("auto_stub", True):
        return
    topo = getattr(node, "_last_topology_result", None) or {}
    main_part = topo.get("main_part") or getattr(
        node, "_human_readable_main_part", None
    )
    grid = int(options.get("grid", 100))
    max_local = int(options.get("mcu_local_wire_max_dist", 8 * grid))
    stubbed = 0
    for net in nets:
        if getattr(net, "_stub_explicit", False) or getattr(net, "stub", False):
            continue
        name = _net_label(net)
        net_parts = list(node._net_connected_parts(net))
        if node._is_power_net_name(name):
            continue
        if _mcu_net_keep_local_wire(net_parts, main_part):
            continue
        if len(net_parts) == 2:
            pts = []
            for part in net_parts:
                for pin in part.pins:
                    if getattr(pin, "net", None) is net:
                        pts.append(_pin_abs_pt(pin))
            if len(pts) == 2:
                dist = abs(pts[0].x - pts[1].x) + abs(pts[0].y - pts[1].y)
                if dist <= max_local:
                    continue
        net._stub = True
        net._stub_explicit = False
        for pin in net.get_pins():
            pin.stub = True
        stubbed += 1
    if stubbed and options.get("schematic_progress", False):
        from skidl.logger import active_logger

        active_logger.info(
            "[mcu] label_stub_policy: stubbed %d outward nets" % stubbed
        )


def _placement_bbox(part):
    """布线/摆放外框（place_bbox×tx），与 KiCad 黄框及去重叠判定一致。"""
    tx = getattr(part, "tx", None)
    if tx is None:
        return _layout_bbox(part)
    pb = getattr(part, "place_bbox", None)
    if pb is None:
        return _layout_bbox(part)
    try:
        return pb * tx
    except Exception:
        return _layout_bbox(part)


def _layout_bbox_intersects(bb_a, bb_b):
    """外框是否相交（用于 MCU keepout）。"""
    if bb_a is None or bb_b is None:
        return False
    return not (
        bb_a.max.x < bb_b.min.x
        or bb_a.min.x > bb_b.max.x
        or bb_a.max.y < bb_b.min.y
        or bb_a.min.y > bb_b.max.y
    )


def _mcu_place_connectors_below_main(node, main_part, connectors, gap, grid):
    """
    连接器排在 MCU place_bbox 下方（原理图页面上 U3 之下）。
    SKiDL 为 Y 向上，导出 KiCad 会 Y 翻转，故用 min.y 侧而不是 max.y。
    """
    if not connectors:
        return
    main_bb = _placement_bbox(main_part)
    if main_bb is None:
        return
    max_conn_h = max(
        (getattr(p.place_bbox, "h", 0) or grid for p in connectors),
        default=grid,
    )
    margin = max(4 * gap, grid * 4)
    conn_y = main_bb.min.y - margin - max_conn_h
    _place_parts_in_row(
        node,
        sorted(connectors, key=node._part_ref_key),
        main_bb.min.x,
        conn_y,
        gap,
        grid,
    )


def _mcu_part_is_connector(part, roles=None):
    """是否连接器（keepout 只应推开此类，勿动贴引脚的 R/C/LED）。"""
    ref = str(getattr(part, "ref", "") or "").upper()
    if roles and roles.get(part) == "connector":
        return True
    return ref.startswith(("J", "P", "CN", "H", "X"))


def _mcu_push_out_of_main_keepout(
    node, main_part, parts, gap, grid, exclude=None, connectors_only=False, roles=None
):
    """
    把与 MCU 膨胀 place_bbox 重叠的器件推开。
    connectors_only=True 时仅移动 Header 等；贴引脚的 R/C/LED 必须 exclude，否则会整排甩到 MCU 下方。
    """
    from skidl.schematics.trunk_layout import _place_parts_in_row

    main_bb = _placement_bbox(main_part)
    if main_bb is None:
        return
    skip = set(exclude or ())
    skip.add(main_part)
    pad = max(gap, grid * 2)
    keep_min = Point(main_bb.min.x - pad, main_bb.min.y - pad)
    keep_max = Point(main_bb.max.x + pad, main_bb.max.y + pad)
    keep_box = BBox(keep_min, keep_max)
    overlapping = []
    for part in parts:
        if part in skip:
            continue
        if connectors_only and not _mcu_part_is_connector(part, roles):
            continue
        bb = _placement_bbox(part)
        if bb is None:
            continue
        if _layout_bbox_intersects(keep_box, bb):
            overlapping.append(part)
    if overlapping:
        max_h = max(
            (getattr(p.place_bbox, "h", 0) or grid for p in overlapping),
            default=grid,
        )
        escape_y = main_bb.min.y - pad - max_h
        _place_parts_in_row(
            node,
            sorted(overlapping, key=node._part_ref_key),
            main_bb.min.x,
            escape_y,
            gap,
            grid,
        )


def apply_mcu_connector_keepout_fixup(node, parts, roles, **options):
    """
    布线失败 labels-only 回退后补一刀：Header 等必须在主 IC place_bbox 下方。
    不依赖 topology 识别是否仍为 mcu。
    """
    if not parts:
        return
    main = getattr(node, "_human_readable_main_part", None)
    if main is None:
        ic_parts = [
            p
            for p in parts
            if str(getattr(p, "ref", "") or "").upper().startswith("U")
        ]
        if ic_parts:
            main = max(ic_parts, key=lambda p: len(getattr(p, "pins", [])))
    if main is None:
        return

    connectors = []
    for part in parts:
        ref = str(getattr(part, "ref", "") or "").upper()
        role = roles.get(part, "other")
        if role == "connector" or ref.startswith(("J", "P", "CN", "H", "X")):
            connectors.append(part)
    if not connectors:
        return

    grid = int(options.get("grid", 100))
    gap = options.get("topology_gap") or options.get(
        "trunk_gap", max(int(options.get("blk_int_pad", 100)), grid * 2)
    )
    _mcu_place_connectors_below_main(node, main, connectors, gap, grid)
    _mcu_push_out_of_main_keepout(
        node,
        main,
        parts,
        gap,
        grid,
        connectors_only=True,
        roles=roles,
    )


def apply_generic_mcu_layout(
    node, parts, roles, main_part, topology, trunk_map, nets=None, **options
):
    """
    人工 MCU 风格布局：MCU 居中；信号串联链按引脚侧共线；上=去耦；下=连接器。
    """
    if not parts or main_part is None:
        return

    node._driver_rail_plan = {"enabled": False}
    node._mcu_manual_pnr = True

    grid = int(options.get("grid", 100))
    blk_pad = int(options.get("blk_int_pad", 100))
    gap = options.get("topology_gap") or options.get(
        "trunk_gap", max(blk_pad, grid * 2)
    )

    from skidl.schematics.trunk_layout import (
        _place_parts_in_row,
        _resolve_overlaps,
        build_part_adjacency,
    )

    _mcu_anchor_main_center(node, main_part, parts, grid)
    main_bbox = _layout_bbox(main_part)
    if main_bbox is None:
        return

    anchor = {main_part}
    placed = {main_part}

    decouple = sorted(
        topology.get("decouple_parts", set()), key=node._part_ref_key
    )
    clock = sorted(topology.get("clock_parts", set()), key=node._part_ref_key)
    reset = sorted(topology.get("reset_parts", set()), key=node._part_ref_key)
    boot = sorted(topology.get("boot_parts", set()), key=node._part_ref_key)
    io_series = sorted(
        topology.get("io_series_parts", set()), key=node._part_ref_key
    )
    connectors = sorted(
        topology.get("connector_parts", set()), key=node._part_ref_key
    )
    indicators = sorted(
        topology.get("indicator_parts", set()), key=node._part_ref_key
    )
    tk_parts = sorted(topology.get("tk_parts", set()), key=node._part_ref_key)

    part_adj = (
        build_part_adjacency(parts, nets)
        if nets
        else {id(p): set() for p in parts}
    )

    # 去耦电容改在共线/贴脚阶段按 MCU 信号引脚侧摆放，不再统一排到 MCU 上方。

    # 左：时钟/复位 + TK 链与 pin 对齐
    left_misc = clock + reset + boot
    if left_misc:
        misc_x = main_bbox.min.x - (5 * gap)
        y = main_bbox.min.y
        for part in left_misc:
            bb = _layout_bbox(part)
            if bb is None:
                continue
            part.tx = Tx().move(Point(misc_x - bb.w, y))
            y += max(bb.h, grid) + gap
            placed.add(part)

    left_connectors = [
        p for p in connectors if _io_side_score(node, p) <= 0
    ]
    right_connectors = [
        p for p in connectors if _io_side_score(node, p) > 0
    ]
    all_connectors = sorted(
        left_connectors + right_connectors, key=node._part_ref_key
    )
    node._connector_port_part_sets = []
    connector_port_placed = set()
    if all_connectors:
        _mcu_place_connectors_below_main(
            node, main_part, all_connectors, gap, grid
        )
        placed.update(all_connectors)

    _mcu_push_out_of_main_keepout(
        node,
        main_part,
        parts,
        gap,
        grid,
        exclude=anchor,
        connectors_only=True,
        roles=roles,
    )
    _resolve_overlaps(node, parts, grid, max(gap, blk_pad), exclude=anchor)

    # 引脚分叉布局 + 串联共线链（去重叠之后，避免被挤离引脚行）。
    node._mcu_colinear_part_sets = []
    node._mcu_fork_specs = []
    node._mcu_fork_part_sets = []
    colinear_placed = set(connector_port_placed)
    mcu_colinear_used = {id(p) for p in connector_port_placed}
    if nets and options.get("mcu_fork_layout", True):
        from .mcu_fork import pin_handled_by_fork, place_all_pin_forks

        _fork_opts = dict(options)
        _fork_opts.setdefault("grid", grid)
        _fork_opts.setdefault("topology_gap", gap)
        _fork_specs, placed_fork, mcu_colinear_used, fork_sets = place_all_pin_forks(
            node,
            main_part,
            parts,
            nets,
            roles,
            mcu_colinear_used,
            **_fork_opts,
        )
        if placed_fork:
            colinear_placed |= placed_fork
            placed |= placed_fork
            anchor |= placed_fork
        for fset in fork_sets:
            node._mcu_colinear_part_sets.append(fset)

    if nets:
        from .mcu_fork import pin_handled_by_fork

        for anchor_pin, chain in _mcu_find_colinear_chains(
            node, main_part, parts, nets, used_parts=mcu_colinear_used
        ):
            if pin_handled_by_fork(node, anchor_pin):
                continue
            chain_placed = _mcu_place_colinear_chain(
                node, main_part, anchor_pin, chain, gap, grid
            )
            if chain_placed:
                colinear_placed |= chain_placed
                node._mcu_colinear_part_sets.append(
                    frozenset(chain_placed | {main_part})
                )
                placed |= chain_placed
                anchor |= chain_placed
                for p in chain_placed:
                    mcu_colinear_used.add(id(p))

    # Header 引脚链在 fork 之后，跳过已被 fork 占用的器件（如 R10）。
    if all_connectors and nets:
        connector_port_placed, node._connector_port_part_sets = (
            _apply_connector_port_layout(
                node,
                main_part,
                all_connectors,
                parts,
                nets,
                gap,
                grid,
                used_parts=mcu_colinear_used,
            )
        )
        if connector_port_placed:
            placed |= connector_port_placed
            anchor |= connector_port_placed
            colinear_placed |= connector_port_placed

    # 仅 TK 短链（共线未覆盖的 R+TK 对）
    pin_chains = _mcu_collect_pin_chains(
        node, main_part, parts, part_adj, io_series, tk_parts
    )
    pin_chains = [
        (r, tk, mp)
        for r, tk, mp in pin_chains
        if (r is None or r not in colinear_placed)
        and (tk is None or tk not in colinear_placed)
    ]
    if pin_chains:
        _mcu_place_pin_side_chains(node, main_part, pin_chains, gap, grid)
        for r, tk, _ in pin_chains:
            if r is not None:
                placed.add(r)
                anchor.add(r)
                colinear_placed.add(r)
            if tk is not None:
                placed.add(tk)
                anchor.add(tk)
                colinear_placed.add(tk)

    # 其余 IO/指示器件：单颗贴对应 MCU 引脚侧（分叉已管器件不再贴回引脚行）
    fork_reserved = set(getattr(node, "_mcu_fork_reserved_parts", None) or [])

    def _skip_post_fork_place(part):
        return part in colinear_placed or part in fork_reserved

    for part in io_series:
        if _skip_post_fork_place(part):
            continue
        if _mcu_place_io_on_main_pin(node, main_part, part, gap, grid):
            placed.add(part)
            anchor.add(part)
    for part in indicators:
        if _skip_post_fork_place(part):
            continue
        if _mcu_place_io_on_main_pin(node, main_part, part, gap, grid):
            placed.add(part)
            anchor.add(part)
    # 去耦：始终以信号脚为准重摆（避免共线链/力导向把它留在错误一侧）
    for part in decouple:
        if _mcu_force_place_decouple_at_signal_pin(
            node, main_part, part, gap, grid
        ):
            placed.add(part)
            anchor.add(part)
            colinear_placed.add(part)

    # 勿再对全表做 keepout：贴引脚的 R/C/LED/TK 与膨胀 MCU 框必然相交，会被误排到 MCU 底下一行。
    if all_connectors:
        _mcu_place_connectors_below_main(
            node, main_part, all_connectors, gap, grid
        )
        _mcu_push_out_of_main_keepout(
            node,
            main_part,
            parts,
            gap,
            grid,
            exclude=anchor,
            connectors_only=True,
            roles=roles,
        )

    topology["fallback"] = False


def _mcu_route_pins(node, net):
    """MCU 本地布线用引脚（不受 auto_stub 的 pin.stub 影响）。"""
    from skidl.schematics.place import is_net_terminal

    return [
        pin
        for pin in net.pins
        if pin.part in node.parts and not is_net_terminal(pin.part)
    ]


def _wire_crosses_sibling_pin(pins, p1, p2):
    """检查水平 wire 是否穿过同器件的另一引脚（不同网），会产生短路。"""
    x_lo, x_hi = (min(p1.x, p2.x), max(p1.x, p2.x))
    y = p1.y
    for pin in pins:
        for sib in getattr(pin.part, "pins", []):
            if sib is pin:
                continue
            if getattr(sib, "net", None) is getattr(pin, "net", None):
                continue
            sp = _mcu_pin_route_pt(sib)
            if sp.y == y and x_lo < sp.x < x_hi:
                return True
    return False


def _mcu_point_side_of_body(main_part, pt):
    """路由点相对 MCU 摆放外框中心所在的侧。"""
    bb = _placement_bbox(main_part) or _layout_bbox(main_part)
    if bb is None:
        return None
    dx = pt.x - bb.ctr.x
    dy = pt.y - bb.ctr.y
    if abs(dx) >= abs(dy):
        return "left" if dx < 0 else "right"
    return "top" if dy > 0 else "bottom"


def _mcu_two_pin_endpoints_straddle_body(main_part, pt_a, pt_b):
    """
    两引脚路由点是否在 MCU body 对侧（左-右或上-下）。
    对侧时不应画水平 local wire，否则会横穿器件本体。
    """
    sa = _mcu_point_side_of_body(main_part, pt_a)
    sb = _mcu_point_side_of_body(main_part, pt_b)
    if sa is None or sb is None or sa == sb:
        return False
    return {sa, sb} in ({"left", "right"}, {"top", "bottom"})


def _mcu_reject_two_pin_local_wire(main_part, pt_a, pt_b):
    """MCU 本地 2-pin 线：端点跨 body 对侧则改 stub，不走短直线。"""
    if main_part is None:
        return False
    return _mcu_two_pin_endpoints_straddle_body(main_part, pt_a, pt_b)


def _mcu_mark_net_stub(net, pins):
    """本地线不适用时，整网改 label/stub。"""
    net._stub = True
    net.stub = True
    for pin in pins:
        pin.stub = True


def _mcu_wire_two_pins(p1, p2, bus_y=None):
    """MCU 支路：给定 bus_y 时一根水平线；否则正交 L 型。"""
    if bus_y is not None:
        return [Segment(Point(p1.x, bus_y), Point(p2.x, bus_y))]
    if p1.y == p2.y:
        return [Segment(copy.copy(p1), copy.copy(p2))]
    if p1.x == p2.x:
        return [Segment(copy.copy(p1), copy.copy(p2))]
    y = p1.y
    mid_a = Point(p1.x, y)
    mid_b = Point(p2.x, y)
    segs = []
    if p1 != mid_a:
        segs.append(Segment(copy.copy(p1), mid_a))
    if mid_a != mid_b:
        segs.append(Segment(mid_a, mid_b))
    if mid_b != p2:
        segs.append(Segment(mid_b, copy.copy(p2)))
    return segs


def _mcu_route_decouple_ground_net(node, net, pins, main, grid):
    """Route the local MCU decoupling ground as a lower trunk, not pin stubs."""
    if main is None or not _mcu_is_ground_net(node, net):
        return None

    context = None
    for pin in pins:
        part = getattr(pin, "part", None)
        ctx = getattr(part, "_mcu_decouple_ground_context", None)
        if ctx and ctx.get("ground_net") is net:
            context = ctx
            break
    if context is None:
        return None

    cap_pin = context["cap_ground_pin"]
    mcu_pin = context["mcu_ground_pin"]
    cap_pt = _mcu_pin_route_pt(cap_pin)
    mcu_pt = _mcu_pin_route_pt(mcu_pin)

    trunk_y = mcu_pt.y

    x_min = min(cap_pt.x, mcu_pt.x)
    x_max = max(cap_pt.x, mcu_pt.x)

    segs = [
        Segment(Point(x_min, trunk_y), Point(x_max, trunk_y))
    ]

    cap_drop = Point(cap_pt.x, trunk_y)
    if cap_pt != cap_drop:
        segs.append(
            Segment(Point(cap_pt.x, cap_pt.y), cap_drop)
        )

    mcu_drop = Point(mcu_pt.x, trunk_y)
    if mcu_pt != mcu_drop:
        segs.append(
            Segment(Point(mcu_pt.x, mcu_pt.y), mcu_drop)
        )
    junctions = getattr(node, "junctions", None)
    if junctions is not None:
        junctions.setdefault(net, [])
        for pt in (copy.copy(cap_pt), copy.copy(mcu_drop)):
            if pt not in junctions[net]:
                junctions[net].append(pt)

    symbol_x = int(round(((cap_pt.x + mcu_pt.x) / 2) / grid)) * grid
    symbol_x = max(x_min + (2 * grid), min(x_max - (2 * grid), symbol_x))
    marker = {"net": net, "point": Point(symbol_x, trunk_y)}
    markers = list(getattr(node, "_mcu_power_symbol_points", []) or [])
    if not any(m.get("net") is net and m.get("point") == marker["point"] for m in markers):
        markers.append(marker)
    node._mcu_power_symbol_points = markers

    local_pins = {cap_pin, mcu_pin}
    for pin in pins:
        if pin in local_pins:
            pin.stub = False
            pin._mcu_force_power_symbol_even_if_wired = False
        else:
            pin.stub = True
            pin._mcu_force_power_symbol_even_if_wired = True
    net._stub = False
    net.stub = False
    return segs


def route_mcu_local_nets(node, nets, **options):
    """
    MCU 专用：2-pin 星型支路用短直线/水平总线，不走 switchbox。
    共线链上的多脚网用水平母线 + 竖 stub；分叉 anchor 网用 T 型线段。
    返回已处理的 net 集合。
    """
    topo = getattr(node, "_last_topology_result", None) or {}
    if topo.get("kind") not in ("mcu", "weak_mcu") or topo.get("fallback"):
        return set()
    if not getattr(node, "_mcu_manual_pnr", False):
        return set()

    main = topo.get("main_part") or getattr(
        node, "_human_readable_main_part", None
    )
    roles = topo.get("roles") or getattr(node, "_part_roles", None)
    handled = set()
    grid = int(options.get("grid", 100))
    colinear_sets = _all_colinear_part_sets(node)

    if options.get("mcu_fork_layout", True):
        from .mcu_fork import (
            find_fork_spec_for_net,
            mark_fork_overflow_stubs,
            route_fork_anchor_net,
        )

        mark_fork_overflow_stubs(node, nets, **options)

    for net in nets:
        if options.get("mcu_fork_layout", True):
            fork_spec = find_fork_spec_for_net(node, net)
            if fork_spec is not None:
                segs = route_fork_anchor_net(node, net, fork_spec, grid)
                if segs:
                    net._stub = False
                    net.stub = False
                    for pin in net.pins:
                        if getattr(pin, "part", None) in getattr(node, "parts", []):
                            pin.stub = False
                    node.wires[net] = segs
                    handled.add(net)
                    continue
        pins = _mcu_route_pins(node, net)
        if len(pins) < 2:
            continue
        decouple_ground_segs = _mcu_route_decouple_ground_net(
            node, net, pins, main, grid
        )
        if decouple_ground_segs:
            node.wires[net] = decouple_ground_segs
            handled.add(net)
            continue
        net_parts = {pin.part for pin in pins}
        if main and _mcu_net_bridges_mcu_and_header(node, main, net_parts):
            net._mcu_header_bridge_stub = True
            _mcu_apply_label_only_stub(node, net, pins)
            handled.add(net)
            continue
        if _mcu_net_connector_named_signal(node, net, net_parts, roles):
            net._mcu_connector_signal_stub = True
            _mcu_apply_label_only_stub(node, net, pins)
            handled.add(net)
            continue
        if _mcu_preserve_label_only_stub(net):
            _mcu_apply_label_only_stub(node, net, pins)
            handled.add(net)
            continue
        if main and not _mcu_net_keep_local_wire(list(net_parts), main):
            # 连接器端口链上的多脚网仍要本地母线
            on_connector_only = False
            for cset in colinear_sets:
                if net_parts <= cset and main not in cset:
                    on_connector_only = True
                    break
            if not on_connector_only:
                continue

        on_colinear = False
        chain_anchor = main
        for cset in colinear_sets:
            if net_parts <= cset:
                on_colinear = True
                if main in cset:
                    chain_anchor = main
                else:
                    for p in net_parts:
                        if _mcu_part_is_connector(p):
                            chain_anchor = p
                            break
                break
        if on_colinear:
            net._stub = False
            net.stub = False
            for pin in pins:
                pin.stub = False
            if len(pins) == 2:
                p1 = _mcu_pin_route_pt(pins[0])
                p2 = _mcu_pin_route_pt(pins[1])
                if main and _mcu_reject_two_pin_local_wire(main, p1, p2):
                    _mcu_mark_net_stub(net, pins)
                elif p1.y == p2.y:
                    if _wire_crosses_sibling_pin(pins, p1, p2):
                        _mcu_mark_net_stub(net, pins)
                    else:
                        node.wires[net] = _mcu_wire_two_pins(p1, p2)
                else:
                    # 两引脚不同行（放置异常），不画线、改用 label 避短路
                    net._stub = True
                    net.stub = True
                    for pin in pins:
                        pin.stub = True
            else:
                node.wires[net] = _route_chain_net_wires(
                    node, net, pins, chain_anchor, grid
                )
            handled.add(net)
            continue

        if len(pins) != 2:
            continue
        # 布局前 auto_stub 可能已标记，本地线需清除以便导出 wire 而非 label。
        # 已决策为 label-only 的网不得清 stub 后再拉线。
        if _mcu_preserve_label_only_stub(net):
            _mcu_apply_label_only_stub(node, net, pins)
            handled.add(net)
            continue
        net._stub = False
        net.stub = False
        for pin in pins:
            pin.stub = False
        p1 = _mcu_pin_route_pt(pins[0])
        p2 = _mcu_pin_route_pt(pins[1])
        if main and _mcu_reject_two_pin_local_wire(main, p1, p2):
            _mcu_mark_net_stub(net, pins)
            handled.add(net)
            continue
        bus_y = p1.y
        if main in net_parts:
            mp = next(p for p in pins if p.part is main)
            bus_y = _mcu_pin_route_pt(mp).y
        node.wires[net] = _mcu_wire_two_pins(p1, p2, bus_y=bus_y)
        for pin in pins:
            pin.stub = False
        net._stub = False
        net.stub = False
        handled.add(net)

    if handled and options.get("schematic_progress", False):
        from skidl.logger import active_logger

        active_logger.info(
            "[mcu] local_wire_route: %d nets" % len(handled)
        )
    return handled


def mcu_stub_remaining_signal_nets(node, nets, handled, **options):
    """
    本地线已布完的 MCU 板：仅对多脚/非 MCU 直连网用 label，2-pin MCU 网保留不 stub。
    避免全图 switchbox 失败触发 labels-only 回退冲掉布局。
    """
    if not getattr(node, "_mcu_manual_pnr", False):
        return set()
    topo = getattr(node, "_last_topology_result", None) or {}
    main = topo.get("main_part") or getattr(node, "_human_readable_main_part", None)
    stubbed = set()
    wired = set(getattr(node, "wires", {}).keys())
    colinear_sets = _all_colinear_part_sets(node)
    for net in nets:
        if net in handled:
            continue
        if getattr(net, "_stub_explicit", False):
            continue
        net_parts = list(node._net_connected_parts(net))
        net_part_set = set(net_parts)
        for cset in colinear_sets:
            if net_part_set <= cset:
                break
        else:
            cset = None
        if cset is not None and len(net_parts) > 1:
            continue
        # 多器件信号网保留：它们是真实器件间连接，不应被 stub 化产生漂浮 label。
        # 但 power 网（含 GND/VCC 等）用电源符号更合理，仍需 stub。
        name = _net_label(net)
        if len(net_parts) > 1 and not node._is_power_net_name(name):
            continue
        # 剩余网 = 单器件悬空网（如 MCU 引脚 /PWM）+ 多器件 power 网一律 stub，
        # 并删除 route_straight_nets 可能画出的穿越相邻引脚 L 形线。
        net._stub = True
        net._stub_explicit = False
        for pin in net.get_pins():
            pin.stub = True
        wires = getattr(node, "wires", {})
        if net in wires:
            del wires[net]
        stubbed.add(net)
    if stubbed and options.get("schematic_progress", False):
        from skidl.logger import active_logger

        active_logger.info(
            "[mcu] stub_remaining_signals: %d nets" % len(stubbed)
        )
    return stubbed


def mcu_route_rank_bias(net, topology):
    """
    mcu matched 时的布线顺序偏置（越小越先布）。
    不改变网表连接，仅影响 route 排序。
    """
    if not topology or topology.get("kind") != "mcu":
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
    if in_bucket("ground_nets"):
        return -500
    if _token_in_text(name, ("OSC", "HSE", "LSE", "XI", "XO", "CRYSTAL")):
        return -400
    if _token_in_text(name, ("NRST", "RESET", "BOOT")):
        return -350
    if _token_in_text(name, _MCU_COMM_NET_TOKENS):
        return -300
    if _token_in_text(name, _MCU_IO_NET_TOKENS):
        return -200
    return 0
