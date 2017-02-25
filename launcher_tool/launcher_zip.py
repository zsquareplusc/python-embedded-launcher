#!python
#
# This file is part of https://github.com/zsquareplusc/python-embedded-launcher
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Build the boot code (__main__.py) for the zip file that is appended to the launcher.
"""

DEFAULT_MAIN = """\
import sys
import os
sys.path.append(sys.argv[1])

import launcher
launcher.patch_sys_path({patch})
launcher.restore_sys_argv()

{run}
"""


# pylint: disable=too-many-arguments
def make_main(entry_point=None, run_path=None, run_module=None,
              extend_sys_path=(), wait_at_exit=False, wait_on_error=False,
              use_bin_dir=False,
              main_script=DEFAULT_MAIN):
    """\
    Generate code for __main__.py. The arguments represent different options
    to start an application, handle sys.path and exit options, which influence
    the code that is generated.
    """
    run_lines = []
    if extend_sys_path:
        for pattern in extend_sys_path:
            run_lines.append('launcher.extend_sys_path_by_pattern({!r})'.format(pattern))
    if wait_at_exit:
        run_lines.append('launcher.wait_at_exit()')
    if wait_on_error and not wait_at_exit:  # waiting on error only needed if not already generally waiting
        run_lines.append('launcher.wait_on_error()')

    if entry_point is not None:
        mod, func = entry_point.split(':')
        run_lines.append('import {module}\n{module}.{main}()'.format(module=mod, main=func))
    elif run_path is not None:
        run_lines.append('import runpy, os\nrunpy.run_path(os.path.expandvars({!r}))'.format(run_path))
    elif run_module is not None:
        run_lines.append('import runpy\nrunpy.run_module({!r})'.format(run_module))

    patch = ''
    if use_bin_dir:
        patch = 'os.path.dirname(os.path.dirname(sys.executable))'
    return main_script.format(run='\n'.join(run_lines), patch=patch)


def main():
    """Command line tool entry point"""
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='create __main__.py')


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

    group_custom = parser.add_argument_group('customization')
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

    parser.add_argument(
        '--bin-dir', action='store_true', default=False,
        help='put binaries in subdirectory /bin')

    args = parser.parse_args()

    sys.stdout.write(make_main(
        entry_point=args.entry_point,
        run_path=args.run_path,
        run_module=args.run_module,
        extend_sys_path=args.extend_sys_path,
        wait_at_exit=args.wait,
        wait_on_error=args.wait_on_error,
        use_bin_dir=args.bin_dir))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
