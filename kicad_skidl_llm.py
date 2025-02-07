#!/usr/bin/env python3
"""
KiCad-SKiDL-LLM Pipeline
------------------------

A tool for analyzing KiCad circuit designs using SKiDL and LLMs. 
Supports direct SKiDL analysis, KiCad schematic conversion, and netlist processing.

Features:
    - KiCad schematic (.kicad_sch) to netlist conversion
    - Netlist to SKiDL project generation
    - Circuit analysis using OpenRouter or Ollama LLM backends
    - Support for subcircuit analysis with selective circuit skipping
    - Detailed logging and timing information

Example Usage:
    # Analyze KiCad schematic
    python kicad_skidl_llm.py --schematic design.kicad_sch --generate-netlist --generate-skidl --analyze --api-key YOUR_KEY
    
    # Analyze existing SKiDL project using Ollama
    python kicad_skidl_llm.py --skidl-dir project/ --analyze --backend ollama
    
    # Skip specific circuits during analysis
    python kicad_skidl_llm.py --skidl circuit.py --analyze --skip-circuits "voltage_regulator1,adc_interface2"
"""

import os
import sys
import platform
import subprocess
import importlib
import textwrap
import traceback
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple, Set
import argparse
import logging
from datetime import datetime
import time
from enum import Enum

from skidl import *

# Global configuration
DEFAULT_TIMEOUT = 300
DEFAULT_MODEL = "google/gemini-2.0-flash-001"
DEFAULT_OUTPUT_DIR = Path.cwd() / "output"

class Backend(Enum):
    """Supported LLM backends."""
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"

# Configure logging
logger = logging.getLogger('kicad_skidl_llm')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', 
                            datefmt='%Y-%m-%d %H:%M:%S')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Disable propagation of SKiDL loggers to prevent duplicate messages
skidl_loggers = ['skidl.logger', 'skidl.active_logger', 'skidl.erc_logger']
for name in skidl_loggers:
    l = logging.getLogger(name)
    l.propagate = False

class CircuitDiscoveryError(Exception):
    """Raised when there are issues discovering or loading circuits."""
    pass


def _analyze_subcircuits(
    hierarchies: Set[str],
    output_file: Optional[Path],
    api_key: Optional[str],
    backend: Backend,
    model: Optional[str],
    prompt: Optional[str],
    start_time: float
) -> Dict[str, Union[bool, float, int, Dict]]:
    """
    Analyze subcircuits using LLM and generate consolidated results.
    
    Args:
        hierarchies: Set of circuit hierarchies to analyze
        output_file: Output file for analysis results
        api_key: API key for LLM service
        backend: LLM backend to use
        model: Model name for selected backend
        prompt: Custom analysis prompt
        start_time: Start time of analysis for timing calculations
        
    Returns:
        Dictionary containing analysis results and metadata
    """
    if not hierarchies:
        logger.warning("No valid circuits found for analysis after applying skip filters")
        return {
            "success": True,
            "subcircuits": {},
            "total_time_seconds": time.time() - start_time,
            "total_tokens": 0
        }
    
    results = {
        "success": True,
        "subcircuits": {},
        "total_time_seconds": 0,
        "total_tokens": 0
    }
    
    consolidated_text = ["=== Subcircuits Analysis ===\n"]
    for hier in sorted(hierarchies):
        logger.info(f"\nAnalyzing subcircuit: {hier}")
        
        # Get description focused on this subcircuit
        circuit_desc = default_circuit.get_circuit_info(hierarchy=hier, depth=1)
        
        # Analyze just this subcircuit
        sub_results = default_circuit.analyze_with_llm(
            api_key=api_key,
            output_file=None,  # Don't write individual files
            backend=backend.value,
            model=model or DEFAULT_MODEL,
            custom_prompt=prompt,
            analyze_subcircuits=False  # Only analyze this specific subcircuit
        )
        
        results["subcircuits"][hier] = sub_results
        results["total_time_seconds"] += sub_results.get("request_time_seconds", 0)
        results["total_tokens"] += (
            sub_results.get("prompt_tokens", 0) + 
            sub_results.get("completion_tokens", 0)
        )
        
        # Build consolidated output text
        consolidated_text.append(f"\n{'='*20} {hier} {'='*20}\n")
        if sub_results.get("success", False):
            analysis_text = sub_results.get("analysis", "No analysis available")
            consolidated_text.append(analysis_text)
            
            token_info = (
                f"\nTokens used: {sub_results.get('total_tokens', 0)} "
                f"(Prompt: {sub_results.get('prompt_tokens', 0)}, "
                f"Completion: {sub_results.get('completion_tokens', 0)})"
            )
            consolidated_text.append(token_info)
        else:
            consolidated_text.append(
                f"Analysis failed: {sub_results.get('error', 'Unknown error')}"
            )
        consolidated_text.append("\n")
    
    # Save consolidated results
    if output_file:
        with open(output_file, "w") as f:
            f.write("\n".join(consolidated_text))
    
    return results

