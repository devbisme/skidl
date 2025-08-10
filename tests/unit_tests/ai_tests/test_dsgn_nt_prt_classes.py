# -*- coding: utf-8 -*-

import pytest
import sys
from skidl import Circuit, Part, Net, Pin
from skidl.partclass import PartClass, PartClassList, DEFAULT_PARTCLASS
from skidl.netclass import NetClass, NetClassList, DEFAULT_NETCLASS
from skidl.designclass import DesignClass


class TestPartClass:
    """Test PartClass creation, equality, and basic functionality."""
    
    def test_partclass_creation(self):
        """Test basic PartClass creation with default values."""
        circuit = Circuit()
        pc = PartClass("TestPartClass", circuit=circuit)
        
        assert pc.name == "TestPartClass"
        assert pc.priority == DEFAULT_PARTCLASS
        assert pc in circuit.partclasses.values()
        
    def test_partclass_creation_with_priority(self):
        """Test PartClass creation with custom priority."""
        circuit = Circuit()
        pc = PartClass("HighPriorityClass", priority=5, circuit=circuit)
        
        assert pc.name == "HighPriorityClass"
        assert pc.priority == 5
        
    def test_partclass_creation_with_attributes(self):
        """Test PartClass creation with custom attributes."""
        circuit = Circuit()
        pc = PartClass("AttrClass", 
                      priority=10,
                      custom_attr="test_value",
                      another_attr=42,
                      circuit=circuit)
        
        assert pc.name == "AttrClass"
        assert pc.priority == 10
        assert pc.custom_attr == "test_value"
        assert pc.another_attr == 42
        
    def test_partclass_equality(self):
        """Test PartClass equality comparison."""
        circuit = Circuit()
        pc1 = PartClass("TestClass", priority=5, attr="value", circuit=circuit)
        pc2 = PartClass("TestClass", priority=5, attr="value", circuit=circuit)
        with pytest.raises(KeyError):
            pc3 = PartClass("TestClass", priority=10, attr="value", circuit=circuit)
        with pytest.raises(KeyError):
            pc3 = PartClass("TestClass", priority=5, attr="new_value", circuit=circuit)
        pc4 = PartClass("DifferentClass", priority=5, attr="value", circuit=circuit)
        
        assert pc1 == pc2  # Same attributes
        assert pc1 != pc4  # Different name
        assert pc1 != "not_a_partclass"  # Different type
        
    def test_partclass_hash(self):
        """Test PartClass hashing functionality."""
        circuit = Circuit()
        pc1 = PartClass("TestClass", priority=5, circuit=circuit)
        pc2 = PartClass("TestClass", priority=5, circuit=circuit)  # Same name, different attributes
        pc3 = PartClass("DifferentClass", priority=5, circuit=circuit)
        
        # Objects with same name should have same hash
        assert hash(pc1) == hash(pc2)
        assert hash(pc1) != hash(pc3)
        
        # Should be usable in sets and as dict keys
        part_set = {pc1, pc2, pc3}
        assert len(part_set) == 2  # pc1 and pc2 have same hash
        
        part_dict = {pc1: "value1", pc3: "value3"}
        assert len(part_dict) == 2


