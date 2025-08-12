# -*- coding: utf-8 -*-
# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Part class management for SKiDL PCB design.

This module provides part class management capabilities for organizing
and categorizing electronic components in PCB designs. Part classes enable designers
to group components with similar characteristics, manufacturing requirements, or
design constraints for efficient management and rule application.

Key Features:
    - Group components with similar characteristics or requirements
    - Support multiple part classes per component for complex categorization
    - Define manufacturing and assembly priorities
    - Attach arbitrary component class attributes

Classes:
    PartClass: Represents a single part class with properties and categorization rules.
        Stores component characteristics, priorities, and custom attributes for
        grouping related electronic components.
        
    PartClassList: A specialized list container for managing multiple PartClass 
        objects. Enables components to belong to multiple classes simultaneously
        for complex categorization scenarios.

Constants:
    DEFAULT_PARTCLASS: Default priority value (0) for standard part classes.
        Lower priority values indicate lower precedence in component selection
        and rule application scenarios.

Common Use Cases:
    - Power components requiring special thermal management
    - High-frequency components needing controlled placement
    - Critical components requiring premium part selection
    - Components grouped by supplier or manufacturer
    - Assembly groups for pick-and-place optimization

Example Usage:
    >>> # Create part classes for different component types
    >>> power_parts = PartClass('PowerComponents', 
    ...                        priority=10,           # High priority
    ...                        thermal_mgmt=True,    # Requires thermal management
    ...                        placement='keep_out') # Special placement rules
    >>> 
    >>> precision_parts = PartClass('PrecisionComponents',
    ...                            priority=5,         # Medium priority
    ...                            tolerance='1%',     # Tight tolerance requirement
    ...                            supplier='premium') # Premium supplier required
    >>> 
    >>> # Create component grouping
    >>> critical_parts = PartClassList(power_parts, precision_parts)
    >>> 
    >>> # Apply to components
    >>> voltage_reg = Part('LM7805', ref='U1')
    >>> voltage_reg.partclasses = power_parts
    >>> 
    >>> precision_resistor = Part('R', ref='R1', value='10k', tolerance='1%')
    >>> precision_resistor.partclasses = precision_parts

Priority System:
    Lower numeric priority values indicate lower precedence. When components
    belong to multiple classes or when classes conflict, the class with
    the highest priority number takes precedence for rule resolution.
