title: An Arduino With SKiDL
date: 2017-04-01
author: Dave Vandenbout
slug: an-arduino-with-skidl

It's April 1st. It's also [Arduino Day](https://day.arduino.cc/). Really. That's not a joke.

In honor of such an august occasion, I'm going to show you how to describe
an Arduino board using SKiDL.
It's really easy; just takes two steps:

1. Find an existing Arduino board designed using KiCad and export its netlist.
2. Use the `netlist_to_skidl` utility to convert it into a SKiDL file.

For step #1, I'm going to use the [Arduino Uno R3 design](https://github.com/rheingoldheavy/arduino_uno_r3_from_scratch) 
done by [Dan Hienzsch](http://www.rheingoldheavy.com/).
There are two great features of Dan's design:

* All the parts are heavily annotated with their manufacturers, part numbers, 
  descriptions, usage notes, etc.
* It's already done, which means I don't have to do it.

![A page of the Arduino schematic.](images/an-arduino-with-skidl/arduino-schematic.png)

After loading the Arduino project with KiCad, the netlist for the design
is exported by the Eeschema schematic editor using the `Tools => Generate Netlist File...`
menu command.
The netlist file is called `Arduino_Uno_R3_From_Scratch.net`.

Step #2 - converting the Arduino netlist into a SKiDL script - is even easier:

```bash
netlist_to_skidl -i Arduino_Uno_R3_From_Scratch.net`
``` 

That's it!
You can look inside `Arduino_Uno_R3_From_Scratch.py` and see the SKiDL code for the Arduino board.
It's divided into three sections:

* Definitions of *part templates*.
* Instantiations of the templates to create the actual parts in the design.
* Instantiations of *nets* to which the pins of the instantiated parts
  are attached to form connections.

For example, here is the definition of a template for a diode:

```py
device_D = Part("Device", 'D', dest=TEMPLATE)
setattr(device_D, 'Characteristics', 'DIODE GEN PURP 100V 300MA SOD123')
setattr(device_D, 'Description', 'ATMEGA328P ICSP Reset Voltage Spike Protection')
setattr(device_D, 'MFN', 'Diodes Inc')
setattr(device_D, 'MFP', '1N4148W-7-F')
setattr(device_D, 'Package ID', 'SOD123')
setattr(device_D, 'Source', 'ANY')
setattr(device_D, 'Critical', 'N')
setattr(device_D, 'Subsystem', '328P_Sub')
```

Further down in the script, this template is instantiated three times to create
three different parts, each with slightly different characteristics:

```py
D1 = device_D(ref='D1', value='DIODE')
setattr(D1, 'Characteristics', '1A, 1000V, SILICON, SIGNAL DIODE, ROHS COMPLIANT, COMPACT, PLASTIC, CASE 403D-02, SMA, 2 PIN')
setattr(D1, 'Description', 'Reverse Voltage Protection Diode')
setattr(D1, 'MFN', 'ON Semi')
setattr(D1, 'MFP', 'MRA4007T3G')
setattr(D1, 'Package ID', 'R-PDSO-J2')
setattr(D1, 'Subsystem', 'Voltage_Reg')

D4 = device_D(ref='D4', value='1N4148W-7-F')
setattr(D4, 'Description', 'ATMEGA16U2 ICSP Reset Voltage Spike Protection')
setattr(D4, 'Subsystem', '16U2_Sub')

D7 = device_D(ref='D7', value='1N4148W-7-F')
```

Finally, connections of these diodes to nets are defined:

```py
net__32 = Net('Vin')
net__32 += C1['1'], P1['8'], D1['1'], R2['2'], U1['3']

net__29 = Net('5V_LDO')
net__29 += C4['2'], U4['32'], C9['1'], U4['4'], U5['20'], U5['7'], C5['1'], U3['3'], Q1['2'], C15['1'], R16['2'], D7['2'], U3['1'], ICSP2['2'], U2['8'], ICSP1['2'], R11['2'], R10['2'], R7['2'], P1['2'], P1['5'], R1['2'], C2['1'], C3['1'], D4['2'], U1['2']

net__33 = Net('Net-(CON1-Pad2)')
net__33 += CON1['3'], CON1['2'], D1['2']

net__54 = Net('Net-(D4-Pad1)')
net__54 += D4['1'], U4['24'], ICSP1['5'], R7['1']

net__5 = Net('/ATMEGA328P/328P_RESET')
net__5 += D7['1'], U5['1'], SW1['4'], P1['3'], R16['1'], R13['2'], SW1['3'], ICSP2['5']
```

You can see the entire Arduino SKiDL script [here](https://gist.github.com/xesscorp/00d48e7ee31fedad00d6b07b9ddd0189).

Once the SKiDL script is available, you can execute it to create the netlist
for an Arduino and then create the PCB using KiCad's `PCBNEW` layout editor.
Or use the SKiDL code as a module in a larger design.

So that's a complete Arduino in SKiDL.
Happy Arduino Day!

Really. I'm not joking.
