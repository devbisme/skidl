import pytest

from skidl.common import *

from .setup_teardown import *

# Skip this test module if PySpice is missing.
pexpect = pytest.importorskip("PySpice")


from skidl.pyspice import *  # isort:skip


def test_lib_import_1():
    lib_search_paths[SPICE].append(r"./SpiceLib/lib")
    lib = SchLib("lt1083", tool=SPICE)
    assert len(lib) > 0
    for p in lib.get_parts():
        print(p)


def test_lib_import_2():
    with pytest.raises(FileNotFoundError):
        lib = SchLib("lt1074", tool=SPICE)


def test_lib_export_1():
    # lib_search_paths[SPICE].append(r"C:\Program Files (x86)\LTC\LTspiceIV\lib")
    set_default_tool(SPICE)
    lib = SchLib("lt1083", tool=SPICE)
    lib.export("my_lt1083", tool=SKIDL)
    # Doesn't work because of "pyspice={...}" placed in exported library.
    # my_lib = SchLib('my_lt1083', tool=SKIDL)
    # assert len(lib) == len(my_lib)


def test_xspice_1():
    set_default_tool(SPICE)
    # Component declarations showing various XSPICE styles.
    vin = sinev(offset=1.65 @ u_V, amplitude=1.65 @ u_V, frequency=100e6)
    adc = Part(
        "pyspice",
        "A",
        io="anlg_in[],dig_out[]",
        model=XspiceModel(
            "adc",
            "adc_bridge",
            in_low=0.05 @ u_V,
            in_high=0.1 @ u_V,
            rise_delay=1e-9 @ u_s,
            fall_delay=1e-9 @ u_s,
        ),
        tool=SKIDL,
    )

    buf_tmp = A(
        io=["buf_in, buf_out"],
        model=XspiceModel(
            "buf",
            "d_buffer",
            rise_delay=1e-9 @ u_s,
            fall_delay=1e-9 @ u_s,
            input_load=1e-12 @ u_s,
        ),
        dest=TEMPLATE,
    )
    buf = buf_tmp()

    dac = A(
        io=["dig_in[]", "anlg_out[]"],
        model=XspiceModel("dac", "dac_bridge", out_low=1.0 @ u_V, out_high=3.3 @ u_V),
    )

    r = R(value=1 @ u_kOhm)

    # Create a part with no connections to test NULL SPICE connections.
    buf2 = buf_tmp()
    buf2["buf_in"] += NC

    # Connections: sine wave -> ADC -> buffer -> DAC.
    vin["p, n"] += (
        adc["anlg_in"][0],
        gnd,
    )  # Attach to first pin in ADC anlg_in vector of pins.
    adc["dig_out"][0] += buf[
        "buf_in"
    ]  # Attach first pin of ADC dig_out vector to buffer.
    buf["buf_out"] += dac["dig_in"][
        0
    ]  # Attach buffer output to first pin of DAC dig_in vector of pins.
    r["p,n"] += (
        dac["anlg_out"][0],
        gnd,
    )  # Attach first pin of DAC anlg_out vector to load resistor.

    circ = generate_netlist()
    print(circ)
    sim = circ.simulator()
    waveforms = sim.transient(step_time=0.1 @ u_ns, end_time=50 @ u_ns)
    time = waveforms.time
    vin = waveforms[node(vin["p"])]
    vout = waveforms[node(r["p"])]

    print("{:^7s}{:^7s}".format("vin", "vout"))
    print("=" * 15)
    for v1, v2 in zip(vin.as_ndarray(), vout.as_ndarray()):
        print("{:6.2f} {:6.2f}".format(v1, v2))
