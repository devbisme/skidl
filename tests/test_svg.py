import pytest

from skidl import *

from .setup_teardown import *


def test_svg_1():
    """Test SVG generation."""

    l1 = Part("Device", "L")
    r1, r2 = Part("Device", "R", dest=TEMPLATE, value="200.0") * 2
    q1 = Part("Device", "Q_NPN_CBE")
    c1 = Part("Device", "C", value="10pF")
    r3 = r2(value="1K")
    vcc, vin, vout, gnd = Net("VCC"), Net("VIN"), Net("VOUT"), Net("GND")
    vcc & r1 & vin & r2 & gnd
    vcc & r3 & vout & q1["C,E"] & gnd
    q1["B"] += vin
    vout & (l1 | c1) & gnd
    rly = Part("Relay", "TE_PCH-1xxx2M")
    rly[1, 2, 3, 5] += gnd
    led = Part("Device", "LED_ARGB", symtx="RH")
    r, g, b = Net("R"), Net("G"), Net("B")
    led["A,RK,GK,BK"] += vcc, r, g, b
    Part(lib="MCU_Microchip_PIC10.lib", name="PIC10F200-IMC")

    generate_svg(file_="test1")


def test_svg_2():
    opamp = Part(lib="Amplifier_Operational.lib", name="AD8676xR", symtx="V")
    opamp.uA.p2 += Net("IN1")
    opamp.uA.p3 += Net("IN2")
    opamp.uA.p1 += Net("OUT")
    opamp.uB.symtx = "L"

    generate_svg(file_="test2")


def test_svg_3():
    gnd = Part("power", "GND")
    vcc = Part("power", "VCC")

    opamp = Part(lib="Amplifier_Operational.lib", name="AD8676xR", symtx="V")

    for part in default_circuit.parts:
        part.validate()

    vcc[1] += opamp[8]
    gnd[1] += opamp[4]

    r = Part("Device", "R_US", dest=TEMPLATE, tx_ops="L")

    Net("IN") & r(value="4K7", symtx="L") & opamp.uA[2] & r(
        value="4K7", symtx="L"
    ) & opamp.uA[1]
    gnd[1] += opamp.uA[3]

    opamp.uA[1] & r(value="10K") & gnd[1]

    for part in default_circuit.parts:
        part.validate()

    generate_svg()

    for part in default_circuit.parts:
        part.validate()

    return

    # The rest uses arrange.py stuff. Left in just for documentation purposes.

    w, h = 5, 5
    arr = best_arr = Arranger(default_circuit, w, h)
    # best_arr.prearranged()
    best_arr.arrange_randomly()
    best_cost = best_arr.cost()
    # print(f"starting cost = {best_cost}")
    # import sys
    # sys.exit()

    for _ in range(1):
        arr.arrange_randomly()
        arr.arrange_kl()
        cost = arr.cost()
        if cost < best_cost:
            best_arr = arr
            best_cost = cost
            print("///// Best arrangement cost = {best_cost:2.2f} /////".format(**locals()))
            arr = Arranger(default_circuit, w, h)

    best_arr.apply()
    for part in best_arr.parts:
        print("{part.ref:5s} {part.region.x} {part.region.y}".format(**locals()))
    print("cost = {best_arr.cost()}".format(**locals()))


def test_svg_4():
    q = Part(lib="Device.lib", name="Q_PNP_CBE", dest=TEMPLATE, symtx="V")
    r = Part("Device", "R", dest=TEMPLATE)
    gndt = Part("power", "GND")
    vcct = Part("power", "VCC")

    gnd = Net("GND")
    vcc = Net("VCC")
    gnd & gndt
    vcc & vcct
    a = Net("A", netio="i")
    b = Net("B", netio="i")
    a_and_b = Net("A_AND_B", netio="o")
    q1 = q()
    q1.E.symio = "i"
    q1.B.symio = "i"
    q1.C.symio = "o"
    q2 = q()
    q2.E.symio = "i"
    q2.B.symio = "i"
    q2.C.symio = "o"
    r1, r2, r3, r4, r5 = r(5, value="10K")
    a & r1 & q1["B", "C"] & r4 & q2["B", "C"] & a_and_b & r5 & gnd
    b & r2 & q1["B"]
    q1["C"] & r3 & gnd
    vcc & q1["E"]
    vcc & q2["E"]

    generate_svg()
    generate_netlist()
    return

    # The rest uses arrange.py stuff. Left in just for documentation purposes.

    arr = best_arr = Arranger(default_circuit, 3, 3)
    # best_arr.prearranged()
    best_arr.arrange_randomly()
    best_cost = best_arr.cost()
    # print(f"starting cost = {best_cost}")
    # import sys
    # sys.exit()

    for _ in range(50):
        arr.arrange_randomly()
        arr.arrange_kl()
        cost = arr.cost()
        if cost < best_cost:
            best_arr = arr
            best_cost = cost
            print("///// Best arrangement cost = {best_cost:2.2f} /////".format(**locals()))
            arr = Arranger(default_circuit, 3, 3)

    best_arr.apply()
    for part in default_circuit.parts:
        print("{part.ref:5s} {part.region.x} {part.region.y}".format(**locals()))
    print("cost = {best_arr.cost()}".format(**locals()))

    best_arr.expand_grid(3, 3)
    arr = best_arr
    for _ in range(50):
        arr.arrange_randomly()
        arr.arrange_kl()
        cost = arr.cost()
        if cost < best_cost:
            best_arr = arr
            best_cost = cost
            print("///// Best arrangement cost = {best_cost:2.2f} /////".format(**locals()))
            arr = Arranger(default_circuit, 3, 3)

    best_arr.apply()
    for part in default_circuit.parts:
        print("{part.ref:5s} {part.region.x} {part.region.y}".format(**locals()))
    print("cost = {best_arr.cost()}".format(**locals()))


