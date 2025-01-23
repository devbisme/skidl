# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Generate KiCad 8 netlist.
"""

import os.path
import time
import uuid

from skidl.pckg_info import __version__
from skidl.scriptinfo import scriptinfo
from skidl.utilities import add_quotes, export_to_all

# This UUID was generated using uuidgen for passing as the namespace argument to uuid.uuid5().
namespace_uuid = uuid.UUID("7026fcc6-e1a0-409e-aaf4-6a17ea82654f")

def gen_netlist_comp(part):
    """Generate the netlist text describing a component.

    Args:
        part (Part): Part object.

    Returns:
        str: String containing component netlist description.
    """

    from skidl.circuit import HIER_SEP

    ref = add_quotes(part.ref)

    value = add_quotes(part.value_to_str())

    footprint = getattr(part, "footprint", "")
    footprint = add_quotes(footprint)

    lib_filename = add_quotes(getattr(getattr(part, "lib", ""), "filename", "NO_LIB"))
    part_name = add_quotes(part.name)

    # Embed the part hierarchy as a set of UUIDs into the sheetpath for each component.
    # This enables hierarchical selection in pcbnew.
    sheetpath_pieces = part.hierarchy.split(HIER_SEP)
    sheetpath = add_quotes("/".join(sheetpath_pieces))
    sheetpath_tstamp = add_quotes("/".join([
        str(uuid.uuid5(namespace_uuid, piece))
        for piece in sheetpath_pieces
    ]))
    part_tstamp = add_quotes(str(uuid.uuid5(namespace_uuid, part.hierarchical_name)))

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
    template = (
        "(export (version D)\n"
        + "  (design\n"
        + '    (source "{src_file}")\n'
        + '    (date "{date}")\n'
        + '    (tool "{tool}"))\n'
    )
    netlist = template.format(**locals())
    netlist += "  (components"
    for p in sorted(circuit.parts, key=lambda p: str(p.ref)):
        netlist += "\n" + gen_netlist_comp(p)
    netlist += ")\n"
    netlist += "  (nets"
    sorted_nets = sorted(circuit.get_nets(), key=lambda n: str(n.name))
    for code, n in enumerate(sorted_nets, 1):
        n.code = code
        netlist += "\n" + gen_netlist_net(n)
    netlist += ")\n)\n"
    return netlist
