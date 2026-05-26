# -*- coding: utf-8 -*-

"""generic MCU topology 检测、互斥与日志格式单元测试。"""

from skidl.geometry import Point
from skidl.schematics.topology import (
    _score_candidate_ic,
    _score_mcu_candidate_ic,
    detect_generic_mcu_topology,
    detect_known_topology,
    format_topology_log_line,
)
from skidl.schematics.topology.mcu import (
    _colinear_chain_sort_key,
    _find_port_colinear_chains,
    _mcu_find_colinear_chains,
    _mcu_walk_colinear_chain,
    _pair_pins_to_main,
    _walk_colinear_chain,
)


class _FakePin:
    def __init__(self, name, part=None):
        self.name = name
        self.part = part
        self.net = None
        self.pt = None
        self.stub = False

    def is_connected(self):
        return self.net is not None


class _FakeNet:
    def __init__(self, name):
        self.name = name
        self.pins = []


class _FakePart:
    def __init__(self, ref, value="", pins=None):
        self.ref = ref
        self.value = value
        self.name = value or ref
        self.lib = ""
        self.pins = pins or []
        self.place_bbox = None
        self.tx = None


class _FakeNode:
    def _net_connected_parts(self, net, allowed_parts=None):
        return [p for p in getattr(net, "_parts", []) if allowed_parts is None or p in allowed_parts]

    def _is_power_net_name(self, name):
        upper = str(name).upper()
        return "GND" in upper or "VCC" in upper or "VDD" in upper or "VSS" in upper

    def _net_names_of(self, part):
        names = set()
        for pin in part.pins:
            if pin.net is not None and getattr(pin.net, "name", None):
                names.add(str(pin.net.name))
        return names

    def _part_ref_key(self, part):
        return str(getattr(part, "ref", "") or "")


def _wire(part, pin_name, net):
    pin = next(p for p in part.pins if p.name == pin_name)
    pin.net = net
    net.pins.append(pin)
    if not hasattr(net, "_parts"):
        net._parts = []
    if part not in net._parts:
        net._parts.append(part)


def _build_tg032_like_graph():
    """MJ6050A3 + 去耦 + IO 串阻 + UART 网（简化 TG032-MCU）。"""
    node = _FakeNode()
    u3 = _FakePart(
        "U3",
        "MJ6050A3",
        pins=[
            _FakePin("VDD"),
            _FakePin("VSS"),
            _FakePin("P30/TX0"),
            _FakePin("P31/RX0"),
            _FakePin("P06/TK3"),
        ],
    )
    for p in u3.pins:
        p.part = u3

    c11 = _FakePart("C11", pins=[_FakePin("1"), _FakePin("2")])
    c12 = _FakePart("C12", pins=[_FakePin("1"), _FakePin("2")])
    r5 = _FakePart("R5", "1K", pins=[_FakePin("1"), _FakePin("2")])
    r6 = _FakePart("R6", "1K", pins=[_FakePin("1"), _FakePin("2")])
    r7 = _FakePart("R7", "1K", pins=[_FakePin("1"), _FakePin("2")])
    j1 = _FakePart("J1", pins=[_FakePin("1"), _FakePin("2"), _FakePin("3"), _FakePin("4")])

    for part in (c11, c12, r5, r6, r7, j1):
        for pin in part.pins:
            pin.part = part

    vcc = _FakeNet("VCC_5V")
    gnd = _FakeNet("GND")
    tx = _FakeNet("TX")
    rx = _FakeNet("RX")
    tk1 = _FakeNet("TK1")
    tk3 = _FakeNet("Net-(U3-TK3)")
    tx_u = _FakeNet("Net-(U3-TX)")
    rx_u = _FakeNet("Net-(U3-RX)")

    _wire(u3, "VDD", vcc)
    _wire(u3, "VSS", gnd)
    _wire(u3, "P30/TX0", tx_u)
    _wire(u3, "P31/RX0", rx_u)
    _wire(u3, "P06/TK3", tk3)
    _wire(c11, "1", vcc)
    _wire(c11, "2", gnd)
    _wire(c12, "1", vcc)
    _wire(c12, "2", gnd)
    _wire(r5, "1", tk1)
    _wire(r5, "2", tk3)
    _wire(r6, "1", tx)
    _wire(r6, "2", tx_u)
    _wire(r7, "1", rx)
    _wire(r7, "2", rx_u)
    _wire(j1, "1", vcc)
    _wire(j1, "2", tx)

    parts = [u3, c11, c12, r5, r6, r7, j1]
    nets = [vcc, gnd, tx, rx, tk1, tk3, tx_u, rx_u]
    roles = {
        u3: "ic",
        c11: "passive",
        c12: "passive",
        r5: "passive",
        r6: "passive",
        r7: "passive",
        j1: "connector",
    }
    adjacency = {id(u3): {c11, c12, r5, r6, r7, j1}}
    for p in (c11, c12, r5, r6, r7, j1):
        adjacency.setdefault(id(p), set()).add(u3)
    return node, u3, parts, nets, roles, adjacency


