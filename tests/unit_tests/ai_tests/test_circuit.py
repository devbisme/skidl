"""
Unit tests for the Circuit class.

This module contains comprehensive tests for the Circuit class functionality
including circuit initialization, component management, electrical rule checking,
and various output generation methods.
"""

import builtins
import json
import os
import tempfile
from collections import Counter
from unittest.mock import Mock, patch, mock_open

import pytest

from skidl import Circuit, Net, Part, Bus, SchLib, SKIDL
from skidl.net import NCNet
from skidl.netclass import NetClass
from skidl.node import Node
from skidl.pin import Pin


class TestCircuitInitialization:
    """Test circuit initialization and basic properties."""

    def test_circuit_creation_default(self):
        """Test creating a circuit with default parameters."""
        circuit = Circuit()
        
        assert circuit.name == ""
        assert circuit.parts == []
        assert circuit.nets == [circuit.NC]
        assert circuit.buses == []
        assert circuit.interfaces == []
        assert isinstance(circuit.NC, NCNet)
        assert circuit.NC.name == "__NOCONNECT"
        assert circuit.track_src is True
        assert circuit.track_abs_path is False
        assert circuit.no_files is False

    def test_circuit_creation_with_kwargs(self):
        """Test creating a circuit with custom attributes."""
        circuit = Circuit(name="TestCircuit", custom_attr="test_value")
        
        assert circuit.name == "TestCircuit"
        assert circuit.custom_attr == "test_value"

    def test_circuit_context_manager(self):
        """Test using circuit as a context manager."""
        original_circuit = builtins.default_circuit
        original_nc = builtins.NC
        
        test_circuit = Circuit(name="TestContext")
        
        with test_circuit as circuit:
            assert builtins.default_circuit is test_circuit
            assert builtins.NC is test_circuit.NC
            assert circuit is test_circuit
        
        # Check that original values are restored
        assert builtins.default_circuit is original_circuit
        assert builtins.NC is original_nc

    def test_circuit_reset(self):
        """Test circuit reset functionality."""
        try:
            with Circuit() as circuit:
                
                # Add some components
                part = Part("Device", "R")
                net = Net("TEST_NET")
                
                assert len(circuit.parts) == 1
                assert len(circuit.nets) == 2
                
                # Reset circuit
                circuit.reset()
                
                assert len(circuit.parts) == 0
                assert len(circuit.nets) == 1  # Only NC net remains
                assert circuit.nets[0] is circuit.NC
        except IndexError:
            # The reset erased the circuit's stack which causes an error upon leaving the context.
            pass

    def test_circuit_mini_reset(self):
        """Test mini reset functionality."""
        try:
            with Circuit() as circuit:
                
                # Add some components
                part = Part("Device", "R")
                net = Net("TEST_NET")
                
                original_nc = circuit.NC
                
                circuit.mini_reset()
                
                assert len(circuit.parts) == 0
                assert len(circuit.nets) == 1  # Only NC net remains
                assert circuit.NC is not original_nc  # New NC net created
        except IndexError:
            # The mini_reset erased the circuit's stack which causes an error upon leaving the context.
            pass

class TestComponentManagement:
    """Test adding and removing circuit components."""

    def test_add_parts(self):
        """Test adding parts to the circuit."""
        with Circuit() as circuit:
            part1 = Part("Device", "R")
            part2 = Part("Device", "C")

            circuit += part1, part2

            assert len(circuit.parts) == 2
            assert part1 in circuit.parts
            assert part2 in circuit.parts
            assert part1.circuit is circuit
            assert part2.circuit is circuit

    def test_remove_parts(self):
        """Test removing parts from the circuit."""
        with Circuit() as circuit:
            part1 = Part("Device", "R")
            part2 = Part("Device", "C")
            
            circuit += part1, part2
            circuit -= part1
            
            assert len(circuit.parts) == 1
            assert part1 not in circuit.parts
            assert part2 in circuit.parts
            assert part1.circuit is None

    def test_add_nets(self):
        """Test adding nets to the circuit."""
        circuit = Circuit()
        net1 = Net("VCC")
        net2 = Net("GND")
        
        circuit += net1, net2
        
        assert len(circuit.nets) == 3  # Including NC net
        assert net1 in circuit.nets
        assert net2 in circuit.nets
        assert net1.circuit is circuit
        assert net2.circuit is circuit

    def test_remove_nets(self):
        """Test removing nets from the circuit."""
        circuit = Circuit()
        net1 = Net("VCC")
        net2 = Net("GND")
        
        circuit += net1, net2
        circuit -= net1
        
        assert len(circuit.nets) == 2  # GND + NC
        assert net1 not in circuit.nets
        assert net2 in circuit.nets
        assert net1.circuit is None

    def test_add_buses(self):
        """Test adding buses to the circuit."""
        circuit = Circuit()
        bus = Bus("DATA", 8)
        
        circuit += bus
        
        assert len(circuit.buses) == 1
        assert bus in circuit.buses
        assert bus.circuit is circuit
        # Bus nets should also be added
        assert len(circuit.nets) > 1

    def test_remove_buses(self):
        """Test removing buses from the circuit."""
        circuit = Circuit()
        bus = Bus("DATA", 8)
        
        circuit += bus
        initial_net_count = len(circuit.nets)
        
        circuit -= bus
        
        assert len(circuit.buses) == 0
        assert bus not in circuit.buses
        assert bus.circuit is None
        # Bus nets should also be removed
        assert len(circuit.nets) < initial_net_count

    def test_add_invalid_type(self):
        """Test adding invalid types raises error."""
        circuit = Circuit()
        
        with pytest.raises(ValueError, match="Can't add a.*to a Circuit object"):
            circuit += "invalid_string"

    def test_remove_invalid_type(self):
        """Test removing invalid types raises error."""
        circuit = Circuit()
        
        with pytest.raises(ValueError, match="Can't remove a.*from a Circuit object"):
            circuit -= "invalid_string"


