"""\
A tool to append files to zip which is in turn appended to an other file.
"""
import argparse
import glob
import os
import pkgutil
import re
import shutil
import sys
import zipfile


DEFAULT_MAIN = """\
import sys
sys.path.append(sys.argv[1])

import launcher
launcher.patch_sys_path(['.', 'Python{py.major}{py.minor}/site-packages'])
launcher.restore_sys_argv()

import {module}
{module}.{main}()"""


def main():
    parser = argparse.ArgumentParser(description='Launcher assembler')

    parser.add_argument('-o', '--output', metavar='FILE',
                        help='Filename to write the result to')
    parser.add_argument('-a', '--append-only', metavar='FILE',
                        help='Append to this file instead of ceating a new one')
    parser.add_argument('--launcher', metavar='EXE',
                        help='Launcher executable to use instead of built-in one')
    parser.add_argument('--main', metavar='FILE',
                        help='use this as __main__.py instead of built-in code')
    parser.add_argument('--raw', action='store_true', default=False,
                        help='Do not append zip data (used to copy launcher only)')
    parser.add_argument('-e', '--entry-point', metavar='MOD:FUNC',
                        help='import given module and call function')
    parser.add_argument('--add-file', action='append', default=[], metavar='FILE',
                        help='Add additional file to zip')
    parser.add_argument('--add-zip', action='append', default=[], metavar='ZIPFILE',
                        help='add contents of zip file')

    args = parser.parse_args()
    if args.main is None and args.entry_point is None and not args.raw:
        parser.error('either --entry-point or --main has to be used')
    if args.append_only and args.output:
        parser.error('either --output and --append-only are conflicting options')
    if not args.append_only and not args.output:
        parser.error('either --output or --append-only must be given')
    if args.append_only:
        args.output = args.append_only  # easier to handle below
        mode = 'ab'
    else:
        mode = 'wb'

    #~ sys.stderr.write('running for {}\n'.format('Python 2.7' if sys.version_info.major == 2 else 'Python 3.x'))

    if args.main is not None:
        main = open(args.main).read()
    else:
        main = DEFAULT_MAIN
    if args.entry_point is not None:
        mod, func = args.entry_point.split(':')
        main = main.format(module=mod, main=func, py=sys.version_info)

    dest_dir = os.path.dirname(args.output)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(args.output, mode) as exe:
        if not args.append_only:
            if args.launcher:
                exe.write(open(args.launcher, 'rb').read())
            else:
                exe.write(pkgutil.get_data(__name__, 'launcher27.exe' if sys.version_info.major == 2 else 'launcher3.exe'))

        if not args.raw:
            with zipfile.ZipFile(exe, 'a', compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('__main__.py', main)
                archive.writestr('launcher.py', pkgutil.get_data(__name__, 'launcher.py'))
                for filename in args.add_file:
                    archive.write(filename)
                for filename in args.add_zip:
                    with zipfile.ZipFile(filename) as source_archive:
                        for entry in source_archive.infolist():
                            archive.writestr(entry, source_archive.read(entry))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
