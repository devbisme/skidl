# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.


import copy
import datetime
import os
import os.path
import time
import uuid
from collections import OrderedDict

from simp_sexp import Sexp
from skidl.scriptinfo import get_script_name
from skidl.geometry import BBox, Point, Tx, Vector
from skidl.schematics.net_terminal import NetTerminal
from skidl.utilities import export_to_all, rmv_attr
from .constants import BLK_INT_PAD, BOX_LABEL_FONT_SIZE, GRID, PIN_LABEL_FONT_SIZE
from .bboxes import calc_symbol_bbox, calc_hier_label_bbox
from .gen_netlist import namespace_uuid, gen_part_tstamp, gen_sheetpath_tstamp


__all__ = []

"""
Functions for generating a KiCad 9 schematic using s-expressions.
"""

# KiCad 9 schematic page sizes in mm
A_SIZES_MM = OrderedDict([
    ("A4", (210, 297)),
    ("A3", (297, 420)),
    ("A2", (420, 594)),
    ("A1", (594, 841)),
    ("A0", (841, 1189)),
])


def get_skidl_version():
    """Get SKiDL version string."""
    try:
        from skidl import __version__
        return __version__
    except ImportError:
        return "unknown"


# Removed manual symbol creation functions - now using SKiDL's draw_cmds data


def part_to_lib_symbol_definition(part):
    """Extract library symbol definition from SKiDL part using its draw_cmds.

    Args:
        part: SKiDL Part object with draw_cmds data

    Returns:
        list: Nested list representing the complete library symbol definition
    """
    # Get library and part name
    lib_name = os.path.splitext(part.lib.filename)[0] if hasattr(part.lib, 'filename') and part.lib.filename else "Device"
    part_name = part.name or "Unknown"
    lib_id = f"{lib_name}:{part_name}"

    # Start building the symbol definition
    symbol_def = [
        "symbol", lib_id,
        ["pin_numbers", ["hide", "yes"]],
        ["pin_names", ["offset", 0]],
        ["exclude_from_sim", "no"],
        ["in_bom", "yes"],
        ["on_board", "yes"]
    ]

    # Add properties from the part
    symbol_def.extend([
        ["property", "Reference", part.ref_prefix or "U",
            ["at", 2.032, 0, 90],
            ["effects", ["font", ["size", 1.27, 1.27]]]
        ],
        ["property", "Value", part_name,
            ["at", 0, 0, 90],
            ["effects", ["font", ["size", 1.27, 1.27]]]
        ],
        ["property", "Footprint", "",
            ["at", 0, 0, 0],
            ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]]
        ],
        ["property", "Datasheet", part.datasheet or "~",
            ["at", 0, 0, 0],
            ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]]
        ]
    ])

    # Add description if available
    if hasattr(part, 'description') and part.description:
        symbol_def.append([
            "property", "Description", part.description,
            ["at", 0, 0, 0],
            ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]]
        ])

    # Add keywords if available
    if hasattr(part, 'keywords') and part.keywords:
        symbol_def.append([
            "property", "ki_keywords", part.keywords,
            ["at", 0, 0, 0],
            ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]]
        ])

    # Add footprint filters if available
    if hasattr(part, 'fplist') and part.fplist:
        fplist_str = " ".join(part.fplist)
        symbol_def.append([
            "property", "ki_fp_filters", fplist_str,
            ["at", 0, 0, 0],
            ["effects", ["font", ["size", 1.27, 1.27]], ["hide", "yes"]]
        ])

    # Process drawing commands from the part
    # draw_cmds is a defaultdict with keys for units (0=common, 1,2,3...=units)

    # Add common graphics (unit 0) if present
    if 0 in part.draw_cmds:
        graphics_cmds = [copy.deepcopy(cmd) for cmd in part.draw_cmds[0] if cmd[0] not in ['pin']]
        if graphics_cmds:
            symbol_def.append([
                "symbol", f"{part_name}_0_1"
            ] + graphics_cmds)

    # Add unit-specific graphics and pins
    for unit_num, draw_cmds in part.draw_cmds.items():
        if unit_num == 0:
            continue  # Already processed above

        # Separate pins from graphics and convert Sexp objects to lists
        pin_cmds = [copy.deepcopy(cmd) for cmd in draw_cmds if cmd[0] == 'pin']
        graphics_cmds = [copy.deepcopy(cmd) for cmd in draw_cmds if cmd[0] not in ['pin', 'property']]

        if pin_cmds or graphics_cmds:
            unit_symbol = ["symbol", f"{part_name}_{unit_num}_{unit_num}"]
            unit_symbol.extend(graphics_cmds)
            unit_symbol.extend(pin_cmds)
            symbol_def.append(unit_symbol)

    # Add embedded_fonts
    symbol_def.append(["embedded_fonts", "no"])

    return symbol_def


