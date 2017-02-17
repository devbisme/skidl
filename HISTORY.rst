.. :changelog:

History
-------


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
