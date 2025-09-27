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

    # def __init__(self):
    #     """
    #     Mixin class to add pin-related methods to a class.
    #     """
    #     pass
    #     # self.pins = []  # List of pins in the part.
    #     # self.match_pin_regex = False  # Allow regex matching of pin names/aliases.

    def __iadd__(self, *pins):
        """
        Add one or more pins to a part and return the part.
        
        Args:
            *pins: Pin objects to add to the part.
            
        Returns:
            Part: The part with added pins.
        """
        return self.add_pins(*pins)
    

    # Get pins from a part using brackets, e.g. [1,5:9,'A[0-9]+'].
    def __getitem__(self, *pin_ids, **criteria):
        """
        Return list of part pins selected by pin numbers or names.

        Args:
            pin_ids: A list of strings containing pin names, numbers,
                regular expressions, slices, lists or tuples. If empty,
                then it will select all pins.

        Keyword Args:
            criteria: Key/value pairs that specify attribute values the
                pins must have in order to be selected.

        Returns:
            Pin or list: A list of pins matching the given IDs and satisfying all the criteria,
                or just a single Pin object if only a single match was found.
                Or None if no match was found.

        Notes:
            Pins can be selected from a part by using brackets like so::

                atmega = Part('atmel', 'ATMEGA16U2')
                net = Net()
                atmega[1] += net  # Connects pin 1 of chip to the net.
                net += atmega['RESET']  # Connects reset pin to the net.
        """
        return self.get_pins(*pin_ids, **criteria)

    def __setitem__(self, ids, pins_nets_buses):
        """
        You can't assign to the pins of parts. You must use the += operator.

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
            ids: Pin IDs being assigned to
            pins_nets_buses: Object being assigned to the pins
            
        Raises:
            TypeError: If direct assignment is attempted
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
        Normal attribute wasn't found, so check pin aliases.
        
        Args:
            attr (str): Attribute name to look for
            
        Returns:
            Pin or NetPinList: The pin(s) with matching alias
            
        Raises:
            AttributeError: If no pin aliases match and the attribute doesn't exist
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
        Return an iterator for stepping thru individual pins of the part.
        
        Returns:
            iterator: Iterator providing access to the part's pins.
        """

        # Get the list pf pins for this part using the getattribute for the
        # basest object to prevent infinite recursion within the __getattr__ method.
        # Don't use super() because it leads to long runtimes under Python 2.7.
        self_pins = object.__getattribute__(self, "pins")

        return (p for p in self_pins)  # Return generator expr.

    def associate_pins(self):
        """
        Make sure all the pins in a part have valid references to the part.
        
        This updates each pin's part attribute to point to this part object.
        """
        for p in self:
            p.part = self

    def add_pins(self, *pins):
        """
        Add one or more pins to a part and return the part.
        
        Args:
            *pins: Pin objects to add to the part.
            
        Returns:
            Part: The part with pins added.
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
        Remove one or more pins from a part.
        
        Args:
            *pin_ids: IDs (names or numbers) of pins to remove.
        """
        for i, pin in enumerate(self):
            if pin.num in pin_ids or pin.name in pin_ids:
                del pins[i]

    def swap_pins(self, pin_id1, pin_id2):
        """
        Swap pin name/number between two pins of a part.
        
        Args:
            pin_id1: ID of first pin (name or number)
            pin_id2: ID of second pin (name or number)
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
        Assign a new name to a pin of a part.
        
        Args:
            pin_id: ID of pin to rename (name or number)
            new_pin_name (str): New name for the pin
        """
        for pin in self:
            if pin_id in (pin.num, pin.name):
                pin.name = new_pin_name
                return

    def renumber_pin(self, pin_id, new_pin_num):
        """
        Assign a new number to a pin of a part.
        
        Args:
            pin_id: ID of pin to renumber (name or number)
            new_pin_num: New number for the pin
        """
        for pin in self:
            if pin_id in (pin.num, pin.name):
                pin.num = new_pin_num
                return

    def get_pins(self, *pin_ids, **criteria):
        """
        Return list of part pins selected by pin numbers or names.

        Args:
            pin_ids: A list of strings containing pin names, numbers,
                regular expressions, slices, lists or tuples. If empty,
                then it will select all pins.

        Keyword Args:
            criteria: Key/value pairs that specify attribute values the
                pins must have in order to be selected.
            silent (bool, optional): If True, don't issue error messages. Defaults to False.
            only_search_numbers (bool, optional): Only search for pins by number. Defaults to False.
            only_search_names (bool, optional): Only search for pins by name. Defaults to False.
            match_regex (bool, optional): Allow regex pattern matching for pin names. Defaults to False.

        Returns:
            Pin or list: A list of pins matching the given IDs and satisfying all the criteria,
                or just a single Pin object if only a single match was found.
                Or None if no match was found and silent=True.
                
        Raises:
            ValueError: If pins can't be found and silent=False.
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
        Disconnect all the part's pins from nets.
        
        This removes all connections to the part's pins.
        """
        for pin in self:
            pin.disconnect()

    def split_pin_names(self, delimiters):
        """
        Use chars in delimiters to split pin names and add as aliases to each pin.
        
        Args:
            delimiters (str): String of characters to use as delimiters for splitting pin names.
        """
        if delimiters:
            for pin in self:
                # Split pin name and add subnames as aliases to the pin.
                pin.split_name(delimiters)

    def _find_min_max_pins(self):
        """
        Return the minimum and maximum pin numbers for the part.
        
        Returns:
            tuple: A tuple containing (min_pin_num, max_pin_num)
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
        Return the pins of the part in a sorted order.
        
        Returns:
            list: Sorted list of the part's pins.
        """
        return sorted(self)

