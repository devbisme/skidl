# JLCEDA Pro ENET Import

SKiDL provides an ENET-specific importer alongside the existing KiCad netlist
importer:

```python
from skidl.enet_to_skidl import enet_to_skidl

source = enet_to_skidl("board.enet")
```

The ENET importer reads JLCEDA Pro JSON netlists and emits a single-sheet SKiDL
Python program containing `Net(...)`, `Part(...)`, and pin connection statements.
It does not route ENET data through the KiCad S-expression parser.

The initial implementation targets ENET `version: "2.0.0"` files with a
`components` object, component `props.Designator`, and `pinInfoMap` entries.
JLCEDA uses hash IDs for symbols and footprints, so the importer preserves the
readable `DeviceName` and `FootprintName` metadata for downstream matching.
