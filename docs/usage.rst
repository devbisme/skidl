========
Usage
========

Scratching the Surface
--------------------------

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


Accessing SKiDL
................................

To use skidl in a project, just place the following at the top of your file::

    import skidl

But for this tutorial, I'll just import everything::

    from skidl import *


Finding Parts
................................

SKiDL provides a convenience function for searching for parts called
(naturally) ``search``. Suppose you want to use a resistor, but don't know 
what the name of the part is. Assuming it probably starts with "R", ``search``
can be used to do a wildcard search of the part libraries:

    >>> search('R.*')
    bbd.lib: RD5106A
    conn.lib: RJ12
    conn.lib: RJ45
    conn.lib: RJ45-TRANSFO
    conn.lib: RJ45_LEDS
    device.lib: R
    device.lib: RELAY_2RT
    device.lib: RF_SHIELD_ONE_PIECE
    device.lib: RF_SHIELD_TWO_PIECES
    ...
    references.lib: REF3212AMDBVREP
    references.lib: REF5020AD
    references.lib: REF5020ADGK
    rfcom.lib: RN42
    rfcom.lib: RN42N
    >>>

Or suppose you want an LM358 opamp::

    >>> search('LM358')
    linear.lib: LM358

Once you have the part name and library, you can see the part's pin numbers, names
and their functions using the ``show`` function::

    >>> show('device','R')
    R:
            Pin 1/~: PASSIVE
            Pin 2/~: PASSIVE

    >>> show('linear','LM358')
    LM358:
            Pin 4/V-: POWER-IN
            Pin 8/V+: POWER-IN
            Pin 1/~: OUTPUT
            Pin 2/-: INPUT
            Pin 3/+: INPUT
            Pin 5/+: INPUT
            Pin 6/-: INPUT
            Pin 7/~: OUTPUT


Instantiating Parts
................................

The part library and name are used to instantiate a part as follows::

    >>> resistor = Part('device','R')

You can customize the resistor by setting its attributes::

    >>> resistor.value = '1K' 
    >>> resistor.value        
    '1K'                      

You can also combine the setting of attributes with the creation of the part::

    >>> resistor = Part('device', 'R', value='1K')
    >>> resistor.value
    '1K'

You can use any valid Python name for a part attribute, but ``ref``, ``value``,
and ``footprint`` are necessary in order to generate the final netlist
for your circuit. And the attribute can hold any type of Python object,
but simple strings are probably the most useful.

The ``ref`` attribute holds the *reference* for the part. It's set automatically
when you create the part::

    >>> resistor.ref
    'R1'

Since this was the first resistor we created, it has the honor of being named ``R1``.
But you can easily change it:

    >>> resistor.ref = 'R5'
    >>> resistor.ref
    'R5'

Now what happens if we create another resistor?::

    >>> another_res = Part('device','R')   
    >>> another_res.ref                        
    'R1'

Since the ``R1`` reference was now available, the new resistor got it.
What if we tried renaming the first resistor back to ``R1``:

    >>> resistor.ref = 'R1'
    >>> resistor.ref
    'R1_1'

Since the ``R1`` reference was already taken, SKiDL tried to give us
something close to what we wanted.
SKiDL won't let different parts have the same reference because
that would confuse the hell out of everybody.
                            

Connecting Pins
................................

Parts are great and all, but not very useful if they aren't connected to anything.
The connections between parts are called *nets* (think of them as wires)
and every net has one or more part *pins* on it.
SKiDL makes it easy to create nets and connect pins to them. 
To demonstrate, let's build the voltage divider circuit
shown in the introduction.

First, start by creating two resistors (note that I've also added the
``footprint`` attribute that describes the physical package for the resistors)::

    >>> rup = Part('device', 'R', value='1K', footprint='Resistors_SMD:R_0805')                            
    >>> rlow = Part('device', 'R', value='500', footprint='Resistors_SMD:R_0805')                          
    >>> rup.ref, rlow.ref                                                
    ('R1', 'R2')                                                         
    >>> rup.value, rlow.value                                            
    ('1K', '500')                                                        

