# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.


from skidl.scriptinfo import get_script_name
from skidl.utilities import export_to_all


__all__ = []

"""
Functions for generating a KiCad EESCHEMA schematic.
"""


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

    from skidl.logger import active_logger

    active_logger.warning(
        "Schematic generation is not implemented for KiCad version 8."
    )
    return
