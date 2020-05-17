===============================
skidl
===============================

.. image:: https://img.shields.io/pypi/v/skidl.svg
        :target: https://pypi.python.org/pypi/skidl
.. image:: https://travis-ci.com/xesscorp/skidl.svg?branch=master
    :target: https://travis-ci.com/xesscorp/skidl


SKiDL is a module that allows you to compactly describe the interconnection of 
electronic circuits and components using Python.
The resulting Python program performs electrical rules checking
for common mistakes and outputs a netlist that serves as input to
a PCB layout tool.

* Free software: MIT license
* Documentation: http://xesscorp.github.io/skidl
* User Forum: http://skidl.discourse.group

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

As a very simple example (and you can see more examples in the 
`SKiDL blog <https://xesscorp.github.io/skidl/docs/_site/blog/>`_),
the SKiDL program below describes a circuit that
takes an input voltage, divides it by three, and outputs it:

.. code-block:: python

    from skidl import *

    # Create input & output voltages and ground reference.
    vin, vout, gnd = Net('VI'), Net('VO'), Net('GND')

    # Create two resistors.
    r1, r2 = 2 * Part("Device", 'R', TEMPLATE, footprint='Resistor_SMD.pretty:R_0805_2012Metric')
    r1.value = '1K'   # Set upper resistor value.
    r2.value = '500'  # Set lower resistor value.

    # Connect the nets and resistors.
    vin += r1[1]      # Connect the input to the upper resistor.
    gnd += r2[2]      # Connect the lower resistor to ground.
    vout += r1[2], r2[1] # Output comes from the connection of the two resistors.

    generate_netlist()

And this is the output that can be fed to a program like KiCad's ``PCBNEW`` to
create the physical PCB::

    (export (version D)                                                                                    
      (design                                                                                              
        (source "C:\xesscorp\KiCad\tools\skidl\tests\vdiv.py")                                             
        (date "09/14/2018 08:49 PM")                                                                       
        (tool "SKiDL (0.0.23)"))                                                                           
      (components                                                                                          
        (comp (ref R1)                                                                                     
          (value 1K)                                                                                       
          (footprint Resistor_SMD.pretty:R_0805_2012Metric)                                                                 
          (fields                                                                                          
            (field (name description) Resistor)                                                            
            (field (name keywords) "r res resistor"))                                                      
          (libsource (lib device) (part R))                                                                
          (sheetpath (names /top/12995167876889795071) (tstamps /top/12995167876889795071)))               
        (comp (ref R2)                                                                                     
          (value 500)                                                                                      
          (footprint Resistor_SMD.pretty:R_0805_2012Metric)                                                                 
          (fields                                                                                          
            (field (name description) Resistor)                                                            
            (field (name keywords) "r res resistor"))                                                      
          (libsource (lib device) (part R))                                                                
          (sheetpath (names /top/8869138953290924483) (tstamps /top/8869138953290924483))))                
      (nets                                                                                                
        (net (code 0) (name GND)                                                                           
          (node (ref R2) (pin 2)))                                                                         
        (net (code 1) (name VI)                                                                            
          (node (ref R1) (pin 1)))                                                                         
        (net (code 2) (name VO)                                                                            
          (node (ref R1) (pin 2))                                                                          
          (node (ref R2) (pin 1))))                                                                        
    )                                                                                                      
