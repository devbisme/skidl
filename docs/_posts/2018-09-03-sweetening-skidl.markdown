---
layout: post
title: Sweetening SKiDL
date: 2018-09-03T19:59:47-04:00
author:
    name: Dave Vandenbout
    photo: devb-pic.jpg
    email: devb@xess.com
    description: Relax, I do this stuff for a living.
category: blog
permalink: blog/sweetening-skidl
---

I've added a bit of syntactic sugar to SKiDL over the past few months:

- [Series, Parallel, and Tee Network Constructors](#series-parallel-and-tee-network-constructors)
- [Bussed Part Pins](#bussed-part-pins)
- [Accessing Part Pins as Attributes](#accessing-part-pins-as-attributes)
 
It doesn't change what SKiDL does, but does make it easier to do it.


### Series, Parallel, and Tee Network Constructors

Last year, I had a [discussion](https://github.com/devbisme/skidl/issues/26) with
[kasbah](https://github.com/kasbah) on the SKiDL Github about his suggestion
to overload the `>>` operator to wire two-pin parts in series.
A lot of good ideas came out of that,
but in the end we thought it had limited use and dropped it.

Fast forward to a few months ago when I was working on a project to use genetic algorithms
for optimizing a power supply.
One of the tasks was to programmatically create series and parallel combinations
of two-pin components.
By looking at the connection of two-pin components in serial or parallel as the
creation of a two-pin *network*, a concise syntax arose to create circuits much
more complicated than simple series connections.

To support this idea in SKiDL, I overloaded the bitwise AND (`&`) and OR (`|`) operators
to connect two-pin components in *series or parallel*, respectively.
For example, here is a network of four series resistors using the standard
SKiDL syntax:

```py
r1, r2, r3, r4 = Part('Device', 'R', dest=TEMPLATE) * 4
r1[2] += r2[1]
r2[2] += r3[1]
r3[2] += r4[1]
```

This is the same thing using the new `&` operator:

```py
r1, r2, r3, r4 = Part('Device', 'R', dest=TEMPLATE) * 4
ser_ntwk = r1 & r2 & r3 & r4
```

![Serial Network]({{site.url}}/images/sweetening-skidl/ser_ntwk.png)

Here are four resistors wired in parallel:

```py
par_ntwk = r1 | r2 | r3 | r4
```

![Parallel Network]({{site.url}}/images/sweetening-skidl/par_ntwk.png)

Or you can do something like placing pairs of resistors in series and then paralleling
those combinations like this:

```py
combo_ntwk = (r1 & r2) | (r3 & r4)
```

![Parallel+Serial Network]({{site.url}}/images/sweetening-skidl/combo_ntwk.png)

In addition to connecting parts, the `&` and `|` operators also work with nets.
This lets you apply inputs and extract outputs by attaching nets to nodes in the network.
To illustrate, here's a simple resistor network that divides an input voltage
to generate an output voltage:

```py
vin, vout, gnd = Net('VI'), Net('VO'), Net('GND')
vdiv_ntwk = vin & r1 & vout & r2 & gnd
```

![Voltage-Divider Network]({{site.url}}/images/sweetening-skidl/vdiv_ntwk.png)

You could do the same thing using a single pin instead of a net.
Here's the voltage divider attached directly to a pin of a microcontroller:

```py
pic10 = Part('MCU_Microchip_PIC10', 'PIC10F320-IP')
pin_ntwk = vin & r1 & pic10['RA3'] & r2 & gnd
```

![Voltage-Divider Network for Microcontroller]({{site.url}}/images/sweetening-skidl/micro_ntwk.png)

The examples above work with *non-polarized* components, but what about *polarized* parts
like diodes and electrolytic capacitors? For those, you have to specify the 
pins *explicitly* with the first pin connected to the preceding part and the
second pin to the following part like so:

```py
vcc = Net('VCC')
d1 = Part('Device', 'D')
polar_ntwk = vcc & r1 & d1['A,K'] & gnd  # Diode anode connected to resistor and cathode to ground.
```

![Polar network]({{site.url}}/images/sweetening-skidl/polar_ntwk.png)

Explicitly listing the pins also lets you use multi-pin parts with networks.
For example, here's an NPN-transistor amplifier built using two networks:
one for the carrying the amplified current through the load resistor and
the transistor's collector and emitter, 
and another for applying the input to the base.

```py
inp, outp = Net('INPUT'), Net('OUTPUT')
q1 = Part('Device', 'Q_NPN_ECB')
ntwk_ce = vcc & r1 & outp & q1['C,E'] & gnd  # Connect net outp to the junction of the resistor and transistor collector.
ntwk_b = inp & r2 & q1['B']  # Connect net inp to the resistor driving the transistor base.
```

![Transistor Amplifier]({{site.url}}/images/sweetening-skidl/trans_ntwk.png)

Not all networks are composed of parts in series or parallel.
For example, here's a [*Pi matching network*](https://www.eeweb.com/tools/pi-match):

![Pi Matching Network]({{site.url}}/images/sweetening-skidl/pi_ntwk.png)

This could be described using the `tee()` function like so:

```py
inp, outp, gnd = Net('INPUT'), Net('OUTPUT'), Net('GND')
l1 = Part('Device', 'L')
c1, c2 = Part('Device', 'C', dest=TEMPLATE) * 2
pi_ntwk = inp & tee(c1 & gnd) & l1 & tee(c2 & gnd) & outp
```

The `tee` function takes any network as its argument and returns the first node of
that network to be connected into the higher-level network.
The network passed to `tee` can be arbitrarily complex, including any
combination of parts, `&`'s, `|`'s, and `tee`'s.


### Bussed Part Pins

Some parts have sequentially-numbered sets of pins, such as a RAM's address and data buses.
Previously, you had to explicitly list these pins to make connections like this:

```terminal
>>> databus = Bus('DATA', 8)
>>> ram = Part('Memory_RAM','AS6C1616')
>>> ram['DQ7,DQ6,DQ5,DQ4,DQ3,DQ2,DQ1,DQ0'] += databus[7:0]
>>> databus
DATA:
        DATA0: Pin U1/29/DQ0/BIDIRECTIONAL
        DATA1: Pin U1/31/DQ1/BIDIRECTIONAL
        DATA2: Pin U1/33/DQ2/BIDIRECTIONAL
        DATA3: Pin U1/35/DQ3/BIDIRECTIONAL
        DATA4: Pin U1/38/DQ4/BIDIRECTIONAL
        DATA5: Pin U1/40/DQ5/BIDIRECTIONAL
        DATA6: Pin U1/42/DQ6/BIDIRECTIONAL
        DATA7: Pin U1/44/DQ7/BIDIRECTIONAL
```

This is functional but tedious for large buses, so I introduced a
more compact notation to do the same thing:

```terminal
>>> ram['DQ[7:0]'] += databus[7:0]
>>> databus
DATA:
        DATA0: Pin U1/29/DQ0/BIDIRECTIONAL
        DATA1: Pin U1/31/DQ1/BIDIRECTIONAL
        DATA2: Pin U1/33/DQ2/BIDIRECTIONAL
        DATA3: Pin U1/35/DQ3/BIDIRECTIONAL
        DATA4: Pin U1/38/DQ4/BIDIRECTIONAL
        DATA5: Pin U1/40/DQ5/BIDIRECTIONAL
        DATA6: Pin U1/42/DQ6/BIDIRECTIONAL
        DATA7: Pin U1/44/DQ7/BIDIRECTIONAL
```


### Accessing Part Pins as Attributes

The standard syntax for accessing a part pin uses array index notation like this:

```terminal
>>> ram['DQ0'] += databus[0]
```

In order to slim this down, part pins can now also be referenced using their
names as attributes:

```terminal
>>> ram.DQ0 += databus[0]
```

Note that this works as long as the pin name is a legal attribute name (i.e., it begins
with an alpha character and contains only alphanumeric characters and the underscore).
If it's not, you'll have to use array indexing.

You can also use attribute references with pin *numbers* by prefixing the number
with `p`:

```terminal
>>> r = Part("Device", 'R')
>>> r

 R (): Resistor
    Pin R1/1/~/PASSIVE
    Pin R1/2/~/PASSIVE

>>> vcc = Net('VCC')
>>> r.p1 += vcc
>>> vcc
VCC: Pin R1/1/~/PASSIVE
```
