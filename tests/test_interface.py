import pytest

from skidl import *

from .setup_teardown import *


def test_interface_1():
    """Test interface."""

    @subcircuit
    def resdiv(gnd, vin, vout):
        res = Part("Device", "R", dest=TEMPLATE)
        r1 = res(value="1k")
        r2 = res(value="500")

        cap = Part("Device", "C", dest=TEMPLATE)
        c1 = cap()
        c2 = cap(value="1uF")

        bus1 = Bus("BB", 10)

        vin += r1[1], c1[1]  # Connect the input to the first resistor.
        gnd += r2[2], c2[2]  # Connect the second resistor to ground.
        vout += (
            r1[2],
            c1[2],
            r2[1],
            c2[1],
        )  # Output comes from the connection of the two resistors.

    intfc = Interface(gnd=Net("GND"), vin=Net("VI"), vout=Net("VO"),)

    resdiv(**intfc)
    resdiv(**intfc)

    assert len(default_circuit.parts) == 8
    assert len(default_circuit.get_nets()) == 3
    assert len(default_circuit.buses) == 2

    assert len(Net.fetch("GND")) == 4
    assert len(Net.fetch("VI")) == 4
    assert len(Net.fetch("VO")) == 8

    assert len(intfc.gnd) == 4
    assert len(intfc.vin) == 4
    assert len(intfc.vout) == 8

    assert len(intfc["gnd"]) == 4
    assert len(intfc["vin"]) == 4
    assert len(intfc["vout"]) == 8

    intfc.gnd += Pin()
    intfc["vin"] += Pin()

    assert len(Net.fetch("GND")) == 5
    assert len(Net.fetch("VI")) == 5
    assert len(Net.fetch("VO")) == 8

    assert len(intfc.gnd) == 5
    assert len(intfc.vin) == 5
    assert len(intfc.vout) == 8

    assert len(intfc["gnd"]) == 5
    assert len(intfc["vin"]) == 5
    assert len(intfc["vout"]) == 8
