import pytest
from skidl import *


def test_lib_import_1():
    Circuit._reset()
    lib = skidl._SchLib('C:/xesscorp/KiCad/libraries/xess.lib')
    assert len(lib) > 0


def test_part_find_1():
    Circuit._reset()
    lib = skidl._SchLib('C:/xesscorp/KiCad/libraries/xess.lib')
    parts = Part(lib, '1117')
    assert isinstance(parts, Part)


def test_nets_1():
    Circuit._reset()
    gnd = Net('GND')
    a = Net('A')
    b = Net('B')
    c = Net()
    p = Pin()
    a += p
    assert len(SubCircuit.nets) == 1
    assert len(a) == 1
    assert len(b) == 0
    assert len(c) == 0


def test_nets_2():
    Circuit._reset()
    gnd = Net('GND')
    a = Net('A')
    b = Net('B')
    c = Net()
    p = Pin()
    assert len(SubCircuit.nets) == 0
    assert len(a) == 0
    assert len(b) == 0
    assert len(c) == 0


def test_bus_1():
    # Make a bus.
    Circuit._reset()
    bus = Bus('BB', 11, 5)
    assert len(bus) == 16


def test_bus_2():
    # Make a bus from nets.
    Circuit._reset()
    gnd = Net('GND')
    a = Net('A')
    b = Net('B')
    c = Net()
    bus = Bus('BB', a, b, c)
    assert len(bus) == 3
    assert len(SubCircuit.nets) == 0


def test_bus_3():
    # Make a bus from ints and nets.
    Circuit._reset()
    gnd = Net('GND')
    a = Net('A')
    b = Net('B')
    c = Net()
    bus = Bus('BB', a, 5, b, c)
    assert len(bus) == 8
    assert len(SubCircuit.nets) == 0


def test_bus_4():
    # Make a bus from ints, nets and buses.
    Circuit._reset()
    gnd = Net('GND')
    a = Net('A')
    b = Net('B')
    c = Net()
    bus1 = Bus('AA', a, c, 2)
    assert len(bus1) == 4
    bus1.name = 'AA'
    assert bus1.name == 'AA'
    bus2 = Bus('BB', b, bus1, 3)
    assert len(bus2) == len(bus1) + 4
    assert len(SubCircuit.nets) == 0


def test_bus_5():
    # Connect a pin to a bus line.
    Circuit._reset()
    gnd = Net('GND')
    a = Net('A')
    b = Net('B')
    c = Net()
    bus = Bus('AA', a, a, 2)
    assert len(bus) == 4
    p = Pin()
    a += p
    assert isinstance(bus[0], Net)
    bus[0] += p
    assert len(a) == 1
    assert len(bus[0]) == 1
    assert len(bus[1]) == 1
    assert len(SubCircuit.nets) == 1


def test_bus_6():
    # Check bus line names.
    Circuit._reset()
    bus_prefix = 'AA'
    net = Net()
    pin = Pin()
    bus = Bus(bus_prefix, 4, net, 3, pin, 4)
    assert len(bus) == 13
    for i, n in enumerate(bus._get_nets()):
        assert bus_prefix + str(i) == n.name
    net.name = 'a'
    for i, n in enumerate(bus._get_nets()):
        if i == 4:
            assert net.name == n.name
        else:
            assert bus_prefix + str(i) == n.name


def test_bus_7():
    # Test bus connections.
    Circuit._reset()
    net = Net()
    pin = Pin()
    bus = Bus('AA', 2)
    net += pin
    net += bus[1]
    assert len(net) == 1


def test_bus_8():
    Circuit._reset()
    bus1 = Bus('A', 8)
    assert isinstance(bus1, Bus)
    nets = [Net() for _ in bus1.nets]
    for n in nets:
        n += Pin()
    bus1 += nets
    assert isinstance(bus1, Bus)
    bus2 = Bus('B', 8)
    assert isinstance(bus2, Bus)
    bus1 += bus2
    assert len(Circuit._get_nets()) == len(bus1)


def test_bus_9():
    Circuit._reset()
    bus1 = Bus('A', 8)
    bus2 = Bus('B', 8)
    bus2 += 8 * Pin()
    bus1 += bus2[7:0]
    assert len(Circuit._get_nets()) == len(bus1)


def test_bus_10():
    Circuit._reset()
    bus1 = Bus('A', 8)
    bus2 = Bus('B', 9)
    with pytest.raises(Exception):
        bus1 += bus2


def test_bus_11():
    Circuit._reset()
    bus1 = Bus('A', 8)
    bus2 = Bus('B', 9)
    with pytest.raises(Exception):
        bus2 += bus1


def test_bus_12():
    Circuit._reset()
    bus1 = Bus('A', 8)
    with pytest.raises(Exception):
        bus1[5:0] = 6 * Pin()


def test_bus_13():
    Circuit._reset()
    bus1 = Bus('A', 8)
    bus1 += 8 * Pin()
    with pytest.raises(Exception):
        bus1[5:0] = 6 * Pin()

def test_bus_14():
    Circuit._reset()
    bus1 = Bus('A',8)
    p1, p2 = 2 * Pin()
    p2 += bus1[5]
    p1 += p2
    p3 = Pin()
    bus1[5] += p3

def test_bus_15():
    Circuit._reset()
    bus1 = Bus('A', 8)
    nets = bus1[:][::-1]
    for n, i in zip(nets, range(8)[::-1]):
        assert 'A'+str(i) == n.name

def test_connect_1():
    Circuit._reset()
    vreg = Part('C:/xesscorp/KiCad/libraries/xess.lib',
                '1117',
                footprint='null')
    vreg.value = 'NCV1117'
    gnd = Net('GND')
    vin = Net('Vin')
    vout = Net('Vout')
    gnd += vreg[1]
    vin += vreg[2]
    vout += vreg[3]
    assert vreg._is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vout) == 1


