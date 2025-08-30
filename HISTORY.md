# History

## 2.1.0 (2025-08-30)

- Fixed #238: tstamps were incorrectly generated for netlist files.
- [netlist_to_skidl]{.title-ref} now generates hierarchical SKiDL code
  that mirrors the hierarchy found in the netlist.
- Parts can be assigned a part class that stores attributes for a set of
  parts.
- Nets can be assigned a net class that stores attributes for a set of
  nets.
- [SubCircuits]{.title-ref} have taken over the [Group]{.title-ref}
  functionality. ([Group]{.title-ref} has been maintained for backwards
  compatibility.)
- [Circuits]{.title-ref} now include a tree of [Node]{.title-ref}
  objects that stores the hierarchical structure.
- Improved tracking of netlist objects back to the source line where
  they were instantiated.
- InSpice has replaced PySpice to allow the use of newer versions of the
  ngspice simulator.
- [KICAD9]{.title-ref} tool identifier added to support KiCad 9.

## 2.0.1 (2024-12-11)

- Fixed #233: Imported [active_logger]{.title-ref} into
  generate_schematic.py of KiCad 6, 7, 8.
- Fixed #235: Removed merging of multi-segment nets when generating
  netlists, XML, SVG, DOT because it removes pins from existing net
  references. Only merge for schematic generation or SPICE simulation.

## 2.0.0 (2024-11-27)

- No longer compatible with Python 2.
- [\@package]{.title-ref} decorator removed.
- Additional [Part]{.title-ref} attributes can be specified when
  exporting libraries.
- Added [unexpio]{.title-ref} dict to [Interface]{.title-ref} objects
  for accessing I/O without buses expanded into individual nets.
- Added connect() and \_\_iadd\_\_() methods to interconnect
  [Interface]{.title-ref} objects.
- Part libraries are pickled when first loaded for faster access on
  subsequent accesses. The directory for storing the pickled library
  files is specified in the SKiDL configuration file.
- The [KICAD]{.title-ref} tool identifier now points to
  [KICAD8]{.title-ref}.

## 1.2.2 (2024-07-13)

- Added SVG schematic generation feature for KiCad 6, 7, and 8.
- Added backend tool identifiers of [KICAD5]{.title-ref},
  [KICAD6]{.title-ref}, [KICAD7]{.title-ref}, and [KICAD8]{.title-ref}.
- For compatibility, [KICAD]{.title-ref} tool identifier points to
  [KICAD5]{.title-ref}.

## 1.2.1 (2023-07-26)

- [is_url]{.title-ref} function fixed to solve problems with
  [search]{.title-ref} and loading libraries.

## 1.2.0 (2023-07-14)

- Added ability to generate an editable schematic from a Circuit object.
  (Currently only works for KiCad V5.)
- Added Group object for creating hierarchy without using function
  calls.
- [generate_pcb]{.title-ref} now takes an optional list of footprint
  library directories.
- If not explicitly declared, [Part]{.title-ref} objects will load the
  default footprint from their symbol definition.
- Added [empty_footprint_handler()]{.title-ref} for parts without
  footprints that logs errors by default but can be overriden by the
  user.
