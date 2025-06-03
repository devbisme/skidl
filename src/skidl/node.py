# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from collections import defaultdict

from skidl.utilities import export_to_all


"""
Node class for storing circuit hierarchy.
"""


@export_to_all
class Node:
    """Data structure for holding information about a node in the circuit hierarchy."""

    def __init__(
        self,
        circuit=None
    ):
        self.parent = None
        self.children = defaultdict(
            lambda: type(self)(None)
        )
        self.parts = []

        # if circuit:
        #     self.add_circuit(circuit)
