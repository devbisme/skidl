# -*- coding: utf-8 -*-
# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from .logger import active_logger
from .utilities import export_to_all, flatten

DEFAULT_PARTCLASS = 0

__all__ = ["DEFAULT_PARTCLASS"]


@export_to_all
class PartClass(object):
    def __init__(self, name, circuit=None, **attribs):

        # This object will belong to the default Circuit object or the one
        # that's passed as a parameter.
        circuit = attribs.pop("circuit", circuit or default_circuit)

        # Assign part class name.
        self.name = name

        # Assign default priority if not specified.
        if "priority" not in attribs:
            attribs["priority"] = DEFAULT_PARTCLASS

        # Assign the other attributes to this object.
        for k, v in list(attribs.items()):
            setattr(self, k, v)

        # Add part class to circuit. Duplicate part classes will be ignored.
        circuit.add_partclasses(self)

    def __eq__(self, prtcls):
        """
        Compare two PartClass objects for equality based on their attributes.

        Args:
            prtcls (PartClass): Another PartClass object to compare against.

        Returns:
            bool: True if both PartClass objects have identical attributes,
                False otherwise.
        """
        if not isinstance(prtcls, PartClass):
            return False
        
        # Compare all attributes of both objects
        return vars(self) == vars(prtcls)

    # Since an __eq__ method was defined, a __hash__ method is also needed
    # to maintain the hashability of PartClass objects.
    # This allows them to be used in sets or as dictionary keys.
    def __hash__(self):
        """Hash based on name (assuming name is immutable)."""
        return hash(self.name)


class PartClassList(list):

    def __init__(self, *partclasses, circuit=None):
        super().__init__()
        self.add(*partclasses, circuit=circuit)

    def __eq__(self, pt_cls_lst):
        return set(self) == set(pt_cls_lst)

    def add(self, *partclasses, circuit=None):
        for cls in flatten(partclasses):
            if cls is None:
                continue
            elif isinstance(cls, PartClassList):
                self.add(
                    *cls, circuit=circuit
                )  # Recursively add part classes from another PartClassList.
                continue
            elif isinstance(cls, PartClass):
                pass
            elif isinstance(cls, str):
                # The name of a part class was passed, so look it up in the circuit.
                circuit = circuit or default_circuit
                cls = circuit.partclasses[cls]
            else:
                active_logger.raise_(
                    TypeError,
                    f"Expected PartClassList, PartClass or string, got {type(cls)}",
                )
            # Add the partclass to the list if it's not already present.
            if cls not in self:
                self.append(cls)

    def by_priority(self):
        return [pc.name for pc in sorted(self, key=lambda pc: pc.priority)]
