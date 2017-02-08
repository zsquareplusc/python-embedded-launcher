#!python
#
# This file is part of https://github.com/zsquareplusc/python-embedded-launcher
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Create a customized launcher.exe. A zip file is created and appended to the
launcher. The zip contains boot code (__main__) and optionally other data
files.
"""
import argparse
import glob
import os
import pkgutil
import sys
import zipfile
import launcher_tool.launcher_zip


def main():
    """Command line tool entry point"""
    parser = argparse.ArgumentParser(description='create customized launcher.exe')

    group_out = parser.add_argument_group('output options')
    group_out_out = group_out.add_mutually_exclusive_group(required=True)
    group_out_out.add_argument(
        '-o', '--output', metavar='FILE',
        help='filename to write the result to')
    group_out_out.add_argument(
        '-a', '--append-only', metavar='FILE',
        help='append to this file instead of creating a new one')

    group_run_group = parser.add_argument_group('entry point options')
    group_run = group_run_group.add_mutually_exclusive_group()
    group_run.add_argument(
        '-e', '--entry-point', metavar='MODULE:FUNC',
        help='import given module and call function')
    group_run.add_argument(
        '--run-path', metavar='FILE',
        help='execute given file (e.g. .py, .zip)')
    group_run.add_argument(
        '-m', '--run-module', metavar='MODULE',
        help='execute module (similar to python -m)')
    group_run.add_argument(
        '--main', metavar='FILE',
        help='use this as __main__.py instead of built-in code')

    group_custom = parser.add_argument_group('customization')

    group_custom.add_argument(
        '--add-file', action='append', default=[], metavar='FILE',
        help='add additional file(s) to zip')
    group_custom.add_argument(
        '--add-zip', action='append', default=[], metavar='ZIPFILE',
        help='add contents of zip file(s)')
    group_custom.add_argument(
        '--launcher', metavar='EXE',
        help='launcher executable to use instead of built-in one')
    group_custom.add_argument(
        '--wait', action='store_true', default=False,
        help='do not close console window automatically')
    group_custom.add_argument(
        '--wait-on-error', action='store_true', default=False,
        help='wait if there is an exception')
    group_custom.add_argument(
        '-p', '--extend-sys-path', metavar='PATTERN', action='append', default=[],
        help='add search pattern for files added to sys.path')

    group_bits = parser.add_argument_group(
        'launcher architecture',
        'default value is based on sys.executable')
    group_bits_choice = group_bits.add_mutually_exclusive_group()
    group_bits_choice.add_argument(
        '--32', dest='bits32', action='store_true', default=False,
        help='force copy of 32 bit version')
    group_bits_choice.add_argument(
        '--64', dest='bits64', action='store_true', default=False,
        help='force copy of 64 bit version')

    group_pyver = parser.add_argument_group(
        'launcher Python version',
        'default value is based on sys.executable')
    group_pyver_choice = group_pyver.add_mutually_exclusive_group()
    group_pyver_choice.add_argument(
        '-2', dest='py2', action='store_true', default=False,
        help='force use of Python 2.7 launcher')
    group_pyver_choice.add_argument(
        '-3', dest='py3', action='store_true', default=False,
        help='force use of Python 3.x launcher')

    args = parser.parse_args()

    is_64bits = sys.maxsize > 2**32  # recommended by docs.python.org "platform" module
    if (sys.version_info.major == 2 and not args.py3) or args.py2:
        if args.bits64:
            launcher_filename = 'launcher27-64.exe'
        elif args.bits32:
            launcher_filename = 'launcher27-32.exe'
        elif is_64bits:
            launcher_filename = 'launcher27-64.exe'
        else:
            launcher_filename = 'launcher27-32.exe'
    else:
        if args.bits64:
            launcher_filename = 'launcher3-64.exe'
        elif args.bits32:
            launcher_filename = 'launcher3-32.exe'
        elif is_64bits:
            launcher_filename = 'launcher3-64.exe'
        else:
            launcher_filename = 'launcher3-32.exe'

    if args.append_only:
        args.output = args.append_only  # easier to handle below
        mode = 'ab'
    else:
        mode = 'wb'

    if args.main is not None:
        main_script = open(args.main).read()
    else:
        main_script = launcher_tool.launcher_zip.make_main(
            entry_point=args.entry_point,
            run_path=args.run_path,
            run_module=args.run_module,
            extend_sys_path=args.extend_sys_path,
            wait_at_exit=args.wait,
            wait_on_error=args.wait_on_error)

    dest_dir = os.path.dirname(args.output)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(args.output, mode) as exe:
        if not args.append_only:
            if args.launcher:
                exe.write(open(args.launcher, 'rb').read())
            else:
                exe.write(pkgutil.get_data(__name__, launcher_filename))
        with zipfile.ZipFile(exe, 'a', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('__main__.py', main_script.encode('utf-8'))
            archive.writestr('launcher.py', pkgutil.get_data(__name__, 'launcher.py'))
            for pattern in args.add_file:
                matches = glob.glob(pattern)
                if matches:
                    for filename in matches:
                        archive.write(filename)
                else:
                    sys.stderr.write('WARNING: {} does not match any files\n'.format(pattern))
            for pattern in args.add_zip:
                matches = glob.glob(pattern)
                if matches:
                    for filename in matches:
                        with zipfile.ZipFile(filename) as source_archive:
                            for entry in source_archive.infolist():
                                if entry.filename == '__main__.py':
                                    sys.stderr.write('WARNING: included {}/__main__.py as _main.py'.format(entry.filename))
                                    entry.filename = '_main.py'
                                archive.writestr(entry, source_archive.read(entry))
                else:
                    sys.stderr.write('WARNING: {} does not match any files\n'.format(pattern))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
