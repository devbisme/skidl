# -*- coding: utf-8 -*-

"""
拓扑识别与布局编排：MCU 与 generic_driver 互斥，否则 trunk-aware。
"""

from skidl.schematics.trunk_layout import apply_trunk_aware_layout, classify_trunk_nets

from .common import _disabled_topology, _topology_options
from .driver import apply_generic_driver_layout, detect_generic_driver_topology
from .mcu import (
    _mcu_apply_label_stub_policy,
    apply_generic_mcu_layout,
    detect_generic_mcu_topology,
)


def _pick_topology(mcu_topo, driver_topo, topo_opts):
    """MCU 与 driver 二选一；同分且均强时 MCU 优先。"""
    strong_th = topo_opts["strong_threshold"]
    weak_th = topo_opts["weak_threshold"]

    mcu_kind = mcu_topo.get("kind")
    drv_kind = driver_topo.get("kind")
    mcu_conf = mcu_topo.get("confidence", 0)
    drv_conf = driver_topo.get("confidence", 0)

    mcu_strong = mcu_kind == "mcu" and mcu_conf >= strong_th
    drv_strong = drv_kind == "generic_driver" and drv_conf >= strong_th

    if mcu_strong and not drv_strong:
        return mcu_topo
    if drv_strong and not mcu_strong:
        return driver_topo
    if mcu_strong and drv_strong:
        if mcu_conf >= drv_conf:
            return mcu_topo
        return driver_topo

    if mcu_kind == "weak_mcu" and mcu_conf >= weak_th and mcu_conf >= drv_conf:
        return mcu_topo
    if drv_kind == "weak_generic_driver" and drv_conf >= weak_th and drv_conf > mcu_conf:
        return driver_topo

    if mcu_conf >= drv_conf:
        return mcu_topo
    return driver_topo


def detect_known_topology(
    node, parts, nets, roles, main_part, trunk_map=None, **options
):
    """拓扑识别门面：先 MCU 再 driver，按置信度互斥选取。"""
    topo_opts = _topology_options(options)
    if not topo_opts["enabled"]:
        return _disabled_topology()

    adjacency = None
    if parts and nets:
        from skidl.schematics.trunk_layout import build_part_adjacency

        adjacency = build_part_adjacency(parts, nets)

    mcu_topo = detect_generic_mcu_topology(
        node,
        parts,
        nets,
        roles,
        main_part,
        trunk_map=trunk_map,
        adjacency=adjacency,
        **options,
    )
    driver_topo = detect_generic_driver_topology(
        node,
        parts,
        nets,
        roles,
        main_part,
        trunk_map=trunk_map,
        adjacency=adjacency,
        **options,
    )
    return _pick_topology(mcu_topo, driver_topo, topo_opts)


def apply_topology_or_trunk_layout(
    node, parts, nets, roles, main_part, **options
):
    """
    互斥分支：mcu / generic_driver 专用布局，否则 trunk-aware。
    结果写入 node._last_topology_result。
    """
    node._schematic_debug_options = options
    trunk_map = classify_trunk_nets(node, parts, nets, roles, main_part, **options)
    topology = detect_known_topology(
        node, parts, nets, roles, main_part, trunk_map=trunk_map, **options
    )
    node._last_topology_result = topology

    topo_opts = _topology_options(options)
    layout_main = topology.get("main_part") or main_part
    strong_th = topo_opts["strong_threshold"]
    kind = topology.get("kind")
    conf = topology.get("confidence", 0)

    layout_opts = dict(options)
    layout_opts.setdefault("grid", 100)
    layout_opts.setdefault("blk_int_pad", 100)

    weak_th = topo_opts["weak_threshold"]
    use_mcu_layout = (
        kind in ("mcu", "weak_mcu")
        and layout_main is not None
        and (
            (kind == "mcu" and conf >= strong_th)
            or (kind == "weak_mcu" and conf >= weak_th)
        )
    )
    if use_mcu_layout:
        node._human_readable_main_part = layout_main
        node._driver_rail_plan = {"enabled": False}
        apply_generic_mcu_layout(
            node,
            parts,
            roles,
            layout_main,
            topology,
            trunk_map,
            nets=nets,
            **layout_opts,
        )
    elif (
        kind == "generic_driver"
        and conf >= strong_th
        and layout_main is not None
    ):
        node._human_readable_main_part = layout_main
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
        apply_trunk_aware_layout(
            node,
            parts,
            roles,
            layout_main,
            trunk_map,
            **layout_opts,
        )
