"""\
Helper functions for executables packaged with python-embedded-launcher.
"""
# imports are delayed, made within the function calls. this is intentionally
# in case the startup code alters sys.path etc.

import sys
import os

SITE_PACKAGES = 'Python{py.major}{py.minor}/site-packages'.format(py=sys.version_info)


def process_pth_file(root, pth_file):
    with open(pth_file, 'rU') as f:
        for line in f:
            line = line.rstrip()
            if not line or line.startswith('#'):
                continue
            elif line.startswith(("import ", "import\t")):
                exec(line)  # statement in py2, function in py3
                continue
            else:
                path = os.path.abspath(os.path.join(root, line))
                if os.path.exists(path):
                    sys.path.append(path)


def patch_sys_path(relative_dirs=('.', SITE_PACKAGES), scan_pth=True):
    """\
    Add directories (relative to exe) to sys.path.
    The default is to add the directory of the exe.
    """
    root = os.path.dirname(sys.executable)
    for path in relative_dirs:
        sys.path.append(os.path.join(root, path))
    if scan_pth:
        import glob
        for path in relative_dirs:
            for pth_file in glob.glob(os.path.join(root, path, '*.pth')):
                process_pth_file(os.path.join(root, path), pth_file)


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


def is_separate_console_window():
    """\
    return true if the console window was opened with this process.
    return false if the console was already open and this application was
    started within it.
    """
    import ctypes
    import ctypes.wintypes
    window = ctypes.windll.kernel32.GetConsoleWindow()
    console_pid = ctypes.wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(window, ctypes.byref(console_pid))
    return console_pid.value == ctypes.windll.kernel32.GetCurrentProcessId()


def close_console():
    """closes the console window, if one was opened for the process"""
    if is_separate_console_window():
        import ctypes
        ctypes.windll.kernel32.FreeConsole()


def wait_at_exit():
    """wait at exit, but only if console window was opened separately"""
    if not is_separate_console_window():
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



def wait_on_error():
    """wait on exception, but only if console window was opened separately"""
    if not is_separate_console_window():
        return

    import msvcrt
    import traceback

    def handle_exception(exctype, value, tb):
        """Print a exception and wait for a key"""
        traceback.print_exception(exctype, value, tb)
        sys.stdout.write('\n[Press any key]\n')
        sys.stdout.flush()
        sys.stderr.flush()
        msvcrt.getch()
    
    sys.excepthook = handle_exception
