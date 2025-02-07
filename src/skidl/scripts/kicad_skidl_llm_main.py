# -*- coding: utf-8 -*-
# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Command-line program for analyzing KiCad/SKiDL circuits using LLMs.
Supports direct SKiDL analysis, KiCad schematic conversion, and netlist processing.
"""

import os
import sys
import platform
import subprocess
import importlib
import logging
from pathlib import Path
from typing import Optional, Set
import argparse
from datetime import datetime
import time
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
import json

from skidl import *
from skidl.pckg_info import __version__

# Constants
DEFAULT_TIMEOUT = 300  # Maximum time to wait for LLM response
DEFAULT_MODEL = "google/gemini-2.0-flash-001"  # Default LLM model

# Configure logging
logger = logging.getLogger("kicad_skidl_llm")

class Backend(Enum):
    """Supported LLM backends."""
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"

@dataclass
class AnalysisState:
    """Tracks the state of circuit analysis across threads."""
    completed: Set[str] = field(default_factory=set)
    failed: dict = field(default_factory=dict)
    results: dict = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)
    total_analysis_time: float = 0.0
    
    def save_state(self, path: Path) -> None:
        """Save current analysis state to disk."""
        with self.lock:
            state_dict = {
                "completed": list(self.completed),
                "failed": self.failed,
                "results": self.results,
                "total_analysis_time": self.total_analysis_time
            }
            with open(path, 'w') as f:
                json.dump(state_dict, f, indent=2)
    
    @classmethod
    def load_state(cls, path: Path) -> 'AnalysisState':
        """Load analysis state from disk."""
        with open(path) as f:
            state_dict = json.load(f)
        state = cls()
        state.completed = set(state_dict["completed"])
        state.failed = state_dict["failed"]
        state.results = state_dict["results"]
        state.total_analysis_time = state_dict.get("total_analysis_time", 0.0)
        return state

    def add_result(self, circuit: str, result: dict) -> None:
        """Thread-safe addition of analysis result."""
        with self.lock:
            self.results[circuit] = result
            self.completed.add(circuit)
            if "request_time_seconds" in result:
                self.total_analysis_time += result["request_time_seconds"]
    
    def add_failure(self, circuit: str, error: str) -> None:
        """Thread-safe recording of analysis failure."""
        with self.lock:
            self.failed[circuit] = error

def validate_kicad_cli(path: str) -> str:
    """Validate KiCad CLI executable and provide platform-specific guidance."""
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
        if system == 'windows':
            raise PermissionError(
                f"KiCad CLI not executable: {path}\n"
                "Ensure the file exists and you have appropriate permissions."
            )
        else:
            raise PermissionError(
                f"KiCad CLI not executable: {path}\n"
                f"Try making it executable with: chmod +x {path}"
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

def handle_kicad_libraries(lib_paths: Optional[list]) -> None:
    """Add and validate KiCad library paths."""
    from skidl import lib_search_paths, KICAD
    valid_paths = []
    invalid_paths = []
    
    # First, clear any existing paths to avoid duplicates
    lib_search_paths[KICAD] = []
    
    # Add system KiCad library path from environment variable
    system_lib_path = os.environ.get('KICAD_SYMBOL_DIR')
    if system_lib_path:
        path = Path(system_lib_path)
        if path.is_dir():
            lib_search_paths[KICAD].append(str(path))
            valid_paths.append(path)
        else:
            logger.warning(f"KICAD_SYMBOL_DIR path does not exist: {path}")
    else:
        logger.warning("KICAD_SYMBOL_DIR environment variable not set")
    
    # Process any additional user-provided paths
    if lib_paths:
        for lib_path in lib_paths:
            path = Path(lib_path)
            if not path.is_dir():
                invalid_paths.append((path, "Directory does not exist"))
                continue
            
            sym_files = list(path.glob("*.kicad_sym"))
            if not sym_files:
                invalid_paths.append((path, "No .kicad_sym files found"))
                continue

            valid_paths.append(path)
            if str(path) not in lib_search_paths[KICAD]:
                lib_search_paths[KICAD].append(str(path))

    if not valid_paths:
        raise RuntimeError(
            "No valid KiCad library paths found. Please ensure KICAD_SYMBOL_DIR "
            "is set correctly and/or provide valid library paths."
        )

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
        return source
    elif args.skidl_dir:
        source = Path(args.skidl_dir)
        if not source.exists():
            raise FileNotFoundError(f"SKiDL directory not found: {source}")
        return source
    elif skidl_dir:
        return skidl_dir
    else:
        raise ValueError("No SKiDL source available for analysis")

def analyze_single_circuit(
    circuit: str,
    api_key: Optional[str],
    backend: Backend,
    model: Optional[str],
    prompt: Optional[str],
    state: AnalysisState
) -> None:
    """Analyze a single circuit and update the shared state."""
    try:
        start_time = time.time()
        
        circuit_desc = default_circuit.get_circuit_info(hierarchy=circuit, depth=1)
        
        result = default_circuit.analyze_with_llm(
            api_key=api_key,
            output_file=None,
            backend=backend.value,
            model=model or DEFAULT_MODEL,
            custom_prompt=prompt,
            analyze_subcircuits=False
        )
        
        result["request_time_seconds"] = time.time() - start_time
        
        state.add_result(circuit, result)
        logger.info(f"✓ Completed analysis of {circuit}")
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        state.add_failure(circuit, error_msg)
        logger.error(f"✗ Failed analysis of {circuit}: {str(e)}")

def analyze_circuits(
    source: Path,
    output_file: Path,
    api_key: Optional[str] = None,
    backend: Backend = Backend.OPENROUTER,
    model: Optional[str] = None,
    prompt: Optional[str] = None,
    skip_circuits: Optional[Set[str]] = None,
    max_concurrent: int = 4,
    state_file: Optional[Path] = None
) -> dict:
    """Analyze SKiDL circuits using parallel LLM analysis."""
    pipeline_start_time = time.time()
    skip_circuits = skip_circuits or set()
    
    state = AnalysisState.load_state(state_file) if state_file and state_file.exists() else AnalysisState()
    
    if skip_circuits:
        logger.info(f"Skipping circuits: {', '.join(sorted(skip_circuits))}")
    
    sys.path.insert(0, str(source.parent if source.is_file() else source))
    try:
        module_name = source.stem if source.is_file() else 'main'
        logger.info(f"Importing {module_name} module...")
        module = importlib.import_module(module_name)
        importlib.reload(module)
        
        if hasattr(module, 'main'):
            logger.info("Executing circuit main()...")
            module.main()
        
        hierarchies = set()
        for part in default_circuit.parts:
            if part.hierarchy != default_circuit.hierarchy:
                if part.hierarchy not in skip_circuits and part.hierarchy not in state.completed:
                    hierarchies.add(part.hierarchy)
        
        if hierarchies:
            logger.info(f"Starting parallel analysis of {len(hierarchies)} circuits...")
            with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                futures = []
                for circuit in sorted(hierarchies):
                    future = executor.submit(
                        analyze_single_circuit,
                        circuit=circuit,
                        api_key=api_key,
                        backend=backend,
                        model=model,
                        prompt=prompt,
                        state=state
                    )
                    futures.append(future)
                    
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Thread failed: {str(e)}")
                    
                    if state_file:
                        state.save_state(state_file)
        
        consolidated_text = ["=== Circuit Analysis Report ===\n"]
        
        if state.completed:
            consolidated_text.append("\n=== Successful Analyses ===")
            for circuit in sorted(state.completed):
                result = state.results[circuit]
                consolidated_text.append(f"\n{'='*20} {circuit} {'='*20}\n")
                consolidated_text.append(result.get("analysis", "No analysis available"))
                token_info = (
                    f"\nTokens used: {result.get('total_tokens', 0)} "
                    f"(Prompt: {result.get('prompt_tokens', 0)}, "
                    f"Completion: {result.get('completion_tokens', 0)})"
                )
                consolidated_text.append(token_info)
        
        if state.failed:
            consolidated_text.append("\n=== Failed Analyses ===")
            for circuit, error in sorted(state.failed.items()):
                consolidated_text.append(f"\n{circuit}: {error}")
        
        # Save consolidated results
        if output_file:
            with open(output_file, "w") as f:
                f.write("\n".join(consolidated_text))
        
        # Calculate total metrics
        total_tokens = sum(
            result.get("total_tokens", 0) 
            for result in state.results.values()
        )
        
        return {
            "success": len(state.completed) > 0 and not state.failed,
            "completed_circuits": sorted(state.completed),
            "failed_circuits": state.failed,
            "results": state.results,
            "total_time_seconds": time.time() - pipeline_start_time,
            "total_analysis_time": state.total_analysis_time,
            "total_tokens": total_tokens
        }
        
    finally:
        sys.path.pop(0)

def main():
    """Main entry point for the KiCad-SKiDL-LLM pipeline."""
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

    args = parser.parse_args()

    # Configure logging based on debug level
    if args.debug is not None:
        log_level = logging.DEBUG + 1 - args.debug
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        handler.setLevel(log_level)
        logger.addHandler(handler)
        logger.setLevel(log_level)

    # Validate argument combinations
    if args.generate_netlist and not args.schematic:
        logger.critical("--generate-netlist requires --schematic")
        sys.exit(2)
    if args.generate_skidl and not (args.netlist or args.generate_netlist):
        logger.critical("--generate-skidl requires --netlist or --generate-netlist")
        sys.exit(2)
    if args.analyze and args.backend == "openrouter" and not args.api_key:
        logger.critical("OpenRouter backend requires --api-key")
        sys.exit(2)

    try:
        start_time = time.time()
        logger.info("Starting KiCad-SKiDL-LLM pipeline")

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
                logger.info(f"Using existing netlist: {netlist_path}")
            else:
                netlist_path = generate_netlist(args, output_dir)

            if args.generate_skidl:
                skidl_dir = generate_skidl_project(args, netlist_path, output_dir)

        # Run circuit analysis if requested
        if args.analyze:
            skidl_source = get_skidl_source(args, netlist_path, skidl_dir)

            # Parse skip circuits if provided
            skip_circuits = set()
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
                    logger.info("\nAnalysis Results:")
                    logger.info(f"  ✓ Completed Circuits: {len(results['completed_circuits'])}")
                    logger.info(f"  ✓ Total Analysis Time: {results['total_analysis_time']:.2f} seconds")
                    logger.info(f"  ✓ Total Pipeline Time: {results['total_time_seconds']:.2f} seconds")
                    if results.get("total_tokens"):
                        logger.info(f"  ✓ Total Tokens Used: {results['total_tokens']}")

                    if results["failed_circuits"]:
                        logger.warning("\nFailed Circuits:")
                        for circuit, error in results["failed_circuits"].items():
                            logger.warning(f"  ✗ {circuit}: {error}")

                    logger.info(f"\nAnalysis results saved to: {args.analysis_output}")
                else:
                    raise RuntimeError(f"Analysis failed: {results.get('error', 'Unknown error')}")

            except Exception as e:
                logger.error("✗ Circuit analysis failed!")
                logger.error(f"Error: {str(e)}")
                if args.backend == "openrouter":
                    logger.error("\nTroubleshooting tips:")
                    logger.error("1. Check your API key")
                    logger.error("2. Verify you have sufficient API credits")
                    logger.error("3. Check for rate limiting")
                else:
                    logger.error("\nTroubleshooting tips:")
                    logger.error("1. Verify Ollama is running locally")
                    logger.error("2. Check if the requested model is installed")
                sys.exit(1)

        total_time = time.time() - start_time
        logger.info(f"\nPipeline completed in {total_time:.2f} seconds")

    except Exception as e:
        logger.critical(f"Pipeline failed: {str(e)}")
        logger.debug("Stack trace:", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()