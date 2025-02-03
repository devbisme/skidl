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
import subprocess
import importlib
import textwrap
import traceback
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse
from skidl import *

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
                print(f"Warning: Could not parse {current_file}: {e}")
                
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
        Analyze circuits from a SKiDL source (file or directory).
        
        Handles both single file and project directory cases:
        - Single file: Imports and executes directly
        - Directory: Finds @subcircuit functions and creates an analysis module
        
        Args:
            source: Path to SKiDL file or project directory
            output_file: Where to save analysis results
            api_key: API key for cloud LLM service (required for openrouter)
            backend: 'openrouter' or 'ollama'
            model: Model name for selected backend (model names must adhere to the backend's naming standard)
            prompt: Custom analysis prompt
            dump_temp: If True, do not delete the temporary analysis module and output its location.
            
        Returns:
            Analysis results dictionary containing:
                - success: bool
                - subcircuits: Dict of subcircuit analysis results
                - total_time_seconds: float
                - total_tokens: int (if applicable)
                - error: str (if success is False)
                
        Raises:
            CircuitDiscoveryError: For circuit loading/execution issues
            RuntimeError: For analysis failures
        """
        if source.is_file():
            # Single file case - import directly.
            sys.path.insert(0, str(source.parent))
            try:
                module = importlib.import_module(source.stem)
                importlib.reload(module)
                if hasattr(module, 'main'):
                    module.main()
                else:
                    raise CircuitDiscoveryError(
                        f"No main() function found in {source}"
                    )
            except Exception as e:
                raise CircuitDiscoveryError(
                    f"Failed to load/execute {source}: {str(e)}"
                ) from e
            finally:
                sys.path.pop(0)
                
        else:
            # Directory case - find and analyze subcircuits.
            try:
                subcircuits = CircuitAnalyzer.find_subcircuits(source)
                if not subcircuits:
                    raise CircuitDiscoveryError(
                        f"No @subcircuit functions found in {source}"
                    )
                
                analysis_module, generated_code = CircuitAnalyzer.create_analysis_module(
                    subcircuits, source
                )
                
                print(f"Found {len(subcircuits)} circuits to analyze:")
                for circuit in subcircuits:
                    print(f"  - {circuit['function']} ({circuit['file']}:{circuit['lineno']})")
                
                sys.path.insert(0, str(source))
                try:
                    module = importlib.import_module('circuit_analysis')
                    importlib.reload(module)
                    module.main()
                finally:
                    sys.path.pop(0)
                    if dump_temp:
                        print(f"Temporary analysis module saved at: {analysis_module}")
                    else:
                        try:
                            analysis_module.unlink()  # Clean up temporary file.
                        except Exception as e:
                            print(f"Warning: Failed to remove temporary module: {e}")
                        
            except Exception as e:
                raise CircuitDiscoveryError(
                    f"Circuit discovery/execution failed: {str(e)}"
                ) from e

        # Run LLM analysis.
        try:
            analysis_kwargs = {
                'output_file': output_file,
                'backend': backend,
                'analyze_subcircuits': True
            }
            
            if api_key:
                analysis_kwargs['api_key'] = api_key
            if model:
                analysis_kwargs['model'] = model
            if prompt:
                analysis_kwargs['custom_prompt'] = prompt
                
            return default_circuit.analyze_with_llm(**analysis_kwargs)
            
        except Exception as e:
            raise RuntimeError(f"LLM analysis failed: {str(e)}") from e


def validate_kicad_cli(path: str) -> str:
    """
    Validate that KiCad CLI exists and is executable.
    
    NOTE for novice users:
      You may need to adjust the path to point to your local KiCad installation.
      For example, on macOS the default might be:
          /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
      Change this value with the --kicad-cli parameter if necessary.
    
    Args:
        path: Path to kicad-cli executable
        
    Returns:
        Validated path
        
    Raises:
        FileNotFoundError: If executable not found
        PermissionError: If executable lacks permissions
    """
    cli_path = Path(path)
    if not cli_path.exists():
        raise FileNotFoundError(f"KiCad CLI not found: {path}")
    if not os.access(str(cli_path), os.X_OK):
        raise PermissionError(f"KiCad CLI not executable: {path}")
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
        description='KiCad schematic to SKiDL conversion and analysis pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              # Generate netlist and SKiDL project from schematic
              %(prog)s --schematic design.kicad_sch --generate-netlist --generate-skidl
              
              # Analyze existing SKiDL project using OpenRouter
              %(prog)s --skidl-source myproject/ --analyze --api-key YOUR_KEY
              
              # Generate SKiDL from netlist and analyze using Ollama
              %(prog)s --netlist circuit.net --generate-skidl --analyze --backend ollama
              
              # Dump the temporary analysis file for inspection:
              %(prog)s --skidl-source myproject/ --analyze --api-key YOUR_KEY --dump-temp
            """)
    )
    
    # Input source group (mutually exclusive).
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
        '--skidl-source',
        help='Path to SKiDL file or project directory'
    )
    
    # Operation mode flags.
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
    
    # Optional configuration.
    parser.add_argument(
        '--kicad-cli',
        default="/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
        help='Path to kicad-cli executable (adjust this if your KiCad installation is in a different location)'
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
        help='LLM backend to use (default is openrouter; note that model names must follow OpenRouter naming standards)'
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
        help='Keep and output the temporary SKiDL analysis file for manual inspection'
    )
    
    args = parser.parse_args()
    
    # Validate argument combinations.
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
    
    Implements a flexible pipeline that can:
    1. Generate netlist from KiCad schematic
    2. Convert netlist to SKiDL project
    3. Analyze circuits using LLM
    
    The pipeline tracks state between steps and provides detailed
    error reporting for each stage.
    
    Note: Ensure that you have configured the correct path for kicad-cli,
    and that any LLM model names conform to the backend's naming requirements.
    
    Raises:
        Various exceptions with descriptive messages for different
        failure modes.
    """
    try:
        args = parse_args()
        
        # Determine output directory.
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track current state for pipeline.
        current_netlist = None
        current_skidl = None
        
        # 1. Generate netlist if requested.
        if args.schematic and args.generate_netlist:
            print("\nStep 1: Generating netlist from schematic...")
            schematic_path = Path(args.schematic)
            if not schematic_path.exists():
                raise FileNotFoundError(f"Schematic not found: {schematic_path}")
            if schematic_path.suffix != '.kicad_sch':
                raise ValueError(f"Input must be .kicad_sch file: {schematic_path}")
            
            # Validate KiCad CLI; adjust the path via --kicad-cli if needed.
            kicad_cli = validate_kicad_cli(args.kicad_cli)
            
            # Generate netlist using the KiCad CLI tool.
            netlist_path = output_dir / f"{schematic_path.stem}.net"
            try:
                subprocess.run([
                    kicad_cli,
                    'sch',
                    'export',
                    'netlist',
                    '-o',
                    str(netlist_path),
                    str(schematic_path)
                ], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f"Netlist generation failed:\n{e.stderr}"
                ) from e
            
            current_netlist = netlist_path
            print(f"✓ Generated netlist: {netlist_path}")
            
        # 2. Start from netlist if provided.
        elif args.netlist:
            current_netlist = Path(args.netlist)
            if not current_netlist.exists():
                raise FileNotFoundError(f"Netlist not found: {current_netlist}")
            print(f"\nUsing existing netlist: {current_netlist}")
            
        # 3. Generate SKiDL project if requested.
        if current_netlist and args.generate_skidl:
            print("\nStep 2: Generating SKiDL project from netlist...")
            skidl_dir = output_dir / f"{current_netlist.stem}_SKIDL"
            skidl_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                subprocess.run([
                    'netlist_to_skidl',
                    '-i', str(current_netlist),
                    '--output', str(skidl_dir)
                ], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f"SKiDL project generation failed:\n{e.stderr}"
                ) from e
            
            current_skidl = skidl_dir
            print(f"✓ Generated SKiDL project: {skidl_dir}")
            
        # 4. Start from SKiDL if provided.
        elif args.skidl_source:
            current_skidl = Path(args.skidl_source)
            if not current_skidl.exists():
                raise FileNotFoundError(f"SKiDL source not found: {current_skidl}")
            print(f"\nUsing existing SKiDL source: {current_skidl}")
            
        # 5. Run analysis if requested.
        if args.analyze:
            if not current_skidl:
                raise ValueError("No SKiDL source available for analysis")
                
            print("\nStep 3: Analyzing circuits...")
            try:
                results = CircuitAnalyzer.analyze_circuits(
                    source=current_skidl,
                    output_file=args.analysis_output,
                    api_key=args.api_key,
                    backend=args.backend,
                    model=args.model,
                    prompt=args.analysis_prompt,
                    dump_temp=args.dump_temp
                )
                
                if results["success"]:
                    print("\nAnalysis Results:")
                    for hier, analysis in results["subcircuits"].items():
                        print(f"\nSubcircuit: {hier}")
                        if analysis["success"]:
                            print(f"✓ Analysis completed in {analysis['request_time_seconds']:.2f} seconds")
                            tokens = analysis.get('prompt_tokens', 0) + analysis.get('response_tokens', 0)
                            if tokens:
                                print(f"  Tokens used: {tokens}")
                        else:
                            print(f"✗ Analysis failed: {analysis['error']}")
                    
                    print(f"\nTotal analysis time: {results['total_time_seconds']:.2f} seconds")
                    if results.get('total_tokens'):
                        print(f"Total tokens used: {results['total_tokens']}")
                    print(f"Analysis results saved to: {args.analysis_output}")
                else:
                    raise RuntimeError(f"Analysis failed: {results.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print("\n✗ Circuit analysis failed!")
                print(f"Error: {str(e)}")
                if args.backend == 'openrouter':
                    print("\nTroubleshooting tips:")
                    print("1. Check your API key")
                    print("2. Verify you have sufficient API credits")
                    print("3. Check for rate limiting")
                else:
                    print("\nTroubleshooting tips:")
                    print("1. Verify Ollama is running locally")
                    print("2. Check if the requested model is installed")
                raise
                
    except Exception as e:
        print("\nError:", str(e))
        print("\nStack trace:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
