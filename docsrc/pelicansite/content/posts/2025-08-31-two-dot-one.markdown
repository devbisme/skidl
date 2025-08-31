title: SKiDL 2.1 Release
date: 2025-08-31
author: Dave Vandenbout
slug: skidl-two-dot-one-release

Today marks the release of SKiDL version **2.1.0**.
The increment in the minor version number indicates that this release includes new features and improvements
while maintaining backward compatibility with version 2.0.0.

Here are the changes in 2.1.0:

- `netlist_to_skidl` now generates hierarchical SKiDL code
  that mirrors the hierarchy found in the netlist.
- Parts can be assigned a *part class* that stores attributes for a set of
  parts.
- Nets can be assigned a *net class* that stores attributes for a set of
  nets.
- `SubCircuits` have taken over the `Group`
  functionality. (`Group` has been maintained for backward
  compatibility.)
- `Circuits` now include a tree of `Node`
  objects that store the hierarchical structure.
- Improved tracking of netlist objects back to the source line where
  they were instantiated.
- InSpice has replaced PySpice to enable the use of newer versions of the
  ngspice simulator.
- The `KICAD9` tool identifier was added to support KiCad 9.
  `KICAD9` is now the default tool for new projects.

See [SKiDL's complete history](https://github.com/devbisme/skidl/blob/master/HISTORY.md) for all the changes
made in each release.

