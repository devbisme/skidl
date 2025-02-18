"""
Circuit analysis using Large Language Models for KiCad/SKiDL designs.

This package provides tools for analyzing circuit designs using LLMs,
with support for:
- Direct SKiDL analysis
- KiCad schematic conversion
- Netlist processing
- Parallel circuit analysis
"""

from .config import DEFAULT_TIMEOUT, DEFAULT_MODEL, Backend
from .state import AnalysisState
from .analyzer import analyze_circuits
from .generator import (
    generate_netlist,
    generate_skidl_project,
    get_skidl_source
)
from .kicad import (
    validate_kicad_cli,
    get_default_kicad_cli,
    handle_kicad_libraries
)

__version__ = "1.0.0"

__all__ = [
    "DEFAULT_TIMEOUT",
    "DEFAULT_MODEL",
    "Backend",
    "AnalysisState",
    "analyze_circuits",
    "generate_netlist",
    "generate_skidl_project",
    "get_skidl_source",
    "validate_kicad_cli",
    "get_default_kicad_cli",
    "handle_kicad_libraries",
]