- Symbol libraries can now be searched on remote repositories by placing
  the URL in the [lib_search_paths]{.title-ref} dictionary. KiCad V6
  symbols are found at
  [https://gitlab.com/kicad/libraries/kicad-symbols/-/raw/master]{.title-ref}
  and V5 symbols are at
  [https://raw.githubusercontent.com/KiCad/kicad-symbols/master/]{.title-ref}.
- [Part]{.title-ref} pins can now be sorted and retrieved in order using
  the [ordered_pins]{.title-ref} property.

## 1.1.0 (2021-10-22)

- Added [generate_pcb()]{.title-ref} function to create a PCB file
  directly from a [Circuit]{.title-ref} object. (Currently only works
  for KiCad.)
- Added [PartTmplt]{.title-ref} shortcut which creates a Part template
  using [dest=TEMPLATE]{.title-ref} implicitly.

## 1.0.0 (2021-05-09)

- Buses can now be created without names and a name will be
  automatically assigned. Or use \"name=\...\" to manually assign a
  name. Or just place a string in the list of arguments and that will be
  used.
- Footprint search can now process directories of footprints without the
  need for an [fp-lib-table]{.title-ref} file.
- [Part]{.title-ref} fields can now be accessed using attributes.
- Creating fields requires use of [Part.fields\[key\]]{.title-ref}
  instead of Part.key.
- Added context manager for [Circuit]{.title-ref} object so Parts/Nets
  can be joined using a [with\...]{.title-ref} statement.
- Adding/removing [Parts]{.title-ref} to/from a [Circuit]{.title-ref}
  can now be done using [+=]{.title-ref} and [-=]{.title-ref}.
- Tags can be added to [Parts]{.title-ref} and [Circuits]{.title-ref}
  for hierarchical naming.
- [Part]{.title-ref} values can now be assigned arbitrary objects
  including units from either PySpice or Pint.
- Multi-function pin names can now be split into a collection of shorter
  aliases, thus reducing the need to access pins using regexes.
- Schematics can now be automatically using the KiCad symbol graphics
  for the parts.
- The library interface now handles the Skywater 130 SPICE libraries.

## 0.0.30 (2020-05-16)

- Added \@package decorator to make subcircuits act like Parts.
- Interfaces now act like dictionaries so the \*\* operator works as
  expected.
- Interface I/O can now be accessed using brackets (\[\]) and via
  attributes (e.g., intfc.a).
- Interface I/O can now be assigned aliases.
- Added tee() function for creating T-junctions in networks.
- Custom ERCs can now be added using the [erc_assert]{.title-ref}
  function.
- Aliases take precedence over default pin names.
- Substring matching in pin names can be enabled/disabled (off by
  default).

## 0.0.29 (2020-01-30)

- Added XSPICE parts capability to SPICE simulations.
- Unconnected XSPICE ports now are set to NULL in SPICE node lists.
- Added no_files() function to disable output to files of netlists,
  ERCs, logs, backup libs.

## 0.0.28 (2019-12-17)

- The `zyc` utility was split into a separate repository and placed on
  PyPi.
- Fixed slicing of grouped part pins so things like `ram['A[1]']` won\'t
  grab `A1`, `A10`, `A11`, etc.

## 0.0.27 (2019-12-16)

- Prevent changing the name of net 0 when generating a SPICE netlist.
- Fixed Pin, Net, Bus and Part iterators so they\'ll work in nested
  loops.
- Part units are automatically added when a part is parsed.
- Files are now opened for reading using latin_1 encoding to allow
  special symbols used by KiCad.
- Part pins can now be aliased directly, e.g. [uc\[5\].aliases +=
  \'gp0\']{.title-ref}.
- Added class method get() to Part to allow finding a part based on
  name, reference, description.
- Refactored ERC functions to allow user-extensibility.
- Created a base object for Circuit, Part, Pin, Net, and Bus objects.
- Added an aliases property to the SKiDL base object so all its children
  could be aliased.
- Updated to perform simulations with ngspice version 30.
- Added a notes property to allow attachment of user notes to Parts,
  Pins, Nets, etc.
- Added net class to net objects for specifying net-specific design
  rules in PCBNEW.
- Ignore multiple pins with the same number in symbols with DeMorgan
  equivalents.
- Fixed problem with non-ASCII chars (e.g. Ohms) in strings.
- Sped-up part/net naming using heap/cache, binary search, sets.
- Sped-up by storing net traversals to avoid recomputation.
- Fixed processing of slices in things like sdram\[\'A\[0:15\]\'\].
- Sped-up part_search() by eliminating unnecessary part parsing.
- Improved schematic generation with graphviz.
- Search now allows AND/OR of parenthesized terms.
- New GUI for searching for parts and footprints.
- Footprint libraries to search are now selected from the global
  fp-lib-table file.
- KiCad library component field values are now stored in a dict in Part
  indexed by the field name or F0, F1, F2\...
- KiCad library component field values are also stored as Part
  attributes using the field name or F0, F1, F2\...
- Added [p]{.title-ref} and [n]{.title-ref} attributes to
  [Part]{.title-ref} object to permit explicit reference to pin numbers
  or names.

## 0.0.26 (2019-01-25)

- `search` command no longer looks in backup library because that leads
  to erroneous hits in all libraries.
- Part objects will now iterate through their pins and len() will return
  the number of pins.
- Updated netlist_to_skidl utility to account for new version of
  kinparse.

## 0.0.25 (2018-12-30)

- Updated website.
- KISYSMOD is no longer used to find part libraries, only
  KICAD_SYMBOL_DIR is used now.

## 0.0.24 (2018-09-15)

- Fixed an error where creating a backup part library for a design would
  create extra pins attached to the nets.

## 0.0.23 (2018-08-25)

- Added Network objects to make it easy to create serial & parallel
  combinations of two-pin parts.
- SKiDL design hierarchy is now embedded in the KiCad netlist that\'s
  generated.

## 0.0.22 (2018-05-XX)

- Added Interface objects for storing complicated sets of I/O signals
  for subsystems.
- ERC no longer redundantly checks every segment of a multi-segment net
  and reports multiple errors.
- copy() function of Part, Bus, Pin, Net objects now returns a scalar
  object while copy(1) returns a list with one object.
- Bus, Pin, and Net objects now have iterators.
- Corrected initialization of KiCad library search paths.

------------------------------------------------------------------------

## 0.0.21 (2018-04-30)

- Added pull() and fetch() methods for getting/creating existing/new Net
  and Bus objects.
- Added drive property to pins to override their default pin function
  attribute.
- Part pins and units can now be accessed as attributes.
- Nets, pins, and buses now support the width property.
- Indexing with brackets now works equivalently for pins, nets, and
  buses.
- Grouped part pins (such as address and data buses) can now be accessed
  using a slice-like notation, e.g. memory\[\'ADDR\[0:7\]\'\].

## 0.0.20 (2018-03-08)

- Matching of pin lists now begins with normal string matching before
  using regexes.
- Added more tests and fixed existing tests.

## 0.0.19 (2018-02-20)

- Selecting part pins now looks for exact match before falling back to
  regex matching.
- PySpice now needs to be manually installed to perform SPICE
  simulations.
- SPICE simulations of subcircuits (.SUBCKT) now supported.
- Improvements/additions to the library of supported SPICE parts.

## 0.0.18 (2018-02-07)

- SPICE simulations of circuits now supported (Python 3 only).

## 0.0.17 (2018-01-23)

- Modularized code into separate files.

## 0.0.16 (2018-01-16)

- Parsing of KiCad EESchema libraries made more robust.
- DEFAULT_TOOL replaced with set_default_tool() function.
- Some code simplification by using a context manager for opening files.

## 0.0.15 (2018-01-09)

- Testing made more robust.

## 0.0.14 (2018-01-05)

- KiCad netlists are now parsed using the external package kinparse.
- Cleaned-up pylint-identified issues.
- Removed absolute file paths to libraries from tests.

## 0.0.13 (2017-08-20)

- Fixed problem where the search function was only returning parts found
  in the last library searched.

## 0.0.12 (2017-04-20)

- Use of builtin now works with Python 2 & 3.
- Started using namedtuple in some places (like net traversal) for
  clarity.
- Corrected pin-to-pin connections so if a net is created, it goes into
  the same Circuit the pins are members of.
- Part templates can now contain a reference to a Circuit object that
  will be applied when the template is instantiated.
- When pins are connected to nets, or nets to nets, the resulting set of
  connected nets are all given the same name.
- Buses are not added to a Circuit object if they are already members of
  it. This fix caused the next problem.
- Buses weren\'t getting added to the Circuit object because they
  already contained a reference to the Circuit. Fixed by clearing ref
  before adding to Circuit.
- Created mini_reset() method to clear circuitry without clearing
  library cache so the libraries don\'t have to be loaded again (slow).
- search() utility now prints the names of libraries as they are
  searched so user sees progress.
- Fixed exceptions if part definition contained non-unicode stuff.
- Hide exceptions that occur when using the show() utility.
- More tests added for NC nets and hand-crafted parts.
- default_circuit and the NC net for the active circuit are now made
  accessible in all modules using \_\_builtin\_\_.
- Corrected error messages that referenced wrong/non-existing variable.
- Inserted NO_LIB for the library if it doesn\'t exist when generating
  KiCad netlists or XML.
- Attributes can now be passed when creating a Circuit object.
- Pins are now associated with part when added to the part.
- Minimum and maximum pins for a part are now computed as needed.
- Each Circuit object now has its own NC net.
- Added tests for bus movement and copying.
- Implemented bus movement between Circuit objects.
- Additional test cases were created.
- Nets and Parts can now be removed from Circuits.
- The circuit that pins and nets are in is now checked before
  connections are made so cross-circuit connections are not created.
- Default members were added to Pin and Part objects so they would
  always exist and not cause errors when missing.
- Implemented moving Parts and Nets from one circuit to another
  (almost).
- Nets with no attached pins are now added to a circuit.
- Re-wrote some tests to account for the presence of no-pin nets in a
  circuit.
- A class method was missing its \'self\' argument.
- Fixed \@subcircuit decorator so it won\'t cause an error if the
  function it decorates doesn\'t have a \'circuit\' keyword argument.
- Split the unit tests across multiple files. Added setup/teardown code.
- Added capability to create multiple, independent Circuit objects to
  which Parts and Nets can be assigned. The default circuit is still the
  target if not Circuit is explicitly referenced.
- Added IOError to exception list for opening a SKiDL part library.

## 0.0.11 (2017-04-04)

- Part libraries in SKiDL format are now supported.
- Parts can now be created on-the-fly and instantiated or added to
  libraries.
- The parts used in a circuit can be stored in a backup SKiDL library
  and used if the original libraries are missing.
- The KiCad standard part libraries were converted to SKiDL libraries
  and placed in skidl.libs.

## 0.0.10 (2017-03-13)

- Nets without pins can now be merged.
- Parts and Pins are now sorted when netlists are generated.
- For an existing Bus, new bus lines can be inserted at any position or
  the bus can be extended.

## 0.0.9 (2017-02-16)

- Use getattr() instead of \_\_class\_\_.\_\_dict\_\_ so that subclasses
  of SKiDL objects can find attributes named within strings without
  searching the \_\_mor\_\_.

## 0.0.8 (2017-01-11)

- skidl_to_netlist now uses templates.
- Default operation of search() is now less exacting.
- Traceback is now suppressed if show() is passed a part name not in a
  library.

## 0.0.7 (2016-09-11)

- Lack of KISYSMOD environment variable no longer causes an exception.
- requirements.txt file now references the requirements from setup.py.
- Changed setup so it generates a pckg_info file with version, author,
  email.

## 0.0.6 (2016-09-10)

- Fixed error caused when trying to find script name when SKiDL is run
  in interactive mode.
- Silenced errors/warnings when loading KiCad part description (.dcm)
  files.

## 0.0.5 (2016-09-07)

- SKiDL now searches for parts with a user-configurable list of library
  search paths.
- Part descriptions and keywords are now loaded from the .dcm file
  associated with a .lib file.

## 0.0.4 (2016-08-27)

- SKiDL scripts can now output netlists in XML format.

## 0.0.3 (2016-08-25)

- Added command-line utility to convert netlists into SKiDL programs.

## 0.0.2 (2016-08-17)

- Changed the link to the documentation.

## 0.0.1 (2016-08-16)

- First release on PyPI.