def analyze_circuits(
    source: Path,
    output_file: Path,
    api_key: Optional[str] = None,
    backend: Backend = Backend.OPENROUTER,
    model: Optional[str] = None,
    prompt: Optional[str] = None,
    skip_circuits: Optional[Set[str]] = None,
    dump_temp: bool = False
) -> Dict[str, Union[bool, float, int, Dict]]:
    """
    Analyze SKiDL circuits using the specified LLM backend.
    
    Args:
        source: Path to SKiDL file or directory
        output_file: Output file for analysis results
        api_key: API key for LLM service
        backend: LLM backend to use
        model: Model name for selected backend
        prompt: Custom analysis prompt
        skip_circuits: Set of circuit hierarchies to skip
        dump_temp: Flag to dump temporary files
        
    Returns:
        Dictionary containing analysis results and metadata
    """
    start_time = time.time()
    skip_circuits = skip_circuits or set()

    if skip_circuits:
        logger.info(f"Skipping circuits: {', '.join(sorted(skip_circuits))}")
    
    sys.path.insert(0, str(source.parent if source.is_file() else source))
    try:
        # Import phase
        t0 = time.time()
        module_name = source.stem if source.is_file() else 'main'
        logger.info(f"Importing {module_name} module...")
        module = importlib.import_module(module_name)
        importlib.reload(module)
        logger.info(f"Import completed in {time.time() - t0:.2f} seconds")
        
        # Circuit instantiation phase
        if hasattr(module, 'main'):
            t0 = time.time()
            logger.info("Executing circuit main()...")
            try:
                module.main()
            except FileNotFoundError as e:
                if "Can't open file:" in str(e):
                    missing_lib = str(e).split(':')[-1].strip()
                    msg = (
                        f"KiCad symbol library not found: {missing_lib}\n"
                        "Use --kicad-lib-paths to specify library directories"
                    )
                    raise CircuitDiscoveryError(msg) from e
                raise
            logger.info(f"Circuit instantiation completed in {time.time() - t0:.2f} seconds")
        
        # LLM Analysis phase
        t0 = time.time()
        logger.info("Starting LLM analysis...")
        
        # Get hierarchies and filter out skipped ones
        hierarchies = set()
        for part in default_circuit.parts:
            if part.hierarchy != default_circuit.hierarchy:  # Skip top level
                if part.hierarchy not in skip_circuits:
                    hierarchies.add(part.hierarchy)
        
        results = _analyze_subcircuits(
            hierarchies=hierarchies,
            output_file=output_file,
            api_key=api_key,
            backend=backend,
            model=model,
            prompt=prompt,
            start_time=start_time
        )
        
        logger.info(f"LLM analysis completed in {time.time() - t0:.2f} seconds")
        total_time = time.time() - start_time
        logger.info(f"Total processing time: {total_time:.2f} seconds")
        
        return results
        
    finally:
        sys.path.pop(0)
             
