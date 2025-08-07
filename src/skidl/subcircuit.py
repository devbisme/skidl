# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Hierarchical grouping in SKiDL.

This module provides classes and decorators for organizing circuit components
into hierarchical groups. Hierarchical grouping helps manage complexity in
large designs by organizing components into logical blocks, similar to
subcircuits in traditional schematic capture tools.
"""

import functools

from .skidlbaseobj import SkidlBaseObject
from .utilities import export_to_all
from .partclass import PartClassList
from .netclass import NetClassList


__all__ = ["subcircuit", "Group"]


@export_to_all
class SubCircuit(SkidlBaseObject):
    """
    Class for managing hierarchical grouping of circuit components.
    
    This class creates a named hierarchical group in a circuit design.
    Parts created within the group context will be assigned to this 
    hierarchical level, making them easier to manage in complex designs.
    
    Args:
        name_or_func (str or callable): Name for the hierarchical group or a function to be decorated.
        **attrs: Additional attributes to store in the group including:
            circuit (Circuit, optional): The circuit this group belongs to.
            tag (str, optional): Tag to distinguish multiple instances with the same name.
            partclass (PartClassList, optional): List of part classes to use for parts created in this group.
        
    Examples:
        >>> with Subcircuit('amplifier'):
        ...     r1 = Part('Device', 'R', value='10K')  # r1 is in the 'amplifier' group
    """

    def __init__(self, func_or_name, **attrs):
        """Initialize a hierarchical group with a name and optional attributes."""
        super().__init__()

        if callable(func_or_name):
            # If this arg is a function, then the class is being used as a decorator.
            # Store the function and use its name as the group name.
            self.func = func_or_name
            self.name = func_or_name.__name__

            # Use the function docstring as a description of what the group does.
            attrs["description"] = func_or_name.__doc__
            
            # Use the function signature from the SKiDL code when __call__() is run.
            # This is useful for debugging and introspection.
            functools.update_wrapper(self, self.func)

        else:
            # If this arg is a string, then the class is being used as a class or context manager.
            self.name = func_or_name

        self.circuit = attrs.pop("circuit", default_circuit)  # The circuit this group belongs to.
        self.tag = attrs.pop("tag", None)  # Tag to distinguish multiple instances of the group.
        self.partclass = attrs.pop("partclass", PartClassList())  # Part classes for parts in this group.
        self.netclass = attrs.pop("netclass", NetClassList())  # Net classes for nets in this group.
        self.description = attrs.pop("description", None)  # Description of the general purpose of the group.
        self.purpose = attrs.pop("purpose", None)  # A specific purpose for this instantiation of the group.

        self.node = None  # Placeholder for Node class, to be set in __enter__.

        # Store any additional attributes.
        for k, v in attrs.items():
            setattr(self, k, v)

    def __enter__(self):
        """
        Create a context for hierarchical grouping of parts and nets.
        
        This activates the group as a child of the currently active node in the circuit, 
        making it the current hierarchical context. The hierarchical Node object is stored for later use.
        
        Returns:
            Group: The group instance (self).
        """
        self.node = self.circuit.activate(name=self.name, tag=self.tag)
        # The following assignments set the attributes in the node (see _setattr__ below).
        self.partclass = self.partclass
        self.netclass = self.netclass
        self.description = self.description
        self.purpose = self.purpose
        return self

    def __exit__(self, type, value, traceback):
        """
        Exit a hierarchical grouping context.
        
        This deactivates the current hierarchical level and returns to the previous one.
        
        Args:
            type: Exception type if an exception occurred.
            value: Exception value if an exception occurred.
            traceback: Traceback if an exception occurred.
        """
        self.circuit.deactivate()

    def __setattr__(self, key, value):
        """
        Set an attribute on the group instance with special handling for certain keys.
        
        This allows setting attributes on the group instance using the syntax:
        `group.key = value`. If the key is one of the special attributes
        (`tag`, `partclass`, 'netclass', `description`, `purpose`), it will also set
        the attribute on the node associated with the group if it exists.
        
        Args:
            key: The name of the attribute to set.
            value: The value to assign to the attribute.
        """
        # First, store the attribute in the object itself
        super().__setattr__(key, value)
        
        # Then, if it's a special attribute and node exists, also set it on the node
        if key in ("tag", "partclass", "netclass", "description", "purpose"):
            if getattr(self, "node", None):
                setattr(self.node, key, value)

    def __call__(self, *args, **kwargs):

        circuit = kwargs.pop("circuit", default_circuit)
        tag = kwargs.pop("tag", self.tag)

        # Most likely the group is being created within the current Circuit, but
        # enter the context just in case it's a different Circuit. This won't hurt 
        # anything if it's the same Circuit.
        with circuit:
            # Enter the hierarchical group context and call the function within it.
            with self:
                # Call the function to create whatever circuitry it handles.
                # The arguments to the function are usually nets to be connected to the
                # parts instantiated in the function, but they may also be user-specific
                # and have no effect on the mechanics of adding parts or nets although
                # they may direct the function as to what parts and nets get created.
                # Store any results it returns. These results are user-specific
                # and have no effect on the mechanics of adding parts or nets.
                results = self.func(*args, **kwargs)

        # At this point, we've popped out of the SubCircuit and Circuit contexts
        # and can return any results of the function call.
        return results

# Aliases for SubCircuit to maintain backward compatibility.
Group = SubCircuit
subcircuit = SubCircuit
