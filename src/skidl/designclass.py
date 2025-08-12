# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Design class module for managing design objects with priorities and name-based access.

This module provides the DesignClass base class that extends dict functionality
to manage objects with names and priorities, enabling efficient retrieval and
sorting operations. It serves as the foundation for specialized design object
containers like NetClass and PartClass collections.

The DesignClass provides a standardized interface for storing, retrieving, and
organizing design objects that have name-based identification and priority-based
ordering. This enables consistent handling of various design elements across
the SKiDL framework.

Key Features:
    - Name-based object storage and retrieval with dict-like interface
    - Priority assignment and validation for design rule precedence
    - Multiple object retrieval with a single operation
    - Automatic validation of object requirements (name attribute)
    - Comprehensive error handling with descriptive messages
    - Priority-based sorting for rule application ordering

Classes:
    DesignClass: Base dictionary class for managing named design objects with priorities.
        Provides the core functionality for storing objects by name, assigning priorities,
        and retrieving objects individually or in groups with priority-based sorting.

Common Use Cases:
    - Foundation for NetClass and PartClass management systems
    - Design rule containers requiring priority-based organization
    - Named object collections in hierarchical design systems
    - Component and net categorization frameworks
    - Design automation tool integration points

Priority System:
    The priority system uses integer values where lower numbers indicate higher
    precedence. This allows for intuitive ordering where priority 1 rules take
    precedence over priority 10 rules. The valid range is 0 to sys.maxsize.

Example Usage:
    >>> # Create a design class for managing custom objects
    >>> design = DesignClass()
    >>> 
    >>> # Create objects with name attribute
    >>> obj1 = CustomObject(name="component1")
    >>> obj2 = CustomObject(name="component2")
    >>> 
    >>> # Add with priorities
    >>> design.add(obj1, priority=10)
    >>> design.add(obj2, priority=5)
    >>> 
    >>> # Retrieve objects
    >>> comp1 = design["component1"]
    >>> comps = design["component1", "component2"]
    >>> 
    >>> # Get priority-sorted names
    >>> sorted_names = design.by_priority("component1", "component2")
    >>> # Returns ["component2", "component1"] (priority 5 before 10)

Integration with SKiDL:
    DesignClass serves as the base class for circuit.netclasses and circuit.partclasses
    collections, providing consistent interfaces for managing design rule objects
    throughout the SKiDL framework.
"""

import sys
from .logger import active_logger
from .utilities import export_to_all, flatten


@export_to_all
class DesignClass(dict):
    """
    A dictionary-based container for managing design objects with priority-based organization.

    DesignClass extends Python's built-in dict to provide specialized functionality
    for storing and retrieving design objects. Each object must have a 'name' attribute
    that serves as the dictionary key, and can be assigned a priority value for ordering.

    The class provides methods for adding objects with priorities, retrieving objects
    by name (single or multiple), sorting object names by priority, and managing the
    collection through standard dictionary operations.

    Key Features:
        - Name-based object storage and retrieval
        - Priority assignment and priority-based sorting
        - Multiple object retrieval with a single call
        - Validation of object requirements (name attribute)
        - Error handling with descriptive messages

        Inherits all dict attributes. Objects are stored with their name as the key
        and the object itself as the value. Each stored object will have a 'priority'
        attribute added if not already present.

    Example:
        >>> design = DesignClass()
        >>> obj1 = SomeObject(name="component1")
        >>> obj2 = SomeObject(name="component2")
        >>> design.add(obj1, priority=10)
        >>> design.add(obj2, priority=5)
        >>> sorted_object_names = design.by_priority("component1", "component2")
        >>> # Returns ["component2", "component1"] (sorted by priority: 5, 10)

        AttributeError: When attempting to add objects without a 'name' attribute
        ValueError: When priority values are outside the valid range (0 to sys.maxsize)
        KeyError: When accessing non-existent objects or adding duplicate names
    """

    def add(self, obj, priority=None):
        """
        Add an object to the design class with an optional priority.

        Args:
            obj: Object to add (must have a 'name' attribute)
            priority (int): Priority value from 0 to MAX_INTEGER (default: None)

        Raises:
            AttributeError: If object doesn't have a 'name' attribute
            ValueError: If priority is not within valid range
            KeyError: If an object with the same name already exists and has differing attributes
        """
        if not hasattr(obj, "name"):
            active_logger.raise_(AttributeError, "Object must have a 'name' attribute")

        if priority != None:
            if not isinstance(priority, int) or priority < 0 or priority > sys.maxsize:
                active_logger.raise_(
                    ValueError, f"Priority must be an integer between 0 and {sys.maxsize}"
                )

        if obj.name in self:
            if self[obj.name] != obj:
                typ = lambda obj: str(type(obj)).split('.')[-1].replace("'>", "").replace("<class '", "")
                active_logger.raise_(
                    KeyError, f"Cannot change attributes of existing {typ(self[obj.name])} with name '{obj.name}'"
                )

        if priority != None:
            obj.priority = priority
        self[obj.name] = obj

    def __getitem__(self, *names):
        """
        Retrieve an object by its name.

        Args:
            names (list[str]): Names of the objects to retrieve

        Returns:
            The object with the given name or a list of objects if multiple names are provided

        Raises:
            KeyError: If no object with the given name exists
        """
        names = flatten(names)
        if len(names) == 1:
            try:
                return super().__getitem__(names[0])
            except KeyError:
                active_logger.raise_(
                    KeyError, f"No object with name '{names[0]}' found"
                )
        else:
            return [self[name] for name in names if name in self]

    def __contains__(self, cls):
        """
        Check if an object is contained within this DesignClass collection.
        
        Provides flexible membership testing that works with both object names
        (as strings) and object instances. This enables intuitive checking
        whether objects are present in the collection regardless of how they
        are referenced.

        Args:
            cls (object, str): The object to check for membership.
                - str: Object name to check in the keys
                - object: Object instance to check in the values
            
        Returns:
            bool: True if the object or name is in the collection, False otherwise.

        Examples:
            >>> design = DesignClass()
            >>> obj = CustomObject(name="test")
            >>> design.add(obj)
            >>> 
            >>> "test" in design      # True - check by name
            >>> obj in design         # True - check by object
            >>> "missing" in design   # False - name not found

        Use Cases:
            - Validating object existence before retrieval
            - Preventing duplicate additions
            - Design rule consistency checking
            - User interface object selection validation
        """
        if isinstance(cls, str):
            return cls in self.keys()
        return cls in self.values()

    def by_priority(self, *names):
        """
        Return class names sorted by their priorities given a list of names.

        Args:
            names (list[str]): List of object names to retrieve and sort

        Returns:
            list[str]: Sorted list of names of classes (lowest priority first)

        Raises:
            KeyError: If any name in the list doesn't exist
        """
        return [obj.name for obj in sorted(self[names], key=lambda obj: obj.priority)]
