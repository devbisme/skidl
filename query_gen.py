#!/usr/bin/env python3

#==============================================================================
# QUICK EDIT CONFIGURATION - Modify these values as needed
#==============================================================================

# Where to look for files
ROOT_DIRECTORY = "/Users/shanemattner/Desktop/skidl"

# Where to save the combined output
OUTPUT_FILE = "collected_code.txt"

# What files to collect (add or remove filenames as needed)
TARGET_FILES = [
    'netlist_to_skidl.py',
    'main_control_board.py',
    'Block_Diagram.py',
    'Project_Architecture.py',
    'Power_Info.py',
    'Revision_History.py',
    'Coral_TPU.py',
    'ESP32S3.PY',
    'Left_Leg.py',
    'Right_Leg.py',
    'Voltage_Regulators.py',    
    'main_simple_project.py',
    'esp32s3mini1.py',
    '_3v3_regulator.py',
    'resistor_divider1.py',
    'test_examples.py',
    'USB.py',
]

# Message to add at the start of the output file
INTRO_MESSAGE = """

netlist_to_skidl.py is the source file for logic that converts a KiCad netlist to a SKiDL script.

This logic seems to work well for a complex KiCAD project.  See the files:
    'main_control_board.py',
    'Block_Diagram.py',
    'Project_Architecture.py',
    'Power_Info.py',
    'Revision_History.py',
    'Coral_TPU.py',
    'ESP32S3.PY',
    'Left_Leg.py',
    'Right_Leg.py',
    'Voltage_Regulators.py',    

However, this logic breaks when trying to convert a KiCAD netlist for a simple project.  See the files:

    'main_simple_project.py',
    'esp32s3mini1.py',
    '_3v3_regulator.py',
    'resistor_divider1.py',
    'test_examples.py',
    'USB.py',

Analyze netlist_to_skidl.py to determine why it breaks for simple projects.  The goal is to make it work for both simple and complex projects. 
The algorithm should be general enough that it works for any KiCAD project.  The algorithm should not be hard-coded to work for specific projects.

Do not produce any code yet.  Just analyze the existing code and determine what changes are needed to make it work for both simple and complex projects.
Ask me questions to clarify anything you do not fully understand.  Give me examples of what you are thinking.

"""

#==============================================================================
# Script Implementation - No need to modify below this line
#==============================================================================

"""
File Collector for Query Building

This script combines specific files into a single output file to help build
queries when iterating on software development. Edit the CONFIGURATION section
at the top to customize which files to collect.
"""

import os
from typing import List
from dataclasses import dataclass

@dataclass
class FileCollectorConfig:
    """Configuration class to store all script parameters"""
    root_directory: str
    output_filename: str
    target_filenames: List[str]
    intro_message: str

def create_config_from_settings() -> FileCollectorConfig:
    """Creates configuration object from the settings defined at the top of the script"""
    return FileCollectorConfig(
        root_directory=ROOT_DIRECTORY,
        output_filename=OUTPUT_FILE,
        target_filenames=TARGET_FILES,
        intro_message=INTRO_MESSAGE
    )

def is_target_file(filename: str, target_files: List[str]) -> bool:
    """
    Check if a filename matches one of our target filenames.
    
    Args:
        filename: Name of the file to check
        target_files: List of target filenames to match against
    """
    return os.path.basename(filename) in target_files

def find_target_files(config: FileCollectorConfig) -> List[str]:
    """
    Search for target files in the root directory.
    
    Args:
        config: Configuration object containing search parameters
    
    Returns:
        List[str]: List of full file paths for matching files
    """
    collected_files = []
    
    # Walk through the directory tree
    for dirpath, _, filenames in os.walk(config.root_directory):
        for filename in filenames:
            if is_target_file(filename, config.target_filenames):
                full_path = os.path.join(dirpath, filename)
                if os.path.isfile(full_path):
                    collected_files.append(full_path)
    
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
                    filename = os.path.basename(file_path)
                    
                    # Add clear separators around file content
                    out_file.write(f"\n/* Begin of file: {filename} */\n")
                    out_file.write(content)
                    out_file.write(f"\n/* End of file: {filename} */\n")
                    
                    # Print statistics for monitoring
                    num_lines = len(content.splitlines())
                    total_lines += num_lines
                    print(f"{filename}: {num_lines} lines")
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        print(f"Total lines written: {total_lines}")

def main():
    """Main execution function"""
    # Create configuration from settings
    config = create_config_from_settings()
    
    # Find all matching files
    collected_files = find_target_files(config)
    
    # Combine files into output
    write_combined_file(collected_files, config)
    
    # Print summary
    print(f"\nProcessed {len(collected_files)} files")
    print(f"Output saved to: {config.output_filename}")

if __name__ == "__main__":
    main()
