# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

import glob
import inspect
import itertools
import os
import os.path
import sys

import pytest

import skidl
from skidl import (
    ERC,
    POWER,
    TEMPLATE,
    Bus,
    Group,
    Net,
    Part,
    PartTmplt,
    SubCircuit,
    generate_graph,
    generate_netlist,
    generate_pcb,
    generate_schematic,
    generate_svg,
    generate_xml,
    subcircuit,
)
import skidl.schematics.place as schplc
from skidl.schematics.place import PlacementFailure
from skidl.schematics.route import RoutingFailure

from .setup_teardown import setup_function, teardown_function

schplc.net_force = schplc.net_force_dist_avg
schplc.overlap_force = schplc.overlap_force_1

sch_options = {}
# seed = int(time.time())
# sch_options["seed"] = seed
# print("Random seed = {}".format(seed))
sch_options["retries"] = 2
sch_options["debug_trace"] = False
# sch_options["allow_routing_failure"] = True
sch_options["pt_to_pt_mult"] = 10  # TODO: Ad-hoc value.
sch_options["normalize"] = True
sch_options["compress_before_place"] = True
# sch_options["allow_jumps"] = True
# sch_options["align_parts"] = True
# sch_options["slip_and_slide"] = True
sch_options["rotate_parts"] = True
# sch_options["trim_anchor_pull_pins"] = True
# sch_options["fanout_attenuation"] = True
# sch_options["remove_power"] = True
# sch_options["remove_high_fanout"] = True
# sch_options["show_orientation_cost"] = True
# sch_options["collect_stats"] = True
if os.getenv("DEBUG_DRAW"):
    # These options control debugging output.
    # To view schematic debugging output, use the command:
    #    DEBUG_DRAW=1 pytest ...
    sch_options["draw_placement"] = True
    # sch_options["draw_all_terminals"] = True
    # sch_options["show_capacities"] = True
    # sch_options["draw_routing_channels"] = True
    # sch_options["draw_global_routing"] = True
    # sch_options["draw_assigned_terminals"] = True
    # sch_options["draw_switchbox_boundary"] = True
    # sch_options["draw_switchbox_routing"] = True


def _empty_footprint_handler(part):
    """Function for handling parts with no footprint.

    Args:
        part (Part): Part with no footprint.
    """
    ref_prefix = part.ref_prefix.upper()

    if ref_prefix in ("R", "C", "L") and len(part.pins) == 2:
        # Resistor, capacitors, inductors default to 0805 SMD footprint.
        part.footprint = "Resistor_SMD:R_0805_2012Metric"

    elif ref_prefix in ("Q",) and len(part.pins) == 3:
        # Transistors default to SOT-23 footprint.
        part.footprint = "Package_TO_SOT_SMD:SOT-23"

    else:
        # Everything else just gets this ridiculous footprint to avoid raising exceptions.
        part.footprint = ":"


# Install the footprint handler for these tests.
skidl.empty_footprint_handler = _empty_footprint_handler


def create_schematic(num_trials=1, flatness=1.0, script_stack_level=1, report_failures=True):
    output_file_root = "./test_data/schematic_output"
    python_version = ".".join([str(n) for n in sys.version_info[0:3]])
    output_dir = os.path.join(output_file_root, python_version)
    try:
        os.makedirs(output_dir, exist_ok=True)
    except TypeError:
        # This happens for Python 2.7 which doesn't support the exist_ok keyword arg.
        try:
            os.makedirs(output_dir)
        except os.error:
            # OK, the directory already exists so just keep going.
            pass
    # top_name = inspect.stack()[script_stack_level].function
    top_name = inspect.stack()[script_stack_level][3]
    for f in glob.glob(os.path.join(output_dir, top_name) + "*.sch"):
        os.remove(f)

    # Initialize file for holding statistics on schematic place & route.
    stats_file = os.path.join(output_dir, top_name + ".csv")
    sch_options["stats_file"] = stats_file
    try:
        os.remove(stats_file)
    except FileNotFoundError:
        pass
    with open(stats_file, "w") as fp:
        # First line shows configuration of P&R options.
        config = ";".join(["{}={}".format(k,v) for k,v in sch_options.items()])
        fp.write(config)
        fp.write("\n")
        # Add headers for columns of statistics.
        fp.write("wire length")
        fp.write("\n")
    
    num_fails = 0
    for trial in range(num_trials):
        try:
            generate_schematic(
                filepath=output_dir,
                top_name=top_name + "_" + str(trial),
                flatness=flatness,
                **sch_options
            )
        except (PlacementFailure, RoutingFailure):
            num_fails += 1

    if num_fails and report_failures:
        raise RoutingFailure
    
    # Return name of P&R stats file.
    return stats_file

