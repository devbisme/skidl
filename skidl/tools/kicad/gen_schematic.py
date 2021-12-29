# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.


from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from itertools import chain
import re
import time
from builtins import range, str
from collections import defaultdict, OrderedDict, Counter
import os.path
from types import DynamicClassAttribute

from future import standard_library

from skidl.tools.kicad.kicad import DrawText

from .geometry import Point, Vector, BBox, Segment, Tx
from .symbol import calc_symbol_bbox
from ...logger import active_logger
from ...net import NCNet
from ...part import Part
from ...scriptinfo import *
from ...utilities import *


standard_library.install_aliases()

"""
Generate a KiCad EESCHEMA schematic from a Circuit object.
"""

GRID = 50
PIN_LABEL_FONT_SIZE = 50


def rotate_power_pins(part, pin_cnt_threshold=10000):
    """Rotate a part based on the direction of its power pins.

    Args:
        part (Part): The part to be rotated.
        pin_cnt_threshold (int): Parts with more pins than this will not be rotated.

    This function is to make sure that voltage sources face up and gnd pins
    face down.
    """

    def is_pwr(net):
        return net_name.startswith("+")

    def is_gnd(net):
        return "gnd" in net_name.lower()

    # Don't rotate parts with too many pins.
    if len(part) > pin_cnt_threshold:
        return

    # Tally what rotation would make each pwr/gnd pin point up or down.
    rotation_tally = Counter()
    for pin in part:
        net_name = getattr(pin.net, "name", "").lower()
        if is_gnd(net_name):
            if pin.orientation == "U":
                rotation_tally[0] += 1
            if pin.orientation == "D":
                rotation_tally[180] += 1
            if pin.orientation == "L":
                rotation_tally[90] += 1
            if pin.orientation == "R":
                rotation_tally[270] += 1
        elif is_pwr(net_name):
            if pin.orientation == "D":
                rotation_tally[0] += 1
            if pin.orientation == "U":
                rotation_tally[180] += 1
            if pin.orientation == "L":
                rotation_tally[270] += 1
            if pin.orientation == "R":
                rotation_tally[90] += 1

    # Rotate the part in the direction with the most tallies.
    try:
        rotation = rotation_tally.most_common()[0][0]
    except IndexError:
        pass
    else:
        # Rotate part 90-degrees clockwise until the desired rotation is reached.
        tx_cw_90 = Tx(a=0, b=-1, c=1, d=0)  # 90-degree trans. matrix.
        for _ in range(round(rotation / 90)):
            part.tx = part.tx.dot(tx_cw_90)


def calc_part_bbox(part):
    """Calculate the bare bounding box and labeled bounding box and store it in the part."""

    # Find part bounding box excluding any net labels on pins.
    part.bare_bbox = calc_symbol_bbox(part)[1]

    # Expand the bounding box if it's too small in either dimension.
    resize_xy = Vector(0, 0)
    if part.bare_bbox.w < 100:
        resize_xy.x = (100 - part.bare_bbox.w) / 2
    if part.bare_bbox.h < 100:
        resize_xy.y = (100 - part.bare_bbox.h) / 2
    part.bare_bbox.resize(resize_xy)

    # Find expanded bounding box that includes any labels attached to pins.
    part.bbox = BBox()
    part.bbox.add(part.bare_bbox)
    for pin in part:
        # Add 1 to the label length to account for extra graphics on label.
        lbl_len = (len(pin.label) + 1) * PIN_LABEL_FONT_SIZE
        pin_dir = pin.orientation
        if pin_dir == "U":
            lbl_vector = Vector(0, -lbl_len)
        elif pin_dir == "D":
            lbl_vector = Vector(0, lbl_len)
        elif pin_dir == "L":
            lbl_vector = Vector(lbl_len, 0)
        elif pin_dir == "R":
            lbl_vector = Vector(-lbl_len, 0)
        part.bbox.add(pin.pt + lbl_vector)


def preprocess_parts_and_nets(circuit):
    """Add stuff to parts & nets for doing placement and routing of schematics."""

    # Pre-process nets.
    net_stubs = circuit.get_net_nc_stubs()
    net_stubs = [net for net in net_stubs if not isinstance(net, NCNet)]
    for net in net_stubs:
        if True or net.netclass != "Power":
            for pin in net.pins:
                pin.label = net.name

    # Pre-process parts
    for part in circuit.parts:

        # Initialize part attributes used for generating schematics.
        part.placed = False
        part.tx = Tx()

        # Initialize pin attributes used for generating schematics.
        for pin in part:
            pin.pt = Point(pin.x, pin.y)
            pin.routed = False
            # Assign empty label if not already labeled.
            pin.label = getattr(pin, "label", "")

        # Rotate parts.  Power pins should face up. GND pins should face down.
        rotate_power_pins(part)

        # Compute bounding boxes around parts
        calc_part_bbox(part)


