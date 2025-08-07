# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Network connection management for SKiDL circuit design.

This module provides comprehensive electrical connection management through the Net
class and its specialized subclass NCNet. These classes represent electrical
connections between component pins, enabling circuit designers to model, analyze,
and verify electrical connectivity in their designs.

Key Capabilities:
    - Electrical connection modeling between component pins
    - Named and anonymous net creation with automatic naming
    - Net merging and electrical rule checking (ERC)
    - Drive strength management and conflict detection  
    - Net class assignment for PCB routing rules
    - Hierarchical net traversal and connectivity analysis
    - No-connect (NC) net support for unconnected pins
    - Integration with netlist generation and PCB tools

Core Classes:
    Net: Primary class representing electrical connections between pins.
        Supports naming, drive strength, net classes, ERC, and connection
        management. Handles automatic net merging when pins are connected.
        
    NCNet: Specialized Net subclass for explicitly unconnected pins.
        Marks pins as intentionally not connected to suppress ERC warnings
        while maintaining design intent documentation.

Connection Model:
    Nets use a pin-centric connection model where pins can belong to multiple
    nets simultaneously, enabling complex electrical relationships. When nets
    are joined (via pin connections), they form electrically connected segments
    that share properties like drive strength and net classes.

Electrical Rules:
    The module supports comprehensive electrical rule checking (ERC) including:
    - Drive strength conflicts (multiple drivers on one net)
    - Floating pin detection (inputs without drivers)
    - No-connect verification (intentionally unconnected pins)
    - Net class rule validation and conflict resolution

Example Usage:
    >>> # Create named and anonymous nets
    >>> vcc = Net('VCC')                    # Named power net
    >>> gnd = Net('GND')                    # Named ground net  
    >>> data = Net()                        # Anonymous net (auto-named)
    >>> 
    >>> # Connect component pins to nets
    >>> vcc += mcu['VCC'], regulator['OUT'] # Multiple connections
    >>> gnd += mcu['GND'], regulator['GND'] # Ground connections
    >>> data += mcu['PA0'], sensor['DATA']  # Data connection
    >>> 
    >>> # Create no-connect nets for unused pins
    >>> nc = NCNet()                        # No-connect net
    >>> nc += mcu['UNUSED1'], mcu['UNUSED2'] # Mark pins as NC
    >>> 
    >>> # Apply net classes for PCB routing
    >>> power_class = NetClass('Power', trace_width=0.5, clearance=0.2)
    >>> vcc.netclass = power_class          # Apply to power nets
    >>> 
    >>> # Check electrical connectivity
    >>> print(f"VCC has {len(vcc)} pins connected")
    >>> print(f"Data net name: {data.name}")
    >>> if vcc.is_attached(mcu['VCC']):
    ...     print("MCU VCC pin is connected to VCC net")

Advanced Features:
    - Multi-segment nets with automatic name merging
    - Drive strength propagation and conflict detection
    - Hierarchical net traversal for complex connectivity
    - Stub net support for schematic generation
    - Network object creation for circuit analysis
    - XML and netlist export for PCB tools
    - Deep copying with automatic name adjustment

Integration:
    Nets integrate seamlessly with other SKiDL components:
    - Parts: Automatic connection via pin assignments
    - Buses: Multi-bit connection management  
    - Circuits: Automatic net registration and naming
    - ERC: Built-in electrical rule checking
    - Tools: Export to KiCad, Altium, Eagle, etc.
