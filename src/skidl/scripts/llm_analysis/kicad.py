"""KiCad integration utilities for circuit analysis."""

import os
import platform
from pathlib import Path
from typing import Optional, List
import logging

from skidl import lib_search_paths, KICAD

logger = logging.getLogger("kicad_skidl_llm")

def validate_kicad_cli(path: str) -> str:
    """Validate KiCad CLI executable and provide platform-specific guidance.
    
    Args:
        path: Path to KiCad CLI executable
        
    Returns:
        Validated path to KiCad CLI
        
    Raises:
        FileNotFoundError: If KiCad CLI is not found
        PermissionError: If KiCad CLI is not executable
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
    """Get the default KiCad CLI path based on the current platform.
    
    Returns:
        Platform-specific default path to KiCad CLI executable
    """
    system = platform.system().lower()
    if system == 'darwin':  # macOS
        return "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
    elif system == 'windows':
        return r"C:\Program Files\KiCad\7.0\bin\kicad-cli.exe"
    else:  # Linux and others
        return "/usr/bin/kicad-cli"

def handle_kicad_libraries(lib_paths: Optional[List[str]]) -> None:
    """Add and validate KiCad library paths.
    
    Args:
        lib_paths: List of paths to KiCad symbol libraries
        
    Raises:
        RuntimeError: If no valid library paths are found
    """
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