# Sizes of EESCHEMA schematic pages from smallest to largest. Dimensions in mils.
A_sizes_list = [
    ("A4", BBox(Point(0, 0), Point(11693, 8268))),
    ("A3", BBox(Point(0, 0), Point(16535, 11693))),
    ("A2", BBox(Point(0, 0), Point(23386, 16535))),
    ("A1", BBox(Point(0, 0), Point(33110, 23386))),
    ("A0", BBox(Point(0, 0), Point(46811, 33110))),
]
A_sizes = OrderedDict(A_sizes_list)


def get_A_size(bbox):
    """Return the A-size page needed to fit the given bounding box."""

    width = bbox.w
    height = bbox.h * 1.25  # TODO: why 1.25?
    for A_size, page in A_sizes.items():
        if width < page.w and height < page.h:
            return A_size
    return "A0"  # Nothing fits, so use the largest available.


class Sheet:
    """Data structure for hierarchical sheets of a schematic."""

    def __init__(self, node, filepath, title):
        self.node = node
        self.filepath = filepath
        self.title = title
        self.bbox = BBox(Point(0, 0), Point(500, 500))
        self.tx = Tx()
        self.placed = False

    def to_eeschema(self, tx):

        node = self.node
        A_size = get_A_size(node.bbox)
        page_bbox = node.bbox.dot(Tx(d=-1))
        move_to_ctr = A_sizes[A_size].ctr - page_bbox.ctr
        move_to_ctr = move_to_ctr.snap(GRID)  # Keep things on grid.
        move_tx = Tx(d=-1).dot(Tx(dx=move_to_ctr.x, dy=move_to_ctr.y))
        eeschema = node.to_eeschema(move_tx)

        # Generate schematic files for lower-levels in the hierarchy.
        dir = os.path.dirname(self.filepath)
        file_name = os.path.join(dir, node.node_key + ".sch")
        with open(file_name, "w") as f:
            print(
                collect_eeschema_code(
                    eeschema,
                    title=self.title,
                    size=A_size,
                ),
                file=f,
            )

        bbox = self.bbox.dot(self.tx.dot(tx))
        time_hex = hex(int(time.time()))[2:]
        eeschema = []
        eeschema.append("$Sheet")
        eeschema.append(
            "S {} {} {} {}".format(bbox.ul.x, bbox.ul.y, bbox.w, bbox.h)
        )  # upper left x/y, width, height
        eeschema.append("U {}".format(time_hex))
        name = self.node.node_key.split(".")[-1]
        eeschema.append('F0 "{}" 50'.format(name))
        eeschema.append('F1 "{}" 50'.format(file_name))
        eeschema.append("$EndSheet")
        eeschema.append("")
        return "\n".join(eeschema)


