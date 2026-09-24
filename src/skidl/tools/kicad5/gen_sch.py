# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
KiCad 5 schematic generation -- not supported.

KiCad 5 needs the legacy EESCHEMA ``.sch`` format rather than the s-expression
``.kicad_sch`` that the ``schematizer`` package writes, and KiCad 5 libraries
describe symbols in a different (non-s-expression) form that the generic
netlist has no slot for. So this backend rejects the request up front with an
explanation instead of emitting a file KiCad 5 can't open.

Every other KiCad 5 output -- netlist, PCB, XML, SVG -- is unaffected.
"""

from skidl.utilities import export_to_all


@export_to_all
def gen_sch(circuit, **kwargs):
    """
    Refuse to generate a KiCad 5 schematic.

    Args:
        circuit (Circuit): Ignored.
        **kwargs: Ignored.

    Raises:
        ValueError: Always. KiCad 5 schematics aren't generated.
    """

    raise ValueError(
        "Schematic generation isn't supported for KiCad 5: it uses the legacy "
        "EESCHEMA '.sch' format, which SKiDL no longer writes. Use KiCad 6 or "
        "later (e.g. tool=KICAD9). KiCad 5 netlists, PCBs, XML and SVG are "
        "unaffected."
    )
