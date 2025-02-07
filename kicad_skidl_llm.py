#!/usr/bin/env python3
"""
KiCad-SKiDL-LLM Pipeline
------------------------

This script provides a flexible pipeline for working with KiCad schematics,
netlists, SKiDL projects, and LLM-based circuit analysis. It supports multiple
entry points and operation modes:

Entry Points:
    - KiCad schematic (.kicad_sch)
    - Netlist (.net)
    - SKiDL project (single file or directory)

Operations:
    - Generate netlist from KiCad schematic
    - Convert netlist to SKiDL project
    - Analyze circuits using LLM (local or cloud-based)

Key Features:
    - Safe discovery and analysis of SKiDL circuits using AST parsing
    - Support for both single-file and multi-file SKiDL projects
    - Flexible LLM backend selection:
         * OpenRouter (cloud-based): Note that model names must be set according 
           to the OpenRouter naming standard.
         * Ollama (local): If using this backend, ensure Ollama is installed locally.
    - Comprehensive error handling and reporting

Additional Notes for Novice Users:
    - Make sure you have KiCad 7.0+ installed. You must also point the script to the 
      correct location of your KiCad CLI executable (using --kicad-cli) if it is not in the default path.
    - For LLM analysis using OpenRouter, you must provide a valid API key with --api-key.
    - Ensure that any LLM model name provided (via --model) adheres to the naming conventions 
      required by the selected backend.

Usage Examples:
    # Generate netlist and SKiDL project from schematic
    python kicad_skidl_llm.py --schematic design.kicad_sch --generate-netlist --generate-skidl
    
    # Analyze existing SKiDL project using OpenRouter
    python kicad_skidl_llm.py --skidl-source myproject/ --analyze --api-key YOUR_KEY
    
    # Generate SKiDL from netlist and analyze using Ollama
    python kicad_skidl_llm.py --netlist circuit.net --generate-skidl --analyze --backend ollama

    # Dump temporary analysis file for inspection
    python kicad_skidl_llm.py --skidl-source myproject/ --analyze --api-key YOUR_KEY --dump-temp

Known Limitations:
    1. Memory usage may be high for projects with many subcircuits.
    2. Python path handling may need adjustment for complex project structures.
    3. Circular dependencies in SKiDL projects may cause issues.
    4. File encoding issues possible with non-UTF8 files.
    5. Large projects may hit API rate limits with cloud LLMs.

Dependencies:
    - Python 3.7+
    - KiCad 7.0+ (for schematic operations)
    - SKiDL
    - AST (standard library)
    - Either OpenRouter API key (for cloud-based LLM analysis) or a local Ollama installation

Author: [Your Name]
Date: February 2024
License: MIT
"""

import os
import sys
import ast
import inspect
import platform
import subprocess
import importlib
import textwrap
import traceback
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse
import logging
from skidl import *

# Set up basic logging configuration.
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

# Custom exception to signal issues during circuit discovery and loading.
class CircuitDiscoveryError(Exception):
    """Raised when there are issues discovering or loading circuits."""
    pass