class Node:
    """Data structure for holding information about a node in the circuit hierarchy."""

    def __init__(self):
        self.parent = None
        self.children = []
        self.sheets = []
        self.non_sheets = []
        self.parts = []
        self.wires = []
        self.tx = Tx()
        self.bbox = BBox()
        self.placed = False

    def calc_bbox(self):
        """Compute the bounding box for the node in the circuit hierarchy."""

        # If a node has no parent, then its the root node so give it an
        # initial bounding box that's just a starting point for placement.
        if not self.parent:
            self.bbox = BBox(Point(0, 0), Point(0, 0))
        else:
            self.bbox = BBox()

        # Update the bounding box with anything that's been placed.
        for obj in chain(self.parts, self.sheets, self.non_sheets):
            if obj.placed:
                # Only placed parts/sheets/non_sheets contribute to the bounding box.
                tx_bbox = obj.bbox.dot(obj.tx)
                self.bbox.add(tx_bbox)

        # Pad the bounding box for extra spacing when placed.
        self.bbox.resize(Vector(100, 100))

    def create_sheets(self, filepath, title, complexity_threshold=100000):
        """Create hierarchical sheets for complex portions of the circuitry."""

        self.complexity = sum((len(part) for part in self.parts))
        slack = complexity_threshold - self.complexity
        self.non_sheets = sorted(self.children, key=lambda child: child.complexity)
        for child in self.non_sheets[:]:
            if child.complexity <= slack:
                slack -= child.complexity
            else:
                self.sheets.append(Sheet(child, filepath, title))
                self.non_sheets.remove(child)

    def move_pin_to_pin(self, moving_pin, anchor_pin):
        """Move pin to anchor pin and then move it until parts in the node no longer collide."""

        moving_part = moving_pin.part
        anchor_part = anchor_pin.part
        vector = anchor_pin.pt.dot(anchor_part.tx) - moving_pin.pt.dot(moving_part.tx)
        self.move_part(moving_part, vector, Vector(-GRID, 0))

    def move_part(self, obj, vector, dir):
        """Move part/sheet/non_sheet until it doesn't collide with other parts/sheets/non_sheets in the node."""

        # Make sure object stays on the grid.
        vector = vector.snap(GRID)

        # Keep moving part until no collisions occur.
        collision = True
        while collision:
            collision = False

            # Update the object transformation matrix to apply movement.
            obj.tx = obj.tx.dot(Tx(dx=vector.x, dy=vector.y))

            # Compute the transformed bounding box for the object including the move.
            bbox = obj.bbox.dot(obj.tx)

            # Look for intersections with the other parts/sheets/non_sheets in the node.
            for other_obj in chain(self.parts, self.sheets, self.non_sheets):

                # Don't detect collisions with itself.
                if other_obj is obj:
                    continue

                # Don't try to avoid something that hasn't been placed yet.
                if not other_obj.placed:
                    continue

                # Compute the transformed bounding box for the other object.
                other_bbox = other_obj.bbox.dot(other_obj.tx)

                if bbox.intersects(other_bbox):
                    # Collision found. No need to check any further.
                    collision = True
                    # After the initial move, use the dir vector for all further moves.
                    vector = dir
                    break

        # Exit the loop once the part doesn't collide with anything.
        # The final part.tx matrix records the movements that were made.
        obj.placed = True

    def place_parts(self):

        # Move parts connected to central part by unlabeled nets.

        # Find central part in this node that everything else is placed around.
        def find_central_part(node):
            central_part = node.parts[0]
            for part in node.parts[1:]:
                if len(part) > len(central_part):
                    central_part = part
            return central_part

        # Return if there are no parts to place in this node.
        if not self.parts:
            return

        self.central_part = find_central_part(self)
        self.central_part.placed = True

        # Go thru the center part's pins, moving any connected parts closer.
        for anchor_pin in self.central_part:

            # Skip unconnected pins.
            if not anchor_pin.is_connected():
                continue

            # Don't move parts connected to labeled (stub) pins.
            if len(anchor_pin.label) != 0:
                continue

            # Don't move parts connected thru power supply nets.
            if anchor_pin.net.netclass == "Power":
                continue

            # Now move any parts connected to this pin.
            for mv_pin in anchor_pin.net.pins:

                # Don't move parts that have already been moved (including the central part).
                if mv_pin.part.placed:
                    continue

                # Skip parts that aren't in the same node of the hierarchy as the center part.
                if mv_pin.part not in self.parts:
                    # if mv_pin.part.hierarchy != self.central_part.hierarchy:
                    continue

                # OK, finally move the part connected to this pin.
                self.move_pin_to_pin(mv_pin, anchor_pin)

        # Move parts connected to parts moved in step previous step.
        for mv_part in self.parts:

            # Skip parts that have already been moved (including central part).
            if mv_part.placed:
                continue

            # Find a pin to pin connection where the part needs to be moved.
            for mv_pin in mv_part:

                # Skip unconnected pins.
                if not mv_pin.is_connected():
                    continue

                # Don't move parts connected to labeled (stub) pins.
                if len(mv_pin.label) > 0:
                    continue

                # Don't move parts connected thru power supply nets.
                if mv_pin.net.netclass == "Power":
                    continue

                # Move this part toward parts connected to its pin.
                for anchor_pin in mv_pin.net.pins:

                    # Skip parts that aren't in the same node of the hierarchy as the moving part.
                    if anchor_pin.part not in self.parts:
                        # if anchor_pin.part.hierarchy != mv_part.hierarchy:
                        continue

                    # Don't move toward the central part.
                    if anchor_pin.part == self.central_part:
                        continue

                    # Skip connections from the part to itself.
                    if anchor_pin.part == mv_part:
                        continue

                    # OK, finally move the part connected to this pin.
                    self.move_pin_to_pin(mv_pin, anchor_pin)

        # Move any remaining parts in the node down & alternating left/right.

        # Calculate the current bounding box for the node.
        self.calc_bbox()

        # Set up part movement increments.
        start = Point(self.bbox.ctr.x, self.bbox.ll.y - 10 * GRID)
        dir = Vector(GRID, 0)

        for part in self.parts:

            # Skip central part.
            if part is self.central_part:
                continue

            # Move any part that hasn't already been moved.
            if not part.placed:
                part_tx_bbox = part.bbox.dot(part.tx)
                ctr_mv = start - Point(part_tx_bbox.ctr.x, part_tx_bbox.ul.y)
                self.move_part(part, ctr_mv, dir)

                # Switch movement direction for the next unmoved part.
                dir = -dir

        # Calculate the current bounding box for the node.
        self.calc_bbox()

    def place_children(self):
        def place_objects(objs):

            # Calculate the initial node bounding box before objects are placed.
            self.calc_bbox()

            # Set up object movement increments.
            start = Point(self.bbox.ctr.x, self.bbox.ll.y - 10 * GRID)
            dir = Vector(GRID, 0)

            for obj in objs:

                # Move any object that hasn't already been moved.
                if not obj.placed:
                    obj_tx_bbox = obj.bbox.dot(obj.tx)
                    ctr_mv = start - Point(obj_tx_bbox.ctr.x, obj_tx_bbox.ul.y)
                    self.move_part(obj, ctr_mv, dir)

                    # Switch movement direction for the next unmoved object.
                    dir = -dir

            # Calculate the node bounding box once the objects have been placed.
            self.calc_bbox()

        place_objects(self.non_sheets)
        place_objects(self.sheets)

    def place(self):
        """Place parts within a hierarchical node."""

        self.place_parts()
        self.place_children()

    def wire_it(self, net):
        """Generate wire segments for a net."""

        def detect_wire_part_collision(wire, parts):
            """Detect collisions between a wire segment and a collection of parts."""

            for part in parts:
                # bbox = part.bbox.dot(part.tx).dot(part.node.tx)
                bbox = part.bbox.dot(part.tx)
                sides = OrderedDict()
                sides["L"] = Segment(bbox.ul, bbox.ll)
                sides["R"] = Segment(bbox.ur, bbox.lr)
                sides["U"] = Segment(bbox.ul, bbox.ur)
                sides["D"] = Segment(bbox.ll, bbox.lr)

                for side_key, side in sides.items():
                    if wire.intersects(side):
                        return part, side_key

            return None, None  # No intersections detected.

        nets_output = []

        # pins = [pin for pin in net.pins if not pin.stub and pin.part.node==node]
        pins = net.pins
        try:
            pin_pairs = zip(pins[:-1], pins[1:])
        except IndexError:
            return nets_output

        for pin1, pin2 in pin_pairs:
            if pin1.routed and pin2.routed:
                continue
            else:
                pin1.routed = True
                pin2.routed = True

                # Calculate the coordinates of a straight line between the 2 pins that need to connect.
                # Apply the part transformation matrix to find the absolute wire endpoint coordinates.
                # Since all wiring is assumed to be internal to this node, don't apply the node
                # transformation matrix.
                pt1 = pin1.pt.dot(pin1.part.tx)
                pt2 = pin2.pt.dot(pin2.part.tx)

                line = [pt1, pt2]
                for i in range(len(line) - 1):
                    segment = Segment(line[i], line[i + 1])
                    # segment = Segment(Point(line[i][0],line[i][1]), Point(line[i+1][0],line[i+1][1]))
                    collided_part, collided_side = detect_wire_part_collision(
                        segment, self.parts
                    )

                    # if we see a collision then draw the net around the rectangle
                    # since we are only going left/right with nets/rectangles the strategy to route
                    # around a rectangle is basically making a 'U' shape around it
                    if False and collided_part:  # TODO: Remove False
                        print("collided part/wire")
                        if collided_side == "L":
                            # check if we collided on the left or right side of the central part
                            if pin2.part.origin.x < 0 or pin1.part.origin.x < 0:
                                # if pin2.part.sch_bb[0] < 0 or pin1.part.sch_bb[0] < 0:
                                # switch first and last coordinates if one is further left
                                if x1 > x2:
                                    t = line[0]
                                    line[0] = line[-1]
                                    line[-1] = t

                                # draw line down
                                d_x1 = (
                                    collided_part.sch_bb.ul.x
                                    - 100
                                    # collided_part.sch_bb[0] - collided_part.sch_bb[2] - 100
                                )
                                d_y1 = y1
                                # d_y1 = t_y1
                                d_x2 = d_x1
                                d_y2 = (
                                    collided_part.sch_bb.ul.y
                                    + 200
                                    # collided_part.sch_bb[1] + collided_part.sch_bb[3] + 200
                                )
                                # d_x3 = d_x2 + collided_part.sch_bb[2] + 100 + 100
                                d_y3 = d_y2
                                line.insert(i + 1, [d_x1, d_y1])
                                line.insert(i + 2, [d_x2, d_y2])
                                line.insert(i + 3, [x1, d_y3])
                            else:
                                # switch first and last coordinates if one is further left
                                if x1 < x2:
                                    t = line[0]
                                    line[0] = line[-1]
                                    line[-1] = t
                                # draw line down
                                d_x1 = (
                                    collided_part.sch_bb.ur.x
                                    + 100
                                    # collided_part.sch_bb[0] + collided_part.sch_bb[2] + 100
                                )
                                d_y1 = y1
                                # d_y1 = t_y1
                                d_x2 = d_x1
                                d_y2 = (
                                    collided_part.sch_bb.ul.y
                                    + 200
                                    # collided_part.sch_bb[1] + collided_part.sch_bb[3] + 200
                                )
                                # d_x3 = d_x2 + collided_part.sch_bb[2] + 100 + 100
                                d_y3 = d_y2
                                line.insert(i + 1, [d_x1, d_y1])
                                line.insert(i + 2, [d_x2, d_y2])
                                line.insert(i + 3, [x2, d_y3])
                            break
                        if collided_side == "R":
                            # switch first and last coordinates if one is further left
                            if x1 > x2:
                                t = line[0]
                                line[0] = line[-1]
                                line[-1] = t

                            # draw line down
                            d_x1 = collided_part.sch_bb.ll.x - 100
                            # d_x1 = collided_part.sch_bb[0] - collided_part.sch_bb[2] - 100
                            d_y1 = y1
                            # d_y1 = t_y1
                            d_x2 = d_x1
                            d_y2 = collided_part.sch_bb.ul.y + 100
                            # d_y2 = collided_part.sch_bb[1] + collided_part.sch_bb[3] + 100
                            d_x3 = d_x2 - collided_part.sch_bb.w / 2 + 100 + 100
                            # d_x3 = d_x2 - collided_part.sch_bb[2] + 100 + 100
                            d_y3 = d_y2
                            line.insert(i + 1, [d_x1, d_y1])
                            line.insert(i + 2, [d_x2, d_y2])
                            line.insert(i + 3, [x1, d_y3])
                            break

                nets_output.append(line)
        return nets_output

    def route(self):
        """Route nets between parts of a node."""

        for part in self.parts:
            for part_pin in part:

                # A label means net is stubbed so there won't be any explicit wires.
                if len(part_pin.label) > 0:
                    continue

                # No explicit wires if the pin is not connected to anything.
                if not part_pin.is_connected():
                    continue

                net = part_pin.net

                # No explicit wires for power nets.
                if net.netclass == "Power":
                    continue

                # Determine if all the pins on this net reside in the node.
                internal_net = True
                for net_pin in net.pins:

                    # Don't consider stubs.
                    if len(net_pin.label) > 0:
                        continue

                    # If a pin is outside this node, then ignore the entire net.
                    if net_pin.part.hierarchy != part_pin.part.hierarchy:
                        internal_net = False
                        break

                # Add wires for this net if the pins are all inside the node.
                if internal_net:
                    self.wires.extend(self.wire_it(net))

    def to_eeschema(self, tx):

        # List to hold all the EESCHEMA code for this node.
        eeschema_code = []

        # Find the transformation matrix for the placement of the node.
        tx = self.tx.dot(tx)

        # Generate EESCHEMA code for each part in the node.
        for part in self.parts:
            part_code = part_to_eeschema(part, tx=tx)
            eeschema_code.append(part_code)

        # Generate EESCHEMA wiring code between the parts in the node.
        for w in self.wires:
            wire_code = wire_to_eeschema(w, tx=tx)
            eeschema_code.append(wire_code)

        # Generate power connections for the each part in the node.
        for part in self.parts:
            stub_code = power_part_to_eeschema(part, tx=tx)
            if len(stub_code) != 0:
                eeschema_code.append(stub_code)

        # Generate pin labels for stubbed nets on each part in the node.
        for part in self.parts:
            for pin in part:
                pin_label_code = pin_label_to_eeschema(pin, tx=tx)
                eeschema_code.append(pin_label_code)

        # Generate non-sheet portions of the node.
        for non_sheet in self.non_sheets:
            eeschema_code.append(non_sheet.to_eeschema(tx=tx))

        # Generate hierarchical sheet boxes.
        for sheet in self.sheets:
            eeschema_code.append(sheet.to_eeschema(tx=tx))

        # Generate the graphic box that surrounds the node.
        block_name = self.node_key.split(".")[-1]
        bbox_code = bbox_to_eeschema(self.bbox, tx, block_name)
        eeschema_code.append(bbox_code)

        return "\n".join(eeschema_code)