def get_lib_symbol_definition_from_part(part):
    """Get library symbol definition using SKiDL part's actual draw_cmds data.

    Args:
        part: SKiDL Part object

    Returns:
        list: Nested list representing the library symbol definition
    """
    return part_to_lib_symbol_definition(part)


def part_to_symbol_sexp(part, tx, main_sheet_uuid, sheet_uuids=None):
    """Convert a SKiDL part to a KiCad 9 symbol s-expression as nested list.

    Args:
        part: SKiDL Part object
        tx: Transformation matrix
        main_sheet_uuid: UUID of the main/root schematic sheet
        sheet_uuids: Dict mapping subcircuit names to their sheet UUIDs

    Returns:
        list: Nested list representing symbol s-expression
    """
    if not part.ref:
        return None

    # Transform part position
    origin = (part.tx * tx).origin
    pos_x, pos_y = float(origin.x), float(origin.y)

    # Generate UUID using same scheme as netlist generator
    symbol_uuid = gen_part_tstamp(part)

    # Get library and part name
    lib_name = os.path.splitext(part.lib.filename)[0] if hasattr(part.lib, 'filename') and part.lib.filename else "Device"
    part_name = part.name or "R"

    # Build proper hierarchical instance path for arbitrary depth
    if sheet_uuids is None:
        sheet_uuids = {}

    # Get the hierarchical path (skip root empty string)
    path_components = [level for level in part.hiertuple[1:] if level]

    if not path_components:
        # Root level part - path is just main sheet UUID
        instance_path = f"/{main_sheet_uuid}"
    else:
        # Multi-level hierarchical path: main_sheet_uuid/level1_uuid/level2_uuid/.../current_sheet_uuid
        path_uuids = [main_sheet_uuid]

        # Build path incrementally for each hierarchy level INCLUDING the current level
        for i in range(len(path_components)):
            # Create the path key for this level (e.g., "power" or "power/regulators")
            level_path = "/".join(path_components[:i+1])
            level_uuid = sheet_uuids.get(level_path)

            if level_uuid:
                path_uuids.append(level_uuid)
            else:
                # Cannot find UUID for this level, stop building path
                break

        instance_path = "/" + "/".join(path_uuids)

    # Create symbol as nested list
    symbol_list = [
        "symbol",
        ["lib_id", f"{lib_name}:{part_name}"],
        ["at", pos_x, pos_y, 0],
        ["unit", 1],
        ["exclude_from_sim", "no"],
        ["in_bom", "yes"],
        ["on_board", "yes"],
        ["dnp", "no"],
        ["uuid", symbol_uuid],
        # Reference property
        ["property", "Reference", part.ref,
            ["at", pos_x, pos_y - 2.54, 0],
            ["effects", ["font", ["size", 1.27, 1.27]]]
        ],
        # Value property
        ["property", "Value", str(part.value) if part.value else part.name,
            ["at", pos_x, pos_y + 2.54, 0],
            ["effects", ["font", ["size", 1.27, 1.27]]]
        ],
        # Footprint property (hidden)
        ["property", "Footprint", getattr(part, 'footprint', ''),
            ["at", pos_x, pos_y, 0],
            ["effects", ["font", ["size", 1.27, 1.27]], ["hide"]]
        ],
        # Datasheet property (hidden)
        ["property", "Datasheet", getattr(part, 'datasheet', '') or "",
            ["at", pos_x, pos_y, 0],
            ["effects", ["font", ["size", 1.27, 1.27]], ["hide"]]
        ],
        # Description property (hidden)
        ["property", "Description", getattr(part, 'description', '') or "",
            ["at", pos_x, pos_y, 0],
            ["effects", ["font", ["size", 1.27, 1.27]], ["hide"]]
        ]
    ]

    # Add all fields from part.fields dictionary (auto-export custom properties)
    y_offset = 5.08  # Start with 0.2 inch offset below the part
    if hasattr(part, 'fields') and part.fields:
        for field_name, field_value in part.fields.items():
            # Skip standard KiCad properties that we already handled above
            if field_name.lower() in ['reference', 'value', 'footprint', 'datasheet', 'description']:
                continue

            # Only add fields with non-empty values
            if field_value and str(field_value).strip():
                field_property = [
                    "property", field_name, str(field_value),
                    ["at", pos_x, pos_y + y_offset, 0],
                    ["effects", ["font", ["size", 1.27, 1.27]], ["hide"]]
                ]
                symbol_list.append(field_property)
                y_offset += 1.27  # Increment position for next field

    # Add other common part attributes as properties (if they exist and aren't already covered)
    additional_attrs = {
        'keywords': 'ki_keywords',
        'manufacturer': 'Manufacturer',
        'manf_num': 'MPN',
        'supplier': 'Supplier',
        'supplier_num': 'SPN',
        'tolerance': 'Tolerance',
        'temp_range': 'Temperature',
        'voltage_rating': 'Voltage',
        'power_rating': 'Power',
        'package': 'Package'
    }

    for attr_name, prop_name in additional_attrs.items():
        attr_value = getattr(part, attr_name, None)
        if attr_value and str(attr_value).strip():
            # Check if this property name already exists in fields to avoid duplicates
            if not (hasattr(part, 'fields') and prop_name in part.fields):
                additional_property = [
                    "property", prop_name, str(attr_value),
                    ["at", pos_x, pos_y + y_offset, 0],
                    ["effects", ["font", ["size", 1.27, 1.27]], ["hide"]]
                ]
                symbol_list.append(additional_property)
                y_offset += 1.27

    # Add the instances section
    symbol_list.extend([
        # Instances section - critical for KiCad to show references correctly
        ["instances",
            ["project", "SKiDL-Generated",
                ["path", instance_path,
                    ["reference", part.ref],
                    ["unit", 1]
                ]
            ]
        ]
    ])

    return symbol_list