class TestPartClassList:
    """Test PartClassList functionality."""
    
    def test_partclasslist_creation_empty(self):
        """Test creating empty PartClassList."""
        pcl = PartClassList()
        assert len(pcl) == 0
        
    def test_partclasslist_creation_with_classes(self):
        """Test creating PartClassList with initial classes."""
        circuit = Circuit()
        pc1 = PartClass("Class1", priority=1, circuit=circuit)
        pc2 = PartClass("Class2", priority=2, circuit=circuit)
        
        pcl = PartClassList(pc1, pc2, circuit=circuit)
        assert len(pcl) == 2
        assert pc1 in pcl
        assert pc2 in pcl
        
    def test_partclasslist_add_by_name(self):
        """Test adding PartClass by string name."""
        circuit = Circuit()
        pc1 = PartClass("Class1", priority=1, circuit=circuit)
        
        pcl = PartClassList(circuit=circuit)
        pcl.add("Class1", circuit=circuit)
        
        assert len(pcl) == 1
        assert pc1 in pcl
        
    def test_partclasslist_add_mixed_types(self):
        """Test adding various types to PartClassList."""
        circuit = Circuit()
        pc1 = PartClass("Class1", priority=1, circuit=circuit)
        pc2 = PartClass("Class2", priority=2, circuit=circuit)
        
        pcl1 = PartClassList(pc1, circuit=circuit)
        pcl2 = PartClassList(circuit=circuit)
        pcl2.add(pc2, "Class1", pcl1, None, circuit=circuit)
        
        assert len(pcl2) == 2
        assert pc1 in pcl2
        assert pc2 in pcl2
        
    def test_partclasslist_deduplication(self):
        """Test that PartClassList prevents duplicates."""
        circuit = Circuit()
        pc1 = PartClass("Class1", priority=1, circuit=circuit)
        
        pcl = PartClassList(pc1, pc1, circuit=circuit)
        assert len(pcl) == 1
        
        pcl.add(pc1, circuit=circuit)
        assert len(pcl) == 1
        
    def test_partclasslist_equality(self):
        """Test PartClassList equality comparison."""
        circuit = Circuit()
        pc1 = PartClass("Class1", priority=1, circuit=circuit)
        pc2 = PartClass("Class2", priority=2, circuit=circuit)
        
        pcl1 = PartClassList(pc1, pc2, circuit=circuit)
        pcl2 = PartClassList(pc2, pc1, circuit=circuit)  # Different order
        pcl3 = PartClassList(pc1, circuit=circuit)
        
        assert pcl1 == pcl2  # Order doesn't matter
        assert pcl1 != pcl3  # Different contents
        
    def test_partclasslist_by_priority(self):
        """Test sorting PartClassList by priority."""
        circuit = Circuit()
        pc1 = PartClass("HighPriority", priority=1, circuit=circuit)
        pc2 = PartClass("MediumPriority", priority=5, circuit=circuit)
        pc3 = PartClass("LowPriority", priority=10, circuit=circuit)
        
        pcl = PartClassList(pc3, pc1, pc2, circuit=circuit)
        sorted_names = pcl.by_priority()
        
        assert sorted_names == ["HighPriority", "MediumPriority", "LowPriority"]
        
    def test_partclasslist_invalid_type_error(self):
        """Test error handling for invalid types."""
        circuit = Circuit()
        pcl = PartClassList(circuit=circuit)
        
        with pytest.raises(TypeError):
            pcl.add(123, circuit=circuit)


class TestNetClass:
    """Test NetClass creation, equality, and basic functionality."""
    
    def test_netclass_creation(self):
        """Test basic NetClass creation with default values."""
        circuit = Circuit()
        nc = NetClass("TestNetClass", circuit=circuit)
        
        assert nc.name == "TestNetClass"
        assert nc.priority == DEFAULT_NETCLASS
        assert nc in circuit.netclasses.values()
        
    def test_netclass_creation_with_routing_params(self):
        """Test NetClass creation with routing parameters."""
        circuit = Circuit()
        nc = NetClass("PowerClass",
                     priority=1,
                     trace_width=0.5,
                     clearance=0.2,
                     via_dia=0.8,
                     via_drill=0.4,
                     circuit=circuit)
        
        assert nc.name == "PowerClass"
        assert nc.priority == 1
        assert nc.trace_width == 0.5
        assert nc.clearance == 0.2
        assert nc.via_dia == 0.8
        assert nc.via_drill == 0.4
        
    def test_netclass_differential_pairs(self):
        """Test NetClass with differential pair parameters."""
        circuit = Circuit()
        nc = NetClass("DiffPairClass",
                     diff_pair_width=0.1,
                     diff_pair_gap=0.2,
                     circuit=circuit)
        
        assert nc.diff_pair_width == 0.1
        assert nc.diff_pair_gap == 0.2
        
    def test_netclass_equality(self):
        """Test NetClass equality comparison."""
        circuit = Circuit()
        nc1 = NetClass("TestClass", priority=5, trace_width=0.15, circuit=circuit)
        nc2 = NetClass("TestClass", priority=5, trace_width=0.15, circuit=circuit)
        with pytest.raises(KeyError):
            nc3 = NetClass("TestClass", priority=10, trace_width=0.15, circuit=circuit)
        nc4 = NetClass("DifferentClass", priority=15, trace_width=0.15, circuit=circuit)
        
        assert nc1 == nc2  # Same attributes
        assert nc1 != nc4  # Different name
        assert nc1 != "not_a_netclass"  # Different type
        
    def test_netclass_hash(self):
        """Test NetClass hashing functionality."""
        circuit = Circuit()
        nc1 = NetClass("TestClass", priority=5, circuit=circuit)
        nc2 = NetClass("TestClass", priority=5, circuit=circuit)
        nc3 = NetClass("DifferentClass", priority=5, circuit=circuit)
        
        # Objects with same name should have same hash
        assert hash(nc1) == hash(nc2)
        assert hash(nc1) != hash(nc3)
        
        # Should be usable in sets and as dict keys
        net_set = {nc1, nc2, nc3}
        assert len(net_set) == 2


