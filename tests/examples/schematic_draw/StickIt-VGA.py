from skidl import *


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
    r = R * sum([1.0 / 2**n for n in range(depth)])
    # The most significant color bit has a weight of r. The next bit has a weight
    # of 2r. The next bit has a weight of 4r, and so on. The weights are arranged
    # in decreasing order so the least significant weight is at the start of the list.
    weights = [str(int(r * 2**n)) for n in reversed(range(depth))]

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

xess_lib = r"/home/devb/tech_stuff/KiCad/libraries/xess.lib"

# Two PMOD headers and a breadboard header bring in the digital red, green,
# and blue buses along with the horizontal and vertical sync.
# (The PMOD and breadboard headers bring in the same signals. PMOD connectors
# are used when the VGA interface connects to a StickIt! motherboard, and the
# breadboard header is for attaching it to a breadboard.
pm = 2 * Part(
    xess_lib, "PMOD-12", footprint="xesscorp/xess.pretty:PMOD-12-MALE", dest=TEMPLATE
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
NC += pm[0]["VCC"], pm[1]["VCC"]

# Connect the ground reference pins on all the connectors.
gnd += bread_board_conn[18], pm[0]["GND"], pm[1]["GND"]

# The PMOD ground pins are defined as power outputs so there will be an error
# if they're connected together. Therefore, turn off the error checking on one
# of them to swallow the error.
pm[1]["GND"].do_erc = False

# Send the RGB buses and syncs to the VGA port circuit.
vga_port(red, grn, blu, hsync, vsync, gnd)

# Stub these nets.
gnd.stub = True
red.stub = True
grn.stub = True
blu.stub = True
hsync.stub = True
vsync.stub = True

ERC()  # Run error checks.
generate_netlist()  # Generate the netlist.
generate_svg()
