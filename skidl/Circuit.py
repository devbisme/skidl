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
from .utilities import *


class Circuit(object):
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

    OK, WARNING, ERROR = range(3)

    def __init__(self, **kwargs):
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
        self.buses = []
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
                    logger.error(
                        "Can't add unmovable part {} to this circuit.".format(
                            part.ref))
                    raise Exception

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
                logger.error("Can't remove part {} from this circuit.".format(
                    part.ref))
                raise Exception

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
                    logger.error(
                        "Can't add unmovable net {} to this circuit.".format(
                            net.name))
                    raise Exception

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
                logger.error(
                    "Can't remove unmovable net {} from this circuit.".format(
                        net.name))
                raise Exception

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
                logger.error(
                    "Can't remove unmovable bus {} from this circuit.".format(
                        bus.name))
                raise Exception

    def add_parts_nets_buses(self, *parts_nets_buses):
        """Add Parts, Nets and Buses to the circuit."""

        from .Part import Part
        from .Net import Net
        from .Bus import Bus

        for pnb in flatten(parts_nets_buses):
            if isinstance(pnb, Part):
                self.add_parts(pnb)
            elif isinstance(pnb, Net):
                self.add_nets(pnb)
            elif isinstance(pnb, Bus):
                self.add_buses(pnb)
            else:
                logger.error("Can't add a {} to a Circuit object.".format(
                    type(pnb)))
                raise Exception
        return self

    def rmv_parts_nets_buses(self, *parts_nets_buses):
        """Remove Parts, Nets and Buses from the circuit."""

        from .Net import Net
        from .Bus import Bus
        from .Part import Part

        for pnb in flatten(parts_nets_buses):
            if isinstance(pnb, Part):
                self.rmv_parts(pnb)
            elif isinstance(pnb, Net):
                self.rmv_nets(pnb)
            elif isinstance(pnb, Bus):
                self.rmv_buses(pnb)
            else:
                logger.error("Can't remove a {} from a Circuit object.".format(
                    type(pnb)))
                raise Exception
        return self

    __iadd__ = add_parts_nets_buses
    __isub__ = rmv_parts_nets_buses

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

    def _erc_setup(self):
        """
        Initialize the electrical rules checker.
        """

        from skidl import Pin

        # Initialize the pin contention matrix.
        self._erc_matrix = [[self.OK for c in range(11)] for r in range(11)]
        self._erc_matrix[Pin.OUTPUT][Pin.OUTPUT] = self.ERROR
        self._erc_matrix[Pin.TRISTATE][Pin.OUTPUT] = self.WARNING
        self._erc_matrix[Pin.UNSPEC][Pin.INPUT] = self.WARNING
        self._erc_matrix[Pin.UNSPEC][Pin.OUTPUT] = self.WARNING
        self._erc_matrix[Pin.UNSPEC][Pin.BIDIR] = self.WARNING
        self._erc_matrix[Pin.UNSPEC][Pin.TRISTATE] = self.WARNING
        self._erc_matrix[Pin.UNSPEC][Pin.PASSIVE] = self.WARNING
        self._erc_matrix[Pin.UNSPEC][Pin.UNSPEC] = self.WARNING
        self._erc_matrix[Pin.PWRIN][Pin.TRISTATE] = self.WARNING
        self._erc_matrix[Pin.PWRIN][Pin.UNSPEC] = self.WARNING
        self._erc_matrix[Pin.PWROUT][Pin.OUTPUT] = self.ERROR
        self._erc_matrix[Pin.PWROUT][Pin.BIDIR] = self.WARNING
        self._erc_matrix[Pin.PWROUT][Pin.TRISTATE] = self.ERROR
        self._erc_matrix[Pin.PWROUT][Pin.UNSPEC] = self.WARNING
        self._erc_matrix[Pin.PWROUT][Pin.PWROUT] = self.ERROR
        self._erc_matrix[Pin.OPENCOLL][Pin.OUTPUT] = self.ERROR
        self._erc_matrix[Pin.OPENCOLL][Pin.TRISTATE] = self.ERROR
        self._erc_matrix[Pin.OPENCOLL][Pin.UNSPEC] = self.WARNING
        self._erc_matrix[Pin.OPENCOLL][Pin.PWROUT] = self.ERROR
        self._erc_matrix[Pin.OPENEMIT][Pin.OUTPUT] = self.ERROR
        self._erc_matrix[Pin.OPENEMIT][Pin.BIDIR] = self.WARNING
        self._erc_matrix[Pin.OPENEMIT][Pin.TRISTATE] = self.WARNING
        self._erc_matrix[Pin.OPENEMIT][Pin.UNSPEC] = self.WARNING
        self._erc_matrix[Pin.OPENEMIT][Pin.PWROUT] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.INPUT] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.OUTPUT] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.BIDIR] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.TRISTATE] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.PASSIVE] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.UNSPEC] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.PWRIN] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.PWROUT] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.OPENCOLL] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.OPENEMIT] = self.ERROR
        self._erc_matrix[Pin.NOCONNECT][Pin.NOCONNECT] = self.ERROR

        # Fill-in the other half of the symmetrical matrix.
        for c in range(1, 11):
            for r in range(c):
                self._erc_matrix[r][c] = self._erc_matrix[c][r]

    def set_pin_conflict_rule(self, pin1_func, pin2_func, conflict_level):
        """
        Set the level of conflict for two types of pins on the same net.

        Args:
            pin1_func: The function of the first pin (e.g., Pin.OUTPUT).
            pin2_func: The function of the second pin (e.g., Pin.TRISTATE).
            conflict_level: Severity of conflict (e.g., self.OK, self.WARNING, self.ERROR).
        """

        # Place the conflict level into the symmetrical ERC matrix.
        self._erc_matrix[pin1_func][pin2_func] = conflict_level
        self._erc_matrix[pin2_func][pin1_func] = conflict_level

    def erc_pin_to_pin_chk(self, pin1, pin2):
        """Check for conflict between two pins on a net."""

        # Use the functions of the two pins to index into the ERC table
        # and see if the pins are compatible (e.g., an input and an output)
        # or incompatible (e.g., a conflict because both are outputs).
        return self._erc_matrix[pin1.func][pin2.func]

    def ERC(self):
        """
        Do an electrical rules check on the circuit.
        """

        self._erc_setup()

        # Check the nets for errors.
        for net in self.nets:
            net.erc()

        # Check the parts for errors.
        for part in self.parts:
            part.erc()

        if (erc_logger.error.count, erc_logger.warning.count) == (0, 0):
            sys.stderr.write('\nNo ERC errors or warnings found.\n\n')
        else:
            sys.stderr.write('\n{} warnings found during ERC.\n'.format(
                erc_logger.warning.count))
            sys.stderr.write('{} errors found during ERC.\n\n'.format(
                erc_logger.error.count))

    def generate_netlist(self, file_=None, tool=None, do_backup=True):
        """
        Return a netlist as a string and also write it to a file/stream.

        Args:
            file: Either a file object that can be written to, or a string
                containing a file name, or None.
            do_backup: If true, create a library with all the parts in the circuit.

        Returns:
            A string containing the netlist.
        """

        import skidl

        if tool is None:
            tool = skidl.get_default_tool()

        try:
            gen_func = getattr(self, '_gen_netlist_{}'.format(tool))
            netlist = gen_func()
        except KeyError:
            logger.error(
                "Can't generate netlist in an unknown ECAD tool format ({}).".
                format(tool))
            raise Exception

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
            f.write(netlist)

        if do_backup:
            self.backup_parts(
            )  # Create a new backup lib for the circuit parts.
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

        import skidl

        if tool is None:
            tool = skidl.get_default_tool()

        try:
            gen_func = getattr(self, '_gen_xml_{}'.format(tool))
            netlist = gen_func()
        except KeyError:
            logger.error(
                "Can't generate XML in an unknown ECAD tool format ({}).".
                format(tool))
            raise Exception

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


