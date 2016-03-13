#!python
#
# This file is part of https://github.com/zsquareplusc/python-embedded-launcher
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Extract the launcher.exe.
"""
import argparse
import os
import pkgutil
import sys


def copy_launcher(fileobj, use_py2=False):
    """copy raw launcher exe to given file object"""
    fileobj.write(pkgutil.get_data(__name__,
                                   'launcher27.exe'
                                   if use_py2
                                   else 'launcher3.exe'))


def main():
    """Command line tool entry point"""
    parser = argparse.ArgumentParser(description='copy the launcher.exe')

    group_out = parser.add_argument_group('output options')
    group_out.add_argument('-o', '--output', metavar='FILE',
                           help='write to this file')

    #~ parser.add_argument('--32', dest='bits32', action='store_true', default=False,
                        #~ help='force download of 32 bit version')
    #~ parser.add_argument('--64', dest='bits64', action='store_true', default=False,
                        #~ help='force download of 64 bit version')

    group_pyver = parser.add_argument_group('Python version')
    group_pyver_choice = group_pyver.add_mutually_exclusive_group()
    group_pyver_choice.add_argument('-2', dest='py2', action='store_true', default=False,
                                    help='force use of Python 2.7 launcher')
    group_pyver_choice.add_argument('-3', dest='py3', action='store_true', default=False,
                                    help='force use of Python 3.x launcher')

    args = parser.parse_args()

    use_python27 = False
    if sys.version_info.major == 2 or args.py2:
        use_python27 = True

    dest_dir = os.path.dirname(args.output)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(args.output, 'wb') as exe:
        copy_launcher(exe, use_python27)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
