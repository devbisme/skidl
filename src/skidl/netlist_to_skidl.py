# -*- coding: utf-8 -*-

"""
Convert a KiCad netlist into equivalent hierarchical SKiDL programs.
"""

import re
import os
import random
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Set
from kinparse import parse_netlist
from .logger import active_logger  # Import the active_logger



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


def legalize_name(name: str, is_filename: bool = False) -> str:
    """Return a version of name that is a legal Python identifier."""
    name = name.lstrip("/ ")
    if name.endswith("+"):
        name = name[:-1] + "_p"
    elif name.endswith("-"):
        name = name[:-1] + "_n"
    if name.startswith("+"):
        name = "_p_" + name[1:]
    elif name.startswith("-"):
        name = "_n_" + name[1:]
    legalized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if legalized and legalized[0].isdigit():
        legalized = "_" + legalized
    return legalized


def find_common_path_prefix(path1: str, path2: str) -> str:
    """Return the common path prefix of two paths."""

    # Collect path prefix until the two paths differ.
    path_prefix = ""
    for c1, c2 in zip(path1, path2):
        if c1 != c2:
            break
        path_prefix += c1

    # Truncate the path prefix up to the last separator.
    last_sep_index = path_prefix.rindex("/")
    path_prefix = path_prefix[: last_sep_index + 1]

    return path_prefix


