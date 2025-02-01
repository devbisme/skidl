# -*- coding: utf-8 -*-

"""
Convert a KiCad netlist into equivalent hierarchical SKiDL programs.
"""

import re
import os
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Set
from kinparse import parse_netlist

@dataclass
class Sheet:
    number: str
    name: str
    path: str
    components: List
    local_nets: Set[str]
    imported_nets: Set[str]
    parent: str = None
    children: List[str] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []

class HierarchicalConverter:
    def __init__(self, netlist_src):
        self.netlist = parse_netlist(netlist_src)
        self.sheets = {}
        self.tab = " " * 4

    def extract_sheet_info(self):
        """Build sheet hierarchy from netlist."""
        print("\n=== Extracting Sheet Info ===")
        # First pass: Create all sheets
        for sheet in self.netlist.sheets:
            path = sheet.name.strip('/')
            name = path.split('/')[-1] if path else 'main'
            parent = '/'.join(path.split('/')[:-1]) if '/' in path else None
            
            self.sheets[path] = Sheet(
                number=sheet.number,
                name=name,
                path=path,
                components=[],
                local_nets=set(),
                imported_nets=set(),
                parent=parent,
                children=[]
            )
        
        # Second pass: Build parent-child relationships
        for sheet in self.sheets.values():
            if sheet.parent:
                parent_sheet = self.sheets.get(sheet.parent)
                if parent_sheet:
                    parent_sheet.children.append(sheet.path)

    def get_sheet_path(self, comp):
        """Get sheet path from component properties."""
        if isinstance(comp.properties, dict):
            return comp.properties.get('Sheetname', '')
        sheet_prop = next((p for p in comp.properties if p.name == 'Sheetname'), None)
        return sheet_prop.value if sheet_prop else ''

    def assign_components_to_sheets(self):
        """Assign components to their respective sheets."""
        print("\n=== Assigning Components to Sheets ===")
        for comp in self.netlist.parts:
            sheet_name = self.get_sheet_path(comp)
            if sheet_name:
                for sheet in self.sheets.values():
                    if sheet.name == sheet_name:
                        sheet.components.append(comp)
                        break

    def get_sheet_hierarchy_path(self, sheet_name):
        """Get the full hierarchical path from root to given sheet."""
        path = []
        current = sheet_name
        while current in self.sheets:
            path.append(current)
            current = self.sheets[current].parent
            if not current:
                break
        return list(reversed(path))

    def find_lowest_common_ancestor(self, sheet1, sheet2):
        """Find the lowest common ancestor sheet between two sheets."""
        path1 = self.get_sheet_hierarchy_path(sheet1)
        path2 = self.get_sheet_hierarchy_path(sheet2)
        
        # Find common prefix
        common_path = []
        for s1, s2 in zip(path1, path2):
            if s1 == s2:
                common_path.append(s1)
            else:
                break
                
        return common_path[-1] if common_path else None

    def find_optimal_net_origin(self, used_sheets, net_name):
        """
        Determine the optimal sheet to create a net based on hierarchy.
        
        Args:
            used_sheets: Set of sheets where net has component pins
            net_name: Name of net being analyzed
        Returns:
            (origin_sheet, paths_to_children)
        """
        # Single sheet usage - create in that sheet
        if len(used_sheets) == 1:
            return list(used_sheets)[0], []
            
        # Power nets (+3.3V, +5V, GND, Vmotor) belong in Project Architecture
        if any(pwr in net_name for pwr in ['+3.3V', '+5V', 'GND', 'Vmotor']):
            return 'Project Architecture', [list(used_sheets)]
            
        # Get sheet paths
        sheet_paths = {sheet: self.get_sheet_hierarchy_path(sheet) 
                    for sheet in used_sheets}
                    
        # Check if sheets are children of Project Architecture
        if 'Project Architecture' in self.sheets:
            shared_nets = 0
            for sheet in used_sheets:
                path = sheet_paths.get(sheet, [])
                if 'Project Architecture' in path:
                    shared_nets += 1
                    
            # If multiple sheets under Project Architecture share this net,
            # it should be created in Project Architecture
            if shared_nets > 1:
                paths = []
                for sheet in used_sheets:
                    if sheet != 'Project Architecture':
                        path = self.get_path_between_sheets('Project Architecture', sheet)
                        if path:
                            paths.append(path)
                return 'Project Architecture', paths

        # If not in Project Architecture, find lowest common parent
        common_ancestors = None
        for paths in sheet_paths.values():
            if common_ancestors is None:
                common_ancestors = set(paths)
            else:
                common_ancestors &= set(paths)
                
        if common_ancestors:
            lowest = max(common_ancestors, 
                        key=lambda x: max(path.index(x) if x in path else -1 
                                        for path in sheet_paths.values()))
            
            # Build paths from parent to children
            paths = []
            for sheet in used_sheets:
                if sheet != lowest:
                    path = sheet_paths[sheet]
                    start_idx = path.index(lowest)
                    child_path = path[start_idx:]
                    if len(child_path) > 1:
                        paths.append(child_path)
            return lowest, paths
            
        # Default to Project Architecture for multi-sheet nets
        if len(used_sheets) > 1 and 'Project Architecture' in self.sheets:
            return 'Project Architecture', [list(used_sheets)]
            
        return list(used_sheets)[0], []

    def analyze_nets(self):
        """Analyze nets to determine hierarchy and relationships between sheets."""
        print("\n=== Starting Enhanced Net Analysis ===")
        
        # Data structures for analysis
        net_usage = defaultdict(lambda: defaultdict(set))  # net -> sheet -> pins
        net_hierarchy = {}  # net -> {origin_sheet, used_in_sheets, path_to_children}
        
        print("\n1. Mapping Net Usage Across Sheets:")
        # First pass: Build net usage map
        for net in self.netlist.nets:
            print(f"\nAnalyzing net: {net.name}")
            for pin in net.pins:
                for comp in self.netlist.parts:
                    if comp.ref == pin.ref:
                        sheet_name = self.get_sheet_path(comp)
                        if sheet_name:
                            net_usage[net.name][sheet_name].add(f"{comp.ref}.{pin.num}")
                            print(f"  - Used in sheet '{sheet_name}' by pin {comp.ref}.{pin.num}")
        
        print("\n2. Analyzing Net Origins and Hierarchy:")
        # Second pass: Determine net origins and build hierarchy
        for net_name, sheet_usages in net_usage.items():
            print(f"\nNet: {net_name}")
            used_sheets = set(sheet_usages.keys())
            
            # Find optimal origin and paths
            origin_sheet, paths_to_children = self.find_optimal_net_origin(used_sheets, net_name)
            
            net_hierarchy[net_name] = {
                'origin_sheet': origin_sheet,
                'used_in_sheets': used_sheets,
                'path_to_children': paths_to_children
            }
            
            print(f"  - Origin sheet: {origin_sheet}")
            print(f"  - Used in sheets: {used_sheets}")
            print(f"  - Paths to children: {[' -> '.join(path) for path in paths_to_children]}")
        
        # Third pass: Update sheet net classifications
        for sheet in self.sheets.values():
            sheet.local_nets.clear()
            sheet.imported_nets.clear()
            
            print(f"\nSheet: {sheet.name}")
            for net_name, hierarchy in net_hierarchy.items():
                if net_name.startswith('unconnected'):
                    continue
                    
                # If this sheet is the origin, it's a local net
                if hierarchy['origin_sheet'] == sheet.name:
                    sheet.local_nets.add(net_name)
                    print(f"  - Local net: {net_name}")
                    
                # If used in this sheet but originates elsewhere, it's imported
                elif sheet.name in hierarchy['used_in_sheets']:
                    sheet.imported_nets.add(net_name)
                    print(f"  - Imported net: {net_name}")
                    
                # If this sheet is in the path between origin and users, it needs to pass the net
                else:
                    for path in hierarchy['path_to_children']:
                        if sheet.name in path:
                            sheet.imported_nets.add(net_name)
                            print(f"  - Imported net (path): {net_name}")
                            break
        
        # Store the analysis results for use in code generation
        self.net_hierarchy = net_hierarchy
        self.net_usage = net_usage
        
        self._print_net_summary()
        
    def _print_net_summary(self):
        """Print a summary of net analysis results."""
        print("\n=== Net Analysis Complete ===")
        print("\nNet Origin Summary:")
        for net_name, hierarchy in self.net_hierarchy.items():
            if not net_name.startswith('unconnected'):
                print(f"\nNet: {net_name}")
                print(f"  Origin: {hierarchy['origin_sheet']}")
                print(f"  Used in: {hierarchy['used_in_sheets']}")
                if hierarchy['path_to_children']:
                    for path in hierarchy['path_to_children']:
                        print(f"  Path: {' -> '.join(path)}")
    
    def legalize_name(self, name: str, is_filename: bool = False) -> str:
        """Convert any name into a valid Python identifier.
        Handles leading and trailing +/- with _p and _n suffixes/prefixes."""
        # Remove leading slashes and spaces
        name = name.lstrip('/ ')

        # Handle trailing + or - first
        if name.endswith('+'):
            name = name[:-1] + '_p'
        elif name.endswith('-'):
            name = name[:-1] + '_n'
            
        # Handle leading + or -
        if name.startswith('+'):
            name = '_p_' + name[1:]
        elif name.startswith('-'):
            name = '_n_' + name[1:]
            
        # Convert remaining non-alphanumeric chars to underscores
        legalized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        # Ensure it starts with a letter or underscore
        if legalized[0].isdigit():
            legalized = '_' + legalized
            
        return legalized

    def component_to_skidl(self, comp: object) -> str:
        """Convert component to SKiDL instantiation with all properties."""
        ref = comp.ref  # Keep original reference
        props = []
        
        # Basic properties
        props.append(f"'{comp.lib}'")  # Library
        props.append(f"'{comp.name}'")  # Part name
        
        # Add value if present
        if comp.value:
            props.append(f"value='{comp.value}'")
            
        # Add footprint if present
        if comp.footprint:
            props.append(f"footprint='{comp.footprint}'")
            
        # Add description if present
        desc = next((p.value for p in comp.properties if p.name == 'Description'), None)
        if desc:
            props.append(f"description='{desc}'")
            
        # Add tag for reference
        props.append(f"ref='{ref}'")  # Preserve reference designator
            
        # Add all additional properties from netlist as part fields
        extra_fields = {}
        if hasattr(comp, 'properties'):
            for prop in comp.properties:
                if prop.name not in ['Reference', 'Value', 'Footprint', 'Datasheet', 'Description']:
                    extra_fields[prop.name] = prop.value
        if extra_fields:
            props.append(f"fields={repr(extra_fields)}")
            
        # Join all properties
        return f"{self.tab}{self.legalize_name(ref)} = Part({', '.join(props)})\n"

    def net_to_skidl(self, net: object, sheet: Sheet) -> str:
        """Convert net to SKiDL connections."""
        net_name = self.legalize_name(net.name)
        if net_name.startswith('unconnected'):
            return ""
            
        pins = []
        for pin in net.pins:
            if any(comp.ref == pin.ref for comp in sheet.components):
                comp = self.legalize_name(pin.ref)
                pins.append(f"{comp}['{pin.num}']")
                
        if pins:
            return f"{self.tab}{net_name} += {', '.join(pins)}\n"
        return ""

    def generate_sheet_code(self, sheet: Sheet) -> str:
        """Generate SKiDL code for a sheet."""
        code = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n"
        ]
        
        # Import child subcircuits
        for child_path in sheet.children:
            child_sheet = self.sheets[child_path]
            module_name = self.legalize_name(child_sheet.name)
            code.append(f"from {module_name} import {module_name}\n")
        
        code.append("\n@subcircuit\n")
        
        # Function parameters - collect nets that are actually used in this sheet
        used_nets = set()
        
        # Only add nets if the sheet has components or children
        if sheet.components or sheet.children:
            for net in sorted(sheet.imported_nets):
                if not net.startswith('unconnected'):
                    # Check if net is actually used in this sheet
                    if sheet.name in self.net_usage.get(net, {}):
                        used_nets.add(self.legalize_name(net))
            
            # Add local nets if this is not the top level
            if sheet.parent:
                for net in sorted(sheet.local_nets):
                    if not net.startswith('unconnected'):
                        if sheet.name in self.net_usage.get(net, {}):
                            used_nets.add(self.legalize_name(net))

            # Only include GND if it's actually used in this sheet
            if 'GND' in self.net_usage and sheet.name in self.net_usage['GND']:
                used_nets.add('GND')
        
        func_name = self.legalize_name(sheet.name)
        code.append(f"def {func_name}({', '.join(sorted(used_nets))}):\n")
        
        # Components
        if sheet.components:
            code.append(f"{self.tab}# Components\n")
            for comp in sorted(sheet.components, key=lambda x: x.ref):
                code.append(self.component_to_skidl(comp))
            code.append("\n")
        
        # Local nets
        local_nets = sorted(net for net in sheet.local_nets 
                        if not net.startswith('unconnected'))
        if local_nets:
            code.append(f"{self.tab}# Local nets\n")
            for net in local_nets:
                original_name = net
                legal_name = self.legalize_name(original_name)
                code.append(f"{self.tab}{legal_name} = Net('{original_name}')\n")
            code.append("\n")
        
        # Hierarchical subcircuits
        if sheet.children:
            code.append(f"\n{self.tab}# Hierarchical subcircuits\n")
            for child_path in sheet.children:
                child_sheet = self.sheets[child_path]
                child_func_name = self.legalize_name(child_sheet.name)
                child_params = []
                
                # Only pass nets that the child sheet actually uses
                for net in sorted(child_sheet.imported_nets):
                    if not net.startswith('unconnected'):
                        if child_sheet.name in self.net_usage.get(net, {}):
                            child_params.append(self.legalize_name(net))
                
                # Only pass GND if child uses it
                if 'GND' in self.net_usage and child_sheet.name in self.net_usage['GND']:
                    child_params.append('GND')
                
                code.append(f"{self.tab}{child_func_name}({', '.join(child_params)})\n")

        # Connections
        if sheet.components:
            code.append(f"\n{self.tab}# Connections\n")
            for net in self.netlist.nets:
                conn = self.net_to_skidl(net, sheet)
                if conn:
                    code.append(conn)
        
        code.append(f"{self.tab}return\n")
        
        return "".join(code)

    def _update_sheet_net_classifications(self, net_hierarchy):
        """Update sheet net classifications based on hierarchy analysis."""
        print("\n3. Updating Sheet Net Classifications:")
        
        for sheet in self.sheets.values():
            sheet.local_nets.clear()
            sheet.imported_nets.clear()
            
            print(f"\nSheet: {sheet.name}")
            for net_name, hierarchy in net_hierarchy.items():
                if net_name.startswith('unconnected'):
                    continue
                    
                # If this sheet is the origin, it's a local net
                if hierarchy['origin_sheet'] == sheet.name:
                    sheet.local_nets.add(net_name)
                    print(f"  - Local net: {net_name}")
                    
                # If used in this sheet but originates elsewhere, it's imported
                elif sheet.name in hierarchy['used_in_sheets']:
                    sheet.imported_nets.add(net_name)
                    print(f"  - Imported net: {net_name}")
                    
                # If this sheet is in the path for any child, it needs to pass the net
                else:
                    for path in hierarchy['path_to_children']:
                        if sheet.name in path:
                            sheet.imported_nets.add(net_name)
                            print(f"  - Imported net (path): {net_name}")
                            break


    def create_main_file(self, output_dir: str):
        """Create the main.py file."""
        code = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n"
        ]
        
        # Import only top-level modules
        for sheet in self.sheets.values():
            if not sheet.parent and sheet.name != 'main':
                module_name = self.legalize_name(sheet.name)
                code.append(f"from {module_name} import {module_name}\n")
        
        code.extend([
            "\ndef main():\n",
        ])
        
        # Only create GND net if any top-level sheets actually use it
        needs_gnd = False
        for sheet in self.sheets.values():
            if not sheet.parent and sheet.name != 'main':
                if 'GND' in self.net_usage and sheet.name in self.net_usage['GND']:
                    needs_gnd = True
                    break

        if needs_gnd:
            code.append(f"{self.tab}# Create global ground net\n")
            code.append(f"{self.tab}gnd = Net('GND')\n\n")
        
        # Call only top-level subcircuits
        code.append(f"{self.tab}# Create subcircuits\n")
        for sheet in self.get_hierarchical_order():
            if not sheet.parent and sheet.name != 'main':
                func_name = self.legalize_name(sheet.name)
                
                # Only process sheets that have components or children
                if sheet.components or sheet.children:
                    # Only include nets that are actually used in the sheet
                    used_nets = []
                    for net in sorted(sheet.imported_nets):
                        if not net.startswith('unconnected'):
                            if sheet.name in self.net_usage.get(net, {}):
                                used_nets.append(self.legalize_name(net))
                    
                    # Only add GND if sheet actually uses it
                    if 'GND' in self.net_usage and sheet.name in self.net_usage['GND']:
                        used_nets.append('gnd')
                        
                    code.append(f"{self.tab}{func_name}({', '.join(used_nets)})\n")
                else:
                    # Empty sheet with no components or children
                    code.append(f"{self.tab}{func_name}()\n")
        
        code.extend([
            "\nif __name__ == \"__main__\":\n",
            f"{self.tab}main()\n",
            f"{self.tab}generate_netlist()\n"
        ])
        
        main_path = Path(output_dir) / "main.py"
        main_path.write_text("".join(code))

        
    def get_hierarchical_order(self):
        """Return sheets in dependency order."""
        ordered = []
        visited = set()
        
        def process_sheet(sheet, stack=None):
            if stack is None:
                stack = set()
                
            # Detect cycles
            if sheet.path in stack:
                raise ValueError(f"Cyclic dependency detected with sheet: {sheet.path}")
            
            # Skip if already fully processed
            if sheet.path in visited:
                return
                
            stack.add(sheet.path)
            
            # Process hierarchy bottom-up:
            # First process children recursively
            for child_path in sheet.children:
                child_sheet = self.sheets[child_path]
                process_sheet(child_sheet, stack)
            
            # Then add this sheet if not already added
            if sheet.path not in visited:
                ordered.append(sheet)
                visited.add(sheet.path)
                
            stack.remove(sheet.path)
        
        # Start with independent sheets (no parent)
        for sheet in self.sheets.values():
            if not sheet.parent:
                process_sheet(sheet)
                
        return ordered

    def convert(self, output_dir: str = None):
        """Convert netlist to SKiDL files."""
        self.extract_sheet_info()
        self.assign_components_to_sheets()
        self.analyze_nets()
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate all sheet files
            for sheet in self.sheets.values():
                if sheet.name != 'main':
                    filename = self.legalize_name(sheet.name, is_filename=True) + '.py'
                    sheet_path = Path(output_dir) / filename
                    sheet_path.write_text(self.generate_sheet_code(sheet))
                    print(f"Wrote sheet file: {sheet_path}")
            
            # Create main.py last
            self.create_main_file(output_dir)
        else:
            main_sheet = next((s for s in self.sheets.values() if not s.parent), None)
            if main_sheet:
                return self.generate_sheet_code(main_sheet)
            return ""

def netlist_to_skidl(netlist_src: str, output_dir: str = None):
    """Convert a KiCad netlist to SKiDL Python files."""
    converter = HierarchicalConverter(netlist_src)
    return converter.convert(output_dir)
