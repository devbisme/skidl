# -*- coding: utf-8 -*-
# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Command-line program to convert a netlist into an equivalent SKiDL program.
"""

import argparse
import logging
import os
import shutil
import sys
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
        metavar="directory",
        help="Output directory for SKiDL code.",
    )
    parser.add_argument(
        "--overwrite", "-w", action="store_true", help="Overwrite existing files and directories."
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
        print("Hey! I need an output directory where I can store the SKiDL code!")
        sys.exit(1)

    output_dir = args.output[0]

    # Check if directory exists and handle accordingly
    if os.path.exists(output_dir):
        if not os.path.isdir(output_dir):
            logger.critical(f"{output_dir} exists and is not a directory!")
            sys.exit(1)
        if not args.overwrite and args.nobackup:
            logger.critical(
                f"Directory {output_dir} already exists! Use the --overwrite option to "
                + "allow modifications to it or allow backups."
            )
            sys.exit(1)
        if not args.nobackup:
            # Create a backup directory
            index = 1
            while True:
                backup_dir = f"{output_dir}.{index}.bak"
                if not os.path.exists(backup_dir):
                    # Found an unused backup directory name, so make backup
                    if os.path.exists(output_dir):
                        shutil.copytree(output_dir, backup_dir)
                    break
                index += 1
            
            if args.overwrite:
                shutil.rmtree(output_dir)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate SKiDL code in the output directory
    netlist_to_skidl(args.input[0], output_dir=output_dir)


###############################################################################
# Main entrypoint.
###############################################################################

if __name__ == "__main__":
    main()