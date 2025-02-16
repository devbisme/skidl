# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Generate KiCad 6 netlist.
"""

import os.path
import time
import textwrap
import uuid

from skidl.pckg_info import __version__
from skidl.scriptinfo import scriptinfo
from skidl.utilities import add_quotes, export_to_all
from skidl.circuit import HIER_SEP

# This UUID was generated using uuidgen for passing as the namespace argument to uuid.uuid5().
namespace_uuid = uuid.UUID("7026fcc6-e1a0-409e-aaf4-6a17ea82654f")

def gen_sheetpath(hierarchy):
    """Generate a sheetpath for the hierarchy.

    Args:
        hierarchy (str): Hierarchical path name.

    Returns:
        str: String containing the sheetpath.
    """
    sheetpath = hierarchy
    sheetpath.replace(HIER_SEP, "/")
    return sheetpath

def gen_sheetpath_tstamp(hierarchy):
    """Generate a timestamp for the sheetpath.

    Args:
        hierarchy (str): Hierarchical path name.

    Returns:
        str: String containing the timestamp.
    """
    hier_pieces = hierarchy.split(HIER_SEP)
    sheetpath_tstamp = add_quotes("/".join([
        str(uuid.uuid5(namespace_uuid, piece))
        for piece in hier_pieces
    ]))
    return sheetpath_tstamp

def gen_part_tstamp(part):
    """Generate a timestamp for the part.

    Args:
        part (Part): Part object.

    Returns:
        str: String containing the timestamp.
    """
    part_tstamp = add_quotes(str(uuid.uuid5(namespace_uuid, part.hierarchical_name)))
    return part_tstamp

def gen_netlist_comp(part):
    """Generate the netlist text describing a component.

    Args:
        part (Part): Part object.

    Returns:
        str: String containing component netlist description.
    """

    ref = add_quotes(part.ref)

    value = add_quotes(part.value_to_str())

    footprint = getattr(part, "footprint", "")
    footprint = add_quotes(footprint)

    lib_filename = add_quotes(getattr(getattr(part, "lib", ""), "filename", "NO_LIB"))
    part_name = add_quotes(part.name)

    # Embed the part hierarchy as a set of UUIDs into the sheetpath for each component.
    # This enables hierarchical selection in pcbnew.
    sheetpath = gen_sheetpath(part.hierarchy)
    sheetpath_tstamp = gen_sheetpath_tstamp(part.hierarchy)
    part_tstamp = gen_part_tstamp(part)

    fields = ""
    for fld_name, fld_value in part.fields.items():
        fld_name = add_quotes(fld_name)
        fld_value = add_quotes(fld_value)
        if fld_value:
            fields += "\n        (field (name {fld_name}) {fld_value})".format(
                **locals()
            )
    if fields:
        fields = "      (fields" + fields
        fields += ")\n"

    template = (
        "    (comp (ref {ref})\n"
        + "      (value {value})\n"
        + "      (footprint {footprint})\n"
        + "{fields}"
        + "      (libsource (lib {lib_filename}) (part {part_name}))\n"
        + "      (sheetpath (names {sheetpath}) (tstamps {sheetpath_tstamp}))\n"
        + "      (tstamps {part_tstamp})\n"
        + "    )\n"
    )
    txt = template.format(**locals())
    return txt


def gen_netlist_net(net):
    """Generate the netlist text describing a net.

    Args:
        part (Net): Net object.

    Returns:
        str: String containing net netlist description.
    """
    code = add_quotes(net.code)
    name = add_quotes(net.name)
    txt = "    (net (code {code}) (name {name})".format(**locals())
    for p in sorted(net.pins, key=str):
        part_ref = add_quotes(p.part.ref)
        pin_num = add_quotes(p.num)
        txt += "\n      (node (ref {part_ref}) (pin {pin_num}))".format(**locals())
    txt += ")"
    return txt

def gen_netlist_sheet(hierarchy, number, src_file):
    sheetpath = gen_sheetpath(hierarchy)
    sheetpath_tstamp = gen_sheetpath_tstamp(hierarchy)
    return f"""
    (sheet (number "{number}") (name "{sheetpath}") (tstamps "{sheetpath_tstamp}")
      (title_block
        (title)
        (company)
        (rev)
        (date)
        (source "{src_file}")
        (comment (number "1") (value ""))
        (comment (number "2") (value ""))
        (comment (number "3") (value ""))
        (comment (number "4") (value ""))
        (comment (number "5") (value ""))
        (comment (number "6") (value ""))
        (comment (number "7") (value ""))
        (comment (number "8") (value ""))
        (comment (number "9") (value ""))
      )
    )"""

@export_to_all
def gen_netlist(circuit):
    """Generate a netlist from a Circuit object.

    Args:
        circuit (Circuit): Circuit object.

    Returns:
        str: String containing netlist text.
    """

    scr_dict = scriptinfo()
    src_file = os.path.join(scr_dict["dir"], scr_dict["source"])
    date = time.strftime("%m/%d/%Y %I:%M %p")
    tool = "SKiDL (" + __version__ + ")"
    netlist = f"""
    (export (version D)
      (design
        (source "{src_file}")
        (date "{date}")
        (tool "{tool}")"""
    netlist = textwrap.dedent(netlist)
    for num, node_name in enumerate(circuit.get_node_names(), 1):
        netlist += gen_netlist_sheet(node_name, num, src_file)
    netlist += "\n  )\n"
    
    netlist += "  (components" + "\n"
    for p in sorted(circuit.parts, key=lambda p: str(p.ref)):
        netlist += gen_netlist_comp(p)
    netlist += "  )\n"
    
    netlist += "  (nets"
    sorted_nets = sorted(circuit.get_nets(), key=lambda n: str(n.name))
    for code, n in enumerate(sorted_nets, 1):
        n.code = code
        netlist += "\n" + gen_netlist_net(n)
    netlist += ")\n)\n"
    return netlist