class TestNetClassManagement:
    """Test net class management functionality."""

    def test_add_netclasses(self):
        """Test adding net classes to the circuit."""
        circuit = Circuit()
        netclass = NetClass("Power", trace_width=0.5)
        
        circuit.add_netclasses(netclass)
        
        assert "Power" in circuit.netclasses
        assert circuit.netclasses["Power"] is netclass

    def test_add_partclasses(self):
        """Test adding part classes to the circuit."""
        circuit = Circuit()
        # Create a mock part class
        partclass = Mock()
        partclass.name = "Resistors"
        
        circuit.add_partclasses(partclass)
        
        assert "Resistors" in circuit.partclasses
        assert circuit.partclasses["Resistors"] is partclass


class TestHierarchicalNodes:
    """Test hierarchical node management."""

    def test_activate_node(self):
        """Test activating a new hierarchical node."""
        circuit = Circuit()
        initial_node = circuit.active_node
        
        new_node = circuit.activate("SubCircuit", "tag1")
        
        assert circuit.active_node is new_node
        assert new_node.parent is initial_node
        assert new_node.name == "SubCircuit1"
        assert new_node.tag == "tag1"
        assert new_node in circuit.nodes

    def test_deactivate_node(self):
        """Test deactivating a hierarchical node."""
        circuit = Circuit()
        initial_node = circuit.active_node
        
        sub_node = circuit.activate("SubCircuit", "tag1")
        circuit.deactivate()
        
        assert circuit.active_node is initial_node

    def test_get_node_names(self):
        """Test getting hierarchical node names."""
        circuit = Circuit()
        
        # Create some nodes
        circuit.activate("Sub1", "tag1")
        circuit.activate("Sub2", "tag2")
        
        node_names = list(circuit.get_node_names())
        
        # Should include root node and created nodes
        assert len(node_names) >= 3


class TestNetManagement:
    """Test advanced net management functionality."""

    def test_get_nets_excludes_nc_and_empty(self):
        """Test get_nets excludes NC nets and empty nets."""
        with Circuit() as circuit:
            
            # Create various nets
            vcc = Net("VCC")
            gnd = Net("GND")
            empty_net = Net("EMPTY")
            
            # Connect some pins to make nets non-empty
            part = Part("Device", "R")
            vcc += part[1]
            gnd += part[2]
            # empty_net has no connections
            
            distinct_nets = circuit.get_nets()
            
            assert vcc in distinct_nets
            assert gnd in distinct_nets
            assert empty_net not in distinct_nets  # Empty net excluded
            assert circuit.NC not in distinct_nets  # NC net excluded

    def test_merge_net_names(self):
        """Test merging names of multi-segment nets."""
        with Circuit() as circuit:
        
            # Create nets that will be merged
            net1 = Net("SIG_A")
            net2 = Net("SIG_B")
            
            # Create a shared pin to merge the nets
            part = Part("Device", "R")
            shared_pin = part[1]
            
            net1 += shared_pin
            net2 += shared_pin  # This should merge the nets
            
            circuit.merge_net_names()
            
            # Both nets should have the same name after merging
            assert net1.name == net2.name

    def test_cull_unconnected_parts(self):
        """Test removing unconnected parts."""
        with Circuit() as circuit:
            
            # Create parts - one connected, one not
            connected_part = Part("Device", "R")
            unconnected_part = Part("Device", "R")
            
            # Connect only one part
            net = Net("VCC")
            net += connected_part[1]
            
            circuit += connected_part, unconnected_part, net
            
            assert len(circuit.parts) == 2
            
            circuit.cull_unconnected_parts()
            
            assert len(circuit.parts) == 1
            assert connected_part in circuit.parts
            assert unconnected_part not in circuit.parts


