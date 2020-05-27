---
layout: post
title: Good Things Come In Packages!
date: 2020-05-27T10:01:10-05:00
author:
    name: Dave Vandenbout
    photo: devb-pic.jpg
    email: devb@xess.com
    description: Relax, I do this stuff for a living.
category: blog
permalink: blog/package-decorator
---

Up to now, SKiDL supported hierarchy by applying the `@subcircuit` decorator to a Python function:

```py
@subcircuit
def analog_average(in1, in2, avg):
    """Output the average of the two inputs."""
    
    # Create two 1K resistors.
    r1, r2 = 2 * Part('Device', 'R', value='1K', dest=TEMPLATE)
   
    # Each input connects thru a resistor to the avg output.
    r1[1,2] += in1, avg
    r2[1,2] += in2, avg
```

Then this subcircuit is instantiated by calling the function with nets
passed as arguments:

```py
in1, in2, in3, in4, out1, out2 = Net()*6  # Make some I/O nets.

analog_average(in1, in2, out1)  # One instantiation of the averager.

... Some more code ...

analog_average(in3, in4, out2)  # A second instantiation.
```

It was [pointed out](https://github.com/xesscorp/skidl/issues/48) that this method
of instantiating subcircuits is quite different from what is used for parts.
Unlike the connections to a subcircuit that are all made at a single place when the
function is called, the connections to a part can be placed
at various, non-contiguous locations in the code:

```py
q_npn = Part("Device", "Q_NPN_BCE")  # Instantiate a transistor.

...

q_npn['E'] += Net('GND')  # Connect the emitter to ground.

...

q_npn['B'] += in1  # Connect an input to the base.

...

q_npn['C'] += out1  # Connect the output to the collector.
```

Another issue is that you can pass a part instance as an argument to a subcircuit that
connects it to the internal circuitry.
But you can't do the same thing with a subcircuit function without making changes to the
code because of the syntactic differences in how connections are made:

```py
@subcircuit
def analog_average(in1, in2, avg, r):
    """Output the average of the two inputs."""

    r1, r2 = r(num_copies=2)  # Create two copies of the resistor part.
    r1[1,2] += in1, avg
    r2[1,2] += in2, avg

    # If r was a subcircuit function, this would have to be written as:
    # r(in1, avg)
    # r(in2, avg)
```

To make subcircuits act more like parts, the `@package` decorator has been introduced.
Just replace the `@subcircuit` decorator while keeping everything else the same:

```py
@package
def analog_average(in1, in2, avg):
    r1, r2 = 2 * Part('Device', 'R', value='1K', dest=TEMPLATE)
    r1[1,2] += in1, avg
    r2[1,2] += in2, avg
```

Instantiating the subcircuit now occurs in two phases.
First, create instances of the subcircuit wherever they are needed:

```py
avg1 = analog_average()

...

avg2 = analog_average()
```

In the second phase, make connections to these subcircuits as if they were parts
with the names of the function parameters serving as pin names:

```py
in1, in2, in3, in4, out1, out2 = Net()*6

# Make connections. You can use either [] or . to reference the I/O.
avg1['in1'] += in1
avg1.in2    += in2
avg1['avg'] += out1

...

avg2['in1'] += in3
avg2['in2'] += in4
avg2.avg    += out2
```

In addition to nets, pins, and buses, you can pass any other type of
parameter to subcircuits.
For example, `analog_average` could take a float as a `ratio` parameter to
set the amount each input contributes to the output:

```py
@package
def analog_average(in1, in2, avg, ratio):
    r = Part('Device', 'R', dest=TEMPLATE)
    r1 = r(value=2000 * ratio)
    r2 = r(value=2000 * (1-ratio))

    r1[1,2] += in1, avg
    r2[1,2] += in2, avg
```

Then the subcircuit can either be instantiated with a given ratio:

```py
avg1 = analog_average(ratio=0.25)
avg1.in1 += in1
avg1.in2 += in2
avg1.avg += out1
```
or you can set the ratio outside the function call:
```py
avg2 = analog_average()
avg2.ratio = 0.25  # Use a normal assignment (=) since this is not a circuit connection.
avg2.in1 += in3
avg2.in2 += in4
avg2.avg += out2
```

A subcircuit function instantiates its circuitry when it is called.
But this doesn't happen when using a package.
Instead, the subcircuit is placed in a list and executed after the
complete circuit is finalized
(i.e., whenever `ERC()` or `generate_netlist()` is called).
The arguments passed to the function consist of the connections
and other values that were assigned to the package parameters in the preceding code.

That's about it for the `@package` decorator.
Since it's new, it hasn't seen a lot of use and there could be unknown bugs
lying in wait.
If you have questions or problems, please ask on the
[SKiDL forum](https://skidl.discourse.group/) or
raise an [issue](https://github.com/xesscorp/skidl/issues). 
