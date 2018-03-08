#!python
#
# This file is part of https://github.com/zsquareplusc/python-embedded-launcher
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Helper functions for executables packaged with python-embedded-launcher.

This file is added to the zip archive that is appended to the exe. It provides
functions that the application (and the startup code) can use.
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

    Usually called by patch_sys_path().
    """
    # the following is a fix for namespace packages where python accesses the
    # local 'sitedir' of the caller... see also issue #7
    sitedir = root
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
    """\
    Add files matching pattern (e.g. *.zip, *.whl, *.egg) to sys.path.

    Usually called by the generated __main__.py.
    """
    import glob
    for path in glob.glob(os.path.join(os.path.dirname(sys.executable),
                                       os.path.expandvars(pattern))):
        sys.path.append(path)


def restore_sys_argv():
    """\
    Restore original command line arguments. The launcher.exe header used
    the command line to pass internas to Python, this function sets sys.argv
    to the values passed to the exe.

    Usually called by the generated __main__.py.
    """
    # pylint: disable=invalid-name
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
    Check if the process owns a console window.

    Return True if the console window was opened with this process.
    Return False if the console was already open and this application was
    started within it.
    """
    import ctypes
    import ctypes.wintypes
    window = ctypes.windll.kernel32.GetConsoleWindow()
    console_pid = ctypes.wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(window, ctypes.byref(console_pid))
    return console_pid.value == ctypes.windll.kernel32.GetCurrentProcessId()


def hide_console(hide=True):
    """\
    Hides the console window, if one was opened for the process.
    """
    if is_separate_console_window():
        import ctypes
        window = ctypes.windll.kernel32.GetConsoleWindow()
        if hide:
            ctypes.windll.user32.ShowWindow(window, 0)  # SW_HIDE
        else:
            ctypes.windll.user32.ShowWindow(window, 5)  # SW_SHOW


class DummyFile(object):
    """Dummy File object to replace stdio when console is closed"""
    # pylint: disable=unused-argument, no-self-use
    def write(self, data):
        """all operations are ignored"""
    def flush(self):
        """all operations are ignored"""
    def read(self, size=None):
        """all operations are ignored"""
        return ''


def close_console():
    """\
    Closes the console window, if one was opened for the process.

    Can be used by GUI applcations to get rid of separate console window.
    See also hide_console_until_error().

    sys.stdout/stderr/stdin are replaced with a dummy object that ignores
    writes / reads empty strings.
    """
    if is_separate_console_window():
        import ctypes
        ctypes.windll.kernel32.CloseHandle(4294967286)  # STD_INPUT_HANDLE
        ctypes.windll.kernel32.CloseHandle(4294967285)  # STD_OUTPUT_HANDLE
        ctypes.windll.kernel32.CloseHandle(4294967284)  # STD_ERROR_HANDLE
        ctypes.windll.kernel32.FreeConsole()
        sys.stdout = sys.stderr = sys.stdin = DummyFile()


def hide_console_until_error():
    """\
    Hides the console window, if one was opened for the process, but shows the
    console window again when a traceback is printed.
    """
    if not is_separate_console_window():
        return

    def handle_exception(exctype, value, tb, orig_hook=sys.excepthook):  # pylint: disable=invalid-name
        """Print an exception and wait for a key"""
        hide_console(False)
        orig_hook(exctype, value, tb)

    sys.excepthook = handle_exception

    hide_console()


def wait_at_exit():
    """\
    Wait at exit, but only if console window was opened separately.
    """
    if not is_separate_console_window():
        return

    import atexit
    import msvcrt

    def wait_at_end():
        """Print a message and wait for a key"""
        sys.stderr.flush()
        sys.stdout.write('\n[Press any key]\n')
        sys.stdout.flush()
        msvcrt.getch()

    atexit.register(wait_at_end)


def wait_on_error():
    """\
    Wait on exception, but only if console window was opened separately.
    """
    if not is_separate_console_window():
        return

    import msvcrt
    import traceback

    def handle_exception(exctype, value, tb):  # pylint: disable=invalid-name
        """Print an exception and wait for a key"""
        traceback.print_exception(exctype, value, tb)
        sys.stderr.flush()
        sys.stdout.write('\n[Press any key]\n')
        sys.stdout.flush()
        msvcrt.getch()

    sys.excepthook = handle_exception
