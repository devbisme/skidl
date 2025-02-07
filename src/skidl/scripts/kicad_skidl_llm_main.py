#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Command-line program for analyzing KiCad/SKiDL circuits using LLMs.
Supports direct SKiDL analysis, KiCad schematic conversion, and netlist processing.
"""

from skidl.scripts.llm_analysis.cli import main

if __name__ == "__main__":
    main()