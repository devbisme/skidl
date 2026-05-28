# -*- coding: utf-8 -*-

"""MCU 引脚分叉布局：检测、主干/支路分类与摆放。"""

from skidl.geometry import BBox, Point, Tx
from skidl.schematics.topology.mcu import (
    _mcu_net_bridges_mcu_and_header,
    _mcu_pin_route_pt,
    _mcu_reject_two_pin_local_wire,
    _mcu_two_pin_endpoints_straddle_body,
    _mcu_walk_colinear_chain,
    route_mcu_local_nets,
)
from skidl.schematics.topology.mcu_fork import (
    build_pin_fork_spec,
    discover_pin_forks,
    is_real_fork,
    place_all_pin_forks,
    place_pin_fork_layout,
    preview_fork_reserved_parts,
)
from tests.unit_tests.test_topology_generic_mcu import (
    _FakeNet,
    _FakeNode,
    _FakePart,
    _FakePin,
    _wire,
)


def _part_with_bbox(ref, w=200, h=100, pins=None):
    p = _FakePart(ref, pins=pins or [_FakePin("1"), _FakePin("2")])
    for pin in p.pins:
        pin.part = p
        pin.pt = Point(0, 0) if pin.name == "1" else Point(w, 0)
        pin.place_pt = pin.pt
    p.place_bbox = BBox(Point(0, 0), Point(w, h))
    p.bbox = p.place_bbox
    p.tx = Tx()
    return p


def _build_tg032_tx_led_fork():
    """U3 P30/TX0 — R10 — /TX；同网 LED1 — R12 — VCC。"""
    node = _FakeNode()
    u3 = _FakePart(
        "U3",
        "MJ6050A3",
        pins=[_FakePin("5"), _FakePin("8")],
    )
    for i, pin in enumerate(u3.pins):
        pin.part = u3
        pin.pt = Point(50 * i, 300)
        pin.place_pt = pin.pt
    u3.place_bbox = BBox(Point(0, 0), Point(400, 600))
    u3.bbox = u3.place_bbox
    u3.tx = Tx()

    r10 = _part_with_bbox("R10")
    led1 = _part_with_bbox("LED1")
    r12 = _part_with_bbox("R12")
    x1 = _FakePart("X1", pins=[_FakePin("1"), _FakePin("2")])
    for pin in x1.pins:
        pin.part = x1

    n_star = _FakeNet("Net-(LED1-2)")
    n_pad = _FakeNet("Net-(LED1-Pad1)")
    tx = _FakeNet("/TX")
    vcc0 = _FakeNet("VCC_5V_0")

    _wire(u3, "5", n_star)
    _wire(r10, "2", n_star)
    _wire(led1, "1", n_star)
    _wire(led1, "2", n_pad)
    _wire(r12, "1", n_pad)
    _wire(r12, "2", vcc0)
    _wire(r10, "1", tx)
    _wire(x1, "2", tx)

    parts = [u3, r10, led1, r12, x1]
    nets = [n_star, n_pad, tx, vcc0]
    roles = {u3: "ic", x1: "connector"}
    return node, u3, u3.pins[0], n_star, parts, nets, roles


def test_is_real_fork_tg032_tx_led():
    node, u3, pin, n_star, parts, nets, roles = _build_tg032_tx_led_fork()
    part_set = set(parts)
    assert is_real_fork(node, u3, pin, n_star, part_set)
    spec = build_pin_fork_spec(
        node, u3, pin, parts, nets, set(), {id(u3): set()}, roles
    )
    assert spec is not None
    assert [p.ref for p in spec.trunk.parts] == ["R10"]
    branch_refs = []
    for b in spec.branches:
        branch_refs.extend(p.ref for p in b.parts)
    assert "LED1" in branch_refs
    assert "R12" in branch_refs


def test_not_fork_simple_series():
    node = _FakeNode()
    u3 = _FakePart("U3", pins=[_FakePin("1")])
    u3.pins[0].part = u3
    r5 = _FakePart("R5", pins=[_FakePin("1"), _FakePin("2")])
    for p in r5.pins:
        p.part = r5
    tk = _FakePart("TK1", pins=[_FakePin("1")])
    tk.pins[0].part = tk
    n1 = _FakeNet("Net-(U3-P05)")
    n2 = _FakeNet("TK1")
    _wire(u3, "1", n1)
    _wire(r5, "2", n1)
    _wire(r5, "1", n2)
    _wire(tk, "1", n2)
    part_set = {u3, r5, tk}
    assert not is_real_fork(node, u3, u3.pins[0], n1, part_set)


def test_not_fork_decouple_only():
    node = _FakeNode()
    u3 = _FakePart("U3", pins=[_FakePin("vdd"), _FakePin("vss")])
    for p in u3.pins:
        p.part = u3
    c1 = _FakePart("C1", pins=[_FakePin("1"), _FakePin("2")])
    c2 = _FakePart("C2", pins=[_FakePin("1"), _FakePin("2")])
    for c in (c1, c2):
        for p in c.pins:
            p.part = c
    vdd = _FakeNet("VDD")
    gnd = _FakeNet("GND")
    _wire(u3, "vdd", vdd)
    _wire(c1, "1", vdd)
    _wire(c1, "2", gnd)
    _wire(c2, "1", vdd)
    _wire(c2, "2", gnd)
    part_set = {u3, c1, c2}
    # 两颗 C 均接 VDD 星型：语义相同，非信号分叉
    assert not is_real_fork(node, u3, u3.pins[0], vdd, part_set)


