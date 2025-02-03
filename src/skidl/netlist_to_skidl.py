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

    def find_optimal_net_origin(self, used_sheets, net_name):
        """Determine the sheet where the net should be defined and list paths for child usage."""
        if len(used_sheets) == 1:
            return list(used_sheets)[0], []
        sheet_paths = {sheet: self.get_sheet_hierarchy_path(sheet) for sheet in used_sheets}
        common_path = None
        for path in sheet_paths.values():
            if common_path is None:
                common_path = path
            else:
                new_common = []
                for s1, s2 in zip(common_path, path):
                    if s1 == s2:
                        new_common.append(s1)
                    else:
                        break
                common_path = new_common
        origin_sheet = common_path[-1] if common_path else ''
        paths = []
        for sheet in used_sheets:
            if sheet != origin_sheet:
                path = sheet_paths[sheet]
                try:
                    start_idx = path.index(origin_sheet)
                    child_path = path[start_idx:]
                    if len(child_path) > 1:
                        paths.append(child_path)
                except ValueError:
                    continue
        return origin_sheet, paths

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

    def analyze_nets(self):
        """Analyze net usage to determine, for each net, which sheet is its origin and in which sheets it is used.
        Then classify nets in each sheet as local (defined in the sheet) or imported (to be passed as a parameter)."""
        print("=== Starting Net Analysis ===")
        net_usage = defaultdict(lambda: defaultdict(set))
        print("1. Mapping Net Usage Across Sheets:")
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
        # Now classify nets for each sheet.
        for sheet in self.sheets.values():
            # If a sheet has no parent (i.e. is top-level), we want it to be the net origin for all nets it uses.
            # So we force its imported nets to be empty.
            if sheet.parent is None:
                sheet.imported_nets = set()
            else:
                sheet.local_nets.clear()
                sheet.imported_nets.clear()
                print(f"\nSheet: {sheet.name}")
                for net_name, hierarchy in net_hierarchy.items():
                    if net_name.startswith('unconnected'):
                        continue
                    # If the net originates in this sheet, mark it as local.
                    if hierarchy['origin_sheet'] == sheet.path:
                        sheet.local_nets.add(net_name)
                    # Otherwise, if this sheet uses the net, mark it as imported.
                    elif sheet.path in hierarchy['used_in_sheets']:
                        sheet.imported_nets.add(net_name)
                    else:
                        for path in hierarchy['path_to_children']:
                            if sheet.path in path:
                                sheet.imported_nets.add(net_name)
                                break
        self.net_hierarchy = net_hierarchy
        self.net_usage = net_usage

    def create_main_file(self, output_dir: str):
        """Generate the main.py file. (This file is not itself a subcircuit and will simply call the top‐level subcircuits.)"""
        code = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n"
        ]
        # Import all sheets that are direct children of main (or have parent == 'main').
        for sheet in self.sheets.values():
            if (sheet.parent is None or sheet.parent == 'main') and sheet.name != 'main':
                module_name = self.legalize_name(sheet.name)
                code.append(f"from {module_name} import {module_name}\n")
        code.extend([
            "\n\ndef main():\n",
            f"{self.tab}# Create global nets\n"
        ])
        # Global nets: those whose origin is in main or that are used in more than one top-level sheet.
        top_level_nets = set()
        for net_name, hierarchy in self.net_hierarchy.items():
            if net_name.startswith('unconnected'):
                continue
            # A net is global if its origin is main or if it is used in more than one sheet with no parent.
            top_usage = [s for s in hierarchy['used_in_sheets'] if (self.sheets[s].parent is None or self.sheets[s].parent=='main')]
            if hierarchy['origin_sheet'] == "main" or len(top_usage) > 1:
                top_level_nets.add(net_name)
        if top_level_nets:
            for net_name in sorted(top_level_nets):
                legal_name = self.legalize_name(net_name)
                code.append(f"{self.tab}{legal_name} = Net('{net_name}')\n")
            code.append("\n")
        # Call each top-level subcircuit unconditionally.
        code.append(f"{self.tab}# Create subcircuits\n")
        for sheet in self.get_hierarchical_order():
            if sheet.name == 'main':
                continue
            if sheet.parent is None or sheet.parent == 'main':
                func_name = self.legalize_name(sheet.name)
                # For top-level sheets, we assume all nets are defined locally so no parameters are passed.
                code.append(f"{self.tab}{func_name}()\n")
        # Do not insert a recursive call to main().
        code.extend([
            "\nif __name__ == \"__main__\":\n",
            f"{self.tab}main()\n",
            f"{self.tab}generate_netlist()\n"
        ])
        main_path = Path(output_dir) / "main.py"
        main_path.write_text("".join(code))

    def generate_sheet_code(self, sheet: Sheet) -> str:
        """Generate the SKiDL code for a given sheet."""
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
        # Determine required nets: nets used in this sheet but not defined here.
        required_nets = set()
        for net_name, hierarchy in self.net_hierarchy.items():
            if net_name.startswith('unconnected'):
                continue
            # If the net is used in the sheet and it does not originate here,
            # then it should be passed in.
            if sheet.path in hierarchy['used_in_sheets'] and hierarchy['origin_sheet'] != sheet.path:
                required_nets.add(net_name)
            else:
                for path in hierarchy['path_to_children']:
                    if sheet.path in path:
                        required_nets.add(net_name)
                        break
        params = [self.legalize_name(net) for net in sorted(required_nets)]
        func_name = self.legalize_name(sheet.name)
        code.append(f"def {func_name}({', '.join(params)}):\n")
        # Create local nets (nets whose origin is in this sheet).
        local_nets = []
        for net_name, hierarchy in self.net_hierarchy.items():
            if net_name.startswith('unconnected'):
                continue
            if hierarchy['origin_sheet'] == sheet.path:
                local_nets.append(net_name)
        if local_nets:
            code.append(f"{self.tab}# Local nets\n")
            for net in sorted(local_nets):
                legal_name = self.legalize_name(net)
                code.append(f"{self.tab}{legal_name} = Net('{net}')\n")
            code.append("\n")
        # Insert component instantiations.
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
                # Determine parameters for the child subcircuit by collecting nets
                child_nets = []
                for net_name, hierarchy in self.net_hierarchy.items():
                    if net_name.startswith('unconnected'):
                        continue
                    if child_sheet.path in hierarchy['used_in_sheets'] and hierarchy['origin_sheet'] != child_sheet.path:
                        child_nets.append(net_name)
                    else:
                        for path in hierarchy['path_to_children']:
                            if child_sheet.path in path:
                                child_nets.append(net_name)
                                break
                child_params = [self.legalize_name(net) for net in sorted(set(child_nets))]
                code.append(f"{self.tab}{child_func_name}({', '.join(child_params)})\n")
        # Insert connections.
        if sheet.components:
            code.append(f"\n{self.tab}# Connections\n")
            for net in self.netlist.nets:
                conn = self.net_to_skidl(net, sheet)
                if conn:
                    code.append(conn)
        code.append(f"{self.tab}return\n")
        return "".join(code)

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
