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


def _pair_pins_to_main(part, main_part):
    """返回 (main_pin, part_pin) 若二者共网。"""
    for pin in part.pins:
        net = getattr(pin, "net", None)
        if net is None:
            continue
        for mp in main_part.pins:
            if getattr(mp, "net", None) is net:
                return mp, pin
    return None, None


def _main_pin_side(main_part, main_pin):
    """按引脚在 MCU 外框上的坐标分侧（比 orientation 更稳，适配 CA51/SOP）。"""
    bb = _layout_bbox(main_part)
    if bb is None:
        return "left"
    pt = _pin_abs_pt(main_pin)
    dx = pt.x - bb.ctr.x
    dy = pt.y - bb.ctr.y
    if abs(dx) >= abs(dy):
        return "left" if dx < 0 else "right"
    return "top" if dy > 0 else "bottom"


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


def _place_part_row_y(part, x_min, row_y, grid):
    """把器件放在 x_min，中心 Y 对齐 row_y（与 MCU pin 同行）；R/C 强制横放。"""
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


def _mcu_place_left_pin_chains(
    node, main_part, chains, main_bbox, gap, grid, tk_on_far_left=True
):
    """
    左侧链：TK — R — MCU pin 同行短直线。
    chains: [(resistor, tk_or_none, main_pin), ...] 已按 pin Y 排序。
    """
    max_r_w = max(
        (_mcu_layout_bbox(r).w if _mcu_layout_bbox(r) else grid for r, _, _ in chains),
        default=grid,
    )
    max_tk_w = grid
    for _, tk, _ in chains:
        if tk is not None:
            tbb = _mcu_layout_bbox(tk)
            if tbb:
                max_tk_w = max(max_tk_w, tbb.w)

    left_pin_xs = [
        _pin_abs_pt(p).x
        for p in main_part.pins
        if _main_pin_side(main_part, p) == "left"
    ]
    if not left_pin_xs:
        left_pin_xs = [_pin_abs_pt(chains[0][2]).x] if chains else [main_bbox.min.x]
    pin_col_x = min(left_pin_xs)
    r_x = pin_col_x - (2 * gap) - max_r_w
    tk_x = r_x - gap - max_tk_w

    for resistor, tk, main_pin in chains:
        row_y = _pin_abs_pt(main_pin).y
        if resistor is not None:
            _place_part_row_y(resistor, r_x, row_y, grid)
        if tk is not None:
            _place_part_row_y(tk, tk_x, row_y, grid)


def _mcu_collect_left_chains(node, main_part, parts, part_adj, io_series, tk_parts):
    """触摸 MCU：串阻与 TK 默认整列排在 MCU 左侧，按 pin Y 逐行对齐。"""
    chains = []
    seen_r = set()
    for part in io_series:
        if part in seen_r:
            continue
        mp, _ = _pair_pins_to_main(part, main_part)
        if mp is None:
            continue
        tk = _tk_partner_for_resistor(part, main_part, part_adj)
        chains.append((part, tk, mp))
        seen_r.add(part)
    for tk in tk_parts:
        if tk in {c[1] for c in chains if c[1]}:
            continue
        mp, _ = _pair_pins_to_main(tk, main_part)
        if mp is None:
            continue
        chains.append((None, tk, mp))
    chains.sort(key=lambda item: _pin_abs_pt(item[2]).y)
    return chains


def _mcu_place_comm_led_block(
    node, main_part, parts, main_bbox, gap, grid, part_adj
):
    """UART/LED 等通信指示：贴在 MCU 左上侧。"""
    comm_rs = []
    led_parts = []
    for part in parts:
        ref = str(getattr(part, "ref", "") or "").upper()
        if ref in ("R10", "R11", "R12"):
            comm_rs.append(part)
        if ref.startswith("LED"):
            led_parts.append(part)
    if not comm_rs and not led_parts:
        return

    block_y = main_bbox.max.y + gap
    x = main_bbox.min.x - (4 * gap)
    ordered = sorted(comm_rs + led_parts, key=node._part_ref_key)
    for part in ordered:
        bb = _mcu_layout_bbox(part)
        if bb is None:
            continue
        _place_part_row_y(part, x, block_y, grid)
        x += max(bb.w, grid) + gap


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