class TestERCFunctionality:
    """Test Electrical Rule Checking functionality."""

    @patch('skidl.circuit.erc_logger')
    @patch('skidl.circuit.active_logger')
    def test_erc_basic_execution(self, mock_active_logger, mock_erc_logger):
        """Test basic ERC execution."""
        circuit = Circuit()
        
        # Mock the logger stack operations
        mock_active_logger.push = Mock()
        mock_active_logger.pop = Mock()
        mock_active_logger.error.reset = Mock()
        mock_active_logger.warning.reset = Mock()
        mock_active_logger.report_summary = Mock()
        mock_active_logger.stop_file_output = Mock()
        
        # Run ERC
        circuit.ERC()
        
        # Verify logger operations
        mock_active_logger.push.assert_called_once_with(mock_erc_logger)
        mock_active_logger.pop.assert_called_once()
        mock_active_logger.error.reset.assert_called_once()
        mock_active_logger.warning.reset.assert_called_once()
        mock_active_logger.report_summary.assert_called_once_with("running ERC")

    def test_erc_with_no_files(self):
        """Test ERC execution with file output disabled."""
        circuit = Circuit()
        circuit.no_files = True
        
        # Mock the logger to avoid actual file operations
        with patch('skidl.circuit.active_logger') as mock_logger:
            mock_logger.push = Mock()
            mock_logger.pop = Mock()
            mock_logger.error.reset = Mock()
            mock_logger.warning.reset = Mock()
            mock_logger.report_summary = Mock()
            mock_logger.stop_file_output = Mock()
            
            circuit.ERC()
            
            mock_logger.stop_file_output.assert_called_once()


class TestFootprintAndTagChecking:
    """Test footprint and tag validation functionality."""

    def test_check_for_empty_footprints(self):
        """Test checking for parts with empty footprints."""
        circuit = Circuit()
        
        # Create part without footprint
        part = Part("Device", "R")
        part.footprint = ""
        circuit += part
        
        # Mock the empty footprint handler
        with patch('skidl.empty_footprint_handler') as mock_handler:
            circuit.check_for_empty_footprints()
            mock_handler.assert_called_once_with(part)

    def test_check_tags(self):
        """Test checking for missing tags."""
        circuit = Circuit()
        
        # Create part and node
        part = Part("Device", "R")
        circuit += part
        node = circuit.activate("TestNode", "")
        circuit.check_tags()


class TestOutputGeneration:
    """Test various output generation methods."""

    def test_generate_netlist(self):
        """Test netlist generation."""
        circuit = Circuit(name="TestCircuit")
        r, c = Part("Device", "R"), Part("Device", "C")
        circuit += r
        circuit += c
        r | c
        result = circuit.generate_netlist()

    def test_generate_xml(self):
        """Test XML generation."""
        circuit = Circuit(name="TestCircuit")
        r, c = Part("Device", "R"), Part("Device", "C")
        circuit += r
        circuit += c
        r | c
        result = circuit.generate_xml()

    def test_generate_svg(self):
        """Test SVG generation."""
        with Circuit(name="TestCircuit") as circuit:
            
            # Add a simple part and net for testing
            part = Part("Device", "R")
            net = Net("VCC")
            net += part[1,2]
            circuit += part, net
            result = circuit.generate_svg()
            
            # Should return JSON data structure
            assert isinstance(result, dict)
            assert "modules" in result
            assert "TestCircuit" in result["modules"]

    def test_generate_dot(self):
        """Test DOT file generation."""
        with Circuit(name="TestCircuit") as circuit:
            
            # Add a simple part and net for testing
            part = Part("Device", "R")
            net = Net("VCC")
            net += part[1,2]
            circuit += part, net
            result = circuit.generate_dot()

    def test_generate_pcb(self):
        """Test PCB generation."""
        with Circuit(name="TestCircuit") as circuit:
            
            # Add a simple part and net for testing
            part = Part("Device", "R", footprint="Resistor_SMD:R_0805_2012Metric")
            net = Net("VCC")
            net += part[1,2]
            circuit += part, net
            circuit.generate_pcb()

    def test_generate_schematic(self):
        """Test schematic generation."""
        with Circuit(name="TestCircuit") as circuit:
            
            # Add a simple part and net for testing
            part = Part("Device", "R")
            net = Net("VCC")
            net += part[1,2]
            circuit += part, net
            circuit.generate_schematic()


