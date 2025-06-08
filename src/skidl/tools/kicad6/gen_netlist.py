# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Generate KiCad 8 netlist.
"""

import os.path
import time
import uuid
from simp_sexp import Sexp

from skidl.pckg_info import __version__
from skidl.scriptinfo import scriptinfo
from skidl.utilities import export_to_all
from skidl.circuit import HIER_SEP

# This UUID was generated using uuidgen for passing as the namespace argument to uuid.uuid5().
namespace_uuid = uuid.UUID("7026fcc6-e1a0-409e-aaf4-6a17ea82654f")


def gen_sheetpath(hierarchy):
    """
    Generate a sheetpath string from a hierarchical path name.

    A sheetpath is a string representation of the hierarchical path
    in a KiCad project. This function converts the given hierarchy
    string into a valid sheetpath format by replacing the hierarchy
    separator with '/' and ensuring it starts and ends with '/'.

    Args:
        hierarchy (str): The hierarchical path name, where levels are
                         separated by a specific hierarchy separator.

    Returns:
        str: The generated sheetpath string. If the input hierarchy
             is empty or None, the function returns "/".
    """

    if not hierarchy:
        return "/"
    return "/" + hierarchy.replace(HIER_SEP, "/").strip("/") + "/"


def gen_part_tstamp(part):
    """
    Generate a unique timestamp for a given part based on its hierarchical name.

    This function uses a UUID version 5 (SHA-1 hash) to create a deterministic
    and unique identifier for the part. The UUID is generated using a namespace
    UUID and the hierarchical name of the part.

    Args:
        part: An object representing the part. It is expected to have a
              'hierarchical_name' attribute that uniquely identifies the part
              within its hierarchy.

    Returns:
        str: A string representation of the generated UUID.
    """

    part_tstamp = str(uuid.uuid5(namespace_uuid, part.hierarchical_name))
    return part_tstamp


def gen_sheetpath_tstamp(sheetpath):
    """
    Generate a timestamp for a given sheetpath.

    This function creates a unique timestamp for a hierarchical sheetpath
    in a KiCad project. If the sheetpath is the root ("/"), the timestamp
    will also be "/". For other sheetpaths, it generates a UUID for each
    segment of the path and combines them into a single timestamp.

    Args:
        sheetpath (str): The hierarchical sheetpath, represented as a string.

    Returns:
        str: A timestamp for the sheetpath. For the root path, it returns "/".
             For other paths, it returns a UUID-based timestamp in the format
             "/<UUID>/<UUID>/.../<UUID>/", where each UUID corresponds to a
             segment of the sheetpath.
    """

    if sheetpath == "/":
        tstamp = "/"
    else:
        path_pieces = sheetpath.strip("/").split("/")
        tstamp = "/".join(
            [str(uuid.uuid5(namespace_uuid, piece)) for piece in path_pieces]
        )
        tstamp = "/" + tstamp + "/"
    return tstamp


def gen_netlist_sheet(hierarchy, number, src_file, **kwargs):
    """
    Generate a netlist sheet representation for a KiCad project.

    This function creates a hierarchical representation of a sheet in a KiCad
    netlist, including its path, timestamp, and title block information.

    Args:
        hierarchy (list): A list representing the hierarchical structure of the sheet.
        number (int): The sheet number in the hierarchy.
        src_file (str): The source file associated with the sheet.

    Returns:
        list: A nested list structure representing the netlist sheet, including
              its metadata and title block information.
    """
    sheetpath = gen_sheetpath(hierarchy)
    sheetpath_tstamp = gen_sheetpath_tstamp(sheetpath)
    sheet = Sexp([
        "sheet",
        ["number", number],
        ["name", sheetpath],
        ["tstamps", sheetpath_tstamp],
        [
            "title_block",
            ["title"],
            ["company"],
            ["rev"],
            ["date"],
            ["source", src_file],
            ["comment", ["number", "1"], ["value", ""]],
            ["comment", ["number", "2"], ["value", ""]],
            ["comment", ["number", "3"], ["value", ""]],
            ["comment", ["number", "4"], ["value", ""]],
            ["comment", ["number", "5"], ["value", ""]],
            ["comment", ["number", "6"], ["value", ""]],
            ["comment", ["number", "7"], ["value", ""]],
            ["comment", ["number", "8"], ["value", ""]],
            ["comment", ["number", "9"], ["value", ""]],
        ],
    ])

    return sheet


def gen_netlist_comp(part, **kwargs):
    """
    Generate a netlist component representation for a given part.

    This function takes a part object and generates a hierarchical representation
    of the part's attributes and metadata in a format suitable for inclusion in
    a KiCad netlist. The generated structure includes information such as the
    part's reference, value, footprint, description, datasheet, and additional
    fields.

    Args:
        part (Part): The part object containing attributes such as name, reference,
                     value, footprint, description, datasheet, and other metadata.

    Returns:
        list: A nested list structure representing the netlist component,
              including fields like reference, value, description, library source,
              sheetpath, timestamps, and custom fields.
    """

    part_name = part.name
    ref = part.ref
    value = part.value_to_str()
    footprint = getattr(part, "footprint", "")
    description = getattr(part, "description", "")
    datasheet = getattr(part, "datasheet", "")
    lib_filename = getattr(getattr(part, "lib", ""), "filename", "NO_LIB")

    # Embed the part hierarchy as a set of UUIDs into the sheetpath for each component.
    # This enables hierarchical selection in pcbnew.
    sheetpath = gen_sheetpath(part.hierarchy)
    sheetpath_tstamp = gen_sheetpath_tstamp(sheetpath)
    part_tstamp = gen_part_tstamp(part)

    fields = Sexp(["fields"])
    part_fields = list(part.fields.items())
    part_fields += list(
        {
            "Description": description,
            "Footprint": footprint,
            "Datasheet": datasheet,
        }.items()
    )
    part_fields.append(["SKiDL Tag", part.tag])
    if kwargs.get("track_src", True):
        part_fields.append(["SKiDL Line", part.src_line(not kwargs.get("track_abs_path", False))])
    for fld_name, fld_value in part_fields:
        if fld_value:
            field = Sexp(["field", ["name", fld_name], fld_value])
        else:
            field = Sexp(["field", ["name", fld_name]])
        fields.append(field)

    comp = Sexp([
        "comp",
        ["ref", ref],
        ["value", value],
        ["description", description],
        ["footprint", footprint],
        # ["datasheet", datasheet],
        fields,
        ["libsource", ["lib", lib_filename], ["part", part_name]],
        ["sheetpath", ["names", sheetpath], ["tstamps", sheetpath_tstamp]],
        ["tstamps", part_tstamp],
    ])

    # If part has a 'dnp' attribute set to True, add the dnp property
    if getattr(part, "dnp", False):
        comp.append(Sexp(["property", ["name", "dnp"]]))
    
    # If part has an 'exclude_from_bom' attribute set to True, add the exclude_from_bom property
    if getattr(part, "exclude_from_bom", False):
        comp.append(Sexp(["property", ["name", "exclude_from_bom"]]))

    return comp


def gen_netlist_net(net, **kwargs):
    """
    Generate a netlist representation for a given net.

    This function creates a hierarchical list structure representing a net
    in a KiCad netlist. The netlist includes the net's code, name, and the
    associated pins sorted by their string representation.

    Args:
        net (Net): The net object containing information about the net's
                   code, name, and associated pins.

    Returns:
        list: A nested list structure representing the net, including
              its code, name, and associated pins with their part references
              and pin numbers.
    """

    nt_lst = Sexp(["net", ["code", net.code], ["name", net.name]])
    for p in sorted(net.pins, key=str):
        nt_lst.append(["node", ["ref", p.part.ref], ["pin", p.num]])

    return nt_lst


@export_to_all
def gen_netlist(circuit, **kwargs):
    """
    Generate a netlist for a given circuit.

    This function creates a netlist representation of the circuit, which includes
    information about components, nets, and design metadata. The netlist is formatted
    as a nested list structure and converted to S-expression format using the Sexp class.

    Args:
        circuit (Circuit): The circuit object containing parts, nets, and other
            design information.

    Returns:
        str: The netlist in S-expression format.

    Notes:
        - The function performs checks for empty footprints and randomly-assigned
          part tags to ensure the netlist is stable and usable for PCB design.
        - The netlist includes metadata such as the source file, date, and tool
          version.
        - Components and nets are sorted for consistent output.
        - The Sexp class is used to create a properly formatted S-expression.
    """

    # If track_src, track_abs_path is not specified in kwargs, use values from the circuit attributes.
    kwargs["track_src"] = kwargs.get("track_src", circuit.track_src)
    kwargs["track_abs_path"] = kwargs.get("track_abs_path", circuit.track_abs_path)

    # Check for some things that can cause problems if the netlist is
    # used to create a PCB.

    # Check for parts with no physical footprint to place on the PCB.
    circuit.check_for_empty_footprints()

    # Check for any randomly-assigned tags since those will lead to
    # unstable associations between parts and PCB footprints.
    circuit.check_part_tags()

    scr_dict = scriptinfo()
    src_file = os.path.join(scr_dict["dir"], scr_dict["source"])
    date = time.strftime("%m/%d/%Y %I:%M %p")
    tool = f"SKiDL ({__version__})"

    sheets = Sexp()
    for num, node_name in enumerate(circuit.get_node_names(), 1):
        sheets.append(gen_netlist_sheet(node_name, num, src_file, **kwargs))

    components = Sexp()
    for p in sorted(circuit.parts, key=lambda p: str(p.ref)):
        components.append(gen_netlist_comp(p, **kwargs))

    nets = Sexp()
    sorted_nets = sorted(circuit.get_nets(), key=lambda n: str(n.name))
    for code, net in enumerate(sorted_nets, 1):
        net.code = code
        nets.append(gen_netlist_net(net, **kwargs))

    netlist = Sexp([
        "export",
        ["version", "D"],
        [
            "design",
            ["source", src_file],
            ["date", date],
            ["tool", tool],
            *sheets,
        ],
        ["components", *components],
        ["nets", *nets],
    ])

    # Add quotes to all strings following the initial keyword in each S-expression of the netlist.
    netlist.add_quotes(lambda s: True)

    # For some reason, KiCad's PCBNEW expects a space after the beginning export keyword
    # or else it rejects the netlist file.
    return netlist.to_str().replace("(export\n", "(export \n", 1)