class TestNetClassList:
    """Test NetClassList functionality."""
    
    def test_netclasslist_creation_empty(self):
        """Test creating empty NetClassList."""
        ncl = NetClassList()
        assert len(ncl) == 0
        
    def test_netclasslist_creation_with_classes(self):
        """Test creating NetClassList with initial classes."""
        circuit = Circuit()
        nc1 = NetClass("Class1", priority=1, circuit=circuit)
        nc2 = NetClass("Class2", priority=2, circuit=circuit)
        
        ncl = NetClassList(nc1, nc2, circuit=circuit)
        assert len(ncl) == 2
        assert nc1 in ncl
        assert nc2 in ncl
        
    def test_netclasslist_add_by_name(self):
        """Test adding NetClass by string name."""
        circuit = Circuit()
        nc1 = NetClass("Class1", priority=1, circuit=circuit)
        
        ncl = NetClassList(circuit=circuit)
        ncl.add("Class1", circuit=circuit)
        
        assert len(ncl) == 1
        assert nc1 in ncl
        
    def test_netclasslist_deduplication(self):
        """Test that NetClassList prevents duplicates."""
        circuit = Circuit()
        nc1 = NetClass("Class1", priority=1, circuit=circuit)
        
        ncl = NetClassList(nc1, nc1, circuit=circuit)
        assert len(ncl) == 1
        
    def test_netclasslist_by_priority(self):
        """Test sorting NetClassList by priority."""
        circuit = Circuit()
        nc1 = NetClass("HighPriority", priority=1, circuit=circuit)
        nc2 = NetClass("MediumPriority", priority=5, circuit=circuit)
        nc3 = NetClass("LowPriority", priority=10, circuit=circuit)
        
        ncl = NetClassList(nc3, nc1, nc2, circuit=circuit)
        sorted_names = ncl.by_priority()
        
        assert sorted_names == ["HighPriority", "MediumPriority", "LowPriority"]