"""

import collections
from collections.abc import Iterable
import re
from copy import copy, deepcopy

from .erc import dflt_net_erc
from .logger import active_logger
from .netclass import NetClass, NetClassList
from .skidlbaseobj import SkidlBaseObject
from .utilities import (
    expand_buses,
    expand_indices,
    export_to_all,
    filter_list,
    find_num_copies,
    flatten,
    from_iadd,
    get_unique_name,
    rmv_iadd,
    set_iadd,
)


__all__ = ["NET_PREFIX"]

# Prefix for implicit nets.
NET_PREFIX = "N$"

Traversal = collections.namedtuple("Traversal", ["nets", "pins"])


@export_to_all
class Net(SkidlBaseObject):
    """
    Represents an electrical connection between component pins in a circuit.
    
    The Net class is the fundamental building block for electrical connectivity
    in SKiDL circuits. It manages collections of pins that are electrically
    connected, handles net naming and drive strength management, supports net
    classes for PCB routing rules, and provides electrical rule checking (ERC).
    
    Nets can be created with explicit names or receive automatically generated
    names. They support dynamic connection and disconnection of pins, automatic
    merging when nets are joined through common pins, and property propagation
    across connected net segments.

    Connection Management:
        Nets use the += operator for intuitive pin connection syntax. When pins
        are connected to nets, the nets automatically merge if the pins were
        previously connected to other nets, creating larger electrically
        connected groups.

    Drive Strength:
        Nets automatically track and manage drive strength based on connected
        pins. Drive conflicts (multiple strong drivers) are detected and can
        be flagged during ERC. The net's drive strength is always the maximum
        of all connected pins.

    Net Classes:
        Nets can be assigned to one or more net classes that define PCB routing
        rules, trace widths, clearances, via sizes, and other physical
        properties. These are used during PCB layout and design rule checking.

    Electrical Rules:
        Built-in ERC functions check for common electrical problems including
        floating inputs, drive conflicts, and design rule violations. Custom
        ERC functions can be added for specific design requirements.
    
    Args:
        name (str, optional): Explicit name for the net. If None or empty,
            an automatically generated unique name will be assigned using
            the NET_PREFIX pattern (e.g., "N$1", "N$2", etc.).
        circuit (Circuit, optional): The circuit this net belongs to.
            If None, the net is added to the default active circuit.
        *pins_nets_buses: Initial pins, nets, or buses to connect to this net.
            Can be individual objects or collections. Nets will be merged
            if pins connect previously separate nets.
        
    Keyword Args:
        attribs: Arbitrary keyword=value attributes to attach to the net.
            Common attributes include drive strength overrides, ERC flags,
            documentation strings, and tool-specific properties.
        
    Examples:
        >>> # Create named nets for power and ground
        >>> vcc = Net('VCC')           # 3.3V power rail
        >>> gnd = Net('GND')           # Ground reference
        >>> 
        >>> # Create anonymous nets (auto-named)
        >>> data_net = Net()           # Becomes "N$1" 
        >>> clock_net = Net()          # Becomes "N$2"
        >>> 
        >>> # Connect pins during creation
        >>> spi_clk = Net('SPI_CLK', mcu['SCK'], flash['CLK'])
        >>> 
        >>> # Connect pins after creation
        >>> data_net += mcu['PA0']     # Connect single pin
        >>> data_net += sensor['OUT'], led['IN']  # Connect multiple pins
        >>> 
        >>> # Apply net classes for PCB routing
        >>> power_class = NetClass('Power', trace_width=0.5)
        >>> vcc.netclass = power_class
        >>> 
        >>> # Check connections and properties
        >>> print(f"VCC net has {len(vcc)} pins")
        >>> print(f"Drive strength: {vcc.drive}")
        >>> if vcc.is_attached(mcu['VCC']):
        ...     print("MCU VCC pin is on VCC net")

    Advanced Usage:
        >>> # Create multiple copies for arrays
        >>> data_buses = 8 * Net('DATA')  # Creates DATA_0 through DATA_7
        >>> 
        >>> # Merge nets by connecting common pins
        >>> net1 = Net('SIGNAL_A')
        >>> net2 = Net('SIGNAL_B') 
        >>> shared_pin = mcu['PA1']
        >>> net1 += shared_pin     # Pin on net1
        >>> net2 += shared_pin     # Merges net1 and net2
        >>> 
        >>> # Use in network analysis
        >>> network = net1.create_network()  # Convert to Network object
        >>> 
        >>> # Export for PCB tools
        >>> netlist_data = vcc.generate_netlist_net('kicad')
    """

    # Set the default ERC functions for all Net instances.
    erc_list = [dflt_net_erc]

    def __init__(self, name=None, circuit=None, *pins_nets_buses, **attribs):
        """
        Initialize a new Net object with optional name and connections.

        Creates a new net with the specified name (or auto-generated name) and
        optionally connects it to the provided pins, nets, or buses. The net
        is automatically added to the specified circuit or the default circuit.

        Args:
            name (str, optional): Desired name for the net. Must be unique within
                the circuit. If None, empty, or conflicts with existing names,
                a unique name will be automatically generated using NET_PREFIX.
            circuit (Circuit, optional): Target circuit for the net. If None,
                the net is added to the currently active default circuit.
            *pins_nets_buses: Initial objects to connect to this net:
                - Pin objects: Individual pins from parts
                - Net objects: Other nets to merge with this one
                - Bus objects: Multi-bit collections (expanded to individual nets)
                - Lists/tuples: Collections of the above objects

        Keyword Args:
            attribs: Additional attributes to set on the net:
                - drive: Override automatic drive strength calculation
                - do_erc: Enable/disable ERC checking (default: True)
                - stub: Mark as stub net for schematic generation
                - Custom attributes for documentation or tool integration

        Raises:
            ValueError: If attempting to connect objects from different circuits.
            TypeError: If attempting to connect unsupported object types.

        Examples:
            >>> # Basic net creation
            >>> vcc = Net('VCC')                    # Named power net
            >>> data = Net()                        # Auto-named net
            >>> 
            >>> # Create with initial connections
            >>> spi_clk = Net('SPI_CLK', mcu['SCK'], flash['CLK'])
            >>> 
            >>> # Create with attributes
            >>> test_net = Net('TEST', do_erc=False, drive=pin_drives.STRONG)
            >>> 
            >>> # Create in specific circuit
            >>> sub_net = Net('SUB_SIGNAL', circuit=subcircuit)

        Automatic Naming:
            If no name is provided or the name conflicts with existing nets,
            an automatic name is generated using the pattern "N$1", "N$2", etc.
            This ensures all nets have unique, valid names within their circuit.

        Circuit Integration:
            The new net is automatically registered with its circuit, making it
            available for name lookups, ERC checking, and netlist generation.
            The circuit maintains references to all nets for global operations.
        """
        from .pin import pin_drives

        super().__init__()

        self._valid = True  # Make net valid before doing anything else.
        self.do_erc = True
        self._drive = pin_drives.NONE
        self._pins = []
        self.circuit = None
        self._netclass = NetClassList()  # Default net class list.
        self.code = None  # This is the net number used in a KiCad netlist file.
        self.stub = False  # Net is not a stub for schematic generation.

        # Set the net name directly to the passed-in name without any adjustment.
        # The net name will be adjusted when it is added to the circuit which
        # may already have a net with the same name.
        self._name = name

        # Add the net to the passed-in circuit or to the default circuit.
        circuit = circuit or default_circuit
        circuit += self

        # Attach whatever pins were given.
        self.connect(pins_nets_buses)
        del self.iadd_flag  # Remove the += flag inserted by connect().

        # Attach additional attributes to the net.
        for k, v in list(attribs.items()):
            setattr(self, k, v)

    def __bool__(self):
        """
        Return True if this is a valid net.
        
        Returns:
            bool: Always True for valid nets.
        """
        return True

    __nonzero__ = __bool__  # Python 2 compatibility.

    def __str__(self):
        """
        Return a string representation of the net and its connected pins.
        
        Returns:
            str: Net name followed by the pins connected to it, sorted alphabetically.
        """
        self.test_validity()
        pins = self.pins
        return (
            self.name + ": " + ", ".join([p.__str__() for p in sorted(pins, key=str)])
        )

    __repr__ = __str__  # TODO: This is a temporary fix. The __repr__ should be more informative.

    # Use += to connect to nets.
    def __iadd__(self, *pins_nets_buses):
        """
        Connect pins, nets, or buses to this net.
        
        Args:
            *pins_nets_buses: One or more Pin, Net, or Bus objects to connect.
            
        Returns:
            Net: Updated net with new connections.
        """
        return self.connect(*pins_nets_buses)

    def __and__(self, obj):
        """
        Connect this net and another object in series.
        
        Args:
            obj: Another part, pin, or net to connect in series with this net.
            
        Returns:
            Network: A series network containing this net and the other object.
        """
        from .network import Network

        return Network(self) & obj

    def __rand__(self, obj):
        """
        Connect another object and this net in series.
        
        Args:
            obj: Another part, pin, or net to connect in series with this net.
            
        Returns:
            Network: A series network containing the other object and this net.
        """
        from .network import Network

        return obj & Network(self)

    def __or__(self, obj):
        """
        Connect this net and another object in parallel.
        
        Args:
            obj: Another part, pin, or net to connect in parallel with this net.
            
        Returns:
            Network: A parallel network containing this net and the other object.
        """
        from .network import Network

        return Network(self) | obj

    def __ror__(self, obj):
        """
        Connect another object and this net in parallel.
        
        Args:
            obj: Another part, pin, or net to connect in parallel with this net.
            
        Returns:
            Network: A parallel network containing the other object and this net.
        """
        from .network import Network

        return obj | Network(self)

    def __len__(self):
        """
        Return the number of pins attached to this net.
        
        Returns:
            int: Number of pins connected to this net.
        """
        self.test_validity()
        return len(self.pins)

    def __getitem__(self, *ids):
        """
        Return the net if the indices resolve to a single index of 0.
        
        A net only has one element (itself), so the only valid index is 0.
        
        Args:
            *ids: A list of indices to apply to the net.
            
        Returns:
            Net: This net if the index is 0, otherwise None or raises an exception.
            
        Raises:
            ValueError: If multiple indices or a non-zero index is used.
        """

        # Resolve the indices.
        indices = list(set(expand_indices(0, self.width - 1, False, *ids)))
        if indices is None or len(indices) == 0:
            return None
        if len(indices) > 1:
            active_logger.raise_(ValueError, "Can't index a net with multiple indices.")
        if indices[0] != 0:
            active_logger.raise_(ValueError, "Can't use a non-zero index for a net.")
        return self

    def __setitem__(self, ids, *pins_nets_buses):
        """
        Prohibit direct assignment to nets. Use the += operator instead.
        
        This method is a work-around that allows the use of the += for making
