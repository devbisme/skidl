# -*- coding: utf-8 -*-

"""Command-line program to convert a JLCEDA Pro ENET file into SKiDL."""

import argparse
from pathlib import Path

from skidl.enet_to_skidl import enet_to_skidl
from skidl.pckg_info import __version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", "-v", action="version", version="skidl " + __version__)
    parser.add_argument("--input", "-i", required=True, type=Path, help="JLCEDA Pro .enet input file.")
    parser.add_argument("--output", "-o", required=True, type=Path, help="Output SKiDL Python file.")
    args = parser.parse_args()

    source = enet_to_skidl(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(source, encoding="utf-8")


if __name__ == "__main__":
    main()