def plot_stats(stats_file):
    """Plot histogram of wire lengths for a set of place&routes."""
    import pandas as pd
    import matplotlib.pyplot as plt
    df = pd.read_csv(stats_file,skiprows=1)
    routed = df[df > 0].dropna()                                                                                                    
    routed.hist(column="wire length", bins=10)
    route_success = (df>0).mean()[0]  # Fraction of successfully routed results.
    route_len_mean = routed.mean()[0]
    route_len_median = routed.median()[0]
    route_len_stddev = routed.std()[0]
    plt.xlabel("Total Routed Wire Length")
    plt.ylabel("Frequency")
    plt.title("Distribution of Total Routed Wiring Length")
    plt.annotate("success={:.2f}\nmean={:.0f}\nmedian={:.0f}\nstddev={:.0f}".format(route_success, route_len_mean, route_len_median, route_len_stddev), xy=(0.75, 0.5), xycoords='axes fraction')
    plt.show()

def summarize_stats(stats_file, stat_headers):
    """Summarize stats of wire lengths for a set of place&routes."""
    stat_dict = {}
    import pandas as pd
    df = pd.read_csv(stats_file,skiprows=1)
    routed = df[df > 0].dropna()
    for hdr in stat_headers:
        func = getattr(routed, hdr, None)
        if func:
            stat = func()[0]
            stat_dict[hdr] = stat
        elif hdr == "success":
            stat = (df>0).mean()[0]
            stat_dict[hdr] = stat
    return stat_dict

def search_bool_options(num_trials=1, flatness=1.0, bool_option_keys=[]):
    """Try combinations of place&route settings and record statistics on wire lengths of place&route results."""
    option_keys = sorted(set(list(sch_options.keys()) + bool_option_keys))
    option_keys = [k for k in option_keys if not k.startswith("draw")]
    num_bool_options = len(bool_option_keys)
    bool_option_settings = [[False,True]] * num_bool_options
    bool_option_settings = itertools.product(*bool_option_settings)
    stat_headers = ["success", "mean", "median", "std"]
    with open("./test_data/option_test.csv", "w") as fp:
        fp.write(",".join(option_keys+stat_headers) + "\n")
        for settings in bool_option_settings:
            bool_settings_dict = dict(zip(bool_option_keys, settings))
            sch_options.update(bool_settings_dict)
            stats_file = create_schematic(num_trials=num_trials, flatness=flatness, script_stack_level=2, report_failures=False)
            summary = summarize_stats(stats_file, stat_headers)
            stat_dict = dict()
            stat_dict.update(sch_options)
            stat_dict.update(summary)
            stat_row =  ",".join([str(stat_dict[k]) for k in option_keys + stat_headers])
            fp.write(stat_row + "\n")
            fp.flush()

@pytest.mark.xfail(raises=(RoutingFailure))
def test_gen_sch_1():
    q = Part(
        lib="Device.lib",
        name="Q_PNP_CBE",
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
        dest=TEMPLATE,
        symtx="V",
    )
    r = Part(
        "Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric", dest=TEMPLATE
    )
    gndt = Part("power", "GND", footprint="TestPoint:TestPoint_Pad_D4.0mm")
    vcct = Part("power", "VCC", footprint="TestPoint:TestPoint_Pad_D4.0mm")

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
    generate_xml()
    generate_graph()

    # For collecting stats on option settings.
    # sch_options["remove_power"] = False
    # sch_options["rotate_parts"] = True
    # search_bool_options(num_trials=10, bool_option_keys=[
    # "remove_high_fanout", "fanout_attenuation",
    # "compress_before_place", "allow_jumps", "normalize"])

    create_schematic(num_trials=1,flatness=1.0)