class NodeTree(defaultdict):
    """Make dict that holds part, net, and bbox info for each node in the hierarchy."""

    def __init__(self, circuit, filepath, title):

        super().__init__(lambda: Node())

        # Save a reference to the original circuit.
        self.circuit = circuit

        # Create a node for each part in the circuit.
        for part in circuit.parts:
            # The node links to the part, and the part links to its node.
            node_key = part.hierarchy
            node = self[node_key]  # Creates the node if it doesn't already exist.
            node.parts.append(part)  # Add part to list of parts in node.
            part.node = node  # Add link from part to the node it's in.

        # Create any intermediary nodes in the hierarchy that might not exist
        # because they don't contain any parts.
        for hierarchy in list(self.keys()):
            breadcrumbs = hierarchy.split(".")
            while breadcrumbs:
                node_key = ".".join(breadcrumbs)
                node = self[node_key]  # Creates a node if it doesn't exist.
                node.node_key = node_key
                # Remove the last portion of the hierarchy string to get the
                # key for the parent node.
                breadcrumbs.pop()

        # Fill-in the parent/child relationship for all the nodes in the hierarchy.
        for node_key, node in self.items():
            parent_key = ".".join(node_key.split(".")[0:-1])
            if parent_key:
                parent = self[parent_key]
                parent.children.append(node)
                node.parent = parent
            else:
                root = node

        # Create list of nodes ordered from leaves (no children) to root (no parent).
        self.leaves2root = []
        available_nodes = list(self.values())
        while available_nodes:
            for node in available_nodes:
                add_node = True
                # Only add a node to the list if all its children are already on the list.
                for child in node.children:
                    if child not in self.leaves2root:
                        add_node = False
                        break
                if add_node:
                    # Add the node to the list and remove it from the list of available nodes.
                    self.leaves2root.append(node)
                    available_nodes.remove(node)

        # Partition circuit into sheets.
        for node in self.leaves2root:
            node.create_sheets(filepath, title)

        self[""].sheets = [Sheet(root, filepath, title)]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def place(self):
        """Place parts within nodes and then place the nodes."""

        # Place parts within each individual node, starting from the leaves and working to the root.
        for node in self.leaves2root:
            node.place()

    def route(self):
        """Route nets within each node of the tree."""
        for node in self.values():
            node.route()

    def to_eeschema(self):
        """Create EESCHEMA schematic files."""
        tx = Tx()
        sheets = [sheet for node in self.values() for sheet in node.sheets]
        for sheet in sheets:
            sheet.to_eeschema(tx)


