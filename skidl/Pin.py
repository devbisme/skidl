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

from .utilities import *


class Pin(object):
    """
    A class for storing data about pins for a part.

    Args:
        attribs: Key/value pairs of attributes to add to the library.

    Attributes:
        nets: The electrical nets this pin is connected to (can be >1).
        part: Link to the Part object this pin belongs to.
        do_erc: When false, the pin is not checked for ERC violations.
    """

    # Various types of pins.
    INPUT, OUTPUT, BIDIR, TRISTATE, PASSIVE, UNSPEC, PWRIN,\
    PWROUT, OPENCOLL, OPENEMIT, NOCONNECT = range(11)

    # Various drive levels a pin can output:
    #   NOCONNECT_DRIVE: NC pin drive.
    #   NO_DRIVE: No drive capability (like an input pin).
    #   PASSIVE_DRIVE: Small drive capability, such as a pullup.
    #   ONESIDE_DRIVE: Can pull high (open-emitter) or low (open-collector).
    #   TRISTATE_DRIVE: Can pull high/low and be in high-impedance state.
    #   PUSHPULL_DRIVE: Can actively drive high or low.
    #   POWER_DRIVE: A power supply or ground line.
    NOCONNECT_DRIVE, NO_DRIVE, PASSIVE_DRIVE, ONESIDE_DRIVE,\
    TRISTATE_DRIVE, PUSHPULL_DRIVE, POWER_DRIVE = range(7)

    # Information about the various types of pins:
    #   function: A string describing the pin's function.
    #   drive: The drive capability of the pin.
    #   rcv_min: The minimum amount of drive the pin must receive to function.
    #   rcv_max: The maximum amount of drive the pin can receive and still function.
    pin_info = {
        INPUT: {
            'function': 'INPUT',
            'func_str': 'INPUT',
            'drive': NO_DRIVE,
            'max_rcv': POWER_DRIVE,
            'min_rcv': PASSIVE_DRIVE,
        },
        OUTPUT: {
            'function': 'OUTPUT',
            'func_str': 'OUTPUT',
            'drive': PUSHPULL_DRIVE,
            'max_rcv': PASSIVE_DRIVE,
            'min_rcv': NO_DRIVE,
        },
        BIDIR: {
            'function': 'BIDIRECTIONAL',
            'func_str': 'BIDIR',
            'drive': TRISTATE_DRIVE,
            'max_rcv': POWER_DRIVE,
            'min_rcv': NO_DRIVE,
        },
        TRISTATE: {
            'function': 'TRISTATE',
            'func_str': 'TRISTATE',
            'drive': TRISTATE_DRIVE,
            'max_rcv': TRISTATE_DRIVE,
            'min_rcv': NO_DRIVE,
        },
        PASSIVE: {
            'function': 'PASSIVE',
            'func_str': 'PASSIVE',
            'drive': PASSIVE_DRIVE,
            'max_rcv': POWER_DRIVE,
            'min_rcv': NO_DRIVE,
        },
        UNSPEC: {
            'function': 'UNSPECIFIED',
            'func_str': 'UNSPEC',
            'drive': NO_DRIVE,
            'max_rcv': POWER_DRIVE,
            'min_rcv': NO_DRIVE,
        },
        PWRIN: {
            'function': 'POWER-IN',
            'func_str': 'PWRIN',
            'drive': NO_DRIVE,
            'max_rcv': POWER_DRIVE,
            'min_rcv': POWER_DRIVE,
        },
        PWROUT: {
            'function': 'POWER-OUT',
            'func_str': 'PWROUT',
            'drive': POWER_DRIVE,
            'max_rcv': PASSIVE_DRIVE,
            'min_rcv': NO_DRIVE,
        },
        OPENCOLL: {
            'function': 'OPEN-COLLECTOR',
            'func_str': 'OPENCOLL',
            'drive': ONESIDE_DRIVE,
            'max_rcv': TRISTATE_DRIVE,
            'min_rcv': NO_DRIVE,
        },
        OPENEMIT: {
            'function': 'OPEN-EMITTER',
            'func_str': 'OPENEMIT',
            'drive': ONESIDE_DRIVE,
            'max_rcv': TRISTATE_DRIVE,
            'min_rcv': NO_DRIVE,
        },
        NOCONNECT: {
            'function': 'NO-CONNECT',
            'func_str': 'NOCONNECT',
            'drive': NOCONNECT_DRIVE,
            'max_rcv': NOCONNECT_DRIVE,
            'min_rcv': NOCONNECT_DRIVE,
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

    def copy(self, num_copies=1, **attribs):
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

            # Attach additional attributes to the pin.
            for k, v in attribs.items():
                setattr(cpy, k, v)

            copies.append(cpy)

        return list_or_scalar(copies)

    # Make copies with the multiplication operator or by calling the object.
    __mul__ = copy
    __rmul__ = copy
    __call__ = copy

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
        part_ref = getattr(self.part, 'ref', '???')
        pin_num = getattr(self, 'num', '???')
        pin_name = getattr(self, 'name', '???')
        pin_func = getattr(self, 'func', Pin.UNSPEC)
        pin_func_str = Pin.pin_info[pin_func]['function']
        return 'Pin {ref}/{num}/{name}/{func}'.format(
            ref=part_ref, num=pin_num, name=pin_name, func=pin_func_str)

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
                    v = 'Pin.' + Pin.pin_info[v]['func_str']
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