class HierarchicalConverter:
    def __init__(self, netlist_src):
        self.netlist = parse_netlist(netlist_src)
        self.sheets = {}
        self.tab = " " * 4

    def get_sheet_path(self, comp):
        """Return the sheet name from the component properties."""
        return comp.sheetpath.names

    def find_lowest_common_ancestor(self, sheet1, sheet2):
        """Return the lowest common ancestor (LCA) of two sheets."""
        return find_common_path_prefix(
            self.sheets[sheet1].path, self.sheets[sheet2].path
        )

    def extract_sheet_info(self):
        """Populate self.sheets with Sheet objects built from the netlist."""

        active_logger.info("=== Extracting Sheet Info ===")

        if getattr(self.netlist, "sheets", None):
            sheet_numbers_paths = [
                (sheet.num, sheet.name) for sheet in self.netlist.sheets
            ]
            sheet_paths = [
                sheet_number_path[1] for sheet_number_path in sheet_numbers_paths
            ]
        else:
            sheet_paths = list(
                set([self.get_sheet_path(part) for part in self.netlist.parts])
            )
            sheet_numbers_paths = enumerate(sheet_paths)

        for sheet_number, sheet_path in sheet_numbers_paths:
            parent = os.path.dirname(sheet_path.rstrip("/"))
            if parent:
                if not parent.endswith("/"):
                    parent += "/"
                name = os.path.basename(sheet_path.rstrip("/"))
            else:
                name = ""
            sheet = Sheet(
                number=sheet_number,
                path=sheet_path,
                name=name,
                parent=parent,
                components=[],
                local_nets=set(),
                imported_nets=set(),
                children=[],
            )
            if not parent:
                self.top_sheet = sheet
            self.sheets[sheet_path] = sheet
            active_logger.info(
                f"  Found sheet: original_name='{sheet.path}', final='{sheet.name}', parent='{sheet.parent}'"
            )

        # Set up parent-child relationships
        for sheet in self.sheets.values():
            parent_sheet = self.sheets.get(sheet.parent)
            if parent_sheet:
                parent_sheet.children.append(sheet.path)

        for sheet_path, sheet in self.sheets.items():
            active_logger.info(
                f"   sheet path='{sheet_path}', parent='{sheet.parent}', children={sheet.children}"
            )

        active_logger.info("=== Completed extracting sheet info ===")

    def assign_components_to_sheets(self):
        """Assign each component from the netlist to its appropriate sheet."""

        active_logger.info("=== Assigning Components to Sheets ===")

        for comp in self.netlist.parts:
            sheet_path = self.get_sheet_path(comp)
            if sheet_path in self.sheets:
                self.sheets[sheet_path].components.append(comp)
                active_logger.info(
                    f"  Assigning component {comp.ref} to sheet {sheet_path}"
                )
            else:
                active_logger.warning(
                    f"Sheet {sheet_path} not found for component {comp.ref}"
                )

        active_logger.info("=== Completed assigning components to sheets ===")

    def analyze_nets(self):
        """Analyze net usage to determine origins and required connections."""

        def find_net_src_dests(net_sheets):
            """
            Return the top-most sheet where the net is used and a list of all
            sheets that the net passes through to its stopping points.
            """

            src = net_sheets[0]
            for sheet in net_sheets[1:]:
                src = self.find_lowest_common_ancestor(src, sheet)

            dests = set()
            src_len = len(src)
            for sheet in set(net_sheets) - {src}:
                sheet = sheet.rstrip("/")
                path_src_to_sheet = sheet[src_len:]
                path_pieces = path_src_to_sheet.split("/")
                path = src
                for piece in path_pieces:
                    path += piece + "/"
                    dests.add(path)

            return src, dests

        active_logger.info("=== Starting Net Analysis ===")

        net_usage = defaultdict(lambda: defaultdict(set))

        active_logger.info("1. Mapping Net Usage Across Sheets:")

        # Map which nets are used in which sheets
        for net in self.netlist.nets:
            active_logger.info(f"\nAnalyzing net: {net.name}")
            for pin in net.pins:
                for comp in self.netlist.parts:
                    if comp.ref == pin.ref:
                        comp_sht_pth = self.get_sheet_path(comp)
                        net_usage[net.name][comp_sht_pth].add(f"{comp.ref}.{pin.num}")
                        active_logger.info(
                            f"  - Used in sheet '{comp_sht_pth}' by pin {comp.ref}.{pin.num}"
                        )

        active_logger.info("2. Analyzing Net Origins and Hierarchy:")

        net_hierarchy = {}
        for net_name, sheet_pins in net_usage.items():
            used_sheets = list(sheet_pins.keys())
            origin_sheet, destination_sheets = find_net_src_dests(used_sheets)
            destination_sheets = list(set(used_sheets) - {origin_sheet})
            net_hierarchy[net_name] = {
                "origin_sheet": origin_sheet,
                "destination_sheets": destination_sheets,
            }
            active_logger.info(f"\nNet: {net_name}")
            active_logger.info(f"  - Origin sheet: {origin_sheet}")
            active_logger.info(f"  - Destination sheets: {destination_sheets}")

        active_logger.info("3. Classifying local vs imported nets:")

        # Clear any existing net classifications
        for sheet in self.sheets.values():
            sheet.local_nets.clear()
            sheet.imported_nets.clear()

        for net_name, hierarchy in net_hierarchy.items():
            if net_name.startswith("unconnected"):
                continue
            self.sheets[hierarchy["origin_sheet"]].local_nets.add(net_name)
            active_logger.info(
                f"  Net {net_name} is local to sheet {hierarchy['origin_sheet']}"
            )
            for dest_sheet in hierarchy["destination_sheets"]:
                self.sheets[dest_sheet].imported_nets.add(net_name)
                active_logger.info(
                    f"  Net {net_name} is imported in sheet {dest_sheet}"
                )

        self.net_hierarchy = net_hierarchy
        self.net_usage = net_usage
        active_logger.info("=== Completed net analysis ===")

        # Print summary for each sheet
        for sheet_path, sheet in self.sheets.items():
            active_logger.info(
                f"Sheet '{sheet_path}': local_nets={sheet.local_nets}, imported_nets={sheet.imported_nets}"
            )

    def cull_from_top(self):
        """Remove top-level sheets that are not needed."""

        top_sheet = self.top_sheet
        while (
            not top_sheet.parent
            and not (top_sheet.components or top_sheet.local_nets)
            and len(top_sheet.children) == 1
        ):
            top_sheet = self.sheets[self.top_sheet.children[0]]
            top_sheet.name = self.top_sheet.name
            del self.sheets[self.top_sheet.path]
            top_sheet.parent = ""
            self.top_sheet = top_sheet

        sheet_names = [sheet.name for sheet in self.sheets.values() if sheet.parent]
        top_sheet_name = "top"
        while top_sheet_name in sheet_names:
            top_sheet_name += str(random.randint(0, 9))
        self.top_sheet.name = top_sheet_name

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
        desc = next((p.value for p in comp.properties if p.name == "Description"), None)
        if desc:
            props.append(f"description='{desc}'")
        props.append(f"ref='{ref}'")
        extra_fields = {}
        if hasattr(comp, "properties"):
            for prop in comp.properties:
                if prop.name not in [
                    "Reference",
                    "Value",
                    "Footprint",
                    "Datasheet",
                    "Description",
                ]:
                    extra_fields[prop.name] = prop.value
        if extra_fields:
            props.append(f"fields={repr(extra_fields)}")
        return f"{self.tab}{legalize_name(ref)} = Part({', '.join(props)})\n"

    def net_to_skidl(self, net: object, sheet: Sheet) -> str:
        """Return a SKiDL connection string for a net within a given sheet."""
        net_name = legalize_name(net.name)
        if net_name.startswith("unconnected"):
            return ""
        pins = []
        for pin in net.pins:
            if any(comp.ref == pin.ref for comp in sheet.components):
                comp_name = legalize_name(pin.ref)
                pins.append(f"{comp_name}['{pin.num}']")
        if pins:
            return f"{self.tab}{net_name} += {', '.join(pins)}\n"
        return ""

    def generate_sheet_code(self, sheet: Sheet) -> str:
        """Generate the SKiDL code for a given sheet."""

        active_logger.info(f"=== generate_sheet_code for sheet '{sheet.name}' ===")

        code = ["# -*- coding: utf-8 -*-\n", "from skidl import *\n"]

        # Import child subcircuits
        for child_path in sheet.children:
            child_sheet = self.sheets[child_path]
            module_name = legalize_name(child_sheet.name)
            code.append(f"from {module_name} import {module_name}\n")

        # Start function definition
        code.append("\n@subcircuit\n")

        # Determine required nets that need to be passed in
        required_nets = []
        for net_name in sorted(sheet.imported_nets):
            # Verify net really needs to be imported
            # (used by this sheet or needed by children)
            if sheet.path in self.net_usage[net_name] or any(
                child in self.net_usage[net_name] for child in sheet.children
            ):
                required_nets.append(legalize_name(net_name))

        func_name = legalize_name(sheet.name)
        code.append(f"def {func_name}({', '.join(required_nets)}):\n")

        # Create local nets
        local_nets = sorted(sheet.local_nets)
        if local_nets:
            code.append(f"{self.tab}# Local nets\n")
            for net in local_nets:
                legal_name = legalize_name(net)
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
                child_func = legalize_name(child.name)

                # Determine which nets to pass to child
                child_params = []
                for net_name in sorted(child.imported_nets):
                    if child_path in self.net_usage[net_name] or any(
                        grandchild in self.net_usage[net_name]
                        for grandchild in child.children
                    ):
                        child_params.append(legalize_name(net_name))

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
        active_logger.info(
            f"Generated code for sheet '{sheet.name}':\n{generated_code}"
        )
        return generated_code

    def generate_main_code(self):
        """Generate the code for the main.py file that creates nets and calls subcircuits."""

        code = (
            "# -*- coding: utf-8 -*-",
            "from skidl import *",
            f"from {self.top_sheet.name} import {self.top_sheet.name}",
            "",
            f"{self.top_sheet.name}()",
            "generate_netlist()",
        )
        return "\n".join(code)

    def convert(self, output_dir: str = None):
        """Run the complete conversion and write files if output_dir is provided."""
        self.extract_sheet_info()
        self.assign_components_to_sheets()
        self.analyze_nets()
        self.cull_from_top()
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            active_logger.info(f"Generating files in {output_dir}")
            for sheet in self.sheets.values():
                if sheet.name != "main":
                    filename = legalize_name(sheet.name, is_filename=True) + ".py"
                    sheet_path = Path(output_dir) / filename
                    sheet_path.write_text(self.generate_sheet_code(sheet))
                    active_logger.info(f"Created sheet file: {sheet_path}")
            main_path = Path(output_dir) / "main.py"
            main_path.write_text(self.generate_main_code())
            active_logger.info("Conversion completed successfully")
        else:
            main_sheet = next((s for s in self.sheets.values() if not s.parent), None)
            if main_sheet:
                return self.generate_sheet_code(main_sheet)
            return ""


def netlist_to_skidl(netlist_src: str, output_dir: str = None):
    """Convert a KiCad netlist to hierarchical SKiDL Python files."""
    converter = HierarchicalConverter(netlist_src)
    return converter.convert(output_dir)