"""

from .logger import active_logger
from .utilities import export_to_all, flatten

DEFAULT_PARTCLASS = 0

__all__ = ["DEFAULT_PARTCLASS"]


@export_to_all
class PartClass(object):
    """
    Defines a group of electronic components sharing common characteristics or requirements.

    Part classes provide a mechanism for organizing components with similar properties,
    manufacturing requirements, or design constraints. They enable designers to apply
    consistent rules across multiple components and facilitate bulk operations on
    component groups.

    The PartClass stores various component characteristics and custom attributes that
    can be used for component selection, placement rules, manufacturing constraints,
    and design automation. These attributes are typically used by design tools and
    scripts to automatically apply appropriate component handling and placement rules.

    Attributes:
        name (str): Unique identifier for the part class within the circuit.
            Used for referencing and organizing part classes.
        priority (int): Precedence level for rule conflicts (default: 0).
            Lower values indicate lower priority when resolving conflicts.
        circuit (Circuit): Reference to the circuit containing this part class.

    Additional attributes can be added via keyword arguments during initialization
    to store custom properties specific to the component group, such as:
        - Manufacturing requirements (e.g., lead_free=True)
        - Thermal properties (e.g., max_temp=125)
        - Placement constraints (e.g., keep_out_zones=['bottom'])
        - Supplier information (e.g., preferred_supplier='Digikey')
        - Assembly requirements (e.g., pick_and_place=True)

    Design Rule Examples:
        - Power components: Special thermal management, larger keep-out zones
        - High-frequency components: Controlled placement, special routing
        - Critical components: Premium part selection, redundancy requirements
        - Standard components: Standard handling, cost optimization
    """

    def __init__(self, name, circuit=None, **attribs):
        """
        Create a new part class with specified name and component characteristics.

        Initializes a part class with the given name and applies any additional
        component characteristics or custom attributes. The part class is automatically
        added to the specified circuit (or the default circuit) and can be referenced by
        name for assignment to components.

        Args:
            name (str): Unique name for the part class within the circuit.
                Should be descriptive of the component type or characteristics
                (e.g., 'PowerComponents', 'PrecisionParts', 'HighFrequency').

        Keyword Args:
            circuit (Circuit, optional): Target circuit for the part class.
                If not specified, uses the circuit parameter from attribs,
                or defaults to the currently active default circuit.
            priority (int, optional): Design rule priority (default: 0).
                Lower values have lower precedence in conflict resolution.
            **attribs: Additional custom attributes for the part class.
                These can include manufacturing requirements, thermal properties,
                placement constraints, or any other component characteristics.

        Raises:
            ValueError: If a part class with the same name but different attributes or priority
                already exists in the circuit.

        Examples:
            >>> # Create power component class
            >>> power_parts = PartClass('PowerComponents',
            ...                        priority=10,              # High priority
            ...                        thermal_mgmt=True,       # Requires thermal management
            ...                        min_trace_width=0.5,     # Minimum trace width (mm)
            ...                        placement_zone='center', # Preferred placement
            ...                        heat_sink_required=True) # Additional cooling needed
            
            >>> # Create precision component class  
            >>> precision_parts = PartClass('PrecisionComponents',
            ...                            priority=5,           # Medium priority
            ...                            tolerance='1%',       # Required tolerance
            ...                            temperature_coeff=50, # ppm/°C requirement
            ...                            supplier_grade='A',   # Premium grade required
            ...                            matching_required=True) # Component matching needed
            
            >>> # Create high-frequency component class
            >>> rf_parts = PartClass('RFComponents',
            ...                      priority=8,                # High priority
            ...                      frequency_range='1GHz',    # Operating frequency
            ...                      ground_plane_req=True,     # Ground plane required
            ...                      via_stitching=True,        # Via stitching needed
            ...                      isolation_req=0.5)         # Isolation requirement (mm)

        Component Integration:
            The part class properties can be used by design automation tools:
            - Component selection: Filter parts by class attributes
            - Placement rules: Apply positioning constraints automatically
            - Routing constraints: Set trace width and spacing requirements
            - Manufacturing: Generate assembly instructions and BOMs
            - Testing: Group components for in-circuit testing
        """

        # This object will belong to the default Circuit object or the one
        # that's passed as a parameter.
        circuit = circuit or default_circuit

        # Assign part class name.
        self.name = name

        # Assign default priority if not specified.
        if "priority" not in attribs:
            attribs["priority"] = DEFAULT_PARTCLASS

        # Assign the other attributes to this object.
        for k, v in list(attribs.items()):
            setattr(self, k, v)

        # Add part class to circuit. Duplicate part classes will be ignored.
        circuit.add_partclasses(self)

    def __eq__(self, prtcls):
        """
        Compare two PartClass objects for equality based on their attributes.

        Performs a comprehensive comparison of all attributes between two PartClass
        objects to determine if they are equivalent. This includes
        the name, priority, and all custom attributes that were set during
        initialization or added later.

        Args:
            prtcls (PartClass): Another PartClass object to compare against.
                Can be any object, but will only return True for PartClass instances
                with identical attribute sets.

        Returns:
            bool: True if both PartClass objects have identical attributes
                (name, priority, and all custom attributes), False otherwise.
                Returns False if the compared object is not a PartClass instance.

        Examples:
            >>> pc1 = PartClass('TestClass', priority=5, custom_attr='value')
            >>> pc2 = PartClass('TestClass', priority=5, custom_attr='value')
            >>> pc3 = PartClass('TestClass', priority=10, custom_attr='value')
            >>> 
            >>> pc1 == pc2  # True - identical attributes
            >>> pc1 == pc3  # False - different priority
            >>> pc1 == 'not_a_partclass'  # False - different type

        Use Cases:
            - Duplicate detection when adding part classes to circuits
            - Validation of part class consistency across design files
            - Unit testing and verification of part class creation
            - Design rule checking and conflict resolution
        """
        if not isinstance(prtcls, PartClass):
            return False
        
        # Compare all attributes of both objects
        return vars(self) == vars(prtcls)

    def __hash__(self):
        """
        Generate a hash value for the PartClass object based on its name.

        Creates a hash value that allows PartClass objects to be used in sets,
        as dictionary keys, and in other hash-based collections. The hash is
        based solely on the name attribute, assuming that names are immutable
        and unique within a circuit context.

        Returns:
            int: Hash value based on the part class name.
                Objects with the same name will have the same hash value,
                enabling efficient lookup and deduplication operations.

        Examples:
            >>> pc1 = PartClass('PowerComponents', priority=1)
            >>> pc2 = PartClass('PowerComponents', priority=5)  # Same name, different priority
            >>> pc3 = PartClass('SignalComponents', priority=1)
            >>> 
            >>> hash(pc1) == hash(pc2)  # True - same name
            >>> hash(pc1) == hash(pc3)  # False - different names
            >>> 
            >>> # Can be used in sets and dictionaries
            >>> part_set = {pc1, pc2, pc3}  # pc1 and pc2 are considered same due to hash
            >>> part_dict = {pc1: 'power_rules', pc3: 'signal_rules'}

        Note:
            This implementation assumes that part class names are immutable after
            creation and unique within their circuit context. Modifying the name
            after creation may lead to inconsistent hash behavior.
        """
        return hash(self.name)


class PartClassList(list):
    """
    A specialized list container for managing multiple PartClass objects.

    PartClassList extends the built-in list to provide enhanced functionality
    for managing collections of PartClass objects. This enables components to belong
    to multiple part classes simultaneously, which is useful for complex designs
    where components may need to satisfy multiple sets of design rules or
    categorization schemes.

    The list provides automatic deduplication, circuit-aware lookups, and
    specialized methods for adding part classes by name or object reference.
    It also supports recursive addition from other PartClassList objects and
    priority-based sorting for rule precedence.

    Features:
        - Automatic deduplication of part class objects
        - Support for adding part classes by name (with circuit lookup)
        - Recursive addition from other PartClassList instances  
        - Circuit-aware part class resolution
        - Equality comparison based on set membership
        - Priority-based sorting for rule application

    Use Cases:
        - Components requiring multiple design rule sets
        - Hierarchical component categorization schemes
        - Complex designs with overlapping component requirements
        - Design rule conflict analysis and resolution
        - Bulk operations on component groups

    Examples:
        >>> # Create component classes
        >>> power_class = PartClass('Power', priority=1)
        >>> critical_class = PartClass('Critical', priority=2)
        >>> expensive_class = PartClass('Expensive', priority=3)
        >>> 
        >>> # Group classes for special components
        >>> special_components = PartClassList(power_class, critical_class)
        >>> 
        >>> # Apply multiple classes to a component
        >>> voltage_regulator = Part('LM7805', ref='U1')
        >>> voltage_regulator.partclasses = special_components
    """

    def __init__(self, *partclasses, circuit=None):
        """
        Initialize the PartClassList with zero or more PartClass objects.

        Creates a new list container and populates it with the provided part classes.
        Part classes can be provided as PartClass objects, string names (resolved
        via circuit lookup), or other PartClassList objects (recursively added).

        Args:
            *partclasses (PartClass, str, or PartClassList): Zero or more items to add:
                - PartClass objects: Added directly to the list
                - str: Part class names resolved via circuit lookup  
                - PartClassList: All contained part classes added recursively
                - None values are ignored for convenience

        Keyword Args:
            circuit (Circuit, optional): Circuit context for name resolution.
                Required when adding part classes by string name. Defaults to
                the default circuit if not specified.

        Examples:
            >>> # Create empty list
            >>> part_classes = PartClassList()
            
            >>> # Create with multiple part classes
            >>> power_class = PartClass('Power', priority=1)
            >>> signal_class = PartClass('Signal', priority=5)  
            >>> classes = PartClassList(power_class, signal_class)
            
            >>> # Add by name (requires circuit context)
            >>> classes = PartClassList('Power', 'Signal', circuit=my_circuit)
            
            >>> # Combine existing lists
            >>> list1 = PartClassList(power_class)
            >>> list2 = PartClassList(signal_class)
            >>> combined = PartClassList(list1, list2)

        Error Handling:
            - None values are silently ignored for convenience
            - Invalid types raise TypeError via the add() method
            - String names that don't exist in circuit raise lookup errors
        """
        super().__init__()
        self.add(*partclasses, circuit=circuit)

    def __eq__(self, pt_cls_lst):
        """
        Compare two PartClassList objects for equality.

        Compares the contents of two PartClassList objects using set-based
        equality, meaning the order of part classes doesn't matter - only
        the presence or absence of specific PartClass objects.

        Args:
            pt_cls_lst (PartClassList): Another PartClassList to compare against.
                Can be any iterable, but meaningful comparison requires another
                PartClassList or similar container with PartClass objects.

        Returns:
            bool: True if both lists contain the same set of PartClass objects,
                False otherwise. Order is ignored in the comparison.

        Examples:
            >>> class1 = PartClass('Power')
            >>> class2 = PartClass('Signal')
            >>> 
            >>> list1 = PartClassList(class1, class2)
            >>> list2 = PartClassList(class2, class1)  # Different order
            >>> list3 = PartClassList(class1)
            >>> 
            >>> list1 == list2  # True - same contents, different order
            >>> list1 == list3  # False - different contents
        """
        return set(self) == set(pt_cls_lst)

    def __contains__(self, partclass):
        """Check if a PartClass is contained within this PartClassList.

        Args:
            partclass (PartClass, str): The object to check for membership.
                Can be either a PartClass object or a string name.

        Returns:
            bool: True if the PartClass is found in the list, False otherwise.
        """
        if isinstance(partclass, str):
            partclass = default_circuit.partclasses.get(partclass, None)
        return super().__contains__(partclass)

    def add(self, *partclasses, circuit=None):
        """
        Add one or more PartClass objects to the list with automatic deduplication.

        Adds the specified part classes to the list, handling various input types
        and automatically preventing duplicates. Supports adding by object reference,
        string name (with circuit lookup), or recursive addition from other lists.

        Args:
            *partclasses (PartClass, str, PartClassList, or None): Items to add:
                - PartClass: Added directly if not already present
                - str: Part class name resolved via circuit lookup
                - PartClassList: All contained classes added recursively  
                - None: Ignored for programming convenience

        Keyword Args:
            circuit (Circuit, optional): Circuit for string name resolution.
                Defaults to default_circuit if not provided. Required when
                adding part classes by string name.

        Raises:
            TypeError: If a partclass argument is not a supported type
                (PartClass, str, PartClassList, or None).
            KeyError: If a string name doesn't match any part class in the circuit.

        Examples:
            >>> classes = PartClassList()
            >>> power_class = PartClass('Power')
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
            PartClass object multiple times will result in only one instance in
            the list. Comparison is done by object identity, not name.

        Circuit Lookup:
            When adding by string name, the method searches the specified circuit's
            part class collection. The lookup is case-sensitive and must match
            exactly. If no circuit is provided, the default circuit is used.
        """
        for cls in flatten(partclasses):
            if cls is None:
                continue
            elif isinstance(cls, PartClassList):
                self.add(
                    *cls, circuit=circuit
                )  # Recursively add part classes from another PartClassList.
                continue
            elif isinstance(cls, PartClass):
                pass
            elif isinstance(cls, str):
                # The name of a part class was passed, so look it up in the circuit.
                circuit = circuit or default_circuit
                cls = circuit.partclasses[cls]
            else:
                active_logger.raise_(
                    TypeError,
                    f"Expected PartClassList, PartClass or string, got {type(cls)}",
                )
            # Add the partclass to the list if it's not already present.
            if cls not in self:
                self.append(cls)

    def by_priority(self):
        """
        Get a list of part class names sorted by their priority values.

        Returns the names of all part classes in the list, sorted in ascending
        order by their priority values. This is useful for applying design rules
        in the correct precedence order, where higher priority numbers indicate
        higher precedence.

        Returns:
            list[str]: A list of part class names sorted by priority (lowest first).
                Empty list if no part classes are present.

        Examples:
            >>> critical = PartClass('Critical', priority=10)
            >>> important = PartClass('Important', priority=5)
            >>> standard = PartClass('Standard', priority=1)
            >>> 
            >>> classes = PartClassList(standard, critical, important)
            >>> sorted_names = classes.by_priority()
            >>> print(sorted_names)  # ['Standard', 'Important', 'Critical']
        """
        return [pc.name for pc in sorted(self, key=lambda pc: pc.priority)]