@pytest.mark.xfail(raises=(SyntaxError))
def test_gen_pcb_1():
    """Test PCB generation."""

    l1 = Part(
        "Device.lib",
        "L",
        footprint="Inductor_SMD:L_0805_2012Metric_Pad1.15x1.40mm_HandSolder",
    )
    r1, r2 = (
        Part(
            "Device.lib",
            "R",
            dest=TEMPLATE,
            value="200.0",
            footprint="Resistor_SMD:R_0805_2012Metric",
        )
        * 2
    )
    q1 = Part(
        "Device.lib", "Q_NPN_CBE", footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2"
    )
    c1 = Part(
        "Device.lib",
        "C",
        value="10pF",
        footprint="Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder",
    )
    r3 = r2(value="1K", footprint="Resistor_SMD:R_0805_2012Metric")
    vcc, vin, vout, gnd = Net("VCC"), Net("VIN"), Net("VOUT"), Net("GND")
    vcc & r1 & vin & r2 & gnd
    vcc & r3 & vout & q1["C,E"] & gnd
    q1["B"] += vin
    vout & (l1 | c1) & gnd
    rly = Part("Relay", "TE_PCH-1xxx2M", footprint="Relay_THT:Relay_SPST_TE_PCH-1xxx2M")
    rly[1, 2, 3, 5] += gnd
    led = Part("Device.lib", "LED_ARGB", symtx="RH", footprint="LED_SMD:LED_RGB_1210")
    r, g, b = Net("R"), Net("G"), Net("B")
    led["A,RK,GK,BK"] += vcc, r, g, b
    Part(
        lib="MCU_Microchip_PIC10.lib",
        name="PIC10F200-IMC",
        footprint="Package_DFN_QFN:DFN-8-1EP_2x3mm_P0.5mm_EP0.61x2.2mm",
    )

    generate_pcb()


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_sch_place():
    @subcircuit
    def test():
        q = Part(
            lib="Device.lib",
            name="Q_PNP_CBE",
            footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
            dest=TEMPLATE,
            # symtx="V",
        )
        r = Part(
            "Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric", dest=TEMPLATE
        )
        vcc = Net("VCC")
        gnd = Net("GND")

        for _ in range(3):
            with Group("G:"):
                a = Net("A")
                b = Net("B")
                o = Net("O")
                q1 = q()
                q2 = q()
                r1, r2, r3 = r(3, value="10K")
                a & r1 & (q1["c,e"] | q2["c,e"]) & r3 & o
                b & r2 & (q1["b"] | q2["b"])

        with Group("B:"):
            n = 5
            qs = []
            rs = []
            for i in range(n):
                qs.append(q())
                rs.append(r())
                vcc & rs[-1] & qs[-1]["c,e"]
                if i:
                    qs[-2].E & qs[-1].B
            Net("A") & r() & qs[0].B
            qs[-1].E & gnd
            qs[-1].C & Net("O")

    test()
    create_schematic(flatness=0.5)


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_sch_place_2():
    @subcircuit
    def test():
        q = Part(
            lib="Device.lib",
            name="Q_PNP_CBE",
            footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
            dest=TEMPLATE,
            symtx="VV",
        )
        r = Part(
            "Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric", dest=TEMPLATE, symtx="VV"
        )
        c = Part("Device.lib", "C", value="10pF")
        vcc = Net("VCC", netio="i")
        gnd = Net("GND", netio="i")
        vcca = Net("VCCA", stub=True)
        gnda = Net("GNDA", stub=True)

        for _ in range(5):
            c_ = c()
            vcca & c_ & gnda
        
        n = 5
        qs = []
        rs = []
        for i in range(n):
            qs.append(q())
            rs.append(r())
            vcc & rs[-1] & qs[-1]["c,e"]
            if i:
                qs[-2].E & qs[-1].B
        Net("A", netio="i") & r() & qs[0].B
        qs[-1].E & gnd
        qs[-1].C & Net("O", netio="o")

    test()
    create_schematic(flatness=0.5)


