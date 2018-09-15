---
layout: home
title: SKiDL
description: Use Python to create circuits.
headline: SKiDL
tags: [Python, SKiDL, home]
---

# TL;DR

**Never use a lousy schematic editor again!**
SKiDL is a simple module that lets you describe electronic circuits using Python.
The resulting Python program outputs a netlist that a PCB layout tool uses to
create a finished circuit board.

### Contents

* [Introduction](#introduction)
* [Installation](#installation)
* [Basic Usage](#basic-usage)
* [Going Deeper](#going-deeper)
* [Going Really Deep](#going-really-deep)
* [Converting Existing Designs to SKiDL](#converting-existing-designs-to-skidl)
* [SPICE Simulations](#spice-simulations)



# Introduction

SKiDL is a module that allows you to compactly describe the interconnection of 
electronic circuits and components using Python.
The resulting Python program performs electrical rules checking
for common mistakes and outputs a netlist that serves as input to
a PCB layout tool.

## Features

* Has a powerful, flexible syntax (because it *is* Python).
* Permits compact descriptions of electronic circuits (think about *not* tracing
  signals through a multi-page schematic).
* Allows textual descriptions of electronic circuits (think about using 
  `diff` and [git](https://en.wikipedia.org/wiki/Git) for circuits).
* Performs electrical rules checking (ERC) for common mistakes (e.g., unconnected device I/O pins).
* Supports linear / hierarchical / mixed descriptions of electronic designs.
* Fosters design reuse (think about using [PyPi](pypi.org) and [Github](github.com)
  to distribute electronic designs).
* Makes possible the creation of *smart circuit modules* whose behavior / structure are changed parametrically
  (think about filters whose component values are automatically adjusted based on your
  desired cutoff frequency).
* Can work with any ECAD tool (only two methods are needed: one for reading the part libraries and another
  for outputing the correct netlist format).
* Takes advantage of all the benefits of the Python ecosystem (because it *is* Python).
* Free software: MIT license.
* Open source: [https://github.com/xesscorp/skidl](https://github.com/xesscorp/skidl)

As a very simple example, the SKiDL program below describes a circuit that
takes an input voltage, divides it by three, and outputs it:

```py
from skidl import *

# Create input & output voltages and ground reference.
vin, vout, gnd = Net('VI'), Net('VO'), Net('GND')

# Create two resistors.
r1, r2 = 2 * Part('device', 'R', TEMPLATE, footprint='Resistors_SMD:R_0805')
r1.value = '1K'   # Set upper resistor value.
r2.value = '500'  # Set lower resistor value.

# Connect the nets and resistors.
vin += r1[1]      # Connect the input to the upper resistor.
gnd += r2[2]      # Connect the lower resistor to ground.
vout += r1[2], r2[1] # Output comes from the connection of the two resistors.

generate_netlist()
```

And this is the netlist output that can be fed to a program like KiCad's `PCBNEW` to
create the physical PCB:

```text
(export (version D)                                                                                    
  (design                                                                                              
    (source "C:\xesscorp\KiCad\tools\skidl\tests\vdiv.py")                                             
    (date "09/14/2018 08:49 PM")                                                                       
    (tool "SKiDL (0.0.23)"))                                                                           
  (components                                                                                          
    (comp (ref R1)                                                                                     
      (value 1K)                                                                                       
      (footprint Resistors_SMD:R_0805)                                                                 
      (fields                                                                                          
        (field (name description) Resistor)                                                            
        (field (name keywords) "r res resistor"))                                                      
      (libsource (lib device) (part R))                                                                
      (sheetpath (names /top/12995167876889795071) (tstamps /top/12995167876889795071)))               
    (comp (ref R2)                                                                                     
      (value 500)                                                                                      
      (footprint Resistors_SMD:R_0805)                                                                 
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
```



# Installation

SKiDL is pure Python so it's easy to install:

```bash
$ pip install skidl
```

or:

```bash
$ easy_install skidl
```

In order for SKiDL to access part libraries,
you'll also need to install [KiCad](http://kicad-pcb.org/).



# Basic Usage

This is the minimum that you need to know to design electronic circuitry
using SKiDL:

* How to get access to SKiDL.
* How to find and instantiate a component (or *part*).
* How to connect *pins* of the parts to each other using *nets*.
* How to run an ERC on the circuit.
* How to generate a *netlist* for the circuit that serves as input to a PCB layout tool.

I'll demonstrate these steps using SKiDL in an interactive Python session,
but normally the statements that are shown would be entered into a file and
executed as a Python script.


## Accessing SKiDL

To use skidl in a project, just place the following at the top of your file:

```py
import skidl
```

But for this tutorial, I'll just import everything:

```py
from skidl import *
```


## Finding Parts

SKiDL provides a convenience function for searching for parts called
(naturally) `search`.
For example, if you needed an operational amplifier, then the following command would
pull up some likely candidates:

```terminal
>>> search('opamp')
linear.lib: LT1492
linear.lib: MCP601SN (2.7V to 6.0V Single Supply CMOS Operational Amplifier, SO-8)
linear.lib: LM321 (Low Power Single Operational Amplifier)
linear.lib: MCP601R (2.7V to 6.0V Single Supply CMOS Operational Amplifier, SOT-23-5)
linear.lib: LM555N (Dual Op amp, rail-to-rail, 8MHz, MSOP8, SOIC8)
...
linear.lib: MCP603ST (2.7V to 6.0V Single Supply CMOS Operational Amplifier, with Chip Select, TSSOP-8)
linear.lib: NE5534 (Low-Noise High-Speed Audio Operational Amplifier)
linear.lib: LT1493
linear.lib: MCP601P (2.7V to 6.0V Single Supply CMOS Operational Amplifier, DIP-8)
linear.lib: MCP601ST (2.7V to 6.0V Single Supply CMOS Operational Amplifier, TSSOP-8)
```

`search` accepts a regular expression and scans for it *anywhere* within the
name, description and keywords of all the parts in the library path.
(You can read more about how SKiDL handles libraries [here](#libraries).)
So the following search pulls up several candidates:

```terminal
>>> search('lm35')
dc-dc.lib: LM3578 (Switching Regulator (adjustable))
linear.lib: LM358 (Dual Rail-to-rail CMOS Operational Amplifier)
regul.lib: LM350T (3A 33V Adjustable Linear Regulator, TO-220)
sensors.lib: LM35-LP (Precision centigrade temperature sensor, TO-92 package)
sensors.lib: LM35-D (Precision centigrade temperature sensor, SOIC-8 package)
sensors.lib: LM35-NEB (Precision centigrade temperature sensor, TO-220 package)
```

If you want to restrict the search to a specific part, then
use a regular expression like the following:

```terminal
>>> search('^lm358$')
linear.lib: LM358 (Dual Rail-to-rail CMOS Operational Amplifier)
```

Once you have the part name and library, you can see the part's pin numbers, names
and their functions using the `show` function:

```terminal
>>> show('linear', 'lm358')

LM358: Dual Rail-to-rail CMOS Operational Amplifier
    Pin None/4/V-/POWER-IN
    Pin None/8/V+/POWER-IN
    Pin None/1/~/OUTPUT
    Pin None/2/-/INPUT
    Pin None/3/+/INPUT
    Pin None/5/+/INPUT
    Pin None/6/-/INPUT
    Pin None/7/~/OUTPUT
```

`show` looks for exact matches of the part name in a library, so the following
command raises an error:

```terminal
>>> show('linear', 'lm35')
ERROR: Unable to find part lm35 in library linear.
```


## Instantiating Parts

The part library and name are used to instantiate a part as follows:

```terminal
>>> resistor = Part('device','R')
```

You can customize the resistor by setting its attributes:

```terminal
>>> resistor.value = '1K' 
>>> resistor.value        
'1K'                      
```

You can also combine the setting of attributes with the creation of the part:

```terminal
>>> resistor = Part('device', 'R', value='1K')
>>> resistor.value
'1K'
```

You can use any valid Python name for a part attribute, but `ref`, `value`,
and `footprint` are necessary in order to generate the final netlist
for your circuit. And the attribute can hold any type of Python object,
but simple strings are probably the most useful.

The `ref` attribute holds the *reference* for the part. It's set automatically
when you create the part:

```terminal
>>> resistor.ref
'R1'
```

Since this was the first resistor we created, it has the honor of being named `R1`.
But you can easily change it:

```terminal
>>> resistor.ref = 'R5'
>>> resistor.ref
'R5'
```

Now what happens if we create another resistor?:

```terminal
>>> another_res = Part('device','R')   
>>> another_res.ref                        
'R1'
```

Since the `R1` reference was now available, the new resistor got it.
What if we tried renaming the first resistor back to `R1`:

```terminal
>>> resistor.ref = 'R1'
>>> resistor.ref
'R1_1'
```

Since the `R1` reference was already taken, SKiDL tried to give us
something close to what we wanted.
SKiDL won't let different parts have the same reference because
that would confuse the hell out of everybody.
                            

## Connecting Pins

Parts are great and all, but not very useful if they aren't connected to anything.
The connections between parts are called *nets* (think of them as wires)
and every net has one or more part *pins* on it.
SKiDL makes it easy to create nets and connect pins to them. 
To demonstrate, let's build the voltage divider circuit
shown in the introduction.

First, start by creating two resistors (note that I've also added the
`footprint` attribute that describes the physical package for the resistors):

```py
>>> rup = Part('device', 'R', value='1K', footprint='Resistors_SMD:R_0805')                            
>>> rlow = Part('device', 'R', value='500', footprint='Resistors_SMD:R_0805')                          
>>> rup.ref, rlow.ref                                                
('R1', 'R2')                                                         
>>> rup.value, rlow.value                                            
('1K', '500')     
```                                                   

To bring the voltage that will be divided into the circuit, let's create a net:

```terminal
>>> v_in = Net('VIN')
>>> v_in.name
'VIN'
```

Now attach the net to one of the pins of the `rup` resistor
(resistors are bidirectional which means it doesn't matter which pin, so pick pin 1):

```terminal
>>> rup[1] += v_in
```

You can verify that the net is attached to pin 1 of the resistor like this:

```terminal
>>> rup[1].net
VIN: Pin R1/1/~/PASSIVE
```

Next, create a ground reference net and attach it to `rlow`:

```terminal
>>> gnd = Net('GND')
>>> rlow[1] += gnd
>>> rlow[1].net
GND: Pin R2/1/~/PASSIVE
```

Finally, the divided voltage has to come out of the circuit on a net.
This can be done in several ways.
The first way is to define the output net and then attach the unconnected
pins of both resistors to it:

```terminal
>>> v_out = Net('VO')
>>> v_out += rup[2], rlow[2]
>>> rup[2].net, rlow[2].net
(VO: Pin R1/2/~/PASSIVE, Pin R2/2/~/PASSIVE, VO: Pin R1/2/~/PASSIVE, Pin R2/2/~/PASSIVE)
```

An alternate method is to connect the resistors and then attach their
junction to the output net:

```terminal
>>> rup[2] += rlow[2]
>>> v_out = Net('VO')
>>> v_out += rlow[2]
>>> rup[2].net, rlow[2].net
(VO: Pin R1/2/~/PASSIVE, Pin R2/2/~/PASSIVE, VO: Pin R1/2/~/PASSIVE, Pin R2/2/~/PASSIVE)
```

Either way works! Sometimes pin-to-pin connections are easier when you're
just wiring two devices together, while the pin-to-net connection method
excels when three or more pins have a common connection.


## Checking for Errors

Once the parts are wired together, you can do simple electrical rules checking
like this:

```terminal
>>> ERC()                           
                                    
2 warnings found during ERC.        
0 errors found during ERC.          
```

Since this is an interactive session, the ERC warnings and errors are stored 
in the file `skidl.erc`. (Normally, your SKiDL circuit description is stored
as a Python script such as `my_circuit.py` and the `ERC()` function will
dump its messages to `my_circuit.erc`.)
The ERC messages are:

```terminal
WARNING: Only one pin (PASSIVE pin 1/~ of R/R1) attached to net VIN.
WARNING: Only one pin (PASSIVE pin 1/~ of R/R2) attached to net GND.
```

These messages are generated because the `VIN` and `GND` nets each have only
a single pin on them and this usually indicates a problem.
But it's OK for this simple example, so the ERC can be turned off for
these two nets to prevent the spurious messages:

```terminal
>>> v_in.do_erc = False
>>> gnd.do_erc = False
>>> ERC()

No ERC errors or warnings found.
```


## Generating a Netlist

The end goal of using SKiDL is to generate a netlist that can be used
with a layout tool to generate a PCB. The netlist is output as follows:

```terminal
>>> generate_netlist()
```

Like the ERC output, the netlist shown below is stored in the file `skidl.net`.
But if your SKiDL circuit description is in the `my_circuit.py` file, 
then the netlist will be stored in `my_circuit.net`.

```text
(export (version D)
  (design
    (source "C:\xesscorp\KiCad\tools\skidl\skidl\skidl.py")
    (date "08/12/2016 10:05 PM")
    (tool "SKiDL (0.0.1)"))
  (components
    (comp (ref R1)
      (value 1K)
      (footprint Resistors_SMD:R_0805))
    (comp (ref R2)
      (value 500)
      (footprint Resistors_SMD:R_0805)))
  (nets
    (net (code 0) (name "VIN")
      (node (ref R1) (pin 1)))
    (net (code 1) (name "GND")
      (node (ref R2) (pin 1)))
    (net (code 2) (name "VO")
      (node (ref R1) (pin 2))
      (node (ref R2) (pin 2))))
)
(export (version D)
  (design
    (source "C:\TEMP\skidl tests\intro_example.py")
    (date "04/19/2017 04:09 PM")
    (tool "SKiDL (0.0.12)"))
  (components
    (comp (ref R1)
      (value 1K)
      (footprint Resistors_SMD:R_0805)
      (fields
        (field (name keywords) "r res resistor")
        (field (name description) Resistor))
      (libsource (lib device) (part R)))
    (comp (ref R2)
      (value 500)
      (footprint Resistors_SMD:R_0805)
      (fields
        (field (name keywords) "r res resistor")
        (field (name description) Resistor))
      (libsource (lib device) (part R))))
  (nets
    (net (code 0) (name GND)
      (node (ref R2) (pin 2)))
    (net (code 1) (name VI)
      (node (ref R1) (pin 1)))
    (net (code 2) (name VO)
      (node (ref R1) (pin 2))
      (node (ref R2) (pin 1))))
)

```

You can also generate the netlist in XML format:

```terminal
>>> generate_xml()
```

This is useful in a KiCad environment where the XML file is used as the
input to BOM-generation tools.



# Going Deeper

The previous section showed the bare minimum you need to know to design
circuits with SKiDL, but doing a complicated circuit that way would suck donkeys.
This section will talk about some more advanced features.

## Basic SKiDL Objects: Parts, Pins, Nets, Buses

SKiDL uses four types of objects to represent a circuit: `Part`, `Pin`,
`Net`, and `Bus`.

The `Part` object represents an electronic component, which SKiDL thinks of as simple
bags of `Pin` objects with a few other attributes attached 
(like the part number, name, reference, value, footprint, etc.).

The `Pin` object represents a terminal that brings an electronic signal into
and out of the part. Each `Pin` object has two important attributes:

* `part` which stores the reference to the `Part` object to which the pin belongs.
* `net` which stores the the reference to the `Net` object that the pin is
  connected to, or `None` if the pin is unconnected.

A `Net` object is kind of like a `Part`: it's a simple bag of pins.
The difference is, unlike a part, pins can be added to a net.
This happens when a pin on some part is connected to the net or when the 
net is merged with another net.

Finally, a `Bus` is just a list of `Net` objects.
A bus of a certain width can be created from a number of existing nets,
newly-created nets, or both.


## Creating SKiDL Objects

Here's the most common way to create a part in your circuit:

```py
my_part = Part('some_library', 'some_part_name')
```

When this is processed, the current directory will be checked for a file
called `some_library.lib` which will be opened and scanned for a part with the
name `some_part_name`. If the file is not found or it doesn't contain
the requested part, then the process will be repeated using KiCad's default
library directory.
(You can change SKiDL's library search by changing the list of directories
stored in the `skidl.lib_search_paths_kicad` list.)

You're not restricted to using only the current directory or the KiCad default
directory to search for parts. You can also search any file for a part by 
using a full file name:

```py
my_part = Part('C:/my_libs/my_great_parts.lib', 'my_super_regulator')
```

You're also not restricted to getting an exact match on the part name: you can
use a *regular expression* instead. For example, this will find a part
with "358" anywhere in a part name or alias:

```py
my_part = Part('some_library', '.*358.*')
```

If the regular expression matches more than one part, then you'll only get the
first match and a warning that multiple parts were found.

Once you have a part, you can set its attributes like you could for any Python
object. As was shown previously, the `ref` attribute will already be set
but you can override it:

```py
my_part.ref = 'U5'
```

The `value` and `footprint` attributes are also required for generating
a netlist. But you can also add any other attribute:

```py
my_part.manf = 'Atmel'
my_part.setattr('manf#', 'ATTINY4-TSHR'
```

It's also possible to set the attributes during the part creation:

```py
my_part = Part('some_lib', 'some_part', ref='U5', footprint='SMD:SOT23_6', manf='Atmel')
```

Creating nets is also simple:

```py
my_net = Net()              # An unnamed net.
my_other_net = Net('Fred')  # A named net.
```

As with parts, SKiDL will alter the name you assign to a net if it collides with another net
having the same name.

You can create a bus of a certain width like this:

```py
my_bus = Bus('bus_name', 8)  # Create a byte-wide bus.
```

(All buses must be named, but SKiDL will look for and correct colliding
bus names.)

You can also create a bus from existing nets, or buses, or the pins of parts:

```py
my_part = Part('linear', 'LM358')
a_net = Net()
b_net = Net()
bus_nets = Bus('net_bus', a_net, b_net)            # A 2-bit bus.
bus_pins = Bus('pin_bus', my_part[1], my_part[3])  # A 2-bit bus.
bus_buses = Bus('bus_bus', my_bus)                 # An 8-bit bus.
```

Finally, you can mix-and-match any combination of widths, nets, buses or part pins:

```py
bus_mixed = Bus('mongrel', 8, a_net, my_bus, my_part[2])  # 8+1+8+1 = 18-bit bus.
```

Finally, you can modify an existing bus by inserting or extending it with any combination
of widths, nets, buses or pins:

```py
bus = Bus('A', 8)   # Eight-bit bus.
bus.insert(4, Bus('I', 3))  # Insert 3-bit bus before bus line bus[4].
bus.extend(5, Pin(), Net()) # Extend bus with another 5-bit bus, a pin, and a net.
```

The final object you can create is a `Pin`. You'll probably never do this
(except in interactive sessions), and it's probably a mistake if
you ever do do it, but here's how to do it:

```terminal
>>> p = Pin(num=1, name='my_pin', func=Pin.TRISTATE)
>>> p
Pin ???/1/my_pin/TRISTATE
```


## Finding SKiDL Objects

Sometimes you may want to access a bus or net that's already been created.
In such an instance, you can use the `get()` class method:

```py
n = Net.get('Fred')  # Find the existing Net object named 'Fred'.
b = Bus.get('A')     # Find the existing Bus object named 'A'.
```

If a net or bus is found with the exact name that was given, then that SKiDL
object is returned (no wild-card searches using regular expressions are allowed).
If the search is unsuccessful, `None` is returned.

There may be other times when you want to access a particular bus or net and,
if it doesn't exist, then create it.
The `fetch()` class method is used for this:

```py
n = Net.fetch('Fred')  # Find the existing Net object named 'Fred' or create it if not found.
b = Bus.fetch('A',8)   # Find the existing Bus object named 'A' or create it if not found.
```

Note that with the `Bus.fetch()` method, you also have to provide the arguments to
build the bus (such as its width) in case it doesn't exist.


## Copying SKiDL Objects

Instead of creating a SKiDL object from scratch, sometimes it's easier to just
copy an existing object. Here are some examples of creating a resistor and then making
some copies of it:

```terminal
>>> r1 = Part('device', 'R', value=500)
>>> r2 = r1.copy()                         # Make a single copy of the resistor.
>>> r3 = r1.copy(value='1K')               # Make a single copy, but give it a different value.
>>> r4 = r1(value='1K')                    # You can also call the object directly to make copies.
>>> r5, r6, r7 = r1(3)                     # Make 3 copies of the resistor.
>>> r8, r9, r10 = r1(value=[110,220,330])  # Make 3 copies, each with a different value.
>>> r11, r12 = 2 * r1                      # Make copies using the '*' operator.
```

In some cases it's clearer to create parts by copying a *template part* that
doesn't actually get included in the netlist for the circuitry.
This is done like so:

```terminal
>>> r_template = Part('device', 'R', dest=TEMPLATE)  # Create a resistor just for copying.
>>> r1 = r_template(value='1K')  # Make copy that becomes part of the actual circuitry.
```


## Accessing Part Pins and Bus Lines

You can access the pins on a part or the individual nets of a bus
using numbers, slices, strings, and regular expressions, either singly or in any combination.

Suppose you have a PIC10 processor in a six-pin package:

```terminal
>>> pic10 = Part('microchip_pic10mcu', 'pic10f220-i/ot')
>>> pic10

PIC10F220-I/OT: PIC10F222, 512W Flash, 24B SRAM, SOT-23-6
    Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL
    Pin U1/2/VSS/POWER-IN
    Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL
    Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL
    Pin U1/5/VDD/POWER-IN
    Pin U1/6/Vpp/~MCLR~/GP3/INPUT
```

The most natural way to access one of its pins is to give the pin number
in brackets:

```terminal
>>> pic10[3]
Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL
```

(If you have a part in a BGA package with pins numbers like `C11`, then
you'll have to enter the pin number as a quoted string like '`C11`'.)

You can also get several pins at once in a list:

```terminal
>>> pic10[3,1,6]
[Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL, Pin U1/6/Vpp/~MCLR~/GP3/INPUT]
```

You can even use Python slice notation:

```terminal
>>> pic10[2:4]  # Get pins 2 through 4.
[Pin U1/2/VSS/POWER-IN, Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL]
>>> pic10[4:2]  # Get pins 4 through 2.
[Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL, Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/2/VSS/POWER-IN]
>>> pic10[:]    # Get all the pins.
[Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL, Pin U1/2/VSS/POWER-IN, Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL, Pin U1/5/VDD/POWER-IN, Pin U1/6/Vpp/~MCLR~/GP3/INPUT]
```

(It's important to note that the slice notation used by SKiDL for parts is slightly
different than standard Python. In Python, a slice `n:m` would fetch indices
`n`, `n+1`, `...`, `m-1`. With SKiDL, it actually fetches all the
way up to the last number: `n`, `n+1`, `...`, `m-1`, `m`.
The reason for doing this is that most electronics designers are used to
the bounds on a slice including both endpoints. Perhaps it is a mistake to
do it this way. We'll see...)

In addition to the bracket notation, you can also get a single pin using an attribute name
that begins with a '`p`' followed by the pin number:

```terminal
>>> pic10.p2
Pin U1/2/VSS/POWER-IN
```

Instead of pin numbers, sometimes it makes the design intent more clear to 
access pins by their names.
For example, it's more obvious that a voltage supply net is being
attached to the power pin of the processor when it's expressed like this:

```py
pic10['VDD'] += supply_5V
```

Like pin numbers, pin names can also be used as attributes to access the pin:

```terminal
>>> pic10.VDD
Pin U1/5/VDD/POWER-IN
```

You can use multiple names or regular expressions to get more than one pin:

```terminal
>>> pic10['VDD','VSS']
[Pin U1/5/VDD/POWER-IN, Pin U1/2/VSS/POWER-IN]
>>> pic10['.*gp[1-3]']
[Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL, Pin U1/6/Vpp/~MCLR~/GP3/INPUT]
```

It can be tedious and error prone entering all the quote marks if you're accessing
many pin names. SKiDL lets you enter a single, comma-delimited string of
pin names:

```terminal
>>> pic10['.*GP0, .*GP1, .*GP2']
[Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL, Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL]
```

Some parts have sequentially-numbered sets of pins like the address and data buses of a RAM.
SKiDL lets you access these pins using a slice-like notation in a string like so:

```terminal
>>> ram = Part('memory', 'sram_512ko')
>>> ram['D[0:7]']
[Pin U1/13/D0/TRISTATE, Pin U1/14/D1/TRISTATE, Pin U1/15/D2/TRISTATE, Pin U1/17/D3/TRISTATE, Pin U1/18/D4/TRISTATE, Pin U1/19/D5/TRISTATE, Pin U1/20/D6/TRISTATE, Pin U1/21/D7/TRISTATE]
```

Or you can access the pins in the reverse order:

```terminal
>>> ram = Part('memory', 'sram_512ko')
>>> ram['D[7:0]']
[Pin U2/21/D7/TRISTATE, Pin U2/20/D6/TRISTATE, Pin U2/19/D5/TRISTATE, Pin U2/18/D4/TRISTATE, Pin U2/17/D3/TRISTATE, Pin U2/15/D2/TRISTATE, Pin U2/14/D1/TRISTATE, Pin U2/13/D0/TRISTATE]
```

`Part` objects also provide the `get_pins()` function which can select pins in even more ways.
For example, this would get every bidirectional pin of the processor:

```terminal
>>> pic10.get_pins(func=Pin.BIDIR)
[Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL, Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL]
```

Accessing the individual nets of a bus works similarly to accessing part pins:

```terminal
>>> a = Net('NET_A')  # Create a named net.
>>> b = Bus('BUS_B', 8, a)  # Create a nine-bit bus.
>>> b
BUS_B:
        BUS_B0:  # Note how the individual nets of the bus are named.
        BUS_B1:
        BUS_B2:
        BUS_B3:
        BUS_B4:
        BUS_B5:
        BUS_B6:
        BUS_B7:
        NET_A:   # The last net retains its original name.
>>> b[0]  # Get the first net of the bus.
BUS_B0:
>>> b[4,8]  # Get the fifth and ninth bus lines.
[BUS_B4: , NET_A: ]
>>> b[3:0]  # Get the first four bus lines in reverse order.
[BUS_B3: , BUS_B2: , BUS_B1: , BUS_B0: ]
>>> b['BUS_B.*']  # Get all the bus lines except the last one.
[BUS_B0: , BUS_B1: , BUS_B2: , BUS_B3: , BUS_B4: , BUS_B5: , BUS_B6: , BUS_B7: ]
>>> b['NET_A']  # Get the last bus line.
NET_A:
```


## Making Connections

Pins, nets, parts and buses can all be connected together in various ways, but
the primary rule of SKiDL connections is:

> > **The `+=` operator is the only way to make connections!**

At times you'll mistakenly try to make connections using the 
assignment operator (`=`). In many cases, SKiDL warns you if you do that,
but there are situations where it can't (because
Python is a general-purpose programming language where
assignment is a necessary operation).
So remember the primary rule!

After the primary rule, the next thing to remember is that SKiDL's main
purpose is creating netlists. To that end, it handles four basic, connection operations:

**Pin-to-Net**:
    A pin is connected to a net, adding it to the list of pins
    connected to that net. If the pin is already attached to other nets,
    then those nets are connected to this net as well.

**Net-to-Pin**: 
    This is the same as doing a pin-to-net connection.

**Pin-to-Pin**:
    A net is created and both pins are attached to it. If one or
    both pins are already connected to other nets, then those nets are connected
    to the newly-created net as well.

**Net-to-Net**:
    Connecting one net to another *merges* the pins on both nets
    onto a single, larger net.

For each type of connection operation, there are three variants based on
the number of things being connected:

**One-to-One**:
    This is the most frequent type of connection, for example, connecting one
    pin to another or connecting a pin to a net.

**One-to-Many**:
    This mainly occurs when multiple pins are connected to the same net, like
    when multiple ground pins of a chip are connected to the circuit ground net.

**Many-to-Many**:
    This usually involves bus connections to a part, such as connecting
    a bus to the data or address pins of a processor. For this variant, there must be the
    same number of things to connect in each set, e.g. you can't connect
    three pins to four nets.

As a first example, let's connect a net to a pin on a part:

```terminal
>>> pic10 = Part('microchip_pic10mcu','pic10f220-i/ot')  # Get a part.
>>> io = Net('IO_NET')    # Create a net.
>>> pic10['.*GP0'] += io  # Connect the net to a part pin.
>>> io                    # Show the pins connected to the net.
IO_NET: Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL
```

You can do the same operation in reverse by connecting the part pin to the net
with the same result:

```terminal
>>> pic10 = Part('microchip_pic10mcu','pic10f220-i/ot')
>>> io = Net('IO_NET')
>>> io += pic10['.*GP0']  # Connect a part pin to the net.
>>> io
IO_NET: Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL
```

You can also connect a pin directly to another pin.
In this case, an *implicit net* will be created between the pins that you can
access using the `net` attribute of either part pin:

```terminal
>>> pic10['.*GP1'] += pic10['.*GP2']  # Connect two pins together.
>>> pic10['.*GP1'].net     # Show the net connected to the pin.
N$1: Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL
>>> pic10['.*GP2'].net     # Show the net connected to the other pin. Same thing!
N$1: Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL
```

You can connect multiple pins together, all at once:

```terminal
>>> pic10[1] += pic10[2,3,6]
>>> pic10[1].net
N$1: Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL, Pin U1/2/VSS/POWER-IN, Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/6/Vpp/~MCLR~/GP3/INPUT
```

Or you can do it incrementally:

```terminal
>>> pic10[1] += pic10[2]
>>> pic10[1] += pic10[3]
>>> pic10[1] += pic10[6]
>>> pic10[1].net
N$1: Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL, Pin U1/2/VSS/POWER-IN, Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/6/Vpp/~MCLR~/GP3/INPUT
```

If you connect pins on separate nets together, then all the pins are merged onto the same net:

```terminal
>>> pic10[1] += pic10[2]  # Put pins 1 & 2 on one net.
>>> pic10[1].net
N$1: Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL, Pin U1/2/VSS/POWER-IN
>>> pic10[3] += pic10[4]  # Put pins 3 & 4 on another net.
>>> pic10[3].net
N$2: Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL
>>> pic10[1] += pic10[4]  # Connect two pins from different nets.
>>> pic10[3].net          # Now all the pins are on the same net!
N$2: Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL, Pin U1/2/VSS/POWER-IN, Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL, Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL
```

Here's an example of connecting a three-bit bus to three pins on a part:

```terminal
>>> pic10 = Part('microchip_pic10mcu','pic10f220-i/ot')
>>> pic10

PIC10F220-I/OT: PIC10F222, 512W Flash, 24B SRAM, SOT-23-6
    Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL
    Pin U1/2/VSS/POWER-IN
    Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL
    Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL
    Pin U1/5/VDD/POWER-IN
    Pin U1/6/Vpp/~MCLR~/GP3/INPUT
>>> b = Bus('GP', 3)        # Create a 3-bit bus.
>>> pic10[4,3,1] += b[2:0]  # Connect bus to part pins, one-to-one.
>>> b
GP:
        GP0: Pin U1/1/ICSPDAT/AN0/GP0/BIDIRECTIONAL
        GP1: Pin U1/3/ICSPCLK/AN1/GP1/BIDIRECTIONAL
        GP2: Pin U1/4/T0CKI/FOSC4/GP2/BIDIRECTIONAL
```

But SKiDL will warn you if there aren't the same number of things to
connect on each side:

```terminal
>>> pic10[4,3,1] += b[1:0]  # Too few bus lines for the pins!
ERROR: Connection mismatch 3 != 2!
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "c:\xesscorp\kicad\tools\skidl\skidl\skidl.py", line 3330, in __iadd__
    raise Exception
Exception
```


## Making Parallel and Serial Networks

The previous section showed some general-purpose techniques for connecting parts,
but SKiDL also has some specialized syntax for wiring two-pin components
in parallel or serial.
For example, here is a network of four resistors connected in series
between power and ground:

```terminal
vcc, gnd = Net('VCC'), Net('GND')
r1, r2, r3, r4 = Part('device', 'R', dest=TEMPLATE) * 4
ser_ntwk = vcc & r1 & r2 & r3 & r4 & gnd
```

It's also possible to connect the resistors in parallel between power and ground:

```terminal
par_ntwk = vcc & (r1 | r2 | r3 | r4) & gnd
```

Or you can do something like placing pairs of resistors in series and then paralleling
those combinations like this:

```terminal
combo_ntwk = vcc & ((r1 & r2) | (r3 & r4)) & gnd
```

The examples above work with *non-polarized* components, but what about parts
like diodes? In that case, you have to specify the pins *explicitly* with the
first pin connected to the preceding part and the second pin to the following part:

```terminal
d1 = Part('device', 'D')
polar_ntwk = vcc & r1 & d1['A,K'] & gnd  # Diode anode connected to resistor and cathode to ground.
```

Explicitly listing the pins also lets you use multi-pin parts with networks.
For example, here's an NPN-transistor amplifier:

```terminal
q1 = Part('device', 'Q_NPN_ECB')
ntwk_ce = vcc & r1 & q1['C,E'] & gnd  # VCC through load resistor to collector and emitter attached to ground.
ntwk_b = r2 & q1['B']  # Resistor attached to base.
```

That's all well and good, but how do you connect to internal points in these networks where
the interesting things are happening?
For instance, how do you apply an input to the transistor circuit and then connect
to the output?
One way is by inserting nets inside the networks:

```terminal
inp, outp = Net('INPUT'), Net('OUTPUT')
ntwk_ce = vcc & r1 & outp & q1['C,E'] & gnd  # Connect net outp to the junction of the resistor and transistor collector.
ntwk_b = inp & r2 & q1['B']  # Connect net inp to the resistor driving the transistor base.
```

After that's done, the `inp` and `outp` nets can be connected to other points in the circuit.


## Units Within Parts

Some components may contain smaller *units* that operate independently of the
component as a whole.
For example, an operational amplifier chip might contain two individual opamp units,
each capable of operating on their own set of inputs and outputs.

Some library parts may already have predefined units, but you can add them to
any part.
For example, a four-pin *resistor network* might contain two resistors:
one attached between pins 1 and 4, and the other bewtween pins 2 and 3.
Each resistor could be assigned to a unit as follows:

```terminal
>>> rn = Part('device', 'R_Pack02')
>>> rn.make_unit('A', 1, 4)  # Make a unit called 'A' for the first resistor.

 R_Pack02 (): 2 Resistor network, parallel topology, DIP package
    Pin RN1/4/R1.2/PASSIVE
    Pin RN1/1/R1.1/PASSIVE
>>> rn.make_unit('B', 2, 3)  # Now make a unit called 'B' for the second resistor.

 R_Pack02 (): 2 Resistor network, parallel topology, DIP package
    Pin RN1/2/R2.1/PASSIVE
    Pin RN1/3/R2.2/PASSIVE
>>> rn.unit['A'][1, 4] += Net(), Net()
```

Once the units are defined, you can use them just like any part:

```terminal
>>> rn.unit['A'][1,4] += Net(), Net()  # Connect resistor A to two nets.
>>> rn.unit['B'][2,3] += rn.unit['A'][1,4]  # Connect resistor B in parallel with resistor A.
```

Now this isn't all that useful because you still have to remember which pins
are assigned to each unit, and if you wanted to swap the resistors you would have
to change the unit names *and the pins numbers!*.
In order to get around this inconvenience, you could assign *aliases* to each
pin like this:

```terminal
>>> rn = Part('device', 'R_Pack02')
>>> rn.make_unit('A', 1, 4)

 R_Pack02 (): 2 Resistor network, parallel topology, DIP package
    Pin RN1/4/R1.2/PASSIVE
    Pin RN1/1/R1.1/PASSIVE
>>> rn.make_unit('B', 2, 3)

 R_Pack02 (): 2 Resistor network, parallel topology, DIP package
    Pin RN1/3/R2.2/PASSIVE
    Pin RN1/2/R2.1/PASSIVE
>>> rn.unit['A'].set_pin_alias('L',1) # Alias 'L' of pin 1 on left-side of package.
>>> rn.unit['A'].set_pin_alias('R',4) # Alias 'R' of pin 4 on right-side of package.
>>> rn.unit['B'].set_pin_alias('L',2) # Alias 'L' of pin 2 on left-side.
>>> rn.unit['B'].set_pin_alias('R',3) # Alias 'R' of pin 3 on right-side.
```

Now the same connections can be made using the pin aliases:

```terminal
>>> rn.unit['A']['L,R'] += Net(), Net()  # Connect resistor A to two nets.
>>> rn.unit['B']['L,R'] += rn.unit['A']['L,R']  # Connect resistor B in parallel with resistor A.
```

In this case, if you wanted to swap the A and B resistors, you only need to change
their unit labels.
The pin aliases don't need to be altered.

If you find the `unit[...]` notation cumbersome, units can also be accessed by
using their names as attributes:

```terminal
>>> rn.A['L,R'] += Net(), Net()  # Connect resistor A to two nets.
>>> rn.B['L,R'] += rn.A['L,R']   # Connect resistor B in parallel with resistor A.
```


## Hierarchy

SKiDL supports the encapsulation of parts, nets and buses into modules
that can be replicated to reduce the design effort, and can be used in
other modules to create a functional hierarchy.
It does this using Python's built-in machinery for defining and calling functions
so there's almost nothing new to learn.

As an example, here's the voltage divider as a module:

```py
from skidl import *
import sys

# Define the voltage divider module. The @subcircuit decorator 
# handles some skidl housekeeping that needs to be done.
@subcircuit
def vdiv(inp, outp):
    """Divide inp voltage by 3 and place it on outp net."""
    rup = Part('device', 'R', value='1K', footprint='Resistors_SMD:R_0805')
    rlo = Part('device','R', value='500', footprint='Resistors_SMD:R_0805')
    rup[1,2] += inp, outp
    rlo[1,2] += outp, gnd

gnd = Net('GND')         # GLobal ground net.
input_net = Net('IN')    # Net with the voltage to be divided.
output_net = Net('OUT')  # Net with the divided voltage.

# Instantiate the voltage divider and connect it to the input & output nets.
vdiv(input_net, output_net)

generate_netlist(sys.stdout)
```

For the most part, `vdiv` is just a standard Python function:
it accepts inputs, it performs operations on them, and it could return
outputs (but in this case, it doesn't need to).
Other than the `@subcircuit` decorator that appears before the function definition,
`vdiv` is just a Python function and it can do anything that a Python function can do.

Here's the netlist that's generated:

```text
(export (version D)
  (design
    (source "C:\TEMP\skidl tests\hier_example.py")
    (date "04/20/2017 09:39 AM")
    (tool "SKiDL (0.0.12)"))
  (components
    (comp (ref R1)
      (value 1K)
      (footprint Resistors_SMD:R_0805)
      (fields
        (field (name keywords) "r res resistor")
        (field (name description) Resistor))
      (libsource (lib device) (part R)))
    (comp (ref R2)
      (value 500)
      (footprint Resistors_SMD:R_0805)
      (fields
        (field (name keywords) "r res resistor")
        (field (name description) Resistor))
      (libsource (lib device) (part R))))
  (nets
    (net (code 0) (name GND)
      (node (ref R2) (pin 2)))
    (net (code 1) (name IN)
      (node (ref R1) (pin 1)))
    (net (code 2) (name OUT)
      (node (ref R1) (pin 2))
      (node (ref R2) (pin 1))))
)
```

For an example of a multi-level hierarchy, the `multi_vdiv` module shown below
can use the `vdiv` module to divide a voltage multiple times:

<a name="multilevel_hierarchy_example"></a>
```py
from skidl import *
import sys

# Define the voltage divider module.
@subcircuit
def vdiv(inp, outp):
    """Divide inp voltage by 3 and place it on outp net."""
    rup = Part('device', 'R', value='1K', footprint='Resistors_SMD:R_0805')
    rlo = Part('device','R', value='500', footprint='Resistors_SMD:R_0805')
    rup[1,2] += inp, outp
    rlo[1,2] += outp, gnd

@subcircuit
def multi_vdiv(repeat, inp, outp):
    """Divide inp voltage by 3 ** repeat and place it on outp net."""
    for _ in range(repeat):
        out_net = Net()     # Create an output net for the current stage.
        vdiv(inp, out_net)  # Instantiate a divider stage.
        inp = out_net       # The output net becomes the input net for the next stage.
    outp += out_net         # Connect the output from the last stage to the module output net.

gnd = Net('GND')         # GLobal ground net.
input_net = Net('IN')    # Net with the voltage to be divided.
output_net = Net('OUT')  # Net with the divided voltage.
multi_vdiv(3, input_net, output_net)  # Run the input through 3 voltage dividers.

generate_netlist(sys.stdout)
```

(For the EE's out there: *yes, I know cascading three simple voltage dividers
will not multiplicatively scale the input voltage because of the
input and output impedances of each stage!*
It's just the simplest example I could think of that shows the feature.)

And here's the resulting netlist:

```text
(export (version D)
  (design
    (source "C:\TEMP\skidl tests\multi_hier_example.py")
    (date "04/20/2017 09:43 AM")
    (tool "SKiDL (0.0.12)"))
  (components
    (comp (ref R1)
      (value 1K)
      (footprint Resistors_SMD:R_0805)
      (fields
        (field (name keywords) "r res resistor")
        (field (name description) Resistor))
      (libsource (lib device) (part R)))
    (comp (ref R2)
      (value 500)
      (footprint Resistors_SMD:R_0805)
      (fields
        (field (name keywords) "r res resistor")
        (field (name description) Resistor))
      (libsource (lib device) (part R)))
    (comp (ref R3)
      (value 1K)
      (footprint Resistors_SMD:R_0805)
      (fields
        (field (name keywords) "r res resistor")
        (field (name description) Resistor))
      (libsource (lib device) (part R)))
    (comp (ref R4)
      (value 500)
      (footprint Resistors_SMD:R_0805)
      (fields
        (field (name keywords) "r res resistor")
        (field (name description) Resistor))
      (libsource (lib device) (part R)))
    (comp (ref R5)
      (value 1K)
      (footprint Resistors_SMD:R_0805)
      (fields
        (field (name keywords) "r res resistor")
        (field (name description) Resistor))
      (libsource (lib device) (part R)))
    (comp (ref R6)
      (value 500)
      (footprint Resistors_SMD:R_0805)
      (fields
        (field (name keywords) "r res resistor")
        (field (name description) Resistor))
      (libsource (lib device) (part R))))
  (nets
    (net (code 0) (name GND)
      (node (ref R2) (pin 2))
      (node (ref R4) (pin 2))
      (node (ref R6) (pin 2)))
    (net (code 1) (name IN)
      (node (ref R1) (pin 1)))
    (net (code 2) (name N$1)
      (node (ref R1) (pin 2))
      (node (ref R2) (pin 1))
      (node (ref R3) (pin 1)))
    (net (code 3) (name N$2)
      (node (ref R3) (pin 2))
      (node (ref R4) (pin 1))
      (node (ref R5) (pin 1)))
    (net (code 4) (name OUT)
      (node (ref R5) (pin 2))
      (node (ref R6) (pin 1))))
)
```


## Libraries

As you've already seen, SKiDL gets its parts from *part libraries*.
By default, SKiDL finds the libraries provided by KiCad (using the `KISYSMOD`
environment variable), so if that's all you need then you're all set.

Currently, SKiDL supports the library formats for the following ECAD tools:

* `KICAD`: KiCad schematic part libraries.
* `SKIDL`: Schematic parts stored as SKiDL/Python modules.

You can set the default library format you want to use in your SKiDL script like so:

```py
set_default_tool(KICAD)  # KiCad is the default library format.
set_default_tool(SKIDL)  # Now SKiDL is the default library format.
```

You can select the directories where SKiDL looks for parts using the 
`lib_search_paths` dictionary:

```py
lib_search_paths[SKIDL] = ['.', '..', 'C:\\temp']
lib_search_paths[KICAD].append('C:\\my\\kicad\\libs')
```

You can convert a KiCad library into the SKiDL format by exporting it:

```py
kicad_lib = SchLib('device', tool=KICAD)       # Open a KiCad library.
kicad_lib.export('my_skidl_lib')               # Export it into a file in SKiDL format.
skidl_lib = SchLib('my_skidl_lib', tool=SKIDL) # Create a SKiDL library object from the new file.
if len(skidl_lib) == len(kicad_lib):
    print('As expected, both libraries have the same number of parts!')
else:
    print('Something went wrong!')
diode = Part(skidl_lib, 'D')                   # Instantiate a diode from the SKiDL library.
```

You can make ad-hoc libraries just by creating a SchLib object and adding
Part objects to it:

```py
my_lib = SchLib(name='my_lib')                      # Create an empty library object.
my_part = Part(name='R', tool=SKIDL, dest=TEMPLATE) # Create an empty part object template.
my_part.ref_prefix = 'R'                            # Set the part reference prefix.
my_part.description = 'resistor'                    # Set the part's description field.
my_part.keywords = 'res resistor'                   # Set the part's keywords.
my_part += Pin(num=1, func=Pin.PASSIVE)             # Add a pin to the part.
my_part += Pin(num=2, func=Pin.PASSIVE)             # Add another pin to the part.
my_lib += my_part                                   # Add the part to the library.

new_resistor = Part(my_lib, 'R')                    # Instantiate the part from the library.
my_lib.export('my_lib')                             # Save the library in a file my_lib.py.
```

Always create a part intended for a library as a template so you don't inadvertently
add it to the circuit netlist.
Then set the part attributes and create and add pins to the part.
Here are the most common attributes you'll want to set:

Attribute | Meaning
----------|------------------
name      | A string containing the name of the part, e.g. 'LM35' for a temperature sensor.
ref_prefix | A string containing the prefix for this part's references, e.g. 'U' for ICs.
description | A string describing the part, e.g. 'temperature sensor'.
keywords  | A string containing keywords about the part, e.g. 'sensor temperature IC'.

When creating a pin, these are the attributes you'll want to set:

Attribute | Meaning
----------|------------------
num       | A string or integer containing the pin number, e.g. 5 or 'A13'.
name      | A string containing the name of the pin, e.g. 'CS'.
func      | An identifier for the function of the pin.

The pin function identifiers are as follows:
 
Identifier | Pin Function
-----------|-----------------
Pin.INPUT | Input pin.
Pin.OUTPUT | Output pin.
Pin.BIDIR | Bidirectional in/out pin.
Pin.TRISTATE | Output pin that goes into a high-impedance state when disabled.
Pin.PASSIVE | Pin on a passive component (like a resistor).
Pin.UNSPEC | Pin with an unspecified function.
Pin.PWRIN | Power input pin (either voltage supply or ground).
Pin.PWROUT | Power output pin (like the output of a voltage regulator).
Pin.OPENCOLL | Open-collector pin (pulls to ground but not to positive rail).
Pin.OPENEMIT | Open-emitter pin (pulls to positive rail but not to ground).
Pin.NOCONNECT | A pin that should be left unconnected.

SKiDL will also create a library of all the parts used in your design whenever
you use the `generate_netlist()` function.
For example, if your SKiDL script is named `my_design.py`, then the parts instantiated
in that script will be stored as a SKiDL library in the file `my_design_lib.py`.
This can be useful if you're sending the design to someone who may not have all
the libraries you do.
Just send them `my_design.py` and `my_design_lib.py` and any parts not found
when they run the script will be fetched from the backup parts in the library.


## Doodads

SKiDL has a few features that don't fit into any other
category. Here they are.

### No Connects

Sometimes you will use a part, but you won't use every pin.
The ERC will complain about those unconnected pins:

```terminal
>>> pic10 = Part('microchip_pic10mcu','pic10f220-i/ot')
>>> ERC()
ERC WARNING: Unconnected pin: BIDIRECTIONAL pin 1/ICSPDAT/AN0/GP0 of PIC10F220-I/OT/U1.
ERC WARNING: Unconnected pin: POWER-IN pin 2/VSS of PIC10F220-I/OT/U1.
ERC WARNING: Unconnected pin: BIDIRECTIONAL pin 3/ICSPCLK/AN1/GP1 of PIC10F220-I/OT/U1.
ERC WARNING: Unconnected pin: BIDIRECTIONAL pin 4/T0CKI/FOSC4/GP2 of PIC10F220-I/OT/U1.
ERC WARNING: Unconnected pin: POWER-IN pin 5/VDD of PIC10F220-I/OT/U1.
ERC WARNING: Unconnected pin: INPUT pin 6/Vpp/~MCLR~/GP3 of PIC10F220-I/OT/U1.

6 warnings found during ERC.
0 errors found during ERC.
```

If you have pins that you intentionally want to leave unconnected, then
attach them to the special-purpose `NC` (no-connect) net and the warnings will
be supressed:

```terminal
>>> pic10[1,3,4] += NC
>>> ERC()
ERC WARNING: Unconnected pin: POWER-IN pin 2/VSS of PIC10F220-I/OT/U1.
ERC WARNING: Unconnected pin: POWER-IN pin 5/VDD of PIC10F220-I/OT/U1.
ERC WARNING: Unconnected pin: INPUT pin 6/Vpp/~MCLR~/GP3 of PIC10F220-I/OT/U1.

3 warnings found during ERC.
0 errors found during ERC.
```

In fact, if you have a part with many pins that are not going to be used,
you can start off by attaching all the pins to the `NC` net.
After that, you can attach the pins you're using to normal nets and they
will be removed from the `NC` net:

```py
my_part[:] += NC  # Connect every pin to NC net.
...
my_part[5] += Net()  # Pin 5 is no longer unconnected.
```

The `NC` net is the only net for which this happens.
For all other nets, connecting two or more nets to the same pin
merges those nets and all the pins on them together.

### Net and Pin Drive Levels

Certain parts have power pins that are required to be driven by
a power supply net or else ERC warnings ensue.
This condition is usually satisfied if the power pins are driven by
the output of another part like a voltage regulator.
But if the regulator output passes through something like a 
ferrite bead (to remove noise), then the filtered signal
is no longer a supply net and an ERC warning is issued.

In order to satisfy the ERC, the drive strength of a net can be set manually
using its `drive` attribute. As a simple example, consider connecting
a net to the power supply input of a processor and then running
the ERC:

```terminal
>>> pic10 = Part('microchip_pic10mcu','pic10f220-i/ot')
>>> a = Net()
>>> pic10['VDD'] += a
>>> ERC()
...
ERC WARNING: Insufficient drive current on net N$1 for pin POWER-IN pin 5/VDD of PIC10F220-I/OT/U1
...
```

This issue is fixed by changing the `drive` attribute of the net:

```terminal
>>> pic10 = Part('microchip_pic10mcu','pic10f220-i/ot')
>>> a = Net()
>>> pic10['VDD'] += a
>>> a.drive = POWER
>>> ERC()
...
(Insufficient drive warning is no longer present.)
...
```

You can set the `drive` attribute at any time to any defined level, but `POWER`
is probably the only setting you'll use.
For any net you create that supplies power to devices in your circuit,
you should probably set its `drive` attribute to `POWER`.
This is equivalent to attaching power flags to nets in some ECAD packages like KiCad.

You can also set the `drive` attribute of part pins to override their default drive level.
This is sometimes useful when you are using an output pin of a part to power
another part.

```terminal
>>> pic10_a = Part('microchip_pic10mcu','pic10f220-I/OT')
>>> pic10_b = Part('microchip_pic10mcu','pic10f220-I/OT')
>>> pic10_b['VDD'] += pic10_a[1]  # Power pic10_b from output pin of pic10_a.
>>> ERC()
ERC WARNING: Insufficient drive current on net N$1 for pin POWER-IN pin 5/VDD of PIC10F220-I/OT/U2
... <additional unconnected pin warnings> ...

>>> pic10_a[1].drive = POWER  # Change drive level of pic10_a output pin.
>>> ERC()
... <unconnected pin warnings, but insufficient drive warning is gone> ...
```

### Pin, Net, Bus Equivalencies

Pins, nets, and buses can all be connected to one another in a number of ways.
In order to make them as interchangeable as possible, some additional functions
are defined for each object:

**`__bool__` and `__nonzero__`**:
    Each object will return `True` when used in a boolean operation.
    This can be useful when trying to select an active connection from a set of
    candidates using the `or` operator:

```terminal
>>> a = Net('A')
>>> b = Bus('B', 8)
>>> c = Pin()
>>> d = a or b or c
>>> d
A:
>>> type(d)
<class 'skidl.Net.Net'>
```

**Indexing**:
    Normally, indices can only be used with a Bus object to select one or more bus lines.
    But `Pin` and `Net` objects can also be indexed as long as the index evaluates to zero:

```terminal
>>> a = Net('A')
>>> c = Pin()
>>> a[0] += c[0]
WARNING: Attaching non-part Pin  to a Net A.
>>> a[0] += c[1]
ERROR: Can't use a non-zero index for a pin.
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\xesscorp\KiCad\tools\skidl\skidl\Pin.py", line 251, in __getitem__
    raise Exception
Exception
```

**Width**:
    `Bus`, `Net`, and `Pin` objects all support the `width` property.
    For a `Bus` object, `width` returns the number of bus lines it contains.
    For a `Net` or `Pin` object, `width` always returns 1.

```terminal
>>> a = Net('A')
>>> b = Bus('B', 8)
>>> c = Pin()
>>> a.width
1
>>> b.width
8
>>> c.width
1
```

### Selectively Supressing ERC Messages

Sometimes a portion of your circuit throws a lot of ERC warnings or errors
even though you know it's correct.
SKiDL provides flags that allow you to turn off the ERC for selected nets, pins,
and parts like so:

```py
my_net.do_erc = False      # Turns of ERC for this particular net.
my_part[5].do_erc = False  # Turns off ERC for this pin of this part.
my_part.do_erc = False     # Turns off ERC for all the pins of this part.
```


# Going Really Deep

If all you need to do is design the circuitry for a PCB, then you probably know
all the SKiDL you need to know.
This section will describe the features of SKiDL that might be useful (or not) to
some of the avant-garde circuit designers out there.

## Circuit Objects

Normally, SKiDL puts parts and nets into a global instance of a `Circuit` object
called `default_circuit` (which, of course, you never noticed).
But you can create other `Circuit` objects:

```terminal
>>> my_circuit = Circuit()
```

and then you can create parts, nets and buses and add them to your new circuit:

```terminal
>>> my_circuit += Part('device','R')  # Add a resistor to the circuit.
>>> my_circuit += Net('GND')          # Add a net.
>>> my_circuit += Bus('byte_bus', 8)  # Add a bus.
```

In addition to the `+=` operator, you can also use the methods `add_parts`, `add_nets`, and `add_buses`.
(There's also the much less-used `-=` operator for removing parts, nets or buses
from a circuit along with the `rmv_parts`, `rmv_nets`, and `rmv_buses` methods.)

You can also place parts, nets, and buses directly into a Circuit object
by using the `circuit` parameter of the object constructors:

```terminal
>>> my_circuit = Circuit()
>>> p = Part('device', 'R', circuit = my_circuit)
>>> n = Net('GND', circuit = my_circuit)
>>> b = Bus('byte_bus', 8, circuit = my_circuit)
```

Hierarchical circuits also work with Circuit objects.
In the previous [multi-level hierarchy example](#multilevel_hierarchy_example),
the subcircuit could be instantiated into a Circuit object like this:

```py
my_circuit = Circuit()   # New Circuit object.

gnd = Net('GND')         # GLobal ground net.
input_net = Net('IN')    # Net with the voltage to be divided.
output_net = Net('OUT')  # Net with the divided voltage.
my_circuit += gnd, input_net, output_net  # Move the nets to the new circuit.

# Instantiate the multi-level hierarchical subcircuit into the new Circuit object.
multi_vdiv(3, input_net, output_net, circuit = my_circuit)
```

The actual `circuit` parameter is not passed on to the subcircuit.
It's extracted and any elements created in the subcircuit are sent there instead of
to the default circuit.
(If the `circuit` argument is omitted, the subcircuit function uses the
default circuit as the target of its operations.)

You can do all the same operations on a Circuit object that are supported on the 
default circuit, such as:

```py
# Check the circuit for errors.
my_circuit.ERC()

# Generate the netlist from the new Circuit object.
my_circuit.generate_netlist(sys.stdout)
```

Naturally, the presence of multiple, independent circuits creates the possibility of 
new types of errors.
Here are a few things you can't do (and will get warned about):

* You can't make connections between parts, nets or buses that reside in 
  different Circuit objects.

* Once a part, net, or bus is connected to something else in a Circuit object,
  it can't be moved to a different Circuit object.


# Converting Existing Designs to SKiDL

If you have an existing schematic-based design, you can convert it to SKiDL as follows:

1. Generate a netlist file for your design using whatever procedure your ECAD
   system provides. For this discussion, call the netlist file `my_design.net`.

2. Convert the netlist file into a SKiDL program using the following command:

    ```terminal
    netlist_to_skidl -i my_design.net -o my_design.py -w
    ```

That's it! You can execute the `my_design.py` script and it will regenerate the
netlist. Or you can use the script as a subcircuit in a larger design.
Or do anything else that a SKiDL-based design supports.


# SPICE Simulations

Now you can describe a circuit using SKiDL and run a SPICE simulation on it!
Go [here](https://github.com/xesscorp/skidl/blob/master/examples/spice-sim-intro/spice-sim-intro.ipynb)
to get the complete details.