class TestDesignClass:
    """Test DesignClass base functionality."""
    
    def test_designclass_creation(self):
        """Test basic DesignClass creation."""
        dc = DesignClass()
        assert len(dc) == 0
        
    def test_designclass_add_object_with_name(self):
        """Test adding objects with name attribute."""
        dc = DesignClass()
        
        # Create a simple object with name attribute
        class TestObj:
            def __init__(self, name):
                self.name = name
                
        obj = TestObj("test_object")
        dc.add(obj, priority=5)
        
        assert len(dc) == 1
        assert "test_object" in dc
        assert dc["test_object"] == obj
        assert obj.priority == 5
        
    def test_designclass_add_without_name_error(self):
        """Test error when adding object without name attribute."""
        dc = DesignClass()
        
        class NoNameObj:
            pass
            
        obj = NoNameObj()
        
        with pytest.raises(AttributeError):
            dc.add(obj)
            
    def test_designclass_invalid_priority_error(self):
        """Test error handling for invalid priority values."""
        dc = DesignClass()
        
        class TestObj:
            def __init__(self, name):
                self.name = name
                
        obj = TestObj("test")
        
        with pytest.raises(ValueError):
            dc.add(obj, priority=-1)
            
        with pytest.raises(ValueError):
            dc.add(obj, priority=sys.maxsize + 1)
            
        with pytest.raises(ValueError):
            dc.add(obj, priority="invalid")
            
    def test_designclass_duplicate_name_with_same_object(self):
        """Test adding same object twice should succeed."""
        dc = DesignClass()
        
        class TestObj:
            def __init__(self, name):
                self.name = name
                
        obj = TestObj("test")
        dc.add(obj, priority=5)
        dc.add(obj, priority=10)  # Should succeed, same object
        
        assert len(dc) == 1
        assert dc["test"] == obj
        
    def test_designclass_duplicate_name_different_object_error(self):
        """Test error when adding different object with same name."""
        dc = DesignClass()
        
        class TestObj:
            def __init__(self, name):
                self.name = name
                
            def __eq__(self, other):
                return False  # Force objects to be different
                
        obj1 = TestObj("test")
        obj2 = TestObj("test")
        
        dc.add(obj1, priority=5)
        
        with pytest.raises(KeyError):
            dc.add(obj2, priority=5)
            
    def test_designclass_getitem_single(self):
        """Test retrieving single object by name."""
        dc = DesignClass()
        
        class TestObj:
            def __init__(self, name):
                self.name = name
                
        obj = TestObj("test")
        dc.add(obj)
        
        retrieved = dc["test"]
        assert retrieved == obj
        
    def test_designclass_getitem_multiple(self):
        """Test retrieving multiple objects by name."""
        dc = DesignClass()
        
        class TestObj:
            def __init__(self, name):
                self.name = name
                
        obj1 = TestObj("test1")
        obj2 = TestObj("test2")
        obj3 = TestObj("test3")
        
        dc.add(obj1)
        dc.add(obj2)
        dc.add(obj3)
        
        retrieved = dc["test1", "test2", "nonexistent"]
        assert len(retrieved) == 2
        assert obj1 in retrieved
        assert obj2 in retrieved
        
    def test_designclass_getitem_nonexistent_error(self):
        """Test error when retrieving nonexistent object."""
        dc = DesignClass()
        
        with pytest.raises(KeyError):
            dc["nonexistent"]
            
    def test_designclass_by_priority(self):
        """Test sorting objects by priority."""
        dc = DesignClass()
        
        class TestObj:
            def __init__(self, name):
                self.name = name
                
        obj1 = TestObj("high")
        obj2 = TestObj("medium")
        obj3 = TestObj("low")
        
        dc.add(obj1, priority=1)
        dc.add(obj2, priority=5)
        dc.add(obj3, priority=10)
        
        sorted_names = dc.by_priority("high", "medium", "low")
        assert sorted_names == ["high", "medium", "low"]
        
    def test_designclass_contains(self):
        """Test __contains__ method for both strings and objects."""
        dc = DesignClass()
        
        class TestObj:
            def __init__(self, name):
                self.name = name
                
        obj = TestObj("test")
        dc.add(obj)
        
        assert "test" in dc
        assert obj in dc
        assert "nonexistent" not in dc


