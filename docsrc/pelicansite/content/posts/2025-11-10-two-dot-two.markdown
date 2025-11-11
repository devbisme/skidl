title: SKiDL 2.2 Release
date: 2025-11-10
author: Dave Vandenbout
slug: skidl-two-dot-two-release

Today marks the release of SKiDL version **2.2.0**.
The increment in the minor version number indicates that this release includes new features and improvements
while maintaining backward compatibility with version 2.1.

Here are the changes in 2.2.0:

- The `skidl-part-search` command-line utility has been added for searching part libraries.
  This utility uses an SQLite database to store part data extracted from symbol libraries.
  The initialization of the database takes several minutes, but after that queries for
  parts are *fast* and will remain so since the database only needs to be initialized once.
  Part searching can be done in a batch or interactive mode.
  In interactive mode, details on part I/O can be browsed.
  Part queries can now include nested, parenthesized search terms with Boolean operators.
- .skidlcfg configuration files are now searched for in platform-appropriate per-user directories.
- Alternate names in KiCad symbols are now added as aliases to part pins.
- Chained indexing (`prt[name1][name2]`) or attributes (`prt[name1].name2`) can now be used
  to select a single pin from a list of part pins that all match with `name1`.
- Pin names containing spaces are now allowed if they are enclosed in single or double quotes.
- `initialize()` and `finalize()` were added to maintain hierarchy when using `SubCircuit` subclasses.
- The I/O of a Subcircuit module can now be accessed using bracket ([]) indexing as if the module were a Part.
- Individual bus lines can now be assigned and accessed by aliases.

See [SKiDL's complete history](https://github.com/devbisme/skidl/blob/master/HISTORY.md) for all the changes
made in each release.

