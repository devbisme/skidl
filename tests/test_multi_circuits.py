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

    circuit1 = Circuit()
    circuit2 = Circuit()
    resdiv(circuit=circuit2)
    resdiv()
    resdiv(circuit=circuit1)
    resdiv(circuit=circuit1)
    resdiv(circuit=circuit2)
    resdiv(circuit=circuit2)

    assert len(default_circuit.parts) == 4
    assert len(default_circuit._get_nets()) == 3
    assert len(default_circuit.buses) == 1

    assert len(circuit1.parts) == 8
    assert len(circuit1._get_nets()) == 6
    assert len(circuit1.buses) == 2

    assert len(circuit2.parts) == 12
    assert len(circuit2._get_nets()) == 9
    assert len(circuit2.buses) == 3

    ERC()
    generate_netlist()
    generate_xml()

    circuit1.ERC()
    circuit1.generate_netlist()
    circuit1.generate_xml()

    circuit2.ERC()
    circuit2.generate_netlist()
    circuit2.generate_xml()

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

    circuit1 = Circuit()
    circuit2 = Circuit()
    resdiv_2(circuit=circuit2)
    resdiv_2()
    resdiv_2(circuit=circuit1)
    resdiv_2(circuit=circuit1)
    resdiv_2(circuit=circuit2)
    resdiv_2(circuit=circuit2)

    assert len(default_circuit.parts) == 12
    assert len(default_circuit._get_nets()) == 9
    assert len(default_circuit.buses) == 3

    assert len(circuit1.parts) == 24
    assert len(circuit1._get_nets()) == 18
    assert len(circuit1.buses) == 6

    assert len(circuit2.parts) == 36
    assert len(circuit2._get_nets()) == 27
    assert len(circuit2.buses) == 9

    ERC()
    generate_netlist()
    generate_xml()

    circuit1.ERC()
    circuit1.generate_netlist()
    circuit1.generate_xml()

    circuit2.ERC()
    circuit2.generate_netlist()
    circuit2.generate_xml()

def test_circuit_add_rmv_1():
    circuit1 = Circuit()
    circuit2 = Circuit()
    r1 = Part('device','R')
    n1 = Net('N1')
    circuit1 += r1
    circuit1 += n1
    assert len(circuit1.parts) == 1
    assert len(circuit2.parts) == 0
    assert len(circuit1.nets) == 1
    assert len(circuit2.nets) == 0
    circuit2 += r1
    circuit2 += n1
    assert len(circuit1.parts) == 0
    assert len(circuit2.parts) == 1
    assert len(circuit1.nets) == 0
    assert len(circuit2.nets) == 1
    n1 += r1[1]
    with pytest.raises(Exception):
        circuit1 += r1

def test_circuit_connect_btwn_circuits_1():
    circuit1 = Circuit()
    circuit2 = Circuit()
    r1 = Part('device','R')
    n1 = Net('N1')
    circuit1 += r1
    circuit2 += n1
    with pytest.raises(Exception):
        n1 += r1[1]
