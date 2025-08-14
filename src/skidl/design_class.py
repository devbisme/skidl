# -*- coding: utf-8 -*-
# The MIT License (MIT) - Copyright (c) Dave Vandenbout.


from .logger import active_logger
from .utilities import export_to_all, flatten

DEFAULT_PRIORITY = 0  # Lowest possible priority.

__all__ = ["DEFAULT_PRIORITY"]


class DesignClass:

    def __init__(self, name, **attribs):

        # Assign part class name.
        self.name = name

        # Assign default priority if not specified.
        if "priority" not in attribs:
            attribs["priority"] = DEFAULT_PRIORITY

        # Assign the other attributes to this object.
        for k, v in list(attribs.items()):
            setattr(self, k, v)

    def __eq__(self, prtcls):
        if not isinstance(prtcls, DesignClass):
            return False
        
        # Compare all attributes of both objects
        return vars(self) == vars(prtcls)

    def __hash__(self):
        return hash(self.name)

@export_to_all
class PartClass(DesignClass):

    def __init__(self, name, circuit=None, **attribs):
        super().__init__(name, **attribs)

        # This object will belong to the default Circuit object or the one
        # that's passed as a parameter.
        circuit = circuit or default_circuit
        circuit.partclasses = self

@export_to_all
class NetClass(DesignClass):

    def __init__(self, name, circuit=None, **attribs):
        super().__init__(name, **attribs)

        # This object will belong to the default Circuit object or the one
        # that's passed as a parameter.
        circuit = circuit or default_circuit
        circuit.netclasses = self

class DesignClasses(dict):

    def __init__(self, *classes, circuit=None, classes_name=None):
        super().__init__()
        self.classes_name = classes_name
        self.add(classes, circuit=circuit)

    def __eq__(self, cls_lst):
        if isinstance(cls_lst, type(self)):
            return vars(self) == vars(cls_lst)
        return False

    def __contains__(self, cls):
        if isinstance(cls, str):
            return cls in self.keys()
        return cls in self.values()

    def __getitem__(self, *names):
        names = flatten(names)
        if len(names) == 1:
            try:
                return super().__getitem__(names[0])
            except KeyError:
                active_logger.raise_(
                    KeyError, f"No {type(self)} with name '{names[0]}' found"
                )
        else:
            return [self[name] for name in names if name in self]

    def add(self, *classes, circuit=None):
        for cls in classes:
            if cls is None:
                continue
            elif isinstance(cls, DesignClasses):
                self.add(*cls.values(), circuit=circuit)  # Recursively add classes from another DesignClasses object.
                continue
            elif isinstance(cls, (list, tuple)):
                self.add(*cls, circuit=circuit)  # Recursively add classes from a list or tuple.
                continue
            elif isinstance(cls, DesignClass):
                if cls in self:
                    continue
                if cls.name in self.keys():
                    # A NetClass with the same name exists but the attributes differ.
                    active_logger.raise_(
                        ValueError, f"Cannot add {type(cls)} '{cls.name}' with differing attributes"
                    )
                pass
            elif isinstance(cls, str):
                # The name of a class was passed, so look it up in the circuit.
                circuit = circuit or default_circuit
                cls = getattr(circuit, self.classes_name)[cls]
            else:
                active_logger.raise_(
                    TypeError,
                    f"Can't add {type(cls)} to {type(self)}",
                )
            # Add the partclass to the list if it's not already present.
            if cls not in self:
                self[cls.name] = cls

    def by_priority(self):
        return [pc.name for pc in sorted(self.values(), key=lambda pc: pc.priority)]
    
class PartClasses(DesignClasses):
    def __init__(self, *classes, circuit=None):
        super().__init__(*classes, circuit=circuit, classes_name="partclasses")

class NetClasses(DesignClasses):
    def __init__(self, *classes, circuit=None):
        super().__init__(*classes, circuit=circuit, classes_name="netclasses")
