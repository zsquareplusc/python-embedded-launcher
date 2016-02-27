"""\
Helper functions for executables packaged with python-embedded-launcher.
"""
# imports are delayed, made within the function calls. this is intentionally
# in case the startup code alters sys.path etc.

import sys
import os


def patch_sys_path(relative_dirs=('.',)):
    """\
    Add directories (relative to exe) to sys.path.
    The default is to add the directory of the exe.
    """
    root = os.path.dirname(sys.executable)
    for path in relative_dirs:
        sys.path.append(os.path.join(root, path))


def add_wheels():
    """add wheel to sys.path"""
    import glob
    for whl in glob.glob(os.path.join(os.path.dirname(sys.executable), 'wheels', '*.whl')):
        sys.path.append(whl)

def restore_sys_argv():
    """get original command line via Windows API"""
    import ctypes
    import shlex
    commandline = ctypes.c_wchar_p(ctypes.windll.kernel32.GetCommandLineW())
    sys.argv = shlex.split(commandline.value, posix=False)

def close_console():
    """closes the console window, if one was opened for the process"""
    import ctypes
    ctypes.windll.kernel32.FreeConsole()
