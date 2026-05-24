# -*- coding: utf-8 -*-

"""generic driver topology 检测与日志格式单元测试。"""

from skidl.geometry import BBox, Point, Tx
from skidl.schematics.topology import (
    _collect_driver_rail_nets,
    _disabled_topology,
    _is_anonymous_net,
    _score_candidate_ic,
    _token_in_text,
    build_driver_rail_plan,
    detect_known_topology,
    format_topology_log_line,
)


class _FakePin:
    def __init__(self, name, part=None):
        self.name = name
        self.part = part
        self.net = None

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
