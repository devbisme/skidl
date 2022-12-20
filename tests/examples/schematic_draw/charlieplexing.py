from skidl import *


def reref(part, r, c):
    part.ref = "{part.name}-{r}-{c}".format(**locals())


@subcircuit
def chplx(b, diode_t, two_pin_t=None):
    for r, hi in enumerate(b, 1):
        for c, lo in enumerate(b, 1):
            if hi != lo:
                diode = diode_t()
                reref(diode, r, c)
                hi += diode["A"]
                if two_pin_t != None:
                    two_pin = two_pin_t()
                    reref(two_pin, r, c)
                    two_pin[:] += diode["K"], lo
                else:
                    lo += diode["K"]


@subcircuit
def chplx_leds(
    b,
    led_t=Part(
        "Device",
        "LED",
        TEMPLATE,
        footprint="KiCad_V5/LED_SMD.pretty:LED_0805_2012Metric_Castellated",
    ),
):

    chplx(b, led_t)


@subcircuit
def chplx_switches(
    b,
    diode_t=Part(
        "Device", "D", TEMPLATE, footprint="KiCad_V5/Diode_SMD.pretty:D_0805_2012Metric"
    ),
    switch_t=Part(
        "Switch",
        "SW_SPST",
        TEMPLATE,
        footprint="KiCad_V5/Button_Switch_SMD.pretty:SW_SPST_CK_RS282G05A3",
    ),
):

    chplx(b, diode_t, switch_t)


vdd, gnd = Net("VDD"), Net("GND")  # power & ground nets.
vdd.drive = POWER
gnd.drive = POWER

c = Part(
    "Device", "C", TEMPLATE, footprint="KiCad_V5/Capacitor_SMD.pretty:C_0805_2012Metric"
)  # capacitor template.

uc = Part(
    "MCU_Microchip_PIC16",
    "PIC16F83-XXSO",
    footprint="KiCad_V5/Package_SO.pretty:SOIC-18W_7.5x11.6mm_P1.27mm",
)  # Microcontroller.
uc.split_pin_names("/")
uc["VDD, VSS"] += vdd, gnd  # Attach pwr, gnd to uC.
c_byp = c(value="10uF")  # Add bypass capacitor.
c_byp[1, 2] += vdd, gnd

xtal = Part(
    "Device",
    "Crystal",
    footprint="KiCad_V5/Crystal.pretty:Crystal_SMD_0603-2Pin_6.0x3.5mm",
)  # Crystal.
uc["OSC1, OSC2"] += xtal[1, 2]  # Attach crystal to uC.
c1, c2 = c(2, value="10pF")  # Crystal trim caps.
c1[1, 2] += xtal[1], gnd  # Connect trim caps.
c2[1, 2] += xtal[2], gnd

chplx_leds(uc["RB[3:0]"])  # 12 charlieplexed LEDs.
chplx_switches(uc["RA[3:0]"])  # 12 charlieplexed switches.

ERC()

generate_netlist()