connections to nets while         prohibiting direct assignment. Python
        processes something like net[0] += Pin() as follows::

            1. Net.__getitem__ is called with '0' as the index. This
               returns a single Net.
            2. The Net.__iadd__ method is passed the net and
               the thing to connect to it (a Pin in this case). This
               method makes the actual connection to the pin. Then
               it creates an iadd_flag attribute in the object it returns.
            3. Finally, Net.__setitem__ is called. If the iadd_flag attribute
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
        Return an iterator for stepping through the net.
        
        A net iterator only yields the net itself because a net has only one element.
        
        Returns:
            iterator: Generator that yields this net.
        """
        # You can only iterate a Net one time.
        return (self[i] for i in [0])  # Return generator expr.

    def __call__(self, num_copies=None, circuit=None, **attribs):
        """
        Create one or more copies of this net.
        
        Args:
            num_copies (int, optional): Number of copies to create.
            circuit (Circuit, optional): Circuit to add the copies to.
            **attribs: Additional attributes to apply to the copies.
            
        Returns:
            Net or list[Net]: Single net or list of net copies.
        """
        return self.copy(num_copies=num_copies, circuit=circuit, **attribs)

    def __mul__(self, num_copies):
        """
        Create multiple copies of this net using the multiplication operator.
        
        Args:
            num_copies (int): Number of copies to create.
            
        Returns:
            list[Net]: List of net copies.
        """
        if num_copies is None:
            num_copies = 0
        return self.copy(num_copies=num_copies)

    __rmul__ = __mul__

    @classmethod
    def get(cls, name, circuit=None):
        """
        Retrieve an existing net by name from a circuit.
        
        Searches the specified circuit (or default circuit) for a net with the
        given name or alias. This provides a convenient way to access existing
        nets without maintaining explicit references, especially useful in
        hierarchical designs or when working with imported netlists.

        The search examines both primary net names and any assigned aliases,
        using string matching to find the best match. Case-sensitive exact
        matching is performed for reliable net identification.
        
        Args:
            name (str): Name or alias of the net to find. Must match exactly
                (case-sensitive) either the net's primary name or one of its
                assigned aliases.
            circuit (Circuit, optional): Circuit to search for the net.
                If None, searches the currently active default circuit.
                
        Returns:
            Net or None: The found Net object if a match is found, otherwise
                None. For nets with multiple interconnected segments, returns
                the first segment found (all segments share the same name).
            
        Examples:
            >>> # Find nets by primary name
            >>> vcc = Net.get('VCC')                    # Find VCC net
            >>> ground = Net.get('GND', my_circuit)     # Find in specific circuit
            >>> 
            >>> # Find nets by alias
            >>> power = Net.get('POWER_RAIL')           # Might be alias for VCC
            >>> 
            >>> # Handle missing nets gracefully
            >>> test_net = Net.get('TEST_SIGNAL')
            >>> if test_net is None:
            ...     print("Test signal net not found")
            ... else:
            ...     print(f"Found net with {len(test_net)} pins")
            >>> 
            >>> # Use in conditional operations
            >>> existing_clk = Net.get('CLK') or Net('CLK')  # Get or create

        Search Strategy:
            The method searches in the following order:
            1. Primary net names (exact string match)
            2. Net aliases (exact string match)
            3. Returns None if no matches found

        Multi-segment Nets:
            For nets composed of multiple interconnected segments (created by
            merging nets), the search returns the first segment found. All
            segments of a multi-segment net share the same name, so any
            segment provides access to the complete electrical group.

        Circuit Context:
            Each circuit maintains its own namespace for net names. The same
            name can exist in different circuits without conflict. Always
            specify the circuit parameter when working with multiple circuits
            to ensure you get the net from the correct context.

        Performance:
            The search is optimized for typical circuit sizes but may be slower
            for very large circuits with thousands of nets. Consider maintaining
            direct references for frequently accessed nets in performance-critical
            applications.
        """
        from .alias import Alias

        circuit = circuit or default_circuit

        search_params = (("name", name, True), ("aliases", name, True))

        for attr, name, do_str_match in search_params:
            # filter_list() always returns a list. A net can consist of multiple
            # interconnected Net objects. If the list is non-empty,
            # just return the first Net object on the list.
            nets = filter_list(circuit.nets, do_str_match=do_str_match, **{attr: name})
            try:
                return nets[0]
            except IndexError:
                pass

        return None

    @classmethod  
    def fetch(cls, name, *args, **attribs):
        """
        Get an existing net by name, or create it if not found.
        
        This convenience method combines the functionality of get() and __init__()
        to provide a "get-or-create" pattern. It first attempts to find an existing
        net with the specified name, and if not found, creates a new net with that
        name and the provided parameters.

        This is particularly useful for building circuits where you want to
        reference nets by name without worrying about whether they already exist,
        such as when importing from netlists or building circuits procedurally.
        
        Args:
            name (str): Name of the net to fetch or create. Used for both
                the search (if net exists) and the name parameter (if creating).
            *args: Additional positional arguments passed to Net() constructor
                if creation is needed. Ignored if net already exists.
            **attribs: Keyword arguments passed to Net() constructor if creation
                is needed. The 'circuit' parameter is used for both search
                and creation contexts.
                
        Returns:
            Net: Either the existing net with the specified name, or a newly
                created net if no existing net was found. The returned net
                is guaranteed to have the requested name (or a unique variant).
            
        Examples:
            >>> # Basic fetch-or-create pattern
            >>> vcc = Net.fetch('VCC')                  # Creates if not exists
            >>> vcc2 = Net.fetch('VCC')                 # Returns existing net
            >>> assert vcc is vcc2                     # Same object
            >>> 
            >>> # Fetch with creation parameters
            >>> power = Net.fetch('POWER_RAIL',
            ...                   mcu['VCC'], regulator['OUT'],  # Initial connections
            ...                   do_erc=True,                   # ERC enabled
            ...                   circuit=main_circuit)          # Specific circuit
            >>> 
            >>> # Use in circuit building
            >>> def connect_power(part):
            ...     vcc = Net.fetch('VCC')              # Always get VCC net
            ...     gnd = Net.fetch('GND')              # Always get GND net  
            ...     vcc += part['VCC']                  # Connect power
            ...     gnd += part['GND']                  # Connect ground
            >>> 
            >>> # Procedural circuit construction
            >>> for i in range(8):
            ...     data_net = Net.fetch(f'DATA_{i}')
            ...     data_net += processor[f'D{i}'], memory[f'D{i}']

        Creation vs. Retrieval:
            - If a net with the specified name exists: Returns existing net,
              ignores all other parameters
            - If no net exists: Creates new net with all provided parameters
            - Circuit context: Used for both search and creation

        Name Uniqueness:
            If the requested name conflicts with existing nets during creation,
            the new net will receive a modified name (e.g., "VCC_1", "VCC_2")
            to maintain uniqueness within the circuit.

        Circuit Handling:
            The 'circuit' parameter serves dual purposes:
            - Search context: Where to look for existing nets
            - Creation context: Where to create new nets if needed
            - If not specified, uses the default circuit for both operations

        Error Handling:
            Creation errors (invalid parameters, circuit conflicts, etc.) are
            passed through from the Net() constructor. Retrieval errors are
            rare since get() returns None for missing nets rather than raising
            exceptions.

        Use Cases:
            - Importing circuits from external netlists
            - Procedural circuit generation with named nets
            - Building reusable circuit functions that reference standard nets
            - Interactive circuit construction where net existence is uncertain
        """
        circuit = attribs.get("circuit", default_circuit)
        return cls.get(name, circuit=circuit) or cls(name, *args, **attribs)

    def get_pins(self):
        """
        Get all pins connected to this net.
        
        Returns:
            list: List of pins attached to this net, including pins attached
                 to electrically connected segments.
        """
        self.test_validity()
        return self._traverse().pins

    def get_nets(self):
        """
        Get all connected net segments including this one.
        
        Returns:
            list: List of all net segments connected to this net, including this net.
        """
        self.test_validity()
        return self._traverse().nets

    def is_attached(self, pin_net_bus):
        """
        Check if a pin, net, or bus is electrically connected to this net.
        
        Args:
            pin_net_bus: A Pin, Net, or Bus object to check for attachment.
            
        Returns:
            bool: True if the object is electrically connected to this net.
            
        Raises:
            TypeError: If the given object is not a Pin, Net, or Bus.
        """
        if isinstance(pin_net_bus, Net):
            return pin_net_bus in self.nets
        if isinstance(pin_net_bus, Pin):
            return pin_net_bus.is_attached(self)
        if isinstance(pin_net_bus, Bus):
            for net in pin_net_bus[:]:
                if self.is_attached(net):
                    return True
            return False
        active_logger.raise_(
            TypeError, f"Nets can't be attached to {type(pin_net_bus)}!"
        )

    def is_movable(self):
        """
        Check if the net can be moved to another circuit.
        
        A net is movable if it's not part of a Circuit or if it has no pins
        attached to it.
        
        Returns:
            bool: True if the net is movable.
        """

        from .circuit import Circuit

        return not isinstance(self.circuit, Circuit) or not self._pins

    def is_implicit(self):
        """
        Check if the net has an implicitly generated name.
        
        Implicit net names start with NET_PREFIX or BUS_PREFIX.
        
        Returns:
            bool: True if the net name is implicitly generated.
        """

        from .bus import BUS_PREFIX

        self.test_validity()
        prefix_re = f"({re.escape(NET_PREFIX)}|{re.escape(BUS_PREFIX)})+"
        return re.match(prefix_re, self.name)

    def copy(self, num_copies=None, circuit=None, **attribs):
        """
        Create one or more copies of this net.
        
        Args:
            num_copies (int, optional): Number of copies to create.
                If None, a single copy will be made.
            circuit (Circuit, optional): The circuit the copies will be added to.
            **attribs: Attributes to apply to the copies.
                
        Returns:
            Net or list[Net]: A single Net copy or list of copies.
            
        Raises:
            ValueError: If num_copies is not a non-negative integer.
            ValueError: If trying to copy a net that already has pins attached.
            
        Examples:
            >>> n = Net('A')    # Create a net.
            >>> n_copy = n()    # Copy the net.
            >>> n_array = 10 * Net('A')  # Create an array of 10 nets.
        """

        self.test_validity()

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
                "Can't make a non-integer number "
                f"({num_copies}) of copies of a net!",
            )
        if num_copies < 0:
            active_logger.raise_(
                ValueError,
                "Can't make a negative number "
                f"({num_copies}) of copies of a net!",
            )

        # If circuit is not specified, then create the copies within circuit of the
        # original, or in the default circuit.
        circuit = circuit or self.circuit or default_circuit

        # Can't make a distinct copy of a net which already has pins on it
        # because what happens if a pin is connected to the copy? Then we have
        # to search for all the other copies to add the pin to those.
        # And what's the value of that?
        if self._pins:
            active_logger.raise_(
                ValueError,
                "Can't make copies of a net that already has " "pins attached to it!",
            )

        # Create a list of copies of this net.
        copies = []

        # Skip some Net attributes that would cause an infinite recursion exception
        # or net naming clashes.
        copy_attrs = vars(self).keys() - ["circuit", "traversal", "_name", "_aliases"]
        
        for i in range(num_copies):

            # Create a new net to store the copy.
            cpy = Net(circuit=circuit)

            # Make a copy of the net.
            cpy = copy(self)  # Start with shallow copy.
            for k,v in self.__dict__.items():
                if isinstance(v, Iterable) and not isinstance(v, str):
                    # Copy the list with shallow copies of its items to the copy.
                    setattr(cpy, k, copy(v))

            # Place the copy into the list of copies.
            copies.append(cpy)

        # Return a list of the copies made or just a single copy.
        if return_list:
            return copies
        return copies[0]

    def connect(self, *pins_nets_buses):
        """
        Connect pins, nets, and buses to this net, creating electrical connections.
        
        This is the primary method for building electrical connectivity in SKiDL
        circuits. It handles connecting individual pins, merging nets, and expanding
        buses into individual connections. When nets are connected through common
        pins, they automatically merge into larger electrically connected groups.

        The method supports the += operator for intuitive connection syntax and
        handles all the complexity of maintaining electrical connectivity, drive
        strength propagation, and net class inheritance across connected segments.
        
        Args:
            *pins_nets_buses: Objects to connect to this net:
                - Pin: Individual component pins to attach
                - Net: Other nets to merge with this one  
                - Bus: Multi-bit collections (individual nets extracted)
                - Lists/tuples: Collections of the above objects
                - None values: Ignored for programming convenience

        Returns:
            Net: This net object (supports method chaining and += operator).
            
        Raises:
            ValueError: If attempting to connect nets from different circuits.
                All connected objects must belong to the same circuit context.
            ValueError: If attempting to connect parts from different circuits.
                Component pins must be from parts in the same circuit.
            TypeError: If attempting to connect unsupported object types.
                Only Pin, Net, and Bus objects can be connected to nets.
            
        Examples:
            >>> # Connect individual pins
            >>> vcc = Net('VCC')
            >>> vcc.connect(mcu['VCC'], regulator['OUT'])
            >>> 
            >>> # Use += operator (equivalent to connect)
            >>> gnd = Net('GND')
            >>> gnd += mcu['GND'], regulator['GND'], capacitor[2]
            >>> 
            >>> # Connect nets (automatic merging)
            >>> signal_a = Net('SIG_A')
            >>> signal_b = Net('SIG_B')
            >>> shared_pin = buffer['OUT']
            >>> signal_a += shared_pin        # Pin on signal_a
            >>> signal_b += shared_pin        # Merges signal_a and signal_b
            >>> 
            >>> # Connect buses (expanded automatically)
            >>> data_bus = Bus('DATA', 8)     # 8-bit bus
            >>> control_net = Net('CTRL')
            >>> control_net += data_bus[0]    # Connect to bit 0 of bus
            >>> 
            >>> # Chain connections
            >>> clock_net = Net('CLK').connect(mcu['CLK'], rtc['CLK_OUT'])

        Net Merging:
            When connecting nets that already have pins attached, the nets
            automatically merge into a single electrical group. All properties
            like drive strength and net classes are combined according to
            precedence rules (maximum drive, class union, etc.).

        Drive Strength:
            Connected pins contribute their drive strength to the net. The net's
            overall drive is the maximum of all connected pins. Drive conflicts
            (multiple strong drivers) are detected during ERC checking.

        Net Classes:
            When nets are merged, their net classes are combined. If conflicting
            net classes are detected, warnings may be issued depending on the
            specific class definitions and priority levels.

        Circuit Validation:
            All connected objects must belong to the same circuit. Cross-circuit
            connections are not allowed and will raise ValueError exceptions.
            This maintains circuit encapsulation and prevents invalid topologies.
        """
        from .pin import PhantomPin, Pin

        def join(net):
            """
            Join nets by giving them each a pin in common.

            Args:
                net: The net to join with self.
            """

            if isinstance(self, NCNet):
                active_logger.raise_(
                    ValueError,
                    f"Can't join with a no-connect net {self.name}!",
                )

            if isinstance(net, NCNet):
                active_logger.raise_(
                    ValueError,
                    f"Can't join with a no-connect net {net.name}!",
                )

            # No need to do anything if merging a net with itself.
            if self == net:
                return

            # If this net has pins, just attach the other net to one of them.
            if self._pins:
                self._pins[0].nets.append(net)
                net._pins.append(self._pins[0])
            # If the other net has pins, attach this net to a pin on the other net.
            elif net._pins:
                net._pins[0].nets.append(self)
                self._pins.append(net._pins[0])
            # If neither net has any pins, then attach a phantom pin to one net
            # and then connect the nets together.
            else:
                p = PhantomPin()
                connect_pin(p)
                self._pins[0].nets.append(net)
                net._pins.append(self._pins[0])

            # Update the drive of the joined nets. When setting the drive of a
            # net the net drive will be the maximum of its current drive or the
            # new drive. So the following two operations will set each net
            # drive to the same maximum value.
            self.drive = net.drive
            net.drive = self.drive

            # Update the net class of the joined nets. The following two
            # operations will set each net's class to the same value, or
            # throw an error if they are in different classes.
            self.netclass = net.netclass
            net.netclass = self.netclass

        def connect_pin(pin):
            """Connect a pin to this net."""
            if pin not in self._pins:
                if not pin.is_connected():
                    # Remove the pin from the no-connect net if it is attached to it.
                    pin.disconnect()
                self._pins.append(pin)
                pin.nets.append(self)
                pin.stub = self.stub  # Update pin stub net for generating schematics.
            return

        self.test_validity()

        # Go through all the pins and/or nets and connect them to this net.
        for pn in expand_buses(flatten(pins_nets_buses)):
            if isinstance(pn, Net):
                if pn.circuit == self.circuit:
                    join(pn)
                else:
                    active_logger.raise_(
                        ValueError,
                        f"Can't attach nets in different circuits ({pn.circuit.name}, {self.circuit.name})!"
                    )
            elif isinstance(pn, Pin):
                if not pn.part or pn.part.circuit == self.circuit:
                    if not pn.part:
                        active_logger.warning(
                            f"Attaching non-part Pin {pn.name} to a Net {self.name}."
                        )
                    connect_pin(pn)
                elif not pn.part.circuit:
                    active_logger.warning(
                        f"Attaching part template Pin {pn.name} to a Net {self.name}."
                    )
                else:
                    active_logger.raise_(
                        ValueError,
                        f"Can't attach a part to a net in different circuits ({pn.part.circuit.name}, {self.circuit.name})!"
                    )
            else:
                active_logger.raise_(
                    TypeError,
                    f"Cannot attach non-Pin/non-Net {type(pn)} to Net {self.name}.",
                )

        # If something has been connected to a net, then recompute its traversal so the
        # correct number of connected pins and nets is recorded.
        try:
            del self.traversal
        except AttributeError:
            pass  # No traversal to delete.
        self._traverse()

        # Add the net to the global netlist. (It won't be added again
        # if it's already there.)
        self.circuit += self

        # Set the flag to indicate this result came from the += operator.
        set_iadd(self, True)

        return self

    def disconnect(self, pin):
        """
        Remove a pin from this net but not from other nets it's attached to.
        
        Args:
            pin (Pin): The pin to disconnect from this net.
        """
        try:
            self._pins.remove(pin)
        except ValueError:
            return  # Pin wasn't in the list, so abort.

        # If a pin has been disconnected from a net, then remove any existing traversal
        # so it will be recomputed the next time it is needed.
        try:
            del self.traversal
        except AttributeError:
            pass  # No traversal to delete.

    def merge_names(self):
        """
        For multi-segment nets, select a common name for all segments.
        
        When nets are joined, they can have different names. This method
        chooses the best name among connected net segments and assigns
        it to all of them.
        """

        def select_name(nets):
            """Return the net with the best name among a list of nets."""

            if len(nets) == 0:
                return None  # No nets, return None.
            if len(nets) == 1:
                return nets[0]  # One net, return it.
            if len(nets) == 2:
                # Two nets, return the best of them.
                name0 = getattr(nets[0], "name")
                name1 = getattr(nets[1], "name")
                fixed0 = getattr(nets[0], "fixed_name", False)
                fixed1 = getattr(nets[1], "fixed_name", False)
                if not name1:
                    return nets[0]
                if not name0:
                    return nets[1]
                if fixed0 and not fixed1:
                    return nets[0]
                if fixed1 and not fixed0:
                    return nets[1]
                if fixed0 and fixed1:
                    active_logger.raise_(
                        ValueError,
                        f"Cannot merge two nets with fixed names: {name0} and {name1}.",
                    )
                if nets[1].is_implicit():
                    return nets[0]
                if nets[0].is_implicit():
                    return nets[1]
                if name0 != name1:
                    active_logger.warning(
                        f"Merging two named nets ({name0} and {name1}) into {name0}."
                    )
                return nets[0]

            # More than two nets, so bisect the list into two smaller lists and
            # recursively find the best name from each list and then return the
            # best name of those two.
            mid_point = len(nets) // 2
            return select_name(
                [select_name(nets[0:mid_point]), select_name(nets[mid_point:])]
            )

        # Assign the same name to all the nets that are connected to this net.
        nets = self.nets
        selected_name = getattr(select_name(nets), "name")
        for net in nets:
            # Assign the name directly to each net. Using the name property
            # would cause the names to be changed so they were unique.
            net._name = selected_name  # pylint: disable=protected-access

    def create_network(self):
        """
        Create a Network object containing just this net.
        
        Returns:
            Network: A network containing this net.
        """
        from .network import Network

        ntwk = Network()
        ntwk.append(self)
        return ntwk

    def generate_netlist_net(self, tool=None):
        """
        Generate the net information for inclusion in a netlist.
        
        Args:
            tool (str, optional): The format for the netlist file (e.g., KICAD).
            
        Returns:
            str: The net information formatted for the specified tool.
        """

        import skidl

        from .tools import tool_modules

        tool = tool or skidl.config.tool

        self.test_validity()

        # Don't add anything to the netlist if no pins are on this net.
        if not self.pins:
            return

        return tool_modules[tool].gen_netlist_net(self)

    def generate_xml_net(self, tool=None):
        """
        Generate the net information for inclusion in an XML file.
        
        Args:
            tool (str, optional): The format for the XML file (e.g., KICAD).
            
        Returns:
            str: The net information formatted as XML for the specified tool.
        """

        import skidl

        from .tools import tool_modules

        tool = tool or skidl.config.tool

        self.test_validity()

        # Don't add anything to the XML if no pins are on this net.
        if not self.pins:
            return

        return tool_modules[tool].gen_xml_net(self)

    def _traverse(self):
        """
        Traverse all nets and pins connected to this net.
        
        This method builds a complete list of all pins and nets that are
        electrically connected to this net, either directly or indirectly.
        
        Returns:
            Traversal: A namedtuple containing lists of all connected nets and pins.
        """

        try:
            return self.traversal  # Return pre-existing traversal.
        except AttributeError:
            pass  # Compute the traversal if it's not available.

        from .pin import PhantomPin

        self.test_validity()
        prev_nets = set([self])
        nets = set([self])
        prev_pins = set([])
        pins = set(self._pins)
        while pins != prev_pins:

            # Add the nets attached to any unvisited pins.
            for pin in pins - prev_pins:
                # No use visiting a pin that is not connected to a net.
                if pin.is_connected():
                    nets |= set(pin.nets)

            # Update the set of previously visited pins.
            prev_pins = copy(pins)

            # Add the pins attached to any unvisited nets.
            for net in nets - prev_nets:
                pins |= set(net._pins)

            # Update the set of previously visited nets.
            prev_nets = copy(nets)

        # Remove any phantom pins that may have existed for tieing nets together.
        pins = set([p for p in pins if not isinstance(p, PhantomPin)])

        # Store the traversal.
        self.traversal = Traversal(nets=list(nets), pins=list(pins))

        # Every net connected to this one should have the same traversal.
        for n in self.traversal.nets:
            n.traversal = self.traversal

        return self.traversal

    @property
    def width(self):
        """
        Get the width of the net.
        
        Returns:
            int: Always 1 for a Net object.
        """
        return 1

    @property
    def name(self):
        """
        Get or set the name of this net.
        
        When setting the net name, if another net with the same name
        exists in the circuit, the name for this net will be adjusted
        to make it unique.
        
        Returns:
            str: Net name.
        """
        return super(Net, self).name

    @name.setter
    def name(self, name):
        """
        Set the name of this net.
        
        Args:
            name (str): The new name for the net.
        """
        self.test_validity()
        # Remove the existing name so it doesn't cause a collision if the
        # object is renamed with its existing name.
        del self.name

        # Now name the object with the given name or some variation
        # of it that doesn't collide with anything else in the list.
        super(Net, type(self)).name.fset(
            self, get_unique_name(self.circuit.nets, "name", NET_PREFIX, name)
        )

    @name.deleter
    def name(self):
        """Delete the net name."""
        self.test_validity()
        super(Net, type(self)).name.fdel(self)

    @property
    def pins(self):
        """
        Get the pins attached to this net.
        
        Returns:
            list: List of pins attached to this net.
        """
        return self.get_pins()

    @property
    def nets(self):
        """
        Get all net segments connected to this net.
        
        Returns:
            list: List of all net segments electrically connected to this net.
        """
        return self.get_nets()

    @property
    def netclass(self):
        """
        Get or set the net class(es) assigned to this net and connected segments.
        
        Net classes define PCB routing rules including trace widths, clearances,
        via sizes, and electrical properties. They control how nets are routed
        during PCB layout and enforce design constraints. A net can be assigned
        to multiple net classes for complex routing requirements.

        When setting net classes, the assignment automatically propagates to all
        electrically connected net segments, ensuring consistent routing rules
        across the entire electrical connection. This maintains design integrity
        when nets are merged or split during circuit construction.

        Returns:
            NetClassList: Container holding zero or more NetClass objects.
            An empty list indicates no net class assignments. The container
            supports iteration, indexing, and membership testing for
            convenient access to assigned classes.

        Examples:
            >>> # Check current net class assignments
            >>> power_net = Net('VCC')
            >>> print(len(power_net.netclass))          # 0 (no classes assigned)
            >>> 
            >>> # Assign single net class
            >>> power_class = NetClass('Power', trace_width=0.5, clearance=0.2)
            >>> power_net.netclass = power_class
            >>> print(len(power_net.netclass))          # 1
            >>> print(power_net.netclass[0].name)       # 'Power'
            >>> 
            >>> # Assign multiple net classes
            >>> critical_class = NetClass('Critical', priority=1)
            >>> power_net.netclass = power_class, critical_class
            >>> print(len(power_net.netclass))          # 2
            >>> 
            >>> # Check for specific class membership
            >>> if power_class in power_net.netclass:
            ...     print(f"Net uses {power_class.name} routing rules")
            >>> 
            >>> # Iterate through assigned classes
            >>> for nc in power_net.netclass:
            ...     print(f"Class: {nc.name}, Width: {nc.trace_width}mm")

        Multi-segment Propagation:
            When nets are electrically connected through shared pins, all
            segments automatically share the same net class assignments:
            
            >>> net1 = Net('SIG_A')
            >>> net2 = Net('SIG_B')
            >>> net1.netclass = power_class          # Assign to net1
            >>> shared_pin = mcu['PA1']
            >>> net1 += shared_pin                   # Connect pin to net1
            >>> net2 += shared_pin                   # Merges nets, shares classes
            >>> print(net2.netclass == net1.netclass)  # True

        Class Conflict Resolution:
            Multiple net classes with conflicting properties are resolved based
            on priority levels and tool-specific rules. Classes with higher
            priority numbers typically override lower priority classes:
            
            >>> low_priority = NetClass('Critical', priority=1, trace_width=0.8)
            >>> high_priority = NetClass('Standard', priority=10, trace_width=0.3)
            >>> signal_net.netclass = high_priority, low_priority
            >>> # PCB tool will likely use 0.8mm width from high_priority class

        Assignment Operations:
            Net class assignments are additive by default - new classes are
            added to existing assignments rather than replacing them:
            
            >>> signal_net.netclass = class1         # Assign first class
            >>> signal_net.netclass = class2         # Add second class
            >>> print(len(signal_net.netclass))      # 2 (both classes assigned)
            >>> 
            >>> # To replace all classes, delete first
            >>> del signal_net.netclass              # Clear all classes
            >>> signal_net.netclass = new_class      # Assign replacement

        PCB Tool Integration:
            Net class assignments are exported during netlist generation and
            become design rules in PCB layout tools. Different tools handle
            multiple classes differently - some merge properties, others use
            priority-based selection, and some apply all rules simultaneously.

        Design Rule Checking:
            Net classes enable automated design rule checking (DRC) during
            PCB layout. Violations of trace width, clearance, or via size
            rules generate errors that must be resolved before manufacturing.
        """
        self.test_validity()
        # Add all the net classes for all the hierarchical nodes surrounding this net.
        total_netclass = NetClassList(circuit=self.circuit)
        total_netclass.add(*self._netclass)
        for node in self.hiernodes:
            if hasattr(node, "netclass"):
                total_netclass.add(*node.netclass)
        return total_netclass

    @netclass.setter
    def netclass(self, *netclasses):
        """
        Assign one or more net classes to this net and all connected segments.
        
        Sets the net class assignment(s) for this net, automatically propagating
        the assignment to all electrically connected net segments. This ensures
        consistent routing rules across the entire electrical connection.

        Args:
            *netclasses: One or more NetClass objects or NetClassList objects
                to assign to this net. Multiple classes can be assigned
                simultaneously by passing multiple arguments.

        Examples:
            >>> power_net = Net('VCC')
            >>> power_class = NetClass('Power', trace_width=0.5)
            >>> critical_class = NetClass('Critical', priority=1)
            >>> 
            >>> # Assign single class
            >>> power_net.netclass = power_class
            >>> 
            >>> # Assign multiple classes
            >>> power_net.netclass = power_class, critical_class
            >>> 
            >>> # Assign from list
            >>> class_list = NetClassList(power_class, critical_class)
            >>> power_net.netclass = class_list

        Propagation:
            The assignment automatically propagates to all nets that are
            electrically connected to this net through shared pins. This
            maintains consistency across multi-segment nets.

        Additive Behavior:
            Net class assignments are additive - existing classes are retained
            when new classes are added. To replace all classes, delete the
            existing assignment first:
            >>> del power_net.netclass      # Clear existing classes
            >>> power_net.netclass = new_class  # Assign new class
        """
        self.test_validity()
        for net in self.nets:
            net._netclass.add(*netclasses, circuit=net.circuit)

    @netclass.deleter
    def netclass(self):
        """
        Remove all net class assignments from this net and connected segments.
        
        Clears all net class assignments from this net and all electrically
        connected net segments. After deletion, the nets will have no routing
        rules or design constraints beyond default values.

        Examples:
            >>> power_net = Net('VCC')
            >>> power_net.netclass = NetClass('Power')
            >>> print(power_net.netclass)              # <NetClass 'Power'>
            >>> 
            >>> del power_net.netclass                 # Remove all classes
            >>> print(power_net.netclass)              # None

        Multi-segment Behavior:
            The deletion propagates to all electrically connected net segments,
            ensuring consistent behavior across the entire electrical connection.
        """
        self.test_validity()
        nets = self.nets  # Get all interconnected subnets.
        for n in nets:
            n._netclass = NetClassList()

    @property
    def drive(self):
        """
        Get, set or delete the drive strength of this net.
        
        The drive strength represents the electrical driving capability of the net.
        It is automatically set to the maximum drive value of any pin connected to
        the net, and cannot be set to a lower value than the current maximum.
        
        Returns:
            int: The drive strength value.
        """
        self.test_validity()
        nets = self.nets  # Get all interconnected subnets.
        max_drive = max(nets, key=lambda n: n._drive)._drive
        return max_drive

    @drive.setter
    def drive(self, drive):
        """
        Set the drive strength for this net.
        
        Args:
            drive (int): The new drive strength value. If less than the current
                         value, the current value will be maintained.
        """
        self.test_validity()
        nets = self.nets  # Get all interconnected subnets.
        max_drive = max(nets, key=lambda n: n._drive)._drive
        max_drive = max(drive, max_drive)
        for n in nets:
            n._drive = max_drive

    @drive.deleter
    def drive(self):
        """Delete the drive strength from this net."""
        self.test_validity()
        nets = self.nets  # Get all interconnected subnets.
        for n in nets:
            del n._drive

    @property
    def stub(self):
        """
        Get or set the stub status of this net.
        
        A stub net is not routed in schematic generation, but
        is represented as a short stub connected to the pin.
        
        Returns:
            bool: True if this is a stub net.
        """
        return self._stub

    @stub.setter
    def stub(self, val):
        """
        Set the stub status for this net.
        
        Args:
            val (bool): True to make this a stub net, False otherwise.
        """
        self._stub = val
        for pin in self.get_pins():
            pin.stub = val

    @property
    def valid(self):
        """
        Check if this net is still valid.
        
        Returns:
            bool: True if the net is valid, False if it has been invalidated.
        """
        return self._valid

    @valid.setter
    def valid(self, val):
        """
        Set the validity status of this net.
        
        Args:
            val (bool): True to mark the net as valid, False to invalidate it.
        """
        self.test_validity()
        self._valid = val

    def test_validity(self):
        """
        Test if the net is valid for use.
        
        Raises:
            ValueError: If the net is no longer valid.
        """
        if self.valid:
            return
        active_logger.raise_(
            ValueError,
            f"Net {self.name} is no longer valid. Do not use it!",
        )


@export_to_all
class NCNet(Net):
    """
    A specialized Net subclass for explicitly marking pins as not connected.
    
    NCNet (No Connect Net) is used to explicitly mark component pins as
    intentionally unconnected. This serves two important purposes:
    
    1. Design Intent Documentation: Clearly indicates that leaving pins
       unconnected is intentional rather than an oversight.
       
    2. ERC Suppression: Prevents electrical rule checking from flagging
       these pins as floating or unconnected errors.

    NCNet objects behave like regular nets for connection purposes but have
    special properties that distinguish them from normal electrical connections.
    They don't appear in netlists since they represent the absence of
    electrical connections rather than actual connections.

    Common Use Cases:
        - Unused input pins on digital logic devices
        - Reserved pins on microcontrollers not used in current design
        - Optional features not implemented in current circuit variant
        - Test points or debugging pins not connected in production
        - Analog inputs not used in specific application configurations

    ERC Behavior:
        NCNet objects are excluded from normal ERC checking since they
        explicitly represent intentionally unconnected pins. This prevents
        false warnings about floating inputs or undriven nets while maintaining
        design verification for actual electrical connections.

    Netlist Generation:
        NCNet objects do not generate entries in netlists or connection lists
        since they represent the explicit absence of connections. PCB tools
        typically handle no-connect markers through special annotations rather
        than actual net connections.
    
    Args:
        name (str, optional): Name for the no-connect net. If None, an
            automatically generated name will be assigned. Multiple pins
            can share the same NCNet or use separate NCNet instances.
        circuit (Circuit, optional): The circuit this no-connect net belongs to.
            If None, uses the default circuit.
        *pins_nets_buses: Pins, nets, or buses to mark as not connected.
            These will be connected to this NCNet to indicate their
            no-connect status.
        
    Keyword Args:
        attribs: Additional attributes for the no-connect net. Note that
            some attributes like drive strength are automatically set to
            appropriate values for no-connect nets.
            
    Examples:
        >>> # Mark individual unused pins as no-connect
        >>> nc1 = NCNet()
        >>> nc1 += mcu['UNUSED_PA5'], mcu['UNUSED_PA6']
        >>> 
        >>> # Use separate NC nets for different pin groups
        >>> analog_nc = NCNet('ANALOG_NC')
        >>> digital_nc = NCNet('DIGITAL_NC') 
        >>> analog_nc += adc['AIN3'], adc['AIN4']
        >>> digital_nc += mcu['PB7'], mcu['PB8']
        >>> 
        >>> # Mark test points as no-connect in production
        >>> test_nc = NCNet('TEST_NC')
        >>> test_nc += test_point_1['PIN'], test_point_2['PIN']
        >>> 
        >>> # Create during component instantiation
        >>> mcu = Part('MCU', 'STM32F401')
        >>> nc_net = NCNet()
        >>> nc_net += mcu['BOOT0'], mcu['NRST']  # Not used in this design

    Design Verification:
        While NCNet pins are excluded from standard ERC checking, they can
        still be verified for design intent:
        - Confirm all NC pins are intentionally unconnected
        - Verify no required pins are accidentally marked as NC
        - Check that NC assignments match design specifications

    Tool Integration:
        Different PCB tools handle no-connect markers differently:
        - KiCad: No-connect flags on pins, excluded from netlist
        - Altium: No ERC markers, special netlist handling
        - Eagle: No-connect symbols, netlist exclusion
        - Other tools: Tool-specific no-connect representations

    Best Practices:
        - Use descriptive names for NC nets to document intent
        - Group related NC pins on the same NC net when appropriate
        - Document why specific pins are marked as no-connect
        - Review NC assignments during design reviews
        - Consider future design variants that might use NC pins
    """

    def __init__(self, name=None, circuit=None, *pins_nets_buses, **attribs):
        """
        Initialize a new no-connect net for unconnected pins.

        Creates a specialized net that marks pins as intentionally not connected,
        suppressing ERC warnings while documenting design intent. The NC net
        automatically sets appropriate drive characteristics and ERC flags.

        Args:
            name (str, optional): Name for the no-connect net. If None, an
                auto-generated name will be assigned. Using descriptive names
                helps document which pins are intentionally unconnected.
            circuit (Circuit, optional): Target circuit for the NC net.
                If None, the NC net is added to the default circuit.
            *pins_nets_buses: Initial pins to mark as no-connect:
                - Pin objects: Individual component pins to mark as NC
                - Collections: Lists or tuples of pins to mark together
                - Note: Connecting nets or buses to NCNet is unusual

        Keyword Args:
            attribs: Additional attributes for the NC net. Some attributes
                are automatically set to appropriate values:
                - drive: Set to NOCONNECT to indicate no driving capability
                - do_erc: Disabled to suppress ERC warnings

        Examples:
            >>> # Basic no-connect net creation
            >>> nc = NCNet()                            # Auto-named NC net
            >>> nc += mcu['UNUSED1'], mcu['UNUSED2']    # Mark pins as NC
            >>> 
            >>> # Named no-connect nets for documentation
            >>> analog_nc = NCNet('ANALOG_UNUSED')
            >>> debug_nc = NCNet('DEBUG_INTERFACE_NC')
            >>> 
            >>> # Create with initial connections
            >>> boot_nc = NCNet('BOOT_PINS', mcu['BOOT0'], mcu['BOOT1'])
            >>> 
            >>> # Different NC nets for different purposes
            >>> test_nc = NCNet('TEST_POINTS_NC')       # Test/debug pins
            >>> feature_nc = NCNet('UNUSED_FEATURES')   # Unimplemented features
            >>> reserved_nc = NCNet('RESERVED_PINS')    # Future expansion

        Automatic Properties:
            The NCNet constructor automatically sets appropriate properties:
            - Drive strength: Set to NOCONNECT to indicate no driving capability
            - ERC checking: Disabled to prevent floating pin warnings
            - Netlist generation: Configured to exclude from output netlists

        Pin Assignment:
            Pins connected to NCNet are marked as intentionally unconnected:
            - Removes pins from any existing nets they were connected to
            - Marks pins with no-connect status for ERC purposes
            - Documents design intent for unconnected pins

        Circuit Integration:
            NCNet objects are registered with their circuit like regular nets
            but are handled specially during ERC checking and netlist generation
            to reflect their special no-connect semantics.
        """
        from .pin import pin_drives

        super().__init__(name=name, circuit=circuit, *pins_nets_buses, **attribs)
        self._drive = pin_drives.NOCONNECT
        self.do_erc = False  # No need to do ERC on no-connect nets.

    def generate_netlist_net(self, tool=None):
        """
        Generate netlist representation for no-connect nets.
        
        No-connect nets intentionally do not appear in circuit netlists since
        they represent the explicit absence of electrical connections rather
        than actual circuit connections. This method always returns an empty
        string to exclude NCNet objects from netlist output.

        Args:
            tool (str, optional): The target netlist generation tool (e.g., 'kicad',
                'altium', 'eagle'). Parameter is accepted for compatibility but
                ignored since NC nets are excluded from all netlist formats.
                
        Returns:
            str: Always returns an empty string. No-connect nets do not generate
                netlist entries since they represent intentionally unconnected pins
                rather than actual electrical connections.

        Examples:
            >>> nc_net = NCNet('UNUSED_PINS')
            >>> nc_net += mcu['PA7'], mcu['PA8']
            >>> 
            >>> # NC nets don't appear in netlists
            >>> netlist_entry = nc_net.generate_netlist_net('kicad')
            >>> print(repr(netlist_entry))              # ''
            >>> 
            >>> # Compare with regular net
            >>> vcc_net = Net('VCC')
            >>> vcc_net += mcu['VCC']
            >>> vcc_entry = vcc_net.generate_netlist_net('kicad')
            >>> print(len(vcc_entry) > 0)               # True

        Tool Integration:
            Different PCB tools handle no-connect pins through special mechanisms:
            - Pin-level no-connect flags rather than net-level connections
            - Special symbols or annotations in schematic capture
            - ERC rule exclusions for intentionally unconnected pins
            - Design rule checking modifications for NC pins

        Design Verification:
            While NC nets don't appear in netlists, they can still be verified:
            - Pin assignment reports can show NC pin assignments
            - ERC reports can list pins marked as no-connect
            - Design review outputs can document intentional non-connections
            - BOM generation can identify unused pin functionality
        """
        return ""

    @property
    def drive(self):
        """
        Get the drive strength of this no-connect net.
        
        No-connect nets have a fixed drive strength of NOCONNECT that cannot
        be modified. This special drive value indicates that the net represents
        intentionally unconnected pins rather than an actual electrical signal.

        The NOCONNECT drive strength serves several purposes:
        - Identifies the net as representing non-connections
        - Excludes the net from drive conflict checking during ERC
        - Indicates to tools that this net should not appear in netlists
        - Documents design intent for unconnected pins

        Returns:
            int: Always returns pin_drives.NOCONNECT. This value cannot be
                changed for NCNet objects since it represents their fundamental
                characteristic as no-connect nets.

        Examples:
            >>> from skidl.pin import pin_drives
            >>> 
            >>> nc_net = NCNet('UNUSED_PINS')
            >>> print(nc_net.drive == pin_drives.NOCONNECT)  # True
            >>> 
            >>> # Compare with regular net drive
            >>> reg_net = Net('SIGNAL')
            >>> reg_net += driver_pin, receiver_pin
            >>> print(reg_net.drive != pin_drives.NOCONNECT)  # True
            >>> 
            >>> # Drive strength cannot be changed for NC nets
            >>> try:
            ...     nc_net.drive = pin_drives.STRONG   # This won't work
            ... except AttributeError:
            ...     print("NCNet drive cannot be modified")

        ERC Integration:
            The NOCONNECT drive strength integrates with electrical rule checking:
            - Pins on NCNet are excluded from floating pin detection
            - No drive conflict checking is performed for NC nets  
            - ERC reports can identify and verify no-connect assignments
            - Design verification can confirm intentional non-connections

        Immutability:
            The drive property for NCNet objects is read-only. Attempting to
            set or delete the drive strength will not work since the NOCONNECT
            drive is fundamental to the NCNet's purpose and behavior.

        Tool Compatibility:
            The NOCONNECT drive strength is recognized by netlist generators
            and ERC systems to provide appropriate handling of no-connect nets
            across different PCB design tools and workflows.
        """
        return self._drive
