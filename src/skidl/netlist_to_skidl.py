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

    def analyze_nets(self):
        """Analyze nets to determine which are local vs imported for each sheet."""
        print("\n=== Analyzing Nets ===")
        # First pass: Group pins by sheet
        net_sheet_map = defaultdict(lambda: defaultdict(list))
        for net in self.netlist.nets:
            for pin in net.pins:
                for comp in self.netlist.parts:
                    if comp.ref == pin.ref:
                        sheet_name = self.get_sheet_path(comp)
                        if sheet_name:
                            net_sheet_map[net.name][sheet_name].append(pin)
                            break

        # Second pass: Determine net locality
        for net_name, sheet_pins in net_sheet_map.items():
            # Store original net names in the sets
            sheets_using_net = set(sheet_pins.keys())
            
            for sheet in self.sheets.values():
                if sheet.name in sheets_using_net:
                    if len(sheets_using_net) > 1:
                        sheet.imported_nets.add(net_name)  # Store original name
                    else:
                        sheet.local_nets.add(net_name)  # Store original name

                    # If sheet has children, add net to imported_nets of children
                    for child_path in sheet.children:
                        child_sheet = self.sheets[child_path]
                        if child_sheet.name in sheets_using_net:
                            child_sheet.imported_nets.add(net_name)

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
            
        # Add all additional properties from netlist
        if hasattr(comp, 'properties'):
            for prop in comp.properties:
                if prop.name not in ['Reference', 'Value', 'Footprint', 'Datasheet', 'Description']:
                    # Always quote values for certain properties
                    if prop.name in ['Sheetname', 'Sheetfile'] or prop.name.startswith('ki_'):
                        value = f"'{prop.value}'"
                    else:
                        # Quote property values that contain spaces
                        value = f"'{prop.value}'" if ' ' in prop.value else prop.value
                    props.append(f"{prop.name}={value}")
            
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
        
        # Function parameters - legalize names for parameters
        params = []
        for net in sorted(sheet.imported_nets):
            if not net.startswith('unconnected'):
                params.append(self.legalize_name(net))
        if 'GND' not in params:
            params.append('GND')
            
        func_name = self.legalize_name(sheet.name)
        code.append(f"def {func_name}({', '.join(params)}):\n")
        
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
                func_name = self.legalize_name(child_sheet.name)
                params = []
                # Pass through the parent's nets to the child
                for net in sorted(child_sheet.imported_nets):
                    if not net.startswith('unconnected'):
                        params.append(self.legalize_name(net))
                if 'GND' not in params:
                    params.append('GND')
                code.append(f"{self.tab}{func_name}({', '.join(params)})\n")

        # Connections
        code.append(f"\n{self.tab}# Connections\n")
        for net in self.netlist.nets:
            conn = self.net_to_skidl(net, sheet)
            if conn:
                code.append(conn)
        code.append(f"{self.tab}return\n")
        
        return "".join(code)

    def create_main_file(self, output_dir: str):
        """Create the main.py file."""
        code = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n"
        ]
        
        # Import only top-level modules (no parents)
        for sheet in self.sheets.values():
            if not sheet.parent and sheet.name != 'main':
                module_name = self.legalize_name(sheet.name)
                code.append(f"from {module_name} import {module_name}\n")
        
        code.extend([
            "\ndef main():\n",
            f"{self.tab}# Create nets\n",
        ])
        
        # Create all global nets
        global_nets = set()
        for sheet in self.sheets.values():
            if not sheet.parent:  # Only include nets from top-level sheets
                global_nets.update(sheet.imported_nets)
        
        for net in sorted(global_nets):
            if not net.startswith('unconnected'):
                original_name = net
                legal_name = self.legalize_name(original_name)
                code.append(f"{self.tab}{legal_name} = Net('{original_name}')\n")
        
        # Call only top-level subcircuits
        code.append(f"\n{self.tab}# Create subcircuits\n")
        for sheet in self.get_hierarchical_order():
            if not sheet.parent and sheet.name != 'main':  # Only call top-level subcircuits
                params = []
                for net in sorted(sheet.imported_nets):
                    if not net.startswith('unconnected'):
                        params.append(self.legalize_name(net))
                if 'GND' not in params:
                    params.append('GND')
                func_name = self.legalize_name(sheet.name)
                code.append(f"{self.tab}{func_name}({', '.join(params)})\n")
        
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
