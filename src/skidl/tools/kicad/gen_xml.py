# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Generate KiCad 5 XML.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import os.path
import time
import os

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from skidl.pckg_info import __version__
from skidl.scriptinfo import get_script_name, scriptinfo
from skidl.utilities import add_quotes, export_to_all, find_and_open_file, rmv_attr
from skidl.logger import active_logger
from skidl.part import LIBRARY
from skidl.utilities import export_to_all, find_and_read_file, num_to_chars, rmv_quotes



def gen_xml_comp(part):
    """Generate the XML describing a component.

    Args:
        part (Part): Part object.

    Returns:
        str: String containing the XML for the part.
    """
    ref = part.ref
    value = add_quotes(part.value_to_str())

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
def gen_xml(circuit):
    """Generate the XML describing a circuit.

    Args:
        circuit (Circuit): Circuit object.

    Returns:
        str: String containing the XML for the circuit.
    """
    from skidl import KICAD

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
        netlist += "\n" + gen_xml_comp(p)
    netlist += "\n  </components>\n"
    netlist += "  <nets>"
    for code, n in enumerate(circuit.get_nets()):
        n.code = code
        netlist += "\n" + gen_xml_net(n)
    netlist += "\n  </nets>\n"
    netlist += "</export>\n"
    return netlist