def bbox_to_eeschema(bbox, tx, name=None):
    """Create a bounding box using EESCHEMA graphic lines."""

    label_pt = round(bbox.ul.dot(tx))

    bbox = round(bbox.dot(tx))

    box = []

    if name:
        box.append(
            "Text Notes {} {} 0    100  ~ 20\n{}".format(label_pt.x, label_pt.y, name)
        )

    box.append("Wire Notes Line")
    box.append("	{} {} {} {}".format(bbox.ll.x, bbox.ll.y, bbox.lr.x, bbox.lr.y))
    box.append("Wire Notes Line")
    box.append("	{} {} {} {}".format(bbox.lr.x, bbox.lr.y, bbox.ur.x, bbox.ur.y))
    box.append("Wire Notes Line")
    box.append("	{} {} {} {}".format(bbox.ur.x, bbox.ur.y, bbox.ul.x, bbox.ul.y))
    box.append("Wire Notes Line")
    box.append("	{} {} {} {}".format(bbox.ul.x, bbox.ul.y, bbox.ll.x, bbox.ll.y))
    box.append("")  # For blank line at end.

    return "\n".join(box)


def part_to_eeschema(part, tx):
    """Create EESCHEMA code for a part.

    Args:
        part (Part): SKiDL part.
        tx (Tx): Transformation matrix.

    Returns:
        string: EESCHEMA code for the part.

    Notes:
        https://en.wikibooks.org/wiki/Kicad/file_formats#Schematic_Files_Format
    """

    time_hex = hex(int(time.time()))[2:]

    tx = part.tx.dot(tx)
    origin = round(tx.origin)

    eeschema = []
    eeschema.append("$Comp")
    eeschema.append("L {}:{} {}".format(part.lib.filename, part.name, part.ref))
    eeschema.append("U 1 1 {}".format(time_hex))
    eeschema.append("P {} {}".format(str(origin.x), str(origin.y)))

    # Add part symbols. For now we are only adding the designator
    n_F0 = 1
    for i in range(len(part.draw)):
        if re.search("^DrawF0", str(part.draw[i])):
            n_F0 = i
            break
    eeschema.append(
        'F 0 "{}" {} {} {} {} {} {} {}'.format(
            part.ref,
            part.draw[n_F0].orientation,
            str(origin.x + part.draw[n_F0].x),
            str(origin.y + part.draw[n_F0].y),
            part.draw[n_F0].size,
            "000",
            part.draw[n_F0].halign,
            part.draw[n_F0].valign,
        )
    )

    n_F2 = 2
    for i in range(len(part.draw)):
        if re.search("^DrawF2", str(part.draw[i])):
            n_F2 = i
            break
    eeschema.append(
        'F 2 "{}" {} {} {} {} {} {} {}'.format(
            part.footprint,
            part.draw[n_F2].orientation,
            str(origin.x + part.draw[n_F2].x),
            str(origin.y + part.draw[n_F2].y),
            part.draw[n_F2].size,
            "001",
            part.draw[n_F2].halign,
            part.draw[n_F2].valign,
        )
    )
    eeschema.append("   1   {} {}".format(str(origin.x), str(origin.y)))
    eeschema.append("   {}  {}  {}  {}".format(tx.a, tx.b, tx.c, tx.d))
    eeschema.append("$EndComp")
    eeschema.append("")  # For blank line at end.

    # For debugging: draws a bounding box around a part.
    # eeschema.append(bbox_to_eeschema(part.bbox, tx))
    # eeschema.append(bbox_to_eeschema(part.bare_bbox, tx))

    return "\n".join(eeschema)


