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
import readline

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


def perform_search_and_display(db, search_terms, args, field_list, format_string):
    """
    Perform search and display results based on current arguments.
    
    Args:
        db: PartSearchDB instance
        search_terms: Search query string
        args: Parsed command line arguments
        field_list: List of fields to display
        format_string: Format string for output
        
    Returns:
        int: Number of results found
    """
    parts = db.search(search_terms, limit=args.limit)
    sorted_parts = sorted(parts, key=lambda p: (p.lib_path, p.part_name))

    # Use ANSI color code for bright yellow bold text.
    found_info_text = f"\033[93m\033[1mFound {len(sorted_parts)} part(s) for: {search_terms}\033[0m"
    print(found_info_text)
    
    if not sorted_parts:
        return 0
    
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
    
    print(found_info_text)
    
    return len(sorted_parts)


def interactive_browse(db, parts, args, field_list, format_string):
    """
    Browse through search results with arrow keys and display part details.
    
    Args:
        db: PartSearchDB instance
        parts: List of PartResult objects from search
        args: Parsed command line arguments
        field_list: List of fields to display
        format_string: Format string for output
    """
    import termios
    import tty
    
    if not parts:
        print("No parts to browse. Perform a search first.")
        return
    
    current_index = 0
    total_parts = len(parts)
    
    print(f"Browse mode: {total_parts} parts found.")
    print("Use UP/DOWN arrow keys to navigate, ENTER to show details, 's' for search mode, 'q' to quit.")
    print()
    
    def show_current_part():
        part = parts[current_index]
        # Clear the line and show current part
        print(f"\r\033[K[{current_index + 1}/{total_parts}] {format_part(part, format_string)}", end='', flush=True)
    
    def show_part_details():
        from skidl.part_query import show_part
        part = parts[current_index]
        print(f"\n\nShowing details for: {part.part_name} from {part.lib_name}")
        print("-" * 60)
        
        # Try to show the part using show_part function
        try:
            template_part = show_part(part.lib_path, part.part_name, tool=args.tool)
            if template_part:
                print(f"Part: {template_part.name}")
                print(f"Library: {part.lib_name}")
                print(f"Description: {part.description or 'N/A'}")
                print(f"Aliases: {part.aliases or 'N/A'}")
                print(f"Keywords: {part.keywords or 'N/A'}")
                print("\nPins:")
                if hasattr(template_part, 'pins') and template_part.pins:
                    for pin in template_part.pins:
                        print(f"  {pin}")
                else:
                    print("  No pins found or part not fully parsed.")
            else:
                print("Could not load part details.")
        except Exception as e:
            print(f"Error loading part: {e}")
        
        print("-" * 60)
        print("Press any key to continue browsing...")
        
        # Wait for any key press to continue
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
        print()  # New line after key press
        show_current_part()  # Redisplay current part
    
    def get_key():
        """Get a single key press from stdin."""
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            
            # Handle escape sequences (arrow keys)
            if key == '\x1b':  # ESC sequence
                key += sys.stdin.read(2)
                
            return key
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    # Show initial part
    show_current_part()
    
    while True:
        try:
            key = get_key()
            
            if key == 'q' or key == '\x03':  # 'q' or Ctrl+C
                print("\n")
                break
            elif key == 's':
                print("\nReturning to search mode...")
                return 'search'
            elif key == '\r' or key == '\n':  # Enter key
                show_part_details()
            elif key == '\x1b[A':  # Up arrow
                if current_index > 0:
                    current_index -= 1
                    show_current_part()
            elif key == '\x1b[B':  # Down arrow  
                if current_index < total_parts - 1:
                    current_index += 1
                    show_current_part()
            elif key == 'h' or key == '?':
                print("\n\nCommands:")
                print("  UP/DOWN arrows - Navigate parts")
                print("  ENTER - Show part details")
                print("  s - Return to search mode")
                print("  h/? - Show this help")
                print("  q - Exit")
                print("\nPress any key to continue...")
                get_key()
                print()
                show_current_part()
                
        except (EOFError, KeyboardInterrupt):
            print("\n")
            break
    
    return None


def interactive_search(db, args, field_list, format_string):
    """
    Run interactive search mode with command history support.
    
    Args:
        db: PartSearchDB instance
        args: Parsed command line arguments
        field_list: List of fields to display
        format_string: Format string for output
    """
    print("Interactive search mode. Use up/down arrows for history.")
    print("Type 'quit', 'exit', or 'q' to exit, 'browse' to enter browse mode.")
    print()
    
    # Configure readline for history
    readline.parse_and_bind('"\\e[A": previous-history')
    readline.parse_and_bind('"\\e[B": next-history')
    
    current_parts = []  # Store current search results for browse mode
    
    while True:
        try:
            search_terms = input("Search terms: ").strip()
            
            # Check for exit commands
            if search_terms.lower() in ['quit', 'exit', 'q']:
                break
            
            # Check for browse mode command
            if search_terms.lower() in ['browse', 'b']:
                if current_parts:
                    result = interactive_browse(db, current_parts, args, field_list, format_string)
                    if result == 'search':
                        continue  # Return to search mode
                    else:
                        break  # Exit if browse mode was quit
                else:
                    print("No search results to browse. Perform a search first.")
                continue
            
            # Check for help command
            if search_terms.lower() in ['help', 'h']:
                print("Commands:")
                print("  <search terms> - Search for parts")
                print("  browse/b - Enter browse mode (if results available)")
                print("  help/h - Show this help")
                print("  quit/q - Exit")
                continue
            
            # Skip empty input
            if not search_terms:
                continue
            
            # Add to history (readline automatically handles this)
            readline.add_history(search_terms)
            
            # Perform search and display results
            parts = db.search(search_terms, limit=args.limit)
            current_parts = sorted(parts, key=lambda p: (p.lib_path, p.part_name))
            
            perform_search_and_display(db, search_terms, args, field_list, format_string)
            
            if current_parts:
                print("Type 'browse' to navigate through results.")
            print()  # Add blank line between searches
            
        except (EOFError, KeyboardInterrupt):
            break


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

Interactive mode:
  Use --interactive to enter interactive search mode after initial search.
  Commands: 'quit', 'exit', 'q' to exit. Up/down arrows for search history.
        """.strip()
    )
    parser.add_argument(
        "terms",
        nargs='?',
        help=(
            "Search terms (Separate terms by space for AND, | for OR. Use quotes for phrases). "
            "Optional in interactive mode."
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
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help=(
            "Enter interactive mode after initial search (if terms provided). "
            "Allows multiple searches with command history support and browse mode."
        ),
    )

    args = parser.parse_args(argv)

    # Check for table mode requirements
    if args.table and not RICH_AVAILABLE:
        print("Error: --table option requires the 'rich' module. "
              "Install with: pip install rich", file=sys.stderr)
        return 1

    # Check if we have search terms or interactive mode
    if not args.terms and not args.interactive:
        parser.error("Search terms are required unless using --interactive mode")

    # Create/load DB for the requested tool
    db = PartSearchDB(tool=args.tool)
    db.load_from_lib_search_paths()

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

    # Perform initial search if terms provided
    if args.terms:
        parts = db.search(args.terms, limit=args.limit)
        sorted_parts = sorted(parts, key=lambda p: (p.lib_path, p.part_name))
        perform_search_and_display(db, args.terms, args, field_list, format_string)
        
        # Add initial search to history for interactive mode
        if args.interactive:
            readline.add_history(args.terms)
            print()

    # Enter interactive mode if requested
    if args.interactive:
        interactive_search(db, args, field_list, format_string)

    return 0


if __name__ == "__main__":
    sys.exit(main())