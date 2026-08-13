# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
KiCad 5 SVG generation -- not supported.

SVG drawings are rendered by the ``schematizer`` package from the generic
netlist's embedded symbol graphics. Those are s-expressions, which KiCad 5
libraries do not provide: a KiCad 5 part carries ``draw`` objects from
``draw_objs.py`` instead, a representation the generic netlist has no slot
for. This is the same gap that stops KiCad 5 schematic generation -- see
``gen_sch.py``.

KiCad 5 netlists, PCBs and XML BOMs are unaffected.
"""

from skidl.utilities import export_to_all


@export_to_all
def gen_svg(circuit, **kwargs):
    """
    Refuse to generate a KiCad 5 SVG drawing.

    Args:
        circuit (Circuit): Ignored.
        **kwargs: Ignored.

    Raises:
        ValueError: Always. KiCad 5 SVG drawings aren't generated.
    """

    raise ValueError(
        "SVG generation isn't supported for KiCad 5: its symbol libraries "
        "don't provide the s-expression graphics the renderer draws from. "
        "Use KiCad 6 or later (e.g. tool=KICAD9). KiCad 5 netlists, PCBs and "
        "XML BOMs are unaffected."
    )