def test_svg_5():

    lib_search_paths[KICAD].append("/home/devb/xesscorp/KiCad/libraries")
    uc = Part(lib="wch.lib", name="CH551G", dest=TEMPLATE)
    uc.split_pin_names("/")
    usb = Part(lib="Connector.lib", name="USB_B_Micro", symtx="H")

    uc1 = uc()
    uc1["UDM, UDP"] += usb["D-, D+"]

    uc_spare = uc()
    uc_spare["UDP"] & uc_spare["UDM"]

    stubs = uc1["UDM"].get_nets()
    stubs.extend(uc1["UDP"].get_nets())

    generate_svg(net_stubs=stubs)


def test_svg_6():
    r = Part("Device", "R", dest=TEMPLATE)
    gndt = Part("power", "GND")
    vcct = Part("power", "VCC")

    gnd = Net("GND")
    vcc = Net("VCC")
    gnd & gndt & r() & r() & (
        r(symtx="l") | r(symtx="R")
    ) & r() & r() & r() & r() & r() & r() & r() & vcct & vcc

    generate_svg()


def test_svg_7():

    fpga = Part(lib="FPGA_Lattice.lib", name="ICE40HX8K-BG121")
    fpga.uA.symtx = "R"
    generate_svg(file_="test7")


def test_svg_8():
    @SubCircuit
    def vga_port(red, grn, blu, hsync, vsync, gnd, logic_lvl=3.3):
        """Generate analog RGB VGA port driven by red, grn, blu digital color buses."""

        # Determine the color depth by finding the max width of the digital color buses.
        # (Note that the color buses don't have to be the same width.)
        depth = max(len(red), len(grn), len(blu))

        # Add extra bus lines to any bus that's smaller than the depth and
        # connect these extra lines to the original LSB bit of the bus.
        for bus in [red, grn, blu]:
            add_width = depth - len(bus)  # Number of lines to add to the bus.
            if add_width > 0:
                bus.insert(0, add_width)  # Add lines to the beginning of the bus.
                bus[add_width] += bus[
                    0:add_width
                ]  # Connect the added bus lines to original LSB.

        # Calculate the resistor weights to support the given color depth.
        vga_input_impedance = 75.0  # Impedance of VGA analog inputs.
        vga_analog_max = 0.7  # Maximum brightness color voltage.
        # Compute the resistance of the upper leg of the voltage divider that will
        # drop the logic_lvl to the vga_analog_max level if the lower leg has
        # a resistance of vga_input_impedance.
        R = (logic_lvl - vga_analog_max) * vga_input_impedance / vga_analog_max
        # The basic weight is R * (1 + 1/2 + 1/4 + ... + 1/2**(width-1))
        r = R * sum([1.0 / 2 ** n for n in range(depth)])
        # The most significant color bit has a weight of r. The next bit has a weight
        # of 2r. The next bit has a weight of 4r, and so on. The weights are arranged
        # in decreasing order so the least significant weight is at the start of the list.
        weights = [str(int(r * 2 ** n)) for n in reversed(range(depth))]

        # Quad resistor packs are used to create weighted sums of the digital
        # signals on the red, green and blue buses. (One resistor in each pack
        # will not be used since there are only three colors.)
        res_network = Part(
            xess_lib, "RN4", footprint="xesscorp/xess.pretty:CTS_742C083", dest=TEMPLATE
        )

        # Create a list of resistor packs, one for each weight.
        res = res_network(value=weights)

        # Create the nets that will accept the weighted sums.
        analog_red = Net("R")
        analog_grn = Net("G")
        analog_blu = Net("B")

        # Match each resistor pack (least significant to most significant) with
        # the the associated lines of each color bus (least significant to
        # most significant) as follows:
        #    res[0], red[0], grn[0], blu[0]
        #    res[1], red[1], grn[1], blu[1]
        #    ...
        # Then attach the individual resistors in each pack between
        # a color bus line and the associated analog color net:
        #    red[0] --- (1)res[0](8) --- analog_red
        #    grn[0] --- (2)res[0](7) --- analog_grn
        #    blu[0] --- (3)res[0](6) --- analog_blu
        #    red[1] --- (1)res[1](8) --- analog_red
        #    grn[1] --- (2)res[1](7) --- analog_grn
        #    blu[1] --- (3)res[1](6) --- analog_blu
        #    ...
        for w, r, g, b in zip(res, red, grn, blu):
            w[1, 8] += r, analog_red  # Red uses the 1st resistor in each pack.
            w[2, 7] += g, analog_grn  # Green uses the 2nd resistor in each pack.
            w[3, 6] += b, analog_blu  # Blue uses the 3rd resistor in each pack.
            w[4, 5] += (
                NC,
                NC,
            )  # Attach the unused resistor in each pack to no-connect nets to suppress ERC warnings.
            w[1].symio = "input"
            w[8].symio = "output"
            w[2].symio = "input"
            w[7].symio = "output"
            w[3].symio = "input"
            w[6].symio = "output"
            w[4].symio = "input"
            w[5].symio = "output"

        # VGA connector outputs the analog red, green and blue signals and the syncs.
        vga_conn = Part(
            "Connector",
            "DB15_FEMALE_HighDensity_MountingHoles",
            footprint="xesscorp/xess.pretty:DB15-3.08mm-HD-FEMALE",
        )

        vga_conn[5, 6, 7, 8, 9, 10] += gnd  # Ground pins.
        vga_conn[4, 11, 12, 15] += NC  # Unconnected pins.
        vga_conn[0] += gnd  # Ground connector shield.
        vga_conn[1] += analog_red  # Analog red signal.
        vga_conn[2] += analog_grn  # Analog green signal.
        vga_conn[3] += analog_blu  # Analog blue signal.
        vga_conn[13] += hsync  # Horizontal sync.
        vga_conn[14] += vsync  # Vertical sync.

        vga_conn[1].symio = "input"
        vga_conn[2].symio = "input"
        vga_conn[3].symio = "input"
        vga_conn[13].symio = "input"
        vga_conn[14].symio = "input"

    # Define some nets and buses.

    gnd = Net("GND")  # Ground reference.
    gnd.drive = POWER

    # Five-bit digital buses carrying red, green, blue color values.
    red = Bus("RED", 5)
    grn = Bus("GRN", 5)
    blu = Bus("BLU", 5)

    # VGA horizontal and vertical sync signals.
    hsync = Net("HSYNC")
    vsync = Net("VSYNC")

    xess_lib = r"/home/devb/xesscorp/KiCad/libraries/xess.lib"

    # Two PMOD headers and a breadboard header bring in the digital red, green,
    # and blue buses along with the horizontal and vertical sync.
    # (The PMOD and breadboard headers bring in the same signals. PMOD connectors
    # are used when the VGA interface connects to a StickIt! motherboard, and the
    # breadboard header is for attaching it to a breadboard.
    pm = 2 * Part(
        xess_lib,
        "PMOD-12",
        footprint="xesscorp/xess.pretty:PMOD-12-MALE",
        dest=TEMPLATE,
    )
    pm[0].symtx = "H"
    pm[1].symtx = "H"
    bread_board_conn = Part(
        "Connector",
        "Conn_01x18_Male",
        footprint="KiCad_V5/Connector_PinHeader_2.54mm.pretty:Pin_Header_1x18_P2.54mm_Vertical",
    )

    # Connect the digital red, green and blue buses and the sync signals to
    # the pins of the PMOD and breadboard headers.
    hsync += bread_board_conn[1], pm[0]["D0"]
    vsync += bread_board_conn[2], pm[0]["D1"]
    red[4] += bread_board_conn[3], pm[0]["D2"]
    grn[4] += bread_board_conn[4], pm[0]["D3"]
    blu[4] += bread_board_conn[5], pm[0]["D4"]
    red[3] += bread_board_conn[6], pm[0]["D5"]
    grn[3] += bread_board_conn[7], pm[0]["D6"]
    blu[3] += bread_board_conn[8], pm[0]["D7"]
    red[2] += bread_board_conn[9], pm[1]["D0"]
    grn[2] += bread_board_conn[10], pm[1]["D1"]
    blu[2] += bread_board_conn[11], pm[1]["D2"]
    red[1] += bread_board_conn[12], pm[1]["D3"]
    grn[1] += bread_board_conn[13], pm[1]["D4"]
    blu[1] += bread_board_conn[14], pm[1]["D5"]
    red[0] += bread_board_conn[15], pm[1]["D6"]
    grn[0] += bread_board_conn[16], pm[1]["D7"]
    blu[0] += bread_board_conn[17]

    # The VGA interface has no active components, so don't connect the PMOD's VCC pins.
    NC & pm[0]["VCC"] & pm[1]["VCC"]

    # Connect the ground reference pins on all the connectors.
    gnd += bread_board_conn[18], pm[0]["GND"], pm[1]["GND"]

    # The PMOD ground pins are defined as power outputs so there will be an error
    # if they're connected together. Therefore, turn off the error checking on one
    # of them to swallow the error.
    pm[1]["GND"].do_erc = False

    # Send the RGB buses and syncs to the VGA port circuit.
    vga_port(red, grn, blu, hsync, vsync, gnd)

    ERC()  # Run error checks.
    generate_netlist()  # Generate the netlist.
    generate_svg(net_stubs=[gnd, red, grn, blu, hsync, vsync])