def net_to_wire_sexp(net, wire_segments, tx):
    """Convert wire segments to KiCad 9 wire s-expressions as nested lists.

    Args:
        net: SKiDL Net object
        wire_segments: List of wire segments
        tx: Transformation matrix

    Returns:
        list: List of nested lists representing wire s-expressions
    """
    wires = []

    for segment in wire_segments:
        # Transform segment points
        transformed_segment = segment * tx
        start = transformed_segment.p1
        end = transformed_segment.p2

        wire_uuid = str(uuid.uuid4())

        wire_list = [
            "wire",
            ["pts",
                ["xy", float(start.x), float(start.y)],
                ["xy", float(end.x), float(end.y)]
            ],
            ["stroke", ["width", 0], ["type", "default"]],
            ["uuid", wire_uuid]
        ]
        wires.append(wire_list)

    return wires


def create_title_block_sexp(title):
    """Create title block s-expression as nested list.

    Args:
        title: Title string for the schematic

    Returns:
        list: Nested list representing title block
    """
    return [
        "title_block",
        ["title", title],
        ["date", datetime.date.today().isoformat()],
        ["company", ""],
        ["comment", 1, "Generated with SKiDL"],
        ["comment", 2, ""],
        ["comment", 3, ""],
        ["comment", 4, ""]
    ]


