# -*- coding: utf-8 -*-
# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Net class management for SKiDL PCB design.

This module provides comprehensive net class management capabilities for organizing
and applying electrical and physical properties to groups of nets in PCB designs.
Net classes enable designers to establish design rules, routing constraints, and
electrical characteristics for related nets.

Key Features:
    - Group nets with similar electrical or routing requirements
    - Establish priority hierarchies for design rule checking
    - Support multiple net classes per net for complex designs
    - Attach arbitrary net class attributes

Classes:
    NetClass: Represents a single net class with properties and categorization rules.
        Stores characteristics, priorities, and custom attributes for
        a group of nets.
        
    NetClassList: A specialized list container for managing multiple NetClass 
        objects. Enables nets to belong to multiple classes simultaneously
        for complex design rule scenarios.

Constants:
    DEFAULT_NETCLASS: Default priority value (0) for standard net classes.
        Lower priority values indicate lower precedence in design rule
        checking and conflict resolution.

Common Use Cases:
    - Power nets requiring wider traces and larger clearances
    - High-speed digital signals needing controlled impedance
    - Differential pairs with specific coupling requirements
    - Sensitive analog signals requiring isolation
    - Clock networks with matched routing lengths

Example Usage:
    >>> # Create net classes for different signal types
    >>> power_class = NetClass('Power', 
    ...                       trace_width=0.5,     # 0.5mm traces
    ...                       clearance=0.2,       # 0.2mm clearance  
    ...                       via_dia=0.8,         # 0.8mm via diameter
    ...                       priority=10)         # High priority
    >>> 
    >>> signal_class = NetClass('Signal',
    ...                        trace_width=0.15,   # 0.15mm traces
    ...                        clearance=0.1,      # 0.1mm clearance
    ...                        priority=1)         # Lower priority
    >>> 
    >>> # Create differential pair class
    >>> diff_class = NetClass('DiffPair',
    ...                      trace_width=0.1,
    ...                      diff_pair_width=0.1,
    ...                      diff_pair_gap=0.2,
    ...                      priority=5)
    >>> 
    >>> # Group multiple classes
    >>> critical_nets = NetClassList(power_class, diff_class)
    >>> 
    >>> # Apply to nets
    >>> vcc_net = Net('VCC')
    >>> vcc_net.netclasses = power_class
    >>> 
    >>> data_p = Net('DATA_P')  
    >>> data_n = Net('DATA_N')
    >>> data_p.netclasses = diff_class
    >>> data_n.netclasses = diff_class

Priority System:
    Higher numeric priority values indicate higher precedence. When nets
    belong to multiple classes or when classes conflict, the class with
    the highest priority number takes precedence for rule resolution.
