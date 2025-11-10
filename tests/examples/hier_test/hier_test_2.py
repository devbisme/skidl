from skidl import *

def test_subcircuit_2():
    """Test nested subcircuit creation and connection."""
    class Resistor(Part):
        def __init__(self, value, ref=None, footprint="Resistors_SMD:R_0805"):
            super().__init__("Device", "R", value=value, ref=ref, footprint=footprint)

    @subcircuit
    def resdiv_1():
        """Create a resistor divider subcircuit with capacitors."""
        gnd = Net("GND")  # Ground reference.
        vin = Net("VI")  # Input voltage to the divider.
        vout = Net("VO")  # Output voltage from the divider.

        r1 = Resistor("1k")
        r2 = Resistor("500")

        cap = Part("Device", "C", dest=TEMPLATE)
        c1 = cap()
        c2 = cap(value="1uF")
        c1[1] += NC
        c2[1, 2] += NC

        bus1 = Bus("BB", 10)

        r1[1] += vin  # Connect the input to the first resistor.
        r2[2] += gnd  # Connect the second resistor to ground.
        vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    @subcircuit
    def resdiv_2():
        """Create a nested resistor divider subcircuit."""
        resdiv_1()
        resdiv_1()

        a = Net("GND")  # Ground reference.
        b = Net("VI")  # Input voltage to the divider.
        c = Net("VO")  # Output voltage from the divider.

        r1 = Resistor("1k")
        r2 = Resistor("500")

        cap = Part("Device", "C", dest=TEMPLATE)
        c1 = cap()
        c2 = cap(value="1uF")

        bus1 = Bus("BB", 10)

        r1[1] += a  # Connect the input to the first resistor.
        r2[2] += b  # Connect the second resistor to ground.
        c += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    # Create multiple circuits and add the nested subcircuit to them.
    default_circuit.name = "DEFAULT"
    circuit1 = Circuit(name="CIRCUIT1")
    circuit2 = Circuit(name="CIRCUIT2")
    resdiv_2(circuit=circuit2)
    resdiv_2()
    resdiv_2(circuit=circuit1)
    resdiv_2(circuit=circuit1)
    resdiv_2(circuit=circuit2)
    resdiv_2(circuit=circuit2)

    # Assert the number of parts, nets, buses, and NC pins in each circuit.
    assert len(default_circuit.parts) == 12
    assert len(default_circuit.get_nets()) == 9
    assert len(default_circuit.buses) == 3
    assert len(NC.pins) == 6

    assert len(circuit1.parts) == 24
    assert len(circuit1.get_nets()) == 18
    assert len(circuit1.buses) == 6
    assert len(circuit1.NC.pins) == 12

    assert len(circuit2.parts) == 36
    assert len(circuit2.get_nets()) == 27
    assert len(circuit2.buses) == 9
    assert len(circuit2.NC.pins) == 18

    # Perform ERC and generate netlist and XML for each circuit.
    ERC()
    generate_netlist()
    generate_xml()

    circuit1.ERC()
    circuit1.generate_netlist()
    circuit1.generate_xml()

    circuit2.ERC()
    circuit2.generate_netlist()
    circuit2.generate_xml()

test_subcircuit_2()
