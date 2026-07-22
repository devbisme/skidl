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
- **Build the package**: `python setup.py sdist`
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
  - `schematics/` — schematic generation (placement, routing)
  - `tools/` — backend interfaces for KiCad 6/7/8/9
  - `tools/kicad9/sexp_schematic.py` — KiCad 9 schematic S-expression writer
  - `tools/kicad9/gen_schematic.py` — KiCad 9 schematic generation entry point
- `tests/` — test suite:
  - `unit_tests/` — unit tests (manually written and AI-generated)
  - `test_data/` — part libraries for testing
  - `examples/` — example circuits

### Schematic Generation Internals

For KiCad integration (KiCad 6-9):
- Symbol definition extraction from draw commands
- Hierarchical UUID generation using `uuid.uuid5` with namespace `7026fcc6-e1a0-409e-aaf4-6a17ea82654f`
- Multi-file schematic output (root + sub-sheets for each subcircuit)
- Force-directed placement and routing for component positioning
- Coordinate system: KiCad uses Y-down, requiring transformations
- S-expression output via `simp_sexp.Sexp` (list subclass for KiCad file formats)

### UUID Scheme (Schematic ↔ PCB Cross-Reference)

SKiDL generates deterministic UUIDs so schematics and PCBs can cross-reference:
```python
namespace_uuid = uuid.UUID("7026fcc6-e1a0-409e-aaf4-6a17ea82654f")
part_uuid = uuid.uuid5(namespace_uuid, part.hiername)
sheet_uuid = uuid.uuid5(namespace_uuid, level_name)
kiid_path = "/{sheet_uuid_1}/{sheet_uuid_2}/.../{part_uuid}"
```
