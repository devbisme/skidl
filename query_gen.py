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
    'example_kicad_project.net',
    'report.txt'
]

# Message to add at the start of the output file
INTRO_MESSAGE = """

netlist_to_skidl.py is the source file for logic that converts a KiCad netlist into equivalent hierarchical SKiDL programs.

This logic works well for a complex KiCad project. See the following files for the complex project:
    - main_control_board.py
    - Block_Diagram.py
    - Project_Architecture.py
    - Power_Info.py
    - Revision_History.py
    - Coral_TPU.py
    - ESP32S3.PY
    - Left_Leg.py
    - Right_Leg.py
    - Voltage_Regulators.py

However, when converting a KiCad netlist for a simple project (see these files):
    - example_kicad_project.net (netlist file being processed)
    - main_simple_project.py
    - esp32s3mini1.py
    - _3v3_regulator.py
    - resistor_divider1.py
    - test_examples.py
    - USB.py
    - report.txt

The logic seems to work fairly well except:
- **esp32s3mini1() Parameter Issue:**  
  The generated subcircuit definition for `esp32s3mini1` erroneously includes an argument named `esp32s3mini1_HW_VER`. This net is not needed as an external parameter for this subcircuit. After manually removing this argument and running the generated main file, the output netlist imports correctly into KiCad (see report.txt for import logs). The problem appears to be in the net analysis logic, where the converter mistakenly classifies the net named `/esp32s3mini1/HW_VER` as imported rather than local. The solution is to adjust the net classification so that if the net originates in the same sheet as the subcircuit (or is intended to be local), it is not passed in as a parameter.

- **main_control_board.py Subcircuit Calls:**  
  In the complex project, the generated `main_control_board.py` does not call any of the subsheets. In other words, the top-level file fails to invoke the subcircuits (such as Block_Diagram, ESP32S3, Voltage_Regulators, etc.). This indicates that the logic used to decide which sheets are “top-level” (and thus should be called from main) is not detecting them properly. The net analysis and sheet‐hierarchy code must be adjusted so that the top‐level aggregator (or main sheet) correctly calls all its child subcircuits—even if some of them do not import any nets—so that the hierarchical structure is fully instantiated in the generated main file.

- **Project_Architecture() Parameter Issue:**  
  The generated definition for `Project_Architecture()` (which serves as the top-level sheet for the board) erroneously includes many parameters (e.g. `_p_3_3V`, `_p_5V`, and several others). Since Project_Architecture.py is intended to be the top-level sheet (with its purpose being mainly to document the overall architecture), it should not require any externally passed parameters; it should instead define its own local nets (or rely on the global definitions created by main). This indicates that the converter’s heuristic for deciding which nets are “imported” (i.e. must be passed in as parameters) is treating nets used in Project_Architecture as imported rather than local. The solution is to modify the net classification logic so that for the top-level aggregator sheet, all nets that it uses are defined locally and no parameters are required.

In summary, the underlying issue in both simple and complex projects is how the converter’s net analysis and sheet‐hierarchy logic decide whether a net is “imported” (and thus should appear as a function parameter) or “local” (defined inside the subcircuit). For the simple project, no parameters are passed to subcircuits (even though the design requires them), while for the complex project the top-level Project_Architecture subcircuit is erroneously given a long parameter list. The fix must be made purely through analysis (e.g. by comparing the sheet’s “origin” for a net versus its usage) rather than by hardcoding specific net or sheet names.

**Where to Look for a Solution:**

- **netlist_to_skidl.py:**  
  • In the `analyze_nets()` method, review how nets are classified as local versus imported. The logic that checks whether a net “originates” in the same sheet should be adjusted so that, for example, the `/esp32s3mini1/HW_VER` net is marked as local (thus not passed in as a parameter to `esp32s3mini1`).  
  • In the `create_main_file()` method, verify the conditions used to decide which sheets are “top-level” (i.e. those that should be called from main). The condition should not omit subcircuits from being called if they belong to the top-level hierarchy.
  
- **Sheet Hierarchy:**  
  Examine how sheet parent/child relationships are built in `extract_sheet_info()` and how they influence the net analysis. Ensure that a top-level aggregator like Project_Architecture is treated as “local” for its nets, so that no external parameters are needed.

- **Subcircuit Calls in main_simple_project.py and main_control_board.py:**  
  Compare the generated main files for the simple and complex projects. The simple project should have calls like  
  ```python
  esp32s3mini1(_p_3V3, _3v3_monitor, _5v_monitor, D_p, D_n, GND)
  _3v3_regulator(_p_3V3, _p_5V, _3v3_monitor, _5v_monitor, GND)
  USB(_p_5V, D_p, D_n, GND)

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
