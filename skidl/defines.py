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
Definitions used everywhere.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# Places where parts can be stored.
#   NETLIST: The part will become part of a circuit netlist.
#   LIBRARY: The part will be placed in the part list for a library.
#   TEMPLATE: The part will be used as a template to be copied from.
from future import standard_library
standard_library.install_aliases()
NETLIST, LIBRARY, TEMPLATE = ['NETLIST', 'LIBRARY', 'TEMPLATE']

# Prefixes for implicit nets and buses.
NET_PREFIX = 'N$'
BUS_PREFIX = 'B$'

# Supported ECAD tools.
ALL_TOOLS = KICAD, SKIDL = ['kicad', 'skidl']

# Utility for changing the net and bus prefixes.
def set_net_bus_prefixes(net, bus):
    global NET_PREFIX
    global BUS_PREFIX
    NET_PREFIX = net
    BUS_PREFIX = bus
