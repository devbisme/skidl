# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from collections import defaultdict

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
        parent=None,
        circuit=None
    ):
        super().__init__()
        self.parent = parent
        self.children = defaultdict(
            lambda: type(self)(None)
        )
        self.circuit = circuit
        self.name = get_unique_name(self.circuit.nodes, "name", "NODE", name)
        self.parts = []

    @property
    def hiertuple(self):
        n = self
        path = [n.name]
        while n.parent:
            n = n.parent
            path.append(n.name)
        return tuple(reversed(path))