def test_mcu_score_mj6050():
    node, u3, parts, nets, roles, adj = _build_tg032_like_graph()
    sc, conf, reasons, combo, flags = _score_mcu_candidate_ic(
        node, u3, parts, nets, roles, set(parts), adj
    )
    assert flags["mcu_identity"]
    assert combo
    assert conf >= 60
    assert sc >= 12


def test_detect_generic_mcu_topology_strong():
    node, u3, parts, nets, roles, adj = _build_tg032_like_graph()
    topo = detect_generic_mcu_topology(
        node, parts, nets, roles, u3, adjacency=adj, human_readable=True
    )
    assert topo["kind"] == "mcu"
    assert topo["matched"]
    assert topo["main_part"] is u3
    assert len(topo.get("decouple_parts", set())) >= 1


def test_detect_known_topology_picks_mcu_over_driver_on_mj6050():
    node, u3, parts, nets, roles, adj = _build_tg032_like_graph()
    topo = detect_known_topology(
        node,
        parts,
        nets,
        roles,
        u3,
        human_readable=True,
        topology_detection=True,
    )
    assert topo["kind"] == "mcu"


def test_buck_driver_not_mcu():
    """LED driver + 电感应判 driver 而非 MCU。"""
    node = _FakeNode()
    u2 = _FakePart(
        "U2",
        "LED DRIVER",
        pins=[
            _FakePin("VIN"),
            _FakePin("GND"),
            _FakePin("SW"),
            _FakePin("FB"),
        ],
    )
    for p in u2.pins:
        p.part = u2
    l1 = _FakePart("L1", pins=[_FakePin("1")])
    l1.pins[0].part = l1
    nets = {
        "vin": _FakeNet("VIN"),
        "gnd": _FakeNet("GND"),
        "sw": _FakeNet("SW"),
        "fb": _FakeNet("FB"),
    }
    _wire(u2, "VIN", nets["vin"])
    _wire(u2, "GND", nets["gnd"])
    _wire(u2, "SW", nets["sw"])
    _wire(u2, "FB", nets["fb"])
    _wire(l1, "1", nets["sw"])
    parts = [u2, l1]
    all_nets = list(nets.values())
    roles = {u2: "ic", l1: "passive"}
    adj = {id(u2): {l1}, id(l1): {u2}}

    mcu_sc, mcu_conf, _, mcu_combo, _ = _score_mcu_candidate_ic(
        node, u2, parts, all_nets, roles, set(parts), adj
    )
    drv_sc, drv_conf, _, drv_combo, _ = _score_candidate_ic(
        node, u2, parts, all_nets, roles, set(parts), adj
    )
    assert drv_combo
    assert drv_conf >= 40
    topo = detect_known_topology(
        node, parts, all_nets, roles, u2, human_readable=True
    )
    assert topo["kind"] == "generic_driver"


def test_pair_pins_to_main_prefers_signal_pin_on_decouple():
    """C11 类去耦：一脚 GND、一脚 P35，应对齐信号脚而非 VSS。"""
    node = _FakeNode()
    u3 = _FakePart(
        "U3",
        pins=[_FakePin("7"), _FakePin("8")],
    )
    c11 = _FakePart("C11", pins=[_FakePin("1"), _FakePin("2")])
    for p in (u3, c11):
        for pin in p.pins:
            pin.part = p
    gnd = _FakeNet("GND_0")
    sig = _FakeNet("Net-(U3-P35-TKCAP)")
    _wire(u3, "8", gnd)
    _wire(u3, "7", sig)
    _wire(c11, "1", gnd)
    _wire(c11, "2", sig)
    mp, pp = _pair_pins_to_main(c11, u3, node=node, prefer_signal=True)
    assert mp is u3.pins[0]
    assert mp.name == "7"
    assert pp is c11.pins[1]


def test_colinear_chain_sort_key_prefers_resistor_before_led():
    led = _FakePart("LED1")
    r10 = _FakePart("R10")
    assert _colinear_chain_sort_key(r10) < _colinear_chain_sort_key(led)


def test_mcu_walk_colinear_chain_star_then_series():
    """U3—R10—LED 同网，LED—R12 再串（简化 LED 支路）。"""
    node = _FakeNode()
    u3 = _FakePart("U3", pins=[_FakePin("5"), _FakePin("VSS")])
    r10 = _FakePart("R10", pins=[_FakePin("1"), _FakePin("2")])
    led = _FakePart("LED1", pins=[_FakePin("A"), _FakePin("K")])
    r12 = _FakePart("R12", pins=[_FakePin("1"), _FakePin("2")])
    for p in (u3, r10, led, r12):
        for pin in p.pins:
            pin.part = p

    n_led = _FakeNet("Net-(LED1-2)")
    n_pad = _FakeNet("Net-(LED1-Pad1)")
    _wire(u3, "5", n_led)
    _wire(r10, "2", n_led)
    _wire(led, "A", n_led)
    _wire(led, "K", n_pad)
    _wire(r12, "1", n_pad)

    parts = [u3, r10, led, r12]
    nets = [n_led, n_pad]
    part_set = set(parts)
    used = set()
    chain, _ = _mcu_walk_colinear_chain(
        node, u3, u3.pins[0], nets, part_set, used
    )
    refs = [getattr(p, "ref", "") for p in chain]
    assert refs[0] == "U3"
    assert refs[1] == "R10"
    assert refs[2] == "LED1"
    assert refs[3] == "R12"


