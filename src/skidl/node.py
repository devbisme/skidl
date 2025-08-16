# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Node class for storing circuit hierarchy.

This module provides the Node class which represents a hierarchical structure
for organizing circuit components. Nodes can have parent-child relationships
and contain parts, allowing for structured circuit design and organization.
"""

import functools
from simp_sexp import Sexp

from .design_class import PartClasses
from .design_class import NetClasses
from .scriptinfo import get_skidl_trace
from .skidlbaseobj import SkidlBaseObject
from .utilities import export_to_all, get_unique_name


__all__ = ["SubCircuit", "subcircuit", "Group"]


@export_to_all
class Node(SkidlBaseObject):
    """
    Data structure for holding information about a node in the circuit hierarchy.
    
    A Node represents a hierarchical container that can hold circuit parts and
    maintain parent-child relationships with other nodes. This enables organized
    circuit design with clear structural relationships.
    """

    def __init__(
        self,
        func_or_name,
        tag=None,
        circuit=None,
        **attrs
    ):
        """
        Initialize a new Node instance.
        
        Args:
            func_or_name (str or callable): Name for the hierarchical group or a function to be decorated.
            tag (Any, optional): An optional tag for categorizing or identifying the node.
            circuit (Circuit, optional): The circuit this node belongs to. If None,
                                        uses the default circuit.
            **attrs: Additional attributes to store in the node.
        """
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

        # Store tag.
        self.tag = tag

        # Store the circuit this node belongs to.
        self.circuit = circuit or default_circuit

        # New nodes have no parent or children.
        self.parent = None
        self.children = []  # New nodes are childless.

        # Store the stack trace for where this node was instantiated.
        self.skidl_trace = get_skidl_trace()

        # Create lists to hold the parts, nets, and buses that are instantiated in this node.
        self.parts = []
        self.nets = []
        self.buses = []

        # Create lists for part and net classes that are directly assigned to this node.
        self._partclasses = PartClasses()
        self.partclasses = attrs.pop("partclasses", PartClasses())
        self._netclasses = NetClasses()
        self.netclasses = attrs.pop("netclasses", NetClasses())

        # Set the description and purpose of the circuitry in this node.
        self.description = attrs.pop("description", "")
        self.purpose = attrs.pop("purpose", "")

        # Store any additional attributes.
        for k, v in attrs.items():
            setattr(self, k, v)

    def __enter__(self):
        """
        Create a context for hierarchical grouping of parts and nets.
        
        This activates the group as a child of the currently active node in the circuit, 
        making it the current hierarchical context. The hierarchical Node object is stored for later use.
        
        Returns:
            Node: The Node object corresponding to this subcircuit.
        """
        self.circuit.activate(self)
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
        """
        Call the node's function within the hierarchical context.
        
        Creates a new node instance and executes the stored function within
        the node's circuit and hierarchical context.
        
        Args:
            *args: Positional arguments to pass to the node's function.
            **kwargs: Keyword arguments to pass to the node's function.
            
        Returns:
            Any: The return value of the node's function.
        """
        node = self.spin_off(**kwargs)

        for kw in ('circuit', 'tag', 'func', 'description', 'purpose'):
            kwargs.pop(kw, None)

        # Most likely the group is being created within the current Circuit, but
        # enter the context just in case it's a different Circuit. This won't hurt 
        # anything if it's the same Circuit.
        with node.circuit:
            # Enter the hierarchical group context and call the function within it.
            with node:
                # Call the function to create whatever circuitry it handles.
                # The arguments to the function are usually nets to be connected to the
                # parts instantiated in the function, but they may also be user-specific
                # and have no effect on the mechanics of adding parts or nets although
                # they may direct the function as to what parts and nets get created.
                # Store any results it returns. These results are user-specific
                # and have no effect on the mechanics of adding parts or nets.
                results = node.func(*args, **kwargs)

        # At this point, we've popped out of the SubCircuit and Circuit contexts
        # and can return any results of the function call.
        return results
    
    def add_child(self, child):
        """
        Add a child node to this node.
        
        Establishes a parent-child relationship between this node and the provided
        child node. Ensures the child has a unique name among siblings.
        
        Args:
            child (Node): The child node to add to this node.
        """
        if child.name:
            child.name = get_unique_name(self.children, "name", child.name, None)
        self.children.append(child)
        child.parent = self

    def spin_off(self, **kwargs):
        """
        Create a new node for the purpose of spinning off a subcircuit.
        
        Creates a copy of this node with potentially modified attributes,
        typically used when creating instances of a node template.
        
        Args:
            **kwargs: Keyword arguments to override node attributes.
            
        Returns:
            Node: A new Node instance based on this node.
        """
        local_kwargs = dict(kwargs)

        # The new node will be in the circuit specified in the kwargs
        # or it will be in the circuit that is currently active.
        local_kwargs['circuit'] = kwargs.get('circuit', default_circuit)

        # Copy some other relevant attributes from the source node.
        for kw in ('tag', 'func', 'description', 'purpose'):
            local_kwargs[kw] = kwargs.get(kw, getattr(self, kw))

        # Create the spun-off node and return it.
        return Node(self.name, **local_kwargs)

    def to_tuple(self):
        """
        Convert the node and its children to a tuple representation.
        
        Creates a nested tuple structure representing this node and all its
        children, including their names, tags, parts, and hierarchical structure.
        
        Returns:
            tuple: A tuple containing (name, tag, parts_refs, children_tuples).
        """
        return (self.name, self.tag, tuple([p.ref for p in self.parts]), tuple([child.to_tuple() for child in self.children]) or None)
    
    def __str__(self):
        """
        Return a string representation of the node and its hierarchy.
        
        Returns:
            str: S-expression formatted string representation of the node hierarchy.
        """
        return Sexp(self.to_tuple()).to_str()

    @property
    def hiernodes(self):
        """
        Return a tuple of the chain of nodes from the top-most node to this one (self).
        
        This property traverses up the hierarchy from the current node to the root,
        then reverses the order to provide a path from root to current node.
        
        Returns:
            tuple: A tuple of Node objects representing the hierarchical path
                  from the root node to this node, inclusive.
        """
        n = self
        path = [n]
        while n.parent:
            n = n.parent
            path.append(n)
        return tuple(reversed(path))

    @property
    def hiertuple(self):
        """
        Return a tuple of the node's hierarchy path names from top-most node to this one (self).
        
        This provides a string representation of the hierarchical path by extracting
        the names from each node in the hierarchy chain.
        
        Returns:
            tuple: A tuple of strings representing the names of nodes in the
                  hierarchical path from root to this node.
        """
        return tuple(n.name for n in self.hiernodes)
    
    @property
    def partclasses(self):
        """
        Return a list of part classes assigned to this node and its ancestors.
        
        Aggregates part classes from this node and all ancestor nodes in the hierarchy.
        
        Returns:
            PartClasses: Combined part classes from this node and its ancestors.
        """
        total_partclasses = PartClasses()
        for node in self.hiernodes:
            total_partclasses.add(node._partclasses)
        return total_partclasses

    @partclasses.setter
    def partclasses(self, *partclasses):
        """
        Set the part classes for this node.
        
        This method allows assigning one or more PartClass objects to this node.
        It adds the provided part classes to the node's part class list.
        
        Args:
            *partclasses: One or more PartClass objects to assign to this node.
        """
        self._partclasses.add(partclasses, circuit=self.circuit)

    @partclasses.deleter
    def partclasses(self):
        """Delete the part classes for this node."""
        self._partclasses = PartClasses()

    @property
    def netclasses(self):
        """
        Return a list of net classes assigned to this node and its ancestors.
        
        Aggregates net classes from this node and all ancestor nodes in the hierarchy.
        
        Returns:
            NetClasses: Combined net classes from this node and its ancestors.
        """
        total_netclasses = NetClasses()
        for node in self.hiernodes:
            total_netclasses.add(node._netclasses)
        return total_netclasses

    @netclasses.setter
    def netclasses(self, *netclasses):
        """
        Set the net classes for this node.
        
        This method allows assigning one or more NetClass objects to this node.
        It adds the provided net classes to the node's net class list.
        
        Args:
            *netclasses: One or more NetClass objects to assign to this node.
        """
        self._netclasses.add(netclasses, circuit=self.circuit)

    @netclasses.deleter
    def netclasses(self):
        """Delete the net classes for this node."""
        self._netclasses = NetClasses()


# Aliases for SubCircuit to maintain backward compatibility.
SubCircuit = Node
Group = Node
subcircuit = Node
