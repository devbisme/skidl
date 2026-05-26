# -*- coding: utf-8 -*-

"""power net 识别与 KiCad power symbol 外形映射单元测试。"""

import pytest

from skidl.schematics.power_net import (
    is_power_net_name,
    resolve_power_symbol_shape,
    resolve_power_symbol_value,
)

_FALLBACK_SHAPES = {
    "GND",
    "AGND",
    "DGND",
    "PGND",
    "VCC",
    "VDD",
    "VSS",
    "+3V3",
    "+5V",
    "+12V",
}


@pytest.mark.parametrize(
    "name",
    [
        "GND",
        "GND_0",
        "GND1",
        "AGND",
        "DGND",
        "VSS",
        "VCC",
        "VCC_5V",
        "VCC_5V_0",
        "VCC_3V3",
        "VCC_3V",
        "3V3",
        "5V",
        "+5V",
        "+3V3",
        "VBUS",
        "VBAT",
    ],
)
def test_is_power_net_name_positive(name):
    assert is_power_net_name(name)


@pytest.mark.parametrize("name", ["DATA", "CLK", "RESET", "N$1", "FOO_BAR"])
def test_is_power_net_name_negative(name):
    assert not is_power_net_name(name)


def test_resolve_power_symbol_value_keeps_original_name():
    assert resolve_power_symbol_value("GND_0") == "GND_0"
    assert resolve_power_symbol_value("VCC_5V_0") == "VCC_5V_0"


@pytest.mark.parametrize(
    ("name", "shape"),
    [
        ("GND", "GND"),
        ("GND_0", "GND"),
        ("GND1", "GND"),
        ("AGND", "AGND"),
        ("VCC_5V_0", "+5V"),
        ("VCC_5V", "+5V"),
        ("5V", "+5V"),
        ("+5V", "+5V"),
        ("VCC_3V3", "+3V3"),
        ("VCC_3V", "+3V3"),
        ("3V3", "+3V3"),
        ("VCC", "VCC"),
    ],
)
def test_resolve_power_symbol_shape(name, shape):
    assert resolve_power_symbol_shape(name, _FALLBACK_SHAPES) == shape


def test_resolve_power_symbol_shape_unknown():
    assert resolve_power_symbol_shape("FOO_BAR", _FALLBACK_SHAPES) is None
    assert resolve_power_symbol_shape("VCC_99V", _FALLBACK_SHAPES) is None
