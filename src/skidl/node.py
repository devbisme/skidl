# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Node class for storing circuit hierarchy.

This module provides the Node class which represents a hierarchical structure
for organizing circuit components. Nodes can have parent-child relationships
and contain parts, allowing for structured circuit design and organization.
"""

from collections import defaultdict

from skidl.partclass import PartClassList
from skidl.scriptinfo import get_skidl_trace
from skidl.skidlbaseobj import SkidlBaseObject
from skidl.utilities import export_to_all, get_unique_name


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
        name,
        tag=None,
        parent=None,
        circuit=None,
        **attrs
    ):
        """
        Initialize a new Node instance.
        
        Args:
            name (str): The name for this node. If None, defaults to "NODE".
                       Names are automatically made unique within the parent's children.
            tag (Any, optional): An optional tag for categorizing or identifying the node.
            parent (Node, optional): The parent node. If provided, this node becomes
                                   a child of the parent.
            circuit (Circuit, optional): The circuit this node belongs to. If None,
                                        uses the default circuit.
            **attrs: Additional attributes to store in the node.
        """
        super().__init__()

        # Store the circuit this node belongs to.
        self.circuit = circuit or default_circuit

        # Setup node parent and child relationships.
        self.children = []  # New nodes are childless.
        self.parent = parent
        if parent:
            # Make this node a child of the parent.
            parent.children.append(self)
            # Assign a name to this new child node.
            # Use the name as the prefix so that it always gets an index number appended to it.
            # If no name was given, then use "NODE" as the default prefix.
            self.name = get_unique_name(self.parent.children, "name", name or "NODE", None)
        else:
            # This node has no parent so it is the root node and has no name.
            self.name = ""
        self.tag = tag

        # Store the stack trace for where this node was instantiated.
        self.skidl_trace = get_skidl_trace()

        # Create a list to hold the parts that are instantiated in this this node.
        self.parts = []

        # Create a list for part classes that are instantiated in this node.
        self._partclass = PartClassList()

        # Store any additional attributes.
        for k, v in attrs.items():
            setattr(self, k, v)

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
    def partclass(self):
        """Return a list of part classes directly assigned to this node."""
        return self._partclass

    @partclass.setter
    def partclass(self, *partclasses):
        """
        Set the part classes for this node.
        
        This method allows assigning one or more PartClass objects to this node.
        It adds the provided part classes to the node's part class list.
        
        Args:
            *partclasses: One or more PartClass objects to assign to this node.
        """
        self._partclass.add(*partclasses, circuit=self.circuit)

    @partclass.deleter
    def partclass(self):
        """Delete the part classes for this node."""
        self._partclass = PartClassList()