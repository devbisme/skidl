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

    filename_sz = 20
    name_sz = 40

    def __init__(
        self,
        circuit=None,
        filepath=".",
        top_name="",
    ):
        self.parent = None
        self.children = defaultdict(
            lambda: self.__class__(None, tool_module, filepath, top_name, title, flatness)
        )
        self.filepath = filepath
        self.top_name = top_name
        self.parts = []

        if circuit:
            self.add_circuit(circuit)

    def find_node_with_part(self, part):
        """Find the node that contains the part based on its hierarchy.

        Args:
            part (Part): The part being searched for in the node hierarchy.

        Returns:
            Node: The Node object containing the part.
        """

        from skidl.circuit import HIER_SEP

        level_names = part.hierarchy.split(HIER_SEP)
        node = self
        for lvl_nm in level_names[1:]:
            node = node.children[lvl_nm]
        assert part in node.parts
        return node

    def add_circuit(self, circuit):
        """Add parts in circuit to node and its children.

        Args:
            circuit (Circuit): Circuit object.
        """

        # Build the circuit node hierarchy by adding the parts.
        for part in circuit.parts:
            self.add_part(part)

        # Add terminals to nodes in the hierarchy for nets that span across nodes.
        for net in circuit.nets:
            # Skip nets that are stubbed since there will be no wire to attach to the NetTerminal.
            if getattr(net, "stub", False):
                continue

            # Search for pins in different nodes.
            for pin1, pin2 in zip(net.pins[:-1], net.pins[1:]):
                if pin1.part.hierarchy != pin2.part.hierarchy:
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

                if part.hierarchy in visited:
                    # Already added a terminal to this node, so don't add another.
                    continue

                # Add NetTerminal to the node with this part/pin.
                self.find_node_with_part(part).add_terminal(net)

                # Record that this hierarchical node was visited.
                visited.append(part.hierarchy)

        # Flatten the hierarchy as specified by the flatness parameter.
        self.flatten(self.flatness)

    def add_part(self, part, level=0):
        """Add a part to the node at the appropriate level of the hierarchy.

        Args:
            part (Part): Part to be added to this node or one of its children.
            level (int, optional): The current level (depth) of the node in the hierarchy. Defaults to 0.
        """

        from skidl.circuit import HIER_SEP

        # Get list of names of hierarchical levels (in order) leading to this part.
        level_names = part.hierarchy.split(HIER_SEP)

        # Get depth in hierarchy for this part.
        part_level = len(level_names) - 1
        assert part_level >= level

        # Node name is the name assigned to this level of the hierarchy.
        self.name = level_names[level]

        # File name for storing the schematic for this node.
        base_filename = "_".join([self.top_name] + level_names[0 : level + 1]) + ".sch"
        self.sheet_filename = base_filename

        if part_level == level:
            # Add part to node at this level in the hierarchy.
            if not part.unit:
                # Monolithic part so just add it to the node.
                self.parts.append(part)
            else:
                # Multi-unit part so add each unit to the node.
                # FIXME: Some part units might be split into other nodes.
                for p in part.unit.values():
                    self.parts.append(p)
        else:
            # Part is at a level below the current node. Get the child node using
            # the name of the next level in the hierarchy for this part.
            child_node = self.children[level_names[level + 1]]

            # Attach the child node to this node. (It may have just been created.)
            child_node.parent = self

            # Add part to the child node (or one of its children).
            child_node.add_part(part, level + 1)

    def get_internal_nets(self):
        """Return a list of nets that have at least one pin on a part in this node."""

        processed_nets = []
        internal_nets = []
        for part in self.parts:
            for part_pin in part:
                # No explicit wire for pins connected to labeled stub nets.
                if part_pin.stub:
                    continue

                # No explicit wires if the pin is not connected to anything.
                if not part_pin.is_connected():
                    continue

                net = part_pin.net

                # Skip nets that have already been processed.
                if net in processed_nets:
                    continue

                processed_nets.append(net)

                # Skip stubbed nets.
                if getattr(net, "stub", False) is True:
                    continue

                # Add net to collection if at least one pin is on one of the parts of the node.
                for net_pin in net.pins:
                    if net_pin.part in self.parts:
                        internal_nets.append(net)
                        break

        return internal_nets

    def get_internal_pins(self, net):
        """Return the pins on the net that are on parts in the node.

        Args:
            net (Net): The net whose pins are being examined.

        Returns:
            list: List of pins on the net that are on parts in this node.
        """

        # Skip pins on stubbed nets.
        if getattr(net, "stub", False) is True:
            return []

        return [pin for pin in net.pins if pin.stub is False and pin.part in self.parts]