def wire_to_eeschema(wire, tx):
    """Create EESCHEMA code for a multi-segment wire.

    Args:
        wire (list): List of (x,y) points for a wire.
        tx (Point): transformation matrix for each point in the wire.

    Returns:
        string: Text to be placed into EESCHEMA file.
    """

    eeschema = []
    pts = [pt.dot(tx) for pt in wire]
    for pt1, pt2 in zip(pts[:-1], pts[1:]):
        eeschema.append("Wire Wire Line")
        eeschema.append("	{} {} {} {}".format(pt1.x, pt1.y, pt2.x, pt2.y))
    eeschema.append("")  # For blank line at end.
    return "\n".join(eeschema)


def power_part_to_eeschema(part, tx=Tx()):
    return ""  # TODO: Remove this.
    out = []
    for pin in part.pins:
        try:
            if not (pin.net is None):
                if pin.net.netclass == "Power":
                    # strip out the '_...' section from power nets
                    t = pin.net.name
                    u = t.split("_")
                    symbol_name = u[0]
                    # find the stub in the part
                    time_hex = hex(int(time.time()))[2:]
                    pin_pt = round(part.origin + offset + Point(pin.x, pin.y))
                    x, y = pin_pt.x, pin_pt.y
                    out.append("$Comp\n")
                    out.append("L power:{} #PWR?\n".format(symbol_name))
                    out.append("U 1 1 {}\n".format(time_hex))
                    out.append("P {} {}\n".format(str(x), str(y)))
                    # Add part symbols. For now we are only adding the designator
                    n_F0 = 1
                    for i in range(len(part.draw)):
                        if re.search("^DrawF0", str(part.draw[i])):
                            n_F0 = i
                            break
                    part_orientation = part.draw[n_F0].orientation
                    part_horizontal_align = part.draw[n_F0].halign
                    part_vertical_align = part.draw[n_F0].valign

                    # check if the pin orientation will clash with the power part
                    if "+" in symbol_name:
                        # voltage sources face up, so check if the pin is facing down (opposite logic y-axis)
                        if pin.orientation == "U":
                            orientation = [-1, 0, 0, 1]
                    elif "gnd" in symbol_name.lower():
                        # gnd points down so check if the pin is facing up (opposite logic y-axis)
                        if pin.orientation == "D":
                            orientation = [-1, 0, 0, 1]
                    out.append(
                        'F 0 "{}" {} {} {} {} {} {} {}\n'.format(
                            "#PWR?",
                            part_orientation,
                            str(x + 25),
                            str(y + 25),
                            str(40),
                            "001",
                            part_horizontal_align,
                            part_vertical_align,
                        )
                    )
                    out.append(
                        'F 1 "{}" {} {} {} {} {} {} {}\n'.format(
                            symbol_name,
                            part_orientation,
                            str(x + 25),
                            str(y + 25),
                            str(40),
                            "000",
                            part_horizontal_align,
                            part_vertical_align,
                        )
                    )
                    out.append("   1   {} {}\n".format(str(x), str(y)))
                    out.append(
                        "   {}   {}  {}  {}\n".format(
                            orientation[0],
                            orientation[1],
                            orientation[2],
                            orientation[3],
                        )
                    )
                    out.append("$EndComp\n")
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
    return "\n" + "".join(out)


