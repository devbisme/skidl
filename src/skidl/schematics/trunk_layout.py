# -*- coding: utf-8 -*-

"""
human_readable 模式下的 net-aware trunk 布局后处理。
"""

from collections import defaultdict

from skidl.geometry import Point, Tx, Vector


def build_part_adjacency(parts, nets):
    """根据 nets 构建 part 邻接图。"""
    part_set = set(parts)
    adjacency = defaultdict(set)
    for net in nets:
        net_parts = [p for p in (pin.part for pin in net.pins) if p in part_set]
        for i, part_a in enumerate(net_parts):
            for part_b in net_parts[i + 1 :]:
                adjacency[id(part_a)].add(part_b)
                adjacency[id(part_b)].add(part_a)
    return adjacency


def _net_name_side_scores(net_name_u):
    """按网名给 top/bottom/left/right 打分；LED+/LED- 优先于泛化 LED token。"""
    scores = {"top": 0, "bottom": 0, "left": 0, "right": 0}

    if "LED+" in net_name_u or net_name_u.endswith("/LED+"):
        scores["top"] += 12
    if "LED-" in net_name_u or net_name_u.endswith("/LED-"):
        scores["bottom"] += 12

    top_tokens = ("VCC", "VDD", "VIN", "VBUS", "24V", "12V", "5V", "3V3", "W+")
    bottom_tokens = ("GND", "AGND", "DGND", "PGND", "VSS", "W-")
    right_tokens = ("OUT", "LOAD", "DRV", "SW")
    left_tokens = ("IN", "SENSE", "FB", "ADC", "CTRL", "PWM", "DIM")

    for token in top_tokens:
        if token in net_name_u:
            scores["top"] += 3
    for token in bottom_tokens:
        if token in net_name_u:
            scores["bottom"] += 3
    for token in right_tokens:
        if token in net_name_u:
            scores["right"] += 2
    for token in left_tokens:
        if token in net_name_u:
            scores["left"] += 2

    # 仅当不是 LED+/LED- 时，才把 LED 视作输出侧提示。
    if "LED+" not in net_name_u and "LED-" not in net_name_u and "LED" in net_name_u:
        scores["right"] += 2

    return scores


def is_trunk_net_name(name):
    """网名是否像电源/地/LED 主干（供 route 排序与简化使用）。"""
    if not name:
        return False
    text = str(name).upper()
    if text.startswith("NET-("):
        return False
    side = _net_name_side_scores(text)
    return max(side.values()) >= 3


def trunk_route_rank_bias(name):
    """全局布线排序：主干网优先（返回值越小越先布）。"""
    if not is_trunk_net_name(name):
        return 0
    text = str(name).upper()
    side = _net_name_side_scores(text)
    # 电源/地/LED 轨最先布，便于后续网复用其通道。
    return -500 - max(side.values()) * 10


def classify_trunk_nets(node, parts, nets, roles, main_part, **options):
    """识别 trunk net，并按 top/bottom/left/right 分类。"""
    if not parts or not nets:
        return {"top": [], "bottom": [], "left": [], "right": []}

    part_set = set(parts)
    side_candidates = {"top": [], "bottom": [], "left": [], "right": []}

    for net in nets:
        net_name = str(getattr(net, "name", "") or "")
        net_name_u = net_name.upper()
        is_named = bool(net_name) and not net_name_u.startswith("NET-(")

        net_parts = node._net_connected_parts(net, allowed_parts=part_set)
        fanout = len(net_parts)
        if fanout < 2:
            continue

        side_score = _net_name_side_scores(net_name_u)
        has_strong_token = max(side_score.values()) >= 3

        if (
            fanout <= 3
            and not is_named
            and not has_strong_token
            and not node._is_power_net_name(net_name_u)
            and node._is_local_functional_cluster(net, net_parts)
        ):
            continue

        role_set = {roles.get(part, "other") for part in net_parts}
        connector_count = sum(1 for part in net_parts if roles.get(part) == "connector")
        power_count = sum(
            1 for part in net_parts if roles.get(part) in ("power", "decoupling")
        )
        main_bonus = 2 if main_part in net_parts else 0

        base_score = (
            fanout * 2
            + len(role_set)
            + connector_count
            + power_count
            + main_bonus
            + (2 if is_named else 0)
        )

        if node._is_power_net_name(net_name_u):
            if any(t in net_name_u for t in ("GND", "VSS", "W-", "LED-")):
                side_score["bottom"] += 3
            else:
                side_score["top"] += 2

        best_side = max(side_score, key=side_score.get)
        if side_score[best_side] <= 0:
            continue

        total_score = base_score + side_score[best_side]
        if total_score < options.get("trunk_score_threshold", 6):
            continue

        side_candidates[best_side].append((total_score, net))

    max_per_side = options.get("trunk_max_per_side", 3)
    trunk_map = {"top": [], "bottom": [], "left": [], "right": []}
    for side, candidates in side_candidates.items():
        candidates.sort(key=lambda item: item[0], reverse=True)
        trunk_map[side] = [net for _, net in candidates[:max_per_side]]

    return trunk_map


