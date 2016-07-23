# -*- coding: utf-8 -*-

# MIT license
# 
# Copyright (C) 2016 by { cookiecutter.full_name }
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

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import argparse
import os
import shutil
import sys
import logging
from .schdl import *
from . import __version__

###############################################################################
# Command-line interface.
###############################################################################


def main():
    parser = argparse.ArgumentParser(
        description=
        '''A Python package for textually describing circuit schematics.''')
    parser.add_argument('--version',
                        '-v',
                        action='version',
                        version='schdl ' + __version__)
    parser.add_argument(
        '--extract',
        '-x',
        nargs='+',
        type=str,
        metavar='file.[xlsx|csv|sch|lib|dcm]',
        help='''Extract field values from one or more spreadsheet or
            schematic files.''')
    parser.add_argument(
        '--insert',
        '-i',
        nargs='+',
        type=str,
        metavar='file.[xlsx|csv|sch|lib|dcm]',
        help='''Insert extracted field values into one or more schematic
            or spreadsheet files.''')
    parser.add_argument('--overwrite',
                        '-w',
                        action='store_true',
                        help='Allow field insertion into an existing file.')
    parser.add_argument(
        '--nobackup',
        '-nb',
        action='store_true',
        help='''Do *not* create backups before modifying files.
            (Default is to make backup files.)''')
    parser.add_argument(
        '--fields',
        '-f',
        nargs='+',
        type=str,
        default=[],
        metavar='name|/name|~name',
        help='''Specify the names of the fields to extract and insert.
            Place a '/' or '~' in front of a field you wish to omit.
            (Leave blank to extract/insert *all* fields.)''')
    parser.add_argument(
        '--debug',
        '-d',
        nargs='?',
        type=int,
        default=0,
        metavar='LEVEL',
        help='Print debugging info. (Larger LEVEL means more info.)')

    args = parser.parse_args()

    logger = logging.getLogger('schdl')
    if args.debug is not None:
        log_level = logging.DEBUG + 1 - args.debug
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        logger.addHandler(handler)
        logger.setLevel(log_level)

    if args.extract is None:
        logger.critical(
            'Hey! Give me some files to extract field values from!')
        sys.exit(2)

    if args.insert is None:
        print('Hey! I need some files where I can insert the field values!')
        sys.exit(1)

    for file in args.insert:
        if os.path.isfile(file):
            if not args.overwrite and args.nobackup:
                logger.critical(
                    '''File {} already exists! Use the --overwrite option to
                    allow modifications to it or allow backups.'''
                    .format(file))
                sys.exit(1)
            if not args.nobackup:
                # Create a backup file.
                index = 1  # Start with this backup file suffix.
                while True:
                    backup_file = file + '.{}.bak'.format(index, file)
                    if not os.path.isfile(backup_file):
                        # Found an unused backup file name, so make backup.
                        shutil.copy(file, backup_file)
                        break  # Backup done, so break out of loop.
                    index += 1  # Else keep looking for an unused backup file name.

    inc_fields = []
    exc_fields = []
    for f in args.fields:
        if f[0] in [r'/', r'~']:
            exc_fields.append(f[1:])
        else:
            inc_fields.append(f)

    schdl(extract_filenames=args.extract,
            insert_filenames=args.insert,
            inc_field_names=inc_fields,
            exc_field_names=exc_fields)

###############################################################################
# Main entrypoint.
###############################################################################
if __name__ == '__main__':
    main()
