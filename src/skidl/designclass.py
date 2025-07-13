# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Design class module for managing design objects with priorities and name-based access.

This module provides the DesignClass base class that extends dict functionality
to manage objects with names and priorities, enabling efficient retrieval and
sorting operations.

Classes:
    DesignClass: Base class for managing design objects with priorities and name-based access.

    allowing for retrieval by name and sorting by priority. It extends the built-in
    dict class to provide specialized methods for design object management.

        Inherits all dict attributes and methods.

    Example:
        >>> design = DesignClass()
        >>> obj = SomeObject(name="component1")
        >>> design.add(obj, priority=10)
        >>> retrieved = design["component1"]

        The object must have a 'name' attribute which will be used as the key
        for storage. A priority attribute will be added to the object for
        later sorting operations.

        Example:
            >>> design.add(my_object, priority=5)

        Retrieve one or more objects by their names.

        Supports both single name retrieval and multiple name retrieval.
        When multiple names are provided, returns a list of objects that exist.

            *names: Variable number of object names to retrieve

            object or list: The object with the given name if single name provided,
                          or a list of objects if multiple names are provided

            KeyError: If no object with the given name exists (single name only)

        Example:
            >>> obj = design["component1"]
            >>> objs = design["comp1", "comp2", "comp3"]

        Retrieves the specified objects and sorts them by their priority
        attribute in ascending order (lowest priority first).

            *names: Variable number of object names to retrieve and sort

        Example:
            >>> sorted_objs = design.get_sorted_by_priority("comp1", "comp2")

            list: List of all object names currently stored

        Example:
            >>> names = design.get_all_names()
            >>> print(names)  # ['component1', 'component2', ...]

        Deletes the object with the specified name from the design class.

        Example:
            >>> design.remove("component1")
"""

import sys
from skidl.logger import active_logger
from skidl.utilities import export_to_all


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
            KeyError: If an object with the same name already exists
        """
        if not hasattr(obj, "name"):
            active_logger.raise_(AttributeError, "Object must have a 'name' attribute")

        if priority != None:
            if not isinstance(priority, int) or priority < 0 or priority > sys.maxsize:
                active_logger.raise_(
                    ValueError, f"Priority must be an integer between 0 and {sys.maxsize}"
                )

        if obj.name in self:
            active_logger.raise_(
                KeyError, f"Object with name '{obj.name}' already exists"
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
        if len(names) == 1:
            try:
                return super().__getitem__(names[0])
            except KeyError:
                active_logger.raise_(
                    KeyError, f"No object with name '{names[0]}' found"
                )
        else:
            return [self[name] for name in names if name in self]

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
