"""\
Helper functions for executables packaged with python-embedded-launcher.
"""
# imports are delayed, made within the function calls. this is intentionally
# in case the startup code alters sys.path etc.

import sys
import os


def patch_sys_path(relative_dirs=('.',), scan_pth=True):
    """\
    Add directories (relative to exe) to sys.path.
    The default is to add the directory of the exe.
    """
    root = os.path.dirname(sys.executable)
    for path in relative_dirs:
        sys.path.append(os.path.join(root, path))
    if scan_pth:
        import glob
        for pth_file in glob.glob(os.path.join(root, '*.pth')):
            for line in open(pth_file):
                if not line.lstrip().startswith('#'):
                    path = os.path.join(root, line)
                    if os.path.exists(path):
                        sys.path.append(path)


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


def wait_at_exit():
    """wait at exit, but only if console window was opened separately"""
    import ctypes
    import ctypes.wintypes
    window = ctypes.windll.kernel32.GetConsoleWindow()
    pid = ctypes.wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(window, ctypes.byref(pid))
    if pid.value != ctypes.windll.kernel32.GetCurrentProcessId():
        return

    import atexit
    import msvcrt

    def wait_at_end():
        """Print a message and wait for a key"""
        sys.stdout.write('\n[Press any key]\n')
        sys.stdout.flush()
        sys.stderr.flush()
        msvcrt.getch()
    atexit.register(wait_at_end)
