from skidl import *
from skidl.pyspice import *

part_templates = {}
r_template = Part(
    "Device",
    "R",
    TEMPLATE,
    tool=KICAD,
    footprint="Resistor_SMD:R_0402_1005Metric",
)
r_spice = next(filter(lambda x: x.name == "R", pyspice_lib.parts))
r_template.convert_for_spice(r_spice, {1: "p", 2: "n"})
part_templates["R"] = r_template


@subcircuit
def circuit():
    vin, vout, gnd = Net("VI"), Net("VO"), Net("GND")

    r1, r2 = 2 * part_templates["R"]
    r1.value = "1K"  # Set upper resistor value.
    r2.value = "500"  # Set lower resistor value.

    vin += r1[1]  # Connect the input to the upper resistor.
    gnd += r2[2]  # Connect the lower resistor to ground.
    vout += r1[2], r2[1]  # Output comes from the connection of the two resistors.

    return Interface(vin=vin, vout=vout, gnd=gnd)


def test_sample():
    #   reset()
    sub_circuit = circuit()

    vs = Part("pyspice", "V", tool=SKIDL, ref="VS", dc_value=1 @ u_V)
    vs["p"] += sub_circuit["VI"]
    vs["n"] += sub_circuit["GND"]

    ERC()
    circ = generate_netlist(
        file="hyranno.net"
    )  # Generate the netlist, but don't write it to a file.


test_sample()
