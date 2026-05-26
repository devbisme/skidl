# -*- coding: utf-8 -*-

"""generic driver topology 检测与日志格式单元测试。"""

from collections import defaultdict

from skidl.geometry import BBox, Point, Segment, Tx
from skidl.schematics.route import (
    Router,
    _prune_linear_endpoint_tails,
    _prune_driver_preroute_tails,
    is_pin_attached,
    repair_unattached_same_net_pins,
    route_driver_rails,
)
from skidl.schematics.trunk_layout import classify_trunk_nets
from skidl.schematics.topology import (
    _build_driver_chain_order,
    _collect_driver_rail_nets,
    _disabled_topology,
    _is_anonymous_net,
    _score_candidate_ic,
    _token_in_text,
    build_driver_rail_plan,
    detect_known_topology,
    driver_wire_preserve_net_set,
    format_topology_log_line,
)


class _FakePin:
    def __init__(self, name, part=None, pt=None):
        self.name = name
        self.part = part
        self.net = None
        self.pt = pt or Point(0, 0)
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
        self.name = ref
        self.pins = pins or []
        self.place_bbox = None
        self.tx = None


class _FakeNode:
    def __init__(self):
        self.parts = []
        self.wires = {}
        self.junctions = defaultdict(list)
        self.children = {}
        self._driver_chain_parts = set()

    def _net_connected_parts(self, net, allowed_parts=None):
        return [p for p in getattr(net, "_parts", []) if allowed_parts is None or p in allowed_parts]

    def _net_names_of(self, part):
        names = set()
        for pin in part.pins:
            if pin.net is not None and getattr(pin.net, "name", None):
                names.add(str(pin.net.name))
        return names

    def _is_power_net_name(self, name):
        return "GND" in str(name).upper() or "VCC" in str(name).upper()

    def _is_local_functional_cluster(self, net, net_parts):
        return False

    def get_internal_pins(self, net):
        return [pin for pin in net.pins if pin.part in self.parts and not pin.stub]

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


def test_token_in_text():
    assert _token_in_text("Net-(U2-DIM)", ("DIM",))
    assert _token_in_text("/LED+", ("LED", "W+"))


def test_disabled_topology():
    topo = _disabled_topology()
    assert topo["kind"] == "disabled"
    line = format_topology_log_line(topo)
    assert "未启用拓扑识别" in line


def test_detect_known_topology_disabled_when_not_human_readable():
    node = _FakeNode()
    topo = detect_known_topology(node, [], [], {}, None, human_readable=False)
    assert topo["kind"] == "disabled"


def test_detect_known_topology_disabled_flag():
    node = _FakeNode()
    topo = detect_known_topology(
        node, [], [], {}, None, human_readable=True, topology_detection=False
    )
    assert topo["kind"] == "disabled"
    assert topo["fallback"] == "trunk_aware"


def test_format_topology_log_lines():
    assert "疑似 driver" in format_topology_log_line(
        {
            "kind": "weak_generic_driver",
            "confidence": 48,
            "fallback": "trunk_aware",
            "main_part": _FakePart("U2"),
        }
    )
    line = format_topology_log_line(
        {
            "kind": "generic_driver",
            "confidence": 76,
            "fallback": False,
            "main_part": _FakePart("U2"),
        }
    )
    assert "已识别为 driver 模块" in line
    assert "主控 U2" in line
    assert "已启用专用布局" in line
    assert "未识别" in format_topology_log_line({"kind": "unrecognized", "confidence": 0})