def _trunk_layout_log(options, trunk_map):
    """human_readable 调试：输出 trunk 分类结果。"""
    if not options.get("schematic_progress", False):
        return
    from skidl.logger import active_logger

    def net_label(net):
        return str(getattr(net, "name", "") or net)

    parts = []
    for side in ("top", "bottom", "left", "right"):
        names = [net_label(n) for n in trunk_map.get(side, [])]
        if names:
            parts.append(f"{side}=[{', '.join(names)}]")
    if parts:
        active_logger.info("[schematic] trunk nets: " + "; ".join(parts))


def _collect_side_parts(node, parts, trunk_map):
    """收集每个 side 上由 trunk net 关联到的器件。"""
    side_parts = {"top": set(), "bottom": set(), "left": set(), "right": set()}
    part_set = set(parts)
    for side, nets in trunk_map.items():
        for net in nets:
            for part in node._net_connected_parts(net, allowed_parts=part_set):
                side_parts[side].add(part)
    return side_parts


def _assign_functional_zones(node, parts, roles, main_part, trunk_map):
    """按器件角色与网名补充 side 归属（不仅依赖 trunk net 覆盖）。"""
    side_parts = _collect_side_parts(node, parts, trunk_map)
    for side in side_parts:
        side_parts[side].discard(main_part)

    right_tokens = ("OUT", "LED", "LOAD", "DRV", "SW")
    left_tokens = ("IN", "PWM", "DIM", "SENSE", "FB", "CTRL")

    for part in parts:
        if part is main_part:
            continue
        ref = str(getattr(part, "ref", "") or "").upper()
        value = str(getattr(part, "value", "") or "").upper()
        net_names = [str(n).upper() for n in node._net_names_of(part)]

        if roles.get(part) == "connector":
            if "LED" in value or "OUT" in value or any(
                any(t in n for t in right_tokens) for n in net_names
            ):
                side_parts["right"].add(part)
                continue

        if ref.startswith("L") and any("LED" in n for n in net_names):
            side_parts["right"].add(part)
            continue

        if ref.startswith("C") and any(
            "LED+" in n or "VIN" in n or "VCC" in n for n in net_names
        ):
            if any("LED+" in n for n in net_names):
                side_parts["top"].add(part)
            continue

        if ref.startswith("R") and any(any(t in n for t in left_tokens) for n in net_names):
            side_parts["left"].add(part)

    return side_parts


def _row_start_x(parts, center_x, gap, grid):
    """根据器件宽度计算水平排布的起始 X。"""
    if not parts:
        return center_x
    widths = [max(getattr(part.place_bbox, "w", 0), grid) for part in parts]
    total_w = sum(widths) + max(0, len(widths) - 1) * gap
    return center_x - total_w / 2.0


def _sort_parts_by_current_x(node, parts):
    return sorted(
        parts, key=lambda part: (node._placement_ctr(part).x, node._part_ref_key(part))
    )


def _place_parts_in_column(node, parts, x, y_start, gap, grid):
    y = y_start
    for part in parts:
        h = max(getattr(part.place_bbox, "h", 0), grid)
        part.tx = Tx().move(Point(x, y))
        y += h + gap


def _place_parts_in_row(node, parts, start_x, start_y, gap, grid, direction=1):
    """水平排布：直接设置 tx，用于 generic driver 主功率链。"""
    x = start_x
    for part in parts:
        w = max(getattr(part.place_bbox, "w", 0), grid)
        if direction >= 0:
            part.tx = Tx().move(Point(x, start_y))
            x += w + gap
        else:
            part.tx = Tx().move(Point(x - w, start_y))
            x -= w + gap


