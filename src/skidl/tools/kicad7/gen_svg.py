# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Generate a static SVG drawing of a KiCad 7 schematic.

Like ``gen_sch``, the work is done by the separate ``schematizer`` package:
this module builds the generic, tool-neutral netlist and asks schematizer to
render it as SVG instead of ``.kicad_sch``. Both formats come off the same
placement and routing pass, so the drawing matches the editable schematic.
"""

from skidl.errors import PlacementFailure, RoutingFailure
from skidl.schematic_netlist import build_generic_netlist
from skidl.utilities import export_to_all

# The KiCad version whose symbol graphics the drawing is based on.
TOOL_NAME = "kicad7"


@export_to_all
def gen_svg(circuit, **kwargs):
    """
    Generate SVG schematic pages for a circuit.

    Args:
        circuit (Circuit): The circuit to draw. Its nets should already be
            merged, as ``Circuit.generate_svg()`` does before calling.
        **kwargs: Passed on to schematizer: ``filepath``, ``top_name``,
            ``title``, and ``flatness`` (0.0 for a page per subcircuit,
            1.0 for a single page).

    Returns:
        str: The directory the SVG files were written to.

    Raises:
        ImportError: The ``schematizer`` package isn't installed.
        PlacementFailure: The parts of the schematic couldn't be placed.
        RoutingFailure: The nets of the schematic couldn't be routed.
    """

    try:
        from schematizer import (
            render,
            PlacementFailure as SchzPlacementFailure,
            RoutingFailure as SchzRoutingFailure,
        )
    except ImportError as e:
        raise ImportError(
            "Generating an SVG schematic requires the 'schematizer' package. "
            "Install it with:  pip install schematizer"
        ) from e

    # A drawing should come out readable rather than not at all: auto_stub
    # converts nets the router can't handle into labels (and falls back to a
    # labels-only page if routing still fails) instead of raising. Callers who
    # want every net drawn as a wire can pass auto_stub=False.
    kwargs.setdefault("auto_stub", True)

    netlist = build_generic_netlist(
        circuit,
        title=kwargs.get("title", ""),
        top_name=kwargs.get("top_name", ""),
    )

    try:
        return render(netlist, tool=TOOL_NAME, format="svg", **kwargs)
    except SchzPlacementFailure as e:
        # Re-raise as SKiDL's own exception types so callers never have to
        # catch (or import) the other package's exceptions.
        raise PlacementFailure(str(e)) from e
    except SchzRoutingFailure as e:
        raise RoutingFailure(str(e)) from e
