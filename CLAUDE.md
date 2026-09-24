# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) and other AI coding assistants when working with code in this repository.

## Development Environment
- This project uses `pip` for dependency management.
- Tests are managed using `pytest`.
- `tox` is used to run tests across multiple environments (different Python/KiCad versions).

## Common Commands
- **Run all tests (default environment)**: `pytest tests`
- **Run tests across all supported test environments**: `tox`
- **Run a specific test**: `pytest tests/unit_tests/test_something.py`
- **Build the package**: `python -m build` (or `tox -e build`)
- **Clean build artifacts**: `rm dist/*`
- **Install in development mode**: `pip install -e .`

## KiCad Environment

SKiDL uses KiCad symbol and footprint libraries. Set these environment variables to point at your KiCad installation:

```bash
export KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols      # or wherever KiCad 9 installs symbols
export KICAD9_FOOTPRINT_DIR=/usr/share/kicad/footprints  # footprint libraries
```

Replace `9` with your KiCad version (6, 7, 8, 9, 10). Without these, SKiDL will warn that default libraries are unavailable.

## Circuit Design API

### Core Classes

Everything starts with `from skidl import *`:

- **`Part(library, name, footprint=...)`** — a component (resistor, IC, connector)
- **`Net(name)`** — an electrical connection between pins
- **`Bus(name, width)`** — a group of related nets
- **`Circuit`** — container for parts and nets (used as context manager)

### Building Circuits

```python
from skidl import *

with Circuit() as ckt:
    vcc, gnd = Net("VCC"), Net("GND")

    # Create parts — library and part name from KiCad symbol libraries
    r1 = Part("Device", "R", value="10k", footprint="Resistor_SMD:R_0805_2012Metric")
    c1 = Part("Device", "C", value="100nF", footprint="Capacitor_SMD:C_0805_2012Metric")

    # Connect pins with +=
    r1[1] += vcc
    r1[2] += c1[1]
    c1[2] += gnd

    # Generate outputs
    ckt.generate_netlist()                    # .net file for PCB tools
    ckt.generate_schematic(auto_stub=True)    # .kicad_sch for KiCad Eeschema
```

Placement is random, so `generate_schematic()`/`generate_svg()` draw the same
circuit differently on each run. There is no way to pin a layout down; if you
get one worth keeping, keep the generated files.

### Hierarchy with @subcircuit

Use `@subcircuit` to group related parts. This creates hierarchy in schematics and enables grouped placement in layout.

```python
@subcircuit
def bypass_cap(vcc, gnd):
    c = Part("Device", "C", value="100nF", footprint="Capacitor_SMD:C_0805_2012Metric")
    c[1] += vcc
    c[2] += gnd

@subcircuit
def ic_block(vcc, gnd, sig_out):
    u = Part("Device", "R", value="10k", footprint="Resistor_SMD:R_0805_2012Metric")
    u[1] += vcc
    u[2] += sig_out
    bypass_cap(vcc, gnd)  # nested subcircuit

with Circuit() as ckt:
    vcc, gnd, sig = Net("VCC"), Net("GND"), Net("SIG")
    ic_block(vcc, gnd, sig)
```

### Pin Connections

```python
# Single pin to net
r1[1] += vcc

# Multiple pins to same net
gnd += r1[2], c1[2], c2[2]

# Part-to-part (creates implicit net)
r1[2] += c1[1]

# Bus connections
data_bus = Bus("DATA", 8)
data_bus[0] += r1[1]
```

### Finding Parts

Pin numbers are **strings**, not integers — `part["1"]` and `part[1]` both work because SKiDL coerces, but be aware when iterating.

```python
# Search for parts in libraries
results = search_parts_in_libs("ATmega328")

# Get part info
print(r1.ref)       # reference designator, e.g. "R1"
print(r1.value)     # value, e.g. "10k"
print(r1.foot)      # footprint string
print(r1.pins)      # list of Pin objects
```

### Common Pitfalls

- **Missing footprint**: Parts without `footprint=` will warn during schematic generation. Always specify footprints.
- **NC pins**: Use `ckt.NC` for intentionally unconnected pins, not just leaving them floating.
- **Pin numbering**: Pin numbers come from KiCad symbol definitions and may not be sequential (e.g., IC pin 1 might be pin "A1").
- **Library names**: Must match KiCad library names exactly (e.g., `"Device"` not `"device"`, `"Connector_Generic"` not `"Connector"`).