def test_mcu_find_colinear_chains_marks_used():
    node, u3, parts, nets, roles, adj = _build_tg032_like_graph()
    specs = _mcu_find_colinear_chains(node, u3, parts, nets)
    assert specs
    outward_refs = set()
    for _, chain in specs:
        for p in chain[1:]:
            outward_refs.add(p.ref)
    assert "R5" in outward_refs or "R6" in outward_refs


def test_walk_colinear_chain_first_step_follows_anchor_pin_only():
    """首步只沿 anchor_pin 的网走，不扫 hub 全部引脚。

    MCU 有 pin1→R6, pin2→R5 两根网；若首步扫全部引脚,
    R5 字母序靠前会被 pin1 的链错误抢走。修复后 pin1 只走
    pin1 那根网，找到 R6。
    """
    node = _FakeNode()
    u3 = _FakePart("U3", pins=[_FakePin("1"), _FakePin("2")])
    r5 = _FakePart("R5", pins=[_FakePin("1"), _FakePin("2")])
    r6 = _FakePart("R6", pins=[_FakePin("1"), _FakePin("2")])
    for p in (u3, r5, r6):
        for pin in p.pins:
            pin.part = p

    net_p04 = _FakeNet("Net-(U3-P04)")
    net_p05 = _FakeNet("Net-(U3-P05)")

    _wire(u3, "1", net_p04)
    _wire(r6, "2", net_p04)
    _wire(u3, "2", net_p05)
    _wire(r5, "2", net_p05)

    part_set = {u3, r5, r6}
    used = set()

    chain_p04, _ = _walk_colinear_chain(
        node, u3, u3.pins[0], part_set, used
    )
    for p in chain_p04[1:]:
        used.add(id(p))
    chain_p05, _ = _walk_colinear_chain(
        node, u3, u3.pins[1], part_set, used
    )

    refs_p04 = [p.ref for p in chain_p04]
    refs_p05 = [p.ref for p in chain_p05]
    assert refs_p04 == ["U3", "R6"], f"pin1 链应走 R6，实际 {refs_p04}"
    assert refs_p05 == ["U3", "R5"], f"pin2 链应走 R5，实际 {refs_p05}"


def test_port_colinear_chain_from_header_stops_at_mcu():
    """Header 引脚 GND/VCC 串阻链在 MCU 前终止（R13/R14 类）。"""
    node = _FakeNode()
    u3 = _FakePart("U3", pins=[_FakePin("12"), _FakePin("8")])
    x1 = _FakePart(
        "X1",
        pins=[_FakePin("1"), _FakePin("2"), _FakePin("3"), _FakePin("4")],
    )
    r13 = _FakePart("R13", pins=[_FakePin("1"), _FakePin("2")])
    r14 = _FakePart("R14", pins=[_FakePin("1"), _FakePin("2")])
    for p in (u3, x1, r13, r14):
        for pin in p.pins:
            pin.part = p

    vcc0 = _FakeNet("VCC_5V_0")
    vcc = _FakeNet("VCC_5V")
    gnd = _FakeNet("GND")
    gnd0 = _FakeNet("GND_0")

    _wire(x1, "1", vcc0)
    _wire(r13, "1", vcc0)
    _wire(r13, "2", vcc)
    _wire(u3, "12", vcc)
    _wire(x1, "4", gnd)
    _wire(r14, "1", gnd)
    _wire(r14, "2", gnd0)
    _wire(u3, "8", gnd0)

    parts = [u3, x1, r13, r14]
    nets = [vcc0, vcc, gnd, gnd0]
    specs, used = _find_port_colinear_chains(
        node, x1, parts, nets, stop_parts={u3, x1}
    )
    chains = {tuple(p.ref for p in chain) for _, chain in specs}
    assert ("X1", "R13") in chains
    assert ("X1", "R14") in chains
    assert id(r13) in used
    assert id(r14) in used
    # MCU 不应出现在 Header 链中
    for _, chain in specs:
        assert u3 not in chain


def test_format_topology_log_mcu():
    line = format_topology_log_line(
        {
            "kind": "mcu",
            "confidence": 80,
            "fallback": False,
            "main_part": _FakePart("U3"),
        }
    )
    assert "MCU 模块" in line
    assert "U3" in line
    assert "专用布局" in line

    weak = format_topology_log_line(
        {
            "kind": "weak_mcu",
            "confidence": 45,
            "fallback": "trunk_aware",
            "main_part": _FakePart("U3"),
        }
    )
    assert "疑似 MCU" in weak
