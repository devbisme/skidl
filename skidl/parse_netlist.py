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
Parsers for netlist files of various formats (only KiCad, at present).
"""


from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()

from pyparsing import *

from .py_2_3 import *

THIS_MODULE = locals()

def _parse_netlist_kicad(text):
    """
    Return a pyparsing object storing the contents of a KiCad netlist.
    """

    def _paren_clause(keyword, value):
        """
        Create a parser for a parenthesized list with an initial keyword.
        """
        lp = Literal('(').suppress()
        rp = Literal(')').suppress()
        return (lp + Keyword(keyword, caseless=True).suppress() + value('val') + rp
                )(keyword)

    #++++++++++++++++++++++++++++ Parser Definition +++++++++++++++++++++++++++

    # Basic elements.
    word = Word(alphas)
    inum = Word(nums)
    fnum = Word(nums) + Optional(Literal('.') + Optional(Word(nums)))
    string = ZeroOrMore(White()).suppress() + CharsNotIn('()') + ZeroOrMore(White()).suppress()
    qstring = dblQuotedString() ^ sglQuotedString()
    qstring.addParseAction(removeQuotes)
    anystring = qstring ^ string

    # Design section.
    source = _paren_clause('source', anystring)
    date = _paren_clause('date', anystring)
    tool = _paren_clause('tool', anystring)
    number = _paren_clause('number', inum)
    name = _paren_clause('name', anystring)
    names = _paren_clause('names', anystring)
    tstamp = _paren_clause('tstamp', anystring)
    tstamps = _paren_clause('tstamps', anystring)
    title = _paren_clause('title', anystring)
    company = _paren_clause('company', anystring)
    rev = _paren_clause('rev', fnum)
    value = _paren_clause('value', anystring)
    comment = Group(_paren_clause('comment', number & value))
    comments = Group(OneOrMore(comment))('comments')
    title_block = _paren_clause('title_block', Optional(title) &
                        Optional(company) & Optional(rev) &
                        Optional(date) & Optional(source) & comments)
    sheet = Group(_paren_clause('sheet', number + name + tstamps + Optional(title_block)))
    sheets = Group(OneOrMore(sheet))('sheets')
    design = _paren_clause('design', Optional(source) & Optional(date) &
                        Optional(tool) & Optional(sheets))

    # Components section.
    ref = _paren_clause('ref', anystring)
    datasheet = _paren_clause('datasheet', anystring)
    field = Group(_paren_clause('field', name & anystring('text')))
    fields = _paren_clause('fields', ZeroOrMore(field))
    lib = _paren_clause('lib', anystring)
    part = _paren_clause('part', anystring)
    footprint = _paren_clause('footprint', anystring)
    libsource = _paren_clause('libsource', lib & part)
    sheetpath = _paren_clause('sheetpath', names & tstamps)
    comp = Group(_paren_clause('comp', ref & value & Optional(datasheet) & 
                    Optional(fields) & Optional(libsource) & Optional(footprint) & 
                    Optional(sheetpath) & Optional(tstamp)))
    components = _paren_clause('components', ZeroOrMore(comp))

    # Part library section.
    description = _paren_clause('description', anystring)
    docs = _paren_clause('docs', anystring)
    pnum = _paren_clause('num', anystring)
    ptype = _paren_clause('type', anystring)
    pin = Group(_paren_clause('pin', pnum & name & ptype))
    pins = _paren_clause('pins', ZeroOrMore(pin))
    alias = Group(_paren_clause('alias', anystring))
    aliases = _paren_clause('aliases', ZeroOrMore(alias))
    fp = Group(_paren_clause('fp', anystring))
    footprints = _paren_clause('footprints', ZeroOrMore(fp))
    libpart = Group(_paren_clause('libpart', lib & part & Optional(
        fields) & Optional(pins) & Optional(footprints) & Optional(aliases) &
                                  Optional(description) & Optional(docs)))
    libparts = _paren_clause('libparts', ZeroOrMore(libpart))

    # Libraries section.
    logical = _paren_clause('logical', anystring)
    uri = _paren_clause('uri', anystring)
    library = Group(_paren_clause('library', logical & uri))
    libraries = _paren_clause('libraries', ZeroOrMore(library))

    # Nets section.
    code = _paren_clause('code', inum)
    part_pin = _paren_clause('pin', anystring)
    node = Group(_paren_clause('node', ref & part_pin))
    nodes = Group(OneOrMore(node))('nodes')
    net = Group(_paren_clause('net', code & name & nodes))
    nets = _paren_clause('nets', ZeroOrMore(net))

    # Entire netlist.
    version = _paren_clause('version', word)
    end_of_file = ZeroOrMore(White()) + stringEnd
    parser = _paren_clause('export', version +
                (design & components & Optional(libparts) & Optional(libraries) & nets
                ))('netlist') + end_of_file.suppress()

    return parser.parseString(text)


def parse_netlist(src, tool='kicad'):
    """
    Return a pyparsing object storing the contents of a netlist.

    Args:
        src: Either a text string, or a filename, or a file object that stores
            the netlist.

    Returns:
        A pyparsing object that stores the netlist contents.

    Exception:
        PyparsingException.
    """

    try:
        text = src.read()
    except Exception:
        try:
            text = open(src,'r').read()
        except Exception:
            text = src

    if not isinstance(text, basestring):
        raise Exception("What is this shit you're handing me? [{}]\n".format(src))

    try:
        # Use the tool name to find the function for loading the library.
        func_name = '_parse_netlist_{}'.format(tool)
        parse_func = THIS_MODULE[func_name]
        return parse_func(text)
    except KeyError:
        # OK, that didn't work so well...
        logger.error('Unsupported ECAD tool library: {}'.format(tool))
        raise Exception
