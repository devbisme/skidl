title: SKiDL 3.0.0 Release
date: 2026-10-16
author: Dave Vandenbout
slug: skidl-three-dot-zero-dot-zero-release

Today marks the release of SKiDL version **3.0.0**. The major version bump reflects
a structural change: schematic generation no longer lives inside SKiDL.

* **Schematics moved to [schematizer](https://pypi.org/project/schematizer/).**
  SKiDL now builds a generic, tool-neutral netlist and hands it to the separate
  `schematizer` package, which does placement, routing, and file writing.
  `generate_schematic()` has the same signature and produces the same files, so
  existing scripts don't need to change.
* **New SVG output.** `generate_svg()` no longer needs `netlistsvg`. It draws the same
  placed-and-routed schematic that `generate_schematic()` produces. Hierarchical designs
  become one linked SVG page per sheet, with each subcircuit drawn as a clickable box.
  The function now returns the output directory instead of a JSON dict.
* **KiCad 5 schematic and SVG output were dropped.** Netlist, PCB, and XML output for
  KiCad 5 still work.
* **`PlacementFailure` and `RoutingFailure`** are now importable from the top level
  (`from skidl import PlacementFailure`). The old `skidl.schematics` module is gone.
* **KiCad 10 `.kicad_symdir` libraries** (one file per symbol) are now supported.
* Fixed fp-lib-table discovery with versioned KiCad preference paths (#326).

Thanks to GitHub user [michaelamici](https://github.com/michaelamici) for a contribution to this release.

See [SKiDL's complete history](https://github.com/devbisme/skidl/blob/master/HISTORY.md) for all the changes
made in each release.
