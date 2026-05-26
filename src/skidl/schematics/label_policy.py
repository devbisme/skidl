# -*- coding: utf-8 -*-

"""原理图标签/NetTerminal 导出策略（MCU 共线链、power 网等）。"""

from skidl.schematics.power_net import is_power_net_name


def mcu_layout_active(node):
    """当前 sheet 是否启用 MCU 专用布局（非 fallback）。"""
    topo = getattr(node, "_last_topology_result", None) or {}
    return topo.get("kind") in ("mcu", "weak_mcu") and not topo.get("fallback")


def mcu_main_part(node):
    topo = getattr(node, "_last_topology_result", None) or {}
    return topo.get("main_part") or getattr(node, "_human_readable_main_part", None)


def _net_real_parts(node, net):
    from skidl.schematics.place import is_net_terminal

    return {
        p
        for p in node._net_connected_parts(net)
        if not is_net_terminal(p)
    }


def net_in_mcu_colinear_set(node, net):
    """网内器件是否落在 MCU/连接器共线链集合内（已本地布局）。"""
    if net is None:
        return False
    sets = list(getattr(node, "_mcu_colinear_part_sets", None) or [])
    sets += list(getattr(node, "_connector_port_part_sets", None) or [])
    if not sets:
        return False
    net_parts = _net_real_parts(node, net)
    return any(net_parts <= cset for cset in sets)


def net_skip_add_net_terminal(net):
    """
    单页 MCU 串链/IO 网不创建 NetTerminal（避免边缘悬空 global_label）。
  条件：网名 Net-(...) 且仅连接多脚 U* 与 R/C/LED/D 类器件。
    """
    name = str(getattr(net, "name", "") or "")
    if not name.startswith("Net-("):
        return False
    parts = set()
    for pin in getattr(net, "pins", []):
        part = getattr(pin, "part", None)
        if part is not None:
            parts.add(part)
    if not parts:
        return False
    main_like = None
    for p in parts:
        ref = str(getattr(p, "ref", "") or "").upper()
        if ref.startswith("U") and len(getattr(p, "pins", []) or []) >= 8:
            main_like = p
            break
    if main_like is None:
        return False
    for p in parts - {main_like}:
        ref = str(getattr(p, "ref", "") or "").upper()
        if not (
            ref.startswith(("R", "C", "LED", "D"))
            or ref.startswith("TK")
        ):
            return False
    return len(parts) <= 4


def net_skip_net_terminal_label(node, net):
    """
    是否跳过边缘 NetTerminal 的标签/电源符号导出。
    power 网、已有导线、MCU 共线链上的网均跳过，避免悬空或重复标签。
    """
    if net is None:
        return True
    name = getattr(net, "name", None)
    if is_power_net_name(name):
        return True
    if mcu_layout_active(node) and net_in_mcu_colinear_set(node, net):
        return True
    return False


def net_skip_stub_pin_label(node, net):
    """
    stub 引脚导出信号 global_label 时是否跳过。
    电源网不跳过（仍导出 power symbol）；MCU 短链/共线链跳过。
    """
    if net is None:
        return True
    if is_power_net_name(getattr(net, "name", None)):
        return False
    if net_in_mcu_colinear_set(node, net):
        return True
    if net_skip_add_net_terminal(net):
        return True
    if net_skip_auto_stub_large_group(node, net):
        return True
    return False


def net_skip_auto_stub_large_group(node, net):
    """
    大组拆分 stub 时是否跳过该网。
    MCU 板上触及主控的短链保留给共线布局/本地线，勿提前打成 global_label。
    """
    if mcu_layout_active(node):
        main = mcu_main_part(node)
        if main is not None:
            net_parts = _net_real_parts(node, net)
            if main in net_parts and len(net_parts) <= 4:
                return True
    # place 早期尚未写入 _last_topology_result 时的回退：含多脚 U* 的短链
    net_parts = _net_real_parts(node, net)
    if len(net_parts) > 4:
        return False
    main_like = None
    for p in net_parts:
        ref = str(getattr(p, "ref", "") or "").upper()
        if ref.startswith("U") and len(getattr(p, "pins", []) or []) >= 8:
            main_like = p
            break
    return main_like is not None and main_like in net_parts
