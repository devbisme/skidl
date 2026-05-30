# -*- coding: utf-8 -*-

import json

import pytest

from skidl.enet_to_skidl import EnetFormatError, enet_to_skidl, parse_enet


def make_enet():
    return {
        "version": "2.0.0",
        "components": {
            "gge1": {
                "props": {
                    "Designator": "R1",
                    "DeviceName": "R_0603",
                    "FootprintName": "R_0603",
                },
                "pinInfoMap": {
                    "1": {"number": "1", "net": "+5V"},
                    "2": {"number": "2", "net": "PA10/USART1_RX"},
                },
            },
            "gge2": {
                "props": {
                    "Designator": "U1",
                    "Manufacturer Part": "MCU'1",
                    "DeviceName": "MCU",
                },
                "pinInfoMap": {
                    "1": {"number": "1", "net": "PA10/USART1_RX"},
                },
            },
        },
    }


def test_parse_enet_groups_component_pins_by_net():
    document = parse_enet(json.dumps(make_enet()))

    assert document.version == "2.0.0"
    assert [component.ref for component in document.components] == ["R1", "U1"]
    assert [net.name for net in document.nets] == ["+5V", "PA10/USART1_RX"]
    assert [(node.ref, node.pin_key) for node in document.nets[1].nodes] == [
        ("R1", "2"),
        ("U1", "1"),
    ]


def test_enet_to_skidl_generates_single_sheet_source():
    source = enet_to_skidl(json.dumps(make_enet()))

    assert "def top():" in source
    assert "_p_5V = Net('+5V')" in source
    assert "PA10_USART1_RX = Net('PA10/USART1_RX')" in source
    assert "R1 = Part('*', 'R_0603'" in source
    assert "U1 = Part('*', 'MCU', value=\"MCU'1\"" in source
    assert "PA10_USART1_RX += R1['2'], U1['1']" in source


def test_parse_enet_rejects_duplicate_designators():
    data = make_enet()
    data["components"]["gge2"]["props"]["Designator"] = "R1"

    with pytest.raises(EnetFormatError, match="Duplicate component Designator"):
        parse_enet(json.dumps(data))


def test_parse_enet_names_unconnected_pin(caplog):
    data = make_enet()
    data["components"]["gge1"]["pinInfoMap"]["1"]["net"] = ""

    document = parse_enet(json.dumps(data))

    assert document.nets[1].name == "unconnected-R1-1-1"
    assert "has no net" in caplog.text

