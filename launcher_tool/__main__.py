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


DEFAULT_MAIN = """\
import sys
sys.path.append(sys.argv[1])

import launcher
launcher.patch_sys_path()
launcher.restore_sys_argv()

{run}
"""


def main():
    """Command line tool entry point"""
    parser = argparse.ArgumentParser(description='create customized launcher.exe')

    group_out = parser.add_argument_group('output options')
    group_out_out = group_out.add_mutually_exclusive_group(required=True)
    group_out_out.add_argument('-o', '--output', metavar='FILE',
                               help='filename to write the result to')
    group_out_out.add_argument('-a', '--append-only', metavar='FILE',
                               help='append to this file instead of creating a new one')

    group_run_group = parser.add_argument_group('entry point options')
    group_run = group_run_group.add_mutually_exclusive_group()
    group_run.add_argument('-e', '--entry-point', metavar='MODULE:FUNC',
                           help='import given module and call function')
    group_run.add_argument('--run-path', metavar='FILE',
                           help='execute given file (e.g. .py, .zip)')
    group_run.add_argument('-m', '--run-module', metavar='MODULE',
                           help='execute module (similar to python -m)')
    group_run.add_argument('--main', metavar='FILE',
                           help='use this as __main__.py instead of built-in code')

    group_custom = parser.add_argument_group('customization')

    group_custom.add_argument('--add-file', action='append', default=[], metavar='FILE',
                              help='add additional file(s) to zip')
    group_custom.add_argument('--add-zip', action='append', default=[], metavar='ZIPFILE',
                              help='add contents of zip file(s)')
    group_custom.add_argument('--launcher', metavar='EXE',
                              help='launcher executable to use instead of built-in one')
    group_custom.add_argument('--wait', action='store_true', default=False,
                              help='do not close console window automatically')
    group_custom.add_argument('--wait-on-error', action='store_true', default=False,
                              help='wait if there is an excpetion')
    group_custom.add_argument('-p', '--extend-sys-path', metavar='PATTERN', action='append', default=[],
                              help='add search pattern for files added to sys.path')

    args = parser.parse_args()
    if args.append_only:
        args.output = args.append_only  # easier to handle below
        mode = 'ab'
    else:
        mode = 'wb'

    run_lines = []
    if args.extend_sys_path:
        for pattern in args.extend_sys_path:
            run_lines.append('launcher.extend_sys_path_by_pattern({!r})'.format(pattern))
    if args.wait:
        run_lines.append('launcher.wait_at_exit()')
    if args.wait_on_error:
        run_lines.append('launcher.wait_on_error()')

    if args.entry_point is not None:
        mod, func = args.entry_point.split(':')
        run_lines.append('import {module}\n{module}.{main}()'.format(module=mod, main=func))
    elif args.run_path is not None:
        run_lines.append('import runpy\nrunpy.run_path({!r})'.format(args.run_path))
    elif args.run_module is not None:
        run_lines.append('import runpy\nrunpy.run_module({!r})'.format(args.run_module))

    if args.main is not None:
        main_script = open(args.main).read()
    else:
        main_script = DEFAULT_MAIN
    main_script = main_script.format(run='\n'.join(run_lines), py=sys.version_info)

    dest_dir = os.path.dirname(args.output)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(args.output, mode) as exe:
        if not args.append_only:
            if args.launcher:
                exe.write(open(args.launcher, 'rb').read())
            else:
                exe.write(pkgutil.get_data(__name__,
                                           'launcher27.exe'
                                           if sys.version_info.major == 2
                                           else 'launcher3.exe'))
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