def create_hierarchical_sheet_sexp(node_name, sheet_filename, position, size, sheet_uuid):
    """Create a hierarchical sheet s-expression for KiCad9.

    Args:
        node_name: Name of the subcircuit/node
        sheet_filename: Filename of the sheet (e.g., "power.kicad_sch")
        position: (x, y) position tuple
        size: (width, height) size tuple
        sheet_uuid: Required predetermined UUID for the sheet

    Returns:
        list: Nested list representing the sheet s-expression
    """

    sheet_sexp = [
        "sheet",
        ["at", float(position[0]), float(position[1])],
        ["size", float(size[0]), float(size[1])],
        ["exclude_from_sim", "no"],
        ["in_bom", "yes"],
        ["on_board", "yes"],
        ["dnp", "no"],
        ["fields_autoplaced", "yes"],
        ["stroke", ["width", 0.1524], ["type", "solid"]],
        ["fill", ["color", 0, 0, 0, 0.0000]],
        ["uuid", sheet_uuid],
        ["property", "Sheetname", node_name,
            ["at", float(position[0]), float(position[1] - 0.7116), 0],
            ["effects", ["font", ["size", 1.27, 1.27]], ["justify", "left", "bottom"]]
        ],
        ["property", "Sheetfile", sheet_filename,
            ["at", float(position[0]), float(position[1] + size[1] + 0.5846), 0],
            ["effects", ["font", ["size", 1.27, 1.27]], ["justify", "left", "top"]]
        ]
    ]

    # TODO: Add hierarchical pins based on net connections

    return sheet_sexp


def group_parts_by_hierarchy(circuit):
    """Group circuit parts by their complete hierarchical paths.

    Args:
        circuit: SKiDL Circuit object

    Returns:
        dict: Dictionary mapping hierarchical paths to lists of parts
              Key format: "level1" or "level1/level2" or "level1/level2/level3" etc.
    """
    hierarchy_groups = {}

    for part in circuit.parts:
        if not isinstance(part, NetTerminal) and hasattr(part, 'hiertuple'):
            # Get the hierarchical path (skip root empty string)
            path_components = [level for level in part.hiertuple[1:] if level]

            if path_components:
                # Create path string like "power" or "power/regulators" or "power/regulators/ldo"
                node_path = "/".join(path_components)
            else:
                # Root level part
                node_path = ""

            if node_path not in hierarchy_groups:
                hierarchy_groups[node_path] = []
            hierarchy_groups[node_path].append(part)

    return hierarchy_groups


def get_all_hierarchy_levels(hierarchy_groups):
    """Extract all unique hierarchy levels from the grouped parts.

    Args:
        hierarchy_groups: Dict from group_parts_by_hierarchy

    Returns:
        set: All unique hierarchy levels (e.g., {"power", "power/regulators", "analog"})
    """
    all_levels = set()

    for path in hierarchy_groups.keys():
        if path:  # Skip root level
            # Add this level and all parent levels
            components = path.split("/")
            for i in range(1, len(components) + 1):
                level_path = "/".join(components[:i])
                all_levels.add(level_path)

    return all_levels


