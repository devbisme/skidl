#!/usr/bin/env python3
"""
Command-line interface to search SKiDL part libraries.

This script uses the PartSearchDB to load libraries from paths configured
in the user's .skidlcfg (via skidl.lib_search_paths) and search for
parts matching the given query terms. All output is plain text with
customizable formatting and field selection.
"""

import argparse
import sys

from tomlkit import table

import skidl
from skidl.part_query import PartSearchDB

try:
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# Available part attributes that can be displayed and description labels.
AVAILABLE_FIELDS = {
    "part_name": "Part Name",
    "lib_name": "Library",
    "lib_file": "Library File",
    "lib_path": "Library Path",
    "description": "Description",
    "aliases": "Aliases",
    "keywords": "Keywords",
}

# Default format template
DEFAULT_FORMAT = "{lib_name}: {part_name} ({description})"
DEFAULT_FIELDS = "lib_name,part_name,description"


def format_part(part, format_string):
    """
    Format a single part using the provided format string.
    
    Args:
        part: PartResult namedtuple with part information
        format_string: Python format string with field placeholders
        
    Returns:
        str: Formatted part information
    """
    # Create a dict of all available fields for formatting
    fields = {
        "part_name": part.part_name,
        "lib_name": part.lib_name,
        "lib_file": part.lib_file,
        "lib_path": part.lib_path,
        "description": part.description or "",
        "aliases": part.aliases or "",
        "keywords": part.keywords or "",
    }
    
    try:
        return format_string.format(**fields)
    except KeyError as e:
        return f"ERROR: Unknown field {e} in format string"


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description=(
            "Search SKiDL part libraries (paths come from .skidlcfg)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Format string examples:
  Default: {DEFAULT_FORMAT}
  Simple:  "{{part_name}}"
  Detailed: "{{lib_name}}/{{part_name}} - {{description}}"
  Custom:   "Part: {{part_name}} | Library: {{lib_name}} | {{aliases}}"

Available fields: {', '.join(AVAILABLE_FIELDS)}
        """.strip()
    )
    parser.add_argument(
        "terms",
        help=(
            "Search terms (Separate terms by space for AND, | for OR. Use quotes for phrases)."
        ),
    )
    parser.add_argument(
        "--tool",
        help=(
            "ECAD tool name (e.g. kicad6, kicad7, kicad8, kicad9)."
        ),
        default=skidl.get_default_tool(),
    )
    parser.add_argument(
        "--format",
        default=DEFAULT_FORMAT,
        help=(
            f"Output format string (default: '{DEFAULT_FORMAT}'). "
            f"Available fields: {', '.join(AVAILABLE_FIELDS)}"
        ),
    )
    parser.add_argument(
        "--fields",
        default=DEFAULT_FIELDS,
        help=(
            "Comma-separated list of fields to display in order. "
            f"Available: {', '.join(AVAILABLE_FIELDS)}. "
            "Overrides --format if specified."
        ),
    )
    parser.add_argument(
        "--separator",
        default=" | ",
        help=(
            "Field separator when using --fields (default: ' | ')"
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of results",
    )
    parser.add_argument(
        "--output",
        "-o",
        help=(
            "Write results to file (defaults to stdout)"
        ),
        default=None,
    )
    parser.add_argument(
        "--table",
        action="store_true",
        help=(
            "Display results as a table (requires rich module)."
        ),
    )

    args = parser.parse_args(argv)

    # Check for table mode requirements
    if args.table and not RICH_AVAILABLE:
        print("Error: --table option requires the 'rich' module. "
              "Install with: pip install rich", file=sys.stderr)
        return 1

    # Create/load DB for the requested tool and search
    db = PartSearchDB(tool=args.tool)
    db.load_from_lib_search_paths()
    parts = db.search(args.terms, limit=args.limit)

    # Sort the parts for output.
    sorted_parts = sorted(parts, key=lambda p: (p.lib_path, p.part_name))

    # Determine field list if using --fields
    field_list = [f.strip() for f in args.fields.split(",")]

    # Determine output format
    if args.fields:
        # Use field list mode
        invalid_fields = [f for f in field_list if f not in AVAILABLE_FIELDS]
        if invalid_fields:
            print(f"Error: Invalid fields: {', '.join(invalid_fields)}",
                  file=sys.stderr)
            print(f"Available fields: {', '.join(AVAILABLE_FIELDS)}",
                  file=sys.stderr)
            return 1
        
        # Create format string from field list
        format_placeholders = ["{" + field + "}" for field in field_list]
        format_string = args.separator.join(format_placeholders)
    else:
        # Use custom format string
        format_string = args.format

    # Format and output results
    if args.table:
        # Display as table using rich
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        
        # Column headers
        col_hdrs = [[AVAILABLE_FIELDS[fld], color] for fld, color in zip(field_list, ["cyan", "green", "white", "yellow", "blue", "red", "magenta"])]
        # Add columns
        no_wrap = True
        for col_hdr in col_hdrs:
            table.add_column(col_hdr[0], style=col_hdr[1], no_wrap=no_wrap)
            no_wrap = False  # Only the first column is no_wrap
        
        # Add rows
        for part in sorted_parts:
            row_data = [getattr(part, field, "") for field in field_list]
            table.add_row(*row_data)
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fp:
                console = Console(file=fp, width=120)
                console.print(table)
        else:
            console = Console()
            console.print(table)

    else:
        # Format as text
        output_lines = [format_part(part, format_string) for part in sorted_parts]
        output_text = "\n".join(output_lines)
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fp:
                print(output_text, file=fp)
        else:
            if output_text:
                print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())