# MIT license
# 
# Copyright (C) 2016 by XESS Corporation.
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
Convert a netlist into an equivalent SKiDL program.
"""


from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import int
from future import standard_library
standard_library.install_aliases()

import re

from .parse_netlist import *


def netlist_to_skidl(netlist_src):

    tab = ' ' * 4

    def legalize(name):
        return re.sub('[^a-zA-Z0-9_]','_',name)

    def comp_to_skidl(comp):
        ltab = tab
        ref = comp.ref.val
        legal_ref = legalize(ref)
        value = comp.value.val
        lib = comp.libsource.lib.val
        part = comp.libsource.part.val
        comp_skidl = "{ltab}{legal_ref} = Part('{lib}', '{part}', ref='{ref}', value='{value}')\n".format(**locals())
        try:
            footprint = comp.footprint.val
            comp_skidl += "{ltab}setattr({legal_ref}, 'footprint', '{footprint}')\n".format(**locals())
        except AttributeError:
            pass
        for fld in comp.fields:
            comp_skidl += "{ltab}setattr({legal_ref}, '{fld.name.val}', '{fld.text}')\n".format(**locals())
        return comp_skidl

    def net_to_skidl(net):
        ltab = tab
        name = net.name.val
        code = int(net.code.val)
        net_skidl = "{ltab}net__{code} = Net('{name}')\n".format(**locals())
        net_skidl += "{ltab}net__{code} += ".format(**locals())
        for n in net.nodes:
            legal_ref = legalize(n.ref.val)
            net_skidl += "{legal_ref}['{n.pin.val}'],".format(**locals())
        return net_skidl[:-1] + '\n' # Strip off the last ','.

    def _netlist_to_skidl(ntlst):
        ltab = tab
        skidl = ''
        skidl += '# -*- coding: utf-8 -*-\n\n'
        skidl += 'from skidl import *\n\n\n'
        circuit_name = legalize(ntlst.design.source.val)
        skidl += 'def {circuit_name}():\n\n'.format(**locals())

        for comp in ntlst.components:
            skidl += comp_to_skidl(comp) + '\n'

        for net in ntlst.nets:
            skidl += net_to_skidl(net) + '\n'

        skidl += '\nif __name__ == "__main__":\n\n'
        skidl += '{ltab}{circuit_name}()\n'.format(**locals())
        skidl += '{ltab}generate_netlist()\n'.format(**locals())

        return skidl

    return _netlist_to_skidl(parse_netlist(netlist_src))
