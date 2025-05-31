# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Class for PCBNEW net classes.

This module provides the NetClass class for defining net classes in PCB designs.
Net classes allow the designer to specify common properties (such as trace width,
clearance, etc.) for groups of nets.
"""

from .logger import active_logger
from .utilities import export_to_all



@export_to_all
class NetClass(object):
    """
    Defines a group of nets that share common physical properties.
    
    Net classes allow setting common PCB properties like trace width, clearance,
    and via dimensions for groups of related nets.
    
    Attributes:
        name (str): Name of the net class
        Various other attributes depending on what's passed in the constructor
    """
    
    def __init__(self, name, **attribs):
        """
        Create a new net class with a name and optional attributes.
        
        Args:
            name (str): Name of the net class
            **attribs: Additional attributes for the net class, such as:
                       - trace_width: Width of PCB traces for nets in this class
                       - clearance: Minimum clearance between nets in this class and other objects
                       - via_dia: Via diameter for nets in this class
                       - via_drill: Via drill diameter for nets in this class
                       - uvia_dia: Microvias diameter
                       - uvia_drill: Microvias drill diameter
                       - diff_pair_width: Width of differential pair traces
                       - diff_pair_gap: Gap between differential pair traces
                       - circuit: Circuit object this net class belongs to
                       
        Raises:
            Warning: If a net class with the same name already exists in the circuit
            
        Examples:
            power_nets = NetClass('Power', 
                                 trace_width=0.5, 
                                 clearance=0.2, 
                                 via_dia=0.8, 
                                 via_drill=0.4)
        """
        # This object will belong to the default Circuit object or the one
        # that's passed as a parameter.
        circuit = attribs.pop("circuit", default_circuit)

        # Assign net class name.
        self.name = name

        # Assign the other attributes to this object.
        for k, v in list(attribs.items()):
            setattr(self, k, v)

        # Is this net class already defined?
        if circuit.netclasses.get(name) is not None:
            active_logger.warning(
                "Cannot redefine existing net class {name}!".format(**locals())
            )
        else:
            circuit.netclasses[name] = self
