#!/usr/bin/env python3

"""
This script is used to collect all the code files needed for the LLM chat completion task.
It will search for specific files in a given directory and combine their contents into a single output file.

Edit the "INTRO_MESSAGE" variable to add a message at the start of the output file.

This tool is useful for preparing code snippets for AI-based code completion tasks.
"""

#==============================================================================
# QUICK EDIT CONFIGURATION - Modify these values as needed
#==============================================================================

# Where to look for files
ROOT_DIRECTORY = "/Users/shanemattner/Desktop/skidl"

# Where to save the combined output
OUTPUT_FILE = "collected_code.txt"

# What files to collect - specify full relative paths from ROOT_DIRECTORY
TARGET_FILES = [
    'src/skidl/circuit.py',
    'src/skidl/llm_providers.py',
    'src/skidl/circuit_analyzer.py',
    'skidl_test.py',
]

# Message to add at the start of the output file
INTRO_MESSAGE = """
Help me develop code for implementing the LLM analysis of the circuit.
"""

#==============================================================================
# Script Implementation - No need to modify below this line
#==============================================================================

import os
from typing import List
from dataclasses import dataclass

@dataclass
class FileCollectorConfig:
    """Configuration class to store all script parameters"""
    root_directory: str
    output_filename: str
    target_files: List[str]
    intro_message: str

def create_config_from_settings() -> FileCollectorConfig:
    """Creates configuration object from the settings defined at the top of the script"""
    return FileCollectorConfig(
        root_directory=ROOT_DIRECTORY,
        output_filename=OUTPUT_FILE,
        target_files=TARGET_FILES,
        intro_message=INTRO_MESSAGE
    )

def normalize_path(path: str) -> str:
    """Normalize a path by replacing backslashes with forward slashes"""
    return path.replace('\\', '/')

def is_target_file(filepath: str, root_dir: str, target_files: List[str]) -> bool:
    """
    Check if a filepath matches our target criteria.
    
    Args:
        filepath: Full path of the file to check
        root_dir: Root directory for relative path calculation
        target_files: List of target relative paths
    """
    # Convert the full path to a relative path from root_dir
    try:
        rel_path = os.path.relpath(filepath, root_dir)
        rel_path = normalize_path(rel_path)
        
        # Debug print
        print(f"Checking file: {rel_path}")
        
        # Check if this relative path matches any target path
        return rel_path in target_files
    except ValueError:
        # This can happen if filepath is on a different drive than root_dir
        return False

def find_target_files(config: FileCollectorConfig) -> List[str]:
    """
    Search for target files in the root directory.
    
    Args:
        config: Configuration object containing search parameters
    
    Returns:
        List[str]: List of full file paths for matching files
    """
    collected_files = []
    
    print(f"\nSearching in root directory: {config.root_directory}")
    print(f"Looking for files with these relative paths:")
    for target in config.target_files:
        print(f"- {target}")
    print()
    
    # Walk through the directory tree
    for dirpath, dirnames, filenames in os.walk(config.root_directory):
        print(f"\nExamining directory: {dirpath}")
        
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if os.path.isfile(full_path) and is_target_file(full_path, config.root_directory, config.target_files):
                collected_files.append(full_path)
                print(f"Added to collection: {full_path}")
    
    return sorted(collected_files)

def write_combined_file(collected_files: List[str], config: FileCollectorConfig) -> None:
    """
    Write all collected file contents to a single output file.
    
    Args:
        collected_files: List of file paths to combine
        config: Configuration object containing output settings
    """
    with open(config.output_filename, 'w') as out_file:
        # Write the introduction message
        out_file.write(config.intro_message + "\n")
        
        # Process each collected file
        total_lines = 0
        for file_path in collected_files:
            try:
                # Read and write each file's contents with clear separation
                with open(file_path, 'r') as input_file:
                    content = input_file.read()
                    relative_path = os.path.relpath(file_path, config.root_directory)
                    relative_path = normalize_path(relative_path)
                    
                    # Add clear separators around file content
                    out_file.write(f"\n/* Begin of file: {relative_path} */\n")
                    out_file.write(content)
                    out_file.write(f"\n/* End of file: {relative_path} */\n")
                    
                    # Print statistics for monitoring
                    num_lines = len(content.splitlines())
                    total_lines += num_lines
                    print(f"{relative_path}: {num_lines} lines")
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        print(f"Total lines written: {total_lines}")

def main():
    """Main execution function"""
    # Create configuration from settings
    config = create_config_from_settings()
    
    # Find all matching files
    collected_files = find_target_files(config)
    
    if not collected_files:
        print("\nNo matching files found! Check your ROOT_DIRECTORY and TARGET_FILES settings.")
        return
        
    print("\nFound files:")
    for f in collected_files:
        print(f"- {f}")
        
    # Combine files into output
    print("\nWriting combined output file...")
    write_combined_file(collected_files, config)
    
    # Print summary
    print(f"\nProcessed {len(collected_files)} files")
    print(f"Output saved to: {config.output_filename}")

if __name__ == "__main__":
    main()