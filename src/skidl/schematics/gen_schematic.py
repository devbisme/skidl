# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.


from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import re
from builtins import range
from collections import Counter

from future import standard_library

from ..scriptinfo import get_script_name
from ..utilities import export_to_all, rmv_attr
from .geometry import BBox, Point, Tx, Vector
from .place import PlacementFailure
from .route import RoutingFailure
from .node import Node
from .net_terminal import NetTerminal

standard_library.install_aliases()

"""
Generate a KiCad EESCHEMA schematic from a Circuit object.
"""

# TODO: Handle symio attribute.


def preprocess_circuit(circuit, **options):
    """Add stuff to parts & nets for doing placement and routing of schematics."""

    def units(part):
        if len(part.unit) == 0:
            return [part]
        else:
            return part.unit.values()

    def initialize(part):
        """Initialize part or its part units."""

        # Initialize the units of the part, or the part itself if it has no units.
        pin_limit = options.get("orientation_pin_limit", 44)
        for part_unit in units(part):
            # Initialize transform matrix.
            part_unit.tx = Tx.from_symtx(getattr(part_unit, "symtx", ""))

            # Lock part orientation if symtx was specified. Also lock parts with a lot of pins
            # since they're typically drawn the way they're supposed to be oriented.
            # And also lock single-pin parts because these are usually power/ground and
            # they shouldn't be flipped around.
            num_pins = len(part_unit.pins)
            part_unit.orientation_locked = getattr(part_unit, "symtx", False) or not (
                1 < num_pins <= pin_limit
            )

            # Assign pins from the parent part to the part unit.
            part_unit.grab_pins()

            # Initialize pin attributes used for generating schematics.
            for pin in part_unit:
                pin.pt = Point(pin.x, pin.y)
                pin.routed = False

    def rotate_power_pins(part):
        """Rotate a part based on the direction of its power pins.

        This function is to make sure that voltage sources face up and gnd pins
        face down.
        """

        # Don't rotate parts that are already explicitly rotated/flipped.
        if not getattr(part, "symtx", ""):
            return

        def is_pwr(net):
            return net_name.startswith("+")

        def is_gnd(net):
            return "gnd" in net_name.lower()

        dont_rotate_pin_cnt = options.get("dont_rotate_pin_count", 10000)

        for part_unit in units(part):
            # Don't rotate parts with too many pins.
            if len(part_unit) > dont_rotate_pin_cnt:
                return

            # Tally what rotation would make each pwr/gnd pin point up or down.
            rotation_tally = Counter()
            for pin in part_unit:
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

            # Rotate the part unit in the direction with the most tallies.
            try:
                rotation = rotation_tally.most_common()[0][0]
            except IndexError:
                pass
            else:
                # Rotate part unit 90-degrees clockwise until the desired rotation is reached.
                tx_cw_90 = Tx(a=0, b=-1, c=1, d=0)  # 90-degree trans. matrix.
                for _ in range(int(round(rotation / 90))):
                    part_unit.tx = part_unit.tx * tx_cw_90

    def calc_part_bbox(part):
        """Calculate the labeled bounding boxes and store it in the part."""

        from ..tools.kicad.kicad import calc_hier_label_bbox, calc_symbol_bbox

        # Find part/unit bounding boxes excluding any net labels on pins.
        # TODO: part.lbl_bbox could be substituted for part.bbox.
        # TODO: Part ref and value should be updated before calculating bounding box.
        bare_bboxes = calc_symbol_bbox(part)[1:]

        for part_unit, bare_bbox in zip(units(part), bare_bboxes):
            # Expand the bounding box if it's too small in either dimension.
            resize_wh = Vector(0, 0)
            if bare_bbox.w < 100:
                resize_wh.x = (100 - bare_bbox.w) / 2
            if bare_bbox.h < 100:
                resize_wh.y = (100 - bare_bbox.h) / 2
            bare_bbox = bare_bbox.resize(resize_wh)

            # Find expanded bounding box that includes any hier labels attached to pins.
            part_unit.lbl_bbox = BBox()
            part_unit.lbl_bbox.add(bare_bbox)
            for pin in part_unit:
                if pin.stub:
                    # Find bounding box for net stub label attached to pin.
                    hlbl_bbox = calc_hier_label_bbox(pin.net.name, pin.orientation)
                    # Move the label bbox to the pin location.
                    hlbl_bbox *= Tx().move(pin.pt)
                    # Update the bbox for the labelled part with this pin label.
                    part_unit.lbl_bbox.add(hlbl_bbox)

            # Set the active bounding box to the labeled version.
            part_unit.bbox = part_unit.lbl_bbox

    # Pre-process parts
    for part in circuit.parts:
        # Initialize part attributes used for generating schematics.
        initialize(part)

        # Rotate parts.  Power pins should face up. GND pins should face down.
        rotate_power_pins(part)

        # Compute bounding boxes around parts
        calc_part_bbox(part)


