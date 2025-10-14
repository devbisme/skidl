"""
Unit tests for code examples from landing.md documentation.

These tests verify that the code examples in the SKiDL landing page
documentation work correctly. No mocking is used to ensure real
functionality is tested.
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

from skidl import (
    Net, Part, Bus, Pin, Circuit, SchLib, Interface, SubCircuit,
    PartClass, NetClass, ERC, generate_netlist, generate_svg,
    erc_assert, tee, POWER, TEMPLATE, KICAD9
)

# Skip entire module unless default tool is KICAD9 because these tests rely on libraries in test_data/kicad9.
if os.getenv("SKIDL_TOOL") != 'KICAD9':
    pytest.skip("Tests require KICAD9 as default tool", allow_module_level=True)


class TestBasicUsage:
    """Test basic SKiDL usage examples from the documentation."""
    
    def test_voltage_divider_circuit(self):
        """Test the basic voltage divider circuit example."""
        # Reset circuit for clean test
        default_circuit.reset()
        
        # Create input & output voltages and ground reference.
        vin, vout, gnd = Net('VI'), Net('VO'), Net('GND')

        # Create two resistors.
        r1, r2 = 2 * Part("Device", 'R', TEMPLATE,
                          footprint='Resistor_SMD.pretty:R_0805_2012Metric')
        r1.value = '1K'   # Set upper resistor value.
        r2.value = '500'  # Set lower resistor value.

        # Connect the nets and resistors.
        vin += r1[1]      # Connect the input to the upper resistor.
        gnd += r2[2]      # Connect the lower resistor to ground.
        # Output comes from the connection of the two resistors.
        vout += r1[2], r2[1]
        
        # Verify connections
        assert len(vin.pins) == 1
        assert len(gnd.pins) == 1
        assert len(vout.pins) == 2        # Verify resistor values
        assert r1.value == '1K'
        assert r2.value == '500'
        
        # Verify pin connections
        assert r1[1] in vin.pins
        assert r2[2] in gnd.pins
        assert r1[2] in vout.pins
        assert r2[1] in vout.pins

    def test_accessing_skidl(self):
        """Test that SKiDL can be imported successfully."""
        # This test passes if the imports at the top work
        assert 'skidl' in sys.modules
        
    def test_part_instantiation(self):
        """Test basic part instantiation examples."""
        default_circuit.reset()
        
        # Basic resistor creation
        resistor = Part('Device', 'R')
        assert resistor.name == 'R'
        assert resistor.ref.startswith('R')
        assert resistor.ref == "R1"
        
        # Set value attribute
        resistor.value = '1K'
        assert resistor.value == '1K'
        
        # Create with attributes
        resistor2 = Part('Device', 'R', value='2K')
        assert resistor2.value == '2K'
        assert resistor2.ref == "R2"
        
        # Test reference assignment
        resistor.ref = 'R5'
        resistor2.ref = 'R5'
        assert resistor.ref == 'R5'
        assert resistor2.ref == 'R5_1'

    def test_pin_connections(self):
        """Test pin connection examples."""
        default_circuit.reset()
        
        # Create parts with footprints
        rup = Part("Device", 'R', value='1K',
                   footprint='Resistor_SMD.pretty:R_0805_2012Metric')
        rlow = Part("Device", 'R', value='500',
                    footprint='Resistor_SMD.pretty:R_0805_2012Metric')
        
        # Create nets
        v_in = Net('VIN')
        gnd = Net('GND')
        
        # Make connections
        rup[1] += v_in
        rlow[1] += gnd
        
        # Verify connections
        assert rup[1].net == v_in
        assert rlow[1].net == gnd
        assert rup[1] in v_in.pins
        assert rlow[1] in gnd.pins
        
        # Test output connection two ways
        v_out = Net('VO')
        v_out += rup[2], rlow[2]
        
        assert rup[2].net == v_out
        assert rlow[2].net == v_out
        assert len(v_out.pins) == 2

    def test_erc_functionality(self):
        """Test basic ERC functionality."""
        default_circuit.reset()
        
        # Create simple circuit
        r1 = Part('Device', 'R', value='1K')
        r2 = Part('Device', 'R', value='500')
        
        vin = Net('VIN')
        gnd = Net('GND')
        vout = Net('VO')
        
        vin += r1[1]
        gnd += r2[2]
        vout += r1[2], r2[1]
        
        # Disable ERC for single-pin nets to avoid warnings
        vin.do_erc = False
        gnd.do_erc = False
        
        # Run ERC - should pass without errors
        ERC()
        # Test passes if no exceptions are raised


class TestSkidlObjects:
    """Test SKiDL object creation and manipulation."""
    
    def test_part_pin_net_bus_creation(self):
        """Test basic SKiDL object creation."""
        default_circuit.reset()
        
        # Test Part creation
        my_part = Part('Device', 'R')
        assert isinstance(my_part, Part)
        assert my_part.name == 'R'
        
        # Test Net creation
        Net()
        named_net = Net('Fred')
        assert named_net.name == 'Fred'
        
        # Test Bus creation
        my_bus = Bus('bus_name', 8)
        assert my_bus.name == 'bus_name'
        assert my_bus.width == 8
        
        anon_bus = Bus(4)
        assert anon_bus.width == 4

    def test_bus_from_existing_objects(self):
        """Test creating buses from existing nets and pins."""
        default_circuit.reset()
        
        my_part = Part('Device', 'R')
        a_net = Net('A')
        b_net = Net('B')
        
        # Bus from nets
        bus_nets = Bus('net_bus', a_net, b_net)
        assert bus_nets.width == 2
        
        # Bus from pins
        bus_pins = Bus('pin_bus', my_part[1], my_part[2])
        assert bus_pins.width == 2

    def test_part_copying(self):
        """Test part copying functionality."""
        default_circuit.reset()
        
        r1 = Part('Device', 'R', value=500)
        
        # Single copy
        r2 = r1.copy()
        assert r2.value == 500
        assert r2.ref != r1.ref
        
        # Copy with different value
        r3 = r1.copy(value='1K')
        assert r3.value == '1K'
        
        # Copy using call syntax
        r4 = r1(value='1K')
        assert r4.value == '1K'
        
        # Multiple copies
        r5, r6, r7 = r1(3, value='1K')
        assert all(r.value == '1K' for r in [r5, r6, r7])
        
        # Multiple copies with different values
        r8, r9, r10 = r1(value=[110, 220, 330])
        assert r8.value == 110
        assert r9.value == 220
        assert r10.value == 330
        
        # Using * operator
        r11, r12 = 2 * r1
        assert r11.value == 500
        assert r12.value == 500

    def test_template_parts(self):
        """Test template part creation."""
        default_circuit.reset()
        
        # Create template part
        rt = Part('Device', 'R', dest=TEMPLATE)
        
        # Template should not be in circuit
        assert rt not in default_circuit.parts
        
        # Create copies from template
        r1, r2, r3 = rt(3, value='1K')
        
        # Copies should be in circuit
        assert all(r in default_circuit.parts for r in [r1, r2, r3])
        assert all(r.value == '1K' for r in [r1, r2, r3])


class TestPinAccess:
    """Test various ways of accessing part pins."""
    
    def test_pin_number_access(self):
        """Test accessing pins by number."""
        default_circuit.reset()
        
        # Create a part with multiple pins
        pic10 = Part('MCU_Microchip_PIC10', 'pic10f220-iot')
        
        # Access single pin by number
        pin3 = pic10[3]
        assert pin3.num == '3'
        
        # Access multiple pins
        # Cast NetPinList to list so standard indexing works.
        pins = list(pic10[3, 1, 6])
        assert len(pins) == 3
        assert pins[0].num == '3'
        assert pins[1].num == '1'
        assert pins[2].num == '6'
        
        # Test slice notation
        slice_pins = pic10[2:4]
        assert len(slice_pins) == 3  # pins 2, 3, 4
        
        # Test all pins
        all_pins = pic10[:]
        assert len(all_pins) == len(pic10.pins)

    def test_pin_name_access(self):
        """Test accessing pins by name."""
        default_circuit.reset()
        
        pic10 = Part('MCU_Microchip_PIC10', 'pic10f220-iot')
        
        # Access by pin name
        vdd_pin = pic10['VDD']
        assert 'VDD' in vdd_pin.name
        
        # Access multiple pins by name
        power_pins = pic10['VDD', 'VSS']
        assert len(power_pins) == 2
        
        # Test space/comma delimited string
        gp_pins = pic10['GP0 GP1 GP2']
        assert len(gp_pins) == 3

    def test_pin_attribute_access(self):
        """Test accessing pins as attributes."""
        default_circuit.reset()
        
        pic10 = Part('MCU_Microchip_PIC10', 'pic10f220-iot')
        
        # Access pin by attribute with 'p' prefix
        pin2 = pic10.p2
        assert pin2.num == '2'
        
        # Access pin by name attribute
        vdd_pin = pic10.VDD
        assert 'VDD' in vdd_pin.name

    def test_pin_aliases(self):
        """Test pin alias functionality."""
        default_circuit.reset()
        
        r = Part('Device', 'R')
        
        # Add alias to pin
        r[2].aliases += 'pullup'
        assert 'pullup' in r[2].aliases
        
        # Access pin by alias
        pullup_pin = r['pullup']
        assert pullup_pin == r[2]


class TestConnections:
    """Test different connection methods."""
    
    def test_basic_connections(self):
        """Test basic connection operations."""
        default_circuit.reset()
        
        pic10 = Part('MCU_Microchip_PIC10', 'pic10f220-iot')
        
        # Net-to-pin connection
        io = Net('IO_NET')
        pic10.GP0 += io
        assert pic10.GP0 in io.pins
        
        # Pin-to-net connection (reverse)
        pic10_2 = Part('MCU_Microchip_PIC10', 'pic10f220-iot')
        io2 = Net('IO_NET2')
        io2 += pic10_2.GP0
        assert pic10_2.GP0 in io2.pins
        
        # Pin-to-pin connection (creates implicit net)
        pic10_3 = Part('MCU_Microchip_PIC10', 'pic10f220-iot')
        pic10_3.GP1 += pic10_3.GP2
        assert pic10_3.GP1.net == pic10_3.GP2.net

    def test_multiple_connections(self):
        """Test connecting multiple pins at once."""
        default_circuit.reset()
        
        pic10 = Part('MCU_Microchip_PIC10', 'pic10f220-iot')
        
        # Connect multiple pins to one pin
        pic10[1] += pic10[2, 3, 6]
        common_net = pic10[1].net
        
        assert pic10[2].net == common_net
        assert pic10[3].net == common_net
        assert pic10[6].net == common_net
        assert len(common_net.pins) == 4

    def test_bus_connections(self):
        """Test bus to pin connections."""
        default_circuit.reset()
        
        pic10 = Part('MCU_Microchip_PIC10', 'pic10f220-iot')
        
        # Create bus and connect to pins
        b = Bus('GP', 3)
        pic10['GP2 GP1 GP0'] += b[2:0]
        
        # Verify connections
        assert pic10['GP2'].net == b[2]
        assert pic10['GP1'].net == b[1] 
        assert pic10['GP0'].net == b[0]


class TestNetworkSyntax:
    """Test serial, parallel, and tee network syntax."""
    
    def test_serial_network(self):
        """Test series network using & operator."""
        default_circuit.reset()
        
        vcc, gnd = Net('VCC'), Net('GND')
        r = Part('Device', 'R', dest=TEMPLATE)
        r1, r2, r3, r4 = r * 4
        
        # Create series network
        ser_ntwk = vcc & r1 & r2 & r3 & r4 & gnd
        
        # Verify that components are connected in series
        # Each resistor should have one pin connected to previous and one to next
        assert len(r1[1].net.pins) >= 1  # Connected to VCC
        assert len(r1[2].net.pins) >= 1  # Connected to r2
        assert len(r4[1].net.pins) >= 1  # Connected to r3
        assert len(r4[2].net.pins) >= 1  # Connected to GND

    def test_parallel_network(self):
        """Test parallel network using | operator."""
        default_circuit.reset()
        
        vcc, gnd = Net('VCC'), Net('GND')
        r = Part('Device', 'R', dest=TEMPLATE)
        r1, r2, r3, r4 = r * 4
        
        # Create parallel network
        par_ntwk = vcc & (r1 | r2 | r3 | r4) & gnd
        
        # In parallel, all resistors should share common nodes
        # All first pins should be on same net (connected to VCC)
        # All second pins should be on same net (connected to GND)
        first_net = r1[1].net
        second_net = r1[2].net
        
        assert r2[1].net == first_net
        assert r3[1].net == first_net
        assert r4[1].net == first_net
        
        assert r2[2].net == second_net
        assert r3[2].net == second_net
        assert r4[2].net == second_net

    def test_combo_network(self):
        """Test combination of series and parallel networks."""
        default_circuit.reset()
        
        vcc, gnd = Net('VCC'), Net('GND')
        r = Part('Device', 'R', dest=TEMPLATE)
        r1, r2, r3, r4 = r * 4
        
        # Series pairs in parallel
        combo_ntwk = vcc & ((r1 & r2) | (r3 & r4)) & gnd
        
        # r1 and r2 should be in series
        assert r1[2].net == r2[1].net
        # r3 and r4 should be in series  
        assert r3[2].net == r4[1].net
        
        # The series pairs should be in parallel
        assert r1[1].net == r3[1].net  # Common input
        assert r2[2].net == r4[2].net  # Common output

    def test_tee_network(self):
        """Test tee network functionality."""
        default_circuit.reset()
        
        inp, outp, gnd = Net('INPUT'), Net('OUTPUT'), Net('GND')
        l = Part('Device', 'L')
        c = Part('Device', 'C', dest=TEMPLATE)
        cs, cl = c * 2
        
        # Pi matching network
        pi_ntwk = inp & tee(cs & gnd) & l & tee(cl & gnd) & outp
        
        # Verify tee connections exist
        assert cs[1].net.pins == inp.pins  # cs connected to input
        assert cs[2].net.pins == gnd.pins  # cs connected to ground
        assert cl[1].net.pins == outp.pins  # cl connected to output
        assert cl[2].net.pins == gnd.pins  # cl connected to ground


class TestHierarchy:
    """Test hierarchical design methods."""
    
    def test_subcircuit_decorator_interface(self):
        """Test SubCircuit decorator with Interface return."""
        default_circuit.reset()
        
        # Define templates
        r_template = Part('Device', 'R',
                          footprint='Resistor_SMD.pretty:R_0805_2012Metric',
                          dest=TEMPLATE)
        
        @SubCircuit
        def voltage_reference():
            """Creates a 2.5V voltage reference using a voltage divider."""
            vcc_local, gnd_local = Net('VCC_LOCAL'), Net('GND_LOCAL')
            
            # Create voltage divider
            r_upper = r_template(value='10K')
            r_lower = r_template(value='10K')
            vcc_local & r_upper & r_lower & gnd_local
            
            # Return interface with the reference voltage
            return Interface(
                vref=r_upper[2],  # Junction between resistors
                vcc=vcc_local,
                gnd=gnd_local
            )
        
        # Create subcircuit
        vref_if = voltage_reference()
        
        # Verify interface
        assert hasattr(vref_if, 'vref')
        assert hasattr(vref_if, 'vcc')
        assert hasattr(vref_if, 'gnd')
        
        # Connect to external nets
        power_5v = Net('5V')
        system_gnd = Net('SYSTEM_GND')
        power_5v += vref_if.vcc
        system_gnd += vref_if.gnd
        
        # Verify connections
        assert vref_if.vcc.pins == power_5v.pins
        assert vref_if.gnd.pins == system_gnd.pins

    def test_subcircuit_subclassing(self):
        """Test SubCircuit subclassing with I/O attributes."""
        default_circuit.reset()
        
        class VoltageRegulator(SubCircuit):
            """3.3V linear voltage regulator module."""
            
            def __init__(self, input_voltage=5.0):
                super().__init__()
                
                # Create the regulator circuit
                reg = Part('Regulator_Linear', 'AMS1117-3.3')
                c_in = Part('Device', 'C', value='100nF')
                c_out = Part('Device', 'C', value='10uF')
                
                # Define I/O attributes first
                self.vin = Net('VIN_REG')
                self.vout = Net('VOUT_REG')
                self.gnd = Net('GND_REG')
                
                # Build regulator circuit
                self.vin & c_in & self.gnd
                self.vin & reg['VI']
                reg['VO'] & c_out & self.gnd
                reg['VO'] & self.vout
                reg['GND'] & self.gnd
        
        # Instantiate regulator
        regulator = VoltageRegulator()

        # Verify I/O attributes exist
        assert hasattr(regulator, 'vin')
        assert hasattr(regulator, 'vout')
        assert hasattr(regulator, 'gnd')
        
        # Connect to external power
        power_12v = Net('12V_IN')
        power_3v3 = Net('3V3')
        system_gnd = Net('GND')
        
        power_12v += regulator.vin
        power_3v3 += regulator.vout
        system_gnd += regulator.gnd

    def test_context_based_hierarchy(self):
        """Test context-based hierarchy with SubCircuit."""
        default_circuit.reset()
        
        # Create main system nets
        vcc_5v = Net('VCC_5V')
        vcc_3v3 = Net('VCC_3V3')
        gnd = Net('GND')
        
        # Power supply section
        with SubCircuit('power_supply') as power:
            reg = Part('Regulator_Linear', 'AMS1117-3.3')
            c1 = Part('Device', 'C', value='100nF')
            c2 = Part('Device', 'C', value='10uF')
            
            vcc_5v & c1 & gnd
            vcc_5v & reg['VI']
            reg['VO'] & c2 & gnd
            reg['VO'] & vcc_3v3
            reg['GND'] & gnd
        
        # Microcontroller section
        with SubCircuit('microcontroller') as mcu_section:
            mcu = Part('MCU_ST_STM32F1', 'STM32F103C8Tx')
            
            # Power connections
            mcu['VDD'] += vcc_3v3
            mcu['VSS'] += gnd
        
        # Verify hierarchy was created
        assert {child.name for child in default_circuit.root.children} == {'power_supply1', 'microcontroller1'}


class TestPartClasses:
    """Test part and net class functionality."""
    
    def test_individual_part_classes(self):
        """Test individual part class assignment."""
        default_circuit.reset()
        
        # Create part classes
        passive_parts = PartClass("passive_parts", priority=1, tolerance="5%")
        active_parts = PartClass("active_parts", priority=5)
        commercial = PartClass("commercial", priority=3)
        
        # Create parts with classes
        resistor = Part("Device", "R", value="1K",
                        partclasses=(passive_parts, commercial))
        
        # Verify classes are assigned
        assert passive_parts in resistor.partclasses
        assert commercial in resistor.partclasses
        
        # Test separate assignment
        vreg = Part("Regulator_Linear", "AMS1117-3.3")
        vreg.partclasses = active_parts, commercial
        
        assert active_parts in vreg.partclasses
        assert commercial in vreg.partclasses

    def test_individual_net_classes(self):
        """Test individual net class assignment."""
        default_circuit.reset()
        
        # Create net classes
        high_speed = NetClass("high_speed", priority=2, width="0.1mm",
                              impedance="50ohm")
        power_nets = NetClass("power_nets", priority=4, width="0.5mm",
                              clearance="0.3mm")
        
        # Create nets with classes
        vcc_5v = Net("VCC_5V", netclasses=power_nets)
        data_bus = Bus("DATA", 8, netclasses=high_speed)
        
        # Verify classes are assigned
        assert power_nets in vcc_5v.netclasses
        assert high_speed in data_bus.netclasses


class TestPartFields:
    """Test part field functionality."""
    
    def test_part_fields_access(self):
        """Test accessing and modifying part fields."""
        default_circuit.reset()
        
        lm35 = Part('Sensor_Temperature', 'LM35-D')
        
        # Verify fields exist
        assert hasattr(lm35, 'fields')
        assert isinstance(lm35.fields, dict)
        
        # Add new field
        lm35.fields['new_field'] = 'new value'
        assert lm35.fields['new_field'] == 'new value'
        
        # Access as attribute
        assert lm35.new_field == 'new value'
        
        # Modify as attribute
        lm35.new_field = 'another new value'
        assert lm35.new_field == 'another new value'
        assert lm35.fields['new_field'] == 'another new value'


class TestAdvancedFeatures:
    """Test advanced SKiDL features."""
    
    def test_no_connects(self):
        """Test no-connect functionality."""
        default_circuit.reset()
        
        pic10 = Part('MCU_Microchip_PIC10', 'pic10f220-iot')
        
        # Connect some pins to NC
        pic10[1, 3, 4] += NC
        
        # Verify pins are connected to NC net
        assert pic10[1].net.name == NC.name
        assert pic10[3].net.name == NC.name
        assert pic10[4].net.name == NC.name
        assert pic10[4].net == NC

        # Test that connecting to normal net removes from NC
        normal_net = Net('NORMAL')
        pic10[1] += normal_net
        assert pic10[1].net == normal_net
        assert pic10[1] not in NC.pins

    def test_net_drive_levels(self):
        """Test net drive level functionality."""
        default_circuit.reset()
        
        pic10 = Part('MCU_Microchip_PIC10', 'pic10f220-iot')
        a = Net('POWER_NET')
        pic10['VDD'] += a
        
        # Set drive level
        a.drive = POWER
        assert a.drive == POWER

    def test_pin_drive_levels(self):
        """Test pin drive level functionality."""
        default_circuit.reset()
        
        pic10_a = Part('MCU_Microchip_PIC10', 'pic10f220-iot')
        pic10_b = Part('MCU_Microchip_PIC10', 'pic10f220-iot')
        
        pic10_b['VDD'] += pic10_a[1]
        
        # Set pin drive level
        pic10_a[1].drive = POWER
        assert pic10_a[1].drive == POWER

    def test_equivalencies(self):
        """Test pin, net, bus equivalencies."""
        default_circuit.reset()
        
        a = Net('A')
        b = Bus('B', 8)
        c = Pin()
        
        # Test boolean operations
        assert bool(a) is True
        assert bool(b) is True
        assert bool(c) is True
        
        # Test width property
        assert a.width == 1
        assert b.width == 8
        assert c.width == 1
        
        # Test indexing
        assert a[0] == a
        assert c[0] == c

    def test_erc_suppression(self):
        """Test selective ERC suppression."""
        default_circuit.reset()
        
        my_net = Net('TEST_NET')
        my_part = Part('Device', 'R')
        
        # Test ERC flags
        my_net.do_erc = False
        my_part[1].do_erc = False
        my_part.do_erc = False
        
        assert my_net.do_erc is False
        assert my_part[1].do_erc is False
        assert my_part.do_erc is False

    def test_custom_erc_assert(self):
        """Test custom ERC assertions."""
        default_circuit.reset()
        
        def get_fanout(net):
            """Count input pins on a net."""
            fanout = 0
            for pin in net.get_pins():
                if pin.func in (Pin.funcs.INPUT, Pin.funcs.BIDIR):
                    fanout += 1
            return fanout
        
        net1 = Net('TEST_NET1')
        
        # Add assertion
        erc_assert('get_fanout(net1) < 5', 'failed on net1')
        
        # Add pins to test assertion
        net1 += Pin(func=Pin.funcs.OUTPUT)
        net1 += Pin(func=Pin.funcs.INPUT) * 3  # Should pass
        
        # Test that assertion was added
        # (We can't easily test execution without running full ERC)
        assert len(default_circuit.erc_assertion_list) == 1

    def test_tags(self):
        """Test part and subcircuit tagging."""
        default_circuit.reset()
        
        # Create parts with tags
        r = Part('Device', 'R', dest=TEMPLATE)
        
        r1 = r(value='1K', tag='r_upper')
        r2 = r(value='500', tag='r_lower')
        
        # Verify tags are set
        assert r1.tag == 'r_upper'
        assert r2.tag == 'r_lower'


class TestCircuitObjects:
    """Test Circuit object functionality."""
    
    def test_custom_circuit_creation(self):
        """Test creating custom Circuit objects."""
        default_circuit.reset()
        
        # Create new circuit
        my_circuit = Circuit()
        
        # Add components to custom circuit
        my_circuit += Part("Device", 'R', circuit=my_circuit)
        my_circuit += Net('GND', circuit=my_circuit)
        my_circuit += Bus('byte_bus', 8, circuit=my_circuit)
        
        # Verify components are in the custom circuit
        assert len(my_circuit.parts) >= 1
        assert len(my_circuit.nets) >= 1
        assert len(my_circuit.buses) >= 1

    def test_circuit_context_manager(self):
        """Test using Circuit as context manager."""
        default_circuit.reset()
        
        my_circuit = Circuit()
        
        with my_circuit:
            p = Part('Device', 'R')
            n = Net('GND')
            b = Bus('byte_bus', 8)
        
        # Components should be in my_circuit, not default_circuit
        assert p in my_circuit.parts
        assert n in my_circuit.nets
        assert b in my_circuit.buses


class TestLibraries:
    """Test library functionality."""
    
    def test_library_creation(self):
        """Test creating ad-hoc libraries."""
        default_circuit.reset()
        
        # Create empty library
        my_lib = SchLib(name='my_lib')
        
        # Add part template to library
        r_template = Part('Device', 'R', dest=TEMPLATE)
        my_lib += r_template
        
        # Verify library contains the part
        assert len(my_lib) >= 1


class TestNetlistGeneration:
    """Test netlist generation functionality."""
    
    def test_generate_netlist_basic(self):
        """Test basic netlist generation."""
        default_circuit.reset()
        
        # Create simple circuit
        r1 = Part('Device', 'R', value='1K',
                  footprint='Resistor_SMD.pretty:R_0805_2012Metric')
        r2 = Part('Device', 'R', value='500',
                  footprint='Resistor_SMD.pretty:R_0805_2012Metric')
        
        vin = Net('VIN')
        vout = Net('VOUT')
        gnd = Net('GND')
        
        vin += r1[1]
        vout += r1[2], r2[1]
        gnd += r2[2]
        
        # Disable ERC warnings for single-pin nets
        vin.do_erc = False
        gnd.do_erc = False
        
        # Test netlist generation to string
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.net',
                                         delete=False) as f:
            try:
                generate_netlist(file_=f)
                f.seek(0)
                netlist_content = f.read()
                
                # Verify netlist contains expected elements
                assert 'export' in netlist_content
                assert 'components' in netlist_content
                assert 'nets' in netlist_content
                assert 'R1' in netlist_content or 'R2' in netlist_content
                
            finally:
                os.unlink(f.name)


class TestGenerateSVG:
    """Test SVG schematic generation."""
    
    def test_svg_generation_basic(self):
        """Test basic SVG generation."""
        default_circuit.reset()
        
        # Create simple AND gate circuit from docs
        q = Part(lib="Transistor_BJT", name="Q_PNP_CBE", dest=TEMPLATE,
                 symtx="V")
        r = Part("Device", "R", dest=TEMPLATE)
        
        # Create nets
        gnd, vcc = Net("GND"), Net("VCC")
        a, b, a_and_b = Net("A"), Net("B"), Net("A_AND_B")
        
        # Set net I/O types for better SVG
        a.netio = "i"
        b.netio = "i"
        a_and_b.netio = "o"
        
        # Instantiate parts
        q1, q2 = q(2)
        r1, r2, r3, r4, r5 = r(5, value="10K")
        
        # Make connections
        a & r1 & q1["B", "C"] & r4 & q2["B", "C"] & a_and_b & r5 & gnd
        b & r2 & q1["B"]
        q1["C"] & r3 & gnd
        vcc += q1["E"], q2["E"]
        
        # Test SVG generation
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.svg',
                                         delete=False) as f:
            try:
                # Note: SVG generation requires netlistsvg which might
                # not be installed
                # This test mainly verifies the function can be called
                # without error
                generate_svg(file_=f.name)
                
                # If we get here without exception, basic test passes
                assert True
                
            except Exception as e:
                # If netlistsvg is not installed, we expect a specific error
                # The test should not fail for missing external dependencies
                if "netlistsvg" in str(e) or "not found" in str(e).lower():
                    pytest.skip("netlistsvg not installed - skipping "
                                "SVG generation test")
                else:
                    # Re-raise unexpected errors
                    raise
            finally:
                if os.path.exists(f.name):
                    os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__])
