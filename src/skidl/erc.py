# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Electrical Rule Checking (ERC) in SKiDL.

This module provides functions for verifying the electrical correctness of SKiDL circuits.
It includes default ERC functions for circuits, parts, pins, and nets that check for 
common issues such as unconnected pins, pin conflicts, and insufficient drive strength.
These functions can be customized or extended to implement domain-specific design rules.
"""

from .logger import active_logger
from .utilities import export_to_all


@export_to_all
def dflt_circuit_erc(circuit):
    """
    Perform electrical rules check on an entire circuit.
    
    This function checks all nets, parts, and interfaces in the circuit
    for electrical rule violations. It first merges multi-segment nets, then
    runs ERC checks on each unique net once to prevent duplicate error messages.
    
    Args:
        circuit (Circuit): The circuit to check for rule violations.
    """

    from .net import Net

    # Check the nets for errors:
    #   1. Merge all multi-segment nets.
    #   2. Find the set of unique net names.
    #   3. Get the net associated with each name and do an ERC on it.
    # This prevents flagging the same error multiple times by running
    # ERC on different segments of a multi-segment net.
    circuit.merge_net_names()
    net_names = set([net.name for net in circuit.nets])
    for name in net_names:
        Net.get(name, circuit=circuit).ERC()

    # Check parts & interfaces for errors:
    for piece in circuit.parts + circuit.interfaces:
        piece.ERC()


@export_to_all
def dflt_part_erc(part):
    """
    Perform electrical rules check on a specific part.
    
    This function checks each pin of the part for rule violations such as
    unconnected pins that should be connected or connected pins that should
    not be connected (NOCONNECT).
    
    Args:
        part (Part): The part to check for rule violations.
    """

    from .pin import Pin, pin_types, pin_drives

    # Don't check this part if the flag is not true.
    if not part.do_erc:
        return

    # Check each pin of the part.
    for pin in part.pins:

        # Skip this pin if the flag is false.
        if not pin.do_erc:
            continue

        # Error if a pin is unconnected but not of type NOCONNECT.
        if pin.net is None:
            if pin.func != pin_types.NOCONNECT:
                active_logger.warning("Unconnected pin: {p}.".format(p=pin.erc_desc()))

        # Error if a no-connect pin is connected to a net.
        elif pin.net.drive != pin_drives.NOCONNECT:
            if pin.func == pin_types.NOCONNECT:
                active_logger.warning(
                    "Incorrectly connected pin: {p} should not be connected to a net ({n}).".format(
                        p=pin.erc_desc(), n=pin.net.name
                    )
                )


@export_to_all
def dflt_net_erc(net):
    """
    Perform electrical rules check on a specific net.
    
    This function verifies that the net has pins connected to it, checks for
    pin conflicts between connected pins, and ensures the net has sufficient
    drive strength for all pins that require it.
    
    Args:
        net (Net): The net to check for rule violations.
    """

    from .pin import pin_drives, pin_info

    net.test_validity()

    # Skip ERC check on this net if flag is cleared.
    if not net.do_erc:
        return

    # Check the number of pins attached to the net.
    pins = net.pins
    num_pins = len(pins)
    if num_pins == 0:
        active_logger.warning("No pins attached to net {n}.".format(n=net.name))
    elif num_pins == 1:
        active_logger.warning(
            "Only one pin ({p}) attached to net {n}.".format(
                p=pins[0].erc_desc(), n=net.name
            )
        )
    else:
        # Multiple pins on the net, so check for conflicts.
        for i in range(num_pins):
            for j in range(i + 1, num_pins):
                pins[i].chk_conflict(pins[j])

    # Check to see if the net has sufficient drive.

    # Find the maximum signal driver on this net. The net might have also
    # been assigned a drive, so include that.
    net_drive = max([p.drive for p in pins] + [net.drive])

    if net_drive <= pin_drives.NONE:
        active_logger.warning("No drivers for net {n}".format(n=net.name))
    for p in pins:
        if pin_info[p.func]["min_rcv"] > net_drive:
            active_logger.warning(
                "Insufficient drive current on net {n} for pin {p}".format(
                    n=net.name, p=p.erc_desc()
                )
            )
