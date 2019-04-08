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
Handles part pins.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from builtins import super
from builtins import range
from future import standard_library
standard_library.install_aliases()
from copy import copy
from enum import IntEnum
from collections import defaultdict

from .utilities import *
from .Alias import *
from .Circuit import OK, WARNING, ERROR


class Pin(object):
    """
    A class for storing data about pins for a part.

    Args:
        attribs: Key/value pairs of attributes to add to the library.

    Attributes:
        nets: The electrical nets this pin is connected to (can be >1).
        part: Link to the Part object this pin belongs to.
        func: Pin function such as PinType.types.INPUT.
        do_erc: When false, the pin is not checked for ERC violations.
    """

    # Various types of pins.
    types = IntEnum('types', ('INPUT', 'OUTPUT', 'BIDIR', 'TRISTATE', 'PASSIVE',
                    'UNSPEC', 'PWRIN', 'PWROUT', 'OPENCOLL', 'OPENEMIT',
                    'NOCONNECT'))

    # Various drive levels a pin can output:
    #   NOCONNECT: NC pin drive.
    #   NONE: No drive capability (like an input pin).
    #   PASSIVE: Small drive capability, such as a pullup.
    #   ONESIDE: Can pull high (open-emitter) or low (open-collector).
    #   TRISTATE: Can pull high/low and be in high-impedance state.
    #   PUSHPULL: Can actively drive high or low.
    #   POWER: A power supply or ground line.
    drives = IntEnum('drives', ('NOCONNECT', 'NONE', 'PASSIVE',
                    'ONESIDE', 'TRISTATE', 'PUSHPULL', 'POWER'))

    # Information about the various types of pins:
    #   function: A string describing the pin's function.
    #   drive: The drive capability of the pin.
    #   rcv_min: The minimum amount of drive the pin must receive to function.
    #   rcv_max: The maximum amount of drive the pin can receive and still function.
    pin_info = {
        types.INPUT: {
            'function': 'INPUT',
            'func_str': 'INPUT',
            'drive': drives.NONE,
            'max_rcv': drives.POWER,
            'min_rcv': drives.PASSIVE,
        },
        types.OUTPUT: {
            'function': 'OUTPUT',
            'func_str': 'OUTPUT',
            'drive': drives.PUSHPULL,
            'max_rcv': drives.PASSIVE,
            'min_rcv': drives.NONE,
        },
        types.BIDIR: {
            'function': 'BIDIRECTIONAL',
            'func_str': 'BIDIR',
            'drive': drives.TRISTATE,
            'max_rcv': drives.POWER,
            'min_rcv': drives.NONE,
        },
        types.TRISTATE: {
            'function': 'TRISTATE',
            'func_str': 'TRISTATE',
            'drive': drives.TRISTATE,
            'max_rcv': drives.TRISTATE,
            'min_rcv': drives.NONE,
        },
        types.PASSIVE: {
            'function': 'PASSIVE',
            'func_str': 'PASSIVE',
            'drive': drives.PASSIVE,
            'max_rcv': drives.POWER,
            'min_rcv': drives.NONE,
        },
        types.UNSPEC: {
            'function': 'UNSPECIFIED',
            'func_str': 'UNSPEC',
            'drive': drives.NONE,
            'max_rcv': drives.POWER,
            'min_rcv': drives.NONE,
        },
        types.PWRIN: {
            'function': 'POWER-IN',
            'func_str': 'PWRIN',
            'drive': drives.NONE,
            'max_rcv': drives.POWER,
            'min_rcv': drives.POWER,
        },
        types.PWROUT: {
            'function': 'POWER-OUT',
            'func_str': 'PWROUT',
            'drive': drives.POWER,
            'max_rcv': drives.PASSIVE,
            'min_rcv': drives.NONE,
        },
        types.OPENCOLL: {
            'function': 'OPEN-COLLECTOR',
            'func_str': 'OPENCOLL',
            'drive': drives.ONESIDE,
            'max_rcv': drives.TRISTATE,
            'min_rcv': drives.NONE,
        },
        types.OPENEMIT: {
            'function': 'OPEN-EMITTER',
            'func_str': 'OPENEMIT',
            'drive': drives.ONESIDE,
            'max_rcv': drives.TRISTATE,
            'min_rcv': drives.NONE,
        },
        types.NOCONNECT: {
            'function': 'NO-CONNECT',
            'func_str': 'NOCONNECT',
            'drive': drives.NOCONNECT,
            'max_rcv': drives.NOCONNECT,
            'min_rcv': drives.NOCONNECT,
        },
    }

    def __init__(self, **attribs):
        self.nets = []
        self.part = None
        self.name = ''
        self.num = ''
        self.do_erc = True

        # Attach additional attributes to the pin.
        for k, v in attribs.items():
            setattr(self, k, v)

    def copy(self, num_copies=None, **attribs):
        """
        Return copy or list of copies of a pin including any net connection.

        Args:
            num_copies: Number of copies to make of pin.

        Keyword Args:
            attribs: Name/value pairs for setting attributes for the pin.

        Notes:
            An instance of a pin can be copied just by calling it like so::

                p = Pin()     # Create a pin.
                p_copy = p()  # This is a copy of the pin.
        """

        # If the number of copies is None, then a single copy will be made
        # and returned as a scalar (not a list). Otherwise, the number of
        # copies will be set by the num_copies parameter or the number of
        # values supplied for each part attribute.
        num_copies_attribs = find_num_copies(**attribs)
        return_list = (num_copies is not None) or (num_copies_attribs > 1)
        if num_copies is None:
            num_copies = max(1, num_copies_attribs)

        # Check that a valid number of copies is requested.
        if not isinstance(num_copies, int):
            logger.error(
                "Can't make a non-integer number ({}) of copies of a pin!".
                format(num_copies))
            raise Exception
        if num_copies < 0:
            logger.error(
                "Can't make a negative number ({}) of copies of a pin!".format(
                    num_copies))
            raise Exception

        copies = []
        for _ in range(num_copies):

            # Make a shallow copy of the pin.
            cpy = copy(self)

            # The copy is not on a net, yet.
            cpy.nets = []

            # Connect the new pin to the same net as the original.
            if self.nets:
                self.nets[0] += cpy

            # Copy the alias for the pin if it has one.
            try:
                cpy.alias = Alias(self.alias.name, id(cpy))
            except AttributeError:
                # Pin has no alias.
                pass

            # Attach additional attributes to the pin.
            for k, v in attribs.items():
                setattr(cpy, k, v)

            copies.append(cpy)

        # Return a list of the copies made or just a single copy.
        if return_list:
            return copies
        return copies[0]

    # Make copies with the multiplication operator or by calling the object.
    __call__ = copy

    def __mul__(self, num_copies):
        if num_copies is None:
            num_copies = 0
        return self.copy(num_copies=num_copies)

    __rmul__ = __mul__

    def __getitem__(self, *ids):
        """
        Return the pin if the indices resolve to a single index of 0.

        Args:
            ids: A list of indices. These can be individual
                numbers, net names, nested lists, or slices.

        Returns:
            The pin, otherwise None or raises an Exception.
        """

        # Resolve the indices.
        indices = list(set(expand_indices(0, self.width - 1, ids)))
        if indices is None or len(indices) == 0:
            return None
        if len(indices) > 1:
            logger.error("Can't index a pin with multiple indices.")
            raise Exception
        if indices[0] != 0:
            logger.error("Can't use a non-zero index for a pin.")
            raise Exception
        return self

    def __setitem__(self, ids, *pins_nets_buses):
        """
        You can't assign to Pins. You must use the += operator.

        This method is a work-around that allows the use of the += for making
        connections to pins while prohibiting direct assignment. Python
        processes something like net[0] += Net() as follows::

            1. Pin.__getitem__ is called with '0' as the index. This
               returns a single Pin.
            2. The Pin.__iadd__ method is passed the pin and
               the thing to connect to it (a Net in this case). This
               method makes the actual connection to the net. Then
               it creates an iadd_flag attribute in the object it returns.
            3. Finally, Pin.__setitem__ is called. If the iadd_flag attribute
               is true in the passed argument, then __setitem__ was entered
               as part of processing the += operator. If there is no
               iadd_flag attribute, then __setitem__ was entered as a result
               of using a direct assignment, which is not allowed.
        """

        # If the iadd_flag is set, then it's OK that we got
        # here and don't issue an error. Also, delete the flag.
        if getattr(pins_nets_buses[0], 'iadd_flag', False):
            del pins_nets_buses[0].iadd_flag
            return

        # No iadd_flag or it wasn't set. This means a direct assignment
        # was made to the pin, which is not allowed.
        logger.error("Can't assign to a Net! Use the += operator.")
        raise Exception

    def __iter__(self):
        """
        Return an iterator for stepping through the pin.
        """
        # You can only iterate a Pin one time.
        return (self for i in [0,]) # Return generator expr.

    def is_connected(self):
        """Return true if a pin is connected to a net (but not a no-connect net)."""

        from .Net import Net, NCNet

        if not self.nets:
            # This pin is not connected to any nets.
            return False

        # Get the types of things this pin is connected to.
        net_types = set([type(n) for n in self.nets])

        if set([NCNet]) == net_types:
            # This pin is only connected to no-connect nets.
            return False
        if set([Net]) == net_types:
            # This pin is only connected to normal nets.
            return True
        if set([Net, NCNet]) == net_types:
            # Can't be connected to both normal and no-connect nets!
            logger.error(
                '{} is connected to both normal and no-connect nets!'.format(
                    self.erc_desc()))
            raise Exception
        # This is just strange...
        logger.error("{} is connected to something strange: {}.".format(
            self.erc_desc(), self.nets))
        raise Exception

    def is_attached(self, pin_net_bus):
        """Return true if this pin is attached to the given pin, net or bus."""

        from .Net import Net
        from .Pin import Pin

        if not self.is_connected():
            return False
        if isinstance(pin_net_bus, Pin):
            if pin_net_bus.is_connected():
                return pin_net_bus.net.is_attached(self.net)
            return False
        if isinstance(pin_net_bus, Net):
            return pin_net_bus.is_attached(self.net)
        if isinstance(pin_net_bus, Bus):
            for net in pin_net_bus[:]:
                if self.net.is_attached(net):
                    return True
            return False
        logger.error("Pins can't be attached to {}!".format(type(pin_net_bus)))
        raise Exception

    def connect(self, *pins_nets_buses):
        """
        Return the pin after connecting it to one or more nets or pins.

        Args:
            pins_nets_buses: One or more Pin, Net or Bus objects or
                lists/tuples of them.

        Returns:
            The updated pin with the new connections.

        Notes:
            You can connect nets or pins to a pin like so::

                p = Pin()     # Create a pin.
                n = Net()     # Create a net.
                p += net      # Connect the net to the pin.
        """

        from .Net import Net

        # Go through all the pins and/or nets and connect them to this pin.
        for pn in expand_buses(flatten(pins_nets_buses)):
            if isinstance(pn, Pin):
                # Connecting pin-to-pin.
                if self.is_connected():
                    # If self is already connected to a net, then add the
                    # other pin to the same net.
                    self.nets[0] += pn
                elif pn.is_connected():
                    # If self is unconnected but the other pin is, then
                    # connect self to the other pin's net.
                    pn.nets[0] += self
                else:
                    # Neither pin is connected to a net, so create a net
                    # in the same circuit as the pin and attach both to it.
                    Net(circuit=self.part.circuit).connect(self, pn)
            elif isinstance(pn, Net):
                # Connecting pin-to-net, so just connect the pin to the net.
                pn += self
            else:
                logger.error('Cannot attach non-Pin/non-Net {} to {}.'.format(
                    type(pn), self.erc_desc()))
                raise Exception

        # Set the flag to indicate this result came from the += operator.
        self.iadd_flag = True  # pylint: disable=attribute-defined-outside-init

        return self

    # Connect a net to a pin using the += operator.
    __iadd__ = connect

    def disconnect(self):
        """Disconnect this pin from all nets."""
        if not self.net:
            return
        for n in self.nets:
            n.disconnect(self)
        self.nets = []

    def get_nets(self):
        """Return a list containing the Net objects connected to this pin."""
        return self.nets

    def get_pins(self):
        """Return a list containing this pin."""
        return to_list(self)

    def create_network(self):
        """Create a network from a single pin."""
        from .Network import Network

        ntwk = Network()
        ntwk.append(self)
        return ntwk

    def __and__(self, obj):
        """Attach a pin and another part/pin/net in serial."""
        from .Network import Network

        return Network(self) & obj

    def __rand__(self, obj):
        """Attach a pin and another part/pin/net in serial."""
        from .Network import Network

        return obj & Network(self)

    def __or__(self, obj):
        """Attach a pin and another part/pin/net in parallel."""
        from .Network import Network

        return Network(self) | obj

    def __ror__(self, obj):
        """Attach a pin and another part/pin/net in parallel."""
        from .Network import Network

        return obj | Network(self)

    def chk_conflict(self, other_pin):
        """Check for electrical rule conflicts between this pin and another."""
        from .Circuit import OK, ERROR, WARNING

        if not self.do_erc or not other_pin.do_erc:
            return

        erc_result = conflict_matrix[self.func][other_pin.func]

        # Return if the pins are compatible.
        if erc_result == OK:
            return

        # Otherwise, generate an error or warning message.
        msg = 'Pin conflict on net {n}: {p1} <==> {p2}'.format(
            n=self.net.name, p1=self.erc_desc(), p2=other_pin.erc_desc())
        if erc_result == WARNING:
            erc_logger.warning(msg)
        else:
            erc_logger.error(msg)

    def erc_desc(self):
        """Return a string describing this pin for ERC."""
        desc = "{func} pin {num}/{name} of {part}".format(
            part=self.part.erc_desc(),
            num=self.num,
            name=self.name,
            func=Pin.pin_info[self.func]['function'])
        return desc

    def __str__(self):
        """Return a description of this pin as a string."""
        ref = getattr(self.part, 'ref', '???')
        num = getattr(self, 'num', '???')
        name = getattr(self, 'name', '???')
        try:
            alias = '/' + self.alias
        except AttributeError:
            alias = ''
        func = getattr(self, 'func', Pin.types.UNSPEC)
        func = Pin.pin_info[func]['function']
        return 'Pin {ref}/{num}/{name}{alias}/{func}'.format(**locals())

    __repr__ = __str__

    def export(self):
        """Return a string to recreate a Pin object."""
        attribs = []
        for k in ['num', 'name', 'func', 'do_erc']:
            v = getattr(self, k, None)
            if v:
                if k == 'func':
                    # Assign the pin function using the actual name of the
                    # function, not its numerical value (in case that changes
                    # in the future if more pin functions are added).
                    v = 'Pin.types.' + Pin.pin_info[v]['func_str']
                else:
                    v = repr(v)
                attribs.append('{}={}'.format(k, v))
        return 'Pin({})'.format(','.join(attribs))

    @property
    def net(self):
        """Return one of the nets the pin is connected to."""
        if self.nets:
            return self.nets[0]
        return None

    @property
    def width(self):
        """Return width of a Pin, which is always 1."""
        return 1

    @property
    def drive(self):
        """
        Get, set and delete the drive strength of this pin.
        """
        return self._drive

    @drive.setter
    def drive(self, drive):
        self._drive = drive

    @drive.deleter
    def drive(self):
        del self._drive

    @property
    def alias(self):
        """Get, set, and delete the alias name for the pin."""

        # Don't test to see if _alias attribute exists. Just let
        # the exception occur if it doesn't.
        return self._alias
 
    @alias.setter
    def alias(self, alias):
        self._alias = Alias(alias, id(self))

    @alias.deleter
    def alias(self):
        del self._alias

    def __bool__(self):
        """Any valid Pin is True."""
        return True

    __nonzero__ = __bool__  # Python 2 compatibility.


