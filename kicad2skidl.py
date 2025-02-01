#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
import argparse

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
    return parser.parse_args()

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
    try:
        netlist_path.unlink()
    except Exception as e:
        print(f"Warning: could not remove netlist file: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