def _set_part_center_x_safe(node, part, all_parts, target_x, grid):
    ctr = node._placement_ctr(part)
    snapped_x = Point(target_x, ctr.y).snap(grid).x
    dx = snapped_x - ctr.x
    if dx:
        node._nudge_part_if_clear(part, all_parts, dx, 0)


def _resolve_overlaps(node, parts, grid, gap, max_rounds=30, exclude=None):
    """轻量去重叠：优先垂直推开，失败再水平。"""
    exclude = exclude or set()
    for _ in range(max_rounds):
        moved = False
        for part in sorted(parts, key=node._part_ref_key):
            if part in exclude:
                continue
            bbox = part.place_bbox * part.tx
            for other in parts:
                if other is part:
                    continue
                if other in exclude:
                    continue
                other_bbox = other.place_bbox * other.tx
                if not bbox.intersects(other_bbox):
                    continue
                ctr = node._placement_ctr(part)
                other_ctr = node._placement_ctr(other)
                dy = gap if ctr.y <= other_ctr.y else -gap
                if node._nudge_part_if_clear(part, parts, 0, dy):
                    moved = True
                    break
                dx = gap if ctr.x <= other_ctr.x else -gap
                if node._nudge_part_if_clear(part, parts, dx, 0):
                    moved = True
                    break
            if moved:
                break
        if not moved:
            break


def apply_trunk_aware_layout(node, parts, roles, main_part, trunk_map, **options):
    """根据 trunk 分类结果做保守坐标后处理（对齐为主，避免整板重排引发布线失败）。"""
    if not parts or main_part is None:
        return

    _trunk_layout_log(options, trunk_map)

    main_bbox = main_part.place_bbox * main_part.tx
    grid = options.get("grid", 100)
    blk_pad = int(options.get("blk_int_pad", 100))
    gap = options.get("trunk_gap", max(blk_pad, grid * 2))

    side_parts = _assign_functional_zones(node, parts, roles, main_part, trunk_map)

    right_x = main_bbox.max.x + (2 * gap)
    left_x = main_bbox.min.x - (2 * gap)

    top_y = None
    bottom_y = None
    if side_parts["top"]:
        max_h = max(
            max(getattr(p.place_bbox, "h", 0), grid) for p in side_parts["top"]
        )
        top_y = main_bbox.min.y - gap - max_h
    if side_parts["bottom"]:
        bottom_y = main_bbox.max.y + gap

    right_sorted = sorted(
        side_parts["right"],
        key=lambda part: (roles.get(part) != "connector", node._part_ref_key(part)),
    )

    # 输出侧：连接器/电感等硬放到右侧列（阅读方向最重要）。
    if right_sorted:
        _place_parts_in_column(
            node,
            right_sorted,
            right_x,
            main_bbox.min.y,
            gap,
            grid,
        )

    # 上/下 rail：只做 Y 对齐，保留原有 X 分区，降低 pin 共线冲突概率。
    if top_y is not None:
        for part in sorted(side_parts["top"], key=node._part_ref_key):
            if part in right_sorted:
                continue
            node._set_part_center_y_safe(part, parts, top_y)

    if bottom_y is not None:
        for part in sorted(side_parts["bottom"], key=node._part_ref_key):
            if part in right_sorted:
                continue
            node._set_part_center_y_safe(part, parts, bottom_y)

    for part in sorted(side_parts["left"], key=node._part_ref_key):
        if part in right_sorted:
            continue
        _set_part_center_x_safe(node, part, parts, left_x, grid)

    for part in sorted(parts, key=node._part_ref_key):
        if roles.get(part) != "connector":
            continue
        value = str(getattr(part, "value", "") or "").upper()
        net_names = [str(n).upper() for n in node._net_names_of(part)]
        if "LED" in value or "OUT" in value or any("LED" in n for n in net_names):
            _set_part_center_x_safe(node, part, parts, right_x, grid)

    _resolve_overlaps(node, parts, grid, max(gap, blk_pad))


def expand_main_ic_keepout(main_part, grid, scale=1.0):
    """轻量扩大主控 place_bbox，给布线/cleanup 留少量 keepout（仅 human_readable）。"""
    if main_part is None:
        return
    pad = Vector(grid * scale, grid * scale)
    main_part.place_bbox = main_part.place_bbox.resize(pad)
