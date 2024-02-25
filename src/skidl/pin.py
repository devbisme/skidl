# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Handles part pins.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import random
import re
import sys
from builtins import range, super
from collections import defaultdict
from copy import copy
from enum import IntEnum
from functools import total_ordering

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .logger import active_logger
from .skidlbaseobj import ERROR, OK, WARNING, SkidlBaseObject
from .utilities import (
    expand_buses,
    expand_indices,
    export_to_all,
    find_num_copies,
    flatten,
    from_iadd,
    rmv_iadd,
    set_iadd,
    to_list,
)



@export_to_all
@total_ordering
class Pin(SkidlBaseObject):
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
    types = IntEnum(
        "types",
        (
            "INPUT",
            "OUTPUT",
            "BIDIR",
            "TRISTATE",
            "PASSIVE",
            "UNSPEC",
            "PWRIN",
            "PWROUT",
            "OPENCOLL",
            "OPENEMIT",
            "PULLUP",
            "PULLDN",
            "NOCONNECT",
            "FREE",
        ),
    )

    # Various drive levels a pin can output.
    # The order of these is important! The first entry has the weakest
    # drive and the drive increases for each successive entry.
    drives = IntEnum(
        "drives",
        (
            "NOCONNECT",  #  NC pin drive.
            "NONE",  # No drive capability (like an input pin).
            "PASSIVE",  # Small drive capability, but less than a pull-up or pull-down.
            "PULLUPDN",  # Pull-up or pull-down capability.
            "ONESIDE",  # Can pull high (open-emitter) or low (open-collector).
            "TRISTATE",  # Can pull high/low and be in high-impedance state.
            "PUSHPULL",  # Can actively drive high or low.
            "POWER",  # A power supply or ground line.
        ),
    )

    # Information about the various types of pins:
    #   function: A string describing the pin's function.
    #   drive: The drive capability of the pin.
    #   rcv_min: The minimum amount of drive the pin must receive to function.
    #   rcv_max: The maximum amount of drive the pin can receive and still function.
    pin_info = {
        types.INPUT: {
            "function": "INPUT",
            "func_str": "INPUT",
            "drive": drives.NONE,
            "max_rcv": drives.POWER,
            "min_rcv": drives.PASSIVE,
        },
        types.OUTPUT: {
            "function": "OUTPUT",
            "func_str": "OUTPUT",
            "drive": drives.PUSHPULL,
            "max_rcv": drives.PASSIVE,
            "min_rcv": drives.NONE,
        },
        types.BIDIR: {
            "function": "BIDIRECTIONAL",
            "func_str": "BIDIR",
            "drive": drives.TRISTATE,
            "max_rcv": drives.POWER,
            "min_rcv": drives.NONE,
        },
        types.TRISTATE: {
            "function": "TRISTATE",
            "func_str": "TRISTATE",
            "drive": drives.TRISTATE,
            "max_rcv": drives.TRISTATE,
            "min_rcv": drives.NONE,
        },
        types.PASSIVE: {
            "function": "PASSIVE",
            "func_str": "PASSIVE",
            "drive": drives.PASSIVE,
            "max_rcv": drives.POWER,
            "min_rcv": drives.NONE,
        },
        types.PULLUP: {
            "function": "PULLUP",
            "func_str": "PULLUP",
            "drive": drives.PULLUPDN,
            "max_rcv": drives.POWER,
            "min_rcv": drives.NONE,
        },
        types.PULLDN: {
            "function": "PULLDN",
            "func_str": "PULLDN",
            "drive": drives.PULLUPDN,
            "max_rcv": drives.POWER,
            "min_rcv": drives.NONE,
        },
        types.UNSPEC: {
            "function": "UNSPECIFIED",
            "func_str": "UNSPEC",
            "drive": drives.NONE,
            "max_rcv": drives.POWER,
            "min_rcv": drives.NONE,
        },
        types.PWRIN: {
            "function": "POWER-IN",
            "func_str": "PWRIN",
            "drive": drives.NONE,
            "max_rcv": drives.POWER,
            "min_rcv": drives.POWER,
        },
        types.PWROUT: {
            "function": "POWER-OUT",
            "func_str": "PWROUT",
            "drive": drives.POWER,
            "max_rcv": drives.PASSIVE,
            "min_rcv": drives.NONE,
        },
        types.OPENCOLL: {
            "function": "OPEN-COLLECTOR",
            "func_str": "OPENCOLL",
            "drive": drives.ONESIDE,
            "max_rcv": drives.TRISTATE,
            "min_rcv": drives.NONE,
        },
        types.OPENEMIT: {
            "function": "OPEN-EMITTER",
            "func_str": "OPENEMIT",
            "drive": drives.ONESIDE,
            "max_rcv": drives.TRISTATE,
            "min_rcv": drives.NONE,
        },
        types.NOCONNECT: {
            "function": "NO-CONNECT",
            "func_str": "NOCONNECT",
            "drive": drives.NOCONNECT,
            "max_rcv": drives.NOCONNECT,
            "min_rcv": drives.NOCONNECT,
        },
        types.FREE: {
            "function": "FREE",
            "func_str": "FREE",
            "drive": drives.NONE,
            "max_rcv": drives.POWER,
            "min_rcv": drives.NOCONNECT,
        },
    }

    def __init__(self, **attribs):
        super().__init__()

        self.nets = []
        self.part = None
        self.name = ""
        self.num = ""
        self.stub = False
        self.do_erc = True
        self.func = self.types.UNSPEC  # Pin function defaults to unspecified.

        # Set pin number as a random integer so that calling Pin() multiple
        # times will give pins that are distinct according to __eq__.
        # This pin number gets overridden if the num is set in attribs.
        self.num = random.randint(100000, sys.maxsize)

        # Attach additional attributes to the pin.
        for k, v in list(attribs.items()):
            setattr(self, k, v)

    def __str__(self):
        """Return a description of this pin as a string."""
        ref = getattr(self.part, "ref", "???")
        num, names, func = self.get_pin_info()
        return "Pin {ref}/{num}/{names}/{func}".format(**locals())

    __repr__ = __str__

    def __bool__(self):
        """Any valid Pin is True."""
        return True

    __nonzero__ = __bool__  # Python 2 compatibility.

    def __lt__(self, o):
        if not isinstance(o, type(self)):
            return NotImplemented
        if self.part != o.part:
            raise ValueError("Comparing pins on different parts not supported.")
        return self._normalize_num() < o._normalize_num()

    def __eq__(self, o):
        if not isinstance(o, type(self)):
            return NotImplemented
        return self.part == o.part and self._normalize_num() == o._normalize_num()

    def __and__(self, obj):
        """Attach a pin and another part/pin/net in serial."""
        from .network import Network

        return Network(self) & obj

    def __rand__(self, obj):
        """Attach a pin and another part/pin/net in serial."""
        from .network import Network

        return obj & Network(self)

    def __or__(self, obj):
        """Attach a pin and another part/pin/net in parallel."""
        from .network import Network

        return Network(self) | obj

    def __ror__(self, obj):
        """Attach a pin and another part/pin/net in parallel."""
        from .network import Network

        return obj | Network(self)

    # Defining an __eq__ method will make Pins unhashable unless we
    # explicitly define a hash method.
    __hash__ = SkidlBaseObject.__hash__

    # Make copies with the multiplication operator or by calling the object.
    def __call__(self, num_copies=None, **attribs):
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

        return self.copy(num_copies=num_copies, **attribs)

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
        indices = list(set(expand_indices(0, self.width - 1, False, *ids)))
        if indices is None or len(indices) == 0:
            return None
        if len(indices) > 1:
            active_logger.raise_(ValueError, "Can't index a pin with multiple indices.")
        if indices[0] != 0:
            active_logger.raise_(ValueError, "Can't use a non-zero index for a pin.")
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
        if from_iadd(pins_nets_buses):
            rmv_iadd(pins_nets_buses)
            return

        # No iadd_flag or it wasn't set. This means a direct assignment
        # was made to the pin, which is not allowed.
        active_logger.raise_(TypeError, "Can't assign to a Net! Use the += operator.")

    def __iter__(self):
        """
        Return an iterator for stepping through the pin.
        """
        # You can only iterate a Pin one time.
        return (self for i in [0])  # Return generator expr.

    def __iadd__(self, *pins_nets_buses):
        """
        Return the pin after connecting it to one or more nets or pins using the += operator.

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
        return self.connect(*pins_nets_buses)

    @classmethod
    def add_type(cls, *pin_types):
        """
        Add new pin type identifiers to the list of pin types.

        Args:
            pin_types: Strings identifying zero or more pin types.
        """
        cls.types = IntEnum("types", [m.name for m in cls.types] + list(pin_types))

        # Also add the pin types as attributes of the Pin class so
        # existing SKiDL part libs will still work (e.g. Pin.INPUT
        # still works as well as the newer Pin.types.INPUT).
        for m in cls.types:
            setattr(cls, m.name, m)

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
            active_logger.raise_(
                ValueError,
                "Can't make a non-integer number ({}) of copies of a pin!".format(
                    num_copies
                ),
            )
        if num_copies < 0:
            active_logger.raise_(
                ValueError,
                "Can't make a negative number ({}) of copies of a pin!".format(
                    num_copies
                ),
            )

        copies = []
        for _ in range(num_copies):

            # Make a shallow copy of the pin.
            cpy = copy(self)

            # The copy is not on a net, yet.
            cpy.nets = []

            # Attach additional attributes to the pin.
            for k, v in list(attribs.items()):
                setattr(cpy, k, v)

            # Connect the new pin to the same net as the original.
            if self.nets:
                self.nets[0] += cpy

            # Copy the aliases for the pin if it has them.
            cpy.aliases = self.aliases

            copies.append(cpy)

        # Return a list of the copies made or just a single copy.
        if return_list:
            return copies
        return copies[0]

    def is_connected(self):
        """Return true if a pin is connected to a net (but not a no-connect net)."""

        from .net import NCNet, Net

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
            active_logger.raise_(
                ValueError,
                "{} is connected to both normal and no-connect nets!".format(
                    self.erc_desc()
                ),
            )
        # This is just strange...
        active_logger.raise_(
            ValueError,
            "{} is connected to something strange: {}.".format(
                self.erc_desc(), self.nets
            ),
        )

    def is_attached(self, pin_net_bus):
        """Return true if this pin is attached to the given pin, net or bus."""

        from .net import Net
        from .pin import Pin

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
        active_logger.raise_(
            ValueError,
            "Pins can't be attached to {}!".format(type(pin_net_bus)),
        )

    def split_name(self, delimiters):
        """Use chars in divider to split a pin name and add substrings to aliases."""

        # Split pin name and add subnames as aliases.
        self.aliases += re.split("[" + re.escape(delimiters) + "]", self.name)

        # Remove any empty aliases.
        self.aliases.clean()

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

        from .net import Net
        from .protonet import ProtoNet

        # Go through all the pins and/or nets and connect them to this pin.
        for pn in expand_buses(flatten(pins_nets_buses)):
            if isinstance(pn, ProtoNet):
                pn += self
            elif isinstance(pn, Pin):
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
                active_logger.raise_(
                    TypeError,
                    "Cannot attach non-Pin/non-Net {} to {}.".format(
                        type(pn), self.erc_desc()
                    ),
                )

        # Set the flag to indicate this result came from the += operator.
        set_iadd(self, True)

        return self

    def disconnect(self):
        """Disconnect this pin from all nets."""
        if not self.net:
            return
        for n in self.nets:
            n.disconnect(self)
            n.merge_names()  # Clean-up the net after removing a pin.
        self.nets = []

    def move(self, net):
        """Move pin to another net.

        Args:
            net (Net): Destination net for pin.
        """

        self.disconnect()
        net += self

    def get_nets(self):
        """Return a list containing the Net objects connected to this pin."""
        return self.nets

    def get_pins(self):
        """Return a list containing this pin."""
        return to_list(self)

    def create_network(self):
        """Create a network from a single pin."""
        from .network import Network

        ntwk = Network()
        ntwk.append(self)
        return ntwk

    def chk_conflict(self, other_pin):
        """Check for electrical rule conflicts between this pin and another."""

        if not self.do_erc or not other_pin.do_erc:
            return

        [erc_result, erc_msg] = conflict_matrix[self.func][other_pin.func]

        # Return if the pins are compatible.
        if erc_result == OK:
            return

        # Otherwise, generate an error or warning message.
        if not erc_msg:
            erc_msg = " ".join(
                (
                    self.pin_info[self.func]["function"],
                    "connected to",
                    other_pin.pin_info[other_pin.func]["function"],
                )
            )
        n = self.net.name
        p1 = self.erc_desc()
        p2 = other_pin.erc_desc()
        msg = "Pin conflict on net {n}, {p1} <==> {p2} ({erc_msg})".format(**locals())
        if erc_result == WARNING:
            active_logger.warning(msg)
        else:
            active_logger.error(msg)

    def erc_desc(self):
        """Return a string describing this pin for ERC."""
        desc = "{func} pin {num}/{name} of {part}".format(
            part=self.part.erc_desc(),
            num=self.num,
            name=self.name,
            func=Pin.pin_info[self.func]["function"],
        )
        return desc

    def get_pin_info(self):
        num = getattr(self, "num", "???")
        names = [getattr(self, "name", "???")]
        names.extend(self.aliases)
        names = ",".join(names)
        func = Pin.pin_info[self.func]["function"]
        return num, names, func

    def export(self):
        """Return a string to recreate a Pin object."""
        attribs = []
        for k in ["num", "name", "func", "do_erc"]:
            v = getattr(self, k, None)
            if v:
                if k == "func":
                    # Assign the pin function using the actual name of the
                    # function, not its numerical value (in case that changes
                    # in the future if more pin functions are added).
                    v = "Pin.types." + Pin.pin_info[v]["func_str"]
                else:
                    v = repr(v)
                attribs.append("{}={}".format(k, v))
        return "Pin({})".format(",".join(attribs))

    def _normalize_num(self):
        """Normalize pin numbers into a tuple for comparison purposes.

        Returns:
            tuple: Tuple consisting of BGA row identifier and numeric column.
                If it's not a BGA pin, then the tuple contains just a single number.
        """

        # Split the pin number into an initial alpha BGA row followed by column number.
        n = list(re.match(r"(\D*)(.*)", str(self.num)).group(1, 2))

        # Uppercase the BGA row. This has no effect if it's not a BGA.
        n[0] = n[0].upper()

        # Convert the column number (or just the single pin number) to an integer if possible.
        try:
            n[-1] = int(n[-1])
        except ValueError:
            pass

        # return the pin number tuple.
        return n

    @property
    def pins(self):
        return self.get_pins()

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
        try:
            return self._drive
        except AttributeError:
            # Drive unspecified, so use default drive for this type of pin.
            return self.pin_info[self.func]["drive"]

    @drive.setter
    def drive(self, drive):
        self._drive = drive

    @drive.deleter
    def drive(self):
        try:
            del self._drive
        except AttributeError:
            pass

    @property
    def ref(self):
        """Return the reference of the part the pin belongs to."""
        return self.part.ref

    @property
    def circuit(self):
        """Return the circuit of the part the pin belongs to."""
        return self.part.circuit


##############################################################################


@export_to_all
class PhantomPin(Pin):
    """
    A pin type that exists solely to tie two pinless nets together.
    It will not participate in generating any netlists.
    """

    def __init__(self, **attribs):
        super().__init__(**attribs)
        self.nets = []
        self.part = None
        self.do_erc = False


##############################################################################


# This will make all the Pin.drive members into attributes of the Pin class
# so things like Pin.INPUT will work as well as Pin.types.INPUT.
Pin.add_type()

# Create the pin conflict matrix as a defaultdict of defaultdicts which
# returns OK if the given element is not in the matrix. This would indicate
# the pin types used to index that element have no contention if connected.
conflict_matrix = defaultdict(lambda: defaultdict(lambda: [OK, ""]))

# Add the non-OK pin connections to the matrix.
conflict_matrix[Pin.types.OUTPUT][Pin.types.OUTPUT] = [ERROR, ""]
conflict_matrix[Pin.types.TRISTATE][Pin.types.OUTPUT] = [WARNING, ""]
conflict_matrix[Pin.types.UNSPEC][Pin.types.INPUT] = [WARNING, ""]
conflict_matrix[Pin.types.UNSPEC][Pin.types.OUTPUT] = [WARNING, ""]
conflict_matrix[Pin.types.UNSPEC][Pin.types.BIDIR] = [WARNING, ""]
conflict_matrix[Pin.types.UNSPEC][Pin.types.TRISTATE] = [WARNING, ""]
conflict_matrix[Pin.types.UNSPEC][Pin.types.PASSIVE] = [WARNING, ""]
conflict_matrix[Pin.types.UNSPEC][Pin.types.PULLUP] = [WARNING, ""]
conflict_matrix[Pin.types.UNSPEC][Pin.types.PULLDN] = [WARNING, ""]
conflict_matrix[Pin.types.UNSPEC][Pin.types.UNSPEC] = [WARNING, ""]
conflict_matrix[Pin.types.PWRIN][Pin.types.TRISTATE] = [WARNING, ""]
conflict_matrix[Pin.types.PWRIN][Pin.types.UNSPEC] = [WARNING, ""]
conflict_matrix[Pin.types.PWROUT][Pin.types.OUTPUT] = [ERROR, ""]
conflict_matrix[Pin.types.PWROUT][Pin.types.BIDIR] = [WARNING, ""]
conflict_matrix[Pin.types.PWROUT][Pin.types.TRISTATE] = [ERROR, ""]
conflict_matrix[Pin.types.PWROUT][Pin.types.UNSPEC] = [WARNING, ""]
conflict_matrix[Pin.types.PWROUT][Pin.types.PWROUT] = [ERROR, ""]
conflict_matrix[Pin.types.OPENCOLL][Pin.types.OUTPUT] = [ERROR, ""]
conflict_matrix[Pin.types.OPENCOLL][Pin.types.BIDIR] = [WARNING, ""]
conflict_matrix[Pin.types.OPENCOLL][Pin.types.TRISTATE] = [ERROR, ""]
conflict_matrix[Pin.types.OPENCOLL][Pin.types.UNSPEC] = [WARNING, ""]
conflict_matrix[Pin.types.OPENCOLL][Pin.types.PWROUT] = [ERROR, ""]
conflict_matrix[Pin.types.OPENEMIT][Pin.types.OUTPUT] = [ERROR, ""]
conflict_matrix[Pin.types.OPENEMIT][Pin.types.BIDIR] = [WARNING, ""]
conflict_matrix[Pin.types.OPENEMIT][Pin.types.TRISTATE] = [ERROR, ""]
conflict_matrix[Pin.types.OPENEMIT][Pin.types.UNSPEC] = [WARNING, ""]
conflict_matrix[Pin.types.OPENEMIT][Pin.types.PWROUT] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.INPUT] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.OUTPUT] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.BIDIR] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.TRISTATE] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.PASSIVE] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.PULLUP] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.PULLDN] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.UNSPEC] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.PWRIN] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.PWROUT] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.OPENCOLL] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.OPENEMIT] = [ERROR, ""]
conflict_matrix[Pin.types.NOCONNECT][Pin.types.NOCONNECT] = [ERROR, ""]
conflict_matrix[Pin.types.PULLUP][Pin.types.PULLUP] = [
    WARNING,
    "Multiple pull-ups connected.",
]
conflict_matrix[Pin.types.PULLDN][Pin.types.PULLDN] = [
    WARNING,
    "Multiple pull-downs connected.",
]
conflict_matrix[Pin.types.PULLUP][Pin.types.PULLDN] = [
    ERROR,
    "Pull-up connected to pull-down.",
]

# Fill-in the other half of the symmetrical contention matrix by looking
# for entries that != OK at position (r,c) and copying them to position
# (c,r).
cols = list(conflict_matrix.keys())
for c in cols:
    for r in list(conflict_matrix[c].keys()):
        conflict_matrix[r][c] = conflict_matrix[c][r]
