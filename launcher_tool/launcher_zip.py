
DEFAULT_MAIN = """\
import sys
sys.path.append(sys.argv[1])

import launcher
launcher.patch_sys_path()
launcher.restore_sys_argv()

{run}
"""

def make_main(entry_point=None, run_path=None, run_module=None,
              extend_sys_path=(), wait_at_exit=False, wait_on_error=False,
              main_script=DEFAULT_MAIN):
    run_lines = []
    if extend_sys_path:
        for pattern in args.extend_sys_path:
            run_lines.append('launcher.extend_sys_path_by_pattern({!r})'.format(pattern))
    if wait_at_exit:
        run_lines.append('launcher.wait_at_exit()')
    if wait_on_error:
        run_lines.append('launcher.wait_on_error()')

    if entry_point is not None:
        mod, func = entry_point.split(':')
        run_lines.append('import {module}\n{module}.{main}()'.format(module=mod, main=func))
    elif run_path is not None:
        run_lines.append('import runpy\nrunpy.run_path({!r})'.format(run_path))
    elif run_module is not None:
        run_lines.append('import runpy\nrunpy.run_module({!r})'.format(run_module))

    return main_script.format(run='\n'.join(run_lines))
