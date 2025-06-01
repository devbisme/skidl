# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import re
from collections import defaultdict
from itertools import chain

from skidl.utilities import export_to_all
from skidl.geometry import BBox, Point, Tx, Vector
from skidl.node import Node
from .place import Placer
from .route import Router


"""
Node subclass used for generating schematics.
"""


@export_to_all
class SchNode(Node, Placer, Router):
    """Data structure for holding information about a node in the circuit hierarchy."""

    filename_sz = 20
    name_sz = 40

    def __init__(
        self,
        circuit=None,
        tool_module=None,
        filepath=".",
        top_name="",
        title="",
        flatness=0.0,
    ):
        # Initialize using the Node superclass.
        super().__init__(None, filepath, top_name)
        self.parent = None
        self.children = defaultdict(
            lambda: self.__class__(
                None, tool_module, filepath, top_name, title, flatness
            )
        )
        self.sheet_name = None
        self.sheet_filename = None
        self.title = title
        self.flatness = flatness
        self.flattened = False
        self.tool_module = tool_module  # Backend tool.
        self.wires = defaultdict(list)
        self.junctions = defaultdict(list)
        self.tx = Tx()
        self.bbox = BBox()

        if circuit:
            self.add_circuit(circuit)

    def add_circuit(self, circuit):
        """Add parts in circuit to node and its children.

        Args:
            circuit (Circuit): Circuit object.
        """

        # Build the circuit node hierarchy by adding the parts.
        super().add_circuit(circuit)

        # Add terminals to nodes in the hierarchy for nets that span across nodes.
        for net in circuit.nets:
            # Skip nets that are stubbed since there will be no wire to attach to the NetTerminal.
            if getattr(net, "stub", False):
                continue

            # Search for pins in different nodes.
            for pin1, pin2 in zip(net.pins[:-1], net.pins[1:]):
                if pin1.part.hierarchical_name != pin2.part.hierarchical_name:
                    # Found pins in different nodes, so break and add terminals to nodes below.
                    break
            else:
                if len(net.pins) == 1:
                    # Single pin on net and not stubbed, so add a terminal to it below.
                    pass
                elif not net.is_implicit():
                    # The net has a user-assigned name, so add a terminal to it below.
                    pass
                else:
                    # No need for net terminal because there are multiple pins
                    # and they are all in the same node.
                    continue

            # Add a single terminal to each node that contains one or more pins of the net.
            visited = []
            for pin in net.pins:
                # A stubbed pin can't be used to add NetTerminal since there is no explicit wire.
                if pin.stub:
                    continue

                part = pin.part

                if part.hierarchical_name in visited:
                    # Already added a terminal to this node, so don't add another.
                    continue

                # Add NetTerminal to the node with this part/pin.
                self.find_node_with_part(part).add_terminal(net)

                # Record that this hierarchical node was visited.
                visited.append(part.hierarchical_name)

        # Flatten the hierarchy as specified by the flatness parameter.
        self.flatten(self.flatness)

    def add_terminal(self, net):
        """Add a terminal for this net to the node.

        Args:
            net (Net): The net to be added to this node.
        """

        from skidl.circuit import HIER_SEP
        from .net_terminal import NetTerminal

        nt = NetTerminal(net, self.tool_module)
        self.parts.append(nt)

    def external_bbox(self):
        """Return the bounding box of a hierarchical sheet as seen by its parent node."""
        bbox = BBox(Point(0, 0), Point(500, 500))
        bbox.add(Point(len("File: " + self.sheet_filename) * self.filename_sz, 0))
        bbox.add(Point(len("Sheet: " + self.name) * self.name_sz, 0))

        # Pad the bounding box for extra spacing when placed.
        bbox = bbox.resize(Vector(100, 100))

        return bbox

    def internal_bbox(self):
        """Return the bounding box for the circuitry contained within this node."""

        # The bounding box is determined by the arrangement of the node's parts and child nodes.
        bbox = BBox()
        for obj in chain(self.parts, self.children.values()):
            tx_bbox = obj.bbox * obj.tx
            bbox.add(tx_bbox)

        # Pad the bounding box for extra spacing when placed.
        bbox = bbox.resize(Vector(100, 100))

        return bbox

    def calc_bbox(self):
        """Compute the bounding box for the node in the circuit hierarchy."""

        if self.flattened:
            self.bbox = self.internal_bbox()
        else:
            # Use hierarchical bounding box if node has not been flattened.
            self.bbox = self.external_bbox()

        return self.bbox

    def flatten(self, flatness=0.0):
        """Flatten node hierarchy according to flatness parameter.

        Args:
            flatness (float, optional): Degree of hierarchical flattening (0=completely hierarchical, 1=totally flat). Defaults to 0.0.

        Create hierarchical sheets for the node and its child nodes. Complexity (or size) of a node
        and its children is the total number of part pins they contain. The sum of all the child sizes
        multiplied by the flatness is the number of part pins that can be shown on the schematic
        page before hierarchy is used. The instances of each type of child are flattened and placed
        directly in the sheet as long as the sum of their sizes is below the slack. Otherwise, the
        children are included using hierarchical sheets. The children are handled in order of
        increasing size so small children are more likely to be flattened while large, complicated
        children are included using hierarchical sheets.
        """

        # Create sheets and compute complexity for any circuitry in hierarchical child nodes.
        for child in self.children.values():
            child.flatten(flatness)

        # Complexity of the parts directly instantiated at this hierarchical level.
        self.complexity = sum((len(part) for part in self.parts))

        # Sum the child complexities and use it to compute the number of pins that can be
        # shown before hierarchical sheets are used.
        child_complexity = sum((child.complexity for child in self.children.values()))
        slack = child_complexity * flatness

        # Group the children according to what types of modules they are by removing trailing instance ids.
        child_types = defaultdict(list)
        for child_id, child in self.children.items():
            child_types[re.sub(r"\d+$", "", child_id)].append(child)

        # Compute the total size of each type of children.
        child_type_sizes = dict()
        for child_type, children in child_types.items():
            child_type_sizes[child_type] = sum((child.complexity for child in children))

        # Sort the groups from smallest total size to largest.
        sorted_child_type_sizes = sorted(
            child_type_sizes.items(), key=lambda item: item[1]
        )

        # Flatten each instance in a group until the slack is used up.
        for child_type, child_type_size in sorted_child_type_sizes:
            if child_type_size <= slack:
                # Include the circuitry of each child instance directly in the sheet.
                for child in child_types[child_type]:
                    child.flattened = True
                # Reduce the slack by the sum of the child sizes.
                slack -= child_type_size
            else:
                # Not enough slack left. Add these children as hierarchical sheets.
                for child in child_types[child_type]:
                    child.flattened = False

    def collect_stats(self, **options):
        """Return comma-separated string with place & route statistics of a schematic."""

        def get_wire_length(node):
            """Return the sum of the wire segment lengths between parts in a routed node."""

            wire_length = 0

            # Sum wire lengths for child nodes.
            for child in node.children.values():
                wire_length += get_wire_length(child)

            # Add the wire lengths between parts in the top node.
            for wire_segs in node.wires.values():
                for seg in wire_segs:
                    len_x = abs(seg.p1.x - seg.p2.x)
                    len_y = abs(seg.p1.y - seg.p2.y)
                    wire_length += len_x + len_y

            return wire_length

        return "{}\n".format(get_wire_length(self))
