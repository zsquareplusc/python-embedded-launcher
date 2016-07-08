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
