# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Circuit management in SKiDL.

This module provides the Circuit class which serves as the central container
for all circuit elements (parts, nets, buses) and their interconnections. 
It handles hierarchical circuit structures, electrical rule checking (ERC),
and output generation (netlists, PCBs, SVGs, etc.).
"""

import builtins
import json
import subprocess
from collections import Counter, deque

import graphviz

try:
    from future import standard_library

    standard_library.install_aliases()
except ImportError:
    pass

from .bus import Bus
from .erc import dflt_circuit_erc
from .group import Group
from .logger import active_logger, erc_logger, stop_log_file_output
from .net import NCNet, Net
from .part import Part, PartUnit
from .pckg_info import __version__
from .pin import pin_types
from .schlib import SchLib
from .scriptinfo import get_script_dir, get_script_name, get_skidl_trace
from .skidlbaseobj import SkidlBaseObject
from .utilities import (
    detect_os,
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
    Container for an entire electronic circuit design.
    
    The Circuit class is the central repository for all the parts, nets, buses,
    and interfaces that make up a circuit. It manages the hierarchical structure
    of the design, performs electrical rule checking, and generates various outputs
    like netlists, PCB files, and graphical representations.
    
    Attributes:
        parts (list): List of all parts in the circuit.
        nets (list): List of all nets in the circuit.
        buses (list): List of all buses in the circuit.
        interfaces (list): List of all interfaces in the circuit.
        hierarchy (str): Current position in the hierarchy, represented as a dot-separated string.
        level (int): Current level in the hierarchy.
        context (list): Stack tracking the context at each hierarchical level.
        erc_list (list): List of ERC (Electrical Rule Checking) functions to run on the circuit.
        NC (Net): The special no-connect net used in this circuit.
    """

    # Set the default ERC functions for all Circuit instances.
    erc_list = [dflt_circuit_erc]

    def __init__(self, **kwargs):
        """
        Initialize a new Circuit object.
        
        Args:
            **kwargs: Arbitrary keyword arguments to set as attributes of the circuit.
        """
        super().__init__()

        # Store the directory of the top-level script when this Circuit is first created.
        self.script_dir = get_script_dir()
        self.track_src = True # By default, put track source info into outputs like netlists.
        self.track_abs_path = False  # By default, track using relative paths.

        self.reset(init=True)

        # Set passed-in attributes for the circuit.
        for k, v in list(kwargs.items()):
            setattr(self, k, v)

    def __iadd__(self, *stuff):
        """
        Add parts, nets, buses, and interfaces to the circuit.
        
        Args:
            *stuff: Various circuit elements to add.
            
        Returns:
            Circuit: The updated circuit with new elements.
        """
        return self.add_stuff(*stuff)

    def __isub__(self, *stuff):
        """
        Remove parts, nets, buses, and interfaces from the circuit.
        
        Args:
            *stuff: Various circuit elements to remove.
            
        Returns:
            Circuit: The updated circuit with elements removed.
        """
        return self.rmv_stuff(*stuff)

    def __enter__(self):
        """
        Create a context to make this circuit the default_circuit.
        
        Returns:
            Circuit: This circuit instance.
        """
        self.circuit_stack.append(default_circuit)
        builtins.default_circuit = self
        return self

    def __exit__(self, type, value, traceback):
        """
        Exit the context and restore the previous default_circuit.
        
        Args:
            type: Exception type if an exception occurred.
            value: Exception value if an exception occurred.
            traceback: Traceback if an exception occurred.
        """
        builtins.default_circuit = self.circuit_stack.pop()

    def mini_reset(self, init=False):
        """
        Clear any circuitry but don't erase any loaded part libraries.
        
        Args:
            init (bool, optional): True if this is being called during initialization.
        """

        self.group_name_cntr = Counter()

        self.name = ""
        self.parts = []
        self.nets = []
        self.netclasses = {}
        self.buses = []
        self.interfaces = []
        self.packages = deque()
        self.hierarchy = "" # top level of the circuitry hierarchy.
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
        """
        Clear any circuitry and cached part libraries and start over.
        
        Args:
            init (bool, optional): True if this is being called during initialization.
        """

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
        """
        Record a new hierarchical name and check for duplicates.
        
        Args:
            name (str): Hierarchical name to add.
            
        Raises:
            ValueError: If the name is a duplicate.
        """
        if name in self._hierarchical_names:
            active_logger.raise_(
                ValueError,
                "Can't add duplicate hierarchical name {} to this circuit.".format(
                    name
                ),
            )
        self._hierarchical_names.add(name)

    def rmv_hierarchical_name(self, name):
        """
        Remove an existing hierarchical name.
        
        Args:
            name (str): Hierarchical name to remove.
            
        Raises:
            ValueError: If the name doesn't exist.
        """
        try:
            self._hierarchical_names.remove(name)
        except KeyError:
            active_logger.raise_(
                ValueError,
                "Can't remove non-existent hierarchical name {} from circuit.".format(
                    name
                ),
            )

    def get_node_names(self):
        """
        Get the names of all subcircuits/groups in the hierarchy.
        
        Returns:
            tuple: Tuple of node names in the circuit hierarchy.
        """
        node_names = set()
        for part in self.parts:
            part_hier_pieces = part.hierarchy.split(HIER_SEP)
            for i in range(len(part_hier_pieces)):
                node_names.add(HIER_SEP.join(part_hier_pieces[:i + 1]))
        return tuple(node_names)

    def activate(self, name, tag):
        """
        Activate a new hierarchical group and save the previous one.
        
        This method saves the current context and creates a new hierarchical level
        with the given name and tag.
        
        Args:
            name (str): Name for the new hierarchical level.
            tag: Tag to disambiguate multiple instances of the same hierarchical name.
                 If None, an incrementing counter will be used.
        """

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
        """
        Deactivate the current hierarchical group and return to the previous one.
        
        This restores the context that existed before the current one was created.
        """

        # Restore the context that existed before this one was created.
        # This does not remove the circuitry since it has already been
        # added to the part and net lists.
        builtins.default_circuit, self.hierarchy = self.context.pop()
        builtins.NC = default_circuit.NC

    def add_parts(self, *parts):
        """
        Add parts to the circuit.
        
        Args:
            *parts: Part objects to add to the circuit.
            
        Raises:
            ValueError: If attempting to add an unmovable part.
        """
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
                    part.skidl_trace = get_skidl_trace(track_abs_path=self.track_abs_path)

                    self.parts.append(part)
                else:
                    active_logger.raise_(
                        ValueError,
                        "Can't add unmovable part {} to this circuit.".format(part.ref),
                    )

    def rmv_parts(self, *parts):
        """
        Remove parts from the circuit.
        
        Args:
            *parts: Part objects to remove from the circuit.
            
        Raises:
            ValueError: If attempting to remove an unmovable part.
        """
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
        """
        Add nets to the circuit.
        
        Args:
            *nets: Net objects to add to the circuit.
            
        Raises:
            ValueError: If attempting to add an unmovable net.
        """
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
        """
        Remove nets from the circuit.
        
        Args:
            *nets: Net objects to remove from the circuit.
            
        Raises:
            ValueError: If attempting to remove an unmovable net.
        """
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
        """
        Add buses to the circuit.
        
        Args:
            *buses: Bus objects to add to the circuit.
            
        Raises:
            ValueError: If attempting to add an unmovable bus.
        """
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
        """
        Remove buses from the circuit.
        
        Args:
            *buses: Bus objects to remove from the circuit.
            
        Raises:
            ValueError: If attempting to remove an unmovable bus.
        """
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

    def add_stuff(self, *stuff):
        """
        Add various circuit elements to the circuit.
        
        Args:
            *stuff: Parts, nets, buses, or interfaces to add.
            
        Returns:
            Circuit: The updated circuit.
            
        Raises:
            ValueError: If attempting to add an unsupported type.
        """

        for thing in flatten(stuff):
            if isinstance(thing, Part):
                self.add_parts(thing)
            elif isinstance(thing, Net):
                self.add_nets(thing)
            elif isinstance(thing, Bus):
                self.add_buses(thing)
            else:
                active_logger.raise_(
                    ValueError,
                    "Can't add a {} to a Circuit object.".format(type(thing)),
                )
        return self

    def rmv_stuff(self, *stuff):
        """
        Remove various circuit elements from the circuit.
        
        Args:
            *stuff: Parts, nets, buses, interfaces, or packages to remove.
            
        Returns:
            Circuit: The updated circuit.
            
        Raises:
            ValueError: If attempting to remove an unsupported type.
        """

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
        """
        Get all distinct nets in the circuit.
        
        This excludes the no-connect net, empty nets, and nets that are electrically
        connected to other nets already in the result list.
        
        Returns:
            list: List of distinct nets in the circuit.
        """

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

    def merge_net_names(self):
        """
        Assign the same name to all segments of multi-segment nets.
        
        This ensures that connected nets share a common name.
        """

        for net in self.nets:
            if len(net.nets) > 1:
                net.merge_names()

    def merge_nets(self):
        """
        Merge multi-segment nets into a single net.
        
        Note: Multi-segment nets had to be merged or else tests to detect the
            same net would fail in routing.py when generating schematics.
            But as a result of merging, net variables can become invalid because of new merging.
            Therefore, only do this when generating schematics so other generate_*() functions
            will not be affected.
        """

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
        """
        Perform Electrical Rule Checking on the circuit.
        
        This method runs both the class-wide ERC functions and any local ERC functions 
        defined for this circuit. It checks for issues like unconnected pins, pin type
        conflicts, etc.
        
        Args:
            *args: Arguments to pass to the ERC functions.
            **kwargs: Keyword arguments to pass to the ERC functions.
        """

        # Save the currently active logger and activate the ERC logger.
        active_logger.push(erc_logger)

        # Reset the counters to clear any warnings/errors from previous ERC run.
        active_logger.error.reset()
        active_logger.warning.reset()

        self.merge_net_names()

        if self.no_files:
            active_logger.stop_file_output()

        super().ERC(*args, **kwargs)

        active_logger.report_summary("running ERC")

        # Restore the logger that was active before the ERC.
        active_logger.pop()

    def cull_unconnected_parts(self):
        """
        Remove parts that aren't connected to anything in the circuit.
        
        This can be useful to clean up a design by removing unused parts.
        """

        for part in self.parts:
            if not part.is_connected():
                self -= part

    def check_for_empty_footprints(self):
        """
        Check that all parts have assigned footprints.
        
        This method calls the empty_footprint_handler for any parts that
        don't have a footprint assigned.
        """

        for part in self.parts:
            if getattr(part, "footprint", "") == "":
                import skidl

                skidl.empty_footprint_handler(part)

    def check_part_tags(self):
        """
        Check for missing or randomly-assigned part tags.
        
        Part tags are important for maintaining stable associations between
        schematic parts and PCB footprints. This method warns about any
        parts with null or randomly-assigned tags.
        """

        for part in self.parts:
            part.check_for_manual_tag()

    def generate_netlist(self, **kwargs):
        """
        Generate a netlist for the circuit.
        
        Args:
            file_ (str or file object, optional): File to write netlist to.
            tool (str, optional): The EDA tool to generate the netlist for.
            do_backup (bool, optional): If True, create a library with all parts in the circuit.
            **kwargs: Additional arguments passed to the tool-specific netlist generator.
            
        Returns:
            str: The generated netlist as a string.
        """

        from . import skidl
        from .tools import tool_modules

        # Reset the counters to clear any warnings/errors from previous run.
        active_logger.error.reset()
        active_logger.warning.reset()

        self.merge_net_names()

        # Don't do any checks for empty footprints or random/missing tags
        # since this should be done when tool-specific netlists are generated.
        # For example, these checks aren't necessary when generating
        # a SPICE netlist.

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
            file_ (str or file object, optional): File to write PCB data to.
            tool (str, optional): The EDA tool to generate the PCB for.
            do_backup (bool, optional): If True, create a library with all parts in the circuit.
            fp_libs (list, optional): List of directories containing footprint libraries.
            **kwargs: Additional arguments passed to the tool-specific PCB generator.
        """

        from . import skidl
        from .tools import tool_modules

        # Reset the counters to clear any warnings/errors from previous run.
        active_logger.error.reset()
        active_logger.warning.reset()

        self.merge_net_names()

        # Check for things that can cause problems.
        self.check_for_empty_footprints()
        self.check_part_tags()

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
        Generate an XML representation of the circuit.
        
        Args:
            file_ (str or file object, optional): File to write XML data to.
            tool (str, optional): Backend tool to use for XML generation.
            
        Returns:
            str: The generated XML as a string.
        """

        from . import skidl
        from .tools import tool_modules

        # Reset the counters to clear any warnings/errors from previous run.
        active_logger.error.reset()
        active_logger.warning.reset()

        self.merge_net_names()

        tool = tool or skidl.config.tool
        netlist = tool_modules[tool].gen_xml(self)

        if not self.no_files:
            with opened(file_ or (get_script_name() + ".xml"), "w") as f:
                f.write(netlist)

        active_logger.report_summary("generating XML")

        return netlist

    def generate_netlistsvg_skin(self, net_stubs, layout_options=None):
        """
        Generate SVG for schematic symbols for a netlistsvg skin file.
        
        This creates the SVG symbol definitions that will be used by netlistsvg
        to visualize the circuit.
        
        Args:
            net_stubs (list): List of nets that are stubbed rather than routed.
            layout_options (str, optional): String of ELK layout options. Defaults to None.
                                           See https://eclipse.dev/elk/reference/options.html
                                           
        Returns:
            str: SVG content for the skin file.
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
        """
        Get all nets/buses that are stubs or no-connects.
        
        Returns:
            list: List of nets that are stubs or no-connects.
        """

        # Search all nets for those set as stubs or that are no-connects.
        stubs = [
            n for n in self.nets if getattr(n, "stub", False) or isinstance(n, NCNet)
        ]

        # Also find buses that are set as stubs and add their individual nets.
        stubs.extend(expand_buses([b for b in self.buses if getattr(b, "stub", False)]))

        return stubs

    def generate_svg(self, file_=None, tool=None, layout_options=None):
        """
        Create an SVG visualization of the circuit and return the netlistsvg input data.
        
        Args:
            file_ (str, optional): Base filename to store SVG and intermediate files.
            tool (str, optional): Backend tool to use.
            layout_options (str, optional): Options to control netlistsvg/ELK layout algorithm.
            
        Returns:
            dict: JSON dictionary that can be used as input to netlistsvg.
        """

        from . import skidl

        # Reset the counters to clear any warnings/errors from previous run.
        active_logger.error.reset()
        active_logger.warning.reset()

        self.merge_net_names()

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
            pin_types.INPUT: "input",
            pin_types.OUTPUT: "output",
            pin_types.BIDIR: "output",
            pin_types.TRISTATE: "output",
            pin_types.PASSIVE: "input",
            pin_types.PULLUP: "output",
            pin_types.PULLDN: "output",
            pin_types.UNSPEC: "input",
            pin_types.PWRIN: "input",
            pin_types.PWROUT: "output",
            pin_types.OPENCOLL: "output",
            pin_types.OPENEMIT: "output",
            pin_types.NOCONNECT: "nc",
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

            if detect_os() == "Windows":
                subprocess.Popen(
                    ["netlistsvg.cmd", json_file, "--skin", skin_file, "-o", svg_file],
                    shell=False,
                )
            else:
                subprocess.Popen(
                    ["netlistsvg", json_file, "--skin", skin_file, "-o", svg_file],
                    shell=False,
                )

        active_logger.report_summary("generating SVG")

        return schematic_json

    def generate_schematic(self, **kwargs):
        """
        Create a schematic file from the circuit.
        
        This generates a visual representation of the circuit that can be
        opened in an EDA tool like KiCad's Eeschema.
        
        Args:
            **kwargs: Arguments for the schematic generator including:
                empty_footprint_handler (function, optional): Custom handler for parts without footprints.
                tool (str, optional): The EDA tool to generate the schematic for.
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

        self.merge_net_names()
        self.merge_nets() # Merge nets or schematic routing will fail.

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
        Generate a Graphviz DOT visualization of the circuit.
        
        Creates a graphical representation of the circuit as a graph where parts
        and nets are nodes, and connections are edges.
        
        Args:
            file_ (str, optional): File to write the DOT data to.
            engine (str, optional): Graphviz layout engine to use. Default is "neato".
            rankdir (str, optional): Direction of graph layout. Default is "LR" (left to right).
            part_shape (str, optional): Shape to use for part nodes. Default is "rectangle".
            net_shape (str, optional): Shape to use for net nodes. Default is "point".
            splines (str, optional): Style for the edges. Try "ortho" for schematic-like feel.
            show_values (bool, optional): Show part values as labels. Default is True.
            show_anon (bool, optional): Show anonymous net names. Default is False.
            split_nets (list, optional): List of net names to split in visualization. Default is ["GND"].
            split_parts_ref (list, optional): List of part references to split in visualization.
            
        Returns:
            graphviz.Digraph: A Graphviz graph object.
        """

        # Reset the counters to clear any warnings/errors from previous run.
        active_logger.error.reset()
        active_logger.warning.reset()

        self.merge_net_names()

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
        Save all parts in the circuit as a SKiDL library file.
        
        This creates a backup library that can be used to restore the parts
        in the circuit.
        
        Args:
            file_ (str or file object, optional): File to write the library to.
                If None, a standard library file will be used.
        """

        from . import skidl
        from skidl import SKIDL

        if self.no_files:
            return

        self.merge_net_names()

        lib = SchLib(tool=SKIDL)  # Create empty library.
        for p in self.parts:
            lib += p

        file_ = file_ or skidl.config.backup_lib_file_name

        lib.export(libname=skidl.config.backup_lib_name, file_=file_)

    def to_tuple(self):
        """
        Create a nested tuple representation of the circuit for comparison.
        
        The tuple contains sorted tuples of parts and nets information,
        suitable for comparing circuits structurally.
        
        Returns:
            tuple: A tuple containing:
                - A tuple of part representations (ref, name, lib)
                - A tuple of net representations (name, pins)
        """

        self.merge_net_names()
        
        return (
            tuple(
                sorted(
                    (
                        (p.ref, p.name, p.lib.filename)
                        for p in self.parts
                    ),
                    key=lambda x: x[0].lower(),
                )
            ),
            tuple(
                sorted(
                    (
                        (n.name, tuple(sorted(tuple((p.part.ref, p.num) for p in n.get_pins()))))
                        for n in self.get_nets()
                    ),
                    key=lambda x: x[0].lower(),
                )
            ),
        )

    @property
    def no_files(self):
        """
        Control whether output files are generated.
        
        Returns:
            bool: True if file output is suppressed, False otherwise.
        """
        return self._no_files

    @no_files.setter
    def no_files(self, stop):
        """
        Set whether to suppress file output.
        
        Args:
            stop (bool): True to suppress file output, False to allow it.
        """
        self._no_files = stop
        stop_log_file_output(stop)