def calc_pin_dir(pin):
    """Calculate pin direction accounting for part transformation matrix."""

    # Copy the part trans. matrix, but remove the translation vector, leaving only scaling/rotation stuff.
    tx = pin.part.tx
    tx = Tx(a=tx.a, b=tx.b, c=tx.c, d=tx.d)

    # Use the pin orientation to compute the pin direction vector.
    pin_vector = {
        "U": Point(0, 1),
        "D": Point(0, -1),
        "L": Point(-1, 0),
        "R": Point(1, 0),
    }[pin.orientation]

    # Rotate the direction vector using the part rotation matrix.
    pin_vector = pin_vector.dot(tx)

    # Create an integer tuple from the rotated direction vector.
    pin_vector = (round(pin_vector.x), round(pin_vector.y))

    # Return the pin orientation based on its rotated direction vector.
    return {
        (0, 1): "U",
        (0, -1): "D",
        (-1, 0): "L",
        (1, 0): "R",
    }[pin_vector]


def pin_label_to_eeschema(pin, tx):
    """Create EESCHEMA text of net label attached to a pin."""

    if len(pin.label) == 0 or not pin.is_connected():
        return ""

    label_type = "HLabel"
    for pn in pin.net.pins:
        if pin.part.hierarchy.startswith(pn.part.hierarchy):
            continue
        if pn.part.hierarchy.startswith(pin.part.hierarchy):
            continue
        label_type = "GLabel"
        break

    part_tx = pin.part.tx.dot(tx)
    pt = pin.pt.dot(part_tx)

    pin_dir = calc_pin_dir(pin)
    orientation = {
        "R": 0,
        "D": 1,
        "L": 2,
        "U": 3,
    }[pin_dir]

    return "Text {} {} {} {}    50   UnSpc ~ 0\n{}\n".format(
        label_type, pt.x, pt.y, orientation, pin.label
    )


