# -*- coding: utf-8 -*-

"""
Convert a KiCad netlist into equivalent hierarchical SKiDL programs.
"""

import re
import os
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Set
from kinparse import parse_netlist
# Removed logger import

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
        """Return the sheet name from the component properties."""
        if isinstance(comp.properties, dict):
            return comp.properties.get('Sheetname', '')
        sheet_prop = next((p for p in comp.properties if p.name == 'Sheetname'), None)
        return sheet_prop.value.strip() if sheet_prop else ''

    def get_sheet_hierarchy_path(self, sheet_name):
        """Return a list representing the hierarchy from root to the given sheet."""
        path = []
        current = sheet_name
        while current in self.sheets:
            path.append(current)
            current = self.sheets[current].parent
            if not current:
                break
        return list(reversed(path))

    def find_lowest_common_ancestor(self, sheet1, sheet2):
        """Return the lowest common ancestor (LCA) of two sheets."""
        path1 = self.get_sheet_hierarchy_path(sheet1)
        path2 = self.get_sheet_hierarchy_path(sheet2)
        common_path = []
        for s1, s2 in zip(path1, path2):
            if s1 == s2:
                common_path.append(s1)
            else:
                break
        return common_path[-1] if common_path else None

    def legalize_name(self, name: str, is_filename: bool = False) -> str:
        """Return a version of name that is a legal Python identifier."""
        name = name.lstrip('/ ')
        if name.endswith('+'):
            name = name[:-1] + '_p'
        elif name.endswith('-'):
            name = name[:-1] + '_n'
        if name.startswith('+'):
            name = '_p_' + name[1:]
        elif name.startswith('-'):
            name = '_n_' + name[1:]
        legalized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        if legalized and legalized[0].isdigit():
            legalized = '_' + legalized
        return legalized

    def component_to_skidl(self, comp: object) -> str:
        """Return a SKiDL instantiation string for a component."""
        ref = comp.ref
        props = []
        props.append(f"'{comp.lib}'")
        props.append(f"'{comp.name}'")
        if comp.value:
            props.append(f"value='{comp.value}'")
        if comp.footprint:
            props.append(f"footprint='{comp.footprint}'")
        desc = next((p.value for p in comp.properties if p.name == 'Description'), None)
        if desc:
            props.append(f"description='{desc}'")
        props.append(f"ref='{ref}'")
        extra_fields = {}
        if hasattr(comp, 'properties'):
            for prop in comp.properties:
                if prop.name not in ['Reference', 'Value', 'Footprint', 'Datasheet', 'Description']:
                    extra_fields[prop.name] = prop.value
        if extra_fields:
            props.append(f"fields={repr(extra_fields)}")
        return f"{self.tab}{self.legalize_name(ref)} = Part({', '.join(props)})\n"

    def net_to_skidl(self, net: object, sheet: Sheet) -> str:
        """Return a SKiDL connection string for a net within a given sheet."""
        net_name = self.legalize_name(net.name)
        if net_name.startswith('unconnected'):
            return ""
        pins = []
        for pin in net.pins:
            if any(comp.ref == pin.ref for comp in sheet.components):
                comp_name = self.legalize_name(pin.ref)
                pins.append(f"{comp_name}['{pin.num}']")
        if pins:
            return f"{self.tab}{net_name} += {', '.join(pins)}\n"
        return ""


    def extract_sheet_info(self):
        """Populate self.sheets with Sheet objects built from the netlist."""
        print("=== Extracting Sheet Info ===")
        self.sheet_name_to_path = {}
        for sheet in self.netlist.sheets:
            original_name = sheet.name.strip('/')
            if not original_name:
                original_name = "main"
            name = original_name.split('/')[-1]
            if '/' in original_name:
                parent = '/'.join(original_name.split('/')[:-1])
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
            self.sheet_name_to_path[name] = original_name
            print(f"  Found sheet: original_name='{original_name}', final='{name}', parent='{parent}'")
            
        # Set up parent-child relationships
        for sheet in self.sheets.values():
            if sheet.parent:
                parent_sheet = self.sheets.get(sheet.parent)
                if parent_sheet:
                    parent_sheet.children.append(sheet.path)
                else:
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

        print("=== Completed extracting sheet info ===")
        for sheet_path, sheet in self.sheets.items():
            print(f"   sheet path='{sheet_path}', parent='{sheet.parent}', children={sheet.children}")
            
    def is_descendant(self, potential_child, ancestor):
        """Check if one sheet is a descendant of another in the hierarchy."""
        current = potential_child
        while current in self.sheets:
            if current == ancestor:
                return True
            current = self.sheets[current].parent
        return False

    def assign_components_to_sheets(self):
        """Assign each component from the netlist to its appropriate sheet."""
        print("=== Assigning Components to Sheets ===")
        unassigned_components = []
        sheet_not_found = set()
        for comp in self.netlist.parts:
            sheet_name = self.get_sheet_path(comp)
            if sheet_name:
                sheet_found = False
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
            print(f"WARNING: Sheets not found in netlist: {sorted(sheet_not_found)}")
            print("WARNING: Components in these sheets will be assigned to root level")
        if unassigned_components:
            print(f"WARNING: Found {len(unassigned_components)} unassigned components")
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


    def create_main_file(self, output_dir: str):
        """Generate the main.py file that creates nets and calls subcircuits."""
        code = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n"
        ]

        # Import all sheets that are direct children of main
        for sheet in self.sheets.values():
            if (sheet.parent is None or sheet.parent == 'main') and sheet.name != 'main':
                module_name = self.legalize_name(sheet.name)
                code.append(f"from {module_name} import {module_name}\n")

        code.extend([
            "\n\ndef main():\n",
            f"{self.tab}# Create global nets\n"
        ])

        # Collect nets that need to be created at top level
        global_nets = set()
        for net_name, hierarchy in self.net_hierarchy.items():
            if net_name.startswith('unconnected'):
                continue
            # A net is global if it's used in multiple top-level sheets
            # or if main is determined to be its origin
            if hierarchy['origin_sheet'] == 'main' or len([s for s in hierarchy['used_in_sheets'] 
                        if (self.sheets[s].parent is None or self.sheets[s].parent=='main')]) > 1:
                global_nets.add(net_name)

        # Create nets at top level
        for net_name in sorted(global_nets):
            legal_name = self.legalize_name(net_name)
            code.append(f"{self.tab}{legal_name} = Net('{net_name}')\n")

        # Call each subcircuit with its required nets
        code.append(f"\n{self.tab}# Create subcircuits\n")
        for sheet in self.get_hierarchical_order():
            if sheet.name == 'main':
                continue
            if sheet.parent is None or sheet.parent == 'main':
                func_name = self.legalize_name(sheet.name)
                
                # Get list of nets this sheet imports (needs passed in)
                params = []
                for net_name in sorted(sheet.imported_nets):
                    params.append(self.legalize_name(net_name))
                
                # Call subcircuit function with required nets
                param_str = ', '.join(params)
                code.append(f"{self.tab}{func_name}({param_str})\n")

        # Add boilerplate
        code.extend([
            "\nif __name__ == \"__main__\":\n",
            f"{self.tab}main()\n",
            f"{self.tab}generate_netlist()\n"
        ])

        # Write the file
        main_path = Path(output_dir) / "main.py"
        main_path.write_text("".join(code))
        
    def find_optimal_net_origin(self, used_sheets, net_name):
        """Determine the sheet where the net should be defined and list paths for child usage.
        
        Args:
            used_sheets: Set of sheet paths where the net is used
            net_name: Name of the net being analyzed
            
        Returns:
            Tuple of (origin_sheet, paths_to_children) where:
            - origin_sheet is the sheet path where the net should be defined
            - paths_to_children is a list of paths showing how the net flows to child sheets
        """
        if len(used_sheets) == 1:
            return list(used_sheets)[0], []
            
        # Get hierarchy paths for all sheets using this net
        sheet_paths = {sheet: self.get_sheet_hierarchy_path(sheet) for sheet in used_sheets}
        
        # Find sheets that could "own" the net by containing all its usage
        origin_candidates = set()
        for sheet in used_sheets:
            # Get all sheets that use this net below current sheet in hierarchy
            child_usage = {s for s in used_sheets 
                        if any(sheet == p for p in sheet_paths[s])}
            if len(child_usage) == len(used_sheets):
                origin_candidates.add(sheet)
                
        # If we found candidate owners, pick the most specific (deepest) one
        if origin_candidates:
            max_depth = 0
            lowest_common = None
            for candidate in origin_candidates:
                depth = len(sheet_paths[candidate])
                if depth > max_depth:
                    max_depth = depth 
                    lowest_common = candidate
        else:
            # Fall back to basic lowest common ancestor
            common_prefix = []
            first_path = sheet_paths[list(used_sheets)[0]]
            for i in range(len(first_path)):
                if all(len(p) > i and p[i] == first_path[i] 
                    for p in sheet_paths.values()):
                    common_prefix.append(first_path[i])
                else:
                    break
            lowest_common = common_prefix[-1] if common_prefix else 'main'

        # Generate paths from origin to sheets that need the net
        paths = []
        for sheet in used_sheets:
            if sheet != lowest_common:
                path = sheet_paths[sheet]
                try:
                    start_idx = path.index(lowest_common)
                    child_path = path[start_idx:]
                    if len(child_path) > 1:
                        paths.append(child_path)
                except ValueError:
                    continue

        return lowest_common, paths

    def analyze_nets(self):
        """Analyze net usage to determine origins and required connections."""
        print("=== Starting Net Analysis ===")
        net_usage = defaultdict(lambda: defaultdict(set))
        
        print("1. Mapping Net Usage Across Sheets:")
        # Map which nets are used in which sheets
        for net in self.netlist.nets:
            print(f"\nAnalyzing net: {net.name}")
            for pin in net.pins:
                for comp in self.netlist.parts:
                    if comp.ref == pin.ref:
                        sheet_name = self.get_sheet_path(comp)
                        if sheet_name:
                            sheet_path = self.sheet_name_to_path.get(sheet_name)
                            if sheet_path:
                                net_usage[net.name][sheet_path].add(f"{comp.ref}.{pin.num}")
                                print(f"  - Used in sheet '{sheet_name}' by pin {comp.ref}.{pin.num}")

        print("2. Analyzing Net Origins and Hierarchy:")
        net_hierarchy = {}
        for net_name, sheet_usages in net_usage.items():
            print(f"\nNet: {net_name}")
            used_sheets = set(sheet_usages.keys())
            origin_sheet, paths_to_children = self.find_optimal_net_origin(used_sheets, net_name)
            net_hierarchy[net_name] = {
                'origin_sheet': origin_sheet,
                'used_in_sheets': used_sheets,
                'path_to_children': paths_to_children
            }
            print(f"  - Origin sheet: {origin_sheet}")
            print(f"  - Used in sheets: {used_sheets}")
            print(f"  - Paths to children: {[' -> '.join(path) for path in paths_to_children]}")

        print("3. Classifying local vs imported nets:")
        # Clear any existing net classifications
        for sheet in self.sheets.values():
            sheet.local_nets.clear()
            sheet.imported_nets.clear()
        
        # Process each sheet
        for sheet_path, sheet in self.sheets.items():
            print(f"  Checking sheet: '{sheet.name}', path='{sheet_path}' with parent='{sheet.parent}'")
            
            # Top level sheet doesn't import nets
            if sheet.parent is None:
                print(f"  Top-level sheet: '{sheet_path}' => clearing imported_nets.")
                continue
                
            for net_name, hierarchy in net_hierarchy.items():
                if net_name.startswith('unconnected'):
                    continue
                    
                # Skip nets not used in or below this sheet
                if sheet_path not in hierarchy['used_in_sheets'] and \
                not any(sheet_path in path for path in hierarchy['path_to_children']):
                    continue
                    
                # Determine if net should be local or imported
                is_local = False
                
                # Net originates in this sheet
                if hierarchy['origin_sheet'] == sheet_path:
                    is_local = True
                    
                # Net is only used within this sheet's hierarchy
                elif all(self.is_descendant(used_sheet, sheet_path) 
                        for used_sheet in hierarchy['used_in_sheets']):
                    is_local = True
                    
                # Handle special case nets (like power/ground) that need to flow down
                elif any(sheet_path in path for path in hierarchy['path_to_children']):
                    is_local = False
                    
                if is_local:
                    sheet.local_nets.add(net_name)
                    print(f"    Net {net_name} is local (origin in this sheet).")
                else:
                    sheet.imported_nets.add(net_name)
                    print(f"    Net {net_name} is imported here.")

        self.net_hierarchy = net_hierarchy
        self.net_usage = net_usage
        print("=== Completed net analysis ===")
        
        # Print summary for each sheet
        for sheet_path, sheet in self.sheets.items():
            print(f"Sheet '{sheet_path}': local_nets={sheet.local_nets}, imported_nets={sheet.imported_nets}")

    def generate_sheet_code(self, sheet: Sheet) -> str:
        """Generate the SKiDL code for a given sheet."""
        print(f"=== generate_sheet_code for sheet '{sheet.name}' ===")
        
        code = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n"
        ]
        
        # Import child subcircuits
        for child_path in sheet.children:
            child_sheet = self.sheets[child_path]
            module_name = self.legalize_name(child_sheet.name)
            code.append(f"from {module_name} import {module_name}\n")
        
        # Start function definition
        code.append("\n@subcircuit\n")
        
        # Determine required nets that need to be passed in
        required_nets = []
        for net_name in sorted(sheet.imported_nets):
            # Verify net really needs to be imported 
            # (used by this sheet or needed by children)
            if (sheet.path in self.net_usage[net_name] or 
                any(child in self.net_usage[net_name] 
                    for child in sheet.children)):
                required_nets.append(self.legalize_name(net_name))
        
        func_name = self.legalize_name(sheet.name)
        code.append(f"def {func_name}({', '.join(required_nets)}):\n")
        
        # Create local nets
        local_nets = sorted(sheet.local_nets)
        if local_nets:
            code.append(f"{self.tab}# Local nets\n")
            for net in local_nets:
                legal_name = self.legalize_name(net)
                code.append(f"{self.tab}{legal_name} = Net('{net}')\n")
            code.append("\n")
        
        # Create components
        if sheet.components:
            code.append(f"{self.tab}# Components\n")
            for comp in sorted(sheet.components, key=lambda x: x.ref):
                code.append(self.component_to_skidl(comp))
            code.append("\n")
        
        # Create subcircuits
        if sheet.children:
            code.append(f"{self.tab}# Hierarchical subcircuits\n")
            for child_path in sheet.children:
                child = self.sheets[child_path]
                child_func = self.legalize_name(child.name)
                
                # Determine which nets to pass to child
                child_params = []
                for net_name in sorted(child.imported_nets):
                    if (child_path in self.net_usage[net_name] or
                        any(grandchild in self.net_usage[net_name] 
                            for grandchild in child.children)):
                        child_params.append(self.legalize_name(net_name))
                
                code.append(f"{self.tab}{child_func}({', '.join(child_params)})\n")
        
        # Create connections
        if sheet.components:
            code.append(f"\n{self.tab}# Connections\n")
            for net in self.netlist.nets:
                conn = self.net_to_skidl(net, sheet)
                if conn:
                    code.append(conn)
        
        code.append(f"{self.tab}return\n")
        
        generated_code = "".join(code)
        print(f"Generated code for sheet '{sheet.name}':\n{generated_code}")
        return generated_code

    def get_hierarchical_order(self):
        """Return the sheets in dependency order (children processed before their parents)."""
        ordered = []
        visited = set()

        def process_sheet(sheet, stack=None):
            if stack is None:
                stack = set()
            if sheet.path in stack:
                raise ValueError(f"Cyclic dependency detected with sheet: {sheet.path}")
            if sheet.path in visited:
                return
            stack.add(sheet.path)
            for child_path in sheet.children:
                child_sheet = self.sheets[child_path]
                process_sheet(child_sheet, stack)
            if sheet.path not in visited:
                ordered.append(sheet)
                visited.add(sheet.path)
            stack.remove(sheet.path)

        for sheet in self.sheets.values():
            if not sheet.parent:
                process_sheet(sheet)
        return ordered

    def convert(self, output_dir: str = None):
        """Run the complete conversion and write files if output_dir is provided."""
        self.extract_sheet_info()
        self.assign_components_to_sheets()
        self.analyze_nets()
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Generating files in {output_dir}")
            for sheet in self.sheets.values():
                if sheet.name != 'main':
                    filename = self.legalize_name(sheet.name, is_filename=True) + '.py'
                    sheet_path = Path(output_dir) / filename
                    sheet_path.write_text(self.generate_sheet_code(sheet))
                    print(f"Created sheet file: {sheet_path}")
            self.create_main_file(output_dir)
            print("Conversion completed successfully")
        else:
            main_sheet = next((s for s in self.sheets.values() if not s.parent), None)
            if main_sheet:
                return self.generate_sheet_code(main_sheet)
            return ""

def netlist_to_skidl(netlist_src: str, output_dir: str = None):
    """Convert a KiCad netlist to hierarchical SKiDL Python files."""
    converter = HierarchicalConverter(netlist_src)
    return converter.convert(output_dir)