def test_connect_2():
    Circuit._reset()
    vreg1 = Part('C:/xesscorp/KiCad/libraries/xess.lib',
                 '1117',
                 footprint='null')
    vreg1.value = 'NCV1117'
    vreg2 = 1 * vreg1
    gnd = Net('GND')
    vin = Net('Vin')
    vout = Net('Vout')
    gnd += vreg1[1]
    vin += vreg1[2]
    vout += vreg1[3]
    vreg2[1, 2, 3] += gnd, vin, vout
    assert vreg1._is_connected() == True
    assert vreg2._is_connected() == True
    assert len(gnd) == 2
    assert len(vin) == 2
    assert len(vout) == 2


def test_connect_3():
    Circuit._reset()
    vreg1 = Part('C:/xesscorp/KiCad/libraries/xess.lib',
                 '1117',
                 footprint='null')
    vreg1.value = 'NCV1117'
    vreg2 = 1 * vreg1
    gnd = Net('GND')
    vin = Net('Vin')
    vout = Net('Vout')
    gnd += vreg1[1], vreg2[1]
    vin += vreg1[2], vreg2[2]
    vout += vreg1[3], vreg2[3]
    assert vreg1._is_connected() == True
    assert vreg2._is_connected() == True
    assert len(gnd) == 2
    assert len(vin) == 2
    assert len(vout) == 2


def test_connect_4():
    Circuit._reset()
    vreg1 = Part('C:/xesscorp/KiCad/libraries/xess.lib',
                 '1117',
                 footprint='null')
    vreg1.value = 'NCV1117'
    vreg2 = 1 * vreg1
    gnd = Net('GND')
    vin = Net('Vin')
    vout = Net('Vout')
    Bus('TMP', gnd, vin, vout)[:] += vreg1[1:3]
    Bus('TMP', gnd, vin, vout)[1:2] += vreg2[(2, 3)]
    assert vreg1._is_connected() == True
    assert vreg2._is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 2
    assert len(vout) == 2


def test_connect_5():
    Circuit._reset()
    vreg1 = Part('C:/xesscorp/KiCad/libraries/xess.lib',
                 '1117',
                 footprint='null')
    gnd = Net('GND')
    vin = Net('Vin')
    vreg1['GND', 'IN'] += gnd, vin
    vreg1['HS'] += vreg1['OUT']
    vreg1['OUT'] += vreg1['HS']
    assert vreg1._is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vreg1['IN'].net) == 1
    assert len(vreg1['HS'].net) == 2


def test_connect_6():
    Circuit._reset()
    gnd = Net('GND')
    vin = Net('Vin')
    vreg1 = Part('C:/xesscorp/KiCad/libraries/xess.lib',
                 '1117',
                 footprint='null',
                 connections={'GND': gnd,
                              'IN': vin})
    vreg2 = Part('C:/xesscorp/KiCad/libraries/xess.lib',
                 '1117',
                 footprint='null',
                 connections={'GND': gnd,
                              'IN': vin})
    vreg1['HS'] += vreg1['OUT']
    vregs = 2 * vreg1
    vregs = vreg1.copy(2)
    assert vreg1._is_connected() == True
    assert len(gnd) == 6
    assert len(vin) == 6
    assert len(vreg1['IN'].net) == 6
    assert len(vreg1['HS'].net) == 10


def test_connect_7():
    Circuit._reset()
    n1, n2 = 2 * Net()
    p1, p2, p3 = 3 * Pin()
    p1 += n1
    n2 += p2, p3
    p1 += p2, p3
    assert len(p1.net) == 3
    assert len(p1.net) == len(p2.net) == len(p3.net)
    assert len(n1) == 3
    assert len(n2) == 3
    assert n2._is_attached(n1)


def test_string_indices_1():
    Circuit._reset()
    vreg1 = Part('C:/xesscorp/KiCad/libraries/xess.lib',
                 '1117',
                 footprint='null')
    gnd = Net('GND')
    vin = Net('Vin')
    vreg1['GND, IN, OUT'] += gnd, vin, vreg1['HS']
    assert vreg1._is_connected() == True
    assert len(gnd) == 1
    assert len(vin) == 1
    assert len(vreg1['IN'].net) == 1
    assert len(vreg1['HS'].net) == 2
    assert len(vreg1['OUT'].net) == 2
    assert vreg1['OUT'].net._is_attached(vreg1['HS'].net)


def test_name_1():
    Circuit._reset()
    vreg1 = Part('C:/xesscorp/KiCad/libraries/xess.lib', '1117')
    assert vreg1.ref == 'U1'
    vreg1.ref = 'U1'
    assert vreg1.ref == 'U1'
    bus1 = Bus(None)
    assert bus1.name == 'B$1'
    bus1 = Bus('B1')
    assert bus1.name == 'B1'
    bus1.name = 'B1'
    assert bus1.name == 'B1'


def test_net_merge_1():
    Circuit._reset()
    a = Net('A')
    b = Net('B')
    a += Pin(), Pin(), Pin(), Pin(), Pin()
    assert len(a) == 5
    b += Pin(), Pin(), Pin()
    assert len(b) == 3
    a += b
    assert len(a) == 8

def test_parser_1():
    parse_netlist(r'C:\xesscorp\KiCad\tools\skidl\tests\Arduino_Uno_R3_From_Scratch.net')

def test_netlist_to_skidl_1():
    netlist_to_skidl(r'C:\xesscorp\KiCad\tools\skidl\tests\Arduino_Uno_R3_From_Scratch.net')