class CircuitAnalyzer:
    """
    Handles discovery and analysis of SKiDL circuits.
    
    This class provides methods for:
    - Finding @subcircuit decorated functions in Python files
    - Safely loading and executing discovered circuits
    - Running LLM analysis on circuits

    Note for LLM Analysis:
      The default LLM analysis uses OpenRouter. This means that any LLM model name
      provided must follow OpenRouter's naming standards. Alternatively, you can choose
      the 'ollama' backend for local analysis if you have Ollama installed.
      
    The analyzer uses AST parsing to discover circuits without executing
    potentially unsafe code, then creates isolated environments for
    circuit execution and analysis.
    """
    
    @staticmethod
    def find_subcircuits(directory: Path) -> List[Dict[str, str]]:
        """
        Recursively find all functions decorated with @subcircuit in Python files.
        
        Uses AST parsing to safely discover circuits without executing code.
        Skips files that can't be parsed and logs warnings.
        
        Args:
            directory: Root directory to search for Python files
            
        Returns:
            List of dicts containing:
                - 'file': Path to Python file
                - 'function': Name of decorated function
                - 'lineno': Line number where the function is defined
                
        Raises:
            CircuitDiscoveryError: If no valid Python files found
        """
        subcircuits = []
        
        class SubcircuitFinder(ast.NodeVisitor):
            """AST visitor that identifies @subcircuit decorated functions."""
            def visit_FunctionDef(self, node):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'subcircuit':
                        subcircuits.append({
                            'file': str(current_file),
                            'function': node.name,
                            'lineno': node.lineno
                        })
        
        python_files = list(directory.rglob('*.py'))
        if not python_files:
            raise CircuitDiscoveryError(f"No Python files found in {directory}")
        
        for current_file in python_files:
            try:
                with open(current_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    SubcircuitFinder().visit(tree)
            except Exception as e:
                logging.warning(f"Could not parse {current_file}: {e}")
                
        return subcircuits

    @staticmethod
    def create_analysis_module(
        subcircuits: List[Dict[str, str]], 
        output_dir: Path
    ) -> Tuple[Path, str]:
        """
        Create a temporary Python module that imports and executes discovered subcircuits.
        The generated module creates dummy SKiDL nets for any parameters required by the 
        subcircuit functions, allowing them to be called without errors.
        
        This version groups the discovered functions by file and generates explicit
        import statements (rather than wildcard imports) so that functions whose names
        start with an underscore (e.g. _3v3_regulator) are imported correctly.
        
        Args:
            subcircuits: List of subcircuit information from find_subcircuits()
            output_dir: Directory to write temporary module
            
        Returns:
            Tuple of:
                - Path to created module
                - Generated code string (for debugging)
                
        Raises:
            CircuitDiscoveryError: If module creation fails
        """
        analysis_file = output_dir / 'circuit_analysis.py'
        try:
            # Generate import statements and helper function.
            code_lines = [
                "from skidl import *\n",
                "from skidl.tools import *\n",
                "import inspect\n\n",
                "# Helper function that creates dummy nets for required parameters.\n",
                "def call_subcircuit(func):\n",
                "    # If the function is wrapped, get the original.\n",
                "    wrapped = getattr(func, '__wrapped__', func)\n",
                "    sig = inspect.signature(wrapped)\n",
                "    # Create a dummy net for each parameter\n",
                "    dummy_args = [Net(param.name) for param in sig.parameters.values()]\n",
                "    return func(*dummy_args)\n\n"
            ]
            
            # Group discovered functions by file.
            imports_by_file = {}
            for s in subcircuits:
                file = s['file']
                func_name = s['function']
                if file not in imports_by_file:
                    imports_by_file[file] = set()
                imports_by_file[file].add(func_name)
            
            # Generate explicit import lines for each file.
            for file, functions in imports_by_file.items():
                module_name = Path(file).stem
                funcs_str = ", ".join(sorted(functions))
                code_lines.append(f"from {module_name} import {funcs_str}\n")
            
            # Create main function to execute each subcircuit via call_subcircuit.
            code_lines.append("\n\ndef main():\n")
            for s in subcircuits:
                func_name = s['function']
                code_lines.append(f"    call_subcircuit({func_name})\n")
            
            code = ''.join(code_lines)
            
            with open(analysis_file, 'w', encoding='utf-8') as f:
                f.write(code)
                
            return analysis_file, code
            
        except Exception as e:
            raise CircuitDiscoveryError(
                f"Failed to create analysis module: {str(e)}"
            ) from e


    @staticmethod
    def analyze_circuits(
        source: Path,
        output_file: str,
        api_key: Optional[str] = None,
        backend: str = 'openrouter',
        model: Optional[str] = None,
        prompt: Optional[str] = None,
        dump_temp: bool = False
    ) -> dict:
        """
        Analyze circuits from either a SKiDL source file/project or KiCad conversion.
        
        Args:
            source: Path to SKiDL file/project or KiCad conversion directory
            output_file: Where to save analysis results
            api_key: API key for cloud LLM service (required for openrouter)
            backend: 'openrouter' or 'ollama'
            model: Model name for selected backend
            prompt: Custom analysis prompt
            dump_temp: If True, do not delete temporary analysis files
                
        Returns:
            Analysis results dictionary
        """
        if source.is_file():
            # Direct SKiDL file case - import and analyze the circuit
            logging.info(f"Analyzing SKiDL file: {source}")
            
            sys.path.insert(0, str(source.parent))
            try:
                # Import the SKiDL module which will populate default_circuit
                module = importlib.import_module(source.stem)
                importlib.reload(module)  # Reload in case it was previously imported
                
                # If there's a main() function, call it to instantiate the circuit
                if hasattr(module, 'main'):
                    module.main()
                    
                # Get the populated default_circuit and analyze it
                return default_circuit.analyze_with_llm(
                    api_key=api_key,
                    output_file=output_file,
                    backend=backend,
                    model=model,
                    prompt=prompt,
                    analyze_subcircuits=True
                )
                
            except Exception as e:
                raise CircuitDiscoveryError(
                    f"Failed to analyze SKiDL file {source}: {str(e)}"
                ) from e
            finally:
                sys.path.pop(0)
                    
        else:
            # Directory case - handle KiCad conversion output
            logging.info(f"Analyzing KiCad conversion directory: {source}")
            
            try:
                # Find subcircuits in the converted SKiDL project
                subcircuits = CircuitAnalyzer.find_subcircuits(source)
                if not subcircuits:
                    raise CircuitDiscoveryError(
                        f"No @subcircuit functions found in {source}"
                    )

                logging.info(f"Found {len(subcircuits)} circuits to analyze:")
                for circuit in subcircuits:
                    logging.info(
                        f"  - {circuit['function']} ({circuit['file']}:{circuit['lineno']})"
                    )

                # For KiCad conversions, we still need to create an analysis module
                # since we're working with generated SKiDL code
                analysis_module, generated_code = CircuitAnalyzer.create_analysis_module(
                    subcircuits, source
                )

                # Execute the generated module
                sys.path.insert(0, str(source))
                try:
                    module = importlib.import_module('circuit_analysis')
                    importlib.reload(module)
                    try:
                        module.main()
                    except FileNotFoundError as e:
                        # Check if this is a KiCad library error
                        if "Can't open file:" in str(e):
                            missing_lib = str(e).split(':')[-1].strip()
                            msg = (
                                f"KiCad symbol library not found: {missing_lib}\n\n"
                                "Use --kicad-lib-paths to specify library directories:\n"
                                "  --kicad-lib-paths /path/to/symbol/libraries/\n"
                            )
                            raise CircuitDiscoveryError(msg) from e
                        raise
                    except Exception as e:
                        raise CircuitDiscoveryError(
                            f"Circuit execution failed: {str(e)}"
                        ) from e
                        
                    # Analyze the populated default_circuit
                    return default_circuit.analyze_with_llm(
                        api_key=api_key,
                        output_file=output_file,
                        backend=backend,
                        model=model,
                        custom_prompt=prompt,
                        analyze_subcircuits=True
                    )
                    
                finally:
                    sys.path.pop(0)
                    # Clean up analysis module if it exists and not dumping temp files
                    if not dump_temp:
                        try:
                            analysis_module.unlink()
                        except Exception as e:
                            logging.warning(f"Failed to remove temporary module: {e}")
                    else:
                        logging.info(f"Temporary analysis module saved at: {analysis_module}")

            except CircuitDiscoveryError:
                raise
            except Exception as e:
                raise CircuitDiscoveryError(f"Circuit analysis failed: {str(e)}") from e
            
def validate_kicad_cli(path: str) -> str:
    """
    Validate that KiCad CLI exists and is executable.
    Provides platform-specific guidance if validation fails.
    
    Common paths by platform:
        - macOS: /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
        - Windows: C:\\Program Files\\KiCad\\7.0\\bin\\kicad-cli.exe
        - Linux: /usr/bin/kicad-cli
    
    Args:
        path: Path to kicad-cli executable
        
    Returns:
        Validated path
        
    Raises:
        FileNotFoundError: If executable not found, with platform-specific guidance
        PermissionError: If executable lacks permissions, with remediation steps
    """
    import platform
    
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


def parse_args() -> argparse.Namespace:
    """
    Parse and validate command line arguments.
    
    Returns:
        Parsed argument namespace
        
    Raises:
        argparse.ArgumentError: For invalid argument combinations
    """
    parser = argparse.ArgumentParser(
        description='KiCad to SKiDL conversion and circuit analysis pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              # Analyze an existing SKiDL file
              %(prog)s --skidl my_circuit.py --analyze --api-key YOUR_KEY
              
              # Generate netlist and SKiDL project from KiCad schematic, then analyze
              %(prog)s --schematic design.kicad_sch --generate-netlist --generate-skidl --analyze --api-key YOUR_KEY
              
              # Generate SKiDL from netlist and analyze using Ollama
              %(prog)s --netlist circuit.net --generate-skidl --analyze --backend ollama
              
              # Analyze KiCad-converted SKiDL project
              %(prog)s --skidl-dir myproject/ --analyze --api-key YOUR_KEY
            """)
    )
    
    # Input source group (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        '--schematic', '-s',
        help='Path to KiCad schematic (.kicad_sch) file'
    )
    source_group.add_argument(
        '--netlist', '-n',
        help='Path to netlist (.net) file'
    )
    source_group.add_argument(
        '--skidl',
        help='Path to SKiDL Python file to analyze'
    )
    source_group.add_argument(
        '--skidl-dir',
        help='Path to SKiDL project directory (e.g., from KiCad conversion)'
    )
    
    # Operation mode flags
    parser.add_argument(
        '--generate-netlist',
        action='store_true',
        help='Generate netlist from schematic'
    )
    parser.add_argument(
        '--generate-skidl',
        action='store_true',
        help='Generate SKiDL project from netlist'
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Run LLM analysis on circuits'
    )
    
    # Optional configuration
    def get_default_kicad_cli() -> str:
        """Get the default KiCad CLI path based on the current platform."""
        system = platform.system().lower()
        if system == 'darwin':  # macOS
            return "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
        elif system == 'windows':
            return "C:\\Program Files\\KiCad\\7.0\\bin\\kicad-cli.exe"
        else:  # Linux and others
            return "/usr/bin/kicad-cli"
    
    parser.add_argument(
        '--kicad-cli',
        default=get_default_kicad_cli(),
        help='Path to kicad-cli executable (defaults to standard installation path for your OS)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='.',
        help='Output directory for generated files'
    )
    parser.add_argument(
        '--api-key',
        help='OpenRouter API key for cloud LLM analysis (required for openrouter backend)'
    )
    parser.add_argument(
        '--backend',
        choices=['openrouter', 'ollama'],
        default='openrouter',
        help='LLM backend to use (default is openrouter)'
    )
    parser.add_argument(
        '--model',
        help='LLM model name for selected backend (ensure the model name conforms to the backend\'s naming standard)'
    )
    parser.add_argument(
        '--analysis-output',
        default='circuit_analysis.txt',
        help='Output file for analysis results'
    )
    parser.add_argument(
        '--analysis-prompt',
        help='Custom prompt for circuit analysis'
    )
    parser.add_argument(
        '--dump-temp',
        action='store_true',
        help='Keep and output the temporary analysis file for inspection'
    )
    parser.add_argument(
        '--kicad-lib-paths',
        nargs='*',
        help='List of custom KiCad library paths (e.g., /path/to/lib1 /path/to/lib2)'
    )
    
    args = parser.parse_args()
    
    # Validate argument combinations
    if args.generate_netlist and not args.schematic:
        parser.error("--generate-netlist requires --schematic")
    if args.generate_skidl and not (args.netlist or args.generate_netlist):
        parser.error("--generate-skidl requires --netlist or --generate-netlist")
    if args.analyze and args.backend == 'openrouter' and not args.api_key:
        parser.error("OpenRouter backend requires --api-key")
        
    return args


def main():
    """
    Main execution function implementing the KiCad-SKiDL-LLM pipeline.
    
    Supports:
    1. Direct analysis of SKiDL Python files
    2. Analysis of SKiDL project directories
    3. KiCad schematic conversion and analysis
    """
    try:
        args = parse_args()
        
        # Determine output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track the SKiDL source to analyze
        skidl_source = None
        
        # Handle KiCad conversion if requested
        if args.schematic or args.netlist:
            current_netlist = None
            
            # Step 1: Generate netlist if requested
            if args.schematic and args.generate_netlist:
                logging.info("Step 1: Generating netlist from schematic...")
                schematic_path = Path(args.schematic)
                if not schematic_path.exists():
                    raise FileNotFoundError(f"Schematic not found: {schematic_path}")
                    
                # Validate KiCad CLI
                kicad_cli = validate_kicad_cli(args.kicad_cli)
                
                # Generate netlist
                netlist_path = output_dir / f"{schematic_path.stem}.net"
                try:
                    subprocess.run([
                        kicad_cli, 'sch', 'export', 'netlist',
                        '-o', str(netlist_path), str(schematic_path)
                    ], check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(f"Netlist generation failed:\n{e.stderr}") from e
                
                current_netlist = netlist_path
                logging.info(f"✓ Generated netlist: {netlist_path}")
                
            elif args.netlist:
                current_netlist = Path(args.netlist)
                if not current_netlist.exists():
                    raise FileNotFoundError(f"Netlist not found: {current_netlist}")
                logging.info(f"Using existing netlist: {current_netlist}")
            
            # Step 2: Generate SKiDL if requested
            if args.generate_skidl:
                logging.info("Step 2: Generating SKiDL project from netlist...")
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
                
                skidl_source = skidl_dir
                logging.info(f"✓ Generated SKiDL project: {skidl_dir}")
        
        # Use direct SKiDL source if provided
        elif args.skidl:
            skidl_source = Path(args.skidl)
            if not skidl_source.exists():
                raise FileNotFoundError(f"SKiDL file not found: {skidl_source}")
            logging.info(f"Using SKiDL file: {skidl_source}")
            
        elif args.skidl_dir:
            skidl_source = Path(args.skidl_dir)
            if not skidl_source.exists():
                raise FileNotFoundError(f"SKiDL directory not found: {skidl_source}")
            logging.info(f"Using SKiDL project directory: {skidl_source}")
        
        # Add KiCad library paths if provided
        if args.kicad_lib_paths:
            from skidl import lib_search_paths, KICAD
            valid_paths = []
            invalid_paths = []
            
            for lib_path in args.kicad_lib_paths:
                path = Path(lib_path)
                if not path.is_dir():
                    invalid_paths.append((path, "Directory does not exist"))
                    continue
                
                # Check for KiCad 8 symbol files (.kicad_sym)
                sym_files = list(path.glob("*.kicad_sym"))
                if not sym_files:
                    invalid_paths.append((path, "No .kicad_sym symbol files found"))
                    continue

                valid_paths.append(path)
                lib_search_paths[KICAD].append(str(path))

            # Log results
            if valid_paths:
                logging.info("Added KiCad 8 library paths:")
                for path in valid_paths:
                    logging.info(f"  ✓ {path}")
                    sym_files = list(path.glob("*.kicad_sym"))
                    for sym in sym_files[:3]:  # Show up to 3 symbol libraries
                        logging.info(f"    - {sym.name}")
                    if len(sym_files) > 3:
                        logging.info(f"    - ... and {len(sym_files)-3} more")

            if invalid_paths:
                logging.warning("Some library paths were invalid:")
                for path, reason in invalid_paths:
                    logging.warning(f"  ✗ {path}: {reason}")
        
        # Step 3: Run analysis if requested
        if args.analyze:
            if not skidl_source:
                raise ValueError("No SKiDL source available for analysis")
                
            logging.info("Step 3: Analyzing circuits...")
            try:
                results = CircuitAnalyzer.analyze_circuits(
                    source=skidl_source,
                    output_file=args.analysis_output,
                    api_key=args.api_key,
                    backend=args.backend,
                    model=args.model,
                    prompt=args.analysis_prompt,
                    dump_temp=args.dump_temp
                )
                
                if results["success"]:
                    logging.info("Analysis Results:")
                    # Handle subcircuit results if present
                    if "subcircuits" in results:
                        for hier, analysis in results["subcircuits"].items():
                            logging.info(f"\nSubcircuit: {hier}")
                            if analysis["success"]:
                                logging.info(f"✓ Analysis completed in {analysis['request_time_seconds']:.2f} seconds")
                                tokens = analysis.get('prompt_tokens', 0) + analysis.get('response_tokens', 0)
                                if tokens:
                                    logging.info(f"  Tokens used: {tokens}")
                            else:
                                logging.error(f"✗ Analysis failed: {analysis['error']}")
                        
                        logging.info(f"\nTotal analysis time: {results['total_time_seconds']:.2f} seconds")
                        if results.get('total_tokens'):
                            logging.info(f"Total tokens used: {results['total_tokens']}")
                    else:
                        # Single circuit analysis results
                        logging.info(f"✓ Analysis completed in {results['request_time_seconds']:.2f} seconds")
                        tokens = results.get('prompt_tokens', 0) + results.get('response_tokens', 0)
                        if tokens:
                            logging.info(f"Tokens used: {tokens}")
                            
                    logging.info(f"Analysis results saved to: {args.analysis_output}")
                else:
                    raise RuntimeError(f"Analysis failed: {results.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logging.error("✗ Circuit analysis failed!")
                logging.error(f"Error: {str(e)}")
                if args.backend == 'openrouter':
                    logging.error("Troubleshooting tips:")
                    logging.error("1. Check your API key")
                    logging.error("2. Verify you have sufficient API credits")
                    logging.error("3. Check for rate limiting")
                else:
                    logging.error("Troubleshooting tips:")
                    logging.error("1. Verify Ollama is running locally")
                    logging.error("2. Check if the requested model is installed")
                raise
                
    except Exception as e:
        logging.error("Error: %s", str(e))
        logging.error("Stack trace:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()