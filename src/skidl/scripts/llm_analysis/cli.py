"""Command-line interface for KiCad/SKiDL circuit analysis."""

import sys
import time
import argparse
from pathlib import Path
from typing import Set

from skidl.pckg_info import __version__

from .config import Backend
from .logging import configure_logging, log_analysis_results, log_backend_help
from .kicad import get_default_kicad_cli, handle_kicad_libraries
from .generator import generate_netlist, generate_skidl_project, get_skidl_source
from .analyzer import analyze_circuits

def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="A tool for analyzing KiCad/SKiDL circuits using LLMs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="skidl " + __version__
    )
    
    # Input source group (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--schematic", "-s",
        help="Path to KiCad schematic (.kicad_sch) file"
    )
    source_group.add_argument(
        "--netlist", "-n",
        help="Path to netlist (.net) file"
    )
    source_group.add_argument(
        "--skidl",
        help="Path to SKiDL Python file to analyze"
    )
    source_group.add_argument(
        "--skidl-dir",
        help="Path to SKiDL project directory"
    )
    
    # Operation mode flags
    parser.add_argument(
        "--generate-netlist",
        action="store_true",
        help="Generate netlist from schematic"
    )
    parser.add_argument(
        "--generate-skidl",
        action="store_true",
        help="Generate SKiDL project from netlist"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Run LLM analysis on circuits"
    )
    
    # Optional configuration
    parser.add_argument(
        "--kicad-cli",
        default=get_default_kicad_cli(),
        help="Path to kicad-cli executable"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=".",
        help="Output directory for generated files"
    )
    parser.add_argument(
        "--api-key",
        help="OpenRouter API key for cloud LLM analysis"
    )
    parser.add_argument(
        "--backend",
        choices=["openrouter", "ollama"],
        default="openrouter",
        help="LLM backend to use"
    )
    parser.add_argument(
        "--model",
        help="LLM model name for selected backend"
    )
    parser.add_argument(
        "--analysis-output",
        default="circuit_analysis.txt",
        help="Output file for analysis results"
    )
    parser.add_argument(
        "--analysis-prompt",
        help="Custom prompt for circuit analysis"
    )
    parser.add_argument(
        "--skip-circuits",
        help="Comma-separated list of circuits to skip during analysis"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=4,
        help="Maximum number of concurrent LLM analyses (default: 4)"
    )
    parser.add_argument(
        "--kicad-lib-paths",
        nargs="*",
        help="List of custom KiCad library paths"
    )
    parser.add_argument(
        "--debug", "-d",
        nargs="?",
        type=int,
        default=0,
        metavar="LEVEL",
        help="Print debugging info. (Larger LEVEL means more info.)"
    )
    
    return parser.parse_args()

def validate_args(args: argparse.Namespace) -> None:
    """Validate command line argument combinations.
    
    Args:
        args: Parsed command line arguments
        
    Raises:
        SystemExit: If invalid argument combinations are detected
    """
    if args.generate_netlist and not args.schematic:
        sys.exit("--generate-netlist requires --schematic")
    if args.generate_skidl and not (args.netlist or args.generate_netlist):
        sys.exit("--generate-skidl requires --netlist or --generate-netlist")
    if args.analyze and args.backend == "openrouter" and not args.api_key:
        sys.exit("OpenRouter backend requires --api-key")

def main() -> None:
    """Main entry point for the KiCad-SKiDL-LLM pipeline."""
    args = parse_args()
    configure_logging(args.debug)
    
    try:
        start_time = time.time()
        print("Starting KiCad-SKiDL-LLM pipeline")

        # Validate arguments
        validate_args(args)
        
        # Setup environment
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Add KiCad library paths if provided
        if args.kicad_lib_paths:
            handle_kicad_libraries(args.kicad_lib_paths)

        # Process input source and generate required files
        netlist_path = None
        skidl_dir = None

        if args.schematic or args.netlist:
            if args.netlist:
                netlist_path = Path(args.netlist)
                if not netlist_path.exists():
                    raise FileNotFoundError(f"Netlist not found: {netlist_path}")
                print(f"Using existing netlist: {netlist_path}")
            else:
                netlist_path = generate_netlist(
                    Path(args.schematic),
                    output_dir,
                    args.kicad_cli
                )

            if args.generate_skidl:
                skidl_dir = generate_skidl_project(netlist_path, output_dir)

        # Run circuit analysis if requested
        if args.analyze:
            skidl_source = get_skidl_source(
                skidl_file=Path(args.skidl) if args.skidl else None,
                skidl_dir=Path(args.skidl_dir) if args.skidl_dir else None,
                generated_dir=skidl_dir
            )

            # Parse skip circuits if provided
            skip_circuits: Set[str] = set()
            if args.skip_circuits:
                skip_circuits = {c.strip() for c in args.skip_circuits.split(",")}

            try:
                results = analyze_circuits(
                    source=skidl_source,
                    output_file=Path(args.analysis_output),
                    api_key=args.api_key,
                    backend=Backend(args.backend),
                    model=args.model,
                    prompt=args.analysis_prompt,
                    skip_circuits=skip_circuits,
                    max_concurrent=args.max_concurrent
                )

                if results["success"]:
                    log_analysis_results(results)
                    print(f"\nAnalysis results saved to: {args.analysis_output}")
                else:
                    raise RuntimeError(f"Analysis failed: {results.get('error', 'Unknown error')}")

            except Exception as e:
                print("✗ Circuit analysis failed!")
                print(f"Error: {str(e)}")
                log_backend_help(args.backend)
                sys.exit(1)

        total_time = time.time() - start_time
        print(f"\nPipeline completed in {total_time:.2f} seconds")

    except Exception as e:
        print(f"Pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()