def validate_kicad_cli(path: str) -> str:
    """
    Validate KiCad CLI executable and provide platform-specific guidance.
    
    Args:
        path: Path to kicad-cli executable
        
    Returns:
        Validated path
        
    Raises:
        FileNotFoundError: If executable not found
        PermissionError: If executable lacks permissions
    """
    system = platform.system().lower()
    cli_path = Path(path)
    
    if not cli_path.exists():
        suggestions = {
            'darwin': [
                "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
                "~/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
            ],
            'windows': [
                r"C:\Program Files\KiCad\7.0\bin\kicad-cli.exe",
                r"C:\Program Files (x86)\KiCad\7.0\bin\kicad-cli.exe"
            ],
            'linux': [
                "/usr/bin/kicad-cli",
                "/usr/local/bin/kicad-cli"
            ]
        }
        
        error_msg = [f"KiCad CLI not found: {path}"]
        if system in suggestions:
            error_msg.append("\nCommon paths for your platform:")
            for suggestion in suggestions[system]:
                error_msg.append(f"  - {suggestion}")
        error_msg.append("\nSpecify the correct path using --kicad-cli")
        raise FileNotFoundError('\n'.join(error_msg))
        
    if not os.access(str(cli_path), os.X_OK):
        if platform.system().lower() == 'windows':
            raise PermissionError(
                f"KiCad CLI not executable: {path}\n"
                "Ensure the file exists and you have appropriate permissions."
            )
        else:
            raise PermissionError(
                f"KiCad CLI not executable: {path}\n"
                "Try making it executable with: chmod +x {path}"
            )
            
    return str(cli_path)

def get_default_kicad_cli() -> str:
    """Get the default KiCad CLI path based on the current platform."""
    system = platform.system().lower()
    if system == 'darwin':  # macOS
        return "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
    elif system == 'windows':
        return r"C:\Program Files\KiCad\7.0\bin\kicad-cli.exe"
    else:  # Linux and others
        return "/usr/bin/kicad-cli"

