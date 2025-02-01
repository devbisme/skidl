#!/usr/bin/env python3
import os
import sys
import subprocess
import importlib
from pathlib import Path
import argparse
from skidl import *

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='KiCad schematic to SKiDL conversion pipeline'
    )
    parser.add_argument(
        '--schematic', '-s', required=True,
        help='Path to KiCad schematic (.kicad_sch) file'
    )
    parser.add_argument(
        '--kicad-cli',
        default="/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
        help='Path to kicad-cli executable'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='.',
        help="Output directory for generated files. If set to '.', a default directory named <schematic_name>_SKIDL is created."
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Run LLM analysis on the generated SKiDL circuit'
    )
    parser.add_argument(
        '--api-key',
        help='OpenRouter API key for LLM analysis'
    )
    parser.add_argument(
        '--analysis-output',
        default='circuit_analysis.txt',
        help='Output file for analysis results'
    )
    parser.add_argument(
        '--model',
        default='google/gemini-flash-1.5',
        help='LLM model to use for analysis (default: google/gemini-flash-1.5)'
    )
    return parser.parse_args()

def execute_skidl_main(skidl_dir: Path) -> None:
    """
    Import and execute the main() function from the generated SKiDL project.
    This creates the circuit that we can then analyze.
    """
    # Add project directory to Python path
    sys.path.insert(0, str(skidl_dir))
    
    try:
        # Import the generated main module
        import main
        importlib.reload(main)  # Reload in case it was previously imported
        
        # Execute main() to create the circuit
        main.main()
        
    finally:
        # Clean up sys.path
        sys.path.pop(0)

def analyze_skidl_circuit(output_file: str, api_key: str = None, model: str = 'google/gemini-flash-1.5') -> dict:
    """
    Analyze the current default circuit using SKiDL's built-in analyze_with_llm.
    
    Args:
        output_file: Path to save analysis results
        api_key: OpenRouter API key (if None, will try to get from environment)
        model: LLM model to use for analysis (default: google/gemini-flash-1.5)
        
    Returns:
        dict: Analysis results including success status, timing, and any errors
    """
    # Get API key from environment if not provided
    if api_key is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "OpenRouter API key not found. Please provide via --api-key or set OPENROUTER_API_KEY environment variable."
            }

    try:
        # First save query only to get circuit description
        default_circuit.analyze_with_llm(
            output_file="query.txt",
            save_query_only=True
        )
        
        # Then do the actual analysis with the specified model
        return default_circuit.analyze_with_llm(
            api_key=api_key,
            output_file=output_file,
            analyze_subcircuits=True,
            model=model,
            custom_prompt="Analyze the circuit for functionality, safety considerations, and potential improvements."
        )
    except Exception as e:
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }

def validate_schematic(schematic_path: Path) -> Path:
    """Validate the schematic file exists and has the correct extension."""
    if not schematic_path.exists():
        raise FileNotFoundError(f"Schematic file not found: {schematic_path}")
    if schematic_path.suffix != '.kicad_sch':
        raise ValueError(f"Input file must be a .kicad_sch file: {schematic_path}")
    return schematic_path

def generate_netlist(schematic_path: Path, kicad_cli_path: str, output_dir: Path) -> Path:
    """Generate netlist from KiCad schematic in the output directory."""
    netlist_path = output_dir / f"{schematic_path.stem}.net"
    cmd = [
        kicad_cli_path,
        'sch',
        'export',
        'netlist',
        '-o',
        str(netlist_path),
        str(schematic_path)
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Generated netlist: {netlist_path}")
        return netlist_path
    except subprocess.CalledProcessError as e:
        print(f"Error generating netlist:\n{e.stderr}", file=sys.stderr)
        raise

def generate_skidl_project(netlist_path: Path, output_dir: Path) -> Path:
    """Generate SKiDL project from the netlist in the output directory."""
    skidl_dir = output_dir
    skidl_dir.mkdir(parents=True, exist_ok=True)
    
    # Run netlist_to_skidl to generate the SKiDL files
    cmd = [
        'netlist_to_skidl',
        '-i', str(netlist_path),
        '--output', str(skidl_dir)
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("\nGenerated SKiDL project files:")
        for file_path in sorted(skidl_dir.glob("*.py")):
            print(f"  {file_path.name}")
        return skidl_dir
    except subprocess.CalledProcessError as e:
        print(f"Error generating SKiDL project:\n{e.stderr}", file=sys.stderr)
        raise

def main():
    args = parse_args()
    schematic_path = validate_schematic(Path(args.schematic))
    
    # Determine the output directory.
    if args.output_dir == '.':
        output_dir = Path(f"{schematic_path.stem}_SKIDL")
    else:
        output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Found valid schematic: {schematic_path}")
    
    # Generate the netlist.
    netlist_path = generate_netlist(schematic_path, args.kicad_cli, output_dir)
    print(f"Successfully generated netlist at: {netlist_path}")
    
    # Convert the netlist to a SKiDL project.
    skidl_dir = generate_skidl_project(netlist_path, output_dir)
    print(f"Successfully generated SKiDL project at: {skidl_dir}")
    
    # Clean up the temporary netlist file.
    # try:
    #     netlist_path.unlink()
    # except Exception as e:
    #     print(f"Warning: could not remove netlist file: {e}", file=sys.stderr)
        
    # Run LLM analysis if requested
    if args.analyze:
        print("\nRunning circuit analysis...")
        try:
            # First execute the main script to create the circuit
            execute_skidl_main(skidl_dir)
            
            # Print docstrings for each subcircuit before analysis
            print("\nSubcircuit Docstrings:")
            for name, doc in default_circuit.subcircuit_docs.items():
                print(f"\n{name}:")
                print(doc)
            
            # Run the analysis
            results = analyze_skidl_circuit(
                output_file=args.analysis_output,
                api_key=args.api_key,
                model=args.model
            )
            
            if results["success"]:
                print("\nAnalysis Results:")
                for hier, analysis in results["subcircuits"].items():
                    print(f"\nSubcircuit: {hier}")
                    if analysis["success"]:
                        print(f"Analysis completed in {analysis['request_time_seconds']:.2f} seconds")
                        tokens = analysis.get('prompt_tokens', 0) + analysis.get('response_tokens', 0)
                        if tokens:
                            print(f"Tokens used: {tokens}")
                    else:
                        print(f"Analysis failed: {analysis['error']}")
                
                print(f"\nTotal analysis time: {results['total_time_seconds']:.2f} seconds")
                if results.get('total_tokens'):
                    print(f"Total tokens used: {results['total_tokens']}")
                print(f"Analysis results saved to: {args.analysis_output}")
            else:
                print(f"\nAnalysis failed: {results.get('error', 'Unknown error')}")
                
        except KeyboardInterrupt:
            print("\nAnalysis interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\nError during analysis: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
