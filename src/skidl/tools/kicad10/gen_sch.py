# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Generate KiCad 10 schematic.

The graphical work -- placement, routing, writing the .kicad_sch files -- is
done by the separate ``schematizer`` package. This module is the KiCad 10
interface to it: it builds the generic, tool-neutral netlist from the circuit,
hands it to schematizer with this KiCad version as the target, and translates
schematizer's failures into SKiDL's own exception types.
"""

from skidl.errors import PlacementFailure, RoutingFailure
from skidl.schematic_netlist import build_generic_netlist
from skidl.utilities import export_to_all

# The KiCad version this module targets. schematizer uses it to select the
# output format details for this version.
TOOL_NAME = "kicad10"


@export_to_all
def gen_sch(circuit, **kwargs):
    """
    Generate KiCad 10 schematic files for a circuit.

    Args:
        circuit (Circuit): The circuit to draw. Its nets should already be
            merged, as ``Circuit.generate_schematic()`` does before calling.
        **kwargs: Passed on to schematizer: ``filepath``, ``top_name``,
            ``title``, plus engine options such as ``flatness``, ``retries``
            and ``auto_stub``.

    Returns:
        str: The directory the schematic files were written to.

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
            "Generating a schematic requires the 'schematizer' package. "
            "Install it with:  pip install schematizer"
        ) from e

    netlist = build_generic_netlist(
        circuit,
        title=kwargs.get("title", ""),
        top_name=kwargs.get("top_name", ""),
    )

    try:
        return render(netlist, tool=TOOL_NAME, **kwargs)
    except SchzPlacementFailure as e:
        # Re-raise as SKiDL's own exception types so callers never have to
        # catch (or import) the other package's exceptions.
        raise PlacementFailure(str(e)) from e
    except SchzRoutingFailure as e:
        raise RoutingFailure(str(e)) from e
