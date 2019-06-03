# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2019 by XESS Corp.
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
ERC functions for Circuit, Part, Pin, Net, Bus, Interface objects.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from builtins import str

from future import standard_library

from .utilities import erc_logger

standard_library.install_aliases()


def dflt_circuit_erc(circuit):
    """
    Do an electrical rules check on a circuit.
    """

    from .Net import Net

    # Check the nets for errors:
    #   1. Merge names to get a single name for all multi-segment nets.
    #   2. Find the set of unique net names.
    #   3. Get the net associated with each name and do an ERC on it.
    # This prevents flagging the same error multiple times by running
    # ERC on different segments of a multi-segment net.
    circuit._merge_net_names()
    net_names = set([net.name for net in circuit.nets])
    for name in net_names:
        Net.get(name, circuit=circuit).ERC()

    # Check the parts for errors.
    for part in circuit.parts:
        part.ERC()

    # Check interfaces for errors.
    for intfc in circuit.interfaces:
        intfc.ERC()

    if (erc_logger.error.count, erc_logger.warning.count) == (0, 0):
        sys.stderr.write("\nNo ERC errors or warnings found.\n\n")
    else:
        sys.stderr.write(
            "\n{} warnings found during ERC.\n".format(erc_logger.warning.count)
        )
        sys.stderr.write(
            "{} errors found during ERC.\n\n".format(erc_logger.error.count)
        )


def dflt_part_erc(part):
    """
    Do an electrical rules check on a part in the schematic.
    """

    from .Pin import Pin

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
            if pin.func != Pin.types.NOCONNECT:
                erc_logger.warning("Unconnected pin: {p}.".format(p=pin.erc_desc()))

        # Error if a no-connect pin is connected to a net.
        elif pin.net.drive != Pin.drives.NOCONNECT:
            if pin.func == Pin.types.NOCONNECT:
                erc_logger.warning(
                    "Incorrectly connected pin: {p} should not be connected to a net ({n}).".format(
                        p=pin.erc_desc(), n=pin.net.name
                    )
                )


def dflt_net_erc(net):
    """
    Do electrical rules check on a net in the schematic.
    """

    from .Pin import Pin

    net.test_validity()

    # Skip ERC check on this net if flag is cleared.
    if not net.do_erc:
        return

    # Check the number of pins attached to the net.
    pins = net.get_pins()
    num_pins = len(pins)
    if num_pins == 0:
        erc_logger.warning("No pins attached to net {n}.".format(n=net.name))
    elif num_pins == 1:
        erc_logger.warning(
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

    if net_drive <= Pin.drives.NONE:
        erc_logger.warning("No drivers for net {n}".format(n=net.name))
    for p in pins:
        if Pin.pin_info[p.func]["min_rcv"] > net_drive:
            erc_logger.warning(
                "Insufficient drive current on net {n} for pin {p}".format(
                    n=net.name, p=p.erc_desc()
                )
            )