To bring the voltage that will be divided into the circuit, let's create a net::

    >>> v_in = Net('VIN')
    >>> v_in.name
    'VIN'

Now attach the net to one of the pins of the ``rup`` resistor
(resistors are bidirectional which means it doesn't matter which pin, so pick pin 1)::

    >>> rup[1] += v_in

You can verify that the net is attached to pin 1 of the resistor like this::

    >>> rup[1].net
    VIN: Pin 1/~: PASSIVE

Next, create a ground reference net and attach it to ``rlow``::

    >>> gnd = Net('GND')
    >>> rlow[1] += gnd
    >>> rlow[1].net
    GND: Pin 1/~: PASSIVE

Finally, the divided voltage has to come out of the circuit on a net.
This can be done in several ways.
The first way is to define the output net and then attach the unconnected
pins of both resistors to it::

    >>> v_out = Net('VO')
    >>> v_out += rup[2], rlow[2]
    >>> rup[2].net, rlow[2].net
    (VO: Pin 2/~: PASSIVE, Pin 2/~: PASSIVE, VO: Pin 2/~: PASSIVE, Pin 2/~: PASSIVE)

An alternate method is to connect the resistors and then attach their
junction to the output net::

    >>> rup[2] += rlow[2]
    >>> v_out = Net('VO')
    >>> v_out += rlow[2]
    >>> rup[2].net, rlow[2].net
    (VO: Pin 2/~: PASSIVE, Pin 2/~: PASSIVE, VO: Pin 2/~: PASSIVE, Pin 2/~: PASSIVE)

Either way works! Sometimes pin-to-pin connections are easier when you're
just wiring two devices together, while the pin-to-net connection method
excels when three or more pins have a common connection.


Checking for Errors
................................

Once the parts are wired together, you can do simple electrical rules checking
like this::

    >>> ERC()                           
                                        
    2 warnings found during ERC.        
    0 errors found during ERC.          

Since this is an interactive session, the ERC warnings and errors are stored 
in the file ``skidl.erc``. (Normally, your SKiDL circuit description is stored
as a Python script such as ``my_circuit.py`` and the ``ERC()`` function will
dump its messages to ``my_circuit.erc``.)
The ERC messages are::

    WARNING: Only one pin (PASSIVE pin 1/~ of R/R1) attached to net VIN.
    WARNING: Only one pin (PASSIVE pin 1/~ of R/R2) attached to net GND.

These messages are generated because the ``VIN`` and ``GND`` nets each have only
a single pin on them and this usually indicates a problem.
But it's OK for this simple example, so the ERC can be turned off for
these two nets to prevent the spurious messages::

    >>> v_in.do_erc = False
    >>> gnd.do_erc = False
    >>> ERC()

    No ERC errors or warnings found.
                                    

Generating a Netlist
................................

The end goal of using SKiDL is to generate a netlist that can be used
with a layout tool to generate a PCB. The netlist is output as follows::

    >>> generate_netlist()

Like the ERC output, the netlist shown below is stored in the file ``skidl.net``.
But if your SKiDL circuit description is in the ``my_circuit.py`` file, 
then the netlist will be stored in ``my_circuit.net``.

::

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


Going Deeper
---------------------

The previous section showed the bare minimum you need to know to design
circuits with SKiDL, but doing a complicated circuit that way would suck donkeys.
This section will talk about some more advanced features.

Basic SKiDL Objects: Parts, Pins, Nets, and Buses
.....................................................

SKiDL uses four types of objects to represent a circuit: ``Part``, ``Pin``,
``Net``, and ``Bus``.

The ``Part`` object represents an electronic component, which SKiDL thinks of as simple
bags of ``Pin`` objects with a few other attributes attached 
(like the part number, name, reference, value, footprint, etc.).

The ``Pin`` object represents a terminal that brings an electronic signal into
and out of the part. Each ``Pin`` object has two important attributes:

* ``part`` which stores the reference to the ``Part`` object to which the pin belongs.
* ``net`` which stores the the reference to the ``Net`` object that the pin is
  connected to, or ``None`` if the pin is unconnected.

A ``Net`` object is kind of like a ``Part``: it's a simple bag of pins.
The difference is, unlike a part, pins can be added to a net.
This happens when a pin on some part is connected to the net or when the 
net is merged with another net.

Finally, a ``Bus`` is just a list of ``Net`` objects.
A bus of a certain width can be created from a number of existing nets,
newly-created nets, or both.


Creating SKiDL Objects
............................

Here's the most common way to create a part in your circuit::

    my_part = Part('some_library', 'some_part_name')

When this is processed, the current directory will be checked for a file
called ``some_library.lib`` which will be opened and scanned for a part with the
name ``some_part_name``. If the file is not found or it doesn't contain
the requested part, then the process will be repeated using KiCad's default
library directory.

You're not restricted to using only the current directory or the KiCad default
directory to search for parts. You can also search any file for a part by 
using a full file name::

    my_part = Part('C:/my_libs/my_great_parts.lib', 'my_super_regulator')

You're also not restricted to getting an exact match on the part name: you can
use a *regular expression* instead. For example, this will find a part
with "358" anywhere in a part name or alias::

    my_part = Part('some_library', '.*358.*')

If the regular expression matches more than one part, then you'll only get the
first match and a warning that multiple parts were found.

Once you have a part, you can set its attributes like you could for any Python
object. As was shown previously, the ``ref`` attribute will already be set
but you can override it::

    my_part.ref = 'U5'

The ``value`` and ``footprint`` attributes are also required for generating
a netlist. But you can also add any other attribute::

    my_part.manf = 'Atmel'
    my_part.setattr('manf#', 'ATTINY4-TSHR'

It's also possible to set the attributes during the part creation::

    my_part = Part('some_lib', 'some_part', ref='U5', footprint='SMD:SOT23_6', manf='Atmel')

Creating nets is also simple::

    my_net = Net()              # An unnamed net.
    my_other_net = Net('Fred')  # A named net.

As with parts, SKiDL will alter the name you assign to a net if it collides with another net
having the same name.

You can create a bus of a certain width like this::

    my_bus = Bus('bus_name', 8)  # Create a byte-wide bus.

(All buses must be named, but SKiDL will look for and correct colliding
bus names.)

You can also create a bus from existing nets, or buses, or the pins of parts::

    my_part = Part('linear', 'LM358')
    a_net = Net()
    b_net = Net()
    bus_nets = Bus('net_bus', a_net, b_net)            # A 2-bit bus.
    bus_pins = Bus('pin_bus', my_part[1], my_part[3])  # A 2-bit bus.
    bus_buses = Bus('bus_bus', my_bus)                 # An 8-bit bus.

Finally, you can mix-and-match any combination of widths, nets, buses or part pins::

    bus_mixed = Bus('mongrel', 8, a_net, my_bus, my_part[2])  # 8+1+8+1 = 18-bit bus.

The final object you can create is a ``Pin``. You'll probably never do this
(except in interactive sessions), and it's probably a mistake if
you ever do do it, but here's how to do it::

    >>> p = Pin(num=1, name='my_pin', func=Pin.TRISTATE)
    >>> p
    Pin 1/my_pin: TRISTATE


Accessing Part Pins and Bus Lines
......................................

You can access the pins on a part or the individual nets of a bus
using numbers, slices, strings, and regular expressions, either singly or in any combination.

Suppose you have a PIC10 processor in a six-pin package::

    >>> pic10 = Part('microchip_pic10mcu', 'pic10f220-i/ot')          
    >>> pic10                                                         
    PIC10F220-I/OT:                                                   
            Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL                      
            Pin 2/VSS: POWER-IN                                       
            Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL                      
            Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL                      
            Pin 5/VDD: POWER-IN                                       
            Pin 6/Vpp/~MCLR~/GP3: INPUT                               

The most natural way to access one of its pins is to give the pin number
in brackets::

    >>> pic10[3]                          
    Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL

(If you have a part in a BGA package with pins numbers like ``C11``, then
you'll have to enter the pin number as a quoted string like ``'C11'``.)

You can also get several pins at once in a list::

    >>> pic10[3,1,6]                                                                                      
    [Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL, Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL, Pin 6/Vpp/~MCLR~/GP3: INPUT]                                                                                                   

You can even use Python slice notation::

    >>> pic10[2:4]  # Get pins 2 through 4.
    [Pin 2/VSS: POWER-IN, Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL, Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL]
    >>> pic10[4:2]  # Get pins 4 through 2.
    [Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL, Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL, Pin 2/VSS: POWER-IN]
    >>> pic10[:]    # Get all the pins.
    [Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL, Pin 2/VSS: POWER-IN, Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL, Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL, Pin 5/VDD: POWER-IN, Pin 6/Vpp/~MCLR~/GP3: INPUT]

(It's important to note that the slice notation used by SKiDL for parts is slightly
different than standard Python. In Python, a slice ``n:m`` would fetch indices
``n``, ``n+1``, ``...``, ``m-1``. With SKiDL, it actually fetches all the
way up to the last number: ``n``, ``n+1``, ``...``, ``m-1``, ``m``.
The reason for doing this is that most electronics designers are used to
the bounds on a slice including both endpoints. Perhaps it is a mistake to
do it this way. We'll see...)

Instead of pin numbers, sometimes it makes the design intent more clear to 
access pins by their names.
For example, it's more obvious that a voltage supply net is being
attached to the power pin of the processor when it's expressed like this::

    pic10['VDD'] += supply_5V

You can use multiple names or regular expressions to get more than one pin::

    >>> pic10['VDD','VSS']
    [Pin 5/VDD: POWER-IN, Pin 2/VSS: POWER-IN]
    >>> pic10['.*GP[1-3]']
    [Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL, Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL, Pin 6/Vpp/~MCLR~/GP3: INPUT]

It can be tedious and error prone entering all the quote marks if you're accessing
many pin names. SKiDL lets you enter a single, comma-delimited string of
pin names::

    >>> pic10['.*GP0, .*GP1, .*GP2']
    [Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL, Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL, Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL]

``Part`` objects also provide the ``get_pins()`` function which can select pins in even more ways.
For example, this would get every bidirectional pin of the processor::

    >>> pic10.get_pins(func=Pin.BIDIR)
    [Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL, Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL, Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL]

However, slice notation doesn't work with pin names. You'll get an error if you try that.

Accessing the individual nets of a bus works similarly to accessing part pins::

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


Making Connections
...........................

Pins, nets, parts and buses can all be connected together in various ways, but
the primary rule of SKiDL connections is:

    **The ``+=`` operator is the only way to make connections!**

At times you'll mistakenly try to make connections using the 
assignment operator (``=``). In many cases, SKiDL warns you if you do that,
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

There are three variants of each connection operation:

**One-to-One**:
    This is the most frequent type of connection, for example, connecting one
    pin to another or connecting a pin to a net.
**One-to-Many**:
    This mainly occurs when multiple pins are connected to the same net, like
    when multiple ground pins of a chip are connected to the circuit ground net.
**Many-to-Many**:
    This usually involves bus connections to a part, such as connecting
    a bus to the data or address pins of a processor. But there must be the
    same number of things to connect in each set, e.g. you can't connect
    three pins to four nets.

As a first example, let's connect a net to a pin on a part::

    >>> pic10 = Part('microchip_pic10mcu','pic10f220-i/ot')  # Get a part.
    >>> io = Net('IO_NET')    # Create a net.
    >>> pic10['.*GP0'] += io  # Connect the net to a part pin.
    >>> io                    # Show the pins connected to the net.
    IO_NET: Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL

You can do the same operation in reverse by connecting the part pin to the net
with the same result::

    >>> pic10 = Part('microchip_pic10mcu','pic10f220-i/ot')
    >>> io = Net('IO_NET')
    >>> io += pic10['.*GP0']  # Connect a part pin to the net.
    >>> io
    IO_NET: Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL

You can also connect a pin directly to another pin.
In this case, an *implicit net* will be created between the pins that can be
accessed using the ``net`` attribute of either part pin::

    >>> pic10['.*GP1'] += pic10['.*GP2']  # Connect two pins together.
    >>> pic10['.*GP1'].net     # Show the net connected to the pin.
    N$1: Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL, Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL
    >>> pic10['.*GP2'].net     # Show the net connected to the other pin. Same thing!
    N$1: Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL, Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL

You can connect multiple pins together, all at once::

    >>> pic10[1] += pic10[2,3,6]
    >>> pic10[1].net
    N$1: Pin 6/Vpp/~MCLR~/GP3: INPUT, Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL, Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL, Pin 2/VSS: POWER-IN

Or you can do it incrementally::

    >>> pic10[1] += pic10[2]
    >>> pic10[1] += pic10[3]
    >>> pic10[1] += pic10[6]
    >>> pic10[1].net
    N$1: Pin 2/VSS: POWER-IN, Pin 6/Vpp/~MCLR~/GP3: INPUT, Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL, Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL

If you connect pins on separate nets together, then all the pins are merged onto the same net::

    >>> pic10[1] += pic10[2]  # Put pins 1 & 2 on one net.
    >>> pic10[1].net
    N$1: Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL, Pin 2/VSS: POWER-IN
    >>> pic10[3] += pic10[4]  # Put pins 3 & 4 on another net.
    >>> pic10[3].net
    N$2: Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL, Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL
    >>> pic10[1] += pic10[4]  # Connect two pins from different nets.
    >>> pic10[3].net          # Now all the pins are on the same net!
    N$2: Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL, Pin 2/VSS: POWER-IN, Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL, Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL

Here's an example of connecting a three-bit bus to three pins on a part:

    >>> pic10 = Part('microchip_pic10mcu','pic10f220-i/ot')
    >>> pic10
    PIC10F220-I/OT:
            Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL
            Pin 2/VSS: POWER-IN
            Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL
            Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL
            Pin 5/VDD: POWER-IN
            Pin 6/Vpp/~MCLR~/GP3: INPUT
    >>> b = Bus('GP', 3)        # Create a 3-bit bus.
    >>> pic10[4,3,1] += b[2:0]  # Connect bus to part pins, one-to-one.
    >>> b
    GP:
            GP0: Pin 1/ICSPDAT/AN0/GP0: BIDIRECTIONAL
            GP1: Pin 3/ICSPCLK/AN1/GP1: BIDIRECTIONAL
            GP2: Pin 4/T0CKI/FOSC4/GP2: BIDIRECTIONAL

But SKiDL will warn you if there aren't the same number of things to
connect on each side::

    >>> pic10[4,3,1] += b[1:0]  # Too few bus lines for the pins!
    ERROR: Connection mismatch 3 != 2!
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "c:\xesscorp\kicad\tools\skidl\skidl\skidl.py", line 2630, in __iadd__
        raise Exception
    Exception


Hierarchy
...................

SKiDL supports the encapsulation of parts, nets and buses into modules
that can be replicated to reduce the design effort, and can be used in
other modules to create a functional hierarchy.
It does this using Python's built-in machinery for defining and calling functions
so there's almost nothing new to learn.

As an example, here's the voltage divider as a module::

    from skidl import *
    import sys

    # Define the voltage divider module. The @SubCircuit decorator 
    # handles some skidl housekeeping that needs to be done.
    @SubCircuit
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

For the most part, ``vdiv`` is just a standard Python function:
it accepts inputs, it performs operations on them, and it could return
outputs (but in this case, it doesn't need to).
Other than the ``@SubCircuit`` decorator that appears before the function definition,
``vdiv`` is just a Python function and it can do anything that a Python function can do.

Here's the netlist that's generated::

    (export (version D)
      (design
        (source "C:/Users/DEVB/PycharmProjects/test1\test.py")
        (date "08/15/2016 03:35 PM")
        (tool "SKiDL (0.0.1)"))
      (components
        (comp (ref R1)
          (value 1K)
          (footprint Resistors_SMD:R_0805))
        (comp (ref R2)
          (value 500)
          (footprint Resistors_SMD:R_0805)))
      (nets
        (net (code 0) (name "IN")
          (node (ref R1) (pin 1)))
        (net (code 1) (name "OUT")
          (node (ref R1) (pin 2))
          (node (ref R2) (pin 1)))
        (net (code 2) (name "GND")
          (node (ref R2) (pin 2))))
    )

For an example of a multi-level hierarchy, the ``multi_vdiv`` module shown below
can use the ``vdiv`` module to divide a voltage multiple times::

    from skidl import *
    import sys

    # Define the voltage divider module.
    @SubCircuit
    def vdiv(inp, outp):
        """Divide inp voltage by 3 and place it on outp net."""
        rup = Part('device', 'R', value='1K', footprint='Resistors_SMD:R_0805')
        rlo = Part('device','R', value='500', footprint='Resistors_SMD:R_0805')
        rup[1,2] += inp, outp
        rlo[1,2] += outp, gnd

    @SubCircuit
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

(For the EE's out there: *yes, I know cascading three simple voltage dividers
will not multiplicatively scale the input voltage because of the
input and output impedances of each stage!*
It's just the simplest example I could think of that shows the feature.)

And here's the resulting netlist::

    (export (version D)
      (design
        (source "C:/Users/DEVB/PycharmProjects/test1\test.py")
        (date "08/15/2016 05:52 PM")
        (tool "SKiDL (0.0.1)"))
      (components
        (comp (ref R1)
          (value 1K)
          (footprint Resistors_SMD:R_0805))
        (comp (ref R2)
          (value 500)
          (footprint Resistors_SMD:R_0805))
        (comp (ref R3)
          (value 1K)
          (footprint Resistors_SMD:R_0805))
        (comp (ref R4)
          (value 500)
          (footprint Resistors_SMD:R_0805))
        (comp (ref R5)
          (value 1K)
          (footprint Resistors_SMD:R_0805))
        (comp (ref R6)
          (value 500)
          (footprint Resistors_SMD:R_0805)))
      (nets
        (net (code 0) (name "IN")
          (node (ref R1) (pin 1)))
        (net (code 1) (name "N$1")
          (node (ref R2) (pin 1))
          (node (ref R1) (pin 2))
          (node (ref R3) (pin 1)))
        (net (code 2) (name "GND")
          (node (ref R4) (pin 2))
          (node (ref R6) (pin 2))
          (node (ref R2) (pin 2)))
        (net (code 3) (name "N$2")
          (node (ref R5) (pin 1))
          (node (ref R3) (pin 2))
          (node (ref R4) (pin 1)))
        (net (code 4) (name "OUT")
          (node (ref R5) (pin 2))
          (node (ref R6) (pin 1))))
    )


Doodads
...................................

SKiDL has a few features that don't fit into any other
category. Here they are.

No Connects
''''''''''''''''''''''

Sometimes you will use a part, but you won't use every pin.
The ERC will complain about those unconnected pins::

    >>> pic10 = Part('microchip_pic10mcu','pic10f220-i/ot')
    >>> ERC()
    ERC WARNING: Unconnected pin: BIDIRECTIONAL pin 1/ICSPDAT/AN0/GP0 of PIC10F220-I/OT/IC1.
    ERC WARNING: Unconnected pin: POWER-IN pin 2/VSS of PIC10F220-I/OT/IC1.
    ERC WARNING: Unconnected pin: BIDIRECTIONAL pin 3/ICSPCLK/AN1/GP1 of PIC10F220-I/OT/IC1.
    ERC WARNING: Unconnected pin: BIDIRECTIONAL pin 4/T0CKI/FOSC4/GP2 of PIC10F220-I/OT/IC1.
    ERC WARNING: Unconnected pin: POWER-IN pin 5/VDD of PIC10F220-I/OT/IC1.
    ERC WARNING: Unconnected pin: INPUT pin 6/Vpp/~MCLR~/GP3 of PIC10F220-I/OT/IC1.

If you have pins that you intentionally want to leave unconnected, then
attach them to the special-purpose ``NC`` (no-connect) net and the warnings will
be supressed::

    >>> pic10[1,3,4] += NC
    >>> ERC()
    ERC WARNING: Unconnected pin: POWER-IN pin 2/VSS of PIC10F220-I/OT/IC1.
    ERC WARNING: Unconnected pin: POWER-IN pin 5/VDD of PIC10F220-I/OT/IC1.
    ERC WARNING: Unconnected pin: INPUT pin 6/Vpp/~MCLR~/GP3 of PIC10F220-I/OT/IC1.

In fact, if you have a part with many pins that are not going to be used,
you can start off by attaching all the pins to the ``NC`` net.
After that, you can attach the pins you're using to normal nets and they
will be removed from the ``NC`` net::

    my_part[:] += NC  # Connect every pin to NC net.
    ...
    my_part[5] += Net()  # Pin 5 is no longer unconnected.

The ``NC`` net is the only net for which this happens.
For all other nets, connecting two or more nets to the same pin
merges those nets and all the pins on them together.

Net Drive Level
''''''''''''''''''''''

Certain parts have power pins that are required to be driven by
a power supply net or else ERC warnings ensue.
This condition is usually satisfied if the power pins are driven by
the output of another part like a voltage regulator.
But if the regulator output passes through something like a 
ferrite bead (to remove noise), then the filtered signal
is no longer a supply net and an ERC warning is issued.

In order to satisfy the ERC, the drive strength of a net can be set manually
using its ``drive`` attribute. As a simple example, consider connecting
a net to the power supply input of a processor and then running
the ERC::

    >>> pic10 = Part('microchip_pic10mcu','pic10f220-i/ot')
    >>> a = Net()
    >>> pic10['VDD'] += a
    >>> ERC()
    ...
    ERC WARNING: Insufficient drive current on net N$1 for pin POWER-IN pin 5/VDD of PIC10F220-I/OT/IC1
    ...

This issue is fixed by changing the ``drive`` attribute of the net::

    >>> pic10 = Part('microchip_pic10mcu','pic10f220-i/ot')
    >>> a = Net()
    >>> pic10['VDD'] += a
    >>> a.drive = POWER
    >>> ERC()
    ...
    (Insufficient drive warning is no longer present.)
    ...

You can set the ``drive`` attribute at any time to any defined level, but ``POWER``
is probably the only setting you'll use.
Also, the ``drive`` attribute retains the highest of all the levels it has been set at,
so once it is set to the POWER level it is impossible to set it to a lower level.
(This is done during internal processing to keep a net at the highest drive 
level of any of the pins that have been attached to it.)

In short, for any net you create that supplies power to devices in your circuit,
you should probably set its ``drive`` attribute to ``POWER``.
This is equivalent to attaching power flags to nets in some ECAD packages like KiCad.

Selectively Supressing ERC Messages
''''''''''''''''''''''''''''''''''''''

Sometimes a portion of your circuit throws a lot of ERC warnings or errors
even though you know it's correct.
SKiDL provides flags that allow you to turn off the ERC for selected nets, pins,
and parts like so::

    my_net.do_erc = False      # Turns of ERC for this particular net.
    my_part[5].do_erc = False  # Turns off ERC for this pin of this part.
    my_part.do_erc = False     # Turns off ERC for all the pins of this part.


Converting Existing Designs to SKiDL
-------------------------------------

If you have an existing schematic-based design, you can convert it to SKiDL as follows:

#. Generate a netlist file for your design using whatever procedure your ECAD
   system provides. For this discussion, call the netlist file ``my_design.net``.

#. Convert the netlist file into a SKiDL program using the following command::

    netlist_to_skidl -i my_design.net -o my_design.py -w

That's it! You can execute the ``my_design.py`` script and it will regenerate the
netlist. Or you can use the script as a subcircuit in a larger design.
Or do anything else that a SKiDL-based design supports.
