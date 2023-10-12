# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Command-line program to convert a netlist into an equivalent SKiDL program.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import argparse
import logging
import os
import shutil
import sys
from builtins import open

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from skidl.netlist_to_skidl import netlist_to_skidl
from skidl.pckg_info import __version__



###############################################################################
# Command-line interface.
###############################################################################


def main():
    parser = argparse.ArgumentParser(
        description="A script for converting a KiCad netlist into SKiDL (a textual description of circuit schematics)."
    )
    parser.add_argument(
        "--version", "-v", action="version", version="skidl " + __version__
    )
    parser.add_argument(
        "--input",
        "-i",
        nargs=1,
        type=str,
        metavar="file.net",
        help="Netlist input file.",
    )
    parser.add_argument(
        "--output",
        "-o",
        nargs=1,
        type=str,
        metavar="file.py",
        help="Output file for SKiDL code.",
    )
    parser.add_argument(
        "--overwrite", "-w", action="store_true", help="Overwrite an existing file."
    )
    parser.add_argument(
        "--nobackup",
        "-nb",
        action="store_true",
        help="Do *not* create backups before modifying files. "
        + "(Default is to make backup files.)",
    )
    parser.add_argument(
        "--debug",
        "-d",
        nargs="?",
        type=int,
        default=0,
        metavar="LEVEL",
        help="Print debugging info. (Larger LEVEL means more info.)",
    )

    args = parser.parse_args()

    logger = logging.getLogger("netlist_to_skidl")
    if args.debug is not None:
        log_level = logging.DEBUG + 1 - args.debug
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        logger.addHandler(handler)
        logger.setLevel(log_level)

    if args.input is None:
        logger.critical("Hey! Give me some netlist files!")
        sys.exit(2)

    if args.output is None:
        print("Hey! I need some place where I can store the SKiDL code!")
        sys.exit(1)

    for file in args.output:
        if os.path.isfile(file):
            if not args.overwrite and args.nobackup:
                logger.critical(
                    "File {} already exists! Use the --overwrite option to "
                    + "allow modifications to it or allow backups.".format(file)
                )
                sys.exit(1)
            if not args.nobackup:
                # Create a backup file.
                index = 1  # Start with this backup file suffix.
                while True:
                    backup_file = file + ".{}.bak".format(index, file)
                    if not os.path.isfile(backup_file):
                        # Found an unused backup file name, so make backup.
                        shutil.copy(file, backup_file)
                        break  # Backup done, so break out of loop.
                    index += 1  # Else keep looking for an unused backup file name.

    skidl_code = netlist_to_skidl(args.input[0])
    open(args.output[0], "w").write(skidl_code)


###############################################################################
# Main entrypoint.
###############################################################################
if __name__ == "__main__":
    main()
