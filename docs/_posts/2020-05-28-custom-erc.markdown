---
layout: post
title: Customized ERC!
date: 2020-05-29T10:01:10-05:00
author:
    name: Dave Vandenbout
    photo: devb-pic.jpg
    email: devb@xess.com
    description: Relax, I do this stuff for a living.
category: blog
permalink: blog/custom-erc
---

Everybody wants ERC. Everybody hates ERC.

Electrical rules checking (ERC) looks for errors in how your circuit is constructed.
It's like running [`lint`](https://en.wikipedia.org/wiki/Lint_(software)), but for hardware.
And as with `lint`, you get a whole bunch of warnings that don't matter but which
*obscure the ones that do*.

SKiDL tries to help by allowing you to
[selectively turn off ERC](https://xesscorp.github.io/skidl/docs/_site/index.html#selectively-supressing-erc-messages)
for nets, pins, and parts.
That fixes part of the problem.

The other part is the inflexibility of ERC: it has fixed rules for common errors
(like two outputs driving against each other), but adding rules for special cases
isn't easy.

The `erc_assert()` function was added to SKiDL to make customizing ERC easier.
With `erc_assert()`, you can add specialized rules that are checked only
in particular instances.
In the example below, `erc_assert()` is used to
flag nets that have too much fanout:

```py
from skidl import *

# Function to get the number of inputs on a net.
def get_fanout(net):
    fanout = 0
    for pin in net.get_pins():
        if pin.func in (Pin.INPUT, Pin.BIDIR):
            fanout += 1
    return fanout

net1, net2 = Net('IN1'), Net('IN2')

# Place some assertions on the fanout of each net.
# Note that the assertions are passed as strings.
erc_assert('get_fanout(net1) < 5', 'failed on net1')
erc_assert('get_fanout(net2) < 5', 'failed on net2')

# Attach some pins to the nets.
net1 += Pin(func=Pin.OUTPUT)
net2 += Pin(func=Pin.OUTPUT)
net1 += Pin(func=Pin.INPUT) * 4  # This net passes the assertion.
net2 += Pin(func=Pin.INPUT) * 5  # This net fails because of too much fanout.

# When the ERC runs, it will also evaluate any erc_assert statements.
ERC()
```
```terminal
ERC ERROR: get_fanout(net2) < 5 failed on net2 in <ipython-input-20-766848d35dca>:16:<module>.

0 warnings found during ERC.
1 errors found during ERC.
```

You might ask: “Why not just use the standard Python `assert` statement?”
The reason is that a standard assertion is evaluated as soon as the `assert` statement
is encountered so the result might be incorrect if the nets
are not yet completely defined.
But the statement passed to the `erc_assert()` function is a **string** that
isn’t evaluated until all the circuitry has been connected and ERC() is called.
Note in the code above that when the `erc_assert()` function is called,
no pins are even attached to the `net1` or `net2` nets.
The `erc_assert()` function just places the statement to be checked into
a queue that gets evaluated when `ERC()` is run.
By then, the nets will have pins attached by then.

You can perform more complicated checks by creating a function and then placing a call
to it in the assertion string:

```py
from skidl import *

def get_fanout(net):
    fanout = 0
    for pin in net.get_pins():
        if pin.func in (Pin.INPUT, Pin.BIDIR):
            fanout += 1
    return fanout

# Function to check a fanout constraint on a net and drop into
# the debugger if the constraint is violated.
def check_fanout(net, threshold):
    fanout = get_fanout(net)
    if fanout >= threshold:
        # Report the net which violated the constraint."
        print(f'{net.name} fanout of {fanout} >= {threshold}.')

        # Drop into the debugger so you can query the circuit
        # and then continue.
        breakpoint()

        return False  # Return False to trigger the erc_assert().

    return True  # Return True if the constraint is not violated.

net1, net2 = Net('IN1'), Net('IN2')

# Place calls to the check_fanout() function into the assertions.
erc_assert('check_fanout(net1, 5)')
erc_assert('check_fanout(net2, 5)')

net1 += Pin(func=Pin.OUTPUT)
net2 += Pin(func=Pin.OUTPUT)
net1 += Pin(func=Pin.INPUT) * 4
net2 += Pin(func=Pin.INPUT) * 5

ERC()
```
```terminal
IN2 fanout of 5 >= 5.
> <ipython-input-18-800a83e11624>(22)check_fanout()
-> return False  # Return False to trigger the erc_assert().
(Pdb) c
ERC ERROR: check_fanout(net2, 5) FAILED in <ipython-input-18-800a83e11624>:30:<module>.

0 warnings found during ERC.
1 errors found during ERC.
```

You can detect if a subcircuit is being used correctly by embedding calls to
`erc_assert()` to check inputs, outputs, and internal circuitry:

```py
from skidl import *

# Return True if the net has a pullup on it, False if not.
def has_pullup(net):
    for pin in net.get_pins():
        if pin.func == Pin.PULLUP:
            return True

    print(f'No pullup on net {net.name}')
    return False

@subcircuit
def some_circuit(in1, in2):
    # Check the subcircuit inputs to see if they have pullups.
    erc_assert('has_pullup(in1)')
    erc_assert('has_pullup(in2)')

    # OK, this subcircuit doesn't really do anything, so you'll
    # just have to imagine that it did.
    pass

net1, net2 = Net('IN1'), Net('IN2')

# Instantiating the subcircuit automatically checks the input nets.
some_circuit(net1, net2)

net1 += Pin(func=Pin.OUTPUT)
net1 += Pin(func=Pin.INPUT)  # No pullup -> this net fails.
net2 += Pin(func=Pin.OUTPUT)
net2 += Pin(func=Pin.PULLUP)

ERC()
```
```terminal
No pullup on net IN1
ERC ERROR: has_pullup(in1) FAILED in <ipython-input-16-6e72ef7d46c8>:15:some_circuit.

0 warnings found during ERC.
1 errors found during ERC.
```

You can even use the `erc_assert()` function to add global checks
that scan the entire circuit for violations of custom rules:

```py
from skidl import *

# Global function that checks all the nets in the circuit and
# flags nets which have pullups when they shouldn't.
def my_erc():
    erc_result = True
    for net in default_circuit.get_nets():
        if getattr(net, 'disallow_pullups', False) == True:
            pin_types = [pin.func for pin in net.get_pins()]
            if Pin.PULLUP in pin_types:
                print(f'Pull-up not allowed on {net.name}.')
            erc_result = False
    return erc_result

net1, net2 = Net('IN1'), Net('IN2')

net1.disallow_pullups = True  # Don't allow pullups on this net.
net1 += Pin(func=Pin.INPUT)
net1 += Pin(func=Pin.PULLUP) # This net will fail ERC. 
net2 += Pin(func=Pin.INPUT)
net2 += Pin(func=Pin.PULLUP)

# Call your own customized global ERC.
erc_assert('my_erc()')

ERC()
```
```terminal
Pull-up not allowed on IN1.
ERC ERROR: my_erc() FAILED in <ipython-input-12-888102e7799c>:24:<module>.

0 warnings found during ERC.
1 errors found during ERC.
```

That's about it for the `erc_assert()` function.
Since it's new, it hasn't seen a lot of use so there could be
modifications that are needed to make it more useful.
If you have questions or problems, please ask on the
[SKiDL forum](https://skidl.discourse.group/) or
raise an [issue](https://github.com/xesscorp/skidl/issues). 
