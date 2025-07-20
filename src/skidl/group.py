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


__all__ = ["SubCircuit", "subcircuit"]


@export_to_all
class Group(SkidlBaseObject):
    """
    Context manager for hierarchical grouping of circuit components.
    
    The Group class creates a named hierarchical level in a circuit design.
    Components created within the group context will be assigned to this 
    hierarchical level, making them easier to manage in complex designs.
    
    Args:
        name (str): Name for the hierarchical group.
        circuit (Circuit, optional): The circuit this group belongs to.
        tag (str, optional): Tag to distinguish multiple instances with the same name.
        **attrs: Additional attributes to store in the node.
        
    Examples:
        >>> with Group('amplifier'):
        ...     r1 = Part('Device', 'R', value='10K')  # r1 is in the 'amplifier' group
    """

    def __init__(self, func_or_name, **attrs):
        """Initialize a hierarchical group with a name and optional attributes."""
        super().__init__()
        if callable(func_or_name):
            self.func = func_or_name
            self.name = func_or_name.__name__  # Use function name as the group name.
        else:
            self.name = func_or_name
        self.circuit = attrs.pop("circuit", default_circuit)
        self.tag = attrs.pop("tag", None)
        self.partclass = attrs.pop("partclass", PartClassList())
        self.node = None  # Placeholder for Node class, to be set in __enter__.

        # Store any additional attributes.
        for k, v in attrs.items():
            setattr(self, k, v)

    def __enter__(self):
        """
        Create a context for hierarchical grouping of parts and nets.
        
        This activates the group in the circuit, making it the current hierarchical context.
        The hierarchical Node object is stored for later use.
        
        Returns:
            Group: The group instance (self).
        """
        self.node = self.circuit.activate(name=self.name, tag=self.tag)
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

    def __call__(self, *args, **kwargs):
        circuit = kwargs.pop("circuit", default_circuit)
        # circuit = kwargs.pop("circuit", self.circuit)
        tag = kwargs.pop("tag", self.tag)

        # Most likely the group is being created within the current Circuit, but
        # enter the context just in case it's a different Circuit. This won't hurt 
        # anything if it's the same Circuit.
        with circuit:
            # Then create a hierarchical group context and call the function within it.
            with self:

                # Call the function to create whatever circuitry it handles.
                # The arguments to the function are usually nets to be connected to the
                # parts instantiated in the function, but they may also be user-specific
                # and have no effect on the mechanics of adding parts or nets although
                # they may direct the function as to what parts and nets get created.
                # Store any results it returns as a list. These results are user-specific
                # and have no effect on the mechanics of adding parts or nets.
                results = self.func(*args, **kwargs)

        # At this point, we've popped out of the group and Circuit contexts
        # and can return the results of the function call.
        return results

SubCircuit = Group  # Alias for Group to maintain backward compatibility.


# @export_to_all
# def SubCircuit(f):
#     """
#     Decorator for creating hierarchical subcircuits.
    
#     When applied to a function, this decorator creates a hierarchical context
#     around the function's execution, placing all components created within
#     the function into a hierarchical group named after the function.
    
#     Args:
#         f (function): The function to decorate.
        
#     Returns:
#         function: Decorated function that creates components within a hierarchical group.
        
#     Examples:
#         >>> @SubCircuit
#         >>> def amplifier(in_net, out_net):
#         ...     r1 = Part('Device', 'R', value='10K')
#         ...     # All parts created here are in the 'amplifier' group
#     """

#     @functools.wraps(f)
#     def sub_f(*args, **kwargs):
#         """
#         Wrapper function that executes the decorated function within a hierarchical group.
        
#         Args:
#             *args: Arguments to pass to the decorated function.
#             **kwargs: Keyword arguments to pass to the decorated function.
            
#         Returns:
#             Any: The return value from the decorated function.
#         """
#         circuit = kwargs.pop("circuit", default_circuit)
#         tag = kwargs.pop("tag", None)

#         # Most likely the group is being created within the current Circuit, but
#         # enter the context just in case it's a different Circuit. This won't hurt 
#         # anything if it's the same Circuit.
#         with circuit:
#             # Then create a hierarchical group context and call the function within it.
#             with Group(name=f.__name__, tag=tag, circuit=circuit):

#                 # Call the function to create whatever circuitry it handles.
#                 # The arguments to the function are usually nets to be connected to the
#                 # parts instantiated in the function, but they may also be user-specific
#                 # and have no effect on the mechanics of adding parts or nets although
#                 # they may direct the function as to what parts and nets get created.
#                 # Store any results it returns as a list. These results are user-specific
#                 # and have no effect on the mechanics of adding parts or nets.
#                 results = f(*args, **kwargs)

#         # At this point, we've popped out of the group and Circuit contexts
#         # and can return the results of the function call.
#         return results

#     return sub_f


# The decorator can also be called as "@subcircuit".
subcircuit = SubCircuit
