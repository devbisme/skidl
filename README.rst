===============================
skidl
===============================

.. image:: https://img.shields.io/pypi/v/skidl.svg
        :target: https://pypi.python.org/pypi/skidl


The SKiDL Python package lets you compactly describe the interconnection of 
electronic circuits and components.
The resulting Python program performs electrical rules checking
for common mistakes and outputs a netlist that serves as input to
a PCB layout tool.

* Free software: MIT license
* Documentation: http://devbisme.github.io/skidl
* User Forum: https://github.com/devbisme/skidl/discussions

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
* Can perform SPICE simulations (Python 3 only).
* Takes advantage of all the benefits of the Python ecosystem (because it *is* Python).

As a very simple example (see more in the 
`blog <https://devbisme.github.io/skidl/category/posts.html>`_),
the SKiDL program below describes a 
`two-input AND gate <https://raw.githubusercontent.com/nturley/netlistsvg/master/doc/and.svg?sanitize=true>`_
built from discrete transistors:

.. image:: https://raw.githubusercontent.com/nturley/netlistsvg/master/doc/and.svg?sanitize=true

.. code-block:: python

    from skidl import *

    # Create part templates.
    q = Part("Device", "Q_PNP_CBE", dest=TEMPLATE)
    r = Part("Device", "R", dest=TEMPLATE)

    # Create nets.
    gnd, vcc = Net("GND"), Net("VCC")
    a, b, a_and_b = Net("A"), Net("B"), Net("A_AND_B")

    # Instantiate parts.
    gndt = Part("power", "GND")             # Ground terminal.
    vcct = Part("power", "VCC")             # Power terminal.
    q1, q2 = q(2)                           # Two transistors.
    r1, r2, r3, r4, r5 = r(5, value="10K")  # Five 10K resistors.

    # Make connections between parts.
    a & r1 & q1["B C"] & r4 & q2["B C"] & a_and_b & r5 & gnd
    b & r2 & q1["B"]
    q1["C"] & r3 & gnd
    vcc += q1["E"], q2["E"], vcct
    gnd += gndt

    generate_netlist(tool=KICAD8) # Create KICAD version 8 netlist.

And this is the output that can be fed to a program like KiCad's ``PCBNEW`` to
create the physical PCB::

  (export (version D)
    (design
      (source "/home/devb/projects/KiCad/tools/skidl/tests/examples/svg/simple_and_gate.py")
      (date "07/19/2024 05:54 AM")
      (tool "SKiDL (1.2.2)"))
    (components
      (comp (ref #PWR1)
        (value GND)
        (footprint )
        (fields
          (field (name F0) #PWR)
          (field (name F1) GND))
        (libsource (lib power) (part GND))
        (sheetpath (names /top/18388231966295430075) (tstamps /top/18388231966295430075)))
      (comp (ref #PWR2)
        (value VCC)
        (footprint )
        (fields
          (field (name F0) #PWR)
          (field (name F1) VCC))
        (libsource (lib power) (part VCC))
        (sheetpath (names /top/12673122245445984714) (tstamps /top/12673122245445984714)))
      (comp (ref Q1)
        (value Q_PNP_CBE)
        (footprint )
        (fields
          (field (name F0) Q)
          (field (name F1) Q_PNP_CBE))
        (libsource (lib Device) (part Q_PNP_CBE))
        (sheetpath (names /top/5884947020177711792) (tstamps /top/5884947020177711792)))
      (comp (ref Q2)
        (value Q_PNP_CBE)
        (footprint )
        (fields
          (field (name F0) Q)
          (field (name F1) Q_PNP_CBE))
        (libsource (lib Device) (part Q_PNP_CBE))
        (sheetpath (names /top/12871193304116279102) (tstamps /top/12871193304116279102)))
      (comp (ref R1)
        (value 10K)
        (footprint )
        (fields
          (field (name F0) R)
          (field (name F1) R))
        (libsource (lib Device) (part R))
        (sheetpath (names /top/17200003438453088695) (tstamps /top/17200003438453088695)))
      (comp (ref R2)
        (value 10K)
        (footprint )
        (fields
          (field (name F0) R)
          (field (name F1) R))
        (libsource (lib Device) (part R))
        (sheetpath (names /top/12314015795656540138) (tstamps /top/12314015795656540138)))
      (comp (ref R3)
        (value 10K)
        (footprint )
        (fields
          (field (name F0) R)
          (field (name F1) R))
        (libsource (lib Device) (part R))
        (sheetpath (names /top/11448722674936198910) (tstamps /top/11448722674936198910)))
      (comp (ref R4)
        (value 10K)
        (footprint )
        (fields
          (field (name F0) R)
          (field (name F1) R))
        (libsource (lib Device) (part R))
        (sheetpath (names /top/2224275500810828611) (tstamps /top/2224275500810828611)))
      (comp (ref R5)
        (value 10K)
        (footprint )
        (fields
          (field (name F0) R)
          (field (name F1) R))
        (libsource (lib Device) (part R))
        (sheetpath (names /top/3631169005149914336) (tstamps /top/3631169005149914336))))
    (nets
      (net (code 1) (name A)
        (node (ref R1) (pin 1)))
      (net (code 2) (name A_AND_B)
        (node (ref Q2) (pin 1))
        (node (ref R5) (pin 1)))
      (net (code 3) (name B)
        (node (ref R2) (pin 1)))
      (net (code 4) (name GND)
        (node (ref #PWR1) (pin 1))
        (node (ref R3) (pin 2))
        (node (ref R5) (pin 2)))
      (net (code 5) (name N$1)
        (node (ref Q1) (pin 2))
        (node (ref R1) (pin 2))
        (node (ref R2) (pin 2)))
      (net (code 6) (name N$2)
        (node (ref Q1) (pin 1))
        (node (ref R3) (pin 1))
        (node (ref R4) (pin 1)))
      (net (code 7) (name N$3)
        (node (ref Q2) (pin 2))
        (node (ref R4) (pin 2)))
      (net (code 8) (name VCC)
        (node (ref #PWR2) (pin 1))
        (node (ref Q1) (pin 3))
        (node (ref Q2) (pin 3))))
  )
