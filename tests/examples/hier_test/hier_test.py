from skidl import *

def test_interface_12():
    """Test nested subcircuits with fixed nets."""
    r = Part("Device", "R", dest=TEMPLATE)
    c = Part("Device", "C", dest=TEMPLATE)

    @subcircuit
    def sub1():
        # Create nets
        my_vin, my_gnd = Net(), Net()
        # Create resistor and capacitor
        r1 = r(tag="r1")
        c1 = c(tag="c1")
        # Connect resistor and capacitor between input and ground
        my_vin & r1 & c1 & my_gnd
        return Interface(my_vin=my_vin, my_gnd=my_gnd)

    @subcircuit
    def sub2(my_vin1, my_vin2, my_gnd):
        # Instantiate subcircuits
        s1 = sub1(tag="s1")
        s2 = sub1(tag="s2")
        # Connect the subcircuits to the nets
        s1.my_vin += my_vin1
        my_vin2 += s2.my_vin
        my_gnd += s1.my_gnd
        s2.my_gnd += my_gnd

    # Create nets
    vin1, vin2, gnd = Net("VIN1"), Net("VIN2"), Net("GND")
    # Instantiate the subcircuit
    sub = sub2(vin1, vin2, gnd, tag="sub")
    # Create resistor and connect between input and ground
    r1 = r()
    vin1 & r1 & gnd

    # Assertions to verify the circuit
    assert len(gnd) == 3
    assert len(vin1) == 2
    assert len(vin2) == 1

    hierarchy = default_circuit.active_node.to_tuple()
    hierarchy2 = default_circuit.active_node.to_tuple()
    assert str(hierarchy) == str(hierarchy2)
    print(str(default_circuit.active_node))
    breakpoint()

test_interface_12()