def gen_header_eeschema(
    cur_sheet_num, total_sheet_num, title, rev_major, rev_minor, year, month, day, size
):
    """Generate an EESCHEMA header."""

    total_sheet_num = cur_sheet_num + 1
    header = []
    header.append("EESchema Schematic File Version 4")
    header.append("EELAYER 30 0")
    header.append("EELAYER END")
    header.append(
        "$Descr {} {} {}".format(
            size,
            A_sizes[size].max.x,
            A_sizes[size].max.y
        )
    )
    header.append("encoding utf-8")
    header.append("Sheet {} {}".format(cur_sheet_num, total_sheet_num))
    header.append('Title "{}"'.format(title))
    header.append('Date "{}-{}-{}"'.format(year, month, day))
    header.append('Rev "v{}.{}"'.format(rev_major, rev_minor))
    header.append('Comp ""')
    header.append('Comment1 ""')
    header.append('Comment2 ""')
    header.append('Comment3 ""')
    header.append('Comment4 ""')
    header.append("$EndDescr")
    header.append("")  # For blank line at end.

    return "\n".join(header)


def gen_footer_eeschema():
    """Generate an EESCHEMA footer."""

    return "$EndSCHEMATC"


def collect_eeschema_code(
    code,
    cur_sheet_num=1,
    total_sheet_num=1,
    title="Default",
    rev_major=0,
    rev_minor=1,
    year=2021,
    month=8,
    day=15,
    size="A2",
):
    """Collect EESCHEMA header, code, and footer and return as a string."""
    return "\n".join(
        (
            gen_header_eeschema(
                cur_sheet_num=cur_sheet_num,
                total_sheet_num=total_sheet_num,
                title=title,
                rev_major=rev_major,
                rev_minor=rev_minor,
                year=year,
                month=month,
                day=day,
                size=size,
            ),
            code,
            gen_footer_eeschema(),
        )
    )


def gen_schematic(circuit, filepath=None, title="Default", gen_elkjs=False):
    """Create a schematic file from a Circuit object."""

    preprocess_parts_and_nets(circuit)

    with NodeTree(circuit, filepath, title) as node_tree:
        node_tree.place()
        node_tree.route()
        node_tree.to_eeschema()


##################################################################################
# INTRONS.
##################################################################################


def gen_elkjs_code(parts, nets):
    # Generate elkjs code that can create an auto diagram with this website:
    # https://rtsys.informatik.uni-kiel.de/elklive/elkgraph.html

    elkjs_code = []

    # range through parts and append code for each part
    for pt in parts:
        error = 0
        try:
            if pt.stub == True:
                continue
        except Exception as e:
            error += 1
        elkjs_part = []
        elkjs_part.append(
            "node {}".format(pt.ref)
            + " {\n"
            + "\tlayout [ size: {},{} ]\n".format(pt.bbox.w, pt.bbox.h)
            + "\tportConstraints: FIXED_SIDE\n"
            + ""
        )

        for p in pt.pins:
            pin_dir = ""
            if p.orientation == "L":
                pin_dir = "EAST"
            elif p.orientation == "R":
                pin_dir = "WEST"
            elif p.orientation == "U":
                pin_dir = "NORTH"
            elif p.orientation == "D":
                pin_dir = "SOUTH"
            elkjs_part.append(
                "\tport p{} ".format(p.num)
                + "{ \n"
                + "\t\t^port.side: {} \n".format(pin_dir)
                + '\t\tlabel "{}"\n'.format(p.name)
                + "\t}\n"
            )
        elkjs_part.append("}")
        elkjs_code.append("\n" + "".join(elkjs_part))

    # range through nets
    for n in nets:
        for p in range(len(n.pins)):
            try:
                part1 = n.pins[p].ref
                pin1 = n.pins[p].num
                part2 = n.pins[p + 1].ref
                pin2 = n.pins[p + 1].num
                t = "edge {}.p{} -> {}.p{}\n".format(part1, pin1, part2, pin2)
                elkjs_code.append(t)
            except:
                pass

    # open file to save elkjs code
    file_path = "elkjs/elkjs.txt"
    f = open(file_path, "a")
    f.truncate(0)  # Clear the file
    for i in elkjs_code:
        print("" + "".join(i), file=f)
    f.close()
