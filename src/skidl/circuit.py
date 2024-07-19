# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Handles complete circuits made of parts and nets.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import functools
import json
import re
import subprocess
import time
from builtins import range, str, super
from collections import Counter, deque

import graphviz

try:
    from future import standard_library

    standard_library.install_aliases()
except ImportError:
    pass

from .bus import Bus
from .common import builtins
from .erc import dflt_circuit_erc
from .group import Group
from .logger import active_logger, erc_logger, stop_log_file_output
from .net import NCNet, Net
from .part import Part, PartUnit
from .pckg_info import __version__
from .pin import Pin
from .schlib import SchLib
from .scriptinfo import get_script_name, get_skidl_trace
from .skidlbaseobj import SkidlBaseObject
from .utilities import (
    expand_buses,
    export_to_all,
    flatten,
    num_to_chars,
    opened,
    reset_get_unique_name,
)


HIER_SEP = "."  # Separator for hierarchy labels.


__all__ = ["HIER_SEP"]


@export_to_all
class Circuit(SkidlBaseObject):
    """
    Class object that holds the entire netlist of parts and nets.

    Attributes:
        parts: List of all the schematic parts as Part objects.
        nets: List of all the schematic nets as Net objects.
        buses: List of all the buses as Bus objects.
        hierarchy: A '.'-separated concatenation of the names of nested
            SubCircuits at the current time it is read.
        level: The current level in the schematic hierarchy.
        context: Stack of contexts for each level in the hierarchy.
    """

    # Set the default ERC functions for all Circuit instances.
    erc_list = [dflt_circuit_erc]

    def __init__(self, **kwargs):
        super().__init__()

        """Initialize the Circuit object."""
        self.reset(init=True)

        # Set passed-in attributes for the circuit.
        for k, v in list(kwargs.items()):
            setattr(self, k, v)

    def __iadd__(self, *stuff):
        """Add Parts, Nets, Buses, and Interfaces to the circuit."""
        return self.add_stuff(*stuff)

    def __isub__(self, *stuff):
        """Remove Parts, Nets, Buses, and Interfaces from the circuit."""
        return self.rmv_stuff(*stuff)

    def __enter__(self):
        """Create a context for making this circuit the default_circuit."""
        self.circuit_stack.append(default_circuit)
        builtins.default_circuit = self
        return self

    def __exit__(self, type, value, traceback):
        builtins.default_circuit = self.circuit_stack.pop()

    def mini_reset(self, init=False):
        """Clear any circuitry but don't erase any loaded part libraries."""

        self.group_name_cntr = Counter()

        self.name = ""
        self.parts = []
        self.nets = []
        self.netclasses = {}
        self.buses = []
        self.interfaces = []
        self.packages = deque()
        self.hierarchy = "top"
        self.level = 0
        self.context = [("top",)]
        self.erc_assertion_list = []
        self.circuit_stack = (
            []
        )  # Stack of previous default_circuits for context manager.
        self.no_files = False  # Allow creation of files for netlists, ERC, libs, etc.

        # Internal set used to check for duplicate hierarchical names.
        self._hierarchical_names = {self.hierarchy}

        # Clear the name heap for nets and parts.
        reset_get_unique_name()

        # Clear out the no-connect net and set the global no-connect if it's
        # tied to this circuit.
        self.NC = NCNet(
            name="__NOCONNECT", circuit=self
        )  # Net for storing no-connects for parts in this circuit.
        if not init and self is default_circuit:
            builtins.NC = self.NC

    def reset(self, init=False):
        """Clear any circuitry and cached part libraries and start over."""

        try:
            from . import skidl

            config = skidl.config
        except ImportError:
            # For Python 2. Always gotta be different...
            from .skidl import config

        # Clear circuitry.
        self.mini_reset(init)

        # Also clear any cached libraries.
        SchLib.reset()

        # Clear out any old backup lib so the new one will get reloaded when it's needed.
        config.backup_lib = None

    def add_hierarchical_name(self, name):
        """Record a new hierarchical name.  Throw an error if it is a duplicate."""
        if name in self._hierarchical_names:
            active_logger.raise_(
                ValueError,
                "Can't add duplicate hierarchical name {} to this circuit.".format(
                    name
                ),
            )
        self._hierarchical_names.add(name)

    def rmv_hierarchical_name(self, name):
        """Remove an existing hierarchical name.  Throw an error if non-existent."""
        try:
            self._hierarchical_names.remove(name)
        except KeyError:
            active_logger.raise_(
                ValueError,
                "Can't remove non-existent hierarchical name {} from circuit.".format(
                    name
                ),
            )

    def activate(self, name, tag):
        """Save the previous hierarchical group and activate a new one."""

        # Create a name for this group from the concatenated names of all
        # the nested contexts that were called on all the preceding levels
        # that led to this one. Also, add a distinct tag to the current
        # name to disambiguate multiple uses of the same function.  This is
        # either specified as an argument, or an incrementing value is used.
        grp_hier_name = self.hierarchy + HIER_SEP + name
        if tag is None:
            tag = self.group_name_cntr[grp_hier_name]
            self.group_name_cntr[grp_hier_name] += 1

        # Save the context from which this was called.
        self.context.append((default_circuit, self.hierarchy))

        # Create a new hierarchical name in the activated context.
        self.hierarchy = self.hierarchy + HIER_SEP + name + str(tag)
        self.add_hierarchical_name(self.hierarchy)

        # Setup some globals needed in this context.
        builtins.default_circuit = self
        builtins.NC = self.NC  # pylint: disable=undefined-variable

    def deactivate(self):
        """Deactivate the current hierarchical group and return to the previous one."""

        # Restore the context that existed before this one was created.
        # This does not remove the circuitry since it has already been
        # added to the part and net lists.
        builtins.default_circuit, self.hierarchy = self.context.pop()
        builtins.NC = default_circuit.NC

    def add_parts(self, *parts):
        """Add some Part objects to the circuit."""
        for part in parts:
            # Add the part to this circuit if the part is movable and
            # it's not already in this circuit.
            if part.circuit != self:
                if part.is_movable():

                    # Remove the part from the circuit it's already in.
                    if isinstance(part.circuit, Circuit):
                        part.circuit -= part

                    # Add the part to this circuit.
                    part.circuit = self  # Record the Circuit object for this part.
                    part.ref = part.ref  # Adjusts the part reference if necessary.

                    # Store hierarchy of part.
                    part.hierarchy = self.hierarchy

                    # Check the part does not have a conflicting hierarchical name
                    self.add_hierarchical_name(part.hierarchical_name)

                    # Store part instantiation trace.
                    part.skidl_trace = ";".join(get_skidl_trace())

                    self.parts.append(part)
                else:
                    active_logger.raise_(
                        ValueError,
                        "Can't add unmovable part {} to this circuit.".format(part.ref),
                    )

    def rmv_parts(self, *parts):
        """Remove some Part objects from the circuit."""
        for part in parts:
            part.disconnect()
            if part.is_movable():
                if part.circuit == self and part in self.parts:
                    self.rmv_hierarchical_name(part.hierarchical_name)
                    part.circuit = None
                    part.hierarchy = None
                    self.parts.remove(part)
                else:
                    active_logger.warning(
                        "Removing non-existent part {} from this circuit.".format(
                            part.ref
                        )
                    )
            else:
                active_logger.raise_(
                    ValueError,
                    "Can't remove part {} from this circuit.".format(part.ref),
                )

    def add_nets(self, *nets):
        """Add some Net objects to the circuit. Assign a net name if necessary."""
        for net in nets:
            # Add the net to this circuit if the net is movable and
            # it's not already in this circuit.
            if net.circuit != self:
                if net.is_movable():

                    # Remove the net from the circuit it's already in.
                    if isinstance(net.circuit, Circuit):
                        net.circuit -= net

                    # Add the net to this circuit.
                    net.circuit = self  # Record the Circuit object the net belongs to.
                    net.name = net.name
                    net.hierarchy = self.hierarchy  # Store hierarchy of net.

                    self.nets.append(net)

                else:
                    active_logger.raise_(
                        ValueError,
                        "Can't add unmovable net {} to this circuit.".format(net.name),
                    )

    def rmv_nets(self, *nets):
        """Remove some Net objects from the circuit."""
        for net in nets:
            if net.is_movable():
                if net.circuit == self and net in self.nets:
                    net.circuit = None
                    net.hierarchy = None
                    self.nets.remove(net)
                else:
                    active_logger.warning(
                        "Removing non-existent net {} from this circuit.".format(
                            net.name
                        )
                    )
            else:
                active_logger.raise_(
                    ValueError,
                    "Can't remove unmovable net {} from this circuit.".format(net.name),
                )

    def add_buses(self, *buses):
        """Add some Bus objects to the circuit. Assign a bus name if necessary."""
        for bus in buses:
            # Add the bus to this circuit if the bus is movable and
            # it's not already in this circuit.
            if bus.circuit != self:
                if bus.is_movable():

                    # Remove the bus from the circuit it's already in, but skip
                    # this if the bus isn't already in a Circuit.
                    if isinstance(bus.circuit, Circuit):
                        bus.circuit -= bus

                    # Add the bus to this circuit.
                    bus.circuit = self
                    bus.name = bus.name
                    bus.hierarchy = self.hierarchy  # Store hierarchy of the bus.

                    self.buses.append(bus)
                    for net in bus.nets:
                        self += net

    def rmv_buses(self, *buses):
        """Remove some buses from the circuit."""
        for bus in buses:
            if bus.is_movable():
                if bus.circuit == self and bus in self.buses:
                    bus.circuit = None
                    bus.hierarchy = None
                    self.buses.remove(bus)
                    for net in bus.nets:
                        self -= net
                else:
                    active_logger.warning(
                        "Removing non-existent bus {} from this circuit.".format(
                            bus.name
                        )
                    )
            else:
                active_logger.raise_(
                    ValueError,
                    "Can't remove unmovable bus {} from this circuit.".format(bus.name),
                )

    def add_packages(self, *packages):
        for package in packages:
            if package.circuit is None:
                if package.is_movable():

                    # Add the package to this circuit.
                    self.packages.appendleft(package)
                    package.circuit = self
                    for obj in package.values():
                        try:
                            if obj.is_movable():
                                obj.circuit = self
                        except AttributeError:
                            pass
            else:
                active_logger.raise_(
                    ValueError,
                    "Can't add the same package to more than one circuit.",
                )

    def rmv_packages(self, *packages):
        for package in packages:
            if package.is_movable():
                if package.circuit == self and package in self.packages:
                    self.packages.remove(package)
                    package.circuit = None
                    for obj in package.values():
                        try:
                            if obj.is_movable():
                                obj.circuit = None
                        except AttributeError:
                            pass
                else:
                    active_logger.active_logger.warning(
                        "Removing non-existent package {} from this circuit.".format(
                            package.name
                        )
                    )
            else:
                active_logger.raise_(
                    ValueError,
                    "Can't remove unmovable package {} from this circuit.".format(
                        package.name
                    ),
                )

    def add_stuff(self, *stuff):
        """Add Parts, Nets, Buses, and Interfaces to the circuit."""

        from .package import Package

        for thing in flatten(stuff):
            if isinstance(thing, Part):
                self.add_parts(thing)
            elif isinstance(thing, Net):
                self.add_nets(thing)
            elif isinstance(thing, Bus):
                self.add_buses(thing)
            elif isinstance(thing, Package):
                self.add_packages(thing)
            else:
                active_logger.raise_(
                    ValueError,
                    "Can't add a {} to a Circuit object.".format(type(thing)),
                )
        return self

    def rmv_stuff(self, *stuff):
        """Remove Parts, Nets, Buses, and Interfaces from the circuit."""

        from .package import Package

        for thing in flatten(stuff):
            if isinstance(thing, Part):
                self.rmv_parts(thing)
            elif isinstance(thing, Net):
                self.rmv_nets(thing)
            elif isinstance(thing, Bus):
                self.rmv_buses(thing)
            elif isinstance(thing, Package):
                self.rmv_packages(thing)
            else:
                active_logger.raise_(
                    ValueError,
                    "Can't remove a {} from a Circuit object.".format(type(thing)),
                )
        return self

    def get_nets(self):
        """Get all the distinct nets for the circuit."""

        distinct_nets = []
        for net in self.nets:
            if net is self.NC:
                # Exclude no-connect net.
                continue
            if not net.pins:
                # Exclude empty nets with no attached pins.
                continue
            for n in distinct_nets:
                # Exclude net if its already attached to a previously selected net.
                if net.is_attached(n):
                    break
            else:
                # This net is not attached to any of the other distinct nets,
                # so it is also distinct.
                distinct_nets.append(net)
        return distinct_nets

    def instantiate_packages(self):
        """Run the package executables to instantiate their circuitry."""

        # Set default_circuit to this circuit and instantiate the packages.
        with self:
            while self.packages:
                package = self.packages.pop()

                # If there are still ProtoNets attached to the package at this point,
                # just replace them with Nets. This will allow any internal connections
                # inside the package to be reflected on the package I/O pins.
                # **THIS WILL PROBABLY FAIL IF THE INTERNAL CONNECTIONS ARE BUSES.**
                # DISABLE THIS FOR NOW...
                # for k, v in package.items():
                #     if isinstance(v, ProtoNet):
                #         package[k] = Net()

                # Call the function to instantiate the package with its arguments.
                package.subcircuit(**package)

    def merge_net_names(self):
        """Assign same name to all segments of multi-segment nets."""

        for net in self.nets:
            if len(net.nets) > 1:
                net.merge_names()

    def merge_nets(self):
        """Merge multi-segment nets into a single net."""

        merged_nets = set()
        for net in self.nets:
            if len(net.nets) > 1 and net not in merged_nets:

                # Select a single name for the net segments.
                net.merge_names()

                # Record merged nets so they aren't processed again.
                merged_nets.update(set(net.nets) - {net})

                # Move all pins to a single segment.
                for pin in net.pins:
                    pin.move(net)

        # Remove merged nets from the circuit.
        self.nets = list(set(self.nets) - merged_nets)

    def ERC(self, *args, **kwargs):
        """Run class-wide and local ERC functions on this circuit."""

        # Save the currently active logger and activate the ERC logger.
        active_logger.push(erc_logger)

        # Reset the counters to clear any warnings/errors from previous ERC run.
        active_logger.error.reset()
        active_logger.warning.reset()

        self._preprocess()

        if self.no_files:
            active_logger.stop_file_output()

        super().ERC(*args, **kwargs)

        active_logger.report_summary("running ERC")

        # Restore the logger that was active before the ERC.
        active_logger.pop()

    def generate_netlist(self, **kwargs):
        """
        Return a netlist and also write it to a file/stream.

        Args:
            file_: Either a file object that can be written to, or a string
                containing a file name, or None.
            tool: The EDA tool the netlist will be generated for.
            do_backup: If true, create a library with all the parts in the circuit.

        Returns:
            A netlist.
        """

        from . import skidl
        from .tools import tool_modules

        # Reset the counters to clear any warnings/errors from previous run.
        active_logger.error.reset()
        active_logger.warning.reset()

        self._preprocess()

        # Extract arguments:
        #     Get EDA tool the netlist will be generated for.
        #     Get file the netlist will be stored in (if any).
        #     Get flag controlling the generation of a backup library.
        tool = kwargs.pop("tool", skidl.config.tool)
        file_ = kwargs.pop("file_", None)
        do_backup = kwargs.pop("do_backup", True)

        netlist = tool_modules[tool].gen_netlist(self, **kwargs)

        active_logger.report_summary("generating netlist")

        if not self.no_files:
            with opened(file_ or (get_script_name() + ".net"), "w") as f:
                f.write(str(netlist))

        if do_backup:
            self.backup_parts()  # Create a new backup lib for the circuit parts.
            # Clear out any old backup lib so the new one will get reloaded when it's needed.
            skidl.config.backup_lib = None

        return netlist

    def generate_pcb(self, **kwargs):
        """
        Create a PCB file from the circuit.

        Args:
            file_: Either a file object that can be written to, or a string
                containing a file name, or None.
            tool: The EDA tool the netlist will be generated for.
            do_backup: If true, create a library with all the parts in the circuit.
            fp_libs: List of directories containing footprint libraries.
        Returns:
            None.
        """

        from . import skidl
        from .tools import tool_modules

        # Reset the counters to clear any warnings/errors from previous run.
        active_logger.error.reset()
        active_logger.warning.reset()

        self._preprocess()

        # Extract arguments:
        #     Get EDA tool the netlist will be generated for.
        #     Get file the netlist will be stored in (if any).
        #     Get flag controlling the generation of a backup library.
        #     Get list of footprint libraries.
        tool = kwargs.pop("tool", skidl.config.tool)
        file_ = kwargs.pop("file_", None)
        do_backup = kwargs.pop("do_backup", True)
        fp_libs = kwargs.pop("fp_libs", None)

        if not self.no_files:
            if do_backup:
                self.backup_parts()  # Create a new backup lib for the circuit parts.
                # Clear out any old backup lib so the new one will get reloaded when it's needed.
                skidl.config.backup_lib = None
            tool_modules[tool].gen_pcb(self, file_, fp_libs=fp_libs)

        active_logger.report_summary("creating PCB")

    def generate_xml(self, file_=None, tool=None):
        """
        Return netlist as an XML string and also write it to a file/stream.

        Args:
            file_: Either a file object that can be written to, or a string
                containing a file name, or None.
            tool: Backend tool such as KICAD.

        Returns:
            A string containing the netlist.
        """

        from . import skidl
        from .tools import tool_modules

        # Reset the counters to clear any warnings/errors from previous run.
        active_logger.error.reset()
        active_logger.warning.reset()

        self._preprocess()

        tool = tool or skidl.config.tool
        netlist = tool_modules[tool].gen_xml(self)

        if not self.no_files:
            with opened(file_ or (get_script_name() + ".xml"), "w") as f:
                f.write(netlist)

        active_logger.report_summary("generating XML")

        return netlist

    def generate_netlistsvg_skin(self, net_stubs, layout_options=None):
        """ Generate SVG for schematic symbols for netlistsvg skin file.

        Args:
            net_stubs (list): List of nets that are stubbed rather than routed.
            layout_options (str, optional): String of ELK layout options. Defaults to None.
                                            https://eclipse.dev/elk/reference/options.html

        Returns:
            str: SVG for skin file.
        """

        default_layout_options = """
                org.eclipse.elk.layered.spacing.nodeNodeBetweenLayers="5"
                org.eclipse.elk.layered.compaction.postCompaction.strategy="4"
                org.eclipse.elk.spacing.nodeNode="50"
                org.eclipse.elk.direction="DOWN"
            """

        layout_options = layout_options or default_layout_options

        # Generate the SVG for each part in the required transformations.
        part_svg = {}
        for part in self.parts:

            # If this part is attached to any net stubs, give it a symbol
            # name specifically for this part + stubs.
            if part.attached_to(net_stubs):
                # This part is attached to net stubs, so give it
                # a symbol name specifically for this part + stubs.
                symbol_name = part.name + "_" + part.ref
            else:
                # This part is not attached to any stubs, so give it
                # a symbol name for this generic part symbol.
                symbol_name = part.name

            # Get the global transformation for the part symbol.
            if len(part.unit) == 1:
                # If there is only a single unit, then that unit is the same as the part.
                # Therefore, ignore the global transformation for the part since we'll
                # pick it up from the unit transformation instead.
                global_symtx = ""
            else:
                # If there are zero units or more than one unit, then use the
                # global transformation for the part or apply it to the units.
                global_symtx = getattr(part, "symtx", "")

            # Get the transformation for each part unit (if any).
            unit_symtx = set([""])
            for unit in part.unit.values():
                unit_symtx.add(getattr(unit, "symtx", ""))

            # Each combination of global + unit transformation is one of
            # the total transformations needed for the part.
            total_symtx = [global_symtx + u_symtx for u_symtx in unit_symtx]

            # Generate SVG of the part for each total transformation.
            for symtx in total_symtx:
                name = symbol_name + "_" + symtx
                # Skip any repeats of the part.
                if name not in part_svg.keys():
                    part_svg[name] = part.generate_svg_component(
                        symtx=symtx, net_stubs=net_stubs
                    )

        part_svg = list(part_svg.values())  # Just keep the SVG for the part symbols.

        head_svg = [
            '<svg xmlns="http://www.w3.org/2000/svg"',
            '     xmlns:xlink="http://www.w3.org/1999/xlink"',
            '     xmlns:s="https://github.com/nturley/netlistsvg">',
            "  <s:properties",
            '    constants="false"',
            '    splitsAndJoins="false"',
            '    genericsLaterals="true">',
            "    <s:layoutEngine {layout_options} />",
            "  </s:properties>",
            "<style>",
            "svg {{",
            "  stroke: #000;",
            "  fill: none;",
            "  stroke-linejoin: round;",
            "  stroke-linecap: round;",
            "}}",
            "text {{",
            "  fill: #000;",
            "  stroke: none;",
            "  font-size: 10px;",
            "  font-weight: bold;",
            '  font-family: "Courier New", monospace;',
            "}}",
            ".skidl_text {{",
            "  fill: #999;",
            "  stroke: none;",
            "  font-weight: bold;",
            '  font-family: consolas, "Courier New", monospace;',
            "}}",
            ".pin_num_text {{",
            "    fill: #840000;",
            "}}",
            ".pin_name_text {{",
            "    fill: #008484;",
            "}}",
            ".net_name_text {{",
            "    font-style: italic;",
            "    fill: #840084;",
            "}}",
            ".part_text {{",
            "    fill: #840000;",
            "}}",
            ".part_ref_text {{",
            "    fill: #008484;",
            "}}",
            ".part_name_text {{",
            "    fill: #008484;",
            "}}",
            ".pen_fill {{",
            "    fill: #840000;",
            "}}",
            ".background_fill {{",
            "    fill: #FFFFC2",
            "}}",
            ".nodelabel {{",
            "  text-anchor: middle;",
            "}}",
            ".inputPortLabel {{",
            "  text-anchor: end;",
            "}}",
            ".splitjoinBody {{",
            "  fill: #000;",
            "}}",
            ".symbol {{",
            "  stroke-linejoin: round;",
            "  stroke-linecap: round;",
            "  stroke: #840000;",
            "}}",
            ".detail {{",
            "  stroke-linejoin: round;",
            "  stroke-linecap: round;",
            "  fill: #000;",
            "}}",
            "</style>",
            "",
            "<!-- signal -->",
            '<g s:type="inputExt" s:width="30" s:height="20" transform="translate(0,0)">',
            '  <text x="-2" y="12" text-anchor=\'end\' class="$cell_id pin_name_text" s:attribute="ref">input</text>',
            '  <s:alias val="$_inputExt_"/>',
            '  <path d="M0,0 V20 H15 L30,10 15,0 Z" class="$cell_id symbol"/>',
            '  <g s:x="30" s:y="10" s:pid="Y" s:position="right"/>',
            "</g>",
            "",
            '<g s:type="outputExt" s:width="30" s:height="20" transform="translate(0,0)">',
            '  <text x="32" y="12" class="$cell_id pin_name_text" s:attribute="ref">output</text>',
            '  <s:alias val="$_outputExt_"/>',
            '  <path d="M30,0 V20 H15 L0,10 15,0 Z" class="$cell_id symbol"/>',
            '  <g s:x="0" s:y="10" s:pid="A" s:position="left"/>',
            "</g>",
            "<!-- signal -->",
            "",
            "<!-- builtin -->",
            '<g s:type="generic" s:width="30" s:height="40" transform="translate(0,0)">',
            '  <text x="15" y="-4" class="nodelabel $cell_id" s:attribute="ref">generic</text>',
            '  <rect width="30" height="40" x="0" y="0" s:generic="body" class="$cell_id"/>',
            '  <g transform="translate(30,10)"',
            '     s:x="30" s:y="10" s:pid="out0" s:position="right">',
            '    <text x="5" y="-4" class="$cell_id">out0</text>',
            "  </g>",
            '  <g transform="translate(30,30)"',
            '     s:x="30" s:y="30" s:pid="out1" s:position="right">',
            '    <text x="5" y="-4" class="$cell_id">out1</text>',
            "  </g>",
            '  <g transform="translate(0,10)"',
            '     s:x="0" s:y="10" s:pid="in0" s:position="left">',
            '      <text x="-3" y="-4" class="inputPortLabel $cell_id">in0</text>',
            "  </g>",
            '  <g transform="translate(0,30)"',
            '     s:x="0" s:y="30" s:pid="in1" s:position="left">',
            '    <text x="-3" y="-4" class="inputPortLabel $cell_id">in1</text>',
            "  </g>",
            "</g>",
            "<!-- builtin -->",
        ]

        head_svg = "\n".join(head_svg).format(**locals())
        part_svg = "\n".join(part_svg)
        tail_svg = "</svg>"

        return "\n".join((head_svg, part_svg, tail_svg))

    def get_net_nc_stubs(self):
        """Get all nets/buses that are stubs or no-connects."""

        # Search all nets for those set as stubs or that are no-connects.
        stubs = [
            n for n in self.nets if getattr(n, "stub", False) or isinstance(n, NCNet)
        ]

        # Also find buses that are set as stubs and add their individual nets.
        stubs.extend(expand_buses([b for b in self.buses if getattr(b, "stub", False)]))

        return stubs

    def generate_svg(self, file_=None, tool=None, layout_options=None):
        """
        Create an SVG file displaying the circuit schematic and
        return the dictionary that can be displayed by netlistsvg.

        Args:
            file_ (_type_, optional): Filename to store SVG. Defaults to None.
            tool (_type_, optional): Backend tool. Defaults to None.
            layout_options (_type_, optional): Options to control netlistsvg/ELK layout algorithm. Defaults to None.

        Returns:
            dict: JSON dictionary for input to netlistsvg.
        """

        from . import skidl

        # Reset the counters to clear any warnings/errors from previous run.
        active_logger.error.reset()
        active_logger.warning.reset()

        self._preprocess()

        # Get the list of nets which will be routed and not represented by stubs.
        net_stubs = self.get_net_nc_stubs()
        routed_nets = list(set(self.nets) - set(net_stubs))

        # Assign each routed net a unique integer. Interconnected nets
        # all get the same number.
        net_nums = {}
        for num, net in enumerate(routed_nets, 1):
            for n in net.get_nets():
                if n.name not in net_nums:
                    net_nums[n.name] = num

        io_dict = {"i": "input", "o": "output", "n": "nc"}

        # Assign I/O ports to any named net that has a netio attribute.
        ports = {}
        for net in routed_nets:
            if not net.is_implicit():
                try:
                    # Net I/O direction set by 1st letter of netio attribute.
                    io = io_dict[net.netio.lower()[0]]
                    ports[net.name] = {
                        "direction": io,
                        "bits": [
                            net_nums[net.name],
                        ],
                    }
                except AttributeError:
                    # Net has no netio so don't assign a port.
                    pass

        pin_dir_tbl = {
            Pin.types.INPUT: "input",
            Pin.types.OUTPUT: "output",
            Pin.types.BIDIR: "output",
            Pin.types.TRISTATE: "output",
            Pin.types.PASSIVE: "input",
            Pin.types.PULLUP: "output",
            Pin.types.PULLDN: "output",
            Pin.types.UNSPEC: "input",
            Pin.types.PWRIN: "input",
            Pin.types.PWROUT: "output",
            Pin.types.OPENCOLL: "output",
            Pin.types.OPENEMIT: "output",
            Pin.types.NOCONNECT: "nc",
        }

        cells = {}
        for part in self.parts:

            if part.attached_to(net_stubs):
                # If the part is attached to any net stubs, it will require
                # an individualized symbol in the netlistsvg skin file.
                # Give it a unique symbol name so it can be found later.
                part_name = part.name + "_" + part.ref
            else:
                # Otherwise, no net stubs so use the name of the
                # generic symbol for this part.
                part_name = part.name

            part_symtx = getattr(part, "symtx", "")

            # Get a list of the units in the part.
            if len(part.unit) <= 1:
                # If there are no units, then use the part itself as a unit.
                # If there is only one unit, then that unit is just the part itself, so use it.
                units = [part]
            else:
                units = part.unit.values()

            for unit in units:

                if not unit.is_connected():
                    continue  # Skip unconnected parts.

                pins = unit.get_pins()

                # Associate each connected pin of a part with the assigned net number.
                connections = {
                    pin.num: [
                        net_nums[pin.net.name],
                    ]
                    for pin in pins
                    if pin.net in routed_nets
                }

                # Assign I/O to each part pin by either using the pin's symio
                # attribute or by using its pin function.
                part_pin_dirs = {
                    pin.num: io_dict[
                        getattr(pin, "symio", pin_dir_tbl[pin.func]).lower()[0]
                    ]
                    for pin in pins
                }
                # Keep only input/output pins. Remove no-connect pins.
                part_pin_dirs = {n: d for n, d in part_pin_dirs.items() if d[0] in "io"}

                # Determine which symbol in the skin file goes with this part.
                unit_symtx = part_symtx + getattr(unit, "symtx", "")
                if not isinstance(unit, PartUnit):
                    ref = part.ref
                    name = part_name + "_1_" + part_symtx
                else:
                    ref = part.ref + num_to_chars(unit.num)
                    name = part_name + "_" + str(unit.num) + "_" + unit_symtx

                # Create the cell that netlistsvg uses to draw the part and connections.
                cells[ref] = {
                    "type": name,
                    "port_directions": part_pin_dirs,
                    "connections": connections,
                    "attributes": {
                        "value": str(part.value),
                    },
                }

        schematic_json = {
            "modules": {
                self.name: {
                    "ports": ports,
                    "cells": cells,
                }
            }
        }

        if not self.no_files:
            file_basename = file_ or get_script_name()
            json_file = file_basename + ".json"
            svg_file = file_basename + ".svg"

            with opened(json_file, "w") as f:
                f.write(
                    json.dumps(
                        schematic_json, sort_keys=True, indent=2, separators=(",", ": ")
                    )
                )

            skin_file = file_basename + "_skin.svg"
            with opened(skin_file, "w") as f:
                f.write(
                    self.generate_netlistsvg_skin(
                        net_stubs=net_stubs, layout_options=layout_options
                    )
                )

            subprocess.Popen(
                ["netlistsvg", json_file, "--skin", skin_file, "-o", svg_file],
                shell=False,
            )

        active_logger.report_summary("generating SVG")

        return schematic_json

    def generate_schematic(self, **kwargs):
        """
        Create a schematic from a Circuit.
        """

        import skidl

        from .tools import tool_modules

        # Reset the counters to clear any warnings/errors from previous run.
        active_logger.error.reset()
        active_logger.warning.reset()

        # Supply a schematic-specific empty footprint handler.
        save_empty_footprint_handler = skidl.empty_footprint_handler

        def _empty_footprint_handler(part):
            """Handle the situation of a Part with no footprint when generating a schematic."""

            active_logger.warning(
                "No footprint for {part}/{ref}.".format(part=part.name, ref=part.ref)
            )

            # Supply a nonsense footprint just so no complaints are raised when the EESCHEMA code is generated.
            part.footprint = ":"

        if kwargs.get("empty_footprint_handler]"):
            skidl.empty_footprint_handler = kwargs["empty_footprint_handler"]
        else:
            skidl.empty_footprint_handler = _empty_footprint_handler

        self._preprocess()

        tool = kwargs.pop("tool", skidl.config.tool)

        try:
            tool_modules[tool].gen_schematic(self, **kwargs)
        finally:
            skidl.empty_footprint_handler = save_empty_footprint_handler

        active_logger.report_summary("generating schematic")

    def generate_dot(
        self,
        file_=None,
        engine="neato",
        rankdir="LR",
        part_shape="rectangle",
        net_shape="point",
        splines=None,
        show_values=True,
        show_anon=False,
        split_nets=["GND"],
        split_parts_ref=[],
    ):
        """
        Returns a graphviz graph as graphviz object and can also write it to a file/stream.
        When used in ipython the graphviz object will drawn as an SVG in the output.

        See https://graphviz.readthedocs.io/en/stable/ and http://graphviz.org/doc/info/attrs.html

        Args:
            file_: A string containing a file name, or None.
            engine: See graphviz documentation
            rankdir: See graphviz documentation
            part_shape: Shape of the part nodes
            net_shape: Shape of the net nodes
            splines: Style for the edges, try 'ortho' for a schematic like feel
            show_values: Show values as external labels on part nodes
            show_anon: Show anonymous net names
            split_nets: splits up the plot for the given list of net names
            split_parts_ref: splits up the plot for all pins for the given list of part refs

        Returns:
            graphviz.Digraph
        """

        # Reset the counters to clear any warnings/errors from previous run.
        active_logger.error.reset()
        active_logger.warning.reset()

        self._preprocess()

        dot = graphviz.Digraph(engine=engine)
        dot.attr(rankdir=rankdir, splines=splines)

        nets = self.get_nets()

        # try and keep things in the same order
        nets.sort(key=lambda n: n.name.lower())

        # Add stubbed nets to split_nets:
        split_nets = split_nets[:]  # Make a local copy.
        split_nets.extend([n.name for n in nets if getattr(n, "stub", False)])

        for i, n in enumerate(nets):
            xlabel = n.name
            if not show_anon and n.is_implicit():
                xlabel = None
            if n.name not in split_nets:
                dot.node(n.name, shape=net_shape, xlabel=xlabel)

            for j, pin in enumerate(n.pins):
                net_ref = n.name
                pin_part_ref = pin.part.ref

                if n.name in split_nets:
                    net_ref += str(j)
                    dot.node(net_ref, shape=net_shape, xlabel=xlabel)
                if pin.part.ref in split_parts_ref and n.name not in split_nets:
                    label = pin.part.ref + ":" + pin.name

                    # add label to part
                    net_ref_part = "%s_%i_%i" % (net_ref, i, j)
                    dot.node(net_ref_part, shape=net_shape, xlabel=label)
                    dot.edge(pin_part_ref, net_ref_part, arrowhead="none")

                    # add label to splited net
                    pin_part_ref = "%s_%i_%i" % (pin_part_ref, i, j)
                    dot.node(pin_part_ref, shape=net_shape, xlabel=label)
                    dot.edge(pin_part_ref, net_ref, arrowhead="none")
                else:
                    dot.edge(
                        pin_part_ref, net_ref, arrowhead="none", taillabel=pin.name
                    )

        for p in sorted(self.parts, key=lambda p: p.ref.lower()):
            xlabel = None
            if show_values:
                xlabel = str(p.value)
            dot.node(p.ref, shape=part_shape, xlabel=xlabel)

        if not self.no_files:
            if file_ is not None:
                dot.save(file_)

        active_logger.report_summary("generating DOT")

        return dot

    generate_graph = generate_dot  # Old method name for generating graphviz dot file.

    def backup_parts(self, file_=None):
        """
        Saves parts in circuit as a SKiDL library in a file.

        Args:
            file: Either a file object that can be written to, or a string
                containing a file name, or None. If None, a standard library
                file will be used.

        Returns:
            Nothing.
        """

        from . import skidl
        from skidl import SKIDL

        if self.no_files:
            return

        self._preprocess()

        lib = SchLib(tool=SKIDL)  # Create empty library.
        for p in self.parts:
            lib += p

        file_ = file_ or skidl.config.backup_lib_file_name

        lib.export(libname=skidl.config.backup_lib_name, file_=file_)

    def _check_for_empty_footprints(self):
        """Make sure part footprints aren't empty before generating netlist/PCB."""

        for part in self.parts:
            if getattr(part, "footprint", "") == "":
                import skidl

                skidl.empty_footprint_handler(part)

    def _cull_unconnected_parts(self):
        """Remove parts that aren't connected to anything."""

        for part in self.parts:
            if not part.is_connected():
                self -= part

    def _preprocess(self):
        """Prepare the circuit for generating a netlist, PCB, etc."""

        self.instantiate_packages()
        # self._cull_unconnected_parts()
        self.merge_nets()
        self._check_for_empty_footprints()

    @property
    def no_files(self):
        """Prevent creation of output files (netlists, ERC, logs) by this Circuit object."""
        return self._no_files

    @no_files.setter
    def no_files(self, stop):
        """Don't output any files if stop is True."""
        self._no_files = stop
        stop_log_file_output(stop)
