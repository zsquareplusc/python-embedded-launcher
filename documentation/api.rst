=====
 API
=====

Launcher
========
A small helper module called ``launcher`` is automatically packaged with the
exe. It contains a few helper functions.

.. module:: launcher

.. function:: patch_sys_path()

    Add directories (relative to executable, if existing) to ``sys.path``.

    - the directory of the executable
    - ``Python{py.major}{py.minor}/site-packages``
    - ``Python{py.major}{py.minor}/Lib/site-packages``
    - ``Lib/site-packages``

    These locations are also scanned for ``.pth`` files.

    This function is called automatically by the start code.


.. function:: extend_sys_path_by_pattern(pattern)

    :param str pattern: String with wildcard

    Add files matching a pattern (e.g. ``*.zip``, ``*.whl``, ``*.egg``) to
    ``sys.path``. The pattern is prefixed with the location of the executable.
    In case of wheel files, it only works for pure Python wheels and only if
    they do no access the file system to load data on their own (should use
    pkgutil_). This function is used if the command line option
    ``--extend-sys-path`` is used.


.. function :: restore_sys_argv()

    Get original command line via Windows API. Restores ``sys.argv`` (which is
    used by the launcher to pass the location of Python). This function is
    called by the default boot code (``__main__``).

    Note: Python 2 usually has ``str`` elements in ``sys.argv``, but this
    function sets them to be ``unicode``.


.. function:: close_console()

    Useful for GUI applications, it closes a separate console window if there
    is one, e.g. when the exe was started by a double click. It is safe to
    call this function even if the application was started in a console
    (determined with :func:`is_separate_console_window()`)

    Note that ``sys.stdout``, ``sys.stderr`` and ``sys.stdin`` are replaced
    with a dummy objects that ignore ``write()``/``flush()`` and return
    empty strings on ``read()``.

    Note: some functions may access the std streams, bypassing ``sys.stdXXX```,
    those will fail due to the closed steams.


.. function:: is_separate_console_window()

    :return: true if the process has a console

    Return true if the console window was opened with this process (e.g.
    the console was opened because the exe was started from the file Explorer).


.. function:: hide_console(hide=True)

    :param bool hide: Hide console when true, show it when false

    Hides the console window, if one was opened for the process. The function
    can also be called to show the window again. This function is used
    by ``hide_console_until_error()``


.. function:: hide_console_until_error()

    Hides the console window, if one was opened for the process, but shows the
    console window again when a traceback is printed. ``sys.excepthook`` is
    set by this function and it calls the previous value after showing the
    console window again.


.. function:: wait_at_exit()

    Wait at exit, but only if console window was opened separately. So if
    the application was started in a console, there is no extra waiting, while
    when it was started from the GUI and a separate console window is opended,
    it will wait extra, so that the user can read the output.

    This function is called automatically if the command line option
    ``--wait`` is used.


.. function:: wait_on_error()

    Wait if the program terminates with an exception, but only if console
    window was opened separately.

    This function is called automatically if the command line option
    ``--wait-on-error`` is used.

.. _pkgutil: https://docs.python.org/3/library/pkgutil.html
