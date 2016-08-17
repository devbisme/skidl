===============================
skidl
===============================

.. .. image:: https://img.shields.io/travis/xesscorp/skidl.svg
        :target: https://travis-ci.org/xesscorp/skidl

.. image:: https://img.shields.io/pypi/v/skidl.svg
        :target: https://pypi.python.org/pypi/skidl


SKiDL is a module that allows you to compactly describe the interconnection of 
electronic circuits and components using Python.
The resulting Python program performs electrical rules checking
for common mistakes and outputs a netlist that serves as input to
a PCB layout tool.

* Free software: MIT license
* Documentation: http://xesscorp.github.io/skidl/index.html

Features
--------

* Has a powerful, flexible syntax (because it *is* Python).
* Permits compact descriptions of electronic circuits (think about *not* tracing
  signals through a multi-page schematic).
* Allows textual descriptions of electronic circuits (think about using 
  ``diff`` and `git <https://en.wikipedia.org/wiki/Git_(software)>`_ for circuits).
* Performs electrical rules checking (ERC) for common mistakes (e.g., unconnected device I/O pins).
* Supports linear / hierarchical / mixed descriptions of electronic designs.
* Fosters design reuse (think about using `PyPi <https://pypi.org/>`_ and `Github <https://github.com/>`_
  to distribute electronic designs).
* Makes possible the creation of *smart circuit modules* whose behavior / structure are changed parametrically
  (think about filters whose component values are automatically adjusted based on your
  desired cutoff frequency).
* Can work with any ECAD tool (only two methods are needed: one for reading the part libraries and another
  for outputing the correct netlist format).
* Takes advantage of all the benefits of the Python ecosystem (because it *is* Python).

As a very simple example, the SKiDL program below describes a circuit that
takes an input voltage, divides it by three, and outputs it::

    from skidl import *

    gnd = Net('GND')  # Ground reference.
    vin = Net('VI')   # Input voltage to the divider.
    vout = Net('VO')  # Output voltage from the divider.
    r1, r2 = 2 * Part('device', 'R', TEMPLATE)  # Create two resistors.
    r1.value, r1.footprint = '1K',  'Resistors_SMD:R_0805'  # Set resistor values
    r2.value, r2.footprint = '500', 'Resistors_SMD:R_0805'  # and footprints.
    r1[1] += vin      # Connect the input to the first resistor.
    r2[2] += gnd      # Connect the second resistor to ground.
    vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    generate_netlist()

And this is the output that can be fed to a program like KiCad's ``PCBNEW`` to
create the physical PCB::

    (export (version D)
      (design
        (source "C:/Users/DEVB/PycharmProjects/test1\test.py")
        (date "08/12/2016 11:13 AM")
        (tool "SKiDL (0.0.1)"))
      (components
        (comp (ref R1)
          (value 1K)
          (footprint Resistors_SMD:R_0805))
        (comp (ref R2)
          (value 500)
          (footprint Resistors_SMD:R_0805)))
      (nets
        (net (code 0) (name "VI")
          (node (ref R1) (pin 1)))
        (net (code 1) (name "GND")
          (node (ref R2) (pin 2)))
        (net (code 2) (name "VO")
          (node (ref R1) (pin 2))
          (node (ref R2) (pin 1))))
    )
