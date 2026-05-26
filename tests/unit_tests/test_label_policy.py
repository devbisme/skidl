# -*- coding: utf-8 -*-

"""label_policy：MCU 共线链 / power 网跳过边缘标签。"""

from skidl.schematics.label_policy import (
    net_in_mcu_colinear_set,
    net_skip_add_net_terminal,
    net_skip_auto_stub_large_group,
    net_skip_net_terminal_label,
    net_skip_stub_pin_label,
)


class _FakePart:
    def __init__(self, ref):
        self.ref = ref


class _FakeNet:
    def __init__(self, name):
        self.name = name
        self.pins = []


class _FakeNode:
    def __init__(self, main, colinear_sets=None, topo_kind="mcu"):
        self._last_topology_result = {
            "kind": topo_kind,
            "fallback": False,
            "main_part": main,
        }
        self._mcu_colinear_part_sets = colinear_sets or []
        self._connector_port_part_sets = []

    def _net_connected_parts(self, net):
        return list(getattr(net, "_parts", []))


def test_skip_net_terminal_for_colinear_net():
    u3 = _FakePart("U3")
    r10 = _FakePart("R10")
    led = _FakePart("LED1")
    net = _FakeNet("Net-(LED1-2)")
    net._parts = [u3, r10, led]
    node = _FakeNode(u3, colinear_sets=[frozenset({u3, r10, led})])
    assert net_skip_net_terminal_label(node, net)
    assert net_in_mcu_colinear_set(node, net)


def test_skip_add_net_terminal_for_mcu_led_chain():
    u3 = _FakePart("U3")
    u3.pins = [None] * 20
    r10 = _FakePart("R10")
    led = _FakePart("LED1")
    net = _FakeNet("Net-(LED1-2)")
    net.pins = [type("P", (), {"part": p})() for p in (led, r10, u3)]
    assert net_skip_add_net_terminal(net)


def test_skip_stub_pin_label_for_mcu_led_chain():
    u3 = _FakePart("U3")
    u3.pins = [None] * 20
    r10 = _FakePart("R10")
    led = _FakePart("LED1")
    net = _FakeNet("Net-(LED1-2)")
    net._parts = [u3, r10, led]
    net.pins = [type("P", (), {"part": p})() for p in (led, r10, u3)]
    node = _FakeNode(u3)
    assert net_skip_stub_pin_label(node, net)


def test_skip_large_group_stub_for_mcu_chain():
    u3 = _FakePart("U3")
    r10 = _FakePart("R10")
    net = _FakeNet("Net-(LED1-2)")
    net._parts = [u3, r10]
    node = _FakeNode(u3)
    assert net_skip_auto_stub_large_group(node, net)