def _mcu_push_out_of_main_keepout(node, main_part, parts, gap, grid):
    """
    把与 MCU place_bbox 重叠的器件推开（spacing 膨胀后 lbl 框仍可能落在黄框内）。
    优先推到 MCU 下方逐行排开。
    """
    main_bb = _placement_bbox(main_part)
    if main_bb is None:
        return
    pad = max(gap, grid * 2)
    keep_min = Point(main_bb.min.x - pad, main_bb.min.y - pad)
    keep_max = Point(main_bb.max.x + pad, main_bb.max.y + pad)
    keep_box = BBox(keep_min, keep_max)
    overlapping = []
    for part in parts:
        if part is main_part:
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
    _mcu_push_out_of_main_keepout(node, main, parts, gap, grid)


def apply_generic_mcu_layout(
    node, parts, roles, main_part, topology, trunk_map, nets=None, **options
):
    """
    人工 MCU 风格布局：MCU 居中；左侧 TK/R/通信与 MCU 左 pin 逐行对齐；上=去耦；下=连接器。
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

    # 上：去耦（SKiDL Y 向上 → 用 max.y + gap）
    if decouple:
        top_y = main_bbox.max.y + gap
        _place_parts_in_row(
            node, decouple, main_bbox.min.x, top_y, gap, grid
        )
        placed.update(decouple)

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

    left_chains = _mcu_collect_left_chains(
        node, main_part, parts, part_adj, io_series, tk_parts
    )

    _mcu_place_comm_led_block(
        node, main_part, parts, main_bbox, gap, grid, part_adj
    )
    placed.update(indicators)

    left_connectors = [
        p for p in connectors if _io_side_score(node, p) <= 0
    ]
    right_connectors = [
        p for p in connectors if _io_side_score(node, p) > 0
    ]
    all_connectors = sorted(
        left_connectors + right_connectors, key=node._part_ref_key
    )
    if all_connectors:
        _mcu_place_connectors_below_main(
            node, main_part, all_connectors, gap, grid
        )
        placed.update(all_connectors)

    _mcu_push_out_of_main_keepout(node, main_part, parts, gap, grid)
    _resolve_overlaps(node, parts, grid, max(gap, blk_pad), exclude=anchor)

    # 左列 TK/R 在去重叠之后放置，避免被 _resolve_overlaps 推到 MCU 右侧。
    if left_chains:
        _mcu_place_left_pin_chains(
            node, main_part, left_chains, main_bbox, gap, grid
        )
        for r, tk, _ in left_chains:
            if r is not None:
                placed.add(r)
                anchor.add(r)
            if tk is not None:
                placed.add(tk)
                anchor.add(tk)

    _mcu_push_out_of_main_keepout(node, main_part, parts, gap, grid)
    if all_connectors:
        _mcu_place_connectors_below_main(
            node, main_part, all_connectors, gap, grid
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


def _mcu_wire_two_pins(p1, p2, bus_y=None):
    """两点间优先水平总线（与人工 MCU 图一致），否则 L 型。"""
    if p1.y == p2.y:
        return [Segment(copy.copy(p1), copy.copy(p2))]
    if p1.x == p2.x:
        return [Segment(copy.copy(p1), copy.copy(p2))]
    y = bus_y if bus_y is not None else p1.y
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


def route_mcu_local_nets(node, nets, **options):
    """
    MCU 专用：2-pin 星型支路用短直线/水平总线，不走 switchbox。
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
    handled = set()

    for net in nets:
        pins = _mcu_route_pins(node, net)
        if len(pins) != 2:
            continue
        net_parts = {pin.part for pin in pins}
        if not _mcu_net_keep_local_wire(list(net_parts), main):
            continue
        # 布局前 auto_stub 可能已标记，本地线需清除以便导出 wire 而非 label。
        net._stub = False
        net.stub = False
        for pin in pins:
            pin.stub = False
        p1 = _mcu_pin_route_pt(pins[0])
        p2 = _mcu_pin_route_pt(pins[1])
        bus_y = p1.y
        if main in net_parts:
            mp = pins[0] if pins[0].part is main else pins[1]
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
    for net in nets:
        if net in handled or net in wired:
            continue
        if getattr(net, "_stub_explicit", False):
            continue
        net_parts = list(node._net_connected_parts(net))
        pins = _mcu_route_pins(node, net)
        if len(net_parts) == 2 and len(pins) == 2:
            continue
        net._stub = True
        net._stub_explicit = False
        for pin in net.get_pins():
            pin.stub = True
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
