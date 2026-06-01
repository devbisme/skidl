# -*- coding: utf-8 -*-

"""
小组连通器件的弱对齐 / 轻美化（human_readable 专用）。

大组用 place.py 中的结构化分区 + 强对齐；小组在力导向之后仅做“去抖/去歪”，
避免把局部几何压坏并引发 routing TerminalClash。
"""

from copy import copy

from skidl.geometry import BBox, Point, Tx


def beautify_small_connected_group(
    parts,
    *,
    classify_role,
    part_ref_key,
    grid,
    blk_int_pad,
):
    """对 small connected group 做保守 Y 向轻美化。

    Args:
        parts: 已放置好的 real parts（不含 NetTerminal）。
        classify_role: 与 Placer._classify_part_role 相同签名的回调。
        part_ref_key: 与 Placer._part_ref_key 相同签名的稳定排序键。
        grid: 布局网格（来自工具 constants.GRID）。
        blk_int_pad: 块间距（BLK_INT_PAD）。
    """
    if not parts or len(parts) < 2:
        return

    parts = list(parts)
    roles = {p: classify_role(p) for p in parts}

    if not _is_horizontal_group(parts):
        # 第一版仅处理偏横向小图；纵向结构保持力导向结果不动。
        return

    y_band_tol = 2 * grid
    pin_sep = grid
    max_snap = 2 * grid

    bands = _cluster_y_bands(parts, part_ref_key, y_band_tol)
    for band in bands:
        if len(band) < 2:
            continue
        target_y = _band_target_y(band, grid)
        for part in band:
            ctr = _part_ctr(part)
            dy = Point(ctr.x, target_y).snap(grid).y - ctr.y
            if abs(dy) > max_snap:
                continue
            _try_nudge_y(part, parts, dy, grid, pin_sep, blk_int_pad)

    _weak_pair_y_touchup(parts, part_ref_key, roles, grid, pin_sep, blk_int_pad, max_snap)
    _resolve_minor_overlaps(parts, part_ref_key, grid, blk_int_pad, pin_sep, primary_axis="y")


def _is_horizontal_group(parts):
    """组整体 bbox 宽 >= 高 时视为偏横向，才做 Y 吸附。"""
    bbox = BBox()
    for part in parts:
        bbox.add(part.place_bbox * part.tx)
    return bbox.w >= bbox.h


def _part_ctr(part):
    return (part.place_bbox * part.tx).ctr


def _pt_dist(a, b):
    """两点欧氏距离（Point 无 distance 方法，用差向量 magnitude）。"""
    return (a - b).magnitude


def _connected_pin_pts(part):
    """取已连接引脚在放置坐标系下的位置（优先 place_pt）。"""
    pts = []
    for pin in part:
        if not getattr(pin, "is_connected", lambda: False)():
            continue
        base = getattr(pin, "place_pt", None) or pin.pt
        pts.append((pin, base * part.tx))
    return pts


def _bbox_overlaps(part, others):
    bbox = part.place_bbox * part.tx
    for other in others:
        if other is part:
            continue
        if bbox.intersects(other.place_bbox * other.tx):
            return True
    return False


def _pins_crowded_risk(part, others, grid, pin_sep):
    """轻量引脚拥挤检查：不同 net 的引脚过近则视为 routing 风险。"""
    for _pin, pt in _connected_pin_pts(part):
        for other in others:
            if other is part:
                continue
            for opin, opt in _connected_pin_pts(other):
                if _pt_dist(pt, opt) >= pin_sep:
                    continue
                pnet = getattr(_pin, "net", None)
                onet = getattr(opin, "net", None)
                if pnet is not None and onet is not None and pnet is not onet:
                    return True
                if abs(pt.y - opt.y) <= grid * 0.5 and abs(pt.x - opt.x) <= grid:
                    return True
    return False


def _move_safe(part, parts, dx, dy, grid, pin_sep):
    """尝试平移；bbox 或引脚风险不达标则回滚。"""
    if not dx and not dy:
        return False
    old_tx = copy(part.tx)
    part.tx *= Tx(dx=dx, dy=dy)
    others = [p for p in parts if p is not part]
    if _bbox_overlaps(part, others) or _pins_crowded_risk(part, others, grid, pin_sep):
        part.tx = old_tx
        return False
    return True