def test_walk_colinear_legacy_when_fork_disabled():
    """mcu_fork_layout 关闭时不影响 _mcu_walk_colinear_chain 贪心单链。"""
    node, u3, pin, n_star, parts, nets, roles = _build_tg032_tx_led_fork()
    part_set = set(parts)
    chain, _ = _mcu_walk_colinear_chain(
        node, u3, pin, nets, part_set, set()
    )
    refs = [p.ref for p in chain]
    assert refs == ["U3", "R10", "LED1", "R12"]


def test_fork_placement_geometry():
    node, u3, pin, n_star, parts, nets, roles = _build_tg032_tx_led_fork()
    node.parts = parts
    spec = build_pin_fork_spec(
        node, u3, pin, parts, nets, set(), {id(u3): set()}, roles
    )
    assert spec is not None
    placed = place_pin_fork_layout(
        node, u3, spec, gap=100, grid=100, margin=100, mcu_fork_layout=True
    )
    r10 = next(p for p in parts if p.ref == "R10")
    led1 = next(p for p in parts if p.ref == "LED1")
    assert r10 in placed and led1 in placed
    r10_y = _mcu_pin_route_pt_y(r10)
    led_y = _mcu_pin_route_pt_y(led1)
    from skidl.schematics.topology.mcu import _mcu_pin_route_pt

    mcu_y = _mcu_pin_route_pt(pin).y
    assert abs(r10_y - mcu_y) < 5
    assert led_y > r10_y + 50


def _mcu_pin_route_pt_y(part):
    from skidl.schematics.topology.mcu import _mcu_pin_route_pt

    for pin in part.pins:
        if getattr(pin, "net", None) is not None:
            return _mcu_pin_route_pt(pin).y
    return 0.0


def test_preview_fork_reserved_includes_led_branch():
    """预扫描应保留 LED1、R12，避免 passive_far 把 R12 排到 Header 行。"""
    node, u3, pin, n_star, parts, nets, roles = _build_tg032_tx_led_fork()
    reserved = preview_fork_reserved_parts(
        node, u3, parts, nets, roles, mcu_fork_layout=True
    )
    refs = {getattr(p, "ref", "") for p in reserved}
    assert "R10" in refs
    assert "LED1" in refs
    assert "R12" in refs


def test_discover_marks_used_parts():
    node, u3, pin, n_star, parts, nets, roles = _build_tg032_tx_led_fork()
    specs = discover_pin_forks(
        node, u3, parts, nets, roles, set(), mcu_fork_layout=True
    )
    assert len(specs) >= 1
    used = {id(p) for s in specs for p in s.all_parts()}
    assert id(next(p for p in parts if p.ref == "R10")) in used


def test_two_pin_straddle_mcu_body_rejects_local_wire():
    """MCU 两侧端点的 2-pin 网不应画横穿本体的水平 local wire。"""
    node = _FakeNode()
    u3 = _FakePart("U3", pins=[_FakePin("VDD"), _FakePin("P1")])
    for pin in u3.pins:
        pin.part = u3
    u3.place_bbox = BBox(Point(0, 0), Point(400, 600))
    u3.bbox = u3.place_bbox
    u3.tx = Tx()
    u3.pins[0].pt = Point(380, 300)
    u3.pins[0].place_pt = u3.pins[0].pt

    r13 = _part_with_bbox("R13")
    r13.pins[0].pt = Point(50, 300)
    r13.pins[0].place_pt = r13.pins[0].pt
    r13.pins[1].pt = Point(250, 300)
    r13.pins[1].place_pt = r13.pins[1].pt

    vcc = _FakeNet("VCC_5V")
    _wire(u3, "VDD", vcc)
    _wire(r13, "1", vcc)

    p_mcu = _mcu_pin_route_pt(u3.pins[0])
    p_r = _mcu_pin_route_pt(r13.pins[0])
    assert _mcu_two_pin_endpoints_straddle_body(u3, p_mcu, p_r)
    assert _mcu_reject_two_pin_local_wire(u3, p_mcu, p_r)

    node.parts = [u3, r13]
    node.wires = {}
    node._mcu_manual_pnr = True
    node._last_topology_result = {"kind": "mcu", "main_part": u3}
    handled = route_mcu_local_nets(node, [vcc], mcu_fork_layout=False)
    assert vcc in handled
    assert vcc not in node.wires
    assert vcc.stub is True


