# -*- coding: utf-8 -*-

"""
拓扑识别与布局编排：在 generic_driver 与 trunk-aware 之间互斥选择。
"""

from skidl.schematics.trunk_layout import apply_trunk_aware_layout, classify_trunk_nets

from .common import _disabled_topology, _topology_options
from .driver import apply_generic_driver_layout, detect_generic_driver_topology

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

def apply_topology_or_trunk_layout(
    node, parts, nets, roles, main_part, **options
):
    """
    互斥分支：generic_driver 仅 apply_generic_driver_layout，否则 trunk-aware。
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
