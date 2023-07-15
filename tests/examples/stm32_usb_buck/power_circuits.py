import power_nets as pn
import utility_circuits as uc

from skidl import *


@package
def power_circuits():
    buck(pn.v_12v, pn.v_5v, pn.v_3v3, pn.gnd)
    anlg_flt(pn.vdda, pn.gnd, pn.vdda)


def anlg_flt(vdd, gnd, vdda):
    # Create parts
    c1 = Part("Device", "C_Small", footprint="C_0603_1608Metric", value="1uF")
    c2 = Part("Device", "C_Small", footprint="C_0603_1608Metric", value="10nF")
    l1 = Part("Device", "L_Small", footprint="L_0603_1608Metric", value="29nH")
    # Connect pins
    vdda += c1.p1, c2.p1, l1.p2
    vdd += l1.p1
    gnd += c1.p2, c2.p2


@SubCircuit
def buck(vin, v_usb, vout, gnd):

    vprotected = Net("v12_fused", stub=True)
    vin_protection(vin, vprotected, gnd)

    reg = Part("Regulator_Linear", "AP1117-15", footprint="SOT-223-3_TabPin2")
    # reg.p3.label = "v12_fused"
    reg.p3 += vprotected
    c1 = Part("Device", "C_Small", footprint="C_0603_1608Metric", value="10uF")
    c2 = Part("Device", "C_Small", footprint="C_0603_1608Metric", value="10uF")
    d = Part("Device", "D_Zener_Small", footprint="D_0201_0603Metric")
    d.p1 += v_usb

    uc.led(vout, gnd, "red", "5.6k")

    vprotected += reg.p3, c1.p1, d.p2
    vout += reg.p2, c2.p1
    gnd += reg.p1, c1.p2, c2.p2


@SubCircuit
def vin_protection(vin, vout, gnd):
    pmos = Part(
        "Device", "Q_PMOS_DGS", footprint="SOT-23"
    )  # reverse polarity protection
    fuse = Part(
        "Device", "Polyfuse_Small", footprint="Fuse_Bourns_MF-RG300"
    )  # resetable fuse
    fb = Part("Device", "Ferrite_Bead", footprint="L_Murata_DEM35xxC")  # ferrite bead

    vin += fuse.p1
    fuse.p2 += pmos.p1
    pmos.p2 += gnd
    pmos.p3 += fb.p1
    fb.p2 += vout