## Project Architecture

SKiDL converts Python circuit descriptions into netlists and schematics for EDA tools (primarily KiCad).

### Key Modules
- `src/skidl/` — core package:
  - `part.py` — `Part` class (components)
  - `net.py` — `Net` class (electrical connections)
  - `pin.py` — `Pin` class (component connection points)
  - `circuit.py` — `Circuit` class (container, generation methods)
  - `bus.py` — `Bus` class (grouped nets)
  - `node.py` — hierarchy tree, `@subcircuit` decorator
  - `schematic_netlist.py` — `build_generic_netlist()`, the JSON handed to `schematizer`
  - `errors.py` — SKiDL's exception types (`PlacementFailure`, `RoutingFailure`)
  - `tools/` — backend interfaces for KiCad 5-10 (netlist, PCB, schematic, SVG, XML, libs)
- `tests/` — test suite:
  - `unit_tests/` — unit tests (manually written and AI-generated)
  - `test_data/` — part libraries for testing
  - `examples/` — example circuits

### Schematic and SVG Generation Live in `schematizer`

Neither schematic nor SVG generation is in this repo. SKiDL's job is electrical
interconnection; the graphical work (placement, routing, writing KiCad files,
drawing SVG) belongs to the separate `schematizer` package.

`Circuit.generate_schematic()` is unchanged from the user's point of view — same
signature, same output files — but internally it:
1. merges nets, then
2. dispatches to the tool's own `gen_sch()` — `tool_modules[tool].gen_sch`, the
   same pattern `generate_netlist`/`generate_pcb`/`generate_xml` use.

`Circuit.generate_svg()` works the same way, dispatching to
`tool_modules[tool].gen_svg` in `tools/kicadN/gen_svg.py`. It is the *same*
pipeline — place, route, then serialize — differing only in the final step, so
an SVG page has the layout of the `.kicad_sch` for the same circuit. It defaults
`auto_stub=True` so a dense circuit yields a readable labelled drawing instead
of a `RoutingFailure`. Hierarchy: one SVG per unflattened sheet, each child
drawn in its parent as a hyperlinked rectangle, with links back up; `flatness`
controls it just as for KiCad.

Each `tools/kicadN/gen_sch.py` is that version's interface to `schematizer`: it
builds a generic, tool-neutral JSON netlist via
`skidl.schematic_netlist.build_generic_netlist()` (embedded symbol definitions +
layout hints like `symtx` and net `stub`/`netio`), calls
`schematizer.render(netlist, tool=TOOL_NAME, ...)`, and translates `schematizer`'s
`PlacementFailure`/`RoutingFailure` into SKiDL's own types from `skidl.errors`
(also importable as `from skidl import PlacementFailure`) — so callers never have
to import the other package. Put any per-KiCad-version handling in that file.

`tools/kicad5/gen_sch.py` and `tools/kicad5/gen_svg.py` exist only to raise a
`ValueError`: KiCad 5 needs the legacy EESCHEMA `.sch` format, and its libraries
carry `part.draw` objects rather than the s-expression graphics the SVG renderer
draws from. A tool with no `gen_sch`/`gen_svg` at all (`spice`, `skidl`) gets a
`ValueError` from the `Circuit` method itself.

Removing the netlistsvg path left `part.draw` (the KiCad 5 symbol graphics
built by `tools/kicad5/lib.py` out of `draw_objs.py`) with **no consumer** — it
was the last thing that read it. Both files stay because the `.lib` parser that
populates `part.draw` is the same one that supplies pins for KiCad 5 netlist,
PCB, and XML output; only the graphics half is now dead weight.

To change anything about placement, routing, or the KiCad file format, work in
the `schematizer` repo — not here. Its engine (and the engine-internals tests
that used to live in `tests/unit_tests/ai_tests/`) is at
`schematizer/src/schematizer/engine/`.

### Randomized output

Placement and routing are randomized, so the same circuit draws differently on
every run and there is no option to make a run reproducible. Tests must not
compare two generated drawings for equality — assert on structure (files
written, element counts, parseability) instead.