##############################################################################


class PhantomPin(Pin):
    """
    A pin type that exists solely to tie two pinless nets together.
    It will not participate in generating any netlists.
    """

    def __init__(self, **attribs):
        super(PhantomPin, self).__init__(**attribs)
        self.nets = []
        self.part = None
        self.do_erc = False


##############################################################################


# Create the pin conflict matrix as a defaultdict of defaultdicts which
# returns OK if the given element is not in the matrix. This would indicate
# the pin types used to index that element have no contention if connected.
conflict_matrix = defaultdict(lambda: defaultdict(lambda: OK))

# Add the non-OK pin connections to the matrix.
conflict_matrix[Pin.types.OUTPUT][Pin.types.OUTPUT] = ERROR
conflict_matrix[Pin.types.TRISTATE][Pin.types.OUTPUT] = WARNING
conflict_matrix[Pin.types.UNSPEC][Pin.types.INPUT] = WARNING
conflict_matrix[Pin.types.UNSPEC][Pin.types.OUTPUT] = WARNING
conflict_matrix[Pin.types.UNSPEC][Pin.types.BIDIR] = WARNING
conflict_matrix[Pin.types.UNSPEC][Pin.types.TRISTATE] = WARNING
conflict_matrix[Pin.types.UNSPEC][Pin.types.PASSIVE] = WARNING
conflict_matrix[Pin.types.UNSPEC][Pin.types.UNSPEC] = WARNING
conflict_matrix[Pin.types.PWRIN][Pin.types.TRISTATE] = WARNING
conflict_matrix[Pin.types.PWRIN][Pin.types.UNSPEC] = WARNING
conflict_matrix[Pin.types.PWROUT][Pin.types.OUTPUT] = ERROR
conflict_matrix[Pin.types.PWROUT][Pin.types.BIDIR] = WARNING
conflict_matrix[Pin.types.PWROUT][Pin.types.TRISTATE] = ERROR
conflict_matrix[Pin.types.PWROUT][Pin.types.UNSPEC] = WARNING
conflict_matrix[Pin.types.PWROUT][Pin.types.PWROUT] = ERROR
conflict_matrix[Pin.types.OPENCOLL][Pin.types.OUTPUT] = ERROR
conflict_matrix[Pin.types.OPENCOLL][Pin.types.TRISTATE] = ERROR
conflict_matrix[Pin.types.OPENCOLL][Pin.types.UNSPEC] = WARNING
conflict_matrix[Pin.types.OPENCOLL][Pin.types.PWROUT] = ERROR
conflict_matrix[Pin.types.OPENEMIT][Pin.types.OUTPUT] = ERROR
conflict_matrix[Pin.types.OPENEMIT][Pin.types.BIDIR] = WARNING
conflict_matrix[Pin.types.OPENEMIT][Pin.types.TRISTATE] = WARNING
conflict_matrix[Pin.types.OPENEMIT][Pin.types.UNSPEC] = WARNING
conflict_matrix[Pin.types.OPENEMIT][Pin.types.PWROUT] = ERROR
conflict_matrix[Pin.types.NOCONNECT][Pin.types.INPUT] = ERROR
conflict_matrix[Pin.types.NOCONNECT][Pin.types.OUTPUT] = ERROR
conflict_matrix[Pin.types.NOCONNECT][Pin.types.BIDIR] = ERROR
conflict_matrix[Pin.types.NOCONNECT][Pin.types.TRISTATE] = ERROR
conflict_matrix[Pin.types.NOCONNECT][Pin.types.PASSIVE] = ERROR
conflict_matrix[Pin.types.NOCONNECT][Pin.types.UNSPEC] = ERROR
conflict_matrix[Pin.types.NOCONNECT][Pin.types.PWRIN] = ERROR
conflict_matrix[Pin.types.NOCONNECT][Pin.types.PWROUT] = ERROR
conflict_matrix[Pin.types.NOCONNECT][Pin.types.OPENCOLL] = ERROR
conflict_matrix[Pin.types.NOCONNECT][Pin.types.OPENEMIT] = ERROR
conflict_matrix[Pin.types.NOCONNECT][Pin.types.NOCONNECT] = ERROR

# Fill-in the other half of the symmetrical contention matrix by looking
# for entries that != OK at position (r,c) and copying them to position
# (c,r).
cols = list(conflict_matrix.keys())
for c in cols:
    for r in conflict_matrix[c].keys():
        conflict_matrix[r][c] = conflict_matrix[c][r]
