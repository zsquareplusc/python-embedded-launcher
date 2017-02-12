=====
 API
=====

A small helper module called ``launcher`` is automatically packaged with the
exe. It contains a few helper functions.

``launcher.patch_sys_path()``
    Add directories (relative to executable, if existing) to ``sys.path``.

    - the directory of the executable
    - ``Python{py.major}{py.minor}/site-packages``
    - ``Python{py.major}{py.minor}/Lib/site-packages``
    - ``Lib/site-packages``

    These locations are also scanned for ``.pth`` files.

``launcher.extend_sys_path_by_pattern(pattern)``
    Add files matching a pattern (e.g. ``*.zip``, ``*.whl``, ``*.egg``) to
    ``sys.path``. The pattern is prefixed with the location of the executable.
    In case of wheel files, it only works for pure Python wheels and only if
    they do no access the file system to load data on their own (should use
    pkgutil_). This function is used if the command line option
    ``--extend-sys-path`` is used.

``launcher.restore_sys_argv()``
    Get original command line via Windows API. Restores ``sys.argv`` (which is
    used by the launcher to pass the location of Python). This function is
    called by the default boot code (``__main__``).

    Note: Python 2 usually has ``str`` elements in ``sys.argv``, but this
    function sets them to be ``unicode``.

``launcher.close_console()``
    Useful for GUI applications, it closes a separate console window if there
    is one, e.g. when the exe was started by a double click.
    Note that ``sys.stdout``, ``sys.stderr`` and ``sys.stdin`` are replaced
    with a dummy object that ignores ``write()``/``flush()`` and returns
    empty strings on ``read()``.

    Note: some functions may access the std streams, bypassing ``sys.stdXXX```,
    those will fail due to the closed steams.

``launcher.is_separate_console_window()``
    Return true if the console window was opened with this process (e.g.
    the console was opened because the exe was started from the file Explorer).

``hide_console(hide=True)``
    Hides the console window, if one was opened for the process. The function
    can also be called to show the window again. This function is used
    by ``hide_console_until_error()``

``launcher.hide_console_until_error()``
    Hides the console window, if one was opened for the process, but shows the
    console window again when a traceback is printed. ``sys.excepthook`` is
    set by this function and it calls the previous value.

``launcher.wait_at_exit()``
    Wait at exit, but only if console window was opened separately.
    This function is called automatically if the command line option
    ``--wait`` is used.

``launcher.wait_on_error()``
    Wait if the program terminates with an exception, but only if console
    window was opened separately.
    This function is called automatically if the command line option
    ``--wait-on-error`` is used.

.. _pkgutil: https://docs.python.org/3/library/pkgutil.html
