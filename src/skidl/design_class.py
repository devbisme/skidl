# -*- coding: utf-8 -*-
# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Design class module for SKIDL.

This module provides classes for managing design elements like parts and nets,
including their classification and organization within circuits. It defines
base classes for design elements and specialized collections for managing
specific types like part classes and net classes.
"""


from abc import ABC

from .logger import active_logger
from .utilities import export_to_all, flatten

DEFAULT_PRIORITY = 0  # Lowest possible priority.

__all__ = ["DEFAULT_PRIORITY"]


class DesignClass(ABC):
    """
    Base class for design elements with prioritized attributes.
    
    This class serves as a foundation for design elements that need to be
    categorized and prioritized within a circuit design. It provides basic
    functionality for storing attributes and comparing design classes.
    """

    def __init__(self, name, **attribs):
        """
        Initialize a design class with a name and attributes.
        
        Args:
            name (str): The name of the design class
            **attribs: Additional attributes for the design class.
                      If 'priority' is not specified, DEFAULT_PRIORITY is used.
        """

        # Assign part class name.
        self.name = name

        # Assign default priority if not specified.
        if "priority" not in attribs:
            attribs["priority"] = DEFAULT_PRIORITY

        # Assign the other attributes to this object.
        for k, v in list(attribs.items()):
            setattr(self, k, v)

    def __eq__(self, cls):
        """
        Check equality between two DesignClass instances.
        
        Args:
            cls: Object to compare with this instance
            
        Returns:
            bool: True if both objects are DesignClass instances with identical attributes
        """
        if not isinstance(cls, DesignClass):
            return False
        
        # Compare all attributes of both objects
        return vars(self) == vars(cls)

    def __hash__(self):
        """
        Generate hash value based on the design class name.
        
        Returns:
            int: Hash value of the name attribute

        Note:
            An explicit hash function is needed since an __eq__ function was defined.
        """
        return hash(self.name)

@export_to_all
class PartClass(DesignClass):
    """
    A design class specifically for categorizing electronic parts.
    
    PartClass extends DesignClass to provide part-specific functionality
    and automatic registration with a circuit's part class collection.
    """

    def __init__(self, name, circuit=None, **attribs):
        """
        Initialize a part class and register it with a circuit.
        
        Args:
            name (str): The name of the part class
            circuit (Circuit, optional): Circuit to register with. 
                                       Uses default_circuit if not specified.
            **attribs: Additional attributes for the part class
        """
        super().__init__(name, **attribs)

        # This object will belong to the default Circuit object or the one
        # that's passed as a parameter.
        circuit = circuit or default_circuit
        circuit.partclasses = self

@export_to_all
class NetClass(DesignClass):
    """
    A design class specifically for categorizing electrical nets.
    
    NetClass extends DesignClass to provide net-specific functionality
    and automatic registration with a circuit's net class collection.
    """

    def __init__(self, name, circuit=None, **attribs):
        """
        Initialize a net class and register it with a circuit.
        
        Args:
            name (str): The name of the net class
            circuit (Circuit, optional): Circuit to register with.
                                       Uses default_circuit if not specified.
            **attribs: Additional attributes for the net class
        """
        super().__init__(name, **attribs)

        # This object will belong to the default Circuit object or the one
        # that's passed as a parameter.
        circuit = circuit or default_circuit
        circuit.netclasses = self

class DesignClasses(ABC, dict):
    """
    A dictionary-based collection for managing design classes.
    
    This class provides a specialized dictionary for storing and managing
    collections of DesignClass objects with enhanced functionality for
    adding, retrieving, and organizing design classes.
    """

    def __init__(self, *classes, circuit=None, classes_name=None):
        """
        Initialize a design classes collection.
        
        Args:
            *classes: Variable number of design classes to add initially
            circuit (Circuit, optional): Associated circuit object
            classes_name (str, optional): Attribute name for this collection
                within a Circuit object such as 'partclasses' or 'netclasses'
        """
        super().__init__()

        # Save the attribute name for referencing this collection in the Circuit object.
        self.classes_name = classes_name

        # Add an initial set of class objects.
        self.add(classes, circuit=circuit)

    def __eq__(self, classes):
        """
        Check equality between two DesignClasses collections.
        
        Args:
            classes: Another DesignClasses object to compare with this collection
            
        Returns:
            bool: True if both objects are of the same type with identical attributes
        """
        if isinstance(classes, type(self)):
            return vars(self) == vars(classes)
        return False

    def __contains__(self, cls):
        """
        Check if a specific design class is contained in this collection.
        
        Args:
            cls (str or DesignClass): Class name or class object to search for
            
        Returns:
            bool: True if the class is found in the collection
        """
        if isinstance(cls, str):
            # If only given the class name, fetch the class object from the collection.
            return cls in self.keys()
        return cls in self.values()

    def __getitem__(self, *names):
        """
        Retrieve design classes by name(s).
        
        Args:
            *names: One or more class names to retrieve
            
        Returns:
            DesignClass or list: Single class if one name provided,
                               list of classes if multiple names provided
                               
        Raises:
            KeyError: If a requested class name is not found
        """
        names = flatten(names)
        if len(names) == 1:
            try:
                return super().__getitem__(names[0])
            except KeyError:
                active_logger.raise_(
                    KeyError, f"No {type(self)} with name '{names[0]}' found"
                )
        else:
            return [self[name] for name in names if name in self]

    def add(self, *classes, circuit=None):
        """
        Add one or more design classes to the collection.
        
        Args:
            *classes: Variable number of classes to add. Can be DesignClass objects,
                     strings (class names), lists, tuples, or other DesignClasses
            circuit (Circuit, optional): Circuit to associate with new classes
            
        Raises:
            ValueError: If attempting to add a class with the same name but different attributes
            TypeError: If attempting to add an unsupported type
        """
        for cls in classes:
            if cls is None:
                continue
            elif isinstance(cls, DesignClasses):
                self.add(*cls.values(), circuit=circuit)  # Recursively add classes from another DesignClasses object.
                continue
            elif isinstance(cls, (list, tuple, set)):
                self.add(*cls, circuit=circuit)  # Recursively add classes from a list, tuple, or set.
                continue
            elif isinstance(cls, DesignClass):
                if cls in self:
                    continue
                if cls.name in self.keys():
                    # A NetClass with the same name exists but the attributes differ.
                    active_logger.raise_(
                        ValueError, f"Cannot add {type(cls)} '{cls.name}' with differing attributes"
                    )
                pass
            elif isinstance(cls, str):
                # The name of a class was passed, so look it up in the circuit.
                circuit = circuit or default_circuit
                cls = getattr(circuit, self.classes_name)[cls]
            else:
                active_logger.raise_(
                    TypeError,
                    f"Can't add {type(cls)} to {type(self)}",
                )
            # Add the partclass to the list if it's not already present.
            if cls not in self:
                self[cls.name] = cls

    def by_priority(self):
        """
        Get class names sorted by priority.
        
        Returns:
            list: List of class names ordered by their priority attribute
        """
        return [pc.name for pc in sorted(self.values(), key=lambda pc: pc.priority)]
    
class PartClasses(DesignClasses):
    """
    Specialized collection for managing part classes.
    
    This class extends DesignClasses to provide specific functionality
    for organizing and managing electronic part classifications.
    """
    
    def __init__(self, *classes, circuit=None):
        """
        Initialize a part classes collection.
        
        Args:
            *classes: Variable number of part classes to add initially
            circuit (Circuit, optional): Associated circuit object
        """
        super().__init__(*classes, circuit=circuit, classes_name="partclasses")

class NetClasses(DesignClasses):
    """
    Specialized collection for managing net classes.
    
    This class extends DesignClasses to provide specific functionality
    for organizing and managing electrical net classifications.
    """
    
    def __init__(self, *classes, circuit=None):
        """
        Initialize a net classes collection.
        
        Args:
            *classes: Variable number of net classes to add initially
            circuit (Circuit, optional): Associated circuit object
        """
        super().__init__(*classes, circuit=circuit, classes_name="netclasses")
