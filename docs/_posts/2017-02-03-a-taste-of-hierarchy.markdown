---
layout: post
title: A Taste of Hierarchy
date: 2017-02-03T21:51:58+00:00
author:
    name: Dave Vandenbout
    photo: devb-pic.jpg
    email: devb@xess.com
    description: Relax, I do this stuff for a living.
category: blog
permalink: blog/a-taste-of-hierarchy
---

In my previous blog posts, the SKiDL circuit descriptions were *flat*.
In this post, I'll show a bit of how to describe a circuit *hierarchically*.

Hierarchy is typically used when there is some subcircuit that needs to be
replicated several times or which can serve as a module in several different designs.
In the USB-to-JTAG interface board, the crystal with its two trimming capacitors
is a good candidate for encapsulation in a subcircuit because this combination
of components appears in many circuits.
Here's what a SKiDL subcircuit for the crystal circuit looks like:

``` py
@SubCircuit
def osc(osc1, osc2, gnd):
    '''Attach a crystal and two caps to the osc1 and osc2 nets.'''
    xtal = Part(xess_lib, 'XTAL4', footprint='XESS:32x25-4') # Instantiate the crystal from the library.
    xtal[2, 4] += gnd                   # Connect the crystal ground pins.
    xtal[3, 1] += osc1, osc2            # Connect the crystal pins to the oscillator nets.
    trim_cap = cap(2, value='10pf')     # Instantiate a pair of trimmer caps.
    trim_cap[0][1, 2] += osc1, gnd      # Connect the trimmer caps to the crystal.
    trim_cap[1][1, 2] += osc2, gnd
```

The `@SubCircuit` decorator handles some housekeeping that's necessary to
integrate the encapsulated circuit into the larger whole.
That's followed by a Python function containing SKiDL code for the subcircuit.
(Look back at [this post]({{site.url}}/blog/building-a-usb-to-jtag-interface-using-skidl)
for a description of what this code does.)

Once the subcircuit is defined, all you need to do is call it somewhere within the
main SKiDL code:

``` py
osc( pic32['OSC1'], pic32['OSC2'], gnd )
```

The function call will pass the oscillator pins of the PIC32 microcontroller to the
subcircuit so they can be attached to the crystal and capacitors (along with the
ground net, `gnd`).

Now, there are several problems that make this subcircuit less than ideal:

1. It depends upon the `xess_lib` global variable to find the library with the crystal.
2. It uses a fixed crystal type from that library: `XTAL4`.
3. It references the global `cap` template to instantiate the trimming capacitors.

In order to make the subcircuit more general, we can pass the crystal and capacitor
parts as parameters to the function:

``` py
@SubCircuit
def osc(osc1, osc2, gnd, crystal, cap):
    '''Attach a crystal and two caps to the osc1 and osc2 nets.'''
    xtal = crystal(1)                  # Instantiate the crystal from the template.
    xtal[2, 4] += gnd                  # Connect the crystal ground pins.
    xtal[3, 1] += osc1, osc2           # Connect the crystal pins to the oscillator nets.
    trim_cap = cap(2, value='10pf')    # Instantiate a pair of trimmer caps.
    trim_cap[0][1, 2] += osc1, gnd     # Connect the trimmer caps to the crystal.
    trim_cap[1][1, 2] += osc2, gnd
```

But that means you have to create the template for the crystal before calling the
`osc` function:

``` py
crystal = Part(xess_lib, 'XTAL4', footprint='XESS:32x25-4', dest=TEMPLATE)
osc(pic32['OSC1'], pic32['OSC2'], gnd, crystal, cap)
```

This works fine as long as you're using a crystal in a four-pin package.
But many crystals only have two terminals.
You can handle that in the subcircuit function as follows:

``` py
@SubCircuit
def osc(osc1, osc2, gnd, crystal, cap):
    '''Attach a crystal and two caps to the osc1 and osc2 nets.'''
    xtal = crystal(1)                  # Instantiate the crystal from the template.
    num_xtal_pins = len(xtal['.*'])    # Get the number of pins on the crystal.
    if num_xtal_pins == 4:             # This handles a 4-pin crystal...
        xtal[2, 4] += gnd              # Connect the crystal ground pins.
        xtal[3, 1] += osc1, osc2       # Connect the crystal pins to the oscillator nets.
    else:                              # Otherwise assume it's a 2-pin crystal...
        xtal[1,2] += osc1, osc2        # Using a two-pin crystal.
    trim_cap = cap(2, value='10pf')    # Instantiate a pair of trimmer caps.
    trim_cap[0][1, 2] += osc1, gnd     # Connect the trimmer caps to the crystal.
    trim_cap[1][1, 2] += osc2, gnd
```

The wildcard regular expression makes `xtal['.*']` return a list of all of its pins.
Then, the Python `len` operator gets the length of the list and tells us how many pins the crystal has.
After that, it's just a matter of connecting the right pins depending upon how many there are.
Now if you call the `osc` function with a two-pin crystal, it will work correctly:

``` py
crystal = Part("Device", 'Crystal', footprint='Crystal:Crystal_HC49-U_Vertical', dest=TEMPLATE)
osc(*pic32['OSC1, OSC2'], gnd, crystal, cap)
```

Of course, sometimes you might want a simpler way to instantiate the subcircuit
without having to pass components as parameters.
Python default parameters come to the rescue!

``` py
@SubCircuit
def osc(osc1, osc2, gnd, 
        crystal = Part("Device", 'Crystal', footprint='Crystal:Crystal_HC49-U_Vertical', dest=TEMPLATE), 
        cap = Part("Device",'C',value='10pf', footprint='Capacitors_SMD:C_0603', dest=TEMPLATE) ):
    '''Attach a crystal and two caps to the osc1 and osc2 nets.'''
    xtal = crystal(1)                  # Instantiate the crystal from the template.
    num_xtal_pins = len(xtal['.*'])    # Get the number of pins on the crystal.
    if num_xtal_pins == 4:             # This handles a 4-pin crystal...
        xtal[2, 4] += gnd              # Connect the crystal ground pins.
        xtal[3, 1] += osc1, osc2       # Connect the crystal pins to the oscillator nets.
    else:                              # Otherwise assume it's a 2-pin crystal...
        xtal[1,2] += osc1, osc2        # Using a two-pin crystal.
    trim_cap = cap(2)                  # Instantiate some trimmer caps.
    trim_cap[0][1, 2] += osc1, gnd     # Connect the trimmer caps to the crystal.
    trim_cap[1][1, 2] += osc2, gnd
```

Now you can instantiate the default oscillator circuit with the function call:

``` py
osc(pic32['OSC1'], pic32['OSC2'], gnd)
```

Finally, here's the [complete SKiDL program]({{site.url}}/files/a-taste-of-hierarchy/intfc_brd.py) so you can see how it fits together:

{% render_code a-taste-of-hierarchy/intfc_brd.py %}