@pytest.mark.xfail(raises=(RoutingFailure))
def test_gen_sch_very_simple():
    r = Part(
        "Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric", dest=TEMPLATE
    )
    # gndt = Part("power", "GND", footprint="TestPoint:TestPoint_Pad_D4.0mm")
    # vcct = Part("power", "VCC", footprint="TestPoint:TestPoint_Pad_D4.0mm")

    # gnd = Net("GND")
    # vcc = Net("VCC")
    # gnd & gndt
    # vcc & vcct
    # gnd & r() & vcc
    r() & r() & r() & r()
    create_schematic(flatness=1.0)


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_sch_simple():
    q = Part(
        lib="Device.lib",
        name="Q_PNP_CBE",
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
        dest=TEMPLATE,
        symtx="V",
    )
    qs = q(15)
    ns = [Net() for p in qs[0].pins]
    for q in qs:
        for p, n in zip(q.pins, ns):
            n += p
    create_schematic(flatness=1.0)


@pytest.mark.xfail(raises=(RoutingFailure))
def test_gen_sch_floating():
    r = Part(
        "Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric", dest=TEMPLATE
    )
    c = Part(
        "Device.lib", "C", footprint="Capacitor_SMD:R_0805_2012Metric", dest=TEMPLATE
    )
    q = Part(
        lib="Device.lib",
        name="Q_PNP_CBE",
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
        dest=TEMPLATE,
        symtx="V",
    )
    # gndt = Part("power", "GND", footprint="TestPoint:TestPoint_Pad_D4.0mm")
    # vcct = Part("power", "VCC", footprint="TestPoint:TestPoint_Pad_D4.0mm")

    gnd = Net("GND")
    vcc = Net("VCC")
    # gnd & gndt
    # vcc & vcct
    # gnd & r() & vcc
    for _ in range(2):
        with Group("A:"):
            vcc & r() & q()["B", "E"] & r() & gnd
            vcc & (c() | c()) & gnd
            c()
            r()
            q()
    create_schematic(flatness=1.0)


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_sch_units():
    @subcircuit
    def test():
        q = Part(
            lib="Device.lib",
            name="Q_PNP_CBE",
            footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
            dest=TEMPLATE,
            symtx="V",
        )
        # r = Part("Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric",dest=TEMPLATE)
        rn = Part("Device", "R_Pack05_Split", footprint=":")
        gndt = Part("power", "GND", footprint="TestPoint:TestPoint_Pad_D4.0mm")
        vcct = Part("power", "VCC", footprint="TestPoint:TestPoint_Pad_D4.0mm")

        gnd = Net("GND", stub=True, netclass="Power")
        vcc = Net("VCC", stub=True, netclass="Power")
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
        # r1, r2, r3, r4, r5 = r(5, value="10K")
        r1, r2, r3, r4, r5 = rn.unit.values()
        a & r1 & q1["B", "C"] & r4 & q2["B", "C"] & a_and_b & r5 & gnd
        b & r2 & q1["B"]
        q1["C"] & r3 & gnd
        vcc & q1["E"]
        vcc & q2["E"]

    with Group("A"):
        q = Part(
            lib="Device.lib",
            name="Q_PNP_CBE",
            footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
            dest=TEMPLATE,
            symtx="V",
        )
        q()
        test()  # This enables a recursion error in test_interface_12 for reasons unknown.

    create_schematic(flatness=1.0)


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_sch_hier():
    with Group("A"):
        with Group("B"):
            q = Part(
                lib="Device.lib",
                name="Q_PNP_CBE",
                footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
                dest=TEMPLATE,
                symtx="V",
            )
            r = Part(
                "Device.lib",
                "R",
                footprint="Resistor_SMD:R_0805_2012Metric",
                dest=TEMPLATE,
            )
            gndt = Part("power", "GND", footprint="TestPoint:TestPoint_Pad_D4.0mm")
            vcct = Part("power", "VCC", footprint="TestPoint:TestPoint_Pad_D4.0mm")

            gnd = Net("GND", stub=True, netclass="Power")
            vcc = Net("VCC", stub=True, netclass="Power")
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

    create_schematic(flatness=0.0)


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_sch_hier_conn():

    r = Part(
        "Device.lib", "R", footprint="Resistor_SMD:R_0805_2012Metric", dest=TEMPLATE
    )
    q = Part(
        lib="Device.lib",
        name="Q_PNP_CBE",
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
        dest=TEMPLATE,
        symtx="V",
    )

    a = Net("A")
    b = Net("B")
    o = Net("O")

    for _ in range(3):
        with Group("A:"):
            q1 = q()
            q2 = q()
            r1, r2, r3 = r(3, value="10K")
            a & r1 & (q1["c,e"] | q2["c,e"]) & r3 & o
            b & r2 & (q1["b"] | q2["b"])

    create_schematic(flatness=1.0)


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_sch_part_tx():
    q = Part(
        lib="Device.lib",
        name="Q_PNP_CBE",
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
        dest=TEMPLATE,
    )
    q1 = q(symtx="")
    q2 = q(symtx="R")
    q3 = q(symtx="L")
    q4 = q(symtx="H")
    q5 = q(symtx="V")
    create_schematic(flatness=1.0)


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_svg_1():
    """Test SVG generation."""

    l1 = Part("Device.lib", "L")
    r1, r2 = Part("Device.lib", "R", dest=TEMPLATE, value="200.0") * 2
    q1 = Part("Device.lib", "Q_NPN_CBE")
    c1 = Part("Device.lib", "C", value="10pF")
    r3 = r2(value="1K")
    vcc, vin, vout, gnd = Net("VCC"), Net("VIN"), Net("VOUT"), Net("GND")
    vcc & r1 & vin & r2 & gnd
    vcc & r3 & vout & q1["C,E"] & gnd
    q1["B"] += vin
    vout & (l1 | c1) & gnd
    rly = Part("Relay", "TE_PCH-1xxx2M")
    rly[1, 2, 3, 5] += gnd
    led = Part("Device.lib", "LED_ARGB", symtx="RH")
    r, g, b = Net("R"), Net("G"), Net("B")
    led["A,RK,GK,BK"] += vcc, r, g, b
    Part(lib="MCU_Microchip_PIC10.lib", name="PIC10F200-IMC")

    create_schematic(flatness=1.0)
    generate_svg(file_="svg_1")


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_svg_2():
    opamp = Part(lib="Amplifier_Operational.lib", name="AD8676xR", symtx="V")
    opamp.uA.p2 += Net("IN1")
    opamp.uA.p3 += Net("IN2")
    opamp.uA.p1 += Net("OUT")
    opamp.uB.symtx = "L"

    create_schematic(flatness=1.0)
    generate_svg(file_="svg_2")


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_svg_3():
    gnd = Part("power", "GND")
    vcc = Part("power", "VCC")

    opamp = Part(lib="Amplifier_Operational.lib", name="AD8676xR", symtx="V")

    for part in default_circuit.parts:
        part.validate()

    vcc[1] += opamp[8]
    gnd[1] += opamp[4]

    r = Part("Device.lib", "R_US", dest=TEMPLATE, tx_ops="L")

    (
        Net("IN")
        & r(value="4K7", symtx="L")
        & opamp.uA[2]
        & r(value="4K7", symtx="L")
        & opamp.uA[1]
    )
    gnd[1] += opamp.uA[3]

    opamp.uA[1] & r(value="10K") & gnd[1]

    for part in default_circuit.parts:
        part.validate()

    create_schematic(flatness=1.0)
    generate_svg(file_="svg_3")

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
            print(
                "///// Best arrangement cost = {best_cost:2.2f} /////".format(
                    **locals()
                )
            )
            arr = Arranger(default_circuit, w, h)

    best_arr.apply()
    for part in best_arr.parts:
        print("{part.ref:5s} {part.region.x} {part.region.y}".format(**locals()))
    print("cost = {best_arr.cost()}".format(**locals()))


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_svg_4():
    q = Part(lib="Device.lib", name="Q_PNP_CBE", dest=TEMPLATE, symtx="V")
    r = Part("Device.lib", "R", dest=TEMPLATE)
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

    create_schematic(flatness=1.0)
    generate_svg("svg_4")
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
            print(
                "///// Best arrangement cost = {best_cost:2.2f} /////".format(
                    **locals()
                )
            )
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
            print(
                "///// Best arrangement cost = {best_cost:2.2f} /////".format(
                    **locals()
                )
            )
            arr = Arranger(default_circuit, 3, 3)

    best_arr.apply()
    for part in default_circuit.parts:
        print("{part.ref:5s} {part.region.x} {part.region.y}".format(**locals()))
    print("cost = {best_arr.cost()}".format(**locals()))


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_svg_5():
    uc = Part(lib="wch.lib", name="CH551G", dest=TEMPLATE)
    uc.split_pin_names("/")
    usb = Part(lib="Connector.lib", name="USB_B_Micro", symtx="H")

    uc1 = uc()
    uc1["UDM, UDP"] += usb["D-, D+"]

    uc_spare = uc()
    uc_spare["UDP"] & uc_spare["UDM"]

    uc1.UDM.net.stub = True
    uc1.UDP.net.stub = True

    create_schematic(flatness=1.0)
    generate_svg("svg_5")


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_svg_6():
    r = Part("Device.lib", "R", dest=TEMPLATE)
    gndt = Part("power", "GND")
    vcct = Part("power", "VCC")

    gnd = Net("GND")
    vcc = Net("VCC")
    (
        gnd
        & gndt
        & r()
        & r()
        & (r() | r())
        # & (r(symtx="l") | r(symtx="R"))
        & r()
        & r()
        & r()
        & r()
        & r()
        & r()
        & r()
        & vcct
        & vcc
    )

    create_schematic(flatness=1.0)
    generate_svg("svg_6")


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_svg_7():

    fpga = Part(lib="FPGA_Lattice.lib", name="ICE40HX8K-BG121")
    fpga.uA.symtx = "R"
    create_schematic(flatness=1.0)
    generate_svg(file_="svg_7")


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_svg_8():
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

    xess_lib = r"xess.lib"

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

    gnd.stub = True
    red.stub = True
    grn.stub = True
    blu.stub = True
    hsync.stub = True
    vsync.stub = True

    ERC()  # Run error checks.
    generate_netlist()  # Generate the netlist.
    create_schematic(flatness=1.0)
    generate_svg("svg_8")


@pytest.mark.xfail(raises=RoutingFailure)
def test_gen_sch_buses():
    ram = PartTmplt("GameteSnapEDA.lib", "MT48LC16M16A2TG-6A_IT:GTR")
    rams = 3 * ram

    for rama, ramb in zip(rams[:-1], rams[1:]):
        rama["DQ[15:0]"] += ramb["DQ[15:0]"]
        rama["A[12:0]"] += ramb["A[12:0]"]
        rama["BA[1:0]"] += ramb["BA[1:0]"]
        rama["DQML"] += ramb["DQML"]
        rama["DQMH"] += ramb["DQMH"]
        rama["~WE~"] += ramb["~WE~"]
        rama["~CAS~"] += ramb["~CAS~"]
        rama["~RAS~"] += ramb["~RAS~"]
        rama["~CS~"] += ramb["~CS~"]
        rama["CLK"] += ramb["CLK"]
        rama["CKE"] += ramb["CKE"]

    gnd = Net("GND")
    vdd = Net("VDD")

    for rama in rams:
        vdd += rama["VDD"]
        gnd += rama["VSS"]
        vdd += rama["VDDQ"]
        gnd += rama["VSSQ"]

    create_schematic()
