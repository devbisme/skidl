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

import skidl
from skidl.part_query import PartSearchDB

try:
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# Available part attributes that can be displayed
AVAILABLE_FIELDS = [
    "part_name",
    "lib_name",
    "lib_file",
    "lib_path",
    "description",
    "aliases",
    "keywords"
]

# Default format template
DEFAULT_FORMAT = "{lib_name}: {part_name} ({description})"


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
            "Search terms (use | for OR, quotes for phrases)."
        ),
    )
    parser.add_argument(
        "--tool",
        help=(
            "ECAD tool name (e.g. kicad_6, kicad_7, kicad_8, kicad_9)."
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
            "Display results as a table (requires rich module). "
            "Incompatible with --format and --fields options."
        ),
    )

    args = parser.parse_args(argv)

    # Check for table mode requirements
    if args.table and not RICH_AVAILABLE:
        print("Error: --table option requires the 'rich' module. "
              "Install with: pip install rich", file=sys.stderr)
        return 1

    if args.table and (args.fields or args.format != DEFAULT_FORMAT):
        print("Error: --table option is incompatible with --format "
              "and --fields", file=sys.stderr)
        return 1

    # Create/load DB for the requested tool and search
    db = PartSearchDB(tool=args.tool)
    db.load_from_lib_search_paths()
    parts = db.search(args.terms, limit=args.limit)

    # Determine output format
    if args.fields:
        # Use field list mode
        field_list = [f.strip() for f in args.fields.split(",")]
        # Validate fields
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
        
        # Add columns
        table.add_column("Part Name", style="cyan", no_wrap=True)
        table.add_column("Library", style="green")
        table.add_column("Description", style="white")
        table.add_column("Aliases", style="yellow")
        table.add_column("Keywords", style="blue")
        
        # Add rows
        for part in sorted(parts, key=lambda p: (p.lib_path, p.part_name)):
            table.add_row(
                part.part_name,
                part.lib_name,
                part.description or "",
                part.aliases or "",
                part.keywords or ""
            )
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fp:
                console = Console(file=fp, width=120)
                console.print(table)
        else:
            console.print(table)
    else:
        # Format as text
        output_lines = []
        for part in sorted(parts, key=lambda p: (p.lib_path, p.part_name)):
            formatted_line = format_part(part, format_string)
            output_lines.append(formatted_line)

        output_text = "\n".join(output_lines)
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fp:
                fp.write(output_text)
                if output_text:  # Only add newline if there's content
                    fp.write("\n")
        else:
            if output_text:
                print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())