# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from collections import defaultdict

from skidl.scriptinfo import get_skidl_trace
from skidl.skidlbaseobj import SkidlBaseObject
from skidl.utilities import export_to_all, get_unique_name


"""
Node class for storing circuit hierarchy.
"""


@export_to_all
class Node(SkidlBaseObject):
    """Data structure for holding information about a node in the circuit hierarchy."""

    def __init__(
        self,
        name,
        tag=None,
        parent=None,
        circuit=None
    ):
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

    @property
    def hiertuple(self):
        """Return a tuple of the node's hierarchy path."""
        n = self
        path = [n.name]
        while n.parent:
            n = n.parent
            path.append(n.name)
        return tuple(reversed(path))