def create_schematic_sexp_for_hierarchy_group(parts_group, title="SKiDL-Generated Schematic", main_sheet_uuid=None, sheet_uuids=None, **options):
    """Create schematic s-expression for a specific hierarchy group.

    Args:
        parts_group: List of parts in this hierarchy level
        title: Title for the schematic
        main_sheet_uuid: UUID of the main/root schematic sheet
        sheet_uuids: Dict mapping subcircuit names to their sheet UUIDs
        options: Generation options

    Returns:
        Sexp: S-expression object representing the schematic for this group
    """
    # Generate unique UUID for schematic
    sch_uuid = str(uuid.uuid4())

    if sheet_uuids is None:
        sheet_uuids = {}

    # Collect unique library symbols used in this group
    unique_lib_parts = {}  # Map lib_id -> part (to avoid duplicates)
    symbol_parts = []  # Store parts and their data for later processing

    base_tx = Tx()
    for i, part in enumerate(parts_group):
        # Simple positioning - arrange parts in a grid
        grid_x = (i % 5) * 25.4  # 5 parts per row, 1 inch spacing
        grid_y = (i // 5) * 12.7  # 0.5 inch row spacing
        part.tx = Tx().move(Point(grid_x, grid_y))

        # Get library and part name
        lib_name = os.path.splitext(part.lib.filename)[0] if hasattr(part.lib, 'filename') and part.lib.filename else "Device"
        part_name = part.name or "Unknown"
        lib_id = f"{lib_name}:{part_name}"

        # Store unique part for lib_symbols (only one definition per lib_id needed)
        if lib_id not in unique_lib_parts:
            unique_lib_parts[lib_id] = part

        symbol_parts.append((part, base_tx))

    # Create lib_symbols section using actual SKiDL part data
    lib_symbols_list = ["lib_symbols"]
    for lib_id, part in unique_lib_parts.items():
        symbol_def = get_lib_symbol_definition_from_part(part)
        lib_symbols_list.append(symbol_def)

    # Create basic schematic structure
    schematic_list = [
        "kicad_sch",
        ["version", 20230409],
        ["generator", "SKiDL"],
        ["generator_version", get_skidl_version()],
        ["uuid", sch_uuid],
        ["paper", "A4"],
        create_title_block_sexp(title),
        lib_symbols_list  # Now contains actual symbol definitions
    ]

    # Add symbol instances for each part
    # Use main_sheet_uuid if provided, otherwise fall back to this schematic's UUID
    instance_main_uuid = main_sheet_uuid if main_sheet_uuid else sch_uuid
    for part, tx in symbol_parts:
        symbol_sexp = part_to_symbol_sexp(part, tx, instance_main_uuid, sheet_uuids)
        if symbol_sexp:
            schematic_list.append(symbol_sexp)

    # Add basic wiring if requested
    if options.get("add_wires", False):
        # This is a placeholder - would need proper routing logic
        for net in circuit.nets:
            if len(net.pins) >= 2:
                # Simple wire between first two pins
                wire_list = [
                    "wire",
                    ["pts",
                        ["xy", 100, 100],
                        ["xy", 125, 100]
                    ],
                    ["stroke", ["width", 0], ["type", "default"]],
                    ["uuid", str(uuid.uuid4())]
                ]
                schematic_list.append(wire_list)

    return Sexp(schematic_list)


def create_subcircuit_schematic_with_child_sheets(parts_group, current_path, title, main_sheet_uuid, sheet_uuids, hierarchy_groups, top_name, **options):
    """Create schematic s-expression for a hierarchy level with child sheet references.

    Args:
        parts_group: List of parts at this hierarchy level
        current_path: Current hierarchy path (e.g., "power" or "power/regulators")
        title: Title for the schematic
        main_sheet_uuid: UUID of the main/root schematic sheet
        sheet_uuids: Dict mapping hierarchy paths to their sheet UUIDs
        hierarchy_groups: All hierarchy groups for finding children
        top_name: Name prefix for child sheet files
        options: Generation options

    Returns:
        Sexp: S-expression object representing the schematic for this level
    """
    # Use the predetermined UUID for this schematic level (not a random one)
    sch_uuid = sheet_uuids.get(current_path) if current_path and sheet_uuids else str(uuid.uuid4())

    if sheet_uuids is None:
        sheet_uuids = {}

    # Collect unique library symbols used in this group
    unique_lib_parts = {}  # Map lib_id -> part (to avoid duplicates)
    symbol_parts = []  # Store parts and their data for later processing

    base_tx = Tx()
    for i, part in enumerate(parts_group):
        # Simple positioning - arrange parts in a grid
        grid_x = (i % 5) * 25.4  # 5 parts per row, 1 inch spacing
        grid_y = (i // 5) * 12.7  # 0.5 inch row spacing
        part.tx = Tx().move(Point(grid_x, grid_y))

        # Get library and part name
        lib_name = os.path.splitext(part.lib.filename)[0] if hasattr(part.lib, 'filename') and part.lib.filename else "Device"
        part_name = part.name or "Unknown"
        lib_id = f"{lib_name}:{part_name}"

        # Store unique part for lib_symbols (only one definition per lib_id needed)
        if lib_id not in unique_lib_parts:
            unique_lib_parts[lib_id] = part

        symbol_parts.append((part, base_tx))

    # Create lib_symbols section using actual SKiDL part data
    lib_symbols_list = ["lib_symbols"]
    for lib_id, part in unique_lib_parts.items():
        symbol_def = get_lib_symbol_definition_from_part(part)
        lib_symbols_list.append(symbol_def)

    # Create basic schematic structure
    schematic_list = [
        "kicad_sch",
        ["version", 20230409],
        ["generator", "SKiDL"],
        ["generator_version", get_skidl_version()],
        ["uuid", sch_uuid],
        ["paper", "A4"],
        create_title_block_sexp(title),
        lib_symbols_list  # Now contains actual symbol definitions
    ]

    # Add symbol instances for each part
    # Always use the main sheet UUID as root - let part_to_symbol_sexp build the full hierarchical path
    for part, tx in symbol_parts:
        symbol_sexp = part_to_symbol_sexp(part, tx, main_sheet_uuid, sheet_uuids)
        if symbol_sexp:
            schematic_list.append(symbol_sexp)

    # Now add child sheet symbols for any deeper levels
    child_levels = []
    current_depth = len(current_path.split("/"))

    # Find all immediate child levels
    for path in hierarchy_groups.keys():
        if path.startswith(current_path + "/") and path != current_path:
            # Check if this is an immediate child (one level deeper)
            path_components = path.split("/")
            if len(path_components) == current_depth + 1:
                child_name = path_components[-1]  # Last component is the child name
                child_levels.append((child_name, path))

    if child_levels:
        # Add hierarchical sheet symbols for child levels
        # Find a good position for child sheets (after any existing content)
        sheet_y = 50.0 + len(parts_group) * 12.7  # Position below parts

        for i, (child_name, child_path) in enumerate(child_levels):
            # Create sheet symbol for child
            safe_child_name = child_path.replace("/", "_")
            sheet_filename = f"{top_name}_{safe_child_name}.kicad_sch"
            sheet_position = (50.0, sheet_y + i * 30.0)
            sheet_size = (25.4, 20.0)  # 1 inch wide, 0.8 inch tall

            # Get the predetermined UUID for this child sheet
            child_sheet_uuid = sheet_uuids.get(child_path)
            sheet_sexp = create_hierarchical_sheet_sexp(
                child_name, sheet_filename, sheet_position, sheet_size, child_sheet_uuid
            )
            schematic_list.append(sheet_sexp)

    return Sexp(schematic_list)


def create_main_schematic_sexp(circuit, title, hierarchy_groups, top_name, **options):
    """Create the main schematic s-expression, potentially with hierarchical sheets.

    Args:
        circuit: SKiDL Circuit object
        title: Title for the schematic
        hierarchy_groups: Dictionary of hierarchy groups
        top_name: Name prefix for subsheet files
        options: Generation options

    Returns:
        tuple: (Sexp object for the main schematic, main sheet UUID, dict of sheet UUIDs)
    """
    # Generate stable UUID for main schematic using same approach as netlist generation
    # For root level, netlist generation uses "/" path, so we generate UUID from that
    main_sheet_uuid = str(uuid.uuid5(namespace_uuid, "/"))

    # Generate sheet UUIDs for ALL hierarchy levels (recursive)
    all_levels = get_all_hierarchy_levels(hierarchy_groups)
    sheet_uuids = {}

    for level_path in all_levels:
        # Generate UUID using same approach as netlist generation
        # Convert level_path like "power/regulators" to hierarchy tuple ("", "power", "regulators")
        path_components = level_path.split("/")
        hierarchy_tuple = ("",) + tuple(path_components)

        # Use netlist generation approach: generate UUID from the final level name
        sheet_uuids[level_path] = str(uuid.uuid5(namespace_uuid, path_components[-1]))

    # Collect lib_symbols needed for root level parts
    unique_lib_parts = {}
    if "" in hierarchy_groups:
        for part in hierarchy_groups[""]:
            lib_name = os.path.splitext(part.lib.filename)[0] if hasattr(part.lib, 'filename') and part.lib.filename else "Device"
            part_name = part.name or "Unknown"
            lib_id = f"{lib_name}:{part_name}"
            if lib_id not in unique_lib_parts:
                unique_lib_parts[lib_id] = part

    # Create lib_symbols section
    lib_symbols_list = ["lib_symbols"]
    for lib_id, part in unique_lib_parts.items():
        symbol_def = get_lib_symbol_definition_from_part(part)
        lib_symbols_list.append(symbol_def)

    # Create main schematic structure
    schematic_list = [
        "kicad_sch",
        ["version", 20230409],
        ["generator", "SKiDL"],
        ["generator_version", get_skidl_version()],
        ["uuid", main_sheet_uuid],
        ["paper", "A4"],
        create_title_block_sexp(title),
        lib_symbols_list
    ]

    # Add root level parts (if any) to main schematic
    if "" in hierarchy_groups:
        root_parts = hierarchy_groups[""]
        for i, part in enumerate(root_parts):
            # Simple positioning for root parts
            grid_x = (i % 5) * 25.4
            grid_y = (i // 5) * 12.7
            part.tx = Tx().move(Point(grid_x, grid_y))

            symbol_sexp = part_to_symbol_sexp(part, Tx(), main_sheet_uuid, sheet_uuids)
            if symbol_sexp:
                schematic_list.append(symbol_sexp)

    # Add hierarchical sheet symbols for immediate child subcircuits only (top-level)
    sheet_y = 50.0  # Start position for sheets
    top_level_subcircuits = set()

    # Find all top-level subcircuits (those without '/' in their path)
    for node_path in hierarchy_groups.keys():
        if node_path and "/" not in node_path:  # Top-level subcircuit
            top_level_subcircuits.add(node_path)

    for i, node_name in enumerate(sorted(top_level_subcircuits)):
        # Create sheet symbol
        sheet_filename = f"{top_name}_{node_name}.kicad_sch"
        sheet_position = (50.0, sheet_y + i * 30.0)
        sheet_size = (25.4, 20.0)  # 1 inch wide, 0.8 inch tall

        # Get the predetermined UUID for this top-level sheet
        top_level_sheet_uuid = sheet_uuids.get(node_name)
        sheet_sexp = create_hierarchical_sheet_sexp(
            node_name, sheet_filename, sheet_position, sheet_size, top_level_sheet_uuid
        )
        schematic_list.append(sheet_sexp)

    return Sexp(schematic_list), main_sheet_uuid, sheet_uuids


@export_to_all
def gen_schematic(
    circuit,
    filepath=".",
    top_name=get_script_name(),
    title="SKiDL-Generated Schematic",
    flatness=0.0,
    retries=2,
    **options
):
    """Create a schematic file from a Circuit object using s-expressions.

    Args:
        circuit (Circuit): The Circuit object that will have a schematic generated for it.
        filepath (str, optional): The directory where the schematic files are placed. Defaults to ".".
        top_name (str, optional): The name for the top of the circuit hierarchy. Defaults to get_script_name().
        title (str, optional): The title of the schematic. Defaults to "SKiDL-Generated Schematic".
        flatness (float, optional): Currently unused in KiCad9 implementation.
        retries (int, optional): Number of times to re-try if routing fails. Defaults to 2.
        options (dict, optional): Dict of options and values, usually for drawing/debugging.
    """

    from skidl.logger import active_logger

    def need_quote(x):
        match x[0]:
            case "title" | "date" | "company" | "comment" | "path" | "project" | "property" | "name" | "number" | "lib_id" | "reference": return True
            case _: return False

    def need_quote_alternate(x):
        match x[0]:
            case "alternate": return True
            case _: return False

    try:
        # Create output filename
        main_schematic_filename = os.path.join(filepath, f"{top_name}.kicad_sch")

        if not circuit.parts:
            active_logger.warning("Circuit has no parts to generate schematic from.")
            return

        active_logger.info(f"Generating KiCad 9 schematic: {main_schematic_filename}")
        active_logger.info(f"Processing {len(circuit.parts)} parts and {len(circuit.nets)} nets")

        # Group parts by hierarchy to determine if we need multiple files
        hierarchy_groups = group_parts_by_hierarchy(circuit)
        active_logger.info(f"Found {len(hierarchy_groups)} hierarchy levels: {list(hierarchy_groups.keys())}")

        # Generate main schematic (may contain sheet symbols for subcircuits)
        main_schematic_sexp, main_sheet_uuid, sheet_uuids = create_main_schematic_sexp(circuit, title, hierarchy_groups, top_name, **options)
        # Add quotes but avoid double-quoting already quoted strings
        main_schematic_sexp.add_quotes(need_quote)
        main_schematic_sexp.add_quotes(need_quote_alternate, stop_idx=2)

        with open(main_schematic_filename, 'w') as f:
            f.write(main_schematic_sexp.to_str())

        active_logger.info(f"Main schematic created: {main_schematic_filename}")

        # Generate separate schematic files for ALL hierarchy levels recursively
        subcircuit_count = 0

        def create_subcircuit_schematic(node_path, parts_list, depth=0):
            nonlocal subcircuit_count

            # Generate filename based on path (replace / with _) with top_name prefix
            safe_name = node_path.replace("/", "_")
            subcircuit_filename = os.path.join(filepath, f"{top_name}_{safe_name}.kicad_sch")
            subcircuit_title = f"{title} - {node_path}"

            active_logger.info(f"{'  ' * depth}Creating schematic for level: {node_path}")

            # Create schematic for this level (includes its own parts)
            subcircuit_sexp = create_subcircuit_schematic_with_child_sheets(
                parts_list, node_path, subcircuit_title, main_sheet_uuid, sheet_uuids, hierarchy_groups, top_name, **options
            )

            # Add quotes but avoid double-quoting already quoted strings
            subcircuit_sexp.add_quotes(need_quote)
            subcircuit_sexp.add_quotes(need_quote_alternate, stop_idx=2)

            with open(subcircuit_filename, 'w') as f:
                f.write(subcircuit_sexp.to_str())

            active_logger.info(f"{'  ' * depth}Subcircuit schematic created: {subcircuit_filename}")
            return 1

        # Process all hierarchy levels recursively
        for node_path, parts in hierarchy_groups.items():
            if node_path == "":  # Skip root level
                continue

            count = create_subcircuit_schematic(node_path, parts)
            subcircuit_count += count

        if subcircuit_count > 0:
            active_logger.info(f"Generated {subcircuit_count} subcircuit schematic files")
        else:
            active_logger.info("No subcircuits found - generated single flat schematic")

    except Exception as e:
        active_logger.error(f"Error generating KiCad 9 schematic: {str(e)}")
        raise
