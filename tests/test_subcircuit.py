import pytest
from skidl import *
from .setup_teardown import *

def test_subcircuit_1():

    class Resistor(Part):
        def __init__(self, value, ref=None, footprint='Resistors_SMD:R_0805'):
            super().__init__('device', 'R', value=value, ref=ref, footprint=footprint)

    @subcircuit
    def resdiv():
        gnd = Net('GND') # Ground reference.
        vin = Net('VI')  # Input voltage to the divider.
        vout = Net('VO')  # Output voltage from the divider.

        r1 = Resistor('1k')
        r2 = Resistor('500')

        cap = Part('device','C', dest=TEMPLATE)
        c1 = cap()
        c2 = cap(value='1uF')

        bus1 = Bus('BB',10)

        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    resdiv()
    resdiv()

    assert len(default_circuit.parts) == 8
    assert len(default_circuit.get_nets()) == 6
    assert len(default_circuit.buses) == 2

    ERC()
    generate_netlist()
    generate_xml()

def test_subcircuit_2():

    class Resistor(Part):
        def __init__(self, value, ref=None, footprint='Resistors_SMD:R_0805'):
            super().__init__('device', 'R', value=value, ref=ref, footprint=footprint)

    @subcircuit    
    def resdiv_1():
        gnd = Net('GND') # Ground reference.
        vin = Net('VI')  # Input voltage to the divider.
        vout = Net('VO')  # Output voltage from the divider.

        r1 = Resistor('1k')
        r2 = Resistor('500')

        cap = Part('device','C', dest=TEMPLATE)
        c1 = cap()
        c2 = cap(value='1uF')

        bus1 = Bus('BB',10)

        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    @subcircuit    
    def resdiv_2():
        resdiv_1()
        resdiv_1()

        a = Net('GND') # Ground reference.
        b = Net('VI')  # Input voltage to the divider.
        c = Net('VO')  # Output voltage from the divider.

        r1 = Resistor('1k')
        r2 = Resistor('500')

        cap = Part('device','C', dest=TEMPLATE)
        c1 = cap()
        c2 = cap(value='1uF')

        bus1 = Bus('BB',10)

        r1[1] += a  # Connect the input to the first resistor.
        r2[2] += b  # Connect the second resistor to ground.
        c += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    resdiv_2()

    assert len(default_circuit.parts) == 12
    assert len(default_circuit.get_nets()) == 9
    assert len(default_circuit.buses) == 3

    ERC()
    generate_netlist()
    generate_xml()
