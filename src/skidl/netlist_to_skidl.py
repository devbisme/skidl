# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Convert a netlist into an equivalent SKiDL program.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import re
from builtins import int
from collections import defaultdict

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from kinparse import parse_netlist

from .part import TEMPLATE
from .utilities import export_to_all



@export_to_all
def netlist_to_skidl(netlist_src):

    tab = " " * 4

    def legalize(name):
        """Make a string into a legal python variable name."""
        return re.sub("[^a-zA-Z0-9_]", "_", name)

    def comp_key(comp):
        """Create an ID key from component's major characteristics."""
        chars = [c for c in [comp.lib, comp.name, comp.footprint] if len(c)]
        return legalize("_".join(chars))

    def template_comp_to_skidl(template_comp):
        """Instantiate a component that will be used as a template."""
        ltab = tab

        # Instantiate component template.
        name = comp_key(template_comp)  # python variable name for template.
        lib = template_comp.lib
        part = template_comp.name
        tmpl = "{ltab}{name} = Part('{lib}', '{part}', dest=TEMPLATE".format(**locals())
        footprint = template_comp.footprint
        if len(footprint):
            tmpl += ", footprint='{footprint}'".format(**locals())
        tmpl += ")\n"

        # Set attributes of template using the component fields.
        for fld in template_comp.fields:
            tmpl += "{ltab}setattr({name}, '{fld.name}', '{fld.value}')\n".format(
                **locals()
            )

        return tmpl

    def comp_to_skidl(comp, template_comps):
        """Instantiate components using the component templates."""
        ltab = tab

        # Use the component key to get the template that matches this component.
        template_comp_name = comp_key(comp)
        template_comp = template_comps[template_comp_name]

        # Get the fields for the template.
        template_comp_fields = {fld.name: fld.value for fld in template_comp.fields}

        # Create a legal python variable for storing the instantiated component.
        ref = comp.ref
        legal_ref = legalize(ref)

        # Instantiate the component and its value (if any).
        inst = "{ltab}{legal_ref} = {template_comp_name}(ref='{ref}'".format(**locals())
        if len(comp.value):
            inst += ", value='{comp.value}'".format(**locals())
        inst += ")\n"

        # Set the fields of the instantiated component if they differ from the values in the template.
        for fld in comp.fields:
            if fld.value != template_comp_fields.get(fld.name, ""):
                inst += (
                    "{ltab}setattr({legal_ref}, '{fld.name}', '{fld.value}')\n".format(
                        **locals()
                    )
                )

        return inst

    def net_to_skidl(net):
        """Instantiate the nets between components."""

        # Build a list of component pins attached to the net.
        pins = []
        for pin in net.pins:
            comp = legalize(pin.ref)  # Name of Python variable storing component.
            pin_num = pin.num  # Pin number of component attached to net.
            pins.append("{comp}['{pin_num}']".format(**locals()))
        pins = ", ".join(pins)  # String the pins into an argument list.

        ltab = tab

        # Instantiate the net, connect the pins to it, and return it.
        return "{ltab}Net('{net.name}').connect({pins})\n".format(**locals())

    # Parse the netlist into a list of components and nets.
    ntlst = parse_netlist(netlist_src)

    # Convert a netlist into a skidl script with the following equence of operations:
    #   1. Create a template for each component having a given library, part name and footprint.
    #   2. Instantiate each component using its matching template. Also, set any attributes
    #      for the component that don't match those in the template.
    #   3. Instantiate the nets connecting the component pins.
    #   4. Call the script to instantiate the complete circuit.
    #   5. Generate the netlist for the circuit.

    # Create header.
    skidl = ""
    skidl += "# -*- coding: utf-8 -*-\n\n"
    skidl += "from skidl import *\n\n\n"

    # Create the beginning of the circuit function.
    circuit_name = legalize(ntlst.source)
    skidl += "def {circuit_name}():".format(**locals())

    # Indent the contents of the circuit function.
    ltab = tab

    # Template for divider between function sections.
    section_div = "#" + "=" * 79
    section_comment = (
        "\n\n{ltab}{section_div}\n{ltab}# {section_desc}\n{ltab}{section_div}\n\n"
    )

    # Component template section.
    section_desc = "Component templates."
    skidl += section_comment.format(**locals())
    comp_templates = {comp_key(comp): comp for comp in ntlst.parts}
    template_statements = sorted(
        [template_comp_to_skidl(c) for c in list(comp_templates.values())]
    )
    skidl += "\n".join(template_statements)

    # Component instantiation section.
    section_desc = "Component instantiations."
    skidl += section_comment.format(**locals())
    comp_inst_statements = sorted(
        [comp_to_skidl(c, comp_templates) for c in ntlst.parts]
    )
    skidl += "\n".join(comp_inst_statements)

    # Net instantiation section.
    section_desc = "Net interconnections between instantiated components."
    skidl += section_comment.format(**locals())
    net_statements = sorted([net_to_skidl(n) for n in ntlst.nets])
    skidl += "\n".join(net_statements)

    # End of circuit function. Now call it to instantiate the circuit and generate the netlist.
    ltab = ""
    section_desc = "Instantiate the circuit and generate the netlist."
    skidl += section_comment.format(**locals())
    ltab = tab
    skidl += 'if __name__ == "__main__":\n'
    skidl += "{ltab}{circuit_name}()\n".format(**locals())
    skidl += "{ltab}generate_netlist()\n".format(**locals())

    return skidl
