# SKiDL

[SKiDL](http://xesscorp.github.io/skidl) source code decoumentation.


## Description

[SKiDL](http://xesscorp.github.io/skidl) lets you create electronic circuits by writing Python scripts instead of using a schematic editor.
The `circuitsascode` auxiliary Python package gives you a library of ready-made electronic circuits that serves several purposes:

1. It provides a set of lower-level modules that you can integrate within your own designs.
1. It shows you examples of how to write SKiDL code.

## Installation

You can install this circuit library using `pip`:

```bash
pip install circuitsascode
```

## Usage

Just import the library to use a circuit module:

```py
import circuitsascode.vregs

vin, vout, gnd = Net("VIN"), Net("VOUT"), Net("GND")
vreg1 = circuitsascode.vregs.adj_reg(vin, vout, gnd, v_vout=3.3)
...
```
