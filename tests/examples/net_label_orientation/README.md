# Net-label orientation examples

Two small designs that stress net-label placement so the labels can be eyeballed
in EESCHEMA. A net label should always extend **away** from the pin it sits on,
so the text runs clear of the part body, in every pin direction and for every
KiCad backend (6/7/8/9).

| script | what it stresses |
|---|---|
| `transistor_rotations.py` | 8 PNP transistors in every rotation/mirror, stub labels on every pin — covers all four pin directions including mirrored parts |
| `nested_interface.py` | hierarchical subcircuits mixing stub nets (`VIN2`) and routed nets (`VIN1`) — covers both stub labels and wire/NetTerminal labels |

Run with the default backend (KiCad 9), or pick another:

```bash
python transistor_rotations.py
SKIDL_TOOL=KICAD8 python transistor_rotations.py
```

The render-free regression test
`tests/unit_tests/ai_tests/test_net_label_orientation.py` pins the
direction → `(angle, justify)` mapping and asserts all four backends agree.
