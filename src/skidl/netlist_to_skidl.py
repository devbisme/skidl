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
from .logger import active_logger

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


    def get_sheet_path(self, comp):
        """Get sheet path from component properties."""
        if isinstance(comp.properties, dict):
            return comp.properties.get('Sheetname', '')
        sheet_prop = next((p for p in comp.properties if p.name == 'Sheetname'), None)
        # Preserve exact sheet name with spaces 
        return sheet_prop.value.strip() if sheet_prop else ''

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


    def legalize_name(self, name: str, is_filename: bool = False) -> str:
        """Convert any name into a valid Python identifier."""
        # Remove leading slashes and spaces
        name = name.lstrip('/ ')

        # Handle trailing + or -
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

    def find_optimal_net_origin(self, used_sheets, net_name):
        """
        Determine the optimal sheet to create a net based on hierarchy.
        Returns (origin_sheet, paths_to_children) where:
            - origin_sheet is the sheet where the net should be defined
            - paths_to_children are the paths for passing the net to child sheets
        """
        # If net is only used in one sheet, create it there
        if len(used_sheets) == 1:
            return list(used_sheets)[0], []
                
        # Get sheet paths for all usage points
        sheet_paths = {sheet: self.get_sheet_hierarchy_path(sheet) 
                    for sheet in used_sheets}
        
        # Find the lowest common ancestor that is also in the used_sheets
        common_path = None
        for path in sheet_paths.values():
            if common_path is None:
                common_path = path
            else:
                # Find common prefix
                new_common = []
                for s1, s2 in zip(common_path, path):
                    if s1 == s2:
                        new_common.append(s1)
                    else:
                        break
                common_path = new_common

        # Get the shallowest sheet that actually uses this net
        origin_sheet = common_path[-1] if common_path else ''
            
        # Build paths from origin to children that use this net
        paths = []
        for sheet in used_sheets:
            if sheet != origin_sheet:
                path = sheet_paths[sheet]
                try:
                    start_idx = path.index(origin_sheet)
                    child_path = path[start_idx:]
                    if len(child_path) > 1:  # Only add if there's a path to traverse
                        paths.append(child_path)
                except ValueError:
                    continue
                        
        return origin_sheet, paths

    def extract_sheet_info(self):
        """Build sheet hierarchy from netlist."""
        active_logger.info("=== Extracting Sheet Info ===")
        
        # Create name-to-path mapping for sheet lookup.
        self.sheet_name_to_path = {}
        
        # First pass: Create all sheets.
        for sheet in self.netlist.sheets:
            # Strip leading/trailing slashes.
            original_name = sheet.name.strip('/')
            # If empty, then use "main".
            if not original_name:
                original_name = "main"
            # Use the last element as the local name.
            name = original_name.split('/')[-1]
            # Determine the parent based on hierarchy.
            # If there is a '/' in the original name, then parent is everything before the last slash.
            # Otherwise, if this sheet is not "main", force its parent to be "main".
            if '/' in original_name:
                parent = '/'.join(original_name.split('/')[:-1])
                # If parent becomes empty, set to main.
                if not parent:
                    parent = "main"
            else:
                parent = "main" if name != "main" else None
            
            self.sheets[original_name] = Sheet(
                number=sheet.number,
                name=name,
                path=original_name,
                components=[],
                local_nets=set(),
                imported_nets=set(),
                parent=parent,
                children=[]
            )
            
            # Store mapping from local name to full hierarchical path.
            self.sheet_name_to_path[name] = original_name

        # Second pass: Build parent-child relationships.
        for sheet in self.sheets.values():
            if sheet.parent:
                parent_sheet = self.sheets.get(sheet.parent)
                if parent_sheet:
                    parent_sheet.children.append(sheet.path)
                else:
                    # In case the parent sheet doesn't exist in our mapping, we create a root.
                    root = self.sheets.get("main")
                    if not root:
                        root = Sheet(
                            number='0',
                            name='main',
                            path='main',
                            components=[],
                            local_nets=set(),
                            imported_nets=set()
                        )
                        self.sheets["main"] = root
                    sheet.parent = "main"
                    root.children.append(sheet.path)

    def assign_components_to_sheets(self):
        """Assign components to their respective sheets."""
        active_logger.info("=== Assigning Components to Sheets ===")
        unassigned_components = []
        sheet_not_found = set()
        
        for comp in self.netlist.parts:
            sheet_name = self.get_sheet_path(comp)
            if sheet_name:
                sheet_found = False
                # Try to match against the sheet's local name
                for path, sheet in self.sheets.items():
                    if sheet_name == sheet.name:
                        sheet.components.append(comp)
                        sheet_found = True
                        break
                if not sheet_found:
                    sheet_not_found.add(sheet_name)
                    unassigned_components.append(comp)
            else:
                unassigned_components.append(comp)
        
        if sheet_not_found:
            active_logger.warning(f"Sheets not found in netlist: {sorted(sheet_not_found)}")
            active_logger.warning("Components in these sheets will be assigned to root level")
        
        if unassigned_components:
            active_logger.warning(f"Found {len(unassigned_components)} unassigned components")
            root = self.sheets.get("main", None)
            if not root:
                root = Sheet(
                    number='0',
                    name='main',
                    path='main',
                    components=[],
                    local_nets=set(),
                    imported_nets=set()
                )
                self.sheets["main"] = root
            root.components.extend(unassigned_components)

    def analyze_nets(self):
        """Analyze nets to determine hierarchy and relationships between sheets."""
        active_logger.info("=== Starting Net Analysis ===")
        
        # Map net usage: net_name -> { sheet_path: set(pins) }
        net_usage = defaultdict(lambda: defaultdict(set))
        
        active_logger.info("1. Mapping Net Usage Across Sheets:")
        for net in self.netlist.nets:
            active_logger.debug(f"\nAnalyzing net: {net.name}")
            for pin in net.pins:
                for comp in self.netlist.parts:
                    if comp.ref == pin.ref:
                        sheet_name = self.get_sheet_path(comp)
                        if sheet_name:
                            sheet_path = self.sheet_name_to_path.get(sheet_name)
                            if sheet_path:
                                net_usage[net.name][sheet_path].add(f"{comp.ref}.{pin.num}")
                                active_logger.debug(f"  - Used in sheet '{sheet_name}' by pin {comp.ref}.{pin.num}")
                            else:
                                active_logger.warning(f"Sheet not found for component {comp.ref}: {sheet_name}")
        
        active_logger.info("2. Analyzing Net Origins and Hierarchy:")
        net_hierarchy = {}
        for net_name, sheet_usages in net_usage.items():
            active_logger.debug(f"\nNet: {net_name}")
            used_sheets = set(sheet_usages.keys())
            
            # Determine optimal origin by finding the lowest common ancestor among all sheets that use this net.
            origin_sheet, paths_to_children = self.find_optimal_net_origin(used_sheets, net_name)
            
            net_hierarchy[net_name] = {
                'origin_sheet': origin_sheet,
                'used_in_sheets': used_sheets,
                'path_to_children': paths_to_children
            }
            
            active_logger.debug(f"  - Origin sheet: {origin_sheet}")
            active_logger.debug(f"  - Used in sheets: {used_sheets}")
            active_logger.debug(f"  - Paths to children: {[' -> '.join(path) for path in paths_to_children]}")
        
        # Third pass: Classify nets for each sheet.
        for sheet in self.sheets.values():
            sheet.local_nets.clear()
            sheet.imported_nets.clear()
            
            active_logger.debug(f"\nSheet: {sheet.name}")
            for net_name, hierarchy in net_hierarchy.items():
                if net_name.startswith('unconnected'):
                    continue
                
                # If this sheet is the origin, mark net as local.
                if hierarchy['origin_sheet'] == sheet.path:
                    sheet.local_nets.add(net_name)
                    active_logger.debug(f"  - Local net: {net_name}")
                # If this sheet is among those that use the net but not the origin, mark it as imported.
                elif sheet.path in hierarchy['used_in_sheets']:
                    sheet.imported_nets.add(net_name)
                    active_logger.debug(f"  - Imported net: {net_name}")
                else:
                    for path in hierarchy['path_to_children']:
                        if sheet.path in path:
                            sheet.imported_nets.add(net_name)
                            active_logger.debug(f"  - Imported net (path): {net_name}")
                            break

        self.net_hierarchy = net_hierarchy
        self.net_usage = net_usage

    def create_main_file(self, output_dir: str):
        """Create the main.py file."""
        code = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n"
        ]
        
        # Import only top-level modules (those with no parent except main itself).
        for sheet in self.sheets.values():
            if (not sheet.parent) and sheet.name != 'main':
                module_name = self.legalize_name(sheet.name)
                code.append(f"from {module_name} import {module_name}\n")
        
        code.extend([
            "\ndef main():\n",
        ])
        
        # Build a set of top-level nets.
        top_level_nets = set()
        for net_name, hierarchy in self.net_hierarchy.items():
            if net_name.startswith('unconnected'):
                continue
            # If the net originates in "main" or is used across multiple top-level sheets,
            # mark it as global.
            if (hierarchy['origin_sheet'] == "main" or 
                len([s for s in hierarchy['used_in_sheets'] if not self.sheets[s].parent]) > 1):
                top_level_nets.add(net_name)
        
        if top_level_nets:
            code.append(f"{self.tab}# Create global nets\n")
            for net_name in sorted(top_level_nets):
                legal_name = self.legalize_name(net_name)
                code.append(f"{self.tab}{legal_name} = Net('{net_name}')\n")
            code.append("\n")
        
        # Call top-level subcircuits.
        code.append(f"{self.tab}# Create subcircuits\n")
        for sheet in self.get_hierarchical_order():
            # Only call subcircuits that are top-level (or have no parent) and are not "main" itself.
            if not sheet.parent and sheet.name != 'main':
                func_name = self.legalize_name(sheet.name)
                needed_nets = []
                for net_name in sorted(sheet.imported_nets):
                    if not net_name.startswith('unconnected'):
                        # Verify that the net is indeed used in the sheet or its children.
                        sheet_path = self.get_sheet_hierarchy_path(sheet.path)
                        net_usage_sheets = self.net_usage.get(net_name, {})
                        if any(usage_sheet in sheet_path for usage_sheet in net_usage_sheets):
                            needed_nets.append(self.legalize_name(net_name))
                code.append(f"{self.tab}{func_name}({', '.join(needed_nets)})\n")
            else:
                code.append(f"{self.tab}{self.legalize_name(sheet.name)}()\n")
        
        code.extend([
            "\nif __name__ == \"__main__\":\n",
            f"{self.tab}main()\n",
            f"{self.tab}generate_netlist()\n"
        ])
        
        main_path = Path(output_dir) / "main.py"
        main_path.write_text("".join(code))

    def generate_sheet_code(self, sheet: Sheet) -> str:
        """Generate SKiDL code for a sheet."""
        code = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n"
        ]
        
        # Import child subcircuits.
        for child_path in sheet.children:
            child_sheet = self.sheets[child_path]
            module_name = self.legalize_name(child_sheet.name)
            code.append(f"from {module_name} import {module_name}\n")
        
        code.append("\n@subcircuit\n")
        
        # Determine required nets: these are nets used in this sheet but not created locally.
        required_nets = set()
        for net_name, hierarchy in self.net_hierarchy.items():
            if net_name.startswith('unconnected'):
                continue
            origin = hierarchy['origin_sheet']
            if sheet.path in hierarchy['used_in_sheets'] and origin != sheet.path:
                required_nets.add(net_name)
            else:
                # Also check if any path from the origin to a child of this sheet passes through this sheet.
                for path in hierarchy['path_to_children']:
                    if sheet.path in path:
                        required_nets.add(net_name)
                        break
        
        # Legalize and sort parameter names.
        params = [self.legalize_name(net) for net in sorted(required_nets)]
        func_name = self.legalize_name(sheet.name)
        code.append(f"def {func_name}({', '.join(params)}):\n")
        
        # Create local nets: nets for which this sheet is the origin.
        local_nets = []
        for net_name, hierarchy in self.net_hierarchy.items():
            if (not net_name.startswith('unconnected') and 
                hierarchy['origin_sheet'] == sheet.path):
                local_nets.append(net_name)
        
        if local_nets:
            code.append(f"{self.tab}# Local nets\n")
            for net in sorted(local_nets):
                legal_name = self.legalize_name(net)
                code.append(f"{self.tab}{legal_name} = Net('{net}')\n")
            code.append("\n")
        
        # Components section.
        if sheet.components:
            code.append(f"{self.tab}# Components\n")
            for comp in sorted(sheet.components, key=lambda x: x.ref):
                code.append(self.component_to_skidl(comp))
            code.append("\n")
        
        # Call child subcircuits.
        if sheet.children:
            code.append(f"{self.tab}# Hierarchical subcircuits\n")
            for child_path in sheet.children:
                child_sheet = self.sheets[child_path]
                child_func_name = self.legalize_name(child_sheet.name)
                child_nets = []
                for net_name, hierarchy in self.net_hierarchy.items():
                    if net_name.startswith('unconnected'):
                        continue
                    origin = hierarchy['origin_sheet']
                    if child_sheet.path in hierarchy['used_in_sheets']:
                        sheet_path = self.get_sheet_hierarchy_path(sheet.path)
                        if origin in sheet_path:
                            child_nets.append(net_name)
                    for path in hierarchy['path_to_children']:
                        if child_sheet.path in path and sheet.path == origin:
                            child_nets.append(net_name)
                child_params = [self.legalize_name(net) for net in sorted(set(child_nets))]
                code.append(f"{self.tab}{child_func_name}({', '.join(child_params)})\n")
        
        # Connections.
        if sheet.components:
            code.append(f"\n{self.tab}# Connections\n")
            for net in self.netlist.nets:
                conn = self.net_to_skidl(net, sheet)
                if conn:
                    code.append(conn)
        
        code.append(f"{self.tab}return\n")
        
        return "".join(code)


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
            active_logger.info(f"Generating files in {output_dir}")
            
            # Generate all sheet files
            for sheet in self.sheets.values():
                if sheet.name != 'main':
                    filename = self.legalize_name(sheet.name, is_filename=True) + '.py'
                    sheet_path = Path(output_dir) / filename
                    sheet_path.write_text(self.generate_sheet_code(sheet))
                    active_logger.debug(f"Created sheet file: {sheet_path}")
            
            # Create main.py last
            self.create_main_file(output_dir)
            active_logger.info("Conversion completed successfully")
        else:
            main_sheet = next((s for s in self.sheets.values() if not s.parent), None)
            if main_sheet:
                return self.generate_sheet_code(main_sheet)
            return ""


def netlist_to_skidl(netlist_src: str, output_dir: str = None):
    """Convert a KiCad netlist to SKiDL Python files."""
    converter = HierarchicalConverter(netlist_src)
    return converter.convert(output_dir)