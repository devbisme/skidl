# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
This script creates SKiDL versions of KiCad part libraries.
"""

import os
import os.path

from skidl import SKIDL, SchLib, lib_search_paths, get_default_tool
from skidl.tools import lib_suffixes

tool = get_default_tool()


def convert_libs(from_dir, to_dir):
    """Convert KiCad libs to SKiDL versions.

    Args:
        from_dir (str): Directory containing the KiCad libraries.
        to_dir (str): Directory where the SKiDL libraries should be stored.
    """

    lib_files = [l for l in os.listdir(from_dir) if l.endswith(lib_suffixes[tool][0])]
    for lib_file in lib_files:
        print(lib_file)
        basename = os.path.splitext(lib_file)[0]
        lib = SchLib(os.path.join(from_dir, lib_file), tool=tool, use_pickle=False)
        lib.export(
            libname=basename,
            file_=os.path.join(to_dir, basename + lib_suffixes[SKIDL]),
            addtl_part_attrs=("search_text",),
        )


if __name__ == "__main__":
    for lib_dir in lib_search_paths[tool]:
        convert_libs(lib_dir, ".")
