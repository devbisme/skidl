# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Functions for generating a KiCad PCB.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from skidl.scriptinfo import get_script_name
from skidl.utilities import export_to_all
from skidl.logger import active_logger



@export_to_all
def gen_pcb(circuit, pcb_file, fp_libs=None):
    """Create a KiCad PCB file directly from a Circuit object.

    Args:
        circuit (Circuit): Circuit object.
        pcb_file: Either a file object that can be written to, or a string
            containing a file name, or None.
        fp_libs: List of directories containing footprint libraries.
    Returns:
        None.
    """

    # Keep the import in here so it doesn't get triggered unless this is used
    # so it eases some problems with tox testing.
    # It requires pcbnew module which may not be present or may be for the
    # wrong Python version (2 vs. 3).
    try:
        import kinet2pcb  # For creating KiCad PCB directly from Circuit object.
    except ImportError:
        active_logger.warning(
            "kinet2pcb module is missing. Can't generate a KiCad PCB without it."
        )
    else:
        pcb_file = pcb_file or (get_script_name() + ".kicad_pcb")
        kinet2pcb.kinet2pcb(circuit, pcb_file, fp_libs)
