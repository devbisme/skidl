# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2022 Dave Vandenbout.

from builtins import super

import pytest

from skidl import ERC, Net, Part, PartTmplt, erc_logger, generate_netlist, PartClass, SubCircuit
from skidl.utilities import to_list, Rgx


def test_part_1():
    """Test connecting all part pins to a net."""
    vreg = Part("Regulator_Linear", "AP1117-ADJ")
    n = Net()
    # Connect all the part pins to a net...
    for pin in vreg:
        n += pin
    # Then see if the number of pins on the net equals the number of part pins.
    assert len(n) == len(vreg)


def test_part_2():
    """Test getting parts by reference."""
    vreg = Part("Regulator_Linear", "AP1117-ADJ")
    r = Part("Device", "R")
    # Get parts by reference and check their count.
    parts = to_list(Part.get("u1"))
    assert len(parts) == 1
    parts = to_list(Part.get("AP1117-ADJ"))
    assert len(parts) == 1
    parts = to_list(Part.get(".*"))
    assert len(parts) == 2


def test_part_3():
    """Test part reference assignment."""
    r = Part("Device", "R", ref=None)
    # Check if the reference is assigned correctly.
    assert r.ref == "R1"


def test_part_unit_1():
    """Test creating units within a part."""
    vreg = Part("Regulator_Linear", "AP1117-ADJ")
    vreg.match_pin_regex = True
    # Create units within the part.
    vreg.make_unit("A", 1, 2)
    vreg.make_unit("B", 3)
    assert len(vreg.unit["A"][".*"]) == 2
    assert len((vreg.unit["B"][".*"],)) == 1


def test_part_unit_2():
    """Test creating units with overlapping pins."""
    vreg = Part("Regulator_Linear", "AP1117-ADJ")
    # Create units with overlapping pins.
    vreg.make_unit("A", 1, 2)
    vreg.make_unit("A", 3)
    assert len((vreg.unit["A"][".*"],)) == 1


def test_part_unit_3():
    """Test creating a unit with specific pins."""
    vreg = Part("Regulator_Linear", "AP1117-ADJ")
    # Create a unit with specific pins.
    vreg.make_unit("1", 1, 2)


def test_part_unit_4():
    """Test wildcard pin matching in units."""
    mem = Part("Memory_RAM", "AS4C4M16SA")
    mem.match_pin_regex = True
    # Match pins using wildcard.
    data_pin_names = [p.name for p in mem[".*DQ[0:15].*"]]
    mem.make_unit("A", data_pin_names)
    # Wildcard pin matching OFF globally.
    mem.match_pin_regex = False
    assert mem[".*"] == None
    assert mem.A[".*"] == None
    assert len(mem[Rgx(".*")]) == len(mem[:])
    assert len(mem.A[Rgx(".*")]) == 16
    # Wildcard pin matching ON globally.
    mem.match_pin_regex = True
    assert len(mem[".*"]) != 0
    assert len(mem.A[".*"]) == 16
    assert len(mem[Rgx(".*")]) == len(mem[:])
    assert len(mem.A[Rgx(".*")]) == 16
    # Wildcard matching OFF for part unit, but ON globally.
    mem.A.match_pin_regex = False
    assert len(mem[".*"]) != 0
    assert mem.A[".*"] == None


def test_part_unit_5():
    """Test if the number of pins in units sum to the total number of pins in the part."""
    hdr = Part("4xxx", "4001")
    # Check if the number of pins in units sum to the total number of pins in the part.
    assert len(hdr) == sum([len(u) for u in hdr.unit.values()])


def test_part_tmplt_1():
    """Test creating parts from a template."""
    rt = PartTmplt("Device", "R", value=1000)
    # Create parts from a template.
    r1, r2 = rt(num_copies=2)
    assert r1.ref == "R1"
    assert r2.ref == "R2"
    assert r1.value == 1000
    assert r2.value == 1000


def test_index_slicing_1():
    """Test pin indexing and slicing."""
    mcu = Part("MCU_STC", "STC15W204S-35x-SOP16", pin_splitters="/()")
    mcu.match_pin_regex = False
    # Test pin indexing and slicing.
    assert len(mcu["T[0:9]"]) == 2
    assert len(mcu["INT[0:9]"]) == 2
    assert len(mcu[Rgx("T[0:9]")]) == 2
    assert len(mcu[Rgx("INT[9:0]")]) == 2
    assert len(mcu[Rgx(r".*CLKO.*")]) == 3
    assert len(mcu[Rgx(".*[T0|M|T2]CLKO.*")]) == 3
    mcu.match_pin_regex = True
    assert len(mcu[r".*CLKO.*"]) == 3
    assert len(mcu[r".*[0:9]CLKO.*"]) == 2
    assert len(mcu[r".*[9:0]CLKO.*"]) == 2
    assert len(mcu[r".*CLKO.*"]) == 3
    assert len(mcu[r".*[T0|M|T2]CLKO.*"]) == 3


def test_index_slicing_2():
    """Test pin indexing and slicing with memory part."""
    mem = Part("Memory_RAM", "AS4C4M16SA")
    mem.match_pin_regex = False
    # Test pin indexing and slicing with memory part.
    assert len(mem["DQ[0:15]"]) == 16
    assert len(mem["DQ[15:0]"]) == 16
    assert len(mem["A[0:15]"]) == 11
    assert len(mem["BA[0:15]"]) == 2
    assert len(mem[Rgx("DQ[0:15]")]) == 16
    assert len(mem[Rgx("DQ[15:0]")]) == 16
    assert len(mem[Rgx("A[0:15]")]) == 11
    assert len(mem[Rgx("BA[0:15]")]) == 2
    mem.match_pin_regex = True
    assert len(mem["^A[0:15]"]) == 11
    assert len(mem[Rgx("^A[0:15]")]) == 11


