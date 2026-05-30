# -*- coding: utf-8 -*-

"""Integration-shaped tests for JLCEDA Pro ENET conversion."""

import json

from skidl.enet_to_skidl import enet_to_skidl


def test_enet_to_skidl_keeps_special_net_names():
    enet = {
        "version": "2.0.0",
        "components": {
            "gge1": {
                "props": {
                    "Designator": "H1",
                    "DeviceName": "HDR-M_2.54_1x02P",
                    "FootprintName": "HDR-TH_2P-P2.54",
                },
                "pinInfoMap": {
                    "1": {"number": "1", "net": "+5V"},
                    "2": {"number": "2", "net": "USB_D-_PA11"},
                },
            }
        },
    }

    source = enet_to_skidl(json.dumps(enet))

    assert "_p_5V = Net('+5V')" in source
    assert "USB_D__PA11 = Net('USB_D-_PA11')" in source
    assert "_p_5V += H1['1']" in source
    assert "USB_D__PA11 += H1['2']" in source