def finalize_parts_and_nets(circuit, **options):
    """Restore parts and nets after place & route is done."""

    # Remove any NetTerminals that were added.
    net_terminals = (p for p in circuit.parts if isinstance(p, NetTerminal))
    circuit.rmv_parts(*net_terminals)

    # Return pins from the part units to their parent part.
    for part in circuit.parts:
        part.grab_pins()

    # Remove some stuff added to parts during schematic generation process.
    rmv_attr(circuit.parts, ("force", "bbox", "lbl_bbox", "tx"))


@export_to_all
def gen_schematic(
    circuit,
    filepath=".",
    top_name=get_script_name(),
    title="SKiDL-Generated Schematic",
    flatness=0.0,
    retries=2,
    **options
):
    """Create a schematic file from a Circuit object.

    Args:
        circuit (Circuit): The Circuit object that will have a schematic generated for it.
        filepath (str, optional): The directory where the schematic files are placed. Defaults to ".".
        top_name (str, optional): The name for the top of the circuit hierarchy. Defaults to get_script_name().
        title (str, optional): The title of the schematic. Defaults to "SKiDL-Generated Schematic".
        flatness (float, optional): Determines how much the hierarchy is flattened in the schematic. Defaults to 0.0 (completely hierarchical).
        retries (int, optional): Number of times to re-try if routing fails. Defaults to 2.
        options (dict, optional): Dict of options and values, usually for drawing/debugging.
    """

    # Part placement options that should always be turned on.
    options["use_push_pull"] = True
    options["rotate_parts"] = True
    options["pt_to_pt_mult"] = 5  # HACK: Ad-hoc value.
    options["pin_normalize"] = True

    # Start with default routing area.
    expansion_factor = 1.0

    # Try to place & route one or more times.
    for _ in range(retries):
        preprocess_circuit(circuit, **options)

        node = Node(circuit, filepath, top_name, title, flatness)

        try:
            # Place parts.
            node.place(expansion_factor=expansion_factor, **options)

            # Route parts.
            node.route(**options)

        except PlacementFailure:
            # Placement failed, so clean up ...
            finalize_parts_and_nets(circuit, **options)
            # ... and try again.
            continue

        except RoutingFailure:
            # Routing failed, so clean up ...
            finalize_parts_and_nets(circuit, **options)
            # ... and expand routing area ...
            expansion_factor *= 1.5  # HACK: Ad-hoc increase of expansion factor.
            # ... and try again.
            continue

        # Generate EESCHEMA code for the schematic.
        node.to_eeschema()

        # Append place & route statistics for the schematic to a file.
        if options.get("collect_stats"):
            stats = node.collect_stats(**options)
            with open(options["stats_file"], "a") as f:
                f.write(stats)

        # Clean up.
        finalize_parts_and_nets(circuit, **options)

        # Place & route was successful if we got here, so exit.
        return

    # Append failed place & route statistics for the schematic to a file.
    if options.get("collect_stats"):
        stats = "-1\n"
        with open(options["stats_file"], "a") as f:
            f.write(stats)

    # Clean-up after failure.
    finalize_parts_and_nets(circuit, **options)

    # Exited the loop without successful routing.
    raise (RoutingFailure)