def parse_args() -> argparse.Namespace:
    """Parse and validate command line arguments."""
    parser = argparse.ArgumentParser(
        description='KiCad to SKiDL conversion and circuit analysis pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              # Generate netlist and SKiDL project from schematic
              %(prog)s --schematic design.kicad_sch --generate-netlist --generate-skidl --analyze --api-key YOUR_KEY
              
              # Analyze existing SKiDL project with circuit skipping
              %(prog)s --skidl-dir project/ --analyze --skip-circuits "circuit1,circuit2" --api-key YOUR_KEY
            """)
    )
    
    # Input source group (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--schematic', '-s', help='Path to KiCad schematic (.kicad_sch) file')
    source_group.add_argument('--netlist', '-n', help='Path to netlist (.net) file')
    source_group.add_argument('--skidl', help='Path to SKiDL Python file to analyze')
    source_group.add_argument('--skidl-dir', help='Path to SKiDL project directory')
    
    # Operation mode flags
    parser.add_argument('--generate-netlist', action='store_true', help='Generate netlist from schematic')
    parser.add_argument('--generate-skidl', action='store_true', help='Generate SKiDL project from netlist')
    parser.add_argument('--analyze', action='store_true', help='Run LLM analysis on circuits')
    
    # Optional configuration
    parser.add_argument('--kicad-cli', default=get_default_kicad_cli(), 
                       help='Path to kicad-cli executable')
    parser.add_argument('--output-dir', '-o', default='.', help='Output directory for generated files')
    parser.add_argument('--api-key', help='OpenRouter API key for cloud LLM analysis')
    parser.add_argument('--backend', choices=['openrouter', 'ollama'], default='openrouter',
                       help='LLM backend to use')
    parser.add_argument('--model', help='LLM model name for selected backend')
    parser.add_argument('--analysis-output', default='circuit_analysis.txt',
                       help='Output file for analysis results')
    parser.add_argument('--analysis-prompt', help='Custom prompt for circuit analysis')
    parser.add_argument('--skip-circuits', help='Comma-separated list of circuits to skip during analysis')
    parser.add_argument('--kicad-lib-paths', nargs='*', 
                       help='List of custom KiCad library paths')
    
    args = parser.parse_args()
    
    # Validate argument combinations
    if args.generate_netlist and not args.schematic:
        parser.error("--generate-netlist requires --schematic")
    if args.generate_skidl and not (args.netlist or args.generate_netlist):
        parser.error("--generate-skidl requires --netlist or --generate-netlist")
    if args.analyze and args.backend == 'openrouter' and not args.api_key:
        parser.error("OpenRouter backend requires --api-key")
        
    return args

def setup_environment(args) -> Path:
    """Setup output directory and return its path."""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def handle_kicad_libraries(lib_paths: Optional[List[str]]) -> None:
    """Add and validate KiCad library paths."""
    if not lib_paths:
        return
        
    from skidl import lib_search_paths, KICAD
    valid_paths = []
    invalid_paths = []
    
    for lib_path in lib_paths:
        path = Path(lib_path)
        if not path.is_dir():
            invalid_paths.append((path, "Directory does not exist"))
            continue
        
        sym_files = list(path.glob("*.kicad_sym"))
        if not sym_files:
            invalid_paths.append((path, "No .kicad_sym symbol files found"))
            continue

        valid_paths.append(path)
        lib_search_paths[KICAD].append(str(path))

    if valid_paths:
        logger.info("Added KiCad library paths:")
        for path in valid_paths:
            logger.info(f"  ✓ {path}")
            sym_files = list(path.glob("*.kicad_sym"))
            for sym in sym_files[:3]:
                logger.info(f"    - {sym.name}")
            if len(sym_files) > 3:
                logger.info(f"    - ... and {len(sym_files)-3} more")

    if invalid_paths:
        logger.warning("Invalid library paths:")
        for path, reason in invalid_paths:
            logger.warning(f"  ✗ {path}: {reason}")

def generate_netlist(args, output_dir: Path) -> Optional[Path]:
    """Generate netlist from schematic if requested."""
    if not (args.schematic and args.generate_netlist):
        return None
        
    logger.info("Step 1: Generating netlist from schematic...")
    schematic_path = Path(args.schematic)
    if not schematic_path.exists():
        raise FileNotFoundError(f"Schematic not found: {schematic_path}")
        
    kicad_cli = validate_kicad_cli(args.kicad_cli)
    netlist_path = output_dir / f"{schematic_path.stem}.net"
    
    try:
        subprocess.run([
            kicad_cli, 'sch', 'export', 'netlist',
            '-o', str(netlist_path), str(schematic_path)
        ], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Netlist generation failed:\n{e.stderr}") from e
    
    logger.info(f"✓ Generated netlist: {netlist_path}")
    return netlist_path

def generate_skidl_project(args, current_netlist: Optional[Path], output_dir: Path) -> Optional[Path]:
    """Generate SKiDL project from netlist if requested."""
    if not args.generate_skidl or not current_netlist:
        return None
        
    logger.info("Step 2: Generating SKiDL project from netlist...")
    skidl_dir = output_dir / f"{current_netlist.stem}_SKIDL"
    skidl_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        subprocess.run([
            'netlist_to_skidl',
            '-i', str(current_netlist),
            '--output', str(skidl_dir)
        ], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"SKiDL project generation failed:\n{e.stderr}") from e
    
    logger.info(f"✓ Generated SKiDL project: {skidl_dir}")
    return skidl_dir

def get_skidl_source(args, netlist_path: Optional[Path], skidl_dir: Optional[Path]) -> Path:
    """Determine the SKiDL source to analyze."""
    if args.skidl:
        source = Path(args.skidl)
        if not source.exists():
            raise FileNotFoundError(f"SKiDL file not found: {source}")
        logger.info(f"Using SKiDL file: {source}")
        return source
    elif args.skidl_dir:
        source = Path(args.skidl_dir)
        if not source.exists():
            raise FileNotFoundError(f"SKiDL directory not found: {source}")
        logger.info(f"Using SKiDL project directory: {source}")
        return source
    elif skidl_dir:
        return skidl_dir
    else:
        raise ValueError("No SKiDL source available for analysis")

def main() -> None:
    """
    Main execution function implementing the KiCad-SKiDL-LLM pipeline.
    
    The pipeline supports:
    1. KiCad schematic to netlist conversion
    2. Netlist to SKiDL project generation
    3. Circuit analysis using LLM
    """
    start_time = time.time()
    try:
        logger.info("Starting KiCad-SKiDL-LLM pipeline")
        args = parse_args()
        
        # Setup environment
        output_dir = setup_environment(args)
        
        # Add KiCad library paths if provided
        if args.kicad_lib_paths:
            handle_kicad_libraries(args.kicad_lib_paths)
        
        # Process input source and generate required files
        netlist_path = None
        skidl_dir = None
        
        if args.schematic or args.netlist:
            # Handle netlist
            if args.netlist:
                netlist_path = Path(args.netlist)
                if not netlist_path.exists():
                    raise FileNotFoundError(f"Netlist not found: {netlist_path}")
                logger.info(f"Using existing netlist: {netlist_path}")
            else:
                netlist_path = generate_netlist(args, output_dir)
            
            # Generate SKiDL project if requested
            if args.generate_skidl:
                skidl_dir = generate_skidl_project(args, netlist_path, output_dir)
        
        # Run circuit analysis if requested
        if args.analyze:
            skidl_source = get_skidl_source(args, netlist_path, skidl_dir)
            
            # Parse skip circuits if provided
            skip_circuits = set()
            if args.skip_circuits:
                skip_circuits = {c.strip() for c in args.skip_circuits.split(',')}
            
            try:
                results = analyze_circuits(
                    source=skidl_source,
                    output_file=args.analysis_output,
                    api_key=args.api_key,
                    backend=Backend(args.backend),
                    model=args.model,
                    prompt=args.analysis_prompt,
                    skip_circuits=skip_circuits
                )
                
                if results["success"]:
                    logger.info("Analysis Results:")
                    if "subcircuits" in results:
                        for hier, analysis in results["subcircuits"].items():
                            logger.info(f"\nSubcircuit: {hier}")
                            if analysis["success"]:
                                logger.info(f"✓ Analysis completed in {analysis['request_time_seconds']:.2f} seconds")
                                tokens = analysis.get('prompt_tokens', 0) + analysis.get('completion_tokens', 0)
                                if tokens:
                                    logger.info(f"  Tokens used: {tokens}")
                            else:
                                logger.error(f"✗ Analysis failed: {analysis['error']}")
                        
                        logger.info(f"\nTotal analysis time: {results['total_time_seconds']:.2f} seconds")
                        if results.get('total_tokens'):
                            logger.info(f"Total tokens used: {results['total_tokens']}")
                    else:
                        logger.info(f"✓ Analysis completed in {results['request_time_seconds']:.2f} seconds")
                        tokens = results.get('prompt_tokens', 0) + results.get('completion_tokens', 0)
                        if tokens:
                            logger.info(f"Tokens used: {tokens}")
                            
                    logger.info(f"Analysis results saved to: {args.analysis_output}")
                else:
                    raise RuntimeError(f"Analysis failed: {results.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error("✗ Circuit analysis failed!")
                logger.error(f"Error: {str(e)}")
                if args.backend == 'openrouter':
                    logger.error("Troubleshooting tips:")
                    logger.error("1. Check your API key")
                    logger.error("2. Verify you have sufficient API credits")
                    logger.error("3. Check for rate limiting")
                else:
                    logger.error("Troubleshooting tips:")
                    logger.error("1. Verify Ollama is running locally")
                    logger.error("2. Check if the requested model is installed")
                raise
        
        total_time = time.time() - start_time
        logger.info(f"Pipeline completed in {total_time:.2f} seconds")
                
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        logger.debug("Stack trace:", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()