def SubCircuit(f):
    """
    A @SubCircuit decorator is used to create hierarchical circuits.

    Args:
        f: The function containing SKiDL statements that represents a subcircuit.
    """

    def sub_f(*args, **kwargs):
        # Upon entry, save the reference to the default Circuit object.
        save_default_circuit = default_circuit  # pylint: disable=undefined-variable

        # If the subcircuit has no 'circuit' argument, then all the SKiDL
        # statements in the subcircuit function will reference the default Circuit
        # object.
        if 'circuit' not in kwargs:
            circuit = default_circuit  # pylint: disable=undefined-variable

        # But if the subcircuit function has a 'circuit' argument, then set the default
        # Circuit object to that. Then all SKiDL statements in the function will
        # make changes (i.e., add parts, nets, buses) to that.
        else:
            circuit = kwargs['circuit']
            del kwargs[
                'circuit']  # Don't pass the circuit parameter down to the f function.
            builtins.default_circuit = circuit

        # Setup some globals needed in the subcircuit.
        builtins.NC = default_circuit.NC  # pylint: disable=undefined-variable

        # Invoking the subcircuit function creates circuitry at a level one
        # greater than the current level. (The top level is zero.)
        circuit.level += 1

        # Create a name for this subcircuit from the concatenated names of all
        # the nested subcircuit functions that were called on all the preceding levels
        # that led to this one.
        circuit.hierarchy = circuit.context[-1][0] + '.' + f.__name__

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
