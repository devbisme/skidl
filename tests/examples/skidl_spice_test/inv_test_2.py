import matplotlib.pyplot as plt

# from skidl import SKIDL, SPICE, TEMPLATE, Part, generate_netlist
from skidl.pyspice import *  # isort:skip


def test_inverters():

    sky_lib = SchLib(
        "/home/devb/tmp/skywater-pdk/libraries/sky130_fd_pr/latest/models/sky130.lib.spice",
        recurse=True,
        lib_section="tt",
    )

    nfet_wl = Parameters(W=1.26, L=0.15)
    pfet_wl = Parameters(W=1.26, L=0.15)

    pfet = Part(sky_lib, "sky130_fd_pr__pfet_01v8", params=pfet_wl, dest=TEMPLATE)
    nfet = Part(sky_lib, "sky130_fd_pr__nfet_01v8", params=nfet_wl, dest=TEMPLATE)

    @package
    def inverter(a=Net(), out=Net()):
        qp = pfet()
        qn = nfet()

        gnd & qn.b
        vdd & qp.b
        vdd & qp["s,d"] & out & qn["d,s"] & gnd
        a & qn.g & qp.g

    #############################################################################

    gnd = Net("0")
    vdd = Net("VDD")
    gnd & V(ref="VIN", dc_value=0.0 @ u_V)["n, p"] & Net("VIN") & Net("VOUT")
    generate_netlist()

    reset()

    gnd = Net("0")
    vdd = Net("VDD")
    a = Net("A")

    # Create a list of 30 inverters.
    invs = [inverter() for _ in range(5)]

    # Attach the square wave to the first inverter in the list.
    a & invs[0].a

    # Go through the list, attaching the input of each inverter to the output of the previous one.
    for i in range(1, len(invs)):
        invs[i - 1].out & invs[i].a

    # Attach the output of the last inverter to the output net.
    invs[-1].out & Net("A_DELAY")

    print(generate_netlist())


if __name__ == "__main__":
    test_inverters()
