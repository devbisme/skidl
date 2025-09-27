"""
Mixin classes for SKiDL objects.

This module provides mixin classes that add specific functionality to SKiDL objects.
The mixins are designed to be combined with base classes to provide additional
capabilities without requiring deep inheritance hierarchies.

Classes:
    PinMixin: Adds pin management functionality to parts and other objects.
"""

from .logger import active_logger
from .pin import Pin
from .skidlbaseobj import SkidlBaseObject
from .utilities import (
    expand_indices,
    filter_list,
    flatten,
    from_iadd,
    list_or_scalar,
    rmv_iadd,
    Rgx,
)

class PinMixin():
    """
    Mixin class that adds pin-related methods and functionality to a class.
    
    This mixin provides comprehensive pin management capabilities including:
    - Adding, removing, and manipulating pins
    - Pin selection using various criteria (names, numbers, regex patterns)
    - Pin connection and disconnection operations
    - Pin aliasing and naming utilities
    
    The mixin maintains a list of pins and provides multiple ways to access them,
    including bracket notation, attribute access, and iteration.
    
    Attributes:
        pins (list): List of Pin objects belonging to the part.
        _match_pin_regex (bool): Enable/disable regex matching for pin names and aliases.
    
    Examples:
        >>> class MyPart(PinMixin):
        ...     def __init__(self):
        ...         super().__init__()
        ...         # Add pins to the part
        ...         self.add_pins(Pin(num=1, name='VCC'), Pin(num=2, name='GND'))
        ...
        >>> part = MyPart()
        >>> vcc_pin = part[1]  # Get pin by number
        >>> gnd_pin = part['GND']  # Get pin by name
    """

    def __init__(self):
        """
        Initialize the PinMixin.
        
        Sets up the pin list and configures default settings for pin matching.
        """
        self.pins = []  # List of pins in the part.
        self._match_pin_regex = False  # Disable regex matching of pin names/aliases by default.

    def __iadd__(self, *pins):
        """
        Add one or more pins to the part using the += operator.
        
        This method allows pins to be added using the += operator syntax,
        which is more intuitive than calling add_pins() directly.
        
        Args:
            *pins: Variable number of Pin objects to add to the part.
            
        Returns:
            Self: The part object with added pins, allowing for method chaining.
            
        Examples:
            >>> part += Pin(num=1, name='VCC')
            >>> part += [Pin(num=2, name='GND'), Pin(num=3, name='DATA')]
        """
        return self.add_pins(*pins)
    

    # Get pins from a part using brackets, e.g. [1,5:9,'A[0-9]+'].
    def __getitem__(self, *pin_ids, **criteria):
        """
        Return pins selected by pin numbers, names, or other criteria.

        This method enables bracket notation for pin selection, supporting
        various selection methods including exact matches, regex patterns,
        and attribute-based filtering.

        Args:
            *pin_ids: Pin identifiers which can be:
                - integers or strings for pin numbers
                - strings for pin names
                - regex patterns (if regex matching is enabled)
                - slices for ranges of pins
                - lists or tuples of any of the above
                If empty, selects all pins.

        Keyword Args:
            criteria: Key/value pairs specifying pin attributes that must match.
                Common criteria include 'func' for pin function, 'unit' for
                unit number, etc.

        Returns:
            Pin, NetPinList, or None: 
                - Single Pin if exactly one match found
                - NetPinList if multiple matches found  
                - None if no matches found

        Examples:
            >>> pin1 = part[1]  # Get pin by number
            >>> reset_pin = part['RESET']  # Get pin by name
            >>> power_pins = part['VCC', 'VDD', 'GND']  # Multiple pins
            >>> analog_pins = part[func='analog']  # Pins with specific function
        """
        return self.get_pins(*pin_ids, **criteria)

    def __setitem__(self, ids, pins_nets_buses):
        """
        Prevent direct assignment to pins while allowing += operator.

        This method is a work-around that allows the use of the += for making
        connections to pins while prohibiting direct assignment. Python
        processes something like my_part['GND'] += gnd as follows::

            1. Part.__getitem__ is called with 'GND' as the index. This
               returns a single Pin or a NetPinList.
            2. The Pin.__iadd__ or NetPinList.__iadd__ method is passed
               the thing to connect to the pin (gnd in this case). This method
               makes the actual connection to the part pin or pins. Then it
               creates an iadd_flag attribute in the object it returns.
            3. Finally, Part.__setitem__ is called. If the iadd_flag attribute
               is true in the passed argument, then __setitem__ was entered
               as part of processing the += operator. If there is no
               iadd_flag attribute, then __setitem__ was entered as a result
               of using a direct assignment, which is not allowed.
               
        Args:
            ids: Pin identifiers being assigned to.
            pins_nets_buses: Object being assigned to the pins.
            
        Raises:
            TypeError: If direct assignment is attempted (no iadd_flag present).
            
        Note:
            This is part of Python's mechanism for handling augmented assignment
            operators. The += operator first calls __getitem__, then __iadd__
            on the returned object, then __setitem__ with the result.
        """

        # If the iadd_flag is set, then it's OK that we got
        # here and don't issue an error. Also, delete the flag.
        if from_iadd(pins_nets_buses):
            rmv_iadd(pins_nets_buses)
            return

        # No iadd_flag or it wasn't set. This means a direct assignment
        # was made to the pin, which is not allowed.
        active_logger.raise_(TypeError, "Can't assign to a part! Use the += operator.")

    def __getattr__(self, attr):
        """
        Enable attribute-style access to pins using their aliases.
        
        When a normal attribute lookup fails, this method searches for pins
        that have the requested attribute name as an alias. This allows
        pins to be accessed as attributes of the part.
        
        Args:
            attr (str): The attribute name being requested.
            
        Returns:
            Pin or NetPinList: 
                - Single Pin if exactly one pin has this alias
                - NetPinList if multiple pins have this alias
            
        Raises:
            AttributeError: If no pins have the requested alias and the
                attribute doesn't exist in the base class.
                
        Examples:
            >>> part.RESET  # Access pin with 'RESET' alias
            >>> part.p1     # Access pin 1 using 'p1' alias
        """
        from skidl.netpinlist import NetPinList

        # Look for the attribute name in the list of pin aliases.
        pins = [pin for pin in self if pin.aliases == attr]

        if pins:
            if len(pins) == 1:
                # Return a single pin if only one alias match was found.
                return pins[0]
            else:
                # Return list of pins if multiple matches were found.
                # Return a NetPinList instead of a vanilla list so += operator works!
                return NetPinList(pins)

        # No pin aliases matched, so use the __getattr__ for the subclass.
        # Don't use super(). It leads to long runtimes under Python 2.7.
        return SkidlBaseObject.__getattr__(self, attr)

    def __iter__(self):
        """
        Enable iteration over the part's pins.
        
        This method makes the part object iterable, allowing direct iteration
        over its pins using for loops and other iteration constructs.
        
        Returns:
            generator: Generator expression yielding Pin objects.
            
        Examples:
            >>> for pin in part:
            ...     print(f"Pin {pin.num}: {pin.name}")
            >>> pin_names = [pin.name for pin in part]
        """

        # Get the list pf pins for this part using the getattribute for the
        # basest object to prevent infinite recursion within the __getattr__ method.
        # Don't use super() because it leads to long runtimes under Python 2.7.
        self_pins = object.__getattribute__(self, "pins")

        return (p for p in self_pins)  # Return generator expr.

    def associate_pins(self):
        """
        Ensure all pins have proper back-references to this part.
        
        This method updates each pin's 'part' attribute to point back to
        this part object, maintaining bidirectional relationships between
        parts and their pins. This is typically called after pins are
        added or when the part structure is modified.
        """
        for p in self:
            p.part = self

    def add_pins(self, *pins):
        """
        Add one or more pins to the part.
        
        This method adds pins to the part and sets up proper relationships
        and aliases. Each pin gets a back-reference to the part, and 
        automatic aliases are created for pin names and numbers.
        
        Args:
            *pins: Variable number of Pin objects or iterables of Pin objects
                to add to the part.
            
        Returns:
            Self: The part object with pins added, enabling method chaining.
            
        Note:
            Automatic aliases are created:
            - Pin name becomes an alias
            - "p" + pin number becomes an alias (e.g., "p1" for pin 1)
            
        Examples:
            >>> part.add_pins(Pin(num=1, name='VCC'))
            >>> part.add_pins([Pin(num=2, name='GND'), Pin(num=3, name='DATA')])
        """
        for pin in flatten(pins):
            pin.part = self
            self.pins.append(pin)
            # Create attributes so pin can be accessed by name or number such
            # as part.ENBL or part.p5.
            pin.aliases += pin.name
            pin.aliases += "p" + str(pin.num)
        return self

    def rmv_pins(self, *pin_ids):
        """
        Remove one or more pins from the part.
        
        Removes pins that match the given identifiers (names or numbers).
        The pins are permanently removed from the part's pin list.
        
        Args:
            *pin_ids: Pin identifiers (names or numbers) of pins to remove.
            
        Examples:
            >>> part.rmv_pins(1, 'RESET')  # Remove pin 1 and RESET pin
            >>> part.rmv_pins('VCC', 'GND')  # Remove power pins
        """
        for i, pin in enumerate(self):
            if pin.num in pin_ids or pin.name in pin_ids:
                del pins[i]

    def swap_pins(self, pin_id1, pin_id2):
        """
        Swap the names and numbers between two pins.
        
        This method exchanges the name and number attributes between two pins,
        effectively swapping their identities while maintaining their physical
        connections and other properties.
        
        Args:
            pin_id1: Identifier (name or number) of the first pin.
            pin_id2: Identifier (name or number) of the second pin.
            
        Examples:
            >>> part.swap_pins(1, 2)  # Swap pins 1 and 2
            >>> part.swap_pins('RESET', 'ENABLE')  # Swap named pins
        """
        i1, i2 = None, None
        for i, pin in enumerate(self):
            pin_num_name = (pin.num, pin.name)
            if pin_id1 in pin_num_name:
                i1 = i
            elif pin_id2 in pin_num_name:
                i2 = i
            if i1 and i2:
                break
        if i1 and i2:
            pins[i1].num, pins[i1].name, pins[i2].num, pins[i2].name = (
                pins[i2].num,
                pins[i2].name,
                pins[i1].num,
                pins[i1].name,
            )

    def rename_pin(self, pin_id, new_pin_name):
        """
        Change the name of a pin.
        
        Finds the pin matching the given identifier and updates its name
        to the new value.
        
        Args:
            pin_id: Current identifier (name or number) of the pin to rename.
            new_pin_name (str): New name to assign to the pin.
            
        Examples:
            >>> part.rename_pin(1, 'POWER')  # Rename pin 1 to 'POWER'
            >>> part.rename_pin('RESET', 'RST')  # Rename RESET pin to RST
        """
        for pin in self:
            if pin_id in (pin.num, pin.name):
                pin.name = new_pin_name
                return

    def renumber_pin(self, pin_id, new_pin_num):
        """
        Change the number of a pin.
        
        Finds the pin matching the given identifier and updates its number
        to the new value.
        
        Args:
            pin_id: Current identifier (name or number) of the pin to renumber.
            new_pin_num: New number to assign to the pin.
            
        Examples:
            >>> part.renumber_pin('RESET', 100)  # Change RESET pin to number 100
            >>> part.renumber_pin(1, 5)  # Change pin 1 to pin 5
        """
        for pin in self:
            if pin_id in (pin.num, pin.name):
                pin.num = new_pin_num
                return

    def get_pins(self, *pin_ids, **criteria):
        """
        Get pins matching specified identifiers and criteria.

        This is the core pin selection method that supports multiple selection
        modes including exact matching, regex patterns, and attribute-based
        filtering. It provides flexible pin selection capabilities for various
        use cases.

        Args:
            *pin_ids: Pin identifiers for selection:
                - Integers or strings for exact pin number matches
                - Strings for exact pin name/alias matches  
                - Regex patterns (when regex matching enabled)
                - Slices for pin number ranges
                - Lists/tuples of any combination above
                If empty, selects all pins.

        Keyword Args:
            criteria: Attribute-based filtering criteria as key=value pairs.
            silent (bool, optional): Suppress error messages if True. Defaults to False.
            only_search_numbers (bool, optional): Restrict search to pin numbers only. 
                Defaults to False.
            only_search_names (bool, optional): Restrict search to pin names/aliases only.
                Defaults to False.
            match_regex (bool, optional): Enable regex pattern matching for names.
                Defaults to False, or uses part's match_pin_regex setting.

        Returns:
            Pin, list, or None:
                - Single Pin object if exactly one match found
                - List of Pin objects if multiple matches found
                - None if no matches found and silent=True
                
        Raises:
            ValueError: If no pins found and silent=False.
            
        Examples:
            >>> pins = part.get_pins(1, 2, 3)  # Get pins 1, 2, 3
            >>> analog_pins = part.get_pins(func='analog')  # Pins with analog function
            >>> power_pins = part.get_pins('VCC', 'VDD', 'GND')  # Named pins
            >>> pattern_pins = part.get_pins('A[0-9]+', match_regex=True)  # Regex
        """

        from .alias import Alias
        from .netpinlist import NetPinList

        # Extract option for suppressing error messages.
        silent = criteria.pop("silent", False)

        # Extract restrictions on searching for only pin names or numbers.
        only_search_numbers = criteria.pop("only_search_numbers", False)
        only_search_names = criteria.pop("only_search_names", False)

        # Extract permission to search for regex matches in pin names/aliases.
        match_regex = criteria.pop("match_regex", False) or self.match_pin_regex

        # If no pin identifiers were given, then use a wildcard that will
        # select all pins.
        if not pin_ids:
            pin_ids = [Rgx(".*")]

        # Determine the minimum and maximum pin ids if they don't already exist.
        if "min_pin" not in dir(self) or "max_pin" not in dir(self):
            self.min_pin, self.max_pin = self._find_min_max_pins()

        # Go through the list of pin IDs one-by-one.
        pins = NetPinList()
        for p_id in expand_indices(self.min_pin, self.max_pin, match_regex, *pin_ids):

            # If only names are being searched, the search of pin numbers is skipped.
            if not only_search_names:
                # Does pin ID (either integer or string) match a pin number...
                tmp_pins = filter_list(
                    self.pins, num=str(p_id), do_str_match=True, **criteria
                )
                if tmp_pins:
                    pins.extend(tmp_pins)
                    continue

            # if only numbers are being searched, then search of pin names is skipped.
            if not only_search_numbers:
                # OK, assume it's not a pin number but a pin name or alias.
                # Look for an exact match.

                # Check pin aliases for an exact match.
                tmp_pins = filter_list(
                    self.pins, aliases=p_id, do_str_match=True, **criteria
                )
                if tmp_pins:
                    pins.extend(tmp_pins)
                    continue

                # Check pin names for an exact match.
                tmp_pins = filter_list(
                    self.pins, name=p_id, do_str_match=True, **criteria
                )
                if tmp_pins:
                    pins.extend(tmp_pins)
                    continue

                # Skip regex matching if not enabled.
                if not match_regex:
                    continue

                # OK, pin ID is not a pin number and doesn't exactly match a pin
                # name or alias. Does it match as a regex?
                p_id_re = p_id

                # Check pin aliases for a regex match.
                tmp_pins = filter_list(self.pins, aliases=Alias(p_id_re), **criteria)
                if tmp_pins:
                    pins.extend(tmp_pins)
                    continue

                # Check the pin names for a regex match.
                tmp_pins = filter_list(self.pins, name=p_id_re, **criteria)
                if tmp_pins:
                    pins.extend(tmp_pins)
                    continue

        # Log an error if no pins were selected using the pin ids.
        if not pins and not silent:
            active_logger.error(
                f"No pins found using {self.name}:{self.ref}[{pin_ids}]"
            )

        return list_or_scalar(pins)

    def disconnect(self):
        """
        Disconnect all pins from their connected nets.
        
        This method breaks all electrical connections to the part by
        disconnecting each pin from any nets it may be connected to.
        The part becomes electrically isolated after this operation.
        
        Examples:
            >>> part.disconnect()  # Disconnect all pins from nets
        """
        for pin in self:
            pin.disconnect()

    def split_pin_names(self, delimiters):
        """
        Split pin names using delimiters and add subnames as aliases.
        
        This method takes pin names that contain delimiter characters and
        splits them into component parts, adding each part as an alias
        to the pin. This enables more flexible pin access patterns.
        
        Args:
            delimiters (str): String containing characters to use as delimiters
                for splitting pin names.
                
        Examples:
            >>> part.split_pin_names('_-/')  # Split on underscore, dash, slash
            >>> # Pin named "DATA_IN" would get aliases "DATA" and "IN"
        """
        if delimiters:
            for pin in self:
                # Split pin name and add subnames as aliases to the pin.
                pin.split_name(delimiters)

    def _find_min_max_pins(self):
        """
        Find the minimum and maximum numeric pin numbers.
        
        This internal method scans all pins to find the lowest and highest
        numbered pins (considering only pins with integer numbers). These
        values are used for pin range operations and indexing.
        
        Returns:
            tuple: A tuple of (min_pin_number, max_pin_number) as integers.
                Returns (0, 0) if no numeric pins are found.
        """
        pin_nums = []
        try:
            for p in self:
                try:
                    pin_nums.append(int(p.num))
                except ValueError:
                    pass
        except AttributeError:
            # This happens if the part has no pins.
            pass
        try:
            return min(pin_nums), max(pin_nums)
        except ValueError:
            # This happens if the part has no integer-labeled pins.
            return 0, 0

    @property
    def ordered_pins(self):
        """
        Get the pins sorted in a consistent order.
        
        Returns the part's pins in sorted order, typically by pin number
        where possible, falling back to name-based sorting for non-numeric pins.
        
        Returns:
            list: Sorted list of the part's Pin objects.
            
        Examples:
            >>> sorted_pins = part.ordered_pins
            >>> for pin in part.ordered_pins:
            ...     print(f"Pin {pin.num}: {pin.name}")
        """
        return sorted(self)

