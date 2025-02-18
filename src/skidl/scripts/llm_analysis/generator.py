"""Netlist and SKiDL project generation utilities."""

import subprocess
import logging
from pathlib import Path
from typing import Optional

from .kicad import validate_kicad_cli

logger = logging.getLogger("kicad_skidl_llm")

def generate_netlist(
    schematic_path: Path,
    output_dir: Path,
    kicad_cli_path: str
) -> Optional[Path]:
    """Generate netlist from KiCad schematic.
    
    Args:
        schematic_path: Path to KiCad schematic file
        output_dir: Directory to save generated netlist
        kicad_cli_path: Path to KiCad CLI executable
        
    Returns:
        Path to generated netlist, or None if generation was skipped
        
    Raises:
        FileNotFoundError: If schematic file doesn't exist
        RuntimeError: If netlist generation fails
    """
    if not schematic_path.exists():
        raise FileNotFoundError(f"Schematic not found: {schematic_path}")
        
    kicad_cli = validate_kicad_cli(kicad_cli_path)
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

def generate_skidl_project(
    netlist_path: Path,
    output_dir: Path
) -> Optional[Path]:
    """Generate SKiDL project from netlist.
    
    Args:
        netlist_path: Path to netlist file
        output_dir: Directory to save generated SKiDL project
        
    Returns:
        Path to generated SKiDL project directory, or None if generation was skipped
        
    Raises:
        RuntimeError: If SKiDL project generation fails
    """
    skidl_dir = output_dir / f"{netlist_path.stem}_SKIDL"
    skidl_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        subprocess.run([
            'netlist_to_skidl',
            '-i', str(netlist_path),
            '--output', str(skidl_dir)
        ], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"SKiDL project generation failed:\n{e.stderr}") from e
    
    logger.info(f"✓ Generated SKiDL project: {skidl_dir}")
    return skidl_dir

def get_skidl_source(
    skidl_file: Optional[Path] = None,
    skidl_dir: Optional[Path] = None,
    generated_dir: Optional[Path] = None
) -> Path:
    """Determine the SKiDL source to analyze.
    
    This function implements a priority order for determining which
    SKiDL source to use for analysis:
    1. Explicitly provided SKiDL file
    2. Explicitly provided SKiDL directory
    3. Generated SKiDL project directory
    
    Args:
        skidl_file: Path to specific SKiDL Python file
        skidl_dir: Path to SKiDL project directory
        generated_dir: Path to automatically generated SKiDL project
        
    Returns:
        Path to SKiDL source to analyze
        
    Raises:
        ValueError: If no valid SKiDL source is available
        FileNotFoundError: If specified source doesn't exist
    """
    if skidl_file:
        if not skidl_file.exists():
            raise FileNotFoundError(f"SKiDL file not found: {skidl_file}")
        return skidl_file
    elif skidl_dir:
        if not skidl_dir.exists():
            raise FileNotFoundError(f"SKiDL directory not found: {skidl_dir}")
        return skidl_dir
    elif generated_dir:
        return generated_dir
    else:
        raise ValueError("No SKiDL source available for analysis")