def test_string_indices_1():
    """Test connecting part pins using string indices."""
    vreg1 = Part("Regulator_Linear", "LT1117-3.3")
    r1 = Part("Device", "R")
    gnd = Net("GND")
    vin = Net("Vin")
    # Connect part pins using string indices.
    vreg1["GND, VI, VO"] += gnd, vin, r1.p1
    assert vreg1.is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vreg1["VI"].net) == 1
    assert len(r1.p1.net) == 2
    assert len(vreg1["VO"].net) == 2
    assert vreg1["VO"].net.is_attached(r1.p1.net)


def test_part_ref_prefix():
    """Test setting a custom reference prefix for a part."""
    c = Part("Device", "C", ref_prefix="test")
    # Set a custom reference prefix for a part.
    assert c.ref == "test1"


def test_subclass_1():
    """Test creating a subclass of Part."""
    class Resistor(Part):
        def __init__(self, value, ref=None, footprint="Resistors_SMD:R_0805"):
            super().__init__("Device", "R", value=value, ref=ref, footprint=footprint)

    gnd = Net("GND")  # Ground reference.
    vin = Net("VI")  # Input voltage to the divider.
    vout = Net("VO")  # Output voltage from the divider.

    r1 = Resistor("1k")
    r2 = Resistor("500")

    # Connect the input to the first resistor.
    r1[1] += vin
    # Connect the second resistor to ground.
    r2[2] += gnd
    # Output comes from the connection of the two resistors.
    vout += r1[2], r2[1]

    ERC()
    generate_netlist()


def test_subclass_2():
    """Test creating a custom subclass of Part."""
    class CustomPart(Part):
        pass

    r1 = Part("Device", "R")
    r2 = CustomPart("Device", "R")
    # Make a connection so resistors don't get culled.
    r1 & r2

    ERC()
    assert erc_logger.warning.count == 2


def test_alias_rename():
    """Test alias and renaming of parts."""
    u1 = Part("Amplifier_Operational", "LT1493")
    u2 = Part("Amplifier_Operational", "LTC6082xGN")
    # Check alias and renaming of parts.
    assert u1.name == "LT1493"
    assert u1.value == "LT1493"
    assert u2.name == "LTC6082xGN"
    assert u2.value == "LTC6082xGN"
    assert len(u1.get_pins()) == len(u2.get_pins())


def test_partclass_1():
    """Test assigning partclass to a part."""
    led = Part("Device", "LED_ARBG")
    led.partclasses = PartClass("my_part", a=1, b=2, c=3, priority=1)  # Assign part class.
    assert "my_part" in led.partclasses  # Check part class name.
    assert led.partclasses["my_part"].a == 1  # Check part class attribute 'a'.


def test_partclass_2():
    """Test reassigning partclass to a part."""
    led = Part("Device", "LED_ARBG")
    led.partclasses = PartClass("my_part", a=1, b=2, c=3, priority=2)  # Assign part class.
    with pytest.raises(ValueError):
        led.partclasses = PartClass("my_part", a=5, b=6, c=7, priority=1)  # Reassign part class should raise error.


def test_netclass_3():
    """Test partclass priority sorting."""
    led = Part("Device", "LED_ARBG")
    led.partclasses = PartClass("class1", priority=1)  # Adding another partclass.
    led.partclasses = PartClass("class2", priority=2)  # Adding another partclass.
    prioritized_names = led.partclasses.by_priority()  # Sort partclasses by priority.
    assert prioritized_names[-1] == "class2"  # Last netclass should be 'class2'.
    assert prioritized_names[-2] == "class1"  # First netclass should be 'class1'.
    partclasses = led.circuit.partclasses[prioritized_names]
    assert partclasses[-1].priority == 2
    assert partclasses[-2].priority == 1


def test_partclass_4():
    """Test partclass single and multiple indexing."""
    led = Part("Device", "LED_ARBG")
    led.partclasses = PartClass("class1", priority=1)  # Adding another partclass.
    led.partclass = PartClass("class2", priority=2)  # Adding another partclass.
    partclass = led.circuit.partclasses["class1"]
    assert partclass.priority == 1
    partclasses = led.circuit.partclasses["class1", "class2"]
    assert partclasses[0].priority == 1
    assert partclasses[1].priority == 2


def test_partclass_5():
    """Test partclass duplication."""
    led = Part("Device", "LED_ARBG")
    prtcls1 = PartClass("class1", priority=1)
    PartClass("class1", priority=1)  # Part class with same name and same attributes doesn't raise error.
    led.partclasses = prtcls1
    led.partclasses = prtcls1  # Reassigning should be ignored and not raise error.
    with pytest.raises(ValueError):
        PartClass("class1", priority=2)  # Part class with same name but different attributes should raise error.


def test_partclass_6():
    """Test partclass multiple assignment."""
    led = Part("Device", "LED_ARBG")
    led.partclasses = PartClass("class1", priority=1), PartClass("class2", priority=2)
    assert "class1" in led.partclasses
    assert "class2" in led.partclasses

def test_partclass_7():
    """Test partclass for part surrounded by hierarchical part classes."""
    # Create a hierarchical part class.
    with SubCircuit("lvl0", partclasses=PartClass("class1",priority=1)):
        with SubCircuit("lvl1"):
            with SubCircuit("lvl2", partclasses=PartClass("class3",priority=3)):
                led = Part("Device", "LED_ARBG")
                led.partclasses = PartClass("class2", priority=2)
                partclasses = led.partclasses.by_priority()
                assert partclasses[0] == "class1"
                assert partclasses[1] == "class2"
                assert partclasses[2] == "class3"
