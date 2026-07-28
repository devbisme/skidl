title: SKiDL 2.3.0 Release
date: 2026-07-28
author: Dave Vandenbout
slug: skidl-two-dot-three-dot-zero-release

Today marks the release of SKiDL version **2.3.0**. The headline changes are:

* **KiCad 10 support.** A `KICAD10` tool identifier and part libraries were added,
  and the generic `KICAD` identifier now points to it as the latest version.
* **Better schematics.** The schematic generator gained an auto-stubbing mode
  (`generate_schematic(auto_stub=True)`) that turns hard-to-route nets into labels,
  emits power symbols for power nets, and runs an ERC-correction loop to clean things up.
  Net-label orientation, power symbols, and multi-unit part references were all fixed,
  and the improvements were propagated across KiCad 6 through 10.
* **Python 3.14 support.**
* **SPICE fixes.** Netlist generation now keeps pin order correct for parts and subcircuits.
* **netlist_to_skidl** now synthesizes missing ancestor sheets and tolerates the
  value-less boolean properties found in KiCad 10 netlists.

Thanks to GitHub users [lachlanfysh](https://github.com/lachlanfysh),
[freudenthal](https://github.com/freudenthal),
[giri256](https://github.com/giri256), and
[Javaispythonsb](https://github.com/Javaispythonsb) for their contributions to this release.

See [SKiDL's complete history](https://github.com/devbisme/skidl/blob/master/HISTORY.md) for all the changes
made in each release.
