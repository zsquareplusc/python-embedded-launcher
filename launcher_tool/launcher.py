#!python
#
# This file is part of https://github.com/zsquareplusc/python-embedded-launcher
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Helper functions for executables packaged with python-embedded-launcher.
"""

# imports are delayed, made within the function calls. this is intentionally
# in case the startup code alters sys.path etc.

import sys
import os


SCAN_DIRECTORIES = [
    '.',
    'Python{py.major}{py.minor}/site-packages'.format(py=sys.version_info),
    'Python{py.major}{py.minor}/Lib/site-packages'.format(py=sys.version_info),
    'Lib/site-packages',
]


def process_pth_file(root, filename):
    """\
    Read and process a Python .pth file:
    - ignore comments and empty lines
    - excute lines starting with 'import'
    - all others: take it as path, test if path exists and append it to
      sys.path when it does.
    """
    with open(filename, 'rU') as pth_file:
        for line in pth_file:
            line = line.rstrip()
            if not line or line.startswith('#'):
                continue
            elif line.startswith(("import ", "import\t")):
                exec(line)  # statement in py2, function in py3, pylint: disable=exec-used
                continue
            else:
                path = os.path.abspath(os.path.join(root, line))
                if os.path.exists(path):
                    sys.path.append(path)


def patch_sys_path(root=os.path.dirname(sys.executable), scan_pth=True):
    """\
    Add an internal list of directories (relative to exe) to sys.path.
    In each of these directories also scan for .pth files.
    """
    for path in SCAN_DIRECTORIES:
        location = os.path.join(root, path)
        if os.path.exists(location):
            sys.path.append(location)
    if scan_pth:
        import glob
        for path in SCAN_DIRECTORIES:
            for pth_file in glob.glob(os.path.join(root, path, '*.pth')):
                process_pth_file(os.path.join(root, path), pth_file)


def extend_sys_path_by_pattern(pattern):
    """add files matching pattern (e.g. *.zip, *.whl, *.egg) to sys.path"""
    import glob
    for whl in glob.glob(os.path.join(os.path.dirname(sys.executable), pattern)):
        sys.path.append(whl)


#~ def restore_sys_argv():
    #~ """get original command line via Windows API"""
    #~ import ctypes
    #~ import shlex
    #~ commandline = ctypes.c_wchar_p(ctypes.windll.kernel32.GetCommandLineW())
    #~ sys.argv = shlex.split(commandline.value, posix=False)

def restore_sys_argv():
    import ctypes
    import ctypes.wintypes
    LocalFree = ctypes.windll.kernel32.LocalFree
    LocalFree.argtypes = [ctypes.wintypes.HLOCAL]
    LocalFree.restype = ctypes.wintypes.HLOCAL
    GetCommandLineW = ctypes.windll.kernel32.GetCommandLineW
    GetCommandLineW.argtypes = []
    GetCommandLineW.restype = ctypes.wintypes.LPCWSTR
    CommandLineToArgvW = ctypes.windll.shell32.CommandLineToArgvW
    CommandLineToArgvW.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_int)]
    CommandLineToArgvW.restype = ctypes.POINTER(ctypes.wintypes.LPWSTR)

    argc = ctypes.c_int()
    argv = CommandLineToArgvW(GetCommandLineW(), ctypes.byref(argc))
    if not argv:
        return
    sys.argv = argv[0:argc.value]
    LocalFree(argv)


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


def hide_console(hide=True):
    """hides the console window, if one was opened for the process"""
    if is_separate_console_window():
        import ctypes
        window = ctypes.windll.kernel32.GetConsoleWindow()
        if hide:
            ctypes.windll.user32.ShowWindow(window, 0) # SW_HIDE
        else:
            ctypes.windll.user32.ShowWindow(window, 5) # SW_SHOW


def close_console():
    """closes the console window, if one was opened for the process"""
    if is_separate_console_window():
        import ctypes
        ctypes.windll.kernel32.CloseHandle(4294967286)  # STD_INPUT_HANDLE
        ctypes.windll.kernel32.CloseHandle(4294967285)  # STD_OUTPUT_HANDLE
        ctypes.windll.kernel32.CloseHandle(4294967284)  # STD_ERROR_HANDLE
        ctypes.windll.kernel32.FreeConsole()


def hide_console_until_error():
    if not is_separate_console_window():
        return

    def handle_exception(exctype, value, tb, orig_hook=sys.excepthook):
        """Print a exception and wait for a key"""
        hide_console(False)
        orig_hook(exctype, value, tb)

    sys.excepthook = handle_exception

    hide_console()


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