class TestCircuitIntegration:
    """Test integration with actual Circuit, Part, and Net objects."""
    
    def test_partclass_assignment_to_parts(self):
        """Test assigning PartClass to Part objects."""
        circuit = Circuit()
        
        # Create part classes
        analog_class = PartClass("AnalogParts", priority=1, circuit=circuit)
        digital_class = PartClass("DigitalParts", priority=2, circuit=circuit)
        
        # Create parts - need to use actual part library
        # For testing, we'll create simple parts
        r1 = Part(lib="Device", name="R", circuit=circuit)
        r1.ref = "R1"
        r1.partclass = analog_class
        
        u1 = Part(lib="4xxx", name="4001", circuit=circuit)
        u1.ref = "U1" 
        u1.partclass = digital_class
        
        assert r1.partclass == analog_class
        assert u1.partclass == digital_class
        
        # Test part class retrieval from circuit
        assert circuit.partclasses["AnalogParts"] == analog_class
        assert circuit.partclasses["DigitalParts"] == digital_class
        
    def test_netclass_assignment_to_nets(self):
        """Test assigning NetClass to Net objects."""
        circuit = Circuit()
        
        # Create net classes
        power_class = NetClass("Power", priority=1, trace_width=0.5, circuit=circuit)
        signal_class = NetClass("Signal", priority=2, trace_width=0.15, circuit=circuit)
        
        # Create nets
        vcc = Net("VCC", circuit=circuit)
        gnd = Net("GND", circuit=circuit)
        data = Net("DATA", circuit=circuit)
        
        # Assign net classes
        vcc.netclass = power_class
        gnd.netclass = power_class
        data.netclass = signal_class
        
        assert vcc.netclass == power_class
        assert gnd.netclass == power_class
        assert data.netclass == signal_class
        
        # Test net class retrieval from circuit
        assert circuit.netclasses["Power"] == power_class
        assert circuit.netclasses["Signal"] == signal_class
        
    def test_multiple_netclasses_per_net(self):
        """Test assigning multiple NetClasses to a single net."""
        circuit = Circuit()
        
        # Create net classes
        high_current = NetClass("HighCurrent", priority=1, trace_width=0.5, circuit=circuit)
        sensitive = NetClass("Sensitive", priority=2, clearance=0.3, circuit=circuit)
        
        # Create net class list
        special_rules = NetClassList(high_current, sensitive, circuit=circuit)
        
        # Create net and assign multiple classes
        power_rail = Net("POWER_RAIL", circuit=circuit)
        power_rail.netclass = special_rules
        
        assert power_rail.netclass == special_rules
        assert high_current in power_rail.netclass
        assert sensitive in power_rail.netclass
        
    def test_hierarchical_circuit_classes(self):
        """Test part and net classes in hierarchical circuits."""
        # Create parent circuit
        parent = Circuit()
        
        # Create child circuit  
        child = Circuit()
        
        # Create classes in parent
        parent_pc = PartClass("ParentPartClass", priority=1, circuit=parent)
        parent_nc = NetClass("ParentNetClass", priority=1, circuit=parent)
        
        # Create classes in child
        child_pc = PartClass("ChildPartClass", priority=2, circuit=child)
        child_nc = NetClass("ChildNetClass", priority=2, circuit=child)
        
        # Create parts and nets in each circuit
        parent_part = Part(lib="Device", name="R", circuit=parent)
        parent_part.ref = "R_PARENT"
        parent_part.partclass = parent_pc
        
        child_part = Part(lib="Device", name="R", circuit=child)
        child_part.ref = "R_CHILD"
        child_part.partclass = child_pc
        
        parent_net = Net("PARENT_NET", circuit=parent)
        parent_net.netclass = parent_nc
        
        child_net = Net("CHILD_NET", circuit=child)
        child_net.netclass = child_nc
        
        # Verify isolation between circuits
        assert parent.partclasses["ParentPartClass"] == parent_pc
        assert child.partclasses["ChildPartClass"] == child_pc
        assert "ChildPartClass" not in parent.partclasses
        assert "ParentPartClass" not in child.partclasses
        
        assert parent.netclasses["ParentNetClass"] == parent_nc
        assert child.netclasses["ChildNetClass"] == child_nc
        assert "ChildNetClass" not in parent.netclasses
        assert "ParentNetClass" not in child.netclasses
        
    def test_priority_based_sorting_integration(self):
        """Test priority-based sorting with actual circuit objects."""
        circuit = Circuit()
        
        # Create various priority classes
        critical = PartClass("Critical", priority=1, circuit=circuit)
        important = PartClass("Important", priority=5, circuit=circuit)
        normal = PartClass("Normal", priority=10, circuit=circuit)
        
        # Create part class list
        pcl = PartClassList(normal, critical, important, circuit=circuit)
        
        # Test sorting
        sorted_names = pcl.by_priority()
        assert sorted_names == ["Critical", "Important", "Normal"]
        
        # Test circuit-level sorting
        circuit_sorted = circuit.partclasses.by_priority("Normal", "Critical", "Important")
        assert circuit_sorted == ["Critical", "Important", "Normal"]
        
    def test_class_assignment_persistence(self):
        """Test that class assignments persist through circuit operations."""
        circuit = Circuit()
        
        # Create classes
        power_class = NetClass("Power", trace_width=0.5, circuit=circuit)
        analog_class = PartClass("Analog", priority=1, circuit=circuit)
        
        # Create part and net
        resistor = Part(lib="Device", name="R", circuit=circuit)
        resistor.ref = "R1"
        resistor.partclass = analog_class
        
        vcc_net = Net("VCC", circuit=circuit)
        vcc_net.netclass = power_class
        
        # Verify assignments persist
        assert resistor.partclass == analog_class
        assert vcc_net.netclass == power_class
        
        # Verify classes are in circuit
        assert analog_class in circuit.partclasses.values()
        assert power_class in circuit.netclasses.values()
        
        # Test that we can retrieve by name
        assert circuit.partclasses["Analog"] == analog_class
        assert circuit.netclasses["Power"] == power_class
