# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2022 Dave Vandenbout.

from builtins import super

from skidl import ERC, Net, Part, PartTmplt, erc_logger, generate_netlist
from skidl.utilities import to_list, Rgx

from .setup_teardown import setup_function, teardown_function


def test_part_1():
    vreg = Part("Regulator_Linear", "AP1117-ADJ")
    n = Net()
    # Connect all the part pins to a net...
    for pin in vreg:
        n += pin
    # Then see if the number of pins on the net equals the number of part pins.
    assert len(n) == len(vreg)


def test_part_2():
    vreg = Part("Regulator_Linear", "AP1117-ADJ")
    codec = Part("Device", "R")
    parts = to_list(Part.get("u1"))
    assert len(parts) == 1
    parts = to_list(Part.get("AP1117-ADJ"))
    assert len(parts) == 1
    parts = to_list(Part.get(".*"))
    assert len(parts) == 2


def test_part_3():
    r = Part("Device", "R", ref=None)
    assert r.ref == "R1"


def test_part_unit_1():
    vreg = Part("Regulator_Linear", "AP1117-ADJ")
    vreg.match_pin_regex = True
    vreg.make_unit("A", 1, 2)
    vreg.make_unit("B", 3)
    assert len(vreg.unit["A"][".*"]) == 2
    assert len((vreg.unit["B"][".*"],)) == 1


def test_part_unit_2():
    vreg = Part("Regulator_Linear", "AP1117-ADJ")
    vreg.make_unit("A", 1, 2)
    vreg.make_unit("A", 3)
    assert len((vreg.unit["A"][".*"],)) == 1


def test_part_unit_3():
    vreg = Part("Regulator_Linear", "AP1117-ADJ")
    vreg.make_unit("1", 1, 2)


def test_part_unit_4():
    mem = Part("Memory_RAM", "AS4C4M16SA")
    mem.match_pin_regex = True
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
    # Test if #pins in units sum to the total #pins in part.
    hdr = Part("4xxx", "4001")
    assert len(hdr) == sum([len(u) for u in hdr.unit.values()])


def test_part_tmplt_1():
    rt = PartTmplt("Device", "R", value=1000)
    r1, r2 = rt(num_copies=2)
    assert r1.ref == "R1"
    assert r2.ref == "R2"
    assert r1.value == 1000
    assert r2.value == 1000


def test_index_slicing_1():
    mcu = Part("MCU_STC", "STC15W204S-35x-SOP16", pin_splitters="/()")
    mcu.match_pin_regex = False
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
    mem = Part("Memory_RAM", "AS4C4M16SA")
    mem.match_pin_regex = False
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
    vreg1 = Part("Regulator_Linear", "LT1117-3.3")
    r1 = Part("Device", "R")
    gnd = Net("GND")
    vin = Net("Vin")
    vreg1["GND, VI, VO"] += gnd, vin, r1.p1
    assert vreg1.is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vreg1["VI"].net) == 1
    assert len(r1.p1.net) == 2
    assert len(vreg1["VO"].net) == 2
    assert vreg1["VO"].net.is_attached(r1.p1.net)


def test_part_ref_prefix():
    c = Part("Device", "C", ref_prefix="test")
    assert c.ref == "test1"


def test_subclass_1():
    class Resistor(Part):
        def __init__(self, value, ref=None, footprint="Resistors_SMD:R_0805"):
            super().__init__("Device", "R", value=value, ref=ref, footprint=footprint)

    gnd = Net("GND")  # Ground reference.
    vin = Net("VI")  # Input voltage to the divider.
    vout = Net("VO")  # Output voltage from the divider.

    r1 = Resistor("1k")
    r2 = Resistor("500")

    r1[1] += vin  # Connect the input to the first resistor.
    r2[2] += gnd  # Connect the second resistor to ground.
    vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    ERC()
    generate_netlist()


def test_subclass_2():
    class CustomPart(Part):
        pass

    r1 = Part("Device", "R")
    r2 = CustomPart("Device", "R")
    r1 & r2  # Make a connection so resistors don't get culled.

    ERC()
    assert erc_logger.warning.count == 2

def test_alias_rename():
    u1 = Part("Amplifier_Operational", "LT1493")
    u2 = Part("Amplifier_Operational", "LTC6082xGN")
    assert u1.name=="LT1493"
    assert u1.value=="LT1493"
    assert u2.name=="LTC6082xGN"
    assert u2.value=="LTC6082xGN"
    assert len(u1.get_pins()) == len(u2.get_pins())