"""

from .logger import active_logger
from .utilities import export_to_all, flatten

DEFAULT_NETCLASS = 0

__all__ = ["DEFAULT_NETCLASS"]


@export_to_all
class NetClass(object):
    """
    Defines a class for nets sharing common electrical and physical properties.

    Net classes provide a mechanism for organizing nets with similar routing
    requirements, electrical characteristics, or design constraints. They enable
    designers to apply consistent rules across multiple nets and integrate with
    PCB design tools for automated rule checking and routing.

    The NetClass stores various electrical and physical parameters that can be
    applied to nets during PCB layout. These parameters are typically used by
    PCB design tools to automatically apply appropriate trace widths, clearances,
    via sizes, and other routing constraints.

    Attributes:
        name (str): Unique identifier for the net class within the circuit.
            Used for referencing and organizing net classes.
        priority (int): Precedence level for design rule conflicts (default: 0).
            Higher values indicate higher priority when resolving conflicts.
    """

    def __init__(self, name, circuit=None, **attribs):
        """
        Create a new net class with specified name, priority, and other attributes.

        Initializes a net class with the given name and applies any additional
        electrical or physical attributes. The net class is automatically added
        to the specified circuit (or default circuit) and can be referenced by
        name for assignment to nets.

        Args:
            name (str): Unique name for the net class within the circuit.
                Should be descriptive of the net type (e.g., 'Power', 'Signal',
                'HighSpeed', 'DiffPair').

        Keyword Args:
            circuit (Circuit, optional): Target circuit for the net class.
                Defaults to the currently active default circuit.
            priority (int, optional): Design rule priority (default: 0).
                Lower values have lower precedence in conflict resolution.
            **attribs: Additional custom attributes for the net class.

        Raises:
            ValueError: If a net class with the same name but different attributes or priority
                already exists in the circuit.

        Examples:
            >>> # Create power supply net class
            >>> power_nets = NetClass('Power',
            ...                      trace_width=0.6,      # 0.6mm for high current
            ...                      clearance=0.25,       # Extra clearance for safety
            ...                      via_dia=1.0,          # Large vias for current
            ...                      via_drill=0.6,        # Corresponding drill size
            ...                      priority=10)          # High priority rules
            
            >>> # Create high-speed signal class  
            >>> hs_signals = NetClass('HighSpeed',
            ...                      trace_width=0.1,      # Thin for impedance
            ...                      clearance=0.15,       # Controlled spacing
            ...                      via_dia=0.4,          # Small vias
            ...                      via_drill=0.2,        # Minimize via size
            ...                      priority=5)
            
            >>> # Create differential pair class
            >>> lvds_pairs = NetClass('LVDS',
            ...                      diff_pair_width=0.09, # Controlled impedance
            ...                      diff_pair_gap=0.18,   # 100-ohm differential
            ...                      clearance=0.2,        # Isolation from others
            ...                      priority=3)
        """
        # This object will belong to the default Circuit object or the one
        # that's passed as a parameter.
        circuit = circuit or default_circuit

        # Assign net class name.
        self.name = name

        # Assign default priority if not specified.
        if "priority" not in attribs:
            attribs["priority"] = DEFAULT_NETCLASS

        # Assign the other attributes to this object.
        for k, v in list(attribs.items()):
            setattr(self, k, v)

        # Add netclass to circuit. Duplicate netclasses will be ignored.
        circuit.add_netclasses(self)

    def __eq__(self, ntcls):
        """
        Compare two NetClass objects for equality based on their attributes.

        Args:
            ntcls (NetClass): Another NetClass object to compare against.

        Returns:
            bool: True if both NetClass objects have identical attributes,
                False otherwise.
        """
        if not isinstance(ntcls, NetClass):
            return False
        
        # Compare all attributes of both objects
        return vars(self) == vars(ntcls)

    # Since an __eq__ method was defined, a __hash__ method is also needed
    # to maintain the hashability of NetClass objects.
    # This allows them to be used in sets or as dictionary keys.
    def __hash__(self):
        """
        Generate a hash value for the NetClass object based on its name.

        Creates a hash value that allows NetClass objects to be used in sets,
        as dictionary keys, and in other hash-based collections. The hash is
        based solely on the name attribute, assuming that names are immutable
        and unique within a circuit context.

        Returns:
            int: Hash value based on the net class name.
                Objects with the same name will have the same hash value,
                enabling efficient lookup and deduplication operations.

        Examples:
            >>> nc1 = NetClass('Power', priority=1)
            >>> nc2 = NetClass('Power', priority=5)  # Same name, different priority
            >>> nc3 = NetClass('Signal', priority=1)
            >>> 
            >>> hash(nc1) == hash(nc2)  # True - same name
            >>> hash(nc1) == hash(nc3)  # False - different names
            >>> 
            >>> # Can be used in sets and dictionaries
            >>> net_set = {nc1, nc2, nc3}  # nc1 and nc2 are considered same due to hash
            >>> net_dict = {nc1: 'power_rules', nc3: 'signal_rules'}

        Note:
            This implementation assumes that net class names are immutable after
            creation and unique within their circuit context. Modifying the name
            after creation may lead to inconsistent hash behavior.
        """
        return hash(self.name)

class NetClassList(list):
    """
    A specialized list container for managing multiple NetClass objects.

    NetClassList extends the built-in list to provide enhanced functionality
    for managing collections of NetClass objects. This enables nets to belong
    to multiple net classes simultaneously, which is useful for complex designs
    where nets may need to satisfy multiple sets of design rules.

    The list provides automatic deduplication, circuit-aware lookups, and
    specialized methods for adding net classes by name or object reference.
    It also supports recursive addition from other NetClassList objects.

    Features:
        - Automatic deduplication of net class objects
        - Support for adding net classes by name (with circuit lookup)
        - Recursive addition from other NetClassList instances  
        - Circuit-aware net class resolution
        - Equality comparison based on set membership

    Use Cases:
        - Nets requiring multiple design rule sets
        - Hierarchical design rule inheritance
        - Complex PCB designs with overlapping requirements
        - Design rule conflict analysis and resolution

    Attributes:
        circuit (Circuit): The circuit context for net class name resolution.
            Used when adding net classes by string name rather than object reference.
    """

    def __init__(self, *netclasses, circuit=None):
        """
        Initialize the NetClassList with zero or more NetClass objects.

        Creates a new list container and populates it with the provided net classes.
        Net classes can be provided as NetClass objects, string names (resolved
        via circuit lookup), or other NetClassList objects (recursively added).

        Args:
            *netclasses (NetClass, str, or NetClassList): Zero or more items to add:
                - NetClass objects: Added directly to the list
                - str: Net class names resolved via circuit lookup  
                - NetClassList: All contained net classes added recursively
                - None values are ignored for convenience

        Keyword Args:
            circuit (Circuit, optional): Circuit context for name resolution.
                Required when adding net classes by string name. Defaults to
                the default circuit if not specified.

        Examples:
            >>> # Create empty list
            >>> net_classes = NetClassList()
            
            >>> # Create with multiple net classes
            >>> power_class = NetClass('Power', trace_width=0.5)
            >>> signal_class = NetClass('Signal', trace_width=0.15)  
            >>> classes = NetClassList(power_class, signal_class)
            
            >>> # Add by name (requires circuit context)
            >>> classes = NetClassList('Power', 'Signal', circuit=my_circuit)
            
            >>> # Combine existing lists
            >>> list1 = NetClassList(power_class)
            >>> list2 = NetClassList(signal_class)
            >>> combined = NetClassList(list1, list2)

        Error Handling:
            - None values are silently ignored
            - Invalid types raise TypeError via the add() method
            - String names that don't exist in circuit raise lookup errors
        """
        super().__init__()
        self.add(*netclasses, circuit=circuit)

    def __eq__(self, nt_cls_lst):
        """
        Compare two NetClassList objects for equality.

        Compares the contents of two NetClassList objects using set-based
        equality, meaning the order of net classes doesn't matter - only
        the presence or absence of specific NetClass objects.

        Args:
            nt_cls_lst (NetClassList): Another NetClassList to compare against.

        Returns:
            bool: True if both lists contain the same set of NetClass objects,
                False otherwise. Order is ignored in the comparison.

        Examples:
            >>> class1 = NetClass('Power')
            >>> class2 = NetClass('Signal')
            >>> 
            >>> list1 = NetClassList(class1, class2)
            >>> list2 = NetClassList(class2, class1)  # Different order
            >>> list3 = NetClassList(class1)
            >>> 
            >>> list1 == list2  # True - same contents, different order
            >>> list1 == list3  # False - different contents
        """
        return set(self) == set(nt_cls_lst)

    def __contains__(self, netclass):
        """
        Check if a NetClass is contained within this NetClassList.
        
        Args:
            netclass (NetClass, str): The object to check for membership.
            
        Returns:
            bool: True if the net class is in the list, False otherwise.
        """
        if isinstance(netclass, str):
            netclass = default_circuit.netclasses.get(netclass, None)
        return super().__contains__(netclass)

    def add(self, *netclasses, circuit=None):
        """
        Add one or more NetClass objects to the list with automatic deduplication.

        Adds the specified net classes to the list, handling various input types
        and automatically preventing duplicates. Supports adding by object reference,
        string name (with circuit lookup), or recursive addition from other lists.

        Args:
            *netclasses (NetClass, str, NetClassList, or None): Items to add:
                - NetClass: Added directly if not already present
                - str: Net class name resolved via circuit lookup
                - NetClassList: All contained classes added recursively  
                - None: Ignored for programming convenience

        Keyword Args:
            circuit (Circuit, optional): Circuit for string name resolution.
                Defaults to default_circuit if not provided. Required when
                adding net classes by string name.

        Raises:
            TypeError: If a netclass argument is not a supported type
                (NetClass, str, NetClassList, or None).
            KeyError: If a string name doesn't match any net class in the circuit.

        Examples:
            >>> classes = NetClassList()
            >>> power_class = NetClass('Power')
            >>> 
            >>> # Add by object reference
            >>> classes.add(power_class)
            >>> 
            >>> # Add by name (requires circuit)
            >>> classes.add('Signal', circuit=my_circuit)
            >>> 
            >>> # Add multiple items
            >>> classes.add(power_class, 'HighSpeed', other_list)
            >>> 
            >>> # Add with mixed types
            >>> classes.add(power_class, None, 'Signal', other_list)

        Deduplication:
            The method automatically prevents duplicate entries. Adding the same
            NetClass object multiple times will result in only one instance in
            the list. Comparison is done by object identity, not name.

        Circuit Lookup:
            When adding by string name, the method searches the specified circuit's
            net class collection. The lookup is case-sensitive and must match
            exactly. If no circuit is provided, the default circuit is used.
        """
        for cls in flatten(netclasses):
            if cls is None:
                continue
            elif isinstance(cls, NetClassList):
                self.add(*cls, circuit=circuit)  # Recursively add netclasses from another NetClassList.
                continue
            elif isinstance(cls, NetClass):
                pass
            elif isinstance(cls, str):
                # The name of a netclass was passed, so look it up in the circuit.
                circuit = circuit or default_circuit
                cls = circuit.netclasses[cls]
            else:
                active_logger.raise_(
                    TypeError, f"Expected NetClassList, NetClass or string, got {type(cls)}"
                )
            # Add the netclass to the list if it's not already present.
            if cls not in self:
                self.append(cls)

    def by_priority(self):
        """
        Get a list of net class names sorted by their priority values.

        Returns the names of all net classes in the list, sorted in ascending
        order by their priority values. This is useful for applying design rules
        in the correct precedence order, where higher priority numbers indicate
        higher precedence.

        Returns:
            list[str]: A list of net class names sorted by priority (lowest first).
                Empty list if no net classes are present.
        """
        return [nc.name for nc in sorted(self, key=lambda nc: nc.priority)]