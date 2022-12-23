# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""
Handler for reading Kicad libraries and generating netlists.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import os.path
import time
from builtins import str

from future import standard_library

from ...logger import active_logger
from ...pckg_info import __version__
from ...scriptinfo import get_script_name, scriptinfo
from ...utilities import find_and_open_file, add_quotes, export_to_all
from . import v5, v6

standard_library.install_aliases()


# These aren't used here, but they are used in modules
# that include this module.
tool_name = "kicad"
# lib_suffix = [".kicad_sym", ".lib"]
lib_suffix = [".lib", ".kicad_sym"]

__all__ = ["tool_name", "lib_suffix"]


@export_to_all
def get_kicad_lib_tbl_dir():
    """Get the path to where the global fp-lib-table file is found."""

    paths = (
        "$HOME/.config/kicad",
        "~/.config/kicad",
        "%APPDATA%/kicad",
        "$HOME/Library/Preferences/kicad",
        "~/Library/Preferences/kicad",
    )

    for path in paths:
        path = os.path.normpath(os.path.expanduser(os.path.expandvars(path)))
        if os.path.lexists(path):
            return path
    return ""


@export_to_all
def load_sch_lib(lib, filename=None, lib_search_paths_=None, lib_section=None):
    """
    Load the parts from a KiCad schematic library file.

    Args:
        lib (SchLib): SKiDL library object.
        filename: The name of the KiCad schematic library file.
    """

    from ...skidl import lib_suffixes
    from .. import KICAD

    # Try to open the file using allowable suffixes for the versions of KiCAD.
    suffixes = lib_suffixes[KICAD]
    base, suffix = os.path.splitext(filename)
    if suffix:
        # If an explicit file extension was given, use it instead of tool lib default extensions.
        suffixes = [suffix]
    for suffix in suffixes:
        # Allow file open failure so multiple suffixes can be tried without error messages.
        f, _ = find_and_open_file(
            filename, lib_search_paths_, suffix, allow_failure=True
        )
        if f:
            # Break from the loop once a library file is successfully opened.
            break
    if not f:
        raise FileNotFoundError(
            "Unable to open KiCad Schematic Library File {}".format(filename)
        )

    # TODO: Find a way to use find_and_read_file() and pass the results.
    if suffix == ".kicad_sym":
        v6.load_sch_lib(lib, f, filename, lib_search_paths_)
    else:
        v5.load_sch_lib(lib, f, filename, lib_search_paths_)


@export_to_all
def parse_lib_part(part, partial_parse=False):
    """
    Create a Part using a part definition from a KiCad schematic library.

    Args:
        part (Part): SKiDL Part object.
        partial_parse: If true, scan the part definition until the
            name and aliases are found. The rest of the definition
            will be parsed if the part is actually used.
    """
    if part.tool_version == "kicad_v6":
        v6.parse_lib_part(part, partial_parse)
    else:
        v5.parse_lib_part(part, partial_parse)


@export_to_all
def gen_netlist(circuit):
    """Generate a netlist from a Circuit object.

    Args:
        circuit (Circuit): Circuit object.

    Returns:
        str: String containing netlist text.
    """
    from .. import KICAD

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
        netlist += "\n" + p.generate_netlist_component(KICAD)
    netlist += ")\n"
    netlist += "  (nets"
    sorted_nets = sorted(circuit.get_nets(), key=lambda n: str(n.name))
    for code, n in enumerate(sorted_nets, 1):
        n.code = code
        netlist += "\n" + n.generate_netlist_net(KICAD)
    netlist += ")\n)\n"
    return netlist


@export_to_all
def gen_netlist_comp(part):
    """Generate the netlist text describing a component.

    Args:
        part (Part): Part object.

    Returns:
        str: String containing component netlist description.
    """

    from ...circuit import HIER_SEP

    ref = add_quotes(part.ref)

    value = add_quotes(part.value_str)

    footprint = getattr(part, "footprint", "")
    footprint = add_quotes(footprint)

    lib_filename = getattr(getattr(part, "lib", ""), "filename", "NO_LIB")
    part_name = add_quotes(part.name)

    # Embed the hierarchy along with a random integer into the sheetpath for each component.
    # This enables hierarchical selection in pcbnew.
    hierarchy = add_quotes("/" + part.hierarchical_name.replace(HIER_SEP, "/"))
    tstamps = hierarchy

    fields = ""
    for fld_name, fld_value in part.fields.items():
        fld_value = add_quotes(fld_value)
        if fld_value:
            fld_name = add_quotes(fld_name)
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
        + "      (sheetpath (names {hierarchy}) (tstamps {tstamps})))"
    )
    txt = template.format(**locals())
    return txt


@export_to_all
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
def gen_pcb(circuit, pcb_file, fp_libs=None):
    """Create a KiCad PCB file directly from a Circuit object.

    Args:
        circuit (Circuit): Circuit object.
        pcb_file: Either a file object that can be written to, or a string
            containing a file name, or None.
        fp_libs: List of directories containing footprint libraries.
    Returns:
        None.
    """

    # Keep the import in here so it doesn't get triggered unless this is used
    # so it eases some problems with tox testing.
    # It requires pcbnew module which may not be present or may be for the
    # wrong Python version (2 vs. 3).
    try:
        import kinet2pcb  # For creating KiCad PCB directly from Circuit object.
    except ImportError:
        active_logger.warning(
            "kinet2pcb module is missing. Can't generate a KiCad PCB without it."
        )
    else:
        pcb_file = pcb_file or (get_script_name() + ".kicad_pcb")
        kinet2pcb.kinet2pcb(circuit, pcb_file, fp_libs)


@export_to_all
def gen_xml(circuit):
    """Generate the XML describing a circuit.

    Args:
        circuit (Circuit): Circuit object.

    Returns:
        str: String containing the XML for the circuit.
    """
    from .. import KICAD

    scr_dict = scriptinfo()
    src_file = os.path.join(scr_dict["dir"], scr_dict["source"])
    date = time.strftime("%m/%d/%Y %I:%M %p")
    tool = "SKiDL (" + __version__ + ")"
    template = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + '<export version="D">\n'
        + "  <design>\n"
        + "    <source>{src_file}</source>\n"
        + "    <date>{date}</date>\n"
        + "    <tool>{tool}</tool>\n"
        + "  </design>\n"
    )
    netlist = template.format(**locals())
    netlist += "  <components>"
    for p in circuit.parts:
        netlist += "\n" + p.generate_xml_component(KICAD)
    netlist += "\n  </components>\n"
    netlist += "  <nets>"
    for code, n in enumerate(circuit.get_nets()):
        n.code = code
        netlist += "\n" + n.generate_xml_net(KICAD)
    netlist += "\n  </nets>\n"
    netlist += "</export>\n"
    return netlist


@export_to_all
def gen_xml_comp(part):
    """Generate the XML describing a component.

    Args:
        part (Part): Part object.

    Returns:
        str: String containing the XML for the part.
    """
    ref = part.ref
    value = part.value_str

    try:
        footprint = part.footprint
    except AttributeError:
        active_logger.error(
            "No footprint for {part}/{ref}.".format(part=part.name, ref=ref)
        )
        footprint = "No Footprint"

    lib_filename = getattr(getattr(part, "lib", ""), "filename", "NO_LIB")
    part_name = add_quotes(part.name)

    fields = ""
    for fld_name, fld_value in part.fields.items():
        fld_value = add_quotes(fld_value)
        if fld_value:
            fld_name = add_quotes(fld_name)
            fields += "\n        (field (name {fld_name}) {fld_value})".format(
                **locals()
            )
    if fields:
        fields = "      <fields>" + fields
        fields += "\n      </fields>\n"

    template = (
        '    <comp ref="{ref}">\n'
        + "      <value>{value}</value>\n"
        + "      <footprint>{footprint}</footprint>\n"
        + "{fields}"
        + '      <libsource lib="{lib_filename}" part="{part_name}"/>\n'
        + "    </comp>"
    )
    txt = template.format(**locals())
    return txt


@export_to_all
def gen_xml_net(net):
    code = net.code
    name = net.name
    txt = '    <net code="{code}" name="{name}">'.format(**locals())
    for p in net.pins:
        part_ref = p.part.ref
        pin_num = p.num
        txt += '\n      <node ref="{part_ref}" pin="{pin_num}"/>'.format(**locals())
    txt += "\n    </net>"
    return txt


@export_to_all
def gen_svg_comp(part, symtx, net_stubs=None):
    """
    Generate SVG for this component.

    Args:
        part: Part object for which an SVG symbol will be created.
        symtx: String such as "HR" that indicates symbol mirroring/rotation.
        net_stubs: List of Net objects whose names will be connected to
            part symbol pins as connection stubs.

    Returns: SVG for the part symbol.
    """
    if part.tool_version == "kicad_v6":
        return v6.gen_svg_comp(part, symtx, net_stubs=None)
    else:
        return v5.gen_svg_comp(part, symtx, net_stubs=None)
