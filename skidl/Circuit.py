# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2018 by XESS Corp.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Handles complete circuits made of parts and nets.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from builtins import range
from builtins import str
from future import standard_library
standard_library.install_aliases()

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

import os.path
import inspect
import time
import graphviz


from .pckg_info import __version__
from .erc import dflt_circuit_erc
from .baseobj import SkidlBaseObject
from .utilities import *

OK, WARNING, ERROR = range(3)

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
        super(Circuit, self).__init__()

        """Initialize the Circuit object."""
        self.reset(init=True)

        # Set passed-in attributes for the circuit.
        for k, v in kwargs.items():
            setattr(self, k, v)

    def reset(self, init=False):
        """Clear any circuitry and cached part libraries and start over."""

        from .SchLib import SchLib

        # Clear circuitry.
        self.mini_reset(init)

        # Also clear any cached libraries.
        SchLib.reset()
        global backup_lib
        backup_lib = None

    def mini_reset(self, init=False):
        """Clear any circuitry but don't erase any loaded part libraries."""

        from .Net import NCNet

        self.name = ''
        self.parts = []
        self.nets = []
        self.netclasses = {}
        self.buses = []
        self.interfaces = []
        self.hierarchy = 'top'
        self.level = 0
        self.context = [('top', )]

        # Clear out the no-connect net and set the global no-connect if it's
        # tied to this circuit.
        self.NC = NCNet(
            name='__NOCONNECT', circuit=self
        )  # Net for storing no-connects for parts in this circuit.
        if not init and self is default_circuit:
            builtins.NC = self.NC

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
                    part.circuit = self  # Record the Circuit object the part belongs to.
                    part.ref = part.ref  # This adjusts the part reference if necessary.
                    part.hierarchy = self.hierarchy  # Tag the part with its hierarchy position.

                    # To determine where this part was created, trace the function
                    # calls that led to this part and place into a field
                    # but strip off all the calls to internal SKiDL functions.
                    call_stack = inspect.stack()  # Get function call stack.
                    # Use the function at the top of the stack to
                    # determine the location of the SKiDL library functions.
                    try:
                        skidl_dir, _ = os.path.split(call_stack[0].filename)
                    except AttributeError:
                        skidl_dir, _ = os.path.split(call_stack[0][1])
                    # Record file_name#line_num starting from the bottom of the stack
                    # and terminate as soon as a function is found that's in the
                    # SKiDL library (no use recording internal calls).
                    skidl_trace = []
                    for frame in reversed(call_stack):
                        try:
                            filename = frame.filename
                            lineno = frame.lineno
                        except AttributeError:
                            filename = frame[1]
                            lineno = frame[2]
                        if os.path.split(filename)[0] == skidl_dir:
                            # Found function in SKiDL library, so trace is complete.
                            break
                        # Get the absolute path to the file containing the function
                        # and the line number of the call in the file. Append these
                        # to the trace.
                        filepath = os.path.abspath(filename)
                        skidl_trace.append('#'.join((filepath, str(lineno))))
                    # Store the function call trace into a part field.
                    if skidl_trace:
                        part.skidl_trace = ';'.join(skidl_trace)

                    self.parts.append(part)

                else:
                    log_and_raise(logger, ValueError,
                        "Can't add unmovable part {} to this circuit.".format(
                            part.ref))

    def rmv_parts(self, *parts):
        """Remove some Part objects from the circuit."""
        for part in parts:
            if part.is_movable():
                if part.circuit == self and part in self.parts:
                    part.circuit = None
                    part.hierarchy = None
                    self.parts.remove(part)
                else:
                    logger.warning(
                        "Removing non-existent part {} from this circuit.".
                        format(part.ref))
            else:
                log_and_raise(logger, ValueError,
                    "Can't remove part {} from this circuit.".format(
                    part.ref))

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
                    net.hierarchy = self.hierarchy  # Tag the net with its hierarchy position.
                    self.nets.append(net)

                else:
                    log_and_raise(logger, ValueError,
                        "Can't add unmovable net {} to this circuit.".format(
                            net.name))

    def rmv_nets(self, *nets):
        """Remove some Net objects from the circuit."""
        for net in nets:
            if net.is_movable():
                if net.circuit == self and net in self.nets:
                    net.circuit = None
                    net.hierarchy = None
                    self.nets.remove(net)
                else:
                    logger.warning(
                        "Removing non-existent net {} from this circuit.".
                        format(net.name))
            else:
                log_and_raise(logger, ValueError,
                    "Can't remove unmovable net {} from this circuit.".format(
                        net.name))

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
                    bus.hierarchy = self.hierarchy  # Tag the bus with its hierarchy position.
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
                        self.nets.remove(net)
                else:
                    logger.warning(
                        "Removing non-existent bus {} from this circuit.".
                        format(bus.name))
            else:
                log_and_raise(logger, ValueError,
                    "Can't remove unmovable bus {} from this circuit.".format(
                        bus.name))

    def add_interfaces(self, *interfaces):
        """Add some Interface objects to the circuit. Assign an interface name if necessary."""
        for interface in interfaces:
            # Add the interface to this circuit if the interface is movable and
            # it's not already in this circuit.
            if interface.circuit != self:
                if interface.is_movable():

                    # Remove the interface from the circuit it's already in, but skip
                    # this if the interface isn't already in a Circuit.
                    if isinstance(interface.circuit, Circuit):
                        interface.circuit -= interface

                    # Add the interface to this circuit.
                    interface.circuit = self
                    interface.name = interface.name
                    interface.hierarchy = self.hierarchy  # Tag the bus with its hierarchy position.
                    self.interfaces.append(interface)

    def rmv_interfaces(self, *interfaces):
        """Remove some interfaces from the circuit."""
        for interface in interfaces:
            if interface.is_movable():
                if interface.circuit == self and interface in self.interfaces:
                    interface.circuit = None
                    interface.hierarchy = None
                    self.interfaces.remove(interface)
                else:
                    logger.warning(
                        "Removing non-existent interface {} from this circuit.".
                        format(interface.name))
            else:
                log_and_raise(logger, ValueError,
                    "Can't remove unmovable interface {} from this circuit.".format(
                        interface.name))

    def add_stuff(self, *stuff):
        """Add Parts, Nets, Buses, and Interfaces to the circuit."""

        from .Part import Part
        from .Net import Net
        from .Bus import Bus
        from .Interface import Interface

        for thing in flatten(stuff):
            if isinstance(thing, Part):
                self.add_parts(thing)
            elif isinstance(thing, Net):
                self.add_nets(thing)
            elif isinstance(thing, Bus):
                self.add_buses(thing)
            elif isinstance(thing, Interface):
                self.add_interfaces(thing)
            else:
                log_and_raise(logger, ValueError,"Can't add a {} to a Circuit object.".format(
                    type(thing)))
        return self

    def rmv_stuff(self, *stuff):
        """Remove Parts, Nets, Buses, and Interfaces from the circuit."""

        from .Net import Net
        from .Bus import Bus
        from .Part import Part
        from .Interface import Interface

        for thing in flatten(stuff):
            if isinstance(thing, Part):
                self.rmv_parts(thing)
            elif isinstance(thing, Net):
                self.rmv_nets(thing)
            elif isinstance(thing, Bus):
                self.rmv_buses(thing)
            elif isinstance(thing, Interface):
                self.rmv_interfaces(thing)
            else:
                log_and_raise(logger, ValueError,"Can't remove a {} from a Circuit object.".format(
                    type(pnb)))
        return self

    __iadd__ = add_stuff
    __isub__ = rmv_stuff

    def get_nets(self):
        """Get all the distinct nets for the circuit."""

        distinct_nets = []
        for net in self.nets:
            if net is self.NC:
                # Exclude no-connect net.
                continue
            if not net.get_pins():
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

    def ERC(self, *args, **kwargs):
        """Run class-wide and local ERC functions on this circuit."""

        # Reset the counters to clear any warnings/errors from previous ERC run.
        erc_logger.error.reset()
        erc_logger.warning.reset()

        exec_function_list(self, 'erc_list', *args, **kwargs)

    def _merge_net_names(self):
        """Select a single name for each multi-segment net."""

        for net in self.nets:
            net.merge_names()

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

        # Reset the counters to clear any warnings/errors from previous run.
        logger.error.reset()
        logger.warning.reset()

        # Before anything else, clean-up names for multi-segment nets.
        self._merge_net_names()

        import skidl

        # Extract arguments:
        #     Get EDA tool the netlist will be generated for.
        #     Get file the netlist will be stored in (if any).
        #     Get flag controlling the generation of a backup library.
        tool = kwargs.pop('tool', skidl.get_default_tool())
        file_ = kwargs.pop('file_', None)
        do_backup = kwargs.pop('do_backup', True)

        try:
            gen_func = getattr(self, '_gen_netlist_{}'.format(tool))
            netlist = gen_func(**kwargs)  # Pass any remaining arguments.
        except KeyError:
            log_and_raise(logger, ValueError,
                "Can't generate netlist in an unknown ECAD tool format ({}).".
                    format(tool))

        if (logger.error.count, logger.warning.count) == (0, 0):
            sys.stderr.write(
                '\nNo errors or warnings found during netlist generation.\n\n')
        else:
            sys.stderr.write(
                '\n{} warnings found during netlist generation.\n'.format(
                    logger.warning.count))
            sys.stderr.write(
                '{} errors found during netlist generation.\n\n'.format(
                    logger.error.count))

        with opened(file_ or (get_script_name() + '.net'), 'w') as f:
            f.write(str(netlist))

        if do_backup:
            self.backup_parts()  # Create a new backup lib for the circuit parts.
            global backup_lib  # Clear out any old backup lib so the new one
            backup_lib = None  #   will get reloaded when it's needed.

        return netlist

    def generate_xml(self, file_=None, tool=None):
        """
        Return netlist as an XML string and also write it to a file/stream.

        Args:
            file_: Either a file object that can be written to, or a string
                containing a file name, or None.

        Returns:
            A string containing the netlist.
        """

        # Reset the counters to clear any warnings/errors from previous run.
        logger.error.reset()
        logger.warning.reset()

        # Before anything else, clean-up names for multi-segment nets.
        self._merge_net_names()

        import skidl

        if tool is None:
            tool = skidl.get_default_tool()

        try:
            gen_func = getattr(self, '_gen_xml_{}'.format(tool))
            netlist = gen_func()
        except KeyError:
            log_and_raise(logger, ValueError,
                "Can't generate XML in an unknown ECAD tool format ({}).".
                    format(tool))

        if (logger.error.count, logger.warning.count) == (0, 0):
            sys.stderr.write(
                '\nNo errors or warnings found during XML generation.\n\n')
        else:
            sys.stderr.write(
                '\n{} warnings found during XML generation.\n'.format(
                    logger.warning.count))
            sys.stderr.write(
                '{} errors found during XML generation.\n\n'.format(
                    logger.error.count))

        with opened(file_ or (get_script_name() + '.xml'), 'w') as f:
            f.write(netlist)

        return netlist

    def generate_graph(self,
                       file_=None,
                       engine='neato',
                       rankdir='LR',
                       part_shape='rectangle',
                       net_shape='point',
                       splines=None,
                       show_values=True,
                       show_anon=False):
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

        Returns:
            graphviz.Digraph
        """

        # Reset the counters to clear any warnings/errors from previous run.
        logger.error.reset()
        logger.warning.reset()

        # Before anything else, clean-up names for multi-segment nets.
        self._merge_net_names()

        dot = graphviz.Digraph(engine=engine)
        dot.attr(rankdir=rankdir, splines=splines)

        nets = self.get_nets()

        # try and keep things in the same order
        nets.sort(key=lambda n: n.name.lower())

        for n in nets:
            xlabel = n.name
            if not show_anon and n.is_implicit():
                xlabel = None
            dot.node(n.name, shape=net_shape, xlabel=xlabel)
            for pin in n.pins:
                dot.edge(pin.part.ref, n.name, arrowhead='none')

        for p in sorted(self.parts, key=lambda p: p.ref.lower()):
            xlabel = None
            if show_values:
                xlabel = p.value
            dot.node(p.ref, shape=part_shape, xlabel=xlabel)

        if file_ is not None:
            dot.save(file_)
        return dot

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

        import skidl
        from .defines import SKIDL

        lib = skidl.SchLib(tool=SKIDL)  # Create empty library.
        for p in self.parts:
            lib += p
        if not file_:
            file_ = skidl.BACKUP_LIB_FILE_NAME
        lib.export(libname=skidl.BACKUP_LIB_NAME, file_=file_)


from collections import defaultdict
__func_name_cntr = defaultdict(int)

def SubCircuit(f):
    """
    A @SubCircuit decorator is used to create hierarchical circuits.

    Args:
        f: The function containing SKiDL statements that represents a subcircuit.
    """

    def sub_f(*args, **kwargs):
        # Upon entry, save the reference to the current default Circuit object.
        save_default_circuit = default_circuit  # pylint: disable=undefined-variable

        # If the subcircuit uses the 'circuit' argument, then set the default
        # Circuit object to that. Otherwise, use the current default Circuit object.
        circuit = kwargs.pop('circuit', default_circuit)
        builtins.default_circuit = circuit

        # Setup some globals needed in the subcircuit.
        builtins.NC = default_circuit.NC  # pylint: disable=undefined-variable

        # Invoking the subcircuit function creates circuitry at a level one
        # greater than the current level. (The top level is zero.)
        circuit.level += 1

        # Create a name for this subcircuit from the concatenated names of all
        # the nested subcircuit functions that were called on all the preceding levels
        # that led to this one. Also, add a distinct integer to the current
        # function name to disambiguate multiple uses of the same function.
        circuit.hierarchy = circuit.context[-1][0] + '.' + f.__name__ + str(__func_name_cntr[f.__name__])
        __func_name_cntr[f.__name__] = __func_name_cntr[f.__name__] + 1

        # Store the context so it can be used if this subcircuit function
        # invokes another subcircuit function within itself to add more
        # levels of hierarchy.
        circuit.context.append((circuit.hierarchy, ))

        # Call the function to create whatever circuitry it handles.
        # The arguments to the function are usually nets to be connected to the
        # parts instantiated in the function, but they may also be user-specific
        # and have no effect on the mechanics of adding parts or nets although
        # they may direct the function as to what parts and nets get created.
        # Store any results it returns as a list. These results are user-specific
        # and have no effect on the mechanics of adding parts or nets.
        results = f(*args, **kwargs)

        # Restore the context that existed before the subcircuitry was
        # created. This does not remove the circuitry since it has already been
        # added to the parts and nets lists.
        circuit.context.pop()

        # Restore the hierarchy label and level.
        circuit.hierarchy = circuit.context[-1][0]
        circuit.level -= 1

        # Restore the default circuit and globals.
        builtins.default_circuit = save_default_circuit
        builtins.NC = default_circuit.NC  # pylint: disable=undefined-variable

        return results

    return sub_f


# The decorator can also be called as "@subcircuit".
subcircuit = SubCircuit