def _try_nudge_y(part, parts, dy, grid, pin_sep, blk_int_pad):
    if not dy:
        return False
    return _move_safe(part, parts, 0, dy, grid, pin_sep)


def _cluster_y_bands(parts, part_ref_key, y_band_tol):
    """按中心 Y 稳定排序后，把相邻 Y 差 <= 容差的器件划入同一水平带。"""
    ordered = sorted(parts, key=lambda p: (_part_ctr(p).y, part_ref_key(p)))
    bands = []
    current = [ordered[0]]
    band_max_y = _part_ctr(ordered[0]).y
    for part in ordered[1:]:
        y = _part_ctr(part).y
        if y - band_max_y <= y_band_tol:
            current.append(part)
            band_max_y = max(band_max_y, y)
        else:
            bands.append(current)
            current = [part]
            band_max_y = y
    bands.append(current)
    return bands


def _band_target_y(band, grid):
    """水平带目标 Y：中位数后吸附网格，比均值更抗离群。"""
    ys = sorted(_part_ctr(p).y for p in band)
    mid = ys[len(ys) // 2]
    return Point(0, mid).snap(grid).y


def _ref_prefix(part):
    ref = str(getattr(part, "ref", "") or "").upper()
    return ref[:1] if ref else ""


def _weak_pair_y_touchup(parts, part_ref_key, roles, grid, pin_sep, blk_int_pad, max_snap):
    """可选：左右大致对应、同类且 Y 已很近的一对器件，仅轻微统一 Y。"""
    if len(parts) < 2:
        return
    ctrs = {p: _part_ctr(p) for p in parts}
    xs = sorted(ctrs[p].x for p in parts)
    mid_x = xs[len(xs) // 2]

    candidates = sorted(parts, key=part_ref_key)
    used = set()
    for i, a in enumerate(candidates):
        if id(a) in used:
            continue
        ca = ctrs[a]
        pa = _ref_prefix(a)
        ha = max(a.place_bbox.h, grid)
        wa = max(a.place_bbox.w, grid)
        for b in candidates[i + 1 :]:
            if id(b) in used:
                continue
            cb = ctrs[b]
            if abs(ca.y - cb.y) > max_snap:
                continue
            if roles.get(a) != roles.get(b) and pa != _ref_prefix(b):
                continue
            hb, wb = max(b.place_bbox.h, grid), max(b.place_bbox.w, grid)
            if abs(ha - hb) > grid or abs(wa - wb) > 2 * grid:
                continue
            if (ca.x - mid_x) * (cb.x - mid_x) >= 0:
                continue
            target_y = Point(0, (ca.y + cb.y) / 2.0).snap(grid).y
            ok_a = abs(target_y - ca.y) <= max_snap and _try_nudge_y(
                a, parts, target_y - ca.y, grid, pin_sep, blk_int_pad
            )
            ok_b = abs(target_y - cb.y) <= max_snap and _try_nudge_y(
                b, parts, target_y - cb.y, grid, pin_sep, blk_int_pad
            )
            if ok_a or ok_b:
                used.add(id(a))
                used.add(id(b))
            break


def _resolve_minor_overlaps(parts, part_ref_key, grid, blk_int_pad, pin_sep, primary_axis="y"):
    """有限轮小步去重叠；主调整轴为 Y 时，优先沿 X 微移。"""
    for _ in range(15):
        moved = False
        for part in sorted(parts, key=part_ref_key):
            if not _bbox_overlaps(part, parts):
                continue
            ctr = _part_ctr(part)
            for other in parts:
                if other is part:
                    continue
                if not (part.place_bbox * part.tx).intersects(
                    other.place_bbox * other.tx
                ):
                    continue
                octr = _part_ctr(other)
                if primary_axis == "y":
                    dx = blk_int_pad if ctr.x <= octr.x else -blk_int_pad
                    if _move_safe(part, parts, dx, 0, grid, pin_sep):
                        moved = True
                        break
                    dy = blk_int_pad if ctr.y <= octr.y else -blk_int_pad
                    if _move_safe(part, parts, 0, dy, grid, pin_sep):
                        moved = True
                        break
                else:
                    dy = blk_int_pad if ctr.y <= octr.y else -blk_int_pad
                    if _move_safe(part, parts, 0, dy, grid, pin_sep):
                        moved = True
                        break
        if not moved:
            break