class TestSpecializedMethods:
    """Test specialized circuit methods."""

    def test_get_net_nc_stubs(self):
        """Test getting stub and no-connect nets."""
        circuit = Circuit()
        
        # Create various types of nets
        normal_net = Net("NORMAL")
        stub_net = Net("STUB")
        stub_net.stub = True
        nc_net = NCNet("NC")
        
        # Create bus with stub
        stub_bus = Bus("STUB_BUS", 4)
        stub_bus.stub = True
        
        circuit += normal_net, stub_net, nc_net, stub_bus
        
        stubs = circuit.get_net_nc_stubs()
        
        assert stub_net in stubs
        assert nc_net in stubs
        assert normal_net not in stubs
        # Bus nets should be included when bus is stub
        for net in stub_bus.nets:
            assert net in stubs

    def test_backup_parts(self):
        """Test backing up parts to library."""
        with Circuit() as circuit:
            
            # Add some parts
            part1 = Part("Device", "R")
            part2 = Part("Device", "C")
            circuit += part1, part2
            
            circuit.backup_parts()

            # Access a non-existent library and parts should be fetched from the backup library instead.
            part1_backup = Part("crap", "R")
            part2_backup = Part("crap", "C")
            

    def test_to_tuple(self):
        """Test converting circuit to tuple representation."""
        with Circuit() as circuit:
            
            # Add components
            part = Part("Device", "R")
            net = Net("VCC")
            net += part[1]
            circuit += part, net
            
            result = circuit.to_tuple()
            
            assert isinstance(result, tuple)
            assert len(result) == 2  # parts tuple and nets tuple
            
            parts_tuple, nets_tuple = result
            assert len(parts_tuple) == 1
            assert len(nets_tuple) == 1

    def test_no_files_property(self):
        """Test no_files property getter and setter."""
        circuit = Circuit()
        
        # Test default value
        assert circuit.no_files is False
        
        # Test setter
        circuit.no_files = True
        assert circuit.no_files is True
        
        circuit.no_files = False
        assert circuit.no_files is False


class TestCircuitIntegration:
    """Integration tests combining multiple circuit features."""

    def test_complete_circuit_workflow(self):
        """Test a complete circuit creation and processing workflow."""
        with Circuit(name="TestWorkFlow") as circuit:
            
            # Create components
            resistor = Part("Device", "R", value="1K")
            capacitor = Part("Device", "C", value="100nF")
            
            # Create nets
            vcc = Net("VCC")
            gnd = Net("GND")
            signal = Net("SIGNAL")
            
            # Make connections
            vcc += resistor[1]
            signal += resistor[2], capacitor[1]
            gnd += capacitor[2]
            
            # Add to circuit
            circuit += resistor, capacitor, vcc, gnd, signal
            
            # Verify circuit state
            assert len(circuit.parts) == 2
            assert len(circuit.nets) == 4  # 3 + NC net
            
            # Test that nets have expected connections
            assert len(vcc.pins) == 1
            assert len(signal.pins) == 2
            assert len(gnd.pins) == 1
            
            # Test getting distinct nets
            distinct_nets = circuit.get_nets()
            assert len(distinct_nets) == 3  # Excludes NC and empty nets

    def test_hierarchical_circuit_creation(self):
        """Test creating hierarchical circuit structures."""
        circuit = Circuit(name="HierarchicalTest")
        
        # Create main circuit components
        main_part = Part("Device", "D")
        circuit += main_part
        
        # Create subcircuit
        sub_node = circuit.activate("SubCircuit", "sub_tag")
        sub_part = Part("Device", "R")
        circuit += sub_part
        
        # Verify hierarchy
        assert main_part.node != sub_part.node
        assert sub_part.node.name == "SubCircuit1"
        assert sub_part.node.parent is not None
        
        # Return to main level
        circuit.deactivate()
        
        main_part2 = Part("Device", "C")
        circuit += main_part2
        
        # Verify back in main level
        assert main_part2.node == main_part.node

    def test_circuit_comparison_via_tuple(self):
        """Test comparing circuits using tuple representation."""
        # Create two identical circuits
        circuit1 = Circuit(name="Circuit1")
        circuit2 = Circuit(name="Circuit2")

        # Add part and net to each circuit.        
        for circuit in [circuit1, circuit2]:
            with circuit as circ:
                part = Part("Device", "R")
                net = Net("VCC")
                net += part[1]
        
        # Circuits should have same tuple representation
        assert circuit1.to_tuple() == circuit2.to_tuple()
        
        # Add different component to one circuit
        extra_part = Part("Device", "C")
        circuit2 += extra_part
        
        # Now they should be different
        assert circuit1.to_tuple() != circuit2.to_tuple()


if __name__ == "__main__":
    pytest.main([__file__])
