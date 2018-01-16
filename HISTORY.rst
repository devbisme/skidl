.. :changelog:

History
-------


0.0.16 (2018-01-16)
______________________

* Parsing of KiCad EESchema libraries made more robust.
* DEFAULT_TOOL replaced with set_default_tool() function.
* Some code simplification by using a context manager for opening files.


0.0.15 (2018-01-09)
______________________

* Testing made more robust.


0.0.14 (2018-01-05)
______________________

* KiCad netlists are now parsed using the external package kinparse.
* Cleaned-up pylint-identified issues.
* Removed absolute file paths to libraries from tests.


0.0.13 (2017-08-20)
______________________

* Fixed problem where the search function was only returning parts found in the last library searched.


0.0.12 (2017-04-20)
______________________

* Use of builtin now works with Python 2 & 3.
* Started using namedtuple in some places (like net traversal) for clarity.
* Corrected pin-to-pin connections so if a net is created, it goes into the same Circuit the pins are members of.
* Part templates can now contain a reference to a Circuit object that will be applied when the template is instantiated.
* When pins are connected to nets, or nets to nets, the resulting set of connected nets are all given the same name.
* Buses are not added to a Circuit object if they are already members of it. This fix caused the next problem.
* Buses weren't getting added to the Circuit object because they already contained a reference to the Circuit. Fixed by clearing ref before adding to Circuit.
* Created mini_reset() method to clear circuitry without clearing library cache so the libraries don't have to be loaded again (slow).
* search() utility now prints the names of libraries as they are searched so user sees progress.
* Fixed exceptions if part definition contained non-unicode stuff.
* Hide exceptions that occur when using the show() utility.
* More tests added for NC nets and hand-crafted parts.
* default_circuit and the NC net for the active circuit are now made accessible in all modules using __builtin__.
* Corrected error messages that referenced wrong/non-existing variable.
* Inserted NO_LIB for the library if it doesn't exist when generating KiCad netlists or XML.
* Attributes can now be passed when creating a Circuit object.
* Pins are now associated with part when added to the part.
* Minimum and maximum pins for a part are now computed as needed.
* Each Circuit object now has its own NC net.
* Added tests for bus movement and copying.
* Implemented bus movement between Circuit objects.
* Additional test cases were created.
* Nets and Parts can now be removed from Circuits.
* The circuit that pins and nets are in is now checked before connections are made so cross-circuit connections are not created.
* Default members were added to Pin and Part objects so they would always exist and not cause errors when missing.
* Implemented moving Parts and Nets from one circuit to another (almost).
* Nets with no attached pins are now added to a circuit.
* Re-wrote some tests to account for the presence of no-pin nets in a circuit.
* A class method was missing its 'self' argument.
* Fixed @subcircuit decorator so it won't cause an error if the function it decorates doesn't have a 'circuit' keyword argument.
* Split the unit tests across multiple files. Added setup/teardown code.
* Added capability to create multiple, independent Circuit objects to which Parts and Nets can be assigned. The default circuit is still the target if not Circuit is explicitly referenced.
* Added IOError to exception list for opening a SKiDL part library.


0.0.11 (2017-04-04)
______________________

* Part libraries in SKiDL format are now supported.
* Parts can now be created on-the-fly and instantiated or added to libraries.
* The parts used in a circuit can be stored in a backup SKiDL library and used if the original libraries are missing.
* The KiCad standard part libraries were converted to SKiDL libraries and placed in skidl.libs.


0.0.10 (2017-03-13)
______________________

* Nets without pins can now be merged.
* Parts and Pins are now sorted when netlists are generated.
* For an existing Bus, new bus lines can be inserted at any position or the bus can be extended.


0.0.9 (2017-02-16)
______________________

* Use getattr() instead of __class__.__dict__ so that subclasses of SKiDL objects
  can find attributes named within strings without searching the __mor__.


0.0.8 (2017-01-11)
______________________

* skidl_to_netlist now uses templates.
* Default operation of search() is now less exacting.
* Traceback is now suppressed if show() is passed a part name not in a library.


0.0.7 (2016-09-11)
______________________

* Lack of KISYSMOD environment variable no longer causes an exception.
* requirements.txt file now references the requirements from setup.py.
* Changed setup so it generates a pckg_info file with version, author, email.


0.0.6 (2016-09-10)
______________________

* Fixed error caused when trying to find script name when SKiDL is run in interactive mode.
* Silenced errors/warnings when loading KiCad part description (.dcm) files.


0.0.5 (2016-09-07)
______________________

* SKiDL now searches for parts with a user-configurable list of library search paths.
* Part descriptions and keywords are now loaded from the .dcm file associated with a .lib file.


0.0.4 (2016-08-27)
______________________

* SKiDL scripts can now output netlists in XML format.


0.0.3 (2016-08-25)
______________________

* Added command-line utility to convert netlists into SKiDL programs.


0.0.2 (2016-08-17)
______________________

* Changed the link to the documentation.


0.0.1 (2016-08-16)
______________________

* First release on PyPI.