def test_two_pin_same_side_allows_local_wire():
    """同侧端点的 2-pin 网仍可画 local wire。"""
    node = _FakeNode()
    u3 = _FakePart("U3", pins=[_FakePin("P1")])
    u3.pins[0].part = u3
    u3.place_bbox = BBox(Point(0, 0), Point(400, 600))
    u3.bbox = u3.place_bbox
    u3.tx = Tx()
    u3.pins[0].pt = Point(50, 300)
    u3.pins[0].place_pt = u3.pins[0].pt

    r5 = _part_with_bbox("R5", w=100)
    r5.pins[0].pt = Point(-150, 300)
    r5.pins[0].place_pt = r5.pins[0].pt
    r5.pins[1].pt = Point(-50, 300)
    r5.pins[1].place_pt = r5.pins[1].pt

    sig = _FakeNet("/TK1")
    _wire(u3, "P1", sig)
    _wire(r5, "2", sig)

    p_mcu = _mcu_pin_route_pt(u3.pins[0])
    p_r = _mcu_pin_route_pt(r5.pins[1])
    assert not _mcu_two_pin_endpoints_straddle_body(u3, p_mcu, p_r)

    node.parts = [u3, r5]
    node.wires = {}
    node._mcu_manual_pnr = True
    node._last_topology_result = {"kind": "mcu", "main_part": u3}
    handled = route_mcu_local_nets(node, [sig], mcu_fork_layout=False)
    assert sig in handled
    assert sig in node.wires


def test_mcu_header_bridge_net_is_stub_not_wired():
    """MCU 与 Header 端口链之间的桥接网（如 VCC_5V）不画贯通线，改 stub。"""
    node = _FakeNode()
    u3 = _FakePart("U3", pins=[_FakePin("12"), _FakePin("8")])
    x1 = _FakePart("X1", pins=[_FakePin("1"), _FakePin("4")])
    r13 = _part_with_bbox("R13")
    for p in (u3, x1):
        for pin in p.pins:
            pin.part = p
    u3.place_bbox = BBox(Point(0, 0), Point(400, 600))
    u3.bbox = u3.place_bbox
    u3.tx = Tx()
    x1.place_bbox = BBox(Point(0, -500), Point(400, -400))
    x1.bbox = x1.place_bbox
    x1.tx = Tx()
    x1.pins[0].pt = Point(50, -450)
    x1.pins[0].place_pt = x1.pins[0].pt
    x1.pins[1].pt = Point(350, -450)
    x1.pins[1].place_pt = x1.pins[1].pt
    u3.pins[0].pt = Point(380, 100)
    u3.pins[0].place_pt = u3.pins[0].pt
    u3.pins[1].pt = Point(380, 50)
    u3.pins[1].place_pt = u3.pins[1].pt
    r13.pins[0].pt = Point(200, -450)
    r13.pins[0].place_pt = r13.pins[0].pt
    r13.pins[1].pt = Point(300, -450)
    r13.pins[1].place_pt = r13.pins[1].pt

    vcc_bridge = _FakeNet("VCC_5V")
    vcc_header = _FakeNet("VCC_5V_0")
    _wire(u3, "12", vcc_bridge)
    _wire(r13, "2", vcc_bridge)
    _wire(x1, "1", vcc_header)
    _wire(r13, "1", vcc_header)

    node._connector_port_part_sets = [frozenset({x1, r13})]
    node.parts = [u3, x1, r13]
    node.wires = {}
    node._mcu_manual_pnr = True
    node._last_topology_result = {"kind": "mcu", "main_part": u3}

    assert _mcu_net_bridges_mcu_and_header(
        node, u3, {u3, r13}
    )
    assert not _mcu_net_bridges_mcu_and_header(
        node, u3, {x1, r13}
    )

    handled = route_mcu_local_nets(
        node, [vcc_bridge, vcc_header], mcu_fork_layout=False
    )
    assert vcc_bridge in handled
    assert vcc_bridge.stub is True
    assert vcc_bridge not in node.wires
    assert vcc_header in handled
    assert vcc_header in node.wires


def test_three_branch_neighbors():
    """anchor net 上三颗 neighbor：应得到 3 条 branch 分类。"""
    node = _FakeNode()
    u3 = _FakePart("U3", pins=[_FakePin("1")])
    u3.pins[0].part = u3
    r1 = _FakePart("R1", pins=[_FakePin("1"), _FakePin("2")])
    r2 = _FakePart("R2", pins=[_FakePin("1"), _FakePin("2")])
    r3 = _FakePart("R3", pins=[_FakePin("1"), _FakePin("2")])
    for p in (r1, r2, r3):
        for pin in p.pins:
            pin.part = p
    n0 = _FakeNet("Net-(U3-P1)")
    tx = _FakeNet("/TX")
    rx = _FakeNet("/RX")
    pwm = _FakeNet("/PWM")
    _wire(u3, "1", n0)
    _wire(r1, "1", n0)
    _wire(r1, "2", tx)
    _wire(r2, "1", n0)
    _wire(r2, "2", rx)
    _wire(r3, "1", n0)
    _wire(r3, "2", pwm)
    part_set = {u3, r1, r2, r3}
    assert is_real_fork(node, u3, u3.pins[0], n0, part_set)
    spec = build_pin_fork_spec(
        node, u3, u3.pins[0], list(part_set), [n0, tx, rx, pwm], set(), {}, {}
    )
    assert spec is not None
    assert len(spec.trunk.parts) >= 1
    assert len(spec.branches) == 2
