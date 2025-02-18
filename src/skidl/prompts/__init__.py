"""Circuit analysis prompt templates.

This package provides templates for generating circuit analysis prompts.
The prompts are organized into:
1. Base prompt structure and methodology
2. Individual analysis section templates
"""

from .base import get_base_prompt
from .sections import ANALYSIS_SECTIONS

__version__ = "1.0.0"

__all__ = ["get_base_prompt", "ANALYSIS_SECTIONS"]