def test_driver_score_combo_on_minimal_buck_like_graph():
    """VIN+GND+SW+FB 组合应达到较高 confidence。"""
    node = _FakeNode()
    u2 = _FakePart(
        "U2",
        "LED DRIVER",
        pins=[
            _FakePin("VIN"),
            _FakePin("GND"),
            _FakePin("SW"),
            _FakePin("FB"),
            _FakePin("PWM"),
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
        "pwm": _FakeNet("PWM"),
    }
    _wire(u2, "VIN", nets["vin"])
    _wire(u2, "GND", nets["gnd"])
    _wire(u2, "SW", nets["sw"])
    _wire(u2, "FB", nets["fb"])
    _wire(u2, "PWM", nets["pwm"])
    _wire(l1, "1", nets["sw"])

    parts = [u2, l1]
    all_nets = list(nets.values())
    roles = {"ic": "ic"}
    roles = {u2: "ic", l1: "passive"}
    sc, conf, reasons, combo, _ = _score_candidate_ic(
        node, u2, parts, all_nets, roles, set(parts), {id(u2): {l1}}
    )
    assert combo
    assert conf >= 40
    assert sc >= 8


def test_build_driver_rail_plan_uses_visual_bbox_not_place_padding():
    """place_bbox 膨胀很大时，bottom_y 仍应贴近 lbl_bbox 下沿。"""
    grid = 100
    u2 = _FakePart("U2")
    u2.tx = Tx()
    u2.lbl_bbox = BBox(Point(0, 0), Point(400, 500))
    u2.place_bbox = BBox(Point(-2000, -2000), Point(6000, 8000))
    gnd = _FakeNet("GND")
    vin = _FakeNet("VCC_24V")
    topology = {
        "kind": "generic_driver",
        "fallback": False,
        "control_nets": [],
        "switch_or_drive_nets": [],
        "ground_nets": [gnd],
        "input_nets": [vin],
        "power_nets": [vin],
        "output_nets": [],
    }
    node = _FakeNode()
    plan = build_driver_rail_plan(
        node,
        [u2],
        [gnd, vin],
        topology,
        u2,
        human_readable=True,
        driver_rail_routing=True,
        grid=grid,
    )
    assert plan["enabled"]
    assert plan["bottom_y"] <= 500 + 3 * grid


def test_collect_driver_rail_nets_excludes_control_and_anonymous():
    node = _FakeNode()
    u2 = _FakePart("U2")
    topology = {
        "control_nets": [],
        "switch_or_drive_nets": [],
        "ground_nets": [],
        "input_nets": [],
        "power_nets": [],
        "output_nets": [],
    }
    led_p = _FakeNet("LED+")
    gnd = _FakeNet("GND")
    pwm = _FakeNet("PWM")
    anon = _FakeNet("Net-(U2-Pad3)")
    sw = _FakeNet("SW")
    top, bottom, control = _collect_driver_rail_nets(
        [led_p, gnd, pwm, anon, sw], topology, node, u2, set()
    )
    assert led_p in top
    assert gnd in bottom
    assert pwm in control
    assert anon not in top and anon not in bottom
    assert _is_anonymous_net(anon)


def test_collect_driver_rail_nets_promotes_input_power_tokens_to_top():
    node = _FakeNode()
    u2 = _FakePart("U2", pins=[_FakePin("VIN"), _FakePin("GND")])
    c1 = _FakePart("C1", pins=[_FakePin("1")])
    j1 = _FakePart("J1", pins=[_FakePin("1")])
    for part in (u2, c1, j1):
        for pin in part.pins:
            pin.part = part

    topology = {
        "control_nets": [],
        "switch_or_drive_nets": [],
        "ground_nets": [],
        "input_nets": [],
        "power_nets": [],
        "output_nets": [],
    }
    vin = _FakeNet("DC_IN_24V")
    gnd = _FakeNet("GND")
    _wire(u2, "VIN", vin)
    _wire(c1, "1", vin)
    _wire(j1, "1", vin)
    _wire(u2, "GND", gnd)

    top, bottom, control = _collect_driver_rail_nets(
        [vin, gnd], topology, node, u2, {u2, c1, j1}
    )

    assert vin in top
    assert gnd in bottom
    assert control == []
    assert topology["rail_debug"]["DC_IN_24V"]["direction"] == "top"
    assert "token:DC_IN" in topology["rail_debug"]["DC_IN_24V"]["reasons"]


def test_collect_driver_rail_nets_promotes_anonymous_input_with_strong_topology_evidence():
    node = _FakeNode()
    u2 = _FakePart("U2", pins=[_FakePin("VIN"), _FakePin("IN"), _FakePin("DIM")])
    c1 = _FakePart("C1", pins=[_FakePin("1")])
    d1 = _FakePart("D1", pins=[_FakePin("K"), _FakePin("A")])
    l1 = _FakePart("L1", pins=[_FakePin("1")])
    for part in (u2, c1, d1, l1):
        for pin in part.pins:
            pin.part = part

    topology = {
        "control_nets": [],
        "switch_or_drive_nets": [],
        "ground_nets": [],
        "input_nets": [],
        "power_nets": [],
        "output_nets": [],
    }
    anon_input = _FakeNet("NET-(D1-K)")
    anon_control = _FakeNet("NET-(U2-DIM)")
    _wire(u2, "VIN", anon_input)
    _wire(u2, "IN", anon_input)
    _wire(c1, "1", anon_input)
    _wire(d1, "K", anon_input)
    _wire(l1, "1", anon_input)
    _wire(u2, "DIM", anon_control)

    top, bottom, control = _collect_driver_rail_nets(
        [anon_input, anon_control], topology, node, u2, {u2, c1, d1, l1}
    )

    assert anon_input in top
    assert anon_control not in top
    assert anon_control not in bottom
    assert anon_control not in control
    assert bottom == []
    assert topology["rail_debug"]["NET-(D1-K)"]["selected_direction"] == "top"
    assert topology["rail_debug"]["NET-(D1-K)"]["rejected_reason"] == ""
    assert "main_pin:VIN" in topology["rail_debug"]["NET-(D1-K)"]["reasons"]
    assert "input_cap" in topology["rail_debug"]["NET-(D1-K)"]["reasons"]
    assert "input_diode" in topology["rail_debug"]["NET-(D1-K)"]["reasons"]
    assert topology["rail_debug"]["NET-(U2-DIM)"]["rejected_reason"] == "anonymous_or_blank"


def _build_tg032_like_driver_graph():
    node = _FakeNode()
    u2 = _FakePart(
        "U2",
        "PT4115",
        pins=[
            _FakePin("SW"),
            _FakePin("GND"),
            _FakePin("DIM"),
            _FakePin("LED"),
            _FakePin("CSN"),
            _FakePin("VIN"),
        ],
    )
    d1 = _FakePart("D1", pins=[_FakePin("A"), _FakePin("K")])
    l1 = _FakePart("L1", "68uH", pins=[_FakePin("1"), _FakePin("2")])
    p3 = _FakePart("P3", "LED Output", pins=[_FakePin("1"), _FakePin("2")])
    r1 = _FakePart("R1", "0.43R", pins=[_FakePin("1"), _FakePin("2")])
    r3 = _FakePart("R3", "3.3K", pins=[_FakePin("1"), _FakePin("2")])
    r4 = _FakePart("R4", "4.7K", pins=[_FakePin("1"), _FakePin("2")])
    c1 = _FakePart("C1", "47uF", pins=[_FakePin("1")])
    for part in (u2, d1, l1, p3, r1, r3, r4, c1):
        for pin in part.pins:
            pin.part = part

    led_p = _FakeNet("/LED+")
    led_n = _FakeNet("/LED-")
    pwm = _FakeNet("/PWM")
    gnd = _FakeNet("GND")
    d1_a = _FakeNet("Net-(D1-A)")
    d1_k = _FakeNet("Net-(D1-K)")
    u2_dim = _FakeNet("Net-(U2-DIM)")

    _wire(u2, "LED", led_p)
    _wire(p3, "1", led_p)
    _wire(r1, "2", led_p)
    _wire(l1, "1", led_n)
    _wire(p3, "2", led_n)
    _wire(r3, "1", pwm)
    _wire(r4, "2", gnd)
    _wire(u2, "GND", gnd)
    _wire(u2, "SW", d1_a)
    _wire(d1, "A", d1_a)
    _wire(l1, "2", d1_a)
    _wire(u2, "CSN", d1_k)
    _wire(u2, "VIN", d1_k)
    _wire(d1, "K", d1_k)
    _wire(r1, "1", d1_k)
    _wire(c1, "1", d1_k)
    _wire(r3, "2", u2_dim)
    _wire(r4, "1", u2_dim)
    _wire(u2, "DIM", u2_dim)

    parts = [u2, d1, l1, p3, r1, r3, r4, c1]
    nets = [led_p, led_n, pwm, gnd, d1_a, d1_k, u2_dim]
    roles = {
        u2: "ic",
        d1: "passive",
        l1: "passive",
        p3: "connector",
        r1: "passive",
        r3: "passive",
        r4: "passive",
        c1: "decoupling",
    }
    return node, parts, nets, roles, u2, l1, p3, r1, r3, r4, d1_k


def test_detect_known_topology_groups_tg032_parts_conservatively():
    node, parts, nets, roles, u2, l1, p3, r1, r3, r4, d1_k = _build_tg032_like_driver_graph()

    topo = detect_known_topology(
        node,
        parts,
        nets,
        roles,
        u2,
        human_readable=True,
    )

    assert topo["kind"] == "generic_driver"
    assert d1_k in topo["input_nets"]
    assert l1 in topo["power_loop_parts"]
    assert r1 in topo["sense_feedback_parts"]
    assert r3 in topo["control_parts"]
    assert r4 in topo["control_parts"]


def test_build_driver_chain_order_keeps_inductor_between_ic_and_output():
    node, parts, nets, roles, u2, l1, p3, r1, r3, r4, _d1_k = _build_tg032_like_driver_graph()
    topo = detect_known_topology(
        node,
        parts,
        nets,
        roles,
        u2,
        human_readable=True,
    )

    chain, chain_parts = _build_driver_chain_order(node, roles, topo, u2)

    assert l1 in chain_parts
    assert chain.index(u2) < chain.index(l1) < chain.index(p3)


def test_classify_trunk_nets_keeps_led_rails_and_adds_input_power_top():
    node = _FakeNode()
    u2 = _FakePart(
        "U2",
        "PT4115",
        pins=[_FakePin("VIN"), _FakePin("GND"), _FakePin("OUT"), _FakePin("LEDN")],
    )
    c1 = _FakePart("C1", pins=[_FakePin("1")])
    j1 = _FakePart("J1", pins=[_FakePin("1")])
    d1 = _FakePart("D1", pins=[_FakePin("1")])
    led_conn = _FakePart("J2", pins=[_FakePin("1"), _FakePin("2")])
    for part in (u2, c1, j1, d1, led_conn):
        for pin in part.pins:
            pin.part = part

    vin = _FakeNet("DC_IN_24V")
    gnd = _FakeNet("GND")
    led_p = _FakeNet("/LED+")
    led_n = _FakeNet("/LED-")
    _wire(u2, "VIN", vin)
    _wire(c1, "1", vin)
    _wire(j1, "1", vin)
    _wire(d1, "1", vin)
    _wire(u2, "GND", gnd)
    _wire(led_conn, "2", gnd)
    _wire(u2, "OUT", led_p)
    _wire(led_conn, "1", led_p)
    _wire(u2, "LEDN", led_n)

    roles = {
        u2: "ic",
        c1: "decoupling",
        j1: "connector",
        d1: "passive",
        led_conn: "connector",
    }
    trunk = classify_trunk_nets(
        node,
        [u2, c1, j1, d1, led_conn],
        [vin, gnd, led_p, led_n],
        roles,
        u2,
    )

    assert vin in trunk["top"]
    assert led_p in trunk["top"]
    assert gnd in trunk["bottom"]
    assert node._trunk_candidate_debug["DC_IN_24V"]["best_side"] == "top"
    assert "main_pin:VIN" in node._trunk_candidate_debug["DC_IN_24V"]["reasons"]


def test_classify_trunk_nets_promotes_only_strong_anonymous_input_rails():
    node = _FakeNode()
    u2 = _FakePart(
        "U2",
        "PT4115",
        pins=[_FakePin("VIN"), _FakePin("IN"), _FakePin("SW"), _FakePin("DIM")],
    )
    c1 = _FakePart("C1", pins=[_FakePin("1")])
    d1 = _FakePart("D1", pins=[_FakePin("K"), _FakePin("A")])
    j1 = _FakePart("J1", pins=[_FakePin("1")])
    l1 = _FakePart("L1", pins=[_FakePin("1")])
    for part in (u2, c1, d1, j1, l1):
        for pin in part.pins:
            pin.part = part

    anon_input = _FakeNet("NET-(D1-K)")
    anon_switch = _FakeNet("NET-(D1-A)")
    anon_control = _FakeNet("NET-(U2-DIM)")
    _wire(u2, "VIN", anon_input)
    _wire(u2, "IN", anon_input)
    _wire(c1, "1", anon_input)
    _wire(d1, "K", anon_input)
    _wire(j1, "1", anon_input)
    _wire(l1, "1", anon_input)
    _wire(u2, "SW", anon_switch)
    _wire(d1, "A", anon_switch)
    _wire(u2, "DIM", anon_control)

    roles = {
        u2: "ic",
        c1: "decoupling",
        d1: "passive",
        j1: "connector",
        l1: "passive",
    }
    trunk = classify_trunk_nets(
        node,
        [u2, c1, d1, j1, l1],
        [anon_input, anon_switch, anon_control],
        roles,
        u2,
    )

    if anon_input in trunk["top"]:
        assert node._trunk_candidate_debug["NET-(D1-K)"]["best_side"] == "top"
    else:
        assert node._trunk_candidate_debug["NET-(D1-K)"]["rejected_reason"] == "anonymous_or_blank"
    assert anon_switch not in trunk["top"]
    assert anon_switch not in trunk["bottom"]
    assert anon_control not in trunk["top"]
    assert node._trunk_candidate_debug["NET-(D1-A)"]["rejected_reason"] == "anonymous_or_blank"
    assert node._trunk_candidate_debug.get("NET-(U2-DIM)", {}).get("rejected_reason", "anonymous_or_blank") == "anonymous_or_blank"


def test_build_driver_rail_plan_adds_per_net_span_from_connected_pins():
    grid = 100
    node = _FakeNode()
    u2 = _FakePart("U2", pins=[_FakePin("VIN", pt=Point(0, 0))])
    c1 = _FakePart("C1", pins=[_FakePin("1", pt=Point(0, 0))])
    far = _FakePart("J9")
    for part, center_x in ((u2, 0), (c1, 800), (far, 5000)):
        part.tx = Tx(dx=center_x, dy=0)
        part.lbl_bbox = BBox(Point(-100, -100), Point(100, 100))
        part.place_bbox = BBox(Point(-200, -200), Point(200, 200))
    for pin in u2.pins:
        pin.part = u2
    for pin in c1.pins:
        pin.part = c1
    node.parts = [u2, c1, far]

    vin = _FakeNet("VCC")
    _wire(u2, "VIN", vin)
    _wire(c1, "1", vin)

    topology = {
        "kind": "generic_driver",
        "fallback": False,
        "control_nets": [],
        "switch_or_drive_nets": [],
        "ground_nets": [],
        "input_nets": [vin],
        "power_nets": [vin],
        "output_nets": [],
    }

    plan = build_driver_rail_plan(
        node,
        node.parts,
        [vin],
        topology,
        u2,
        human_readable=True,
        driver_rail_routing=True,
        grid=grid,
    )

    assert plan["enabled"]
    assert plan["x_max"] >= 5000
    assert plan["rail_spans"][vin] == (-100, 900)


def test_route_driver_rails_trims_span_but_still_covers_all_connected_pins():
    grid = 100
    node = _FakeNode()
    u2 = _FakePart("U2", pins=[_FakePin("VIN", pt=Point(0, 100))])
    c1 = _FakePart("C1", pins=[_FakePin("1", pt=Point(0, 0))])
    c2 = _FakePart("C2", pins=[_FakePin("1", pt=Point(0, 0))])
    far = _FakePart("J9")
    for part, dx, dy in ((u2, 0, 0), (c1, 600, 0), (c2, 1200, 0), (far, 4800, 0)):
        part.tx = Tx(dx=dx, dy=dy)
        part.lbl_bbox = BBox(Point(-100, -100), Point(100, 100))
        part.place_bbox = BBox(Point(-300, -300), Point(300, 300))
    for pin in u2.pins:
        pin.part = u2
    for pin in c1.pins:
        pin.part = c1
    for pin in c2.pins:
        pin.part = c2
    node.parts = [u2, c1, c2, far]

    vin = _FakeNet("VCC")
    _wire(u2, "VIN", vin)
    _wire(c1, "1", vin)
    _wire(c2, "1", vin)

    node._last_topology_result = {
        "kind": "generic_driver",
        "fallback": False,
        "main_part": u2,
        "control_nets": [],
        "switch_or_drive_nets": [],
        "ground_nets": [],
        "input_nets": [vin],
        "power_nets": [vin],
        "output_nets": [],
    }

    handled = route_driver_rails(
        node,
        [vin],
        human_readable=True,
        driver_rail_routing=True,
        grid=grid,
    )

    assert vin in handled
    assert vin in node.wires
    horiz = [seg for seg in node.wires[vin] if seg.p1.y == seg.p2.y]
    vert = [seg for seg in node.wires[vin] if seg.p1.x == seg.p2.x]
    assert len(horiz) == 1
    assert len(vert) == 3
    assert horiz[0].p1.x == -100
    assert horiz[0].p2.x == 1300
    assert horiz[0].p2.x < 4800
    assert {seg.p1.x for seg in vert} == {0, 600, 1200}


def test_route_driver_rails_skips_local_two_pin_non_power_chain_net():
    grid = 100
    node = _FakeNode()
    d1 = _FakePart("D1", pins=[_FakePin("A", pt=Point(0, 0))])
    r1 = _FakePart("R1", pins=[_FakePin("1", pt=Point(0, 0))])
    for part, dx in ((d1, 0), (r1, 600)):
        part.tx = Tx(dx=dx, dy=0)
        for pin in part.pins:
            pin.part = part
    node.parts = [d1, r1]
    node._driver_chain_parts = {d1, r1}
    node._last_topology_result = {"kind": "disabled"}
    node._driver_rail_plan = {
        "enabled": True,
        "grid": grid,
        "top_nets": [],
        "bottom_nets": [],
    }

    local = _FakeNet("NET-(D1-A)")
    _wire(d1, "A", local)
    _wire(r1, "1", local)

    handled = route_driver_rails(
        node,
        [local],
        human_readable=True,
        driver_rail_routing=True,
        grid=grid,
    )

    assert local not in handled
    assert local not in node.wires


def test_route_driver_rails_keeps_power_like_two_pin_chain_net():
    grid = 100
    node = _FakeNode()
    u1 = _FakePart("U1", pins=[_FakePin("VIN", pt=Point(0, 100))])
    c1 = _FakePart("C1", pins=[_FakePin("1", pt=Point(0, 100))])
    for part, dx in ((u1, 0), (c1, 700)):
        part.tx = Tx(dx=dx, dy=0)
        for pin in part.pins:
            pin.part = part
    node.parts = [u1, c1]
    node._driver_chain_parts = {u1, c1}
    node._last_topology_result = {"kind": "disabled"}
    node._driver_rail_plan = {
        "enabled": True,
        "grid": grid,
        "top_nets": [],
        "bottom_nets": [],
    }

    vcc = _FakeNet("VCC")
    _wire(u1, "VIN", vcc)
    _wire(c1, "1", vcc)

    handled = route_driver_rails(
        node,
        [vcc],
        human_readable=True,
        driver_rail_routing=True,
        grid=grid,
    )

    assert vcc in handled
    horiz = [seg for seg in node.wires[vcc] if seg.p1.y == seg.p2.y]
    vert = [seg for seg in node.wires[vcc] if seg.p1.x == seg.p2.x]
    assert len(horiz) == 1
    assert len(vert) == 2


def test_prune_driver_preroute_tails_keeps_connections_and_one_grid_margin():
    grid = 100
    node = _FakeNode()
    u2 = _FakePart("U2", pins=[_FakePin("VIN", pt=Point(0, 100))])
    l1 = _FakePart("L1", pins=[_FakePin("1", pt=Point(0, 100))])
    for part, dx in ((u2, 0), (l1, 600)):
        part.tx = Tx(dx=dx, dy=0)
        for pin in part.pins:
            pin.part = part
    node.parts = [u2, l1]

    vin = _FakeNet("VCC")
    _wire(u2, "VIN", vin)
    _wire(l1, "1", vin)
    segs = [
        Segment(Point(-600, 0), Point(1600, 0)),
        Segment(Point(0, 100), Point(0, 0)),
        Segment(Point(600, 100), Point(600, 0)),
    ]

    pruned = _prune_driver_preroute_tails(node, vin, segs, grid)
    horiz = [seg for seg in pruned if seg.p1.y == seg.p2.y]

    assert len(horiz) == 1
    assert horiz[0].p1.x == -100
    assert horiz[0].p2.x == 700
    assert is_pin_attached(u2.pins[0], pruned)
    assert is_pin_attached(l1.pins[0], pruned)


def test_prune_driver_preroute_tails_removes_dangling_endpoint_beyond_last_stub():
    grid = 100
    node = _FakeNode()
    u2 = _FakePart("U2", pins=[_FakePin("VIN", pt=Point(0, 100))])
    c1 = _FakePart("C1", pins=[_FakePin("1", pt=Point(0, 100))])
    for part, dx in ((u2, 0), (c1, 800)):
        part.tx = Tx(dx=dx, dy=0)
        for pin in part.pins:
            pin.part = part
    node.parts = [u2, c1]

    vin = _FakeNet("VCC")
    _wire(u2, "VIN", vin)
    _wire(c1, "1", vin)
    segs = [
        Segment(Point(0, 0), Point(1200, 0)),
        Segment(Point(0, 100), Point(0, 0)),
        Segment(Point(800, 100), Point(800, 0)),
    ]

    pruned = _prune_driver_preroute_tails(node, vin, segs, grid)

    assert Segment(Point(0, 0), Point(900, 0)) in pruned
    assert Segment(Point(800, 100), Point(800, 0)) in pruned
    assert Segment(Point(0, 100), Point(0, 0)) in pruned
    assert not any(seg == Segment(Point(0, 0), Point(1200, 0)) for seg in pruned)


def test_prune_driver_preroute_tails_keeps_real_junction_endpoint():
    grid = 100
    node = _FakeNode()
    vin = _FakeNet("VCC")
    segs = [
        Segment(Point(0, 0), Point(1000, 0)),
        Segment(Point(1000, 0), Point(1000, 300)),
        Segment(Point(400, -100), Point(400, 0)),
    ]
    node.junctions[vin].append(Point(1000, 0))

    pruned = _prune_driver_preroute_tails(node, vin, segs, grid)
    horiz = [seg for seg in pruned if seg.p1.y == seg.p2.y]

    assert len(horiz) == 1
    assert horiz[0].p1 == Point(300, 0)
    assert horiz[0].p2 == Point(1000, 0)
    assert Segment(Point(1000, 0), Point(1000, 300)) in pruned


def test_prune_linear_endpoint_tails_handles_trunk_net_without_touching_branch():
    grid = 100
    node = _FakeNode()
    trunk = _FakeNet("/LED+")
    segs = [
        Segment(Point(-200, 0), Point(1200, 0)),
        Segment(Point(0, 100), Point(0, 0)),
        Segment(Point(900, 0), Point(900, 300)),
    ]

    pruned = _prune_linear_endpoint_tails(node, trunk, segs, grid)
    horiz = [seg for seg in pruned if seg.p1.y == seg.p2.y]

    assert len(horiz) == 1
    assert horiz[0].p1 == Point(-100, 0)
    assert horiz[0].p2 == Point(900, 0)
    assert Segment(Point(900, 0), Point(900, 300)) in pruned


def test_driver_wire_preserve_net_set_keeps_prerouted_rails():
    grid = 100
    node = _FakeNode()
    u2 = _FakePart("U2", pins=[_FakePin("VIN", pt=Point(0, 0))])
    c1 = _FakePart("C1", pins=[_FakePin("1", pt=Point(0, 0))])
    for part, dx in ((u2, 0), (c1, 500)):
        part.tx = Tx(dx=dx, dy=0)
        part.lbl_bbox = BBox(Point(-100, -100), Point(100, 100))
        part.place_bbox = BBox(Point(-200, -200), Point(200, 200))
    for pin in u2.pins:
        pin.part = u2
    for pin in c1.pins:
        pin.part = c1
    node.parts = [u2, c1]

    vin = _FakeNet("VCC")
    _wire(u2, "VIN", vin)
    _wire(c1, "1", vin)

    node._last_topology_result = {
        "kind": "generic_driver",
        "fallback": False,
        "main_part": u2,
        "control_nets": [],
        "switch_or_drive_nets": [],
        "ground_nets": [],
        "input_nets": [vin],
        "power_nets": [vin],
        "output_nets": [],
    }
    node._driver_rail_plan = build_driver_rail_plan(
        node,
        node.parts,
        [vin],
        node._last_topology_result,
        u2,
        human_readable=True,
        driver_rail_routing=True,
        grid=grid,
    )

    preserve = driver_wire_preserve_net_set(
        node,
        [vin],
        human_readable=True,
        driver_rail_routing=True,
        grid=grid,
    )

    assert vin in preserve


def test_repair_unattached_pin_adds_short_stub_to_same_net_rail():
    grid = 100
    node = _FakeNode()
    r1 = _FakePart("R1", pins=[_FakePin("1", pt=Point(0, 0))])
    r1.tx = Tx(dx=200, dy=100)
    r1.pins[0].part = r1
    node.parts = [r1]

    vin = _FakeNet("VCC")
    _wire(r1, "1", vin)
    node.wires[vin] = [Segment(Point(0, 0), Point(500, 0))]

    repaired = repair_unattached_same_net_pins(node, [vin], grid=grid)

    assert repaired == 1
    assert is_pin_attached(r1.pins[0], node.wires[vin])
    assert any(
        seg.p1 == Point(200, 0) and seg.p2 == Point(200, 100)
        for seg in node.wires[vin]
    )


def test_repair_unattached_pin_does_not_cross_attach_other_net():
    grid = 100
    node = _FakeNode()
    c10 = _FakePart("C10", pins=[_FakePin("1", pt=Point(0, 0))])
    c10.tx = Tx(dx=200, dy=100)
    c10.pins[0].part = c10
    node.parts = [c10]

    gnd = _FakeNet("GND")
    other = _FakeNet("SW")
    _wire(c10, "1", gnd)
    node.wires[gnd] = [Segment(Point(0, 0), Point(500, 0))]
    node.wires[other] = [Segment(Point(200, -100), Point(200, 100))]

    repaired = repair_unattached_same_net_pins(node, [gnd], grid=grid)

    assert repaired == 0
    assert not is_pin_attached(c10.pins[0], node.wires[gnd])
    assert len(node.wires[gnd]) == 1


def test_repair_unattached_pin_does_not_duplicate_existing_attach():
    grid = 100
    node = _FakeNode()
    l1 = _FakePart("L1", pins=[_FakePin("1", pt=Point(0, 0))])
    l1.tx = Tx(dx=300, dy=100)
    l1.pins[0].part = l1
    node.parts = [l1]

    sw = _FakeNet("SW")
    _wire(l1, "1", sw)
    node.wires[sw] = [Segment(Point(300, 0), Point(300, 100))]

    repaired = repair_unattached_same_net_pins(node, [sw], grid=grid)

    assert repaired == 0
    assert len(node.wires[sw]) == 1


def test_repair_unattached_pin_splits_same_net_wire_under_pin():
    grid = 100
    node = _FakeNode()
    c1 = _FakePart("C1", pins=[_FakePin("1", pt=Point(0, 0))])
    c1.tx = Tx(dx=200, dy=0)
    c1.pins[0].part = c1
    node.parts = [c1]

    led = _FakeNet("LED+")
    _wire(c1, "1", led)
    node.wires[led] = [Segment(Point(0, 0), Point(400, 0))]

    repaired = repair_unattached_same_net_pins(node, [led], grid=grid)

    assert repaired == 1
    assert is_pin_attached(c1.pins[0], node.wires[led])
    assert len(node.wires[led]) == 2
    assert any(
        seg.p1 == Point(0, 0) and seg.p2 == Point(200, 0) for seg in node.wires[led]
    )
    assert any(
        seg.p1 == Point(200, 0) and seg.p2 == Point(400, 0)
        for seg in node.wires[led]
    )


def test_passive_attach_prefers_collinear_trunk_axis():
    grid = 100
    node = _FakeNode()
    r4 = _FakePart("R4", pins=[_FakePin("1", pt=Point(0, 0)), _FakePin("2", pt=Point(200, 0))])
    r4.tx = Tx(dx=200, dy=200)
    for pin in r4.pins:
        pin.part = r4
    node.parts = [r4]

    vin = _FakeNet("VCC")
    _wire(r4, "1", vin)
    node.wires[vin] = [
        Segment(Point(100, 0), Point(100, 100)),
        Segment(Point(100, 100), Point(200, 100)),
    ]

    repaired = repair_unattached_same_net_pins(node, [vin], grid=grid)

    assert repaired == 1
    assert is_pin_attached(r4.pins[0], node.wires[vin])
    assert any(
        seg.p1 == Point(100, 0) and seg.p2 == Point(100, 200)
        for seg in node.wires[vin]
    )
    assert any(
        seg.p1 == Point(100, 200) and seg.p2 == Point(200, 200)
        for seg in node.wires[vin]
    )
    assert not any(
        seg.p1 == Point(200, 100) and seg.p2 == Point(200, 200)
        for seg in node.wires[vin]
    )


def test_passive_collinear_attach_falls_back_when_extension_blocked():
    grid = 100
    node = _FakeNode()
    r4 = _FakePart("R4", pins=[_FakePin("1", pt=Point(0, 0)), _FakePin("2", pt=Point(200, 0))])
    r4.tx = Tx(dx=200, dy=200)
    for pin in r4.pins:
        pin.part = r4
    node.parts = [r4]

    vin = _FakeNet("VCC")
    other = _FakeNet("SW")
    _wire(r4, "1", vin)
    node.wires[vin] = [
        Segment(Point(100, 0), Point(100, 100)),
        Segment(Point(100, 100), Point(200, 100)),
    ]
    node.wires[other] = [Segment(Point(0, 150), Point(150, 150))]

    repaired = repair_unattached_same_net_pins(node, [vin], grid=grid)

    assert repaired == 1
    assert is_pin_attached(r4.pins[0], node.wires[vin])
    assert any(
        seg.p1 == Point(200, 100) and seg.p2 == Point(200, 200)
        for seg in node.wires[vin]
    )
    assert not any(
        seg.p1 == Point(100, 0) and seg.p2 == Point(100, 200)
        for seg in node.wires[vin]
    )


def test_passive_collinear_attach_does_not_break_capacitor_stub_repair():
    grid = 100
    node = _FakeNode()
    c1 = _FakePart("C1", pins=[_FakePin("1", pt=Point(0, 0)), _FakePin("2", pt=Point(100, 0))])
    c1.tx = Tx(dx=200, dy=100)
    for pin in c1.pins:
        pin.part = c1
    node.parts = [c1]

    gnd = _FakeNet("GND")
    _wire(c1, "1", gnd)
    node.wires[gnd] = [Segment(Point(0, 0), Point(400, 0))]

    repaired = repair_unattached_same_net_pins(node, [gnd], grid=grid)

    assert repaired == 1
    assert is_pin_attached(c1.pins[0], node.wires[gnd])
    assert any(
        seg.p1 == Point(200, 0) and seg.p2 == Point(200, 100)
        for seg in node.wires[gnd]
    )


def test_non_passive_attach_keeps_existing_stub_strategy():
    grid = 100
    node = _FakeNode()
    u3 = _FakePart("U3", pins=[_FakePin("IO", pt=Point(0, 0)), _FakePin("NC", pt=Point(200, 0))])
    u3.tx = Tx(dx=200, dy=200)
    for pin in u3.pins:
        pin.part = u3
    node.parts = [u3]

    sig = _FakeNet("SIG")
    _wire(u3, "IO", sig)
    node.wires[sig] = [
        Segment(Point(100, 0), Point(100, 100)),
        Segment(Point(100, 100), Point(200, 100)),
    ]

    repaired = repair_unattached_same_net_pins(node, [sig], grid=grid)

    assert repaired == 1
    assert is_pin_attached(u3.pins[0], node.wires[sig])
    assert any(
        seg.p1 == Point(200, 100) and seg.p2 == Point(200, 200)
        for seg in node.wires[sig]
    )
    assert not any(
        seg.p1 == Point(100, 0) and seg.p2 == Point(100, 200)
        for seg in node.wires[sig]
    )


def test_passive_jog_cleanup_replaces_r3_style_l_stub_with_straight_stub():
    grid = 100
    node = _FakeNode()
    r3 = _FakePart("R3", pins=[_FakePin("1", pt=Point(0, 0)), _FakePin("2", pt=Point(0, 200))])
    src = _FakePart("J1", pins=[_FakePin("1", pt=Point(0, 0))])
    for part, dx, dy in ((r3, 100, 100), (src, 0, 0)):
        part.tx = Tx(dx=dx, dy=dy)
        part.bbox = BBox(Point(-50, -50), Point(50, 250))
        for pin in part.pins:
            pin.part = part
    node.parts = [r3, src]

    pwm = _FakeNet("PWM")
    _wire(r3, "1", pwm)
    _wire(src, "1", pwm)
    node.wires[pwm] = [
        Segment(Point(0, 0), Point(400, 0)),
        Segment(Point(80, 0), Point(80, 50)),
        Segment(Point(80, 50), Point(100, 50)),
        Segment(Point(100, 50), Point(100, 100)),
    ]

    repaired = repair_unattached_same_net_pins(node, [pwm], grid=grid)

    assert repaired == 0
    assert any(
        seg.p1 == Point(100, 0) and seg.p2 == Point(100, 100)
        for seg in node.wires[pwm]
    )
    assert not any(
        seg.p1 == Point(80, 50) and seg.p2 == Point(100, 50)
        for seg in node.wires[pwm]
    )
    assert not any(
        seg.p1 == Point(80, 0) and seg.p2 == Point(80, 50)
        for seg in node.wires[pwm]
    )


def test_passive_jog_cleanup_skips_when_straight_stub_would_hit_other_net():
    grid = 100
    node = _FakeNode()
    r3 = _FakePart("R3", pins=[_FakePin("1", pt=Point(0, 0)), _FakePin("2", pt=Point(0, 200))])
    src = _FakePart("J1", pins=[_FakePin("1", pt=Point(0, 0))])
    for part, dx, dy in ((r3, 100, 100), (src, 0, 0)):
        part.tx = Tx(dx=dx, dy=dy)
        part.bbox = BBox(Point(-50, -50), Point(50, 250))
        for pin in part.pins:
            pin.part = part
    node.parts = [r3, src]

    pwm = _FakeNet("PWM")
    sw = _FakeNet("SW")
    _wire(r3, "1", pwm)
    _wire(src, "1", pwm)
    node.wires[pwm] = [
        Segment(Point(0, 0), Point(400, 0)),
        Segment(Point(80, 0), Point(80, 50)),
        Segment(Point(80, 50), Point(100, 50)),
        Segment(Point(100, 50), Point(100, 100)),
    ]
    node.wires[sw] = [Segment(Point(100, 20), Point(100, 80))]

    repaired = repair_unattached_same_net_pins(node, [pwm], grid=grid)

    assert repaired == 0
    assert any(
        seg.p1 == Point(80, 50) and seg.p2 == Point(100, 50)
        for seg in node.wires[pwm]
    )
    assert any(
        seg.p1 == Point(100, 50) and seg.p2 == Point(100, 100)
        for seg in node.wires[pwm]
    )
    assert not any(
        seg.p1 == Point(100, 0) and seg.p2 == Point(100, 100)
        for seg in node.wires[pwm]
    )


def test_passive_jog_cleanup_keeps_existing_straight_capacitor_attach():
    grid = 100
    node = _FakeNode()
    c1 = _FakePart("C1", pins=[_FakePin("1", pt=Point(0, 0)), _FakePin("2", pt=Point(100, 0))])
    src = _FakePart("J1", pins=[_FakePin("1", pt=Point(0, 0))])
    for part, dx, dy in ((c1, 200, 100), (src, 0, 0)):
        part.tx = Tx(dx=dx, dy=dy)
        part.bbox = BBox(Point(-50, -50), Point(150, 50))
        for pin in part.pins:
            pin.part = part
    node.parts = [c1, src]

    gnd = _FakeNet("GND")
    _wire(c1, "1", gnd)
    _wire(src, "1", gnd)
    node.wires[gnd] = [
        Segment(Point(0, 0), Point(400, 0)),
        Segment(Point(200, 0), Point(200, 100)),
    ]

    repaired = repair_unattached_same_net_pins(node, [gnd], grid=grid)

    assert repaired == 0
    assert len(node.wires[gnd]) == 2
    assert any(
        seg.p1 == Point(200, 0) and seg.p2 == Point(200, 100)
        for seg in node.wires[gnd]
    )


def test_humanize_wires_removes_passive_attach_jog_for_attached_pin():
    node = _FakeNode()
    node._route_options = {"human_readable": True}
    r3 = _FakePart("R3", pins=[_FakePin("1", pt=Point(0, 0)), _FakePin("2", pt=Point(0, 200))])
    src = _FakePart("J1", pins=[_FakePin("1", pt=Point(0, 0))])
    for part, dx, dy in ((r3, 100, 100), (src, 0, 0)):
        part.tx = Tx(dx=dx, dy=dy)
        part.bbox = BBox(Point(-50, -50), Point(50, 250))
        for pin in part.pins:
            pin.part = part
    node.parts = [r3, src]

    pwm = _FakeNet("PWM")
    _wire(r3, "1", pwm)
    _wire(src, "1", pwm)
    node.wires[pwm] = [
        Segment(Point(0, 0), Point(400, 0)),
        Segment(Point(80, 0), Point(80, 50)),
        Segment(Point(80, 50), Point(100, 50)),
        Segment(Point(100, 50), Point(100, 100)),
    ]

    Router.humanize_wires(node)

    assert any(
        seg.p1 == Point(100, 0) and seg.p2 == Point(100, 100)
        for seg in node.wires[pwm]
    )
    assert not any(
        seg.p1 == Point(80, 50) and seg.p2 == Point(100, 50)
        for seg in node.wires[pwm]
    )


def test_humanize_wires_keeps_passive_attach_corner_when_it_is_a_real_branch():
    node = _FakeNode()
    node._route_options = {"human_readable": True}
    r3 = _FakePart("R3", pins=[_FakePin("1", pt=Point(0, 0)), _FakePin("2", pt=Point(0, 200))])
    src = _FakePart("J1", pins=[_FakePin("1", pt=Point(0, 0))])
    load = _FakePart("J2", pins=[_FakePin("1", pt=Point(0, 0))])
    for part, dx, dy in ((r3, 100, 100), (src, 0, 0), (load, 160, 50)):
        part.tx = Tx(dx=dx, dy=dy)
        part.bbox = BBox(Point(-50, -50), Point(50, 250))
        for pin in part.pins:
            pin.part = part
    node.parts = [r3, src, load]

    pwm = _FakeNet("PWM")
    _wire(r3, "1", pwm)
    _wire(src, "1", pwm)
    _wire(load, "1", pwm)
    node.wires[pwm] = [
        Segment(Point(0, 0), Point(400, 0)),
        Segment(Point(80, 0), Point(80, 50)),
        Segment(Point(80, 50), Point(100, 50)),
        Segment(Point(100, 50), Point(100, 100)),
        Segment(Point(100, 50), Point(160, 50)),
    ]

    Router.humanize_wires(node)

    assert any(
        seg.p1 == Point(80, 50) and seg.p2 == Point(100, 50)
        for seg in node.wires[pwm]
    )
    assert any(
        seg.p1 == Point(100, 50) and seg.p2 == Point(160, 50)
        for seg in node.wires[pwm]
    )
    assert not any(
        seg.p1 == Point(100, 0) and seg.p2 == Point(100, 100)
        for seg in node.wires[pwm]
    )


def test_generic_driver_passive_pin_attach_repair_after_rail_preroute():
    grid = 100
    node = _FakeNode()
    u2 = _FakePart("U2", pins=[_FakePin("VIN", pt=Point(0, 100))])
    l1 = _FakePart("L1", pins=[_FakePin("1", pt=Point(0, 0))])
    c10 = _FakePart("C10", pins=[_FakePin("1", pt=Point(0, 0))])
    for part, dx, dy in ((u2, 0, 0), (l1, 600, -100), (c10, 1200, -100)):
        part.tx = Tx(dx=dx, dy=dy)
        if part is u2:
            part.lbl_bbox = BBox(Point(-100, -100), Point(100, 100))
            part.place_bbox = BBox(Point(-300, -300), Point(300, 300))
        else:
            part.lbl_bbox = BBox(Point(-100, 0), Point(100, 0))
            part.place_bbox = BBox(Point(-150, 0), Point(150, 0))
        for pin in part.pins:
            pin.part = part
    node.parts = [u2, l1, c10]

    vin = _FakeNet("VCC")
    _wire(u2, "VIN", vin)
    _wire(l1, "1", vin)
    _wire(c10, "1", vin)
    node._last_topology_result = {
        "kind": "generic_driver",
        "fallback": False,
        "main_part": u2,
        "control_nets": [],
        "switch_or_drive_nets": [],
        "ground_nets": [],
        "input_nets": [vin],
        "power_nets": [vin],
        "output_nets": [],
    }

    handled = route_driver_rails(
        node,
        [vin],
        human_readable=True,
        driver_rail_routing=True,
        grid=grid,
    )
    assert vin in handled

    rail_y = min(seg.p1.y for seg in node.wires[vin] if seg.p1.y == seg.p2.y)
    node.wires[vin] = [seg for seg in node.wires[vin] if seg.p1.y == seg.p2.y]
    assert not is_pin_attached(l1.pins[0], node.wires[vin])
    assert not is_pin_attached(c10.pins[0], node.wires[vin])

    repaired = repair_unattached_same_net_pins(node, [vin], grid=grid)

    assert repaired == 2
    assert is_pin_attached(l1.pins[0], node.wires[vin])
    assert is_pin_attached(c10.pins[0], node.wires[vin])
    assert any(
        seg.p1 == Point(600, rail_y) and seg.p2 == Point(600, -100)
        for seg in node.wires[vin]
    )
    assert any(
        seg.p1 == Point(1200, rail_y) and seg.p2 == Point(1200, -100)
        for seg in node.wires[vin